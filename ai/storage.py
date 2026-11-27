"""Storage adapters.

BattleCache  Redis.  A live battle is snapshotted after every round (cg:battle:<server>:<id>), and
             every character who fought is snapshotted with their stats after the battle
             (cg:char:<server>:<user>). Falls back to memory when Redis is unreachable
             (set REDIS_REQUIRED=1 to refuse to start instead).
GameStore    Long-term state: colonies, players, maps. SQLite by default (testing, small servers),
             DynamoDB single table for production - the same packed items in both (see ``pack``
             and ai/STORAGE.md); ``python -m ai.migrate`` moves everything between them.

DynamoDB key design
    PK = SERVER#<server_id>   SK = META                 colony: rules, manager user ids
    PK = SERVER#<server_id>   SK = PLAYER#<user_id>     one character per user per server
    PK = SERVER#<server_id>   SK = MAP                  seed + broken/looted bitmasks + roamers
    GSI1: GSI1PK = USER#<user_id>, GSI1SK = SERVER#<server_id>   all of a user's characters
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import pickle
import sqlite3
import threading
import time
import uuid
import zlib
from decimal import Decimal
from typing import Optional

import numpy as np

from .records import PlayerRecord
from .rules import Colony


# ======================================================================================
# Redis
# ======================================================================================
class BattleCache:
    def __init__(self, url: Optional[str] = None, ttl: int = 6 * 3600):
        self.ttl = ttl
        self._mem: dict = {}
        self._mutex = threading.Lock()                   # guards _mem when Redis is not there
        self.r = None
        try:
            import redis
            self.r = redis.Redis.from_url(url or os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
                                          socket_connect_timeout=0.5)
            self.r.ping()
        except Exception as e:
            self.r = None                                # no server / no library: stay in memory
            if os.environ.get("REDIS_REQUIRED"):
                raise RuntimeError(f"REDIS_REQUIRED is set but Redis is unreachable: {e}")
            print(f"[storage] Redis unavailable ({type(e).__name__}); battle cache in memory")

    @property
    def backend(self) -> str:
        return "redis" if self.r is not None else "memory"

    @staticmethod
    def key(server_id, battle_id) -> str:
        return f"cg:battle:{server_id}:{battle_id}"

    def save(self, battle) -> None:
        k = self.key(battle.server_id, battle.id)
        blob = pickle.dumps(battle, protocol=pickle.HIGHEST_PROTOCOL)
        tail = "\n".join(battle.log[-40:])
        if self.r is not None:
            pipe = self.r.pipeline()
            pipe.hset(k, mapping={"state": blob, "round": battle.round, "log": tail})
            pipe.expire(k, self.ttl)
            pipe.execute()
        else:
            self._mem[k] = {"state": blob, "round": battle.round, "log": tail}

    def load(self, server_id, battle_id):
        """Returns the Battle (call ``.attach(io, world, cache)`` on it) or None.

        Snapshots are pickles: only ever load them from a Redis instance you control.
        """
        k = self.key(server_id, battle_id)
        blob = self.r.hget(k, "state") if self.r is not None else self._mem.get(k, {}).get("state")
        return pickle.loads(blob) if blob else None

    def delete(self, server_id, battle_id) -> None:
        k = self.key(server_id, battle_id)
        if self.r is not None:
            self.r.delete(k)
        else:
            self._mem.pop(k, None)

    # ---- characters, after every fight ---------------------------------------------------
    CHAR_TTL = 30 * 86400                               # a cache: the database keeps them for good

    @staticmethod
    def char_key(server_id, user_id) -> str:
        return f"cg:char:{server_id}:{user_id}"

    def save_character(self, rec, extra: Optional[dict] = None) -> None:
        """Snapshot a character right after a battle: the whole record, and the stats it fights with."""
        from .constants import Stat
        st = rec.to_spec().stats
        stats = {s.name.lower(): round(float(st[s]), 2) for s in Stat}
        stats.update(old_stats=rec.old_stats, skills=getattr(rec, "skills", None),
                     skill_points=getattr(rec, "skill_points", 0), level=rec.level, xp=rec.xp,
                     points=rec.points, alive=rec.alive, condition=rec.condition_text())
        mapping = {"record": json.dumps(_to_json(rec.to_item())), "stats": json.dumps(_to_json(stats)),
                   "saved_at": time.time(), **{k: json.dumps(_to_json(v)) for k, v in (extra or {}).items()}}
        k = self.char_key(rec.server_id, rec.user_id)
        if self.r is not None:
            pipe = self.r.pipeline()
            pipe.hset(k, mapping=mapping)
            pipe.expire(k, self.CHAR_TTL)
            pipe.execute()
        else:
            self._mem[k] = mapping

    def load_character(self, server_id, user_id) -> Optional[dict]:
        """{"record": PlayerRecord, "stats": {...}, "saved_at": float} or None."""
        k = self.char_key(server_id, user_id)
        raw = self.r.hgetall(k) if self.r is not None else self._mem.get(k)
        if not raw:
            return None
        raw = {(a.decode() if isinstance(a, bytes) else a): (b.decode() if isinstance(b, bytes) else b)
               for a, b in raw.items()}
        return {"record": PlayerRecord.from_item(_from_json(json.loads(raw["record"]))),
                "stats": _from_json(json.loads(raw["stats"])), "saved_at": float(raw["saved_at"])}

    def lock(self, server_id, battle_id, owner: str, seconds: int = 30) -> bool:
        """One command at a time per battle (several bot workers may race)."""
        k = self.key(server_id, battle_id) + ":lock"
        if self.r is not None:
            return bool(self.r.set(k, owner, nx=True, ex=seconds))
        if k in self._mem:
            return False
        self._mem[k] = owner
        return True

    def unlock(self, server_id, battle_id) -> None:
        k = self.key(server_id, battle_id) + ":lock"
        if self.r is not None:
            self.r.delete(k)
        else:
            self._mem.pop(k, None)

    # ---- coordination: shared by every thread and every bot process on this Redis ---------------
    # Named locks (owned: only the holder's token releases them; they expire if the holder dies),
    # version counters (has someone else changed this since I looked?), expiring sets (who is in a
    # fight right now - entries lapse by themselves if their process dies) and small JSON documents
    # (lobbies). Without Redis they live in this process's memory, which is right for one process.
    _RELEASE = "if redis.call('get', KEYS[1]) == ARGV[1] then return redis.call('del', KEYS[1]) else return 0 end"
    _EXTEND = ("if redis.call('get', KEYS[1]) == ARGV[1] then return redis.call('pexpire', KEYS[1], ARGV[2]) "
               "else return 0 end")

    def acquire(self, name: str, ttl: float = 30.0, wait: float = 30.0) -> Optional[str]:
        """Take the lock ``name``. Returns the token to release it with, or None if it could not be
        had within ``wait`` seconds. It frees itself after ``ttl`` seconds if never released."""
        k, token = f"cg:lock:{name}", uuid.uuid4().hex
        deadline, pause = time.monotonic() + wait, 0.002
        while True:
            if self.r is not None:
                if self.r.set(k, token, nx=True, px=int(ttl * 1000)):
                    return token
            else:
                with self._mutex:
                    held = self._mem.get(k)
                    if held is None or held[1] <= time.monotonic():
                        self._mem[k] = (token, time.monotonic() + ttl)
                        return token
            if time.monotonic() >= deadline:
                return None
            time.sleep(pause)
            pause = min(pause * 2, 0.05)

    def release(self, name: str, token: Optional[str]) -> bool:
        """Let go of ``name`` - only if ``token`` still holds it (it may have expired and been retaken)."""
        if token is None:
            return False
        k = f"cg:lock:{name}"
        if self.r is not None:
            return bool(self.r.eval(self._RELEASE, 1, k, token))
        with self._mutex:
            if self._mem.get(k, (None,))[0] == token:
                del self._mem[k]
                return True
        return False

    def extend(self, name: str, token: Optional[str], ttl: float = 30.0) -> bool:
        """Push a held lock's expiry out (a long save). False if it is no longer ours."""
        if token is None:
            return False
        k = f"cg:lock:{name}"
        if self.r is not None:
            return bool(self.r.eval(self._EXTEND, 1, k, token, int(ttl * 1000)))
        with self._mutex:
            if self._mem.get(k, (None,))[0] == token:
                self._mem[k] = (token, time.monotonic() + ttl)
                return True
        return False

    def version(self, name: str) -> int:
        k = f"cg:ver:{name}"
        v = self.r.get(k) if self.r is not None else self._mem.get(k)
        return int(v) if v else 0

    def bump(self, name: str) -> int:
        k = f"cg:ver:{name}"
        if self.r is not None:
            return int(self.r.incr(k))
        with self._mutex:
            self._mem[k] = int(self._mem.get(k, 0)) + 1
            return self._mem[k]

    def mark(self, name: str, members, ttl: float) -> None:
        """Put ``members`` in the expiring set ``name`` for ``ttl`` seconds (again = refresh)."""
        members = [str(m) for m in members]
        if not members:
            return
        k, until = f"cg:set:{name}", time.time() + ttl
        if self.r is not None:
            self.r.zadd(k, {m: until for m in members})
            self.r.expire(k, int(ttl) + 60)
        else:
            with self._mutex:
                self._mem.setdefault(k, {}).update({m: until for m in members})

    def unmark(self, name: str, members) -> None:
        members = [str(m) for m in members]
        if not members:
            return
        k = f"cg:set:{name}"
        if self.r is not None:
            self.r.zrem(k, *members)
        else:
            with self._mutex:
                for m in members:
                    self._mem.get(k, {}).pop(m, None)

    def marked(self, name: str) -> set:
        """The members of ``name`` that have not expired."""
        k, now = f"cg:set:{name}", time.time()
        if self.r is not None:
            return {m.decode() if isinstance(m, bytes) else m for m in self.r.zrangebyscore(k, now, "+inf")}
        with self._mutex:
            return {m for m, until in self._mem.get(k, {}).items() if until > now}

    def put_json(self, name: str, value, ttl: Optional[float] = None) -> None:
        k, raw = f"cg:doc:{name}", json.dumps(_to_json(value), separators=(",", ":"))
        if self.r is not None:
            self.r.set(k, raw, ex=int(ttl) if ttl else None)
        else:
            with self._mutex:
                self._mem[k] = (raw, time.time() + ttl if ttl else None)

    def get_json(self, name: str):
        k = f"cg:doc:{name}"
        if self.r is not None:
            raw = self.r.get(k)
        else:
            with self._mutex:
                raw, until = self._mem.get(k, (None, None))
                if until is not None and until <= time.time():
                    self._mem.pop(k, None)
                    raw = None
        return _from_json(json.loads(raw)) if raw else None

    def drop(self, name: str) -> None:
        k = f"cg:doc:{name}"
        if self.r is not None:
            self.r.delete(k)
        else:
            with self._mutex:
                self._mem.pop(k, None)

    def map_set(self, name: str, field, value) -> None:
        k = f"cg:map:{name}"
        if self.r is not None:
            self.r.hset(k, str(field), str(value))
        else:
            with self._mutex:
                self._mem.setdefault(k, {})[str(field)] = str(value)

    def map_del(self, name: str, *fields) -> None:
        k = f"cg:map:{name}"
        if not fields:
            return
        if self.r is not None:
            self.r.hdel(k, *[str(f) for f in fields])
        else:
            with self._mutex:
                for f in fields:
                    self._mem.get(k, {}).pop(str(f), None)

    def map_all(self, name: str) -> dict:
        k = f"cg:map:{name}"
        if self.r is not None:
            return {(a.decode() if isinstance(a, bytes) else a): (b.decode() if isinstance(b, bytes) else b)
                    for a, b in self.r.hgetall(k).items()}
        with self._mutex:
            return dict(self._mem.get(k, {}))


# ======================================================================================
# DynamoDB
# ======================================================================================
def _to_db(v):
    """Python -> DynamoDB types (floats become Decimal, numpy scalars become Python)."""
    if isinstance(v, bool) or v is None or isinstance(v, (str, bytes, int)):
        return v
    if isinstance(v, (float, np.floating)):
        return Decimal(str(float(v)))
    if isinstance(v, np.integer):
        return int(v)
    if isinstance(v, dict):
        return {str(k): _to_db(x) for k, x in v.items()}
    if isinstance(v, (list, tuple, set, frozenset)):
        return [_to_db(x) for x in v]
    raise TypeError(f"cannot store {type(v).__name__}")


def _from_db(v):
    if isinstance(v, Decimal):
        return int(v) if v == v.to_integral_value() else float(v)
    if hasattr(v, "value") and not isinstance(v, (str, bytes)):        # boto3 Binary
        return bytes(v.value)
    if isinstance(v, dict):
        return {k: _from_db(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [_from_db(x) for x in v]
    return v


def _to_json(v):
    if isinstance(v, bytes):
        return {"__b64__": base64.b64encode(v).decode()}
    if isinstance(v, (np.floating, np.integer)):
        return v.item()
    if isinstance(v, dict):
        return {str(k): _to_json(x) for k, x in v.items()}
    if isinstance(v, (list, tuple, set, frozenset)):
        return [_to_json(x) for x in v]
    return v


def _from_json(v):
    if isinstance(v, dict):
        if set(v) == {"__b64__"}:
            return base64.b64decode(v["__b64__"])
        return {k: _from_json(x) for k, x in v.items()}
    if isinstance(v, list):
        return [_from_json(x) for x in v]
    return v


# ---- the stored item format (the same bytes in SQLite and DynamoDB) ----------------------------
PACK_VERSION = 1
GSI_ATTRS = ("name", "level", "alive", "points")      # small, readable copies kept beside the blob (players)


def pack(pk: str, sk: str, item: dict) -> dict:
    """A game object as a stored item: the keys, a few small readable attributes, and the whole object
    as one zlib-compressed JSON blob ``d``. One compact binary attribute instead of dozens of nested
    ones keeps most items under 1 KB, i.e. one DynamoDB write unit per save."""
    blob = zlib.compress(json.dumps(_to_json(item), separators=(",", ":"), sort_keys=True).encode(), 6)
    out = {"PK": pk, "SK": sk, "v": PACK_VERSION, "d": blob}
    if "GSI1PK" in item:                                # players only: a sparse index
        out["GSI1PK"], out["GSI1SK"] = item["GSI1PK"], item["GSI1SK"]
        for k in GSI_ATTRS:
            if k in item:
                out[k] = item[k]
    return out


def _digest(stored: dict) -> bytes:
    """What an item looks like in storage, in 16 bytes: equal digests = nothing to write."""
    return hashlib.blake2b(bytes(stored["d"]) + repr(sorted((k, v) for k, v in stored.items() if k != "d")).encode(),
                           digest_size=16).digest()


def unpack(stored: dict) -> dict:
    d = stored.get("d")
    if d is None:                                       # an unpacked item (written before packing existed)
        return {k: v for k, v in stored.items() if k not in ("PK", "SK", "GSI1PK", "GSI1SK")}
    if hasattr(d, "value"):                             # boto3 Binary
        d = d.value
    return _from_json(json.loads(zlib.decompress(bytes(d))))


class GameStore:
    """Long-term state. Three interchangeable backends with one item format (``pack``):

    sqlite     (default)  one file; for testing and small deployments. CULLING_SQLITE sets the path.
    dynamodb              the single table described at the top of this module. CULLING_DB=dynamodb
    json                  the old JSON file, kept for old saves (CULLING_DB=json)

    ``ai/migrate.py`` copies everything from one backend to another.
    """

    def __init__(self, table: str = "CullingGame", region: Optional[str] = None,
                 endpoint_url: Optional[str] = None, local_path: str = "culling_save.json",
                 use_dynamo: Optional[bool] = None, backend: Optional[str] = None,
                 sqlite_path: Optional[str] = None):
        kind = backend or os.environ.get("CULLING_DB") or ("dynamodb" if (use_dynamo or (
            use_dynamo is None and os.environ.get("CULLING_DYNAMO"))) else "sqlite")
        self.table = None
        self.db = None
        self.local_path = local_path
        self._local: dict = {}
        self._written: dict = {}                        # (pk, sk) -> digest of what storage holds (as last read or
        self._lock = threading.RLock()                  #             written here): unchanged = no write
        self.writes = 0                                 # items actually written (skips do not count)
        self.coord = None                               # a BattleCache: coordinates GLOBAL items between processes
        self._globals: dict = {}                        # sk -> (version seen, item)
        if kind == "dynamodb":
            try:
                import boto3
                self.table = boto3.resource("dynamodb", region_name=region or os.environ.get("AWS_REGION"),
                                            endpoint_url=endpoint_url or os.environ.get("DYNAMO_ENDPOINT")).Table(table)
                self.table.load()
            except Exception as e:
                print(f"[storage] DynamoDB unavailable ({type(e).__name__}: {e}); using SQLite")
                self.table = None
                kind = "sqlite"
        if kind == "sqlite":
            path = sqlite_path or os.environ.get("CULLING_SQLITE", "culling.db")
            self.db = sqlite3.connect(path, check_same_thread=False, isolation_level=None)
            self.db.execute("PRAGMA journal_mode=WAL")
            self.db.execute("PRAGMA synchronous=NORMAL")
            self.db.execute("CREATE TABLE IF NOT EXISTS items (pk TEXT NOT NULL, sk TEXT NOT NULL, "
                            "gsi1pk TEXT, gsi1sk TEXT, item BLOB NOT NULL, PRIMARY KEY (pk, sk))")
            self.db.execute("CREATE INDEX IF NOT EXISTS gsi1 ON items (gsi1pk, gsi1sk) WHERE gsi1pk IS NOT NULL")
            self.sqlite_path = path
        elif kind == "json" and os.path.exists(local_path):
            with open(local_path) as f:
                self._local = _from_json(json.load(f))
        self.kind = kind

    @property
    def backend(self) -> str:
        return {"dynamodb": "dynamodb", "sqlite": f"sqlite ({getattr(self, 'sqlite_path', '')})"}.get(self.kind, "json-file")

    @staticmethod
    def create_table(table: str = "CullingGame", **kw) -> None:
        """One-off setup for a real deployment: on-demand billing, a sparse KEYS+few-attributes index."""
        import boto3
        boto3.client("dynamodb", **kw).create_table(**table_definition(table))

    # ---- primitives --------------------------------------------------------------------
    def _put(self, pk: str, sk: str, item: dict, new_only: bool = False) -> bool:
        stored = pack(pk, sk, item)
        digest = _digest(stored)
        with self._lock:
            if not new_only and self._written.get((pk, sk)) == digest:
                return True                             # nothing changed since the last write: skip it
            if self.table is not None:
                kw = {"ConditionExpression": "attribute_not_exists(PK)"} if new_only else {}
                try:
                    self.table.put_item(Item=_to_db(stored), **kw)
                except Exception as e:
                    if new_only and "ConditionalCheckFailed" in type(e).__name__ + str(e):
                        return False
                    raise
            elif self.db is not None:
                row = (pk, sk, stored.get("GSI1PK"), stored.get("GSI1SK"), _blob(stored))
                if new_only:
                    try:
                        self.db.execute("INSERT INTO items VALUES (?,?,?,?,?)", row)
                    except sqlite3.IntegrityError:
                        return False
                else:
                    self.db.execute("INSERT OR REPLACE INTO items VALUES (?,?,?,?,?)", row)
            else:
                if new_only and sk in self._local.get(pk, {}):
                    return False
                self._local.setdefault(pk, {})[sk] = item
                self._flush()
            self._written[(pk, sk)] = digest
            self.writes += 1
        return True

    def _seen(self, stored: dict) -> dict:
        """Note what storage holds for an item just read (another process may have written it), so
        the next save of the same content is skipped and a save of anything else is not."""
        if stored.get("d") is not None:
            self._written[(stored["PK"], stored["SK"])] = _digest(stored)
        return unpack(stored)

    def _get(self, pk: str, sk: str) -> Optional[dict]:
        with self._lock:
            if self.table is not None:
                item = self.table.get_item(Key={"PK": pk, "SK": sk}, ConsistentRead=True).get("Item")
                if item is None:
                    self._written.pop((pk, sk), None)
                return self._seen(_from_db(item)) if item else None
            if self.db is not None:
                row = self.db.execute("SELECT item FROM items WHERE pk=? AND sk=?", (pk, sk)).fetchone()
                if row is None:
                    self._written.pop((pk, sk), None)
                return self._seen(_unblob(row[0])) if row else None
            return self._local.get(pk, {}).get(sk)

    def _delete(self, pk: str, sk: str) -> None:
        with self._lock:
            self._written.pop((pk, sk), None)
            if self.table is not None:
                self.table.delete_item(Key={"PK": pk, "SK": sk})
            elif self.db is not None:
                self.db.execute("DELETE FROM items WHERE pk=? AND sk=?", (pk, sk))
            else:
                self._local.get(pk, {}).pop(sk, None)
                self._flush()

    def _query(self, pk: str, prefix: str) -> list:
        with self._lock:
            if self.table is not None:
                from boto3.dynamodb.conditions import Key
                kw = {"KeyConditionExpression": Key("PK").eq(pk) & Key("SK").begins_with(prefix),
                      "ConsistentRead": True}
                items = []
                while True:
                    page = self.table.query(**kw)
                    items += page["Items"]
                    if "LastEvaluatedKey" not in page:
                        return [self._seen(_from_db(i)) for i in items]
                    kw["ExclusiveStartKey"] = page["LastEvaluatedKey"]
            if self.db is not None:
                rows = self.db.execute("SELECT item FROM items WHERE pk=? AND sk >= ? AND sk < ? ORDER BY sk",
                                       (pk, prefix, prefix + "￿")).fetchall()
                return [self._seen(_unblob(r[0])) for r in rows]
            return [v for k, v in sorted(self._local.get(pk, {}).items()) if k.startswith(prefix)]

    # ---- game-wide items (PK = GLOBAL): the global leaderboard and the global market -------------
    # Shared by every colony and every bot process. ``coord`` (a BattleCache) gives each one a lock
    # and a version number in Redis: an update takes the lock and re-reads the item if another
    # process has changed it since this one last looked. Without ``coord`` this process owns them.
    def get_global(self, sk: str) -> dict:
        with self._lock:
            ver = self.coord.version(f"global:{sk}") if self.coord is not None else 0
            seen = self._globals.get(sk)
            if seen is None or seen[0] != ver:
                seen = self._globals[sk] = (ver, self._get("GLOBAL", sk) or {})
            return seen[1]

    def update_global(self, sk: str, fn) -> dict:
        """Read-modify-write a GLOBAL item: one writer at a time, written only if it changed."""
        token = self.coord.acquire(f"global:{sk}", ttl=15, wait=15) if self.coord is not None else None
        try:
            with self._lock:
                d = self.get_global(sk)
                before = self.writes
                fn(d)
                self._put("GLOBAL", sk, d)
                if self.coord is not None and self.writes != before:
                    self._globals[sk] = (self.coord.bump(f"global:{sk}"), d)
                return d
        finally:
            if self.coord is not None:
                self.coord.release(f"global:{sk}", token)

    def raw_items(self):
        """Every stored item in the common (packed) format, for migrate.py."""
        with self._lock:
            if self.table is not None:
                kw = {}
                while True:
                    page = self.table.scan(**kw)
                    for i in page["Items"]:
                        yield _from_db(i)
                    if "LastEvaluatedKey" not in page:
                        return
                    kw["ExclusiveStartKey"] = page["LastEvaluatedKey"]
            elif self.db is not None:
                for (blob,) in self.db.execute("SELECT item FROM items").fetchall():
                    yield _unblob(blob)
            else:
                for pk, sks in self._local.items():
                    for sk, item in sks.items():
                        yield pack(pk, sk, item)

    def put_raw(self, stored: dict) -> None:
        """Write one item already in the packed format (migrate.py)."""
        item = unpack(stored)
        if "GSI1PK" in stored:
            item.update(GSI1PK=stored["GSI1PK"], GSI1SK=stored["GSI1SK"])
        self._put(stored["PK"], stored["SK"], item)

    def _flush(self) -> None:
        tmp = self.local_path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(_to_json(self._local), f)
        os.replace(tmp, self.local_path)

    # ---- colonies ----------------------------------------------------------------------
    def put_colony(self, colony: Colony) -> None:
        self._put(f"SERVER#{colony.server_id}", "META", colony.to_item())

    def get_colony(self, server_id: str) -> Optional[Colony]:
        item = self._get(f"SERVER#{server_id}", "META")
        return Colony.from_item(item) if item else None

    def put_map(self, server_id: str, state: dict) -> None:
        self._put(f"SERVER#{server_id}", "MAP", state)

    def get_map(self, server_id: str) -> Optional[dict]:
        return self._get(f"SERVER#{server_id}", "MAP")

    # ---- players -----------------------------------------------------------------------
    def put_player(self, rec: PlayerRecord, new_only: bool = False) -> bool:
        item = rec.to_item()
        item.update(GSI1PK=f"USER#{rec.user_id}", GSI1SK=f"SERVER#{rec.server_id}")
        return self._put(f"SERVER#{rec.server_id}", f"PLAYER#{rec.user_id}", item, new_only)

    def get_player(self, server_id: str, user_id: str) -> Optional[PlayerRecord]:
        item = self._get(f"SERVER#{server_id}", f"PLAYER#{user_id}")
        return PlayerRecord.from_item(item) if item else None

    def list_players(self, server_id: str) -> list:
        return [PlayerRecord.from_item(i) for i in self._query(f"SERVER#{server_id}", "PLAYER#")]

    def players_of_user(self, user_id: str) -> list:
        """Every character a Discord user owns, across servers."""
        if self.table is not None:
            from boto3.dynamodb.conditions import Key
            page = self.table.query(IndexName="GSI1", KeyConditionExpression=Key("GSI1PK").eq(f"USER#{user_id}"))
            keys = [(i["GSI1SK"].split("#", 1)[1]) for i in page["Items"]]
            return [r for r in (self.get_player(sid, user_id) for sid in keys) if r is not None]
        if self.db is not None:
            with self._lock:
                rows = self.db.execute("SELECT item FROM items WHERE gsi1pk=?", (f"USER#{user_id}",)).fetchall()
            return [PlayerRecord.from_item(unpack(_unblob(r[0]))) for r in rows]
        return [PlayerRecord.from_item(v) for pk in self._local.values() for sk, v in pk.items()
                if sk == f"PLAYER#{user_id}"]


def _blob(stored: dict) -> bytes:
    """A packed item as one SQLite value (exactly what DynamoDB would hold)."""
    return json.dumps(_to_json(stored), separators=(",", ":")).encode()


def _unblob(blob) -> dict:
    return _from_json(json.loads(bytes(blob).decode()))


def table_definition(table: str = "CullingGame") -> dict:
    """The DynamoDB table, chosen for cost (see ai/STORAGE.md)."""
    return dict(
        TableName=table, BillingMode="PAY_PER_REQUEST",
        AttributeDefinitions=[{"AttributeName": n, "AttributeType": "S"} for n in ("PK", "SK", "GSI1PK", "GSI1SK")],
        KeySchema=[{"AttributeName": "PK", "KeyType": "HASH"}, {"AttributeName": "SK", "KeyType": "RANGE"}],
        GlobalSecondaryIndexes=[{
            "IndexName": "GSI1",
            "Projection": {"ProjectionType": "INCLUDE", "NonKeyAttributes": list(GSI_ATTRS)},
            "KeySchema": [{"AttributeName": "GSI1PK", "KeyType": "HASH"},
                          {"AttributeName": "GSI1SK", "KeyType": "RANGE"}]}],
        TableClass="STANDARD")
