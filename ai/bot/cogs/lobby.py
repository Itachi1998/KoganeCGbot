"""/lobby - the original lobby (teams, ready, start), now the only way into a fight.

Fights need a lobby. A player who is not on a lobby team can move around the colony and do
everything else, but nothing can attack them and they cannot attack anyone: roaming curses pass
them by and /pvp refuses. Joining a lobby team means you are in the culling game for real.

From the lobby (owner's buttons):
  Hunt   fight the curses at the owner's node, with every lobby player who is there. Saved:
         wounds, death, points, XP, loot.
  PvP    the lobby's sides against each other, everyone at the owner's node. Saved, and Judgeman
         hears of it.
  Spar   practice against opponents the owner picks, anywhere. NOTHING is saved.
Curses that reach lobby players on their own (while anyone lets time pass) fight them too, and
those fights are played in the lobby's thread.

Lobby state lives in Redis (lobbies.py), and every button is a stateless "dynamic item" whose id
names the action and the lobby - so lobbies and their buttons survive a restart and can be served
by any bot process.
"""
from __future__ import annotations

import asyncio
import copy
import time
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
from ..lobbies import FIELD, START_GUARD, TEAMS, Lobby

TEAM_CODE = {"a": "Team A", "b": "Team B", "c": "Team C", "f": FIELD}


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


def spar_opponent(npc: dict, rng):
    return npc_spirit(Grade(int(npc["arg"])), rng) if npc["kind"] == "curse" else make_npc(int(npc["arg"]), 10, rng)


# ---- stateless components: the id says what to do and to which lobby ---------------------------
class LobbyButton(discord.ui.DynamicItem[discord.ui.Button],
                  template=r"kl:(?P<act>[a-z]+):(?P<cid>\d+)(?::(?P<arg>[a-z0-9]+))?"):
    def __init__(self, act: str, cid: int, arg: Optional[str] = None, *, label: str = "",
                 style: discord.ButtonStyle = discord.ButtonStyle.secondary):
        super().__init__(discord.ui.Button(label=label, style=style,
                                           custom_id=f"kl:{act}:{cid}" + (f":{arg}" if arg else "")))
        self.act, self.cid, self.arg = act, cid, arg

    @classmethod
    async def from_custom_id(cls, itx: discord.Interaction, item: discord.ui.Button, match):
        return cls(match["act"], int(match["cid"]), match["arg"], label=item.label or "", style=item.style)

    async def callback(self, itx: discord.Interaction) -> None:
        cog = itx.client.get_cog("Lobby")
        await cog.on_button(itx, self.act, self.cid, self.arg)


class LobbySelect(discord.ui.DynamicItem[discord.ui.Select], template=r"ks:(?P<act>[a-z0-9]+):(?P<cid>\d+)"):
    def __init__(self, act: str, cid: int, *, placeholder: str = "", options=None):
        super().__init__(discord.ui.Select(placeholder=placeholder, custom_id=f"ks:{act}:{cid}",
                                           options=options or [discord.SelectOption(label="-", value="-")]))
        self.act, self.cid = act, cid

    @classmethod
    async def from_custom_id(cls, itx: discord.Interaction, item: discord.ui.Select, match):
        return cls(match["act"], int(match["cid"]), placeholder=item.placeholder or "", options=item.options)

    async def callback(self, itx: discord.Interaction) -> None:
        cog = itx.client.get_cog("Lobby")
        await cog.on_select(itx, self.act, self.cid, list(itx.data.get("values", [])))


def lobby_view(cog: "LobbyCog", lb: Lobby) -> discord.ui.LayoutView:
    """The lobby message. Built from the lobby's state alone, so any process can redraw it."""
    view = discord.ui.LayoutView(timeout=None)
    game = cog.rt.sessions.get(str(lb.guild_id))
    running = cog.is_running(lb, game)

    def who(u):
        rec = game.player(u) if game else None
        where = f" **{rec.name}** @ node {rec.node}" if rec else " (no character)"
        return f"> <@{u}>{where}" + (" ✅" if u in lb.ready else "")

    owner_rec = game.player(lb.owner) if game else None
    here = owner_rec.node if owner_rec else None
    curses = ([r.label for r in game.world.roamers if not r.respawn_at and r.node == here]
              if game is not None and here is not None else [])
    body = [f"{style.stat('Owner', f'<@{lb.owner}>')}  {style.stat('Status', 'In battle' if running else 'In queue')}"
            f"  {style.stat('Type', 'Private (invite only, PvP only)' if lb.private else 'Public')}"]
    for t in TEAMS:
        body.append(f"### `{t}`\n" + ("\n".join(who(u) for u in lb.teams[t]) or "> No players"))
    if lb.private:
        body.append("### `Invited`\n" + (", ".join(f"<@{u}>" for u in sorted(lb.invited)) or "> -"))
    body.append("### `At the owner's node`\n"
                + (f"> node {here}: " + (", ".join(curses) or "no curses") if here is not None else "> -"))
    if not lb.private:
        body.append("### `Spar opponents`\n" + ("\n".join(f"> {n['label']}" for n in lb.npcs) or "> None"))
    body.append("### `Spectators`\n" + (", ".join(f"<@{u}>" for u in lb.spectators) or "> None"))
    body.append("-# Teams A, B and C fight each other; everyone on the Field fights everyone. "
                + ("A private lobby is for PvP between invited players only: no curse finds its members."
                   if lb.private else "Only players on a team can fight or be attacked. **Hunt** and **PvP** "
                   "are real and saved; **Spar** is practice and saves nothing."))
    container = discord.ui.Container(accent_colour=style.LOBBY)
    url = style.avatar_url(cog.bot)
    head = discord.ui.TextDisplay(style.heading(lb.name))
    container.add_item(discord.ui.Section(head, accessory=discord.ui.Thumbnail(url)) if url else head)
    container.add_item(discord.ui.TextDisplay("\n".join(body)[:3900]))
    cid = lb.channel_id
    if not running:
        row = discord.ui.ActionRow()
        for code, t in TEAM_CODE.items():
            row.add_item(LobbyButton("join", cid, code, label=f"Join {t}", style=discord.ButtonStyle.green))
        row.add_item(LobbyButton("spectate", cid, label="Spectate"))
        container.add_item(row)
        row2 = discord.ui.ActionRow()
        row2.add_item(LobbyButton("ready", cid, label="Ready Up", style=discord.ButtonStyle.green))
        row2.add_item(LobbyButton("leave", cid, label="Leave Lobby", style=discord.ButtonStyle.red))
        row2.add_item(LobbyButton("refresh", cid, label="Refresh"))
        container.add_item(row2)
        own = discord.ui.ActionRow()
        if not lb.private:
            own.add_item(LobbyButton("hunt", cid, label="Hunt", style=discord.ButtonStyle.green))
        own.add_item(LobbyButton("pvp", cid, label="PvP", style=discord.ButtonStyle.red))
        if not lb.private:
            own.add_item(LobbyButton("spar", cid, label="Spar", style=discord.ButtonStyle.blurple))
            own.add_item(LobbyButton("clear", cid, label="Clear Opponents"))
        own.add_item(LobbyButton("disband", cid, label="Disband", style=discord.ButtonStyle.red))
        container.add_item(own)
    else:
        container.add_item(discord.ui.ActionRow(LobbyButton("refresh", cid, label="Refresh")))
    if not running and not lb.private:
        container.add_item(discord.ui.ActionRow(LobbySelect(
            "curse", cid, placeholder="Spar: add a cursed spirit...",
            options=[discord.SelectOption(label=f"{GRADE_NAME[g]} curse", value=str(int(g))) for g in Grade])))
        for n, lo in enumerate(range(0, len(NPC_ROSTER), 25)):   # a select holds 25 options
            container.add_item(discord.ui.ActionRow(LobbySelect(
                f"npc{n}", cid,
                placeholder="Spar: add a named opponent (level 10; Sukuna: 10 fingers)..." if lo == 0
                else "Spar: more named opponents...",
                options=[discord.SelectOption(label=name[:100], value=str(i))
                         for i, (name, _, _) in enumerate(NPC_ROSTER) if lo <= i < lo + 25])))
    view.add_item(container)
    return view


class LobbyCog(commands.Cog, name="Lobby"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.rng = np.random.default_rng()

    @property
    def rt(self):
        return self.bot.runtime

    def is_running(self, lb: Lobby, game=None) -> bool:
        """A fight of this lobby is on: it is being set up, or one of its players is marked fighting
        (marks lapse by themselves if the process playing the fight dies)."""
        if lb.starting_until > time.time():
            return True
        if not lb.players:
            return False
        busy = self.rt.fighting(lb.guild_id)
        return any(str(u) in busy for u in lb.players)

    # ---- commands -------------------------------------------------------------------------------
    @commands.hybrid_group(name="lobby", description="Fights need a lobby: hunt curses, PvP, or spar",
                           invoke_without_command=True)
    @commands.guild_only()
    async def lobby(self, ctx: commands.Context) -> None:
        lb = self.rt.lobby_of(ctx.guild.id, ctx.author.id)
        await ctx.send(view=style.panel(self.bot, "Lobby",
                                        "* **Fights need a lobby.** Outside one you can move and do everything else, "
                                        "but nothing can attack you and you can't attack anyone.\n"
                                        "* `/lobby create [name]` opens a lobby thread; join a team there.\n"
                                        "* **Hunt**: fight the curses at the owner's node (saved). **PvP**: the lobby's "
                                        "sides against each other at the owner's node (saved). **Spar**: practice, "
                                        "nothing saved.\n"
                                        "* `/lobby create private:True` is invite-only (`/lobby invite`) and PvP only.\n"
                                        "* Curses that reach public-lobby players fight them in the lobby's thread.\n"
                                        "* `/lobby leave` takes you out (you can't be attacked after that).\n\n"
                                        + (f"You are in **{lb.name}** (<#{lb.channel_id}>)." if lb else
                                           "You are not in a lobby.")),
                       ephemeral=True)

    @lobby.command(name="create", description="Open a lobby (private: invite-only PvP)")
    @commands.guild_only()
    async def create(self, ctx: commands.Context, name: Optional[str] = None, private: bool = False) -> None:
        name = (name or f"{ctx.author.display_name}'s {'private ' if private else ''}lobby")[:80]
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
        if self.rt.book.get(channel.id) is not None:
            await ctx.send("There is already a lobby here.", ephemeral=True)
            return
        lb = Lobby(ctx.guild.id, ctx.author.id, name, channel.id, private=private, invited=[ctx.author.id])
        self.rt.remember(channel)
        self.rt.session(ctx.guild)                              # (so the lobby can show where everyone stands)
        self.rt.book.put(lb)
        await channel.send(view=lobby_view(self, lb))
        if channel is not ctx.channel:
            await ctx.send(f"Lobby opened: {channel.mention}", ephemeral=True)
        elif ctx.interaction is not None and not ctx.interaction.response.is_done():
            await ctx.send("Lobby opened.", ephemeral=True)

    @lobby.command(name="invite", description="Invite a player to your private lobby")
    @commands.guild_only()
    async def invite(self, ctx: commands.Context, member: discord.Member) -> None:
        mine = next((x for x in self.rt.book.in_guild(ctx.guild.id) if x.owner == ctx.author.id and x.private), None)
        if mine is None:
            await ctx.send("You do not own a private lobby.", ephemeral=True)
            return

        def add(lb):
            if member.id in lb.invited:
                return False
            lb.invited.append(member.id)
        self.rt.book.update(mine.channel_id, add)
        channel = self.rt.channel(mine.channel_id)
        try:
            await channel.add_user(member)
        except (discord.HTTPException, AttributeError):
            pass
        await ctx.send(f"Invited {member.mention} to **{mine.name}**.", ephemeral=True)

    @lobby.command(name="leave", description="Leave your lobby (nothing can attack you after that)")
    @commands.guild_only()
    async def leave(self, ctx: commands.Context) -> None:
        lb = self.rt.lobby_of(ctx.guild.id, ctx.author.id)
        if lb is None:
            await ctx.send("You are not in a lobby.", ephemeral=True)
            return
        if str(ctx.author.id) in self.rt.fighting(ctx.guild.id):
            await ctx.send("Not in the middle of a fight.", ephemeral=True)
            return
        self.rt.book.update(lb.channel_id, lambda x: x.leave(ctx.author.id))
        await ctx.send(f"You left **{lb.name}**.", ephemeral=True)

    # ---- buttons and selects -----------------------------------------------------------------------
    async def _redraw(self, itx: discord.Interaction, lb: Optional[Lobby]) -> None:
        if lb is None:
            view = style.panel(None, None, "`This lobby is gone.`", accent=style.LOBBY, thumbnail=False)
        else:
            view = lobby_view(self, lb)
        if itx.response.is_done():
            await itx.edit_original_response(view=view)
        else:
            await itx.response.edit_message(view=view)

    async def _say(self, itx: discord.Interaction, text: str) -> None:
        await itx.response.send_message(text, ephemeral=True)

    async def on_button(self, itx: discord.Interaction, act: str, cid: int, arg: Optional[str]) -> None:
        book, uid = self.rt.book, itx.user.id
        lb = book.get(cid)
        if lb is None:
            return await self._redraw(itx, None)
        self.rt.remember(itx.channel)
        game = self.rt.session(itx.guild)
        owner_only = act in ("hunt", "pvp", "spar", "clear", "disband")
        if owner_only and uid != lb.owner:
            return await self._say(itx, "Only the lobby owner can do that.")
        if act != "refresh" and self.is_running(lb, game):
            return await self._say(itx, "A fight is on. Wait until it is over.")

        if act == "join":
            team = TEAM_CODE.get(arg or "")
            rec = game.player(uid)
            if team is None:
                return await self._say(itx, "No such team.")
            if rec is None:
                return await self._say(itx, "You need a living character in this colony (`/create`).")
            if lb.private and uid not in lb.invited:
                return await self._say(itx, "This lobby is private: the owner has to `/lobby invite` you.")
            if str(uid) in game.in_battle:
                return await self._say(itx, "You are in a fight right now.")
            book.remove_user(lb.guild_id, uid, except_channel=cid)       # one lobby at a time

            def join(x):
                x.leave(uid)
                x.teams[team].append(uid)
            lb = book.update(cid, join)
        elif act == "spectate":
            def watch(x):
                x.leave(uid)
                x.spectators.append(uid)
            lb = book.update(cid, watch)
        elif act == "ready":
            if uid not in lb.players:
                return await self._say(itx, "Join a team first.")

            def ready(x):
                x.ready.remove(uid) if uid in x.ready else x.ready.append(uid)
            lb = book.update(cid, ready)
        elif act == "leave":
            def leave(x):
                x.leave(uid)
                if uid == x.owner and x.players:
                    x.owner = x.players[0]
            lb = book.update(cid, leave)
        elif act == "clear":
            lb = book.update(cid, lambda x: x.npcs.clear())
        elif act == "disband":
            book.delete(lb)
            return await itx.response.edit_message(view=style.panel(None, None, "`Lobby Disbanded`",
                                                                    accent=style.LOBBY, thumbnail=False))
        elif act in ("hunt", "pvp", "spar"):
            return await self._start(itx, lb, act)
        await self._redraw(itx, lb)

    async def on_select(self, itx: discord.Interaction, act: str, cid: int, values: list) -> None:
        lb = self.rt.book.get(cid)
        if lb is None:
            return await self._redraw(itx, None)
        if itx.user.id != lb.owner:
            return await self._say(itx, "Only the lobby owner can do that.")
        if lb.private or not values or not values[0].isdigit():
            return await self._redraw(itx, lb)
        n = int(values[0])
        if act == "curse" and 0 <= n < len(Grade):
            npc = {"kind": "curse", "arg": n, "label": f"{GRADE_NAME[n]} curse"}
        elif act.startswith("npc") and 0 <= n < len(NPC_ROSTER):
            npc = {"kind": "npc", "arg": n, "label": NPC_ROSTER[n][0]}
        else:
            return await self._redraw(itx, lb)

        def add(x):
            if len(x.npcs) >= 8:
                return False
            x.npcs.append(npc)
        await self._redraw(itx, self.rt.book.update(cid, add))

    async def _start(self, itx: discord.Interaction, lb: Lobby, mode: str) -> None:
        if not lb.players:
            return await self._say(itx, "Nobody has joined a team.")
        missing = [u for u in lb.players if u not in lb.ready]
        if missing:
            return await self._say(itx, "Not everyone is ready: " + ", ".join(f"<@{u}>" for u in missing))
        if lb.private and mode != "pvp":
            return await self._say(itx, "A private lobby is for PvP only.")
        if mode == "spar" and not lb.npcs and len(lb.sides()) < 2:
            return await self._say(itx, "Add spar opponents, or put players on two or more sides.")
        if mode == "pvp" and len(lb.sides()) < 2:
            return await self._say(itx, "PvP needs at least two sides: two teams, or two players on the Field.")
        started: list = []

        def begin(x):                                       # atomically: only one Start wins
            if x.starting_until > time.time():
                return False
            x.starting_until = time.time() + START_GUARD
            started.append(True)
        lb = self.rt.book.update(lb.channel_id, begin)
        if not started or lb is None:
            return await self._say(itx, "A fight is already starting.")
        await self._redraw(itx, lb)
        asyncio.create_task(self.start(itx.guild, lb, mode, itx.channel))

    # ---- fights ---------------------------------------------------------------------------------
    async def start(self, guild: discord.Guild, lb: Lobby, mode: str, channel=None) -> None:
        channel = channel or self.rt.channel(lb.channel_id)
        self.rt.remember(channel)
        try:
            if mode == "spar":
                await self.spar(guild, lb, channel)
            else:
                ok, msg = await self.rt.run(guild, channel, self._real, lb, mode)
                if not ok:
                    msg = "The colony is busy on another bot process. Try again in a moment."
                if msg:
                    await channel.send(view=style.panel(self.bot, "Lobby", msg, accent=style.LOBBY))
        except Exception as e:
            await channel.send(f"The fight broke off: `{type(e).__name__}: {e}`")
            raise
        finally:
            def done(x):
                x.starting_until = 0.0
                x.ready.clear()
            fresh = self.rt.book.update(lb.channel_id, done)
            if fresh is not None:
                await channel.send(view=lobby_view(self, fresh))

    def _real(self, game, lb: Lobby, mode: str) -> Optional[str]:
        """Hunt or PvP, in the colony, on the battle thread. Returns a message for the lobby, if any."""
        owner = game.player(lb.owner)
        if owner is None:
            return "The owner has no living character here."
        nid = owner.node
        busy = game.in_battle
        here = [p for u in lb.players if (p := game.player(u)) is not None and nid in game.where(p)
                and p.user_id not in busy]
        away = [u for u in lb.players if game.player(u) is None or nid not in game.where(game.player(u))]
        note = (" Not at node %d, so not in it: " % nid + ", ".join(f"<@{u}>" for u in away)) if away else ""
        if not here:
            return "Nobody from the lobby is free to fight at the owner's node."
        if mode == "hunt":
            roamers = [r for r in game.world.roamers if not r.respawn_at and not r.engaged and r.node == nid][:3]
            if not roamers:
                return (f"There are no curses at node {nid}. `/look` shows what is nearby; move toward them, or "
                        "let time pass and they will come to you.")
            game.encounter(nid, roamers, here)
        else:
            sides = {p.user_id: lb.side_of(int(p.user_id)) for p in here}
            if len(set(sides.values())) < 2:
                return f"At least two sides need someone at node {nid}." + note
            starter = lb.side_of(lb.owner)
            for p in here:
                if sides[p.user_id] == starter:            # the side that started it: Judgeman hears of it
                    p.crimes.add(Crime.ASSAULT, nid, game.day())
            names = sorted({t for t in TEAMS for u in lb.teams[t] if str(u) in sides})
            game.fight([(game.present(p, nid), sides[p.user_id]) for p in here], nid,
                       " vs ".join(names) + (" (every one for themselves)" if FIELD in names else "") + "!")
        game.save()
        return ("The fight is over." + note) if note else None

    async def spar(self, guild: discord.Guild, lb: Lobby, channel) -> None:
        """Practice: everyone fights with a copy of their character, so nothing is saved."""
        rt = self.rt
        game = rt.session(guild)
        busy = game.in_battle
        players = [u for u in lb.players if str(u) not in busy]
        if not players:
            await channel.send(view=style.panel(self.bot, "Lobby", "Everyone here is already in a fight.",
                                                accent=style.LOBBY))
            return
        game.enter_spar(players)                           # busy for the colony too, until it is over
        try:
            colony = Colony(str(guild.id), game.colony.name, rules=list(game.colony.rules))   # a throwaway copy
            io = DiscordIO(self.bot, channel, asyncio.get_running_loop())
            b = Battle(str(guild.id), seed=int(self.rng.integers(1 << 30)), io=io, colony=colony, cache=rt.cache)
            for uid in players:
                rec = game.player(uid)
                if rec is not None:
                    b.add(copy.deepcopy(rec).to_spec("human"), lb.side_of(uid))
            for npc in lb.npcs:
                b.add(spar_opponent(npc, self.rng), 50)
            standard_field(b)
            io.say(f"*** {lb.name}: a spar (nothing here is saved) ***")
            result = await run_battle(b, io, rt.pool)
            await channel.send(view=style.panel(self.bot, "Spar over",
                                                f"{style.stat('Rounds', result['rounds'])}\n"
                                                f"{style.stat('Standing', ', '.join(result['winners']) or 'nobody')}",
                                                accent=style.LOBBY))
        finally:
            game.leave_spar(players)


async def setup(bot: commands.Bot) -> None:
    bot.add_dynamic_items(LobbyButton, LobbySelect)
    await bot.add_cog(LobbyCog(bot))
