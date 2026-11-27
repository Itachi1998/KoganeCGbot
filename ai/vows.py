"""Binding vows: give something up, get something back.

A vow is data. It can
  * bind the fighter (``restrictions``: flags the engine enforces - never dodge, a sealed arm...),
  * move the numbers of their TECHNIQUE around (``boons``: multipliers on ``Combatant.mult`` -
    out, str, tool, cost, speed),
  * move the numbers of their DOMAIN around (``domain``: changes to ``Combatant.domain_mods`` -
    range steps, output, refine, rounds, cost, shell),
  * or change how the next technique is released (``release``: "snap" / "oath").
Every vow here pays for what it gives with something else on the same sheet, the way they do in
the manga: Malevolent Shrine has no barrier and a great range for it; a barrier's conditions can be
swapped; an attack can be let go without gathering if it is weaker - or if you chant for ever after.

``custom`` prices a restriction-based vow automatically and ``trade`` registers a stat-shifting
one, so new vows can be added without touching the engine.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .constants import OATH_BUFF, RANGE_OUTPUT, SNAP_DEBUFF, Part
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
TECHNIQUE_STATS = ("out", "str", "tool", "cost", "speed")
DOMAIN_STATS = ("range", "output", "refine", "rounds", "cost", "shell")


@dataclass(frozen=True)
class Vow:
    key: str
    name: str
    desc: str
    restrictions: tuple = ()
    boons: dict = field(default_factory=dict)      # technique numbers: multipliers on Combatant.mult
    permanent: bool = False                        # sworn once, for good: saved on the character
    domain: dict = field(default_factory=dict)     # domain numbers: see _shift_domain
    release: str = ""                              # "snap" | "oath": the next channelled technique goes at once
    repeat: bool = False                           # may be sworn again once it has been spent
    kind: str = "technique"                        # technique | domain | release | binding (for the lists)


_pct = lambda m: f"{abs(m - 1):.0%}"               # noqa: E731

VOWS = {v.key: v for v in (
    # ---- bindings: a restriction for a boon ---------------------------------------------------
    Vow("tool_devotion", "Tool Devotion",
        "Give up every other cursed tool forever; the one in your hand hits 50% harder.",
        ("no_tool_swap",), {"tool": 1.5}, permanent=True, kind="binding"),
    Vow("reveal_hand", "Revealing One's Hand",
        "Explain your technique to the enemy: +20% output, but they read all your channelling.",
        ("revealed",), {"out": 1.2}, kind="binding"),
    Vow("bound_arm", "Bound Arm", "Seal your left arm for the fight: +30% output.",
        ("bound_arm",), {"out": 1.3}, kind="binding"),
    Vow("iron_stance", "Iron Stance", "Never dodge: +20% strength.", ("no_dodge",), {"str": 1.2}, kind="binding"),
    Vow("forsake_domain", "Forsaken Domain", "Give up domain expansion: +30% output.",
        ("no_domain",), {"out": 1.3}, kind="binding"),
    # ---- technique: move its numbers around ---------------------------------------------------------
    Vow("overcharge", "Overcharge", "Pour more into everything: +30% output, and every technique costs 50% more.",
        boons={"out": 1.3, "cost": 1.5}),
    Vow("measured_output", "Measured Output", "Hold back: techniques cost 30% less, at 15% less output.",
        boons={"cost": 0.7, "out": 0.85}),
    Vow("quick_hands", "Quick Hands", "Techniques activate 40% sooner, at 15% less output.",
        boons={"speed": 0.6, "out": 0.85}),
    Vow("deliberate_form", "Deliberate Form", "Take your time: techniques take 60% longer to activate, "
        "and hit 25% harder.", boons={"speed": 1.6, "out": 1.25}),
    # ---- release: let a technique go without the channelling phase --------------------------------------
    Vow("snap_release", "Snap Release",
        f"Your next channelled technique needs no gathering and no time: it is loosed in the same round on what "
        f"cursed energy is in hand, {_pct(SNAP_DEBUFF)} weaker. Use the same technique again next round and it "
        f"has to be chanted. Can be sworn again once spent.", release="snap", repeat=True, kind="release"),
    Vow("oath_of_incantation", "Oath of Incantation",
        f"PERMANENT. Once a fight, your first channelled technique needs no gathering and no time, and lands "
        f"{_pct(OATH_BUFF)} harder. In exchange every other technique you ever use has to be chanted.",
        permanent=True, release="oath", kind="release"),
    # ---- domain: move its numbers around ------------------------------------------------------------------
    Vow("widened_domain", "Widened Domain",
        f"Your domain reaches one step further (one target -> every enemy -> all it natively takes in), and its "
        f"sure-hit is {_pct(1 / RANGE_OUTPUT)} weaker - range for output, as Malevolent Shrine has it.",
        domain={"range": +1}, kind="domain"),
    Vow("condensed_domain", "Condensed Domain",
        f"Your domain is pulled in one step: it takes in fewer, and its sure-hit is {_pct(RANGE_OUTPUT)} stronger. "
        f"Pulled in to one target, everyone else is shut outside the barrier.", domain={"range": -1}, kind="domain"),
    Vow("pinpoint_domain", "Pinpoint Domain",
        "Your domain closes on ONE target, whatever it natively takes in; everyone else is shut outside. Its "
        "sure-hit is stronger for every step it was pulled in.", domain={"range": -9}, kind="domain"),
    Vow("inverted_barrier", "Inverted Barrier",
        "Swap your barrier's conditions: strong from OUTSIDE instead of from inside. Nothing breaks in (an open "
        "domain gets no edge on it), but it holds nobody in and gives ground to another closed barrier.",
        domain={"shell": "reinforced"}, kind="domain"),
    Vow("brief_domain", "Brief Domain", "Your domain stands one round less, and is 25% stronger in a clash.",
        domain={"rounds": -1, "refine": 1.25}, kind="domain"),
    Vow("lasting_domain", "Lasting Domain", "Your domain stands one round longer; its sure-hit is 15% weaker.",
        domain={"rounds": +1, "output": 0.85}, kind="domain"),
    Vow("lavish_domain", "Lavish Domain", "Your domain costs half again as much cursed energy; its sure-hit is "
        "20% stronger.", domain={"cost": 1.5, "output": 1.2}, kind="domain"),
)}


def custom(key: str, name: str, restrictions: tuple, boon: str, permanent: bool = False) -> Vow:
    """Build and register a balanced vow from restriction flags."""
    if boon not in BOONS or not restrictions or any(r not in SACRIFICE for r in restrictions):
        raise ValueError("unknown restriction or boon")
    mult = round(1 + 0.08 * sum(SACRIFICE[r] for r in restrictions) * (1.25 if permanent else 1.0), 2)
    vow = Vow(key, name, f"Sacrifice: {', '.join(restrictions)}. Gain: x{mult} {boon}.",
              tuple(restrictions), {boon: mult}, permanent, kind="binding")
    VOWS[key] = vow
    return vow


def trade(key: str, name: str, desc: str, technique: dict = None, domain: dict = None,
          permanent: bool = False) -> Vow:
    """Register a vow that moves numbers around: ``technique`` multiplies Combatant.mult entries
    (out, str, tool, cost, speed), ``domain`` changes Combatant.domain_mods (range and rounds are
    added; output, refine and cost multiplied; shell set). It has to cost something."""
    technique, domain = dict(technique or {}), dict(domain or {})
    if any(k not in TECHNIQUE_STATS for k in technique) or any(k not in DOMAIN_STATS for k in domain):
        raise ValueError("unknown stat")
    better = lambda k, v: (v < 1) if k in ("cost", "speed") else (v > 1)      # noqa: E731
    gains = [better(k, v) for k, v in technique.items()] + [
        (v > 0) if k in ("range", "rounds") else (v < 1) if k == "cost" else (v > 1)
        for k, v in domain.items() if k != "shell"]
    if gains and all(gains) and "shell" not in domain:
        raise ValueError("a binding vow gives something up: this one only gains")
    vow = Vow(key, name, desc, boons=technique, domain=domain, permanent=permanent,
              kind="domain" if domain and not technique else "technique")
    VOWS[key] = vow
    return vow


def _shift_domain(c, changes: dict) -> None:
    mods = c.domain_mods
    for k, v in changes.items():
        if k in ("range", "rounds"):
            mods[k] += v
        elif k == "shell":
            mods[k] = v
        else:
            mods[k] *= v


def available(c) -> list:
    """Vows this fighter could swear right now."""
    taken = c.meta.get("vows", set())
    return [v for v in VOWS.values() if v.key not in taken]


def apply(b, c, vow: Vow, announce: bool = True) -> bool:
    taken = c.meta.setdefault("vows", set())
    if vow.key in taken:
        b.tell(c, "That vow is already in force." + (" (It can be sworn again once it is spent.)" if vow.repeat else ""))
        return False
    if "tool" in vow.boons and c.weapon is None:
        b.tell(c, "You need a cursed tool in hand to swear that.")
        return False
    if vow.release and c.vow_snap is not None:
        b.tell(c, "A vow is already waiting on your next technique.")
        return False
    if vow.domain and announce and b.domain_of(c) is not None:
        b.tell(c, "Your domain is already standing: a vow can only shape the next one.")
        return False
    taken.add(vow.key)
    for r in vow.restrictions:
        c.vow_flags.add(r)
        if r == "bound_arm":
            c.sealed_parts.add(Part.L_ARM)
    for k, v in vow.boons.items():
        if k in c.mult:
            c.mult[k] *= v
    if vow.domain:
        _shift_domain(c, vow.domain)
    if vow.release:
        c.vow_snap = vow.release                         # (the oath arms once in every fight: apply runs on joining)
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
