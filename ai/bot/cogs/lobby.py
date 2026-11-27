"""/lobby - the original lobby (teams, ready, start), now the only way into a fight.

Fights need a lobby. A player who is not on a lobby team can move around the colony and do
everything else, but nothing can attack them and they cannot attack anyone: roaming curses pass
them by and /pvp refuses. Joining a lobby team means you are in the culling game for real.

From the lobby (owner's buttons):
  Hunt   fight the curses at the owner's node, with every lobby player who is there. Saved:
         wounds, death, points, XP, loot.
  PvP    Team A against Team B, everyone at the owner's node. Saved, and Judgeman hears of it.
  Spar   practice against opponents the owner picks, anywhere. NOTHING is saved.
Curses that reach lobby players on their own (while anyone lets time pass) fight them too, and
those fights are played in the lobby's thread.
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
from ...crimes import Crime
from ...effects import tame_all
from ...records import finger_bearer, npc_fighter, npc_spirit, sukuna_npc
from ...rules import Colony
from .. import style
from ..bridge import DiscordIO, run_battle

TEAMS = ("Team A", "Team B", "Team C", "Field")
FIELD = "Field"                                       # everyone on the field fights for themselves


def side_of(lb, uid: int) -> int:
    """Battle team number: Team A/B/C are 0/1/2; each player on the Field is a side of their own."""
    for i, t in enumerate(TEAMS):
        if uid in lb.teams[t]:
            return 10 + lb.teams[t].index(uid) if t == FIELD else i
    return -1


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
    def __init__(self, guild_id: int, owner: int, name: str, channel, private: bool = False):
        self.guild_id, self.owner, self.name, self.channel = guild_id, owner, name, channel
        self.private = private                       # invite-only, PvP only, and no curse finds its members
        self.invited: set = {owner}
        self.teams = {t: [] for t in TEAMS}           # user ids
        self.spectators: list = []
        self.ready: set = set()
        self.npcs: list = []                          # spar opponents: (label, factory(rng))
        self.running = False

    @property
    def players(self) -> list:
        return [u for t in TEAMS for u in self.teams[t]]

    def sides(self) -> set:
        return {side_of(self, u) for u in self.players}

    @property
    def members(self) -> set:
        """Who can fight (and be attacked): the players on a team. Spectators can't."""
        return set(self.players)

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
        game = cog.rt.sessions.get(str(lb.guild_id))

        def who(u):
            rec = game.player(u) if game else None
            where = f" @ node {rec.node}" if rec else " (no character)"
            return f"> <@{u}>{where}" + (" ✅" if u in lb.ready else "")

        owner_rec = game.player(lb.owner) if game else None
        here = owner_rec.node if owner_rec else None
        curses = ([r.label for r in game.world.roamers if not r.respawn_at and r.node == here]
                  if game is not None and here is not None else [])
        body = [f"{style.stat('Owner', f'<@{lb.owner}>')}  {style.stat('Status', 'In battle' if lb.running else 'In queue')}"
                f"  {style.stat('Type', 'Private (invite only, PvP only)' if lb.private else 'Public')}"]
        for t in TEAMS:
            body.append(f"### `{t}`\n" + ("\n".join(who(u) for u in lb.teams[t]) or "> No players"))
        if lb.private:
            body.append("### `Invited`\n" + (", ".join(f"<@{u}>" for u in sorted(lb.invited)) or "> -"))
        body.append("### `At the owner's node`\n"
                    + (f"> node {here}: " + (", ".join(curses) or "no curses") if here is not None else "> -"))
        body.append("### `Spar opponents`\n" + ("\n".join(f"> {label}" for label, _ in lb.npcs) or "> None"))
        body.append("### `Spectators`\n" + (", ".join(f"<@{u}>" for u in lb.spectators) or "> None"))
        body.append("-# Teams A, B and C fight each other; everyone on the Field fights everyone. "
                    + ("A private lobby is for PvP between invited players only: no curse finds its members."
                       if lb.private else "Only players on a team can fight or be attacked. **Hunt** and **PvP** "
                       "are real and saved; **Spar** is practice and saves nothing."))
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
            container.add_item(row)
            row2 = discord.ui.ActionRow()
            row2.add_item(self._btn("Ready Up", discord.ButtonStyle.green, self.ready))
            row2.add_item(self._btn("Leave Lobby", discord.ButtonStyle.red, self.leave))
            row2.add_item(self._btn("Refresh", discord.ButtonStyle.secondary, self.refresh))
            container.add_item(row2)
            own = discord.ui.ActionRow()
            if not lb.private:
                own.add_item(self._btn("Hunt", discord.ButtonStyle.green, self.hunt))
            own.add_item(self._btn("PvP", discord.ButtonStyle.red, self.pvp))
            if not lb.private:
                own.add_item(self._btn("Spar", discord.ButtonStyle.blurple, self.spar))
            own.add_item(self._btn("Disband", discord.ButtonStyle.red, self.disband))
            container.add_item(own)
        if not lb.running and not lb.private:
            curses_sel = discord.ui.Select(placeholder="Spar: add a cursed spirit...", options=[
                discord.SelectOption(label=f"{GRADE_NAME[g]} curse", value=str(g)) for g in Grade])
            curses_sel.callback = self.add_curse
            container.add_item(discord.ui.ActionRow(curses_sel))
            for lo in range(0, len(NPC_ROSTER), 25):             # a select holds 25 options
                npcs = discord.ui.Select(
                    placeholder="Spar: add a named opponent (level 10; Sukuna: 10 fingers)..."
                    if lo == 0 else "Spar: more named opponents...",
                    options=[discord.SelectOption(label=name[:100], value=str(i))
                             for i, (name, _, _) in enumerate(NPC_ROSTER) if lo <= i < lo + 25])
                npcs.callback = self.add_npc
                container.add_item(discord.ui.ActionRow(npcs))
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
            if self.lobby.private and itx.user.id not in self.lobby.invited:
                await itx.response.send_message("This lobby is private: the owner has to `/lobby invite` you.",
                                                ephemeral=True)
                return
            if itx.user.id in self.cog.rt.busy_users:
                await itx.response.send_message("You are in a fight right now.", ephemeral=True)
                return
            for other in self.cog.rt.lobbies.values():          # one lobby at a time
                if other is not self.lobby and other.guild_id == self.lobby.guild_id:
                    other.leave(itx.user.id)
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

    async def disband(self, itx):
        if not await self._owner(itx):
            return
        self.cog.rt.lobbies.pop(self.lobby.channel.id, None)
        await itx.response.edit_message(view=style.panel(None, None, "`Lobby Disbanded`", accent=style.LOBBY,
                                                         thumbnail=False))
        self.stop()

    async def _go(self, itx, mode: str) -> None:
        """Common checks, then hand the fight to the cog."""
        if not await self._owner(itx):
            return
        lb = self.lobby
        if not lb.players:
            await itx.response.send_message("Nobody has joined a team.", ephemeral=True)
            return
        missing = [u for u in lb.players if u not in lb.ready]
        if missing:
            await itx.response.send_message("Not everyone is ready: " + ", ".join(f"<@{u}>" for u in missing),
                                            ephemeral=True)
            return
        if lb.private and mode != "pvp":
            await itx.response.send_message("A private lobby is for PvP only.", ephemeral=True)
            return
        if mode == "spar" and not lb.npcs and len(lb.sides()) < 2:
            await itx.response.send_message("Add spar opponents, or put players on two or more sides.", ephemeral=True)
            return
        if mode == "pvp" and len(lb.sides()) < 2:
            await itx.response.send_message("PvP needs at least two sides: two teams, or two players on the Field.",
                                            ephemeral=True)
            return
        lb.running = True
        await self.refresh(itx)
        asyncio.create_task(self.cog.start(itx.guild, lb, mode))

    async def hunt(self, itx):
        await self._go(itx, "hunt")

    async def pvp(self, itx):
        await self._go(itx, "pvp")

    async def spar(self, itx):
        await self._go(itx, "spar")


class LobbyCog(commands.Cog, name="Lobby"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.rng = np.random.default_rng()

    @property
    def rt(self):
        return self.bot.runtime

    @commands.hybrid_group(name="lobby", description="Fights need a lobby: hunt curses, PvP, or spar",
                           invoke_without_command=True)
    @commands.guild_only()
    async def lobby(self, ctx: commands.Context) -> None:
        lb = self.rt.lobby_of(ctx.guild.id, ctx.author.id)
        await ctx.send(view=style.panel(self.bot, "Lobby",
                                        "* **Fights need a lobby.** Outside one you can move and do everything else, "
                                        "but nothing can attack you and you can't attack anyone.\n"
                                        "* `/lobby create [name]` opens a lobby thread; join a team there.\n"
                                        "* **Hunt**: fight the curses at the owner's node (saved). **PvP**: Team A "
                                        "against Team B at the owner's node (saved). **Spar**: practice, nothing saved.\n"
                                        "* Curses that reach lobby players fight them in the lobby's thread.\n"
                                        "* `/lobby leave` takes you out (you can't be attacked after that).\n\n"
                                        + (f"You are in **{lb.name}** ({lb.channel.mention})." if lb else
                                           "You are not in a lobby.")),
                       ephemeral=True)

    @lobby.command(name="create", description="Open a lobby (private: invite-only PvP)")
    @commands.guild_only()
    async def create(self, ctx: commands.Context, name: Optional[str] = None, private: bool = False) -> None:
        name = name or f"{ctx.author.display_name}'s {'private ' if private else ''}lobby"
        channel = ctx.channel
        if isinstance(ctx.channel, discord.TextChannel):
            try:
                channel = await ctx.channel.create_thread(
                    name=name[:90], invitable=False if private else True,
                    type=discord.ChannelType.private_thread if private else discord.ChannelType.public_thread)
                if private:
                    await channel.add_user(ctx.author)
            except discord.HTTPException:
                if private:
                    await ctx.send("I could not open a private thread here (I need **Create Private Threads**).",
                                   ephemeral=True)
                    return
                channel = ctx.channel
        if channel.id in self.rt.lobbies:
            await ctx.send("There is already a lobby here.", ephemeral=True)
            return
        lb = Lobby(ctx.guild.id, ctx.author.id, name, channel, private=private)
        self.rt.lobbies[channel.id] = lb
        await channel.send(view=LobbyView(self, lb))
        if channel is not ctx.channel:
            await ctx.send(f"Lobby opened: {channel.mention}", ephemeral=True)

    @lobby.command(name="invite", description="Invite a player to your private lobby")
    @commands.guild_only()
    async def invite(self, ctx: commands.Context, member: discord.Member) -> None:
        lb = next((x for x in self.rt.lobbies.values() if x.guild_id == ctx.guild.id and x.owner == ctx.author.id
                   and x.private), None)
        if lb is None:
            await ctx.send("You do not own a private lobby.", ephemeral=True)
            return
        lb.invited.add(member.id)
        try:
            await lb.channel.add_user(member)
        except (discord.HTTPException, AttributeError):
            pass
        await ctx.send(f"Invited {member.mention} to **{lb.name}**.", ephemeral=True)

    @lobby.command(name="leave", description="Leave your lobby (nothing can attack you after that)")
    @commands.guild_only()
    async def leave(self, ctx: commands.Context) -> None:
        lb = self.rt.lobby_of(ctx.guild.id, ctx.author.id)
        if lb is None:
            await ctx.send("You are not in a lobby.", ephemeral=True)
            return
        if lb.running and ctx.author.id in lb.members:
            await ctx.send("Not in the middle of a fight.", ephemeral=True)
            return
        lb.leave(ctx.author.id)
        await ctx.send(f"You left **{lb.name}**.", ephemeral=True)

    # ---- fights ---------------------------------------------------------------------------------
    async def start(self, guild: discord.Guild, lb: Lobby, mode: str) -> None:
        try:
            if mode == "spar":
                await self.spar(guild, lb)
            else:
                ok, msg = await self.rt.run(guild, lb.channel, self._real, lb, mode, wait=True)
                if msg:
                    await lb.channel.send(view=style.panel(self.bot, "Lobby", msg, accent=style.LOBBY))
        except Exception as e:
            await lb.channel.send(f"The fight broke off: `{type(e).__name__}: {e}`")
            raise
        finally:
            lb.running = False
            lb.ready.clear()
            if lb.channel.id in self.rt.lobbies:
                await lb.channel.send(view=LobbyView(self, lb))

    def _real(self, game, lb: Lobby, mode: str) -> Optional[str]:
        """Hunt or PvP, in the colony, on the battle thread. Returns a message for the lobby, if any."""
        owner = game.player(lb.owner)
        if owner is None:
            return "The owner has no living character here."
        nid = owner.node
        here = [p for u in lb.players if (p := game.player(u)) is not None and nid in game.where(p)]
        away = [u for u in lb.players if game.player(u) is None or nid not in game.where(game.player(u))]
        note = (" Not at node %d, so not in it: " % nid + ", ".join(f"<@{u}>" for u in away)) if away else ""
        if mode == "hunt":
            roamers = [r for r in game.world.roamers if not r.respawn_at and r.node == nid][:3]
            if not roamers:
                return (f"There are no curses at node {nid}. `/look` shows what is nearby; move toward them, or "
                        "let time pass and they will come to you.")
            game.encounter(nid, roamers, here)
        else:
            sides = {p.user_id: side_of(lb, int(p.user_id)) for p in here}
            if len(set(sides.values())) < 2:
                return f"At least two sides need someone at node {nid}." + note
            starter = side_of(lb, lb.owner)
            for p in here:
                if sides[p.user_id] == starter:            # the side that started it: Judgeman hears of it
                    p.crimes.add(Crime.ASSAULT, nid, game.day())
            names = sorted({t for t in TEAMS for u in lb.teams[t] if str(u) in sides})
            game.fight([(game.present(p, nid), sides[p.user_id]) for p in here], nid,
                       " vs ".join(names) + (" (every one for themselves)" if FIELD in names else "") + "!")
        game.save()
        return ("The fight is over." + note) if note else None

    async def spar(self, guild: discord.Guild, lb: Lobby) -> None:
        """Practice: everyone fights with a copy of their character, so nothing is saved."""
        rt = self.rt
        players = list(lb.players)
        rt.busy_users.update(players)
        try:
            game = rt.session(guild)
            colony = Colony(str(guild.id), game.colony.name, rules=list(game.colony.rules))   # a throwaway copy
            io = DiscordIO(self.bot, lb.channel, asyncio.get_running_loop())
            b = Battle(str(guild.id), seed=int(self.rng.integers(1 << 30)), io=io, colony=colony)
            for uid in lb.players:
                rec = game.player(uid) or rt.store.get_player(str(guild.id), str(uid))
                if rec is not None and rec.alive:
                    b.add(copy.deepcopy(rec).to_spec("human"), side_of(lb, uid))
            for label, factory in lb.npcs:
                b.add(factory(self.rng), 50)
            standard_field(b)
            io.say(f"*** {lb.name}: a spar (nothing here is saved) ***")
            result = await run_battle(b, io)
            await lb.channel.send(view=style.panel(self.bot, "Spar over",
                                                   f"{style.stat('Rounds', result['rounds'])}\n"
                                                   f"{style.stat('Standing', ', '.join(result['winners']) or 'nobody')}",
                                                   accent=style.LOBBY))
        finally:
            rt.busy_users.difference_update(players)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(LobbyCog(bot))
