"""Data types for techniques.

A technique is *pure data*: a frozen dataclass that can be written as JSON and loaded
back.  Anything that needs custom behaviour names a handler (``effect``) that lives in
``effects.py``; the data never contains code.  New techniques that only use standard
attacks, buffs, statuses and reactions need no Python at all - see ``technique_from_dict``.
"""
from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Any, Mapping, Optional

from .constants import DType, Kind, Part, React, Rng, Stat, Status, Target


@dataclass(frozen=True, eq=False)
class Action:
    key: str
    name: str
    kind: Kind = Kind.ATTACK
    target: Target = Target.ENEMY
    power: float = 0.0
    dtype: DType = DType.CURSED
    ce: int = 0                       # cursed energy cost
    sta: int = 0                      # stamina cost
    rng: Rng = Rng.MELEE
    requires: tuple = ()              # body-part groups, one usable part needed per group
    channel: int = 0                  # 1 = cursed energy must be channelled first (readable by others)
    activation: Optional[float] = None  # beats to activate; default: 1 if channelled, else 0
    speed: float = 1.0                # technique speed: how fast a ranged technique or buff arrives
    can_chant: bool = False           # may be amplified by an incantation (extra turn)
    min_level: int = 1
    statuses: tuple = ()              # (Status, chance, duration, magnitude)
    tags: frozenset = frozenset()     # phenomena, used by adaptation ("slash", "blood", ...)
    react: Optional[React] = None     # set on defensive reactions
    effect: Optional[str] = None      # name of a handler in effects.EFFECTS
    params: Mapping[str, Any] = field(default_factory=dict)
    acc: float = 0.0
    needs_status: Optional[Status] = None
    desc: str = ""


@dataclass(frozen=True, eq=False)
class Technique:
    key: str
    name: str
    actions: tuple = ()
    desc: str = ""
    flags: tuple = ()                 # passive flags granted to the user
    stat_mods: Mapping[Stat, float] = field(default_factory=dict)   # multipliers
    copyable: bool = True
    innate: bool = True               # False for the basic kit everyone has
    tool: Optional[str] = None        # key of a cursed tool the technique's user starts with
    grade: int = 2                    # how strong the technique itself is (constants.Grade); sets its
                                      # user's power (TIER_POWER), their rank, and how rare it is


TECHNIQUES: dict[str, Technique] = {}
ACTIONS: dict[str, Action] = {}
ACTION_TECH: dict[str, str] = {}      # action key -> technique key


def register(tech: Technique) -> Technique:
    TECHNIQUES[tech.key] = tech
    for a in tech.actions:
        if a.key in ACTIONS and ACTION_TECH[a.key] != tech.key:
            raise ValueError(f"duplicate action key {a.key!r}")
        ACTIONS[a.key] = a
        ACTION_TECH[a.key] = tech.key
    return tech


# ---- JSON ---------------------------------------------------------------------------
_ENUMS = {"kind": Kind, "target": Target, "dtype": DType, "rng": Rng, "react": React,
          "needs_status": Status}


def action_to_dict(a: Action) -> dict:
    out: dict[str, Any] = {}
    default = Action("", "")
    for f in fields(Action):
        v = getattr(a, f.name)
        if f.name not in ("key", "name") and v == getattr(default, f.name):
            continue
        if f.name in _ENUMS:
            v = v.name
        elif f.name == "requires":
            v = [[Part(p).name for p in group] for group in v]
        elif f.name == "statuses":
            v = [[Status(s).name, ch, dur, mag] for s, ch, dur, mag in v]
        elif f.name == "tags":
            v = sorted(v)
        elif f.name == "params":
            v = dict(v)
        out[f.name] = v
    return out


def action_from_dict(d: Mapping[str, Any]) -> Action:
    kw = dict(d)
    for name, enum in _ENUMS.items():
        if kw.get(name) is not None:
            kw[name] = enum[kw[name]]
    if "requires" in kw:
        kw["requires"] = tuple(tuple(Part[p] for p in g) for g in kw["requires"])
    if "statuses" in kw:
        kw["statuses"] = tuple((Status[s], ch, dur, mag) for s, ch, dur, mag in kw["statuses"])
    if "tags" in kw:
        kw["tags"] = frozenset(kw["tags"])
    return Action(**kw)


def technique_to_dict(t: Technique) -> dict:
    return {"key": t.key, "name": t.name, "desc": t.desc, "flags": list(t.flags),
            "stat_mods": {Stat(k).name: v for k, v in t.stat_mods.items()},
            "copyable": t.copyable, "innate": t.innate, "tool": t.tool, "grade": int(t.grade),
            "actions": [action_to_dict(a) for a in t.actions]}


def technique_from_dict(d: Mapping[str, Any]) -> Technique:
    return Technique(
        key=d["key"], name=d["name"], desc=d.get("desc", ""),
        flags=tuple(d.get("flags", ())),
        stat_mods={Stat[k]: v for k, v in d.get("stat_mods", {}).items()},
        copyable=d.get("copyable", True), innate=d.get("innate", True), tool=d.get("tool"), grade=int(d.get("grade", 2)),
        actions=tuple(action_from_dict(a) for a in d.get("actions", ())))


def load_technique(d: Mapping[str, Any]) -> Technique:
    """Build a technique from a JSON-style dict and register it."""
    return register(technique_from_dict(d))
