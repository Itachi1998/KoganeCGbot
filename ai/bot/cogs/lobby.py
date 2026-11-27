"""/lobby - the original lobby (teams, ready, start) driving the ai battle engine.

Lobby fights are SPARS: everyone fights with a copy of their character, so nothing that happens
here (wounds, death, points, loot, XP) is saved. Real fights happen in the colony (/pvp, and the
curses that find you). The owner can add cursed spirits or named NPCs as opponents (PvE), or
split the players into Team A and Team B (PvP), or both.
"""
from __future__ import annotations

import asyncio
import copy
from typing import Optional

import discord
import numpy as np
from discord.ext import commands

from ...battle import Battle
from ...cli import NPC_ROSTER, standard_field
from ...constants import GRADE_NAME, Grade
from ...effects import tame_all
from ...records import finger_bearer, npc_fighter, npc_spirit, sukuna_npc
from ...rules import Colony
from .. import style
from ..bridge import DiscordIO, run_battle

TEAMS = ("Team A", "Team B")


def make_npc(index: int, level: int, rng):
    name, pclass, tech = NPC_ROSTER[index]
    if tech == "finger_bearer":
        return finger_bearer(rng)
    if tech == "sukuna":                                  # "level" is his finger count
        return sukuna_npc(max(1, min(level, 20)), rng)
    if tech == "sukuna_megumi":
        return sukuna_npc(max(1, min(level, 20)), rng, ["ten_shadows"], "Megumi")
    return npc_fighter(name.split(" (")[0], pclass, level, tech, rng,
                       weapon="inverted_spear" if name.startswith("The Sorcerer Killer") else None,
                       tech_state=tame_all({}) if tech == "ten_shadows" else None)


class Lobby:
    def __init__(self, owner: int, name: str, channel):
        self.owner, self.name, self.channel = owner, name, channel
        self.teams = {t: [] for t in TEAMS}           # user ids
        self.spectators: list = []
        self.ready: set = set()
        self.npcs: list = []                          # (label, factory(rng))
        self.running = False
        self.message: Optional[discord.Message] = None

    @property
    def players(self) -> list:
        return self.teams[TEAMS[0]] + self.teams[TEAMS[1]]

    def team_of(self, uid: int) -> Optional[str]:
        return next((t for t, ids in self.teams.items() if uid in ids), None)

    def leave(self, uid: int) -> None:
        for ids in self.teams.values():
            if uid in ids:
                ids.remove(uid)
        if uid in self.spectators:
            self.spectators.remove(uid)
        self.ready.discard(uid)


class LobbyView(discord.ui.LayoutView):
    def __init__(self, cog: "LobbyCog", lobby: Lobby):
        super().__init__(timeout=None)
        self.cog, self.lobby = cog, lobby
        lb = lobby
        status = "In battle" if lb.running else "In queue"
        body = [f"{style.stat('Owner', f'<@{lb.owner}>')}  {style.stat('Status', status)}"]
        for t in TEAMS:
            body.append(f"### `{t}`\n" + ("\n".join(f"> <@{u}>" + (" ✅" if u in lb.ready else "") for u in lb.teams[t])
                                         or "> No players"))
        body.append("### `Opponents`\n" + ("\n".join(f"> {label}" for label, _ in lb.npcs) or "> None (PvP only)"))
        body.append("### `Spectators`\n" + (", ".join(f"<@{u}>" for u in lb.spectators) or "> None"))
        body.append("-# Lobby fights are spars: nothing that happens here is saved to your character.")
        container = discord.ui.Container(accent_colour=style.LOBBY)
        url = style.avatar_url(cog.bot)
        head = discord.ui.TextDisplay(style.heading(lb.name))
        container.add_item(discord.ui.Section(head, accessory=discord.ui.Thumbnail(url)) if url else head)
        container.add_item(discord.ui.TextDisplay("\n".join(body)[:4000]))
        if not lb.running:
            row = discord.ui.ActionRow()
            for t in TEAMS:
                row.add_item(self._btn(f"Join {t}", discord.ButtonStyle.green, self._join(t)))
            row.add_item(self._btn("Spectate", discord.ButtonStyle.secondary, self.spectate))
            row.add_item(self._btn("Ready Up", discord.ButtonStyle.green, self.ready))
            row.add_item(self._btn("Leave Lobby", discord.ButtonStyle.red, self.leave))
            container.add_item(row)
            curses = discord.ui.Select(placeholder="Owner: add a cursed spirit...", options=[
                discord.SelectOption(label=f"{GRADE_NAME[g]} curse", value=str(g)) for g in Grade])
            curses.callback = self.add_curse
            container.add_item(discord.ui.ActionRow(curses))
            for lo in range(0, len(NPC_ROSTER), 25):             # a select holds 25 options
                npcs = discord.ui.Select(
                    placeholder="Owner: add a named opponent (level 10; Sukuna: 10 fingers)..."
                    if lo == 0 else "Owner: more named opponents...",
                    options=[discord.SelectOption(label=name[:100], value=str(i))
                             for i, (name, _, _) in enumerate(NPC_ROSTER) if lo <= i < lo + 25])
                npcs.callback = self.add_npc
                container.add_item(discord.ui.ActionRow(npcs))
            own = discord.ui.ActionRow()
            own.add_item(self._btn("Start Round", discord.ButtonStyle.green, self.start))
            own.add_item(self._btn("Clear Opponents", discord.ButtonStyle.secondary, self.clear))
            own.add_item(self._btn("Disband Lobby", discord.ButtonStyle.red, self.disband))
            container.add_item(own)
        self.add_item(container)

    @staticmethod
    def _btn(label, style_, cb):
        b = discord.ui.Button(label=label, style=style_)
        b.callback = cb
        return b

    async def refresh(self, itx: discord.Interaction) -> None:
        await itx.response.edit_message(view=LobbyView(self.cog, self.lobby))

    def _join(self, team: str):
        async def cb(itx: discord.Interaction):
            rec = self.cog.rt.store.get_player(str(itx.guild.id), str(itx.user.id))
            if rec is None or not rec.alive:
                await itx.response.send_message("You need a living character in this colony (`/create`).",
                                                ephemeral=True)
                return
            self.lobby.leave(itx.user.id)
            self.lobby.teams[team].append(itx.user.id)
            await self.refresh(itx)
        return cb

    async def spectate(self, itx):
        self.lobby.leave(itx.user.id)
        self.lobby.spectators.append(itx.user.id)
        await self.refresh(itx)

    async def ready(self, itx):
        if itx.user.id not in self.lobby.players:
            await itx.response.send_message("Join a team first.", ephemeral=True)
            return
        self.lobby.ready ^= {itx.user.id}
        await self.refresh(itx)

    async def leave(self, itx):
        self.lobby.leave(itx.user.id)
        if itx.user.id == self.lobby.owner and self.lobby.players:
            self.lobby.owner = self.lobby.players[0]
        await self.refresh(itx)

    async def _owner(self, itx) -> bool:
        if itx.user.id != self.lobby.owner:
            await itx.response.send_message("Only the lobby owner can do that.", ephemeral=True)
            return False
        return True

    async def add_curse(self, itx):
        if not await self._owner(itx):
            return
        g = Grade(int(itx.data["values"][0]))
        self.lobby.npcs.append((f"{GRADE_NAME[g]} curse", lambda rng, g=g: npc_spirit(g, rng)))
        await self.refresh(itx)

    async def add_npc(self, itx):
        if not await self._owner(itx):
            return
        i = int(itx.data["values"][0])
        self.lobby.npcs.append((NPC_ROSTER[i][0], lambda rng, i=i: make_npc(i, 10, rng)))
        await self.refresh(itx)

    async def clear(self, itx):
        if await self._owner(itx):
            self.lobby.npcs.clear()
            await self.refresh(itx)

    async def disband(self, itx):
        if not await self._owner(itx):
            return
        self.cog.lobbies.pop(self.lobby.channel.id, None)
        await itx.response.edit_message(view=style.panel(None, None, "`Lobby Disbanded`", accent=style.LOBBY,
                                                         thumbnail=False))
        self.stop()

    async def start(self, itx):
        if not await self._owner(itx):
            return
        lb = self.lobby
        a, b_ = lb.teams[TEAMS[0]], lb.teams[TEAMS[1]]
        if not lb.players:
            await itx.response.send_message("Nobody has joined a team.", ephemeral=True)
            return
        if not lb.npcs and not (a and b_):
            await itx.response.send_message("Add opponents, or put players on both teams.", ephemeral=True)
            return
        missing = [u for u in lb.players if u not in lb.ready]
        if missing:
            await itx.response.send_message("Not everyone is ready: " + ", ".join(f"<@{u}>" for u in missing),
                                            ephemeral=True)
            return
        clash = [u for u in lb.players if u in self.cog.rt.busy_users]
        if clash:
            await itx.response.send_message("Already in another lobby fight: " + ", ".join(f"<@{u}>" for u in clash),
                                            ephemeral=True)
            return
        lb.running = True
        await self.refresh(itx)
        asyncio.create_task(self.cog.fight(itx.guild, lb))


class LobbyCog(commands.Cog, name="Lobby"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.lobbies: dict = {}
        self.rng = np.random.default_rng()

    @property
    def rt(self):
        return self.bot.runtime

    @commands.hybrid_group(name="lobby", description="Spar with other players and NPCs", invoke_without_command=True)
    @commands.guild_only()
    async def lobby(self, ctx: commands.Context) -> None:
        await ctx.send(view=style.panel(self.bot, "Lobby",
                                        "* `/lobby create [name]` opens a lobby (in a thread when possible).\n"
                                        "* Join Team A or Team B, Ready Up; the owner adds curses or named "
                                        "opponents and presses **Start Round**.\n"
                                        "* In the fight, press **Open controls** when it is your move.\n"
                                        "* Lobby fights are spars: nothing is saved. Real fights happen in the colony."),
                       ephemeral=True)

    @lobby.command(name="create", description="Open a lobby")
    @commands.guild_only()
    async def create(self, ctx: commands.Context, name: Optional[str] = None) -> None:
        name = name or f"{ctx.author.display_name}'s lobby"
        channel = ctx.channel
        if isinstance(ctx.channel, discord.TextChannel):
            try:
                channel = await ctx.channel.create_thread(name=name[:90], type=discord.ChannelType.public_thread)
            except discord.HTTPException:
                channel = ctx.channel
        if channel.id in self.lobbies:
            await ctx.send("There is already a lobby here.", ephemeral=True)
            return
        lb = Lobby(ctx.author.id, name, channel)
        self.lobbies[channel.id] = lb
        lb.message = await channel.send(view=LobbyView(self, lb))
        if channel is not ctx.channel:
            await ctx.send(f"Lobby opened: {channel.mention}", ephemeral=True)

    async def fight(self, guild: discord.Guild, lb: Lobby) -> None:
        """Play the spar to the end in the lobby's channel."""
        rt = self.rt
        players = list(lb.players)
        rt.busy_users.update(players)
        try:
            game = rt.session(guild)
            colony = Colony(str(guild.id), game.colony.name, rules=list(game.colony.rules))   # a throwaway copy
            io = DiscordIO(self.bot, lb.channel, asyncio.get_running_loop())
            b = Battle(str(guild.id), seed=int(self.rng.integers(1 << 30)), io=io, colony=colony)
            for team_no, team in enumerate(TEAMS):
                for uid in lb.teams[team]:
                    rec = game.player(uid) or rt.store.get_player(str(guild.id), str(uid))
                    if rec is None or not rec.alive:
                        continue
                    spar = copy.deepcopy(rec)                    # nothing comes back from a spar
                    b.add(spar.to_spec("human"), team_no)
            for label, factory in lb.npcs:
                b.add(factory(self.rng), 50)
            standard_field(b)
            io.say(f"*** {lb.name}: the fight begins ***")
            result = await run_battle(b, io)
            winners = ", ".join(result["winners"]) or "nobody"
            await lb.channel.send(view=style.panel(self.bot, "Battle over",
                                                   f"{style.stat('Rounds', result['rounds'])}\n"
                                                   f"{style.stat('Standing', winners)}", accent=style.LOBBY))
        except Exception as e:
            await lb.channel.send(f"The fight broke off: `{type(e).__name__}: {e}`")
            raise
        finally:
            rt.busy_users.difference_update(players)
            lb.running = False
            lb.ready.clear()
            if lb.channel.id in self.lobbies:
                lb.message = await lb.channel.send(view=LobbyView(self, lb))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(LobbyCog(bot))
