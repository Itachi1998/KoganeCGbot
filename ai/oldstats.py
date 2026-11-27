"""The original bot's character stats: rolled exactly as its Spin button did, then scaled into the engine.

The original rolled HP 100-300, CE 200-2000, Strength 50-200 and Speed 50-200, added a class boost
and technique boosts (Six Eyes, Copy/Shrine/Limitless, Shrine, Heavenly Restriction: Zero).
Those numbers are kept on the player (``PlayerRecord.old_stats``) and shown to them.

The engine works on a much smaller scale (HP ~100, CE ~60, STR/SPD ~10), so in a fight each old
stat becomes a multiplier: the rolled value over what an average roll of that class comes to
(``REFERENCE``).  A sorcerer who rolled 400 HP where the average is 300 has a third more HP than
the engine's baseline sorcerer of the same level and technique; Shrine's +3000 CE makes for
several times the cursed energy.  Level-ups and the engine's own technique multipliers still
apply on top.
"""
from __future__ import annotations

from typing import Optional

from .constants import PClass, Stat

# Base roll ranges (inclusive), as in cogs/character_cog.py CreateButton.
ROLL = {"hp": (100, 300), "ce": (200, 2000), "str": (50, 200), "spd": (50, 200)}

# Class boosts: Sorcerer, Reincarnate, Curse. The original had no Mutant; it gets the sorcerer's.
CLASS_BOOST = {
    PClass.SORCERER: {"hp": 100, "ce": 50, "str": 100, "spd": 100},
    PClass.REINCARNATED: {"hp": 150, "ce": 100, "str": 120, "spd": 120},
    PClass.CURSED_SPIRIT: {"hp": 150, "ce": 200, "str": 150, "spd": 150},
    PClass.MUTANT: {"hp": 100, "ce": 50, "str": 100, "spd": 100},
}

# What an average roll of each class comes to (mid-range roll + class boost, no technique boost).
REFERENCE = {pc: {k: (lo + hi) / 2 + CLASS_BOOST[pc][k] for k, (lo, hi) in ROLL.items()} for pc in CLASS_BOOST}

ENGINE_STAT = {"hp": Stat.MAX_HP, "ce": Stat.MAX_CE, "str": Stat.STR, "spd": Stat.SPD}
FACTOR_CAP = 5.0                       # no single stat more than five times the engine's baseline


def roll(pclass, tech: str, six_eyes: bool, rng) -> dict:
    """The original Spin: base rolls, class boost, then technique boosts (in the original's order)."""
    pclass = PClass(pclass)
    s = {k: int(rng.integers(lo, hi + 1)) for k, (lo, hi) in ROLL.items()}
    for k, v in CLASS_BOOST[pclass].items():
        s[k] += v
    if six_eyes or tech == "limitless":          # the original: Six Eyes +1000 CE, +300 HP
        s["ce"] += 1000
        s["hp"] += 300
    if tech in ("copy", "shrine", "limitless"):  # copy / shrine / limitless: +1000 CE, +100 HP
        s["ce"] += 1000
        s["hp"] += 100
    if tech == "shrine":                         # shrine on top: +2000 CE, +200 HP
        s["ce"] += 2000
        s["hp"] += 200
    if tech == "heavenly_restriction":           # heavenly restriction (zero): body over energy
        s["str"] += 200
        s["spd"] += 200
        s["hp"] += 300
        s["ce"] = 0
    return s


def factors(pclass, old: Optional[dict]) -> dict:
    """Engine multipliers for a player's old stats (empty when they have none)."""
    if not old:
        return {}
    ref = REFERENCE[PClass(pclass)]
    return {k: min(FACTOR_CAP, max(0.0, float(old[k]) / ref[k])) for k in ENGINE_STAT if k in old}


def apply(stats, pclass, old: Optional[dict]) -> None:
    """Scale an engine stat row by the player's old stats (in place)."""
    for k, f in factors(pclass, old).items():
        stats[ENGINE_STAT[k]] *= f
