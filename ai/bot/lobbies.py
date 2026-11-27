"""Lobby state, kept in Redis (through BattleCache) so it survives a restart and is shared by every
bot process.  Without Redis it lives in this process's memory.

    cg:doc:lobby:<channel id>            the lobby, as JSON (expires LOBBY_TTL after its last change)
    cg:map:lobbies:<guild id>            channel id -> "1" (the lobbies of a server)
    cg:map:lobby_members:<guild id>      user id -> "<channel id>:<1 if private else 0>" (who is on a team where)

A lobby is changed with ``LobbyBook.update(channel_id, fn)``: read, change, write under the lobby's
own lock, so two people pressing buttons at once (even on two bot processes) cannot lose a change.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, Optional

TEAMS = ("Team A", "Team B", "Team C", "Field")
FIELD = "Field"                    # everyone on the field fights for themselves
LOBBY_TTL = 24 * 3600              # an untouched lobby is forgotten after a day
START_GUARD = 90.0                 # seconds a lobby counts as "starting" before its fighters are marked


@dataclass
class Lobby:
    guild_id: int
    owner: int
    name: str
    channel_id: int
    private: bool = False                              # invite-only, PvP only, and no curse finds its members
    invited: list = field(default_factory=list)
    teams: dict = field(default_factory=lambda: {t: [] for t in TEAMS})    # team -> user ids
    spectators: list = field(default_factory=list)
    ready: list = field(default_factory=list)
    npcs: list = field(default_factory=list)           # spar opponents: {"kind": "curse"|"npc", "arg": int, "label": str}
    starting_until: float = 0.0                        # a fight is being set up (guards against a double start)

    @property
    def players(self) -> list:
        return [u for t in TEAMS for u in self.teams.get(t, [])]

    @property
    def members(self) -> set:
        """Who can fight (and be attacked): the players on a team. Spectators can't."""
        return set(self.players)

    def side_of(self, uid: int) -> int:
        """Battle team number: Team A/B/C are 0/1/2; each player on the Field is a side of their own."""
        for i, t in enumerate(TEAMS):
            if uid in self.teams.get(t, []):
                return 10 + self.teams[t].index(uid) if t == FIELD else i
        return -1

    def sides(self) -> set:
        return {self.side_of(u) for u in self.players}

    def leave(self, uid: int) -> bool:
        """Take a user off every team (and out of the spectators). True if anything changed."""
        changed = False
        for ids in self.teams.values():
            if uid in ids:
                ids.remove(uid)
                changed = True
        if uid in self.spectators:
            self.spectators.remove(uid)
            changed = True
        if uid in self.ready:
            self.ready.remove(uid)
            changed = True
        return changed

    def to_doc(self) -> dict:
        return dict(self.__dict__)

    @classmethod
    def from_doc(cls, d: dict) -> "Lobby":
        lb = cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})
        for t in TEAMS:
            lb.teams.setdefault(t, [])
        return lb


class LobbyBook:
    def __init__(self, cache):
        self.cache = cache
        self._seen: dict = {}                          # guild id -> (when, members): a half-second memo

    # ---- reading ------------------------------------------------------------------------------
    def get(self, channel_id) -> Optional[Lobby]:
        doc = self.cache.get_json(f"lobby:{int(channel_id)}")
        return Lobby.from_doc(doc) if doc else None

    def in_guild(self, guild_id) -> list:
        out = []
        for cid in list(self.cache.map_all(f"lobbies:{int(guild_id)}")):
            lb = self.get(cid)
            if lb is None:                             # expired: tidy the index
                self.cache.map_del(f"lobbies:{int(guild_id)}", cid)
            else:
                out.append(lb)
        return out

    def members(self, guild_id, fresh: bool = False) -> dict:
        """user id (str) -> (channel id, private) for everyone on a lobby team in this server.
        Memoised for half a second: the colony asks once per player per hour of game time."""
        gid = int(guild_id)
        seen = self._seen.get(gid)
        if not fresh and seen is not None and time.monotonic() - seen[0] < 0.5:
            return seen[1]
        out = {}
        for uid, where in self.cache.map_all(f"lobby_members:{gid}").items():
            cid, _, private = where.partition(":")
            out[uid] = (int(cid), private == "1")
        self._seen[gid] = (time.monotonic(), out)
        return out

    def of_user(self, guild_id, user_id) -> Optional[Lobby]:
        where = self.members(guild_id, fresh=True).get(str(user_id))
        if where is None:
            return None
        lb = self.get(where[0])
        if lb is None or int(user_id) not in lb.members:        # the lobby expired, or the map is behind
            self.cache.map_del(f"lobby_members:{int(guild_id)}", user_id)
            self._seen.pop(int(guild_id), None)
            return None
        return lb

    # ---- writing ------------------------------------------------------------------------------
    def put(self, lb: Lobby) -> None:
        self.cache.put_json(f"lobby:{lb.channel_id}", lb.to_doc(), ttl=LOBBY_TTL)
        self.cache.map_set(f"lobbies:{lb.guild_id}", lb.channel_id, "1")
        name = f"lobby_members:{lb.guild_id}"
        mark = f"{lb.channel_id}:{1 if lb.private else 0}"
        here = {str(u) for u in lb.members}
        current = self.cache.map_all(name)
        gone = [u for u, where in current.items() if where.partition(":")[0] == str(lb.channel_id) and u not in here]
        self.cache.map_del(name, *gone)
        for u in here:
            if current.get(u) != mark:
                self.cache.map_set(name, u, mark)
        self._seen.pop(lb.guild_id, None)

    def delete(self, lb: Lobby) -> None:
        self.cache.drop(f"lobby:{lb.channel_id}")
        self.cache.map_del(f"lobbies:{lb.guild_id}", lb.channel_id)
        name = f"lobby_members:{lb.guild_id}"
        gone = [u for u, where in self.cache.map_all(name).items() if where.partition(":")[0] == str(lb.channel_id)]
        self.cache.map_del(name, *gone)
        self._seen.pop(lb.guild_id, None)

    def update(self, channel_id, fn: Callable) -> Optional[Lobby]:
        """Change a lobby atomically: ``fn(lobby)`` under the lobby's lock. Returns the lobby as saved
        (None if it no longer exists). ``fn`` may return False to say "nothing to save"."""
        name = f"lobby:{int(channel_id)}"
        token = self.cache.acquire(name, ttl=10, wait=5)
        try:
            lb = self.get(channel_id)
            if lb is None:
                return None
            if fn(lb) is not False:
                self.put(lb)
            return lb
        finally:
            self.cache.release(name, token)

    def remove_user(self, guild_id, user_id, except_channel=None) -> None:
        """Take a user out of whatever lobby they are in in a server (they joined another, or left the colony)."""
        where = self.members(guild_id, fresh=True).get(str(user_id))
        if where is None or where[0] == except_channel:
            return
        if self.update(where[0], lambda lb: lb.leave(int(user_id))) is None:      # that lobby has expired
            self.cache.map_del(f"lobby_members:{int(guild_id)}", user_id)
            self._seen.pop(int(guild_id), None)
