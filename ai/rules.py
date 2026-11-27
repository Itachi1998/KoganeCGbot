"""Colonies (Discord servers), purchasable culling game rules and the 19-day clock."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional

from .constants import DAY, INACTIVITY_DAYS, RULE_COST


@dataclass(frozen=True)
class Rule:
    key: str
    name: str
    desc: str
    cost: int = RULE_COST


RULES = {r.key: r for r in (
    Rule("point_transfer", "Point Transfer", "Players may give points to one another (and buy mercy with them)."),
    Rule("colony_transfer", "Free Passage", "Players may move to another colony that has also added this rule."),
    Rule("score_board", "Open Score Board", "Everyone can see every player's points and last known location."),
    Rule("long_clock", "Extended Clock", "The inactivity limit becomes 30 days instead of 19."),
)}


@dataclass
class Colony:
    """One Discord server."""
    server_id: str
    name: str = "Colony"
    managers: list = field(default_factory=list)       # Discord user ids allowed to administer
    rules: list = field(default_factory=list)          # keys of added rules
    created_ts: float = field(default_factory=time.time)
    map_seed: int = 0
    clock: float = 0.0                                 # CLI only: game time, which can run ahead of real time
    # Tools players have put up for sale at the shop: [{"seller", "item", "price", "looted"}]
    market: list = field(default_factory=list)

    def has(self, key: str) -> bool:
        return key in self.rules

    @property
    def inactivity_days(self) -> int:
        return 30 if self.has("long_clock") else INACTIVITY_DAYS

    def to_item(self) -> dict:
        return dict(self.__dict__)

    @classmethod
    def from_item(cls, d: dict) -> "Colony":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


def buy_rule(colony: Colony, rec, key: str) -> str:
    rule = RULES.get(key)
    if not rule:
        return "No such rule. Options: " + ", ".join(RULES)
    if colony.has(key):
        return f"{rule.name} is already in force here."
    if rec.points < rule.cost:
        return f"Adding a rule costs {rule.cost} points; you have {rec.points}."
    rec.points -= rule.cost                             # spending is not scoring: the clock keeps running
    colony.rules.append(key)
    return f"Rule added to {colony.name}: {rule.name} - {rule.desc}"


def transfer_points(colony: Optional[Colony], src, dst, n: int, now: Optional[float] = None) -> Optional[str]:
    """Returns an error message, or None on success."""
    if colony is None or not colony.has("point_transfer"):
        return "This colony has not added the Point Transfer rule."
    if n <= 0 or src.points < n:
        return "Not enough points."
    src.points -= n
    dst.score(n, now)                                   # receiving points resets the receiver's clock
    return None


def can_move_player(src: Colony, dst: Colony) -> bool:
    return src.has("colony_transfer") and dst.has("colony_transfer")


def is_inactive(rec, colony: Optional[Colony], now: Optional[float] = None) -> bool:
    limit = colony.inactivity_days if colony else INACTIVITY_DAYS
    return rec.alive and (now if now is not None else time.time()) - rec.last_score_ts > limit * DAY


def enforce_inactivity(records, colony: Optional[Colony], now: Optional[float] = None) -> list:
    """Technique removal for anyone whose score has not changed in time. Returns the dead."""
    dead = [r for r in records if is_inactive(r, colony, now)]
    for r in dead:
        r.alive = False
    return dead
