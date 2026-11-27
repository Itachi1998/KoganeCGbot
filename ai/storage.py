"""Storage adapters.

BattleCache  Redis.  A live battle is snapshotted after every round so a stateless bot
             process can pick it up again; keys carry the server (colony) id.
GameStore    DynamoDB, single table.  Long-term state: colonies, players, maps.

Both fall back to a local implementation (in-memory dict / JSON file) when the service or
its client library is unavailable, so the game runs on a bare machine.

DynamoDB key design
    PK = SERVER#<server_id>   SK = META                 colony: rules, manager user ids
    PK = SERVER#<server_id>   SK = PLAYER#<user_id>     one character per user per server
    PK = SERVER#<server_id>   SK = MAP                  seed + broken/looted bitmasks + roamers
    GSI1: GSI1PK = USER#<user_id>, GSI1SK = SERVER#<server_id>   all of a user's characters
"""
from __future__ import annotations

import base64
import json
import os
import pickle
from decimal import Decimal
from typing import Optional

import numpy as np

from .records import PlayerRecord
from .rules import Colony, can_move_player


# ======================================================================================
# Redis
# ======================================================================================
class BattleCache:
    def __init__(self, url: Optional[str] = None, ttl: int = 6 * 3600):
        self.ttl = ttl
        self._mem: dict = {}
        self.r = None
        try:
            import redis
            self.r = redis.Redis.from_url(url or os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
                                          socket_connect_timeout=0.5)
            self.r.ping()
        except Exception:
            self.r = None                                # no server / no library: stay in memory

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


class GameStore:
    def __init__(self, table: str = "CullingGame", region: Optional[str] = None,
                 endpoint_url: Optional[str] = None, local_path: str = "culling_save.json",
                 use_dynamo: Optional[bool] = None):
        self.table = None
        self.local_path = local_path
        want = use_dynamo if use_dynamo is not None else bool(os.environ.get("CULLING_DYNAMO"))
        if want:
            try:
                import boto3
                self.table = boto3.resource("dynamodb", region_name=region,
                                            endpoint_url=endpoint_url or os.environ.get("DYNAMO_ENDPOINT")).Table(table)
                self.table.load()
            except Exception as e:
                print(f"[storage] DynamoDB unavailable ({type(e).__name__}); using {local_path}")
                self.table = None
        self._local: dict = {}
        if self.table is None and os.path.exists(local_path):
            with open(local_path) as f:
                self._local = _from_json(json.load(f))

    @property
    def backend(self) -> str:
        return "dynamodb" if self.table is not None else "json-file"

    @staticmethod
    def create_table(table: str = "CullingGame", **kw) -> None:
        """One-off setup for a real deployment."""
        import boto3
        boto3.client("dynamodb", **kw).create_table(
            TableName=table, BillingMode="PAY_PER_REQUEST",
            AttributeDefinitions=[{"AttributeName": n, "AttributeType": "S"} for n in ("PK", "SK", "GSI1PK", "GSI1SK")],
            KeySchema=[{"AttributeName": "PK", "KeyType": "HASH"}, {"AttributeName": "SK", "KeyType": "RANGE"}],
            GlobalSecondaryIndexes=[{
                "IndexName": "GSI1", "Projection": {"ProjectionType": "ALL"},
                "KeySchema": [{"AttributeName": "GSI1PK", "KeyType": "HASH"},
                              {"AttributeName": "GSI1SK", "KeyType": "RANGE"}]}])

    # ---- primitives --------------------------------------------------------------------
    def _put(self, pk: str, sk: str, item: dict, new_only: bool = False) -> bool:
        if self.table is not None:
            kw = {"ConditionExpression": "attribute_not_exists(PK)"} if new_only else {}
            try:
                self.table.put_item(Item=_to_db({**item, "PK": pk, "SK": sk}), **kw)
            except Exception as e:
                if new_only and "ConditionalCheckFailed" in type(e).__name__ + str(e):
                    return False
                raise
            return True
        if new_only and sk in self._local.get(pk, {}):
            return False
        self._local.setdefault(pk, {})[sk] = item
        self._flush()
        return True

    def _get(self, pk: str, sk: str) -> Optional[dict]:
        if self.table is not None:
            item = self.table.get_item(Key={"PK": pk, "SK": sk}).get("Item")
            return _from_db(item) if item else None
        return self._local.get(pk, {}).get(sk)

    def _delete(self, pk: str, sk: str) -> None:
        if self.table is not None:
            self.table.delete_item(Key={"PK": pk, "SK": sk})
        else:
            self._local.get(pk, {}).pop(sk, None)
            self._flush()

    def _query(self, pk: str, prefix: str) -> list:
        if self.table is not None:
            from boto3.dynamodb.conditions import Key
            kw = {"KeyConditionExpression": Key("PK").eq(pk) & Key("SK").begins_with(prefix)}
            items = []
            while True:
                page = self.table.query(**kw)
                items += page["Items"]
                if "LastEvaluatedKey" not in page:
                    return [_from_db(i) for i in items]
                kw["ExclusiveStartKey"] = page["LastEvaluatedKey"]
        return [v for k, v in sorted(self._local.get(pk, {}).items()) if k.startswith(prefix)]

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
            return [PlayerRecord.from_item(_from_db(i)) for i in page["Items"]]
        return [PlayerRecord.from_item(v) for pk in self._local.values() for sk, v in pk.items()
                if sk == f"PLAYER#{user_id}"]

    def move_player(self, rec: PlayerRecord, dst_server: str) -> Optional[str]:
        """Colony transfer. Returns an error message or None on success."""
        src, dst = self.get_colony(rec.server_id), self.get_colony(dst_server)
        if src is None or dst is None:
            return "Unknown colony."
        if not can_move_player(src, dst):
            return "Both colonies must have added the Free Passage rule."
        other = self.get_player(dst_server, rec.user_id)
        if other is not None and other.alive:
            return "You already have a living character in that colony."
        old = rec.server_id
        rec.server_id, rec.node, rec.hideout = dst_server, 0, None
        self.put_player(rec)
        self._delete(f"SERVER#{old}", f"PLAYER#{rec.user_id}")
        return None
