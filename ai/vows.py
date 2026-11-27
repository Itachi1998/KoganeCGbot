"""Binding vows: give something up, get something back.

A vow is data - a set of restriction flags the engine enforces and a set of boons it
applies.  ``custom`` prices a new vow automatically: the heavier the sacrifice, the
larger the return, so new vows can be added without touching the engine.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .constants import Part
from .rules import transfer_points

# What each restriction is worth when pricing a custom vow.
SACRIFICE = {
    "no_tool_swap": 2.5,   # never wield another cursed tool
    "no_tools": 2.0,       # never wield cursed tools at all
    "no_dodge": 2.0,
    "no_domain": 3.0,
    "revealed": 2.0,       # your technique is explained: everyone reads your channelling
    "bound_arm": 3.0,      # the left arm may not be used
}
BOONS = ("out", "str", "tool")          # cursed energy output, strength, tool output


@dataclass(frozen=True)
class Vow:
    key: str
    name: str
    desc: str
    restrictions: tuple = ()
    boons: dict = field(default_factory=dict)
    permanent: bool = False


VOWS = {v.key: v for v in (
    Vow("tool_devotion", "Tool Devotion",
        "Give up every other cursed tool forever; the one in your hand hits 50% harder.",
        ("no_tool_swap",), {"tool": 1.5}, permanent=True),
    Vow("reveal_hand", "Revealing One's Hand",
        "Explain your technique to the enemy: +20% output, but they read all your channelling.",
        ("revealed",), {"out": 1.2}),
    Vow("rushed_cast", "Rushed Casting",
        "Your next technique is released on its channelling turn. Afterwards every technique "
        "needs an incantation turn.", (), {"instant": 1}),
    Vow("bound_arm", "Bound Arm", "Seal your left arm for the fight: +30% output.",
        ("bound_arm",), {"out": 1.3}),
    Vow("iron_stance", "Iron Stance", "Never dodge: +20% strength.", ("no_dodge",), {"str": 1.2}),
    Vow("forsake_domain", "Forsaken Domain", "Give up domain expansion: +30% output.",
        ("no_domain",), {"out": 1.3}),
)}


def custom(key: str, name: str, restrictions: tuple, boon: str, permanent: bool = False) -> Vow:
    """Build and register a balanced vow from restriction flags."""
    if boon not in BOONS or not restrictions or any(r not in SACRIFICE for r in restrictions):
        raise ValueError("unknown restriction or boon")
    mult = round(1 + 0.08 * sum(SACRIFICE[r] for r in restrictions) * (1.25 if permanent else 1.0), 2)
    vow = Vow(key, name, f"Sacrifice: {', '.join(restrictions)}. Gain: x{mult} {boon}.",
              tuple(restrictions), {boon: mult}, permanent)
    VOWS[key] = vow
    return vow


def apply(b, c, vow: Vow, announce: bool = True) -> bool:
    taken = c.meta.setdefault("vows", set())
    if vow.key in taken:
        b.tell(c, "That vow is already in force.")
        return False
    if "tool" in vow.boons and c.weapon is None:
        b.tell(c, "You need a cursed tool in hand to swear that.")
        return False
    taken.add(vow.key)
    for r in vow.restrictions:
        c.vow_flags.add(r)
        if r == "bound_arm":
            c.sealed_parts.add(Part.L_ARM)
    for k, v in vow.boons.items():
        if k in c.mult:
            c.mult[k] *= v
        elif k == "instant":
            c.vow_instant = True
    if vow.permanent and c.record is not None and vow.key not in c.record.vows:
        c.record.vows.append(vow.key)
    if announce:
        b.say(f"{c} swears a binding vow - {vow.name}: {vow.desc}")
    return True


def spare(b, payer, target, points: int) -> bool:
    """Buy mercy: both sides are bound not to attack each other for the rest of the fight."""
    if not b.hostile(payer, target):
        b.tell(payer, "You are not fighting them.")
        return False
    if payer.record is None:
        b.tell(payer, "You have no points to offer.")
        return False
    if b.colony is None or not b.colony.has("point_transfer"):
        b.tell(payer, "This colony has not added the Point Transfer rule.")
        return False
    if points <= 0 or payer.record.points < points:
        b.tell(payer, "Not enough points.")
        return False
    hurt = target.hp / max(target.max_hp, 1) < 0.5
    p = float(np.clip(0.15 + points / 20 + (0.3 if hurt else 0.0), 0.05, 0.95))
    b.say(f"{payer} offers {target} {points} points for a vow of mutual non-aggression.")
    if b.ask(target, f"Accept {points} points to spare {payer}?", ["Accept", "Refuse"], [p, 1 - p]) != 0:
        b.say(f"{target} refuses.")
        return True
    if target.record is not None:
        transfer_points(b.colony, payer.record, target.record, points, b.now)
    else:
        payer.record.points -= points
    b.truces.add(frozenset((payer.root.cid, target.root.cid)))
    b.say(f"The vow is sealed. {payer} and {target} can no longer harm each other here.")
    return True
