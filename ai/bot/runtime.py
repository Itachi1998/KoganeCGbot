"""Shared state for the bot: one ColonySession per Discord server, run one command at a time."""
from __future__ import annotations

import asyncio
import os
from typing import Optional

import discord

from ..colony import ColonySession
from ..storage import BattleCache, GameStore
from .bridge import DiscordIO


class Runtime:
    def __init__(self, bot: discord.Client):
        self.bot = bot
        # CULLING_DB = sqlite (default; file at CULLING_SQLITE) | dynamodb | json - see ai/STORAGE.md
        self.store = GameStore(local_path=os.environ.get("CULLING_SAVE", "culling_save.json"))
        self.cache = BattleCache()
        self.sessions: dict = {}
        self.locks: dict = {}
        self.busy_users: set = set()          # users in a lobby spar right now
        self.lobbies: dict = {}               # channel id -> Lobby (cogs/lobby.py)
        self.loop = None

    # ---- lobbies: only players in one can fight (or be attacked) ----------------------------
    def lobby_of(self, guild_id, user_id):
        return next((lb for lb in self.lobbies.values()
                     if lb.guild_id == int(guild_id) and int(user_id) in lb.members), None)

    def _hooks(self, game: ColonySession, guild_id: int) -> None:
        def can_fight(p):
            return self.lobby_of(guild_id, p.user_id) is not None

        def pvp_check(me, foe):
            mine, theirs = self.lobby_of(guild_id, me.user_id), self.lobby_of(guild_id, foe.user_id)
            if mine is None:
                return "Fights need a lobby: join one first (`/lobby create`, or a Join button)."
            if theirs is not mine:
                return f"{foe.name} is not in your lobby. You can only attack players in the same lobby."
            return None

        def io_for(party):
            lb = next((self.lobby_of(guild_id, p.user_id) for p in party
                       if self.lobby_of(guild_id, p.user_id) is not None), None)
            if lb is None or getattr(game.io, "dest", None) is lb.channel:
                return game.io
            return DiscordIO(self.bot, lb.channel, self.loop)      # the fight is shown in the lobby's thread
        game.can_fight, game.pvp_check, game.io_for = can_fight, pvp_check, io_for

    def lock(self, guild_id) -> asyncio.Lock:
        return self.locks.setdefault(str(guild_id), asyncio.Lock())

    def session(self, guild: discord.Guild) -> ColonySession:
        gid = str(guild.id)
        if gid not in self.sessions:
            self.sessions[gid] = ColonySession(gid, self.store, self.cache, name=guild.name,
                                               managers=[str(guild.owner_id)] if guild.owner_id else [])
            self._hooks(self.sessions[gid], guild.id)
        return self.sessions[gid]

    async def run(self, guild: discord.Guild, channel, fn, *args, wait: bool = False):
        """Run ``fn(session, *args)`` in a worker thread with this colony to itself.

        Fights started by the command are played in ``channel``. Returns (ok, result); ok is False
        when the colony is busy and ``wait`` is not set.
        """
        lock = self.lock(guild.id)
        if lock.locked() and not wait:
            return False, None
        async with lock:
            game = self.session(guild)
            self.loop = asyncio.get_running_loop()
            io = DiscordIO(self.bot, channel, self.loop)
            game.io = io
            try:
                return True, await asyncio.to_thread(fn, game, *args)
            finally:
                await asyncio.to_thread(io.flush)

    async def command(self, guild: discord.Guild, channel, user_id, line: str) -> Optional[str]:
        """One colony command for a user. None when the colony is busy with something else."""
        def go(game: ColonySession):
            me = game.player(user_id)
            if me is None:
                return "You have no living character in this colony. Use `/create` first."
            out: list = []
            game.command(me, line, lambda s: out.append(str(s)))
            return "\n".join(out).strip("\n") or "Done."
        ok, text = await self.run(guild, channel, go)
        return text if ok else None
