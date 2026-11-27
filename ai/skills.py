"""Skill points: earned on level-ups, spent on seven trainable stats.

+10 points for every level-up up to level 10, +5 for every level after that. Each stat takes at
most SKILL_CAP points. What a point does:

  efficiency   CE efficiency: 1% off every technique's cursed energy cost (the usual 60% cap holds;
               the Six Eyes and Sukuna are above it anyway)
  speed        physical speed: close-range moves land sooner (+0.5 speed for melee timing) and hit
               more often (+0.5% accuracy) per point
  strength     physical strength: +2% damage on close-range moves per point
  perception   +1 perception: reading channelled techniques and enemy cursed energy, reacting while
               committed (16+), the switch chance, soul perception, and technique unlocks
  soul         soul perception: counts double toward perceiving the soul (needed to harm an Idle
               Transfiguration body), and +3% damage to soul-bodied targets per point
  refinement   domain refinement: +3% to your domain's strength in a clash per point
  navigation   the colony: moving takes less time (-4% a point, at least a quarter hour), `look`
               sees curses further off (+1 hop per 5 points), the best navigator in a party may slip
               an ambush (2% a point, up to 40%), and at 10+ you always know where the medic is
"""
from __future__ import annotations

SKILLS = {
    "efficiency": ("CE Efficiency", "1% off technique CE costs per point"),
    "speed": ("Physical Speed", "close-range moves: sooner and more accurate"),
    "strength": ("Physical Strength", "close-range moves: +2% damage per point"),
    "perception": ("Perception", "+1 perception: reactions, reading, unlocks"),
    "soul": ("Soul Perception", "perceive and harm the soul (Idle Transfiguration)"),
    "refinement": ("Domain Refinement", "+3% domain strength in a clash per point"),
    "navigation": ("Navigation", "faster travel, see further, slip ambushes"),
}
ALIASES = {"eff": "efficiency", "ce": "efficiency", "spd": "speed", "str": "strength", "per": "perception",
           "soul_perception": "soul", "domain": "refinement", "nav": "navigation"}
SKILL_CAP = 50


def points_for_level(new_level: int) -> int:
    """Skill points for reaching ``new_level``."""
    return 10 if new_level <= 10 else 5


def points_through(level: int) -> int:
    """Everything a character of this level has earned since level 1."""
    return sum(points_for_level(lv) for lv in range(2, int(level) + 1))


def get(rec, key: str) -> int:
    return int((getattr(rec, "skills", None) or {}).get(key, 0)) if rec is not None else 0


def of(c, key: str) -> int:
    """A combatant's points in a skill: only a player's own body has trained (not summons)."""
    rec = getattr(c, "record", None)
    return get(rec, key) if rec is not None and getattr(c, "kind", "fighter") == "fighter" else 0


def resolve(name: str):
    name = name.lower().strip()
    return name if name in SKILLS else ALIASES.get(name)


def spend(rec, name: str, n: int) -> str:
    key = resolve(name)
    if key is None:
        return "No such skill. Choose from: " + ", ".join(SKILLS)
    if n <= 0:
        return "Spend at least one point."
    have = get(rec, key)
    n = min(n, SKILL_CAP - have)
    if n <= 0:
        return f"{SKILLS[key][0]} is already at the cap ({SKILL_CAP})."
    if rec.skill_points < n:
        return f"You have {rec.skill_points} skill point(s)."
    rec.skill_points -= n
    rec.skills[key] = have + n
    return f"{SKILLS[key][0]} {have} -> {have + n}. {rec.skill_points} skill point(s) left."


# ---- effects used by the engine and the colony ------------------------------------------------
def melee_mult(c) -> float:
    return 1.0 + 0.02 * of(c, "strength")


def melee_speed(c) -> float:
    return 0.5 * of(c, "speed")


def melee_acc(c) -> float:
    return 0.005 * of(c, "speed")


def soul_sight(c) -> float:
    """Extra perception toward perceiving the soul."""
    return 2.0 * of(c, "soul")


def soul_damage(c) -> float:
    return 1.0 + 0.03 * of(c, "soul")


def refinement(c) -> float:
    return 1.0 + 0.03 * of(c, "refinement")


def travel_hours(rec) -> float:
    return max(0.25, 1.0 - 0.04 * get(rec, "navigation"))


def sight_range(rec) -> int:
    return 1 + get(rec, "navigation") // 5


def evade_chance(recs) -> float:
    return min(0.40, 0.02 * max((get(r, "navigation") for r in recs), default=0))
