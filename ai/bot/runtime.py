"""Shared state for the bot: one ColonySession per Discord server, lobbies in Redis, a battle thread pool.

What lives where
    Redis (BattleCache)   the colony locks and versions, who is fighting, lobbies, live battle
                          snapshots, post-battle character snapshots
    the database          colonies, maps, characters, the global leaderboard and market
    this process          the loaded ColonySessions (reloaded when another process saves), running
                          battles and their Discord views, a registry of channel objects
"""
from __future__ import annotations

import asyncio
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

import discord

from ..colony import ColonyBusy, ColonySession
from ..storage import BattleCache, GameStore
from .bridge import DiscordIO
from .lobbies import Lobby, LobbyBook

# The bot's developers: may use /devcreate (any technique) and /mod anywhere. More ids, comma
# separated, in KOGANE_DEV_IDS.
DEV_IDS = {"677718946270543882"} | {x.strip() for x in os.environ.get("KOGANE_DEV_IDS", "").split(",") if x.strip()}


def is_dev(user_id) -> bool:
    return str(user_id) in DEV_IDS


class Runtime:
    def __init__(self, bot: discord.Client):
        self.bot = bot
        # CULLING_DB = sqlite (default; file at CULLING_SQLITE) | dynamodb | json - see ai/STORAGE.md
        self.store = GameStore(local_path=os.environ.get("CULLING_SAVE", "culling_save.json"))
        self.cache = BattleCache()
        self.store.coord = self.cache
        self.book = LobbyBook(self.cache)
        self.sessions: dict = {}
        self.channels: dict = {}                      # channel id -> channel object seen by this process
        # Every battle in progress holds one thread (parked while it waits for players), so the pool
        # is the ceiling on simultaneous battles + commands. Threads waiting on input cost ~nothing.
        self.pool = ThreadPoolExecutor(max_workers=int(os.environ.get("KOGANE_MAX_BATTLES", "256")),
                                       thread_name_prefix="battle")
        self.loop = None

    # ---- channels --------------------------------------------------------------------------------
    def remember(self, channel) -> None:
        if channel is not None and getattr(channel, "id", None) is not None:
            self.channels[int(channel.id)] = channel

    def channel(self, channel_id):
        """The channel (or thread) object for an id, if this process can see it."""
        ch = self.channels.get(int(channel_id))
        if ch is None:
            getter = getattr(self.bot, "get_channel", None)
            ch = getter(int(channel_id)) if getter else None
            if ch is not None:
                self.channels[int(channel_id)] = ch
        return ch

    # ---- lobbies: only players in one can fight (or be attacked) ----------------------------
    def lobby_of(self, guild_id, user_id) -> Optional[Lobby]:
        return self.book.of_user(guild_id, user_id)

    def _hooks(self, game: ColonySession, guild_id: int) -> None:
        def can_fight(p):                     # curses only find players on a team in a PUBLIC lobby
            where = self.book.members(guild_id).get(str(p.user_id))
            return where is not None and not where[1]

        def pvp_check(me, foe):
            members = self.book.members(guild_id, fresh=True)
            mine, theirs = members.get(str(me.user_id)), members.get(str(foe.user_id))
            if mine is None:
                return "Fights need a lobby: join one first (`/lobby create`, or a Join button)."
            if theirs is None or theirs[0] != mine[0]:
                return f"{foe.name} is not in your lobby. You can only attack players in the same lobby."
            return None

        def io_for(party):                    # a fight is shown in its players' lobby thread
            members = self.book.members(guild_id)
            where = next((members[str(p.user_id)] for p in party if str(p.user_id) in members), None)
            ch = self.channel(where[0]) if where is not None else None
            if ch is None or getattr(game.io, "dest", None) is ch or self.loop is None:
                return game.io
            return DiscordIO(self.bot, ch, self.loop)
        game.can_fight, game.pvp_check, game.io_for = can_fight, pvp_check, io_for

    def session(self, guild: discord.Guild) -> ColonySession:
        gid = str(guild.id)
        if gid not in self.sessions:
            game = ColonySession(gid, self.store, self.cache, name=guild.name,
                                 managers=[str(guild.owner_id)] if guild.owner_id else [])
            game.concurrent = True                # fights let go of the colony's lock (colony.py)
            self._hooks(game, guild.id)
            self.sessions.setdefault(gid, game)
        return self.sessions[gid]

    async def run(self, guild: discord.Guild, channel, fn, *args, wait: bool = True):
        """Run ``fn(session, *args)`` on a battle thread, holding the colony's lock.

        The lock (this process's, then the colony's in Redis) is only held while the command works
        on the colony; a fight it starts releases it for as long as the fight lasts (the fighters
        are marked busy instead), so any number of fights and commands go on side by side in one
        colony, on one bot process or several. Fights are played in ``channel``, or in the lobby's
        thread. Returns (True, result) - or (False, None) if another process kept the colony too long.
        """
        game = self.session(guild)
        self.loop = asyncio.get_running_loop()
        self.remember(channel)
        io = DiscordIO(self.bot, channel, self.loop)

        def work():
            try:
                game.acquire()
            except ColonyBusy:
                return False, None
            try:
                game.io = io                              # this thread's fights go through this io
                return True, fn(game, *args)
            finally:
                game.release()
                io.flush()                                # after the lock: it waits on Discord
        return await self.loop.run_in_executor(self.pool, work)

    async def command(self, guild: discord.Guild, channel, user_id, line: str) -> Optional[str]:
        """One colony command for a user. None when the colony could not be had (another process)."""
        def go(game: ColonySession):
            me = game.player(user_id)
            if me is None:
                return "You have no living character in this colony. Use `/create` first."
            out: list = []
            game.command(me, line, lambda s: out.append(str(s)))
            return "\n".join(out).strip("\n") or "Done."
        ok, text = await self.run(guild, channel, go)
        return text if ok else None

    async def exchange(self, src: discord.Guild, dst: discord.Guild, user_id) -> Optional[str]:
        """Move a user's character from ``src`` to ``dst`` - or, if they have one in each, trade the
        two. Both colonies are held (in server-id order, so two transfers cannot deadlock)."""
        a, b = self.session(src), self.session(dst)
        self.loop = asyncio.get_running_loop()
        first, second = sorted((a, b), key=lambda g: g.server_id)

        def work():
            try:
                first.acquire()
            except ColonyBusy:
                return None
            try:
                try:
                    second.acquire()
                except ColonyBusy:
                    return None
                try:
                    return a.exchange(b, user_id)
                finally:
                    second.release()
            finally:
                first.release()
        text = await self.loop.run_in_executor(self.pool, work)
        if text is not None and "leaves" in text:             # they are someone else in each colony now
            self.book.remove_user(src.id, user_id)
            self.book.remove_user(dst.id, user_id)
        return text
