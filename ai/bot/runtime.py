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
        self.store = GameStore(local_path=os.environ.get("CULLING_SAVE", "culling_save.json"))
        self.cache = BattleCache()
        self.sessions: dict = {}
        self.locks: dict = {}
        self.busy_users: set = set()          # users in a lobby (spar) fight right now

    def lock(self, guild_id) -> asyncio.Lock:
        return self.locks.setdefault(str(guild_id), asyncio.Lock())

    def session(self, guild: discord.Guild) -> ColonySession:
        gid = str(guild.id)
        if gid not in self.sessions:
            self.sessions[gid] = ColonySession(gid, self.store, self.cache, name=guild.name,
                                               managers=[str(guild.owner_id)] if guild.owner_id else [])
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
            io = DiscordIO(self.bot, channel, asyncio.get_running_loop())
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
