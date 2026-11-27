"""Persistent player records, fighter specs and NPC factories."""
from __future__ import annotations

import copy
import time
from dataclasses import dataclass, field
from typing import Any, Optional

import numpy as np

from .constants import (FINGER_AMP, CE_RECOVERY, REST_RECOVERY, REST_STEP, SIX_EYES_EFF, SIX_EYES_REST, SUKUNA_EFF, SUKUNA_CE_BASE, SUKUNA_LEVEL, SUKUNA_OUT_FINGER, SUKUNA_OUT_FLOOR, STRONG_VESSEL, TIER_POWER, ADVANCED_LEVEL, BRAIN_SLOTS, EFF_CAP, N_STATS, REINCARNATED_UNLOCK, Grade,
                        PClass, Stat)
from .crimes import Crime, CrimeLog
from .data import CLASS_BASE, ITEMS
from .techniques import TECHNIQUES

POOLS = (Stat.MAX_HP, Stat.MAX_CE, Stat.MAX_STA)
ATTRS = (Stat.STR, Stat.SPD, Stat.DUR, Stat.PER, Stat.OUT)


def xp_to_next(level: int) -> int:
    return int(40 * level ** 1.6)


def technique_grade(techniques) -> Optional[Grade]:
    """The grade of the strongest innate technique someone has (None: no innate technique)."""
    tiers = [TECHNIQUES[k].grade for k in techniques if k in TECHNIQUES and TECHNIQUES[k].innate]
    return Grade(max(tiers)) if tiers else None


def grade_for(level: int, techniques=()) -> Grade:
    """A sorcerer's grade is mostly their technique. Experience closes the last two steps up to
    it (two below until level 5, one below until level 9); only a veteran (level 16+) ranks one
    above what their technique would give, and never special grade by experience alone. Without
    an innate technique the ceiling is Grade 3, or Grade 1 for a veteran of level 16+."""
    tier = technique_grade(techniques)
    if tier is None:
        return Grade.G1 if level >= 16 else Grade(min(int(Grade.G3), (level - 1) // 6))
    behind = 2 if level < 5 else 1 if level < 9 else 0
    bonus = 1 if level >= 16 and tier < Grade.G1 else 0
    return Grade(max(0, min(int(Grade.SPECIAL), int(tier) - behind + bonus)))


def grade_for_level(level: int) -> Grade:        # kept for callers that have no technique to hand
    return grade_for(level, ())


def roll_technique(pclass, rng) -> str:
    """The culling game decides what you awaken with, at the odds the original bot used
    (rarity.py: per-technique rarity numbers and its weight_system)."""
    from .rarity import roll_technique as _roll
    return _roll(pclass, rng)


def has_six_eyes(techniques, six_eyes: bool = False) -> bool:
    return bool(six_eyes) or any("six_eyes" in TECHNIQUES[k].flags for k in techniques if k in TECHNIQUES)


def build_stats(pclass: PClass, level: int, techniques: list[str],
                body: Optional[dict] = None, equipment: Optional[dict] = None,
                old_stats: Optional[dict] = None, skills: Optional[dict] = None) -> np.ndarray:
    """Class base -> level scaling -> technique multipliers -> the player's rolled (original-bot)
    stats -> body-hop overrides -> armor."""
    s = np.zeros(N_STATS)
    for k, v in CLASS_BASE[PClass(pclass)].items():
        s[k] = v
    for k in POOLS:
        s[k] *= 1 + 0.07 * (level - 1)
    for k in ATTRS:
        s[k] += 0.5 * (level - 1)
    s[Stat.CE_REGEN] = CE_RECOVERY               # percent of maximum cursed energy back each round, for everyone
    s[Stat.EFF] += 1.5 * (level - 1)             # experience wastes less cursed energy
    for key in techniques:
        for k, mult in TECHNIQUES[key].stat_mods.items():
            s[k] *= mult
    tier = technique_grade(techniques)
    if tier is not None:                                 # a stronger technique is simply stronger
        power = TIER_POWER[int(tier)]
        s[Stat.OUT] *= power
        for stat in (Stat.STR, Stat.DUR, Stat.MAX_HP, Stat.MAX_CE):
            s[stat] *= power ** 0.5
    if old_stats:                                # what they rolled at creation (oldstats.py)
        from .oldstats import apply as apply_old
        apply_old(s, pclass, old_stats)
    if skills:                                   # trained with skill points (skills.py)
        s[Stat.EFF] += skills.get("efficiency", 0)
        s[Stat.PER] += skills.get("perception", 0)
    if body:                                     # stats of a hopped-into body
        for k, v in body.items():
            s[int(k)] = v
    armor = ITEMS.get((equipment or {}).get("armor") or "")
    if armor:
        s[Stat.DUR] += armor.params.get("dur", 0)
    s[Stat.EFF] = min(s[Stat.EFF], EFF_CAP)
    s[Stat.HP], s[Stat.CE], s[Stat.STA] = s[Stat.MAX_HP], s[Stat.MAX_CE], s[Stat.MAX_STA]
    return s


@dataclass
class Spec:
    """Everything the battle engine needs to put one combatant on the field."""
    name: str
    pclass: PClass = PClass.SORCERER
    level: int = 1
    grade: Grade = Grade.G3
    stats: Optional[np.ndarray] = None
    techniques: list = field(default_factory=lambda: ["basic"])
    tech_state: dict = field(default_factory=dict)
    flags: set = field(default_factory=set)
    traits: set = field(default_factory=set)
    equipment: dict = field(default_factory=lambda: {"weapon": None, "armor": None})
    inventory: list = field(default_factory=list)
    vows: list = field(default_factory=list)
    extra_actions: list = field(default_factory=list)
    controller: str = "ai"                 # "human" | "ai"
    kind: str = "fighter"                  # fighter | shikigami | spirit | puppet
    record: Any = None                     # PlayerRecord for real players
    crimes: Optional[CrimeLog] = None
    meta: dict = field(default_factory=dict)


@dataclass
class PlayerRecord:
    """One character. A Discord user may own one per server (colony)."""
    server_id: str
    user_id: str
    name: str
    pclass: int = int(PClass.SORCERER)
    level: int = 1
    xp: int = 0
    points: int = 0
    alive: bool = True
    created_ts: float = field(default_factory=time.time)
    last_score_ts: float = field(default_factory=time.time)
    techniques: list = field(default_factory=list)         # innate technique keys
    brain_capacity: int = BRAIN_SLOTS
    tech_state: dict = field(default_factory=dict)         # shikigami roster, copies, spirits...
    inventory: list = field(default_factory=list)
    equipment: dict = field(default_factory=lambda: {"weapon": None, "armor": None})
    vows: list = field(default_factory=list)               # permanent binding vows
    body: Optional[dict] = None                            # body-hop stat overrides
    node: int = 0
    hideout: Optional[int] = None
    kills: dict = field(default_factory=lambda: {"players": 0, "spirits": 0})
    looted: list = field(default_factory=list)             # item keys taken from the dead (sell at any price)
    six_eyes: bool = False                                 # born with the Six Eyes (Limitless always is)
    old_stats: Optional[dict] = None                       # {"hp", "ce", "str", "spd"} rolled at creation (oldstats.py)
    skill_points: int = 0                                  # unspent (skills.py)
    skills: dict = field(default_factory=dict)             # skill -> points spent
    fingers: int = 0                                       # Sukuna's fingers eaten and still caged
    vessel: int = 0                                        # how many this body can cage (20 = a strong vessel)
    ce_frac: float = 1.0                                   # cursed energy left after the last fight (share of maximum)...
    ce_ts: float = 0.0                                     # ...and when that was: it comes back with time
    # Lasting injuries, as fractions so they survive level-ups: HP, per-part HP, which limbs
    # are gone, and max HP lost to soul damage.  None = unhurt.  Nothing heals on its own.
    condition: Optional[dict] = None
    crimes: CrimeLog = field(default_factory=CrimeLog)

    # ---- injuries --------------------------------------------------------------------
    def _cond(self) -> dict:
        if self.condition is None:
            self.condition = {"hp": 1.0, "parts": [1.0] * 6, "gone": [0] * 6, "scar": 0.0}
        return self.condition

    @property
    def injured(self) -> bool:
        c = self.condition
        return bool(c) and (c["hp"] < 0.999 or c["scar"] > 0.001 or any(c["gone"])
                            or any(p < 0.999 for p, g in zip(c["parts"], c["gone"]) if not g))

    @property
    def can_self_heal(self) -> bool:
        """A cursed spirit's own regeneration, or reverse cursed technique: level 10 AND one of the
        techniques whose users managed it in the source."""
        from .data import RCT_TECHNIQUES
        return self.pclass == PClass.CURSED_SPIRIT or (
            self.unlock_level >= 10 and bool(RCT_TECHNIQUES & set(self.techniques)))

    @property
    def can_heal_others(self) -> bool:
        """Outputting reverse cursed energy into someone else: level 12 and Shrine or Copy."""
        from .data import RCT_OUTPUT_TECHNIQUES
        return (self.pclass != PClass.CURSED_SPIRIT and self.unlock_level >= 12
                and bool(RCT_OUTPUT_TECHNIQUES & set(self.techniques)))

    def rested_ce(self, now: float) -> float:
        """Share of maximum cursed energy this character has by ``now``: what the last fight left,
        plus a quarter of the maximum for every five minutes since (the Six Eyes: 85%)."""
        six = has_six_eyes(self.techniques, self.six_eyes)
        rate = SIX_EYES_REST if six else REST_RECOVERY
        return float(min(1.0, self.ce_frac + rate * max(0.0, now - self.ce_ts) / REST_STEP))

    @property
    def efficiency(self) -> float:
        """Percent off technique costs, as a fight will apply it."""
        if has_six_eyes(self.techniques, self.six_eyes):
            return SIX_EYES_EFF
        return float(self.to_spec().stats[Stat.EFF])

    def mend(self, frac: float, limbs: int = 0) -> None:
        """Heal a fraction of max HP and regrow up to ``limbs`` lost limbs. Soul scars stay."""
        c = self._cond()
        c["hp"] = min(1.0, c["hp"] + frac)
        c["parts"] = [p if g else min(1.0, p + frac) for p, g in zip(c["parts"], c["gone"])]
        for i in range(2, 6):                                # arms and legs
            if limbs > 0 and c["gone"][i]:
                c["gone"][i], c["parts"][i] = 0, 0.5
                limbs -= 1
        if not self.injured:
            self.condition = None

    @property
    def mendable(self) -> bool:
        """Hurt in a way healing can fix (soul scars are not)."""
        c = self.condition
        return self.injured and (c["hp"] < 0.999 or any(c["gone"]) or any(p < 0.999 for p in c["parts"]))

    def full_heal(self) -> None:
        """Body and soul. Nothing in the game does this except taking a new body."""
        self.condition = None

    def condition_text(self) -> str:
        c = self.condition
        if not self.injured:
            return "unhurt"
        names = ["head", "torso", "left arm", "right arm", "left leg", "right leg"]
        bits = [f"HP {c['hp']:.0%}"] if c["hp"] < 0.995 else []
        bits += [f"{n} gone" for n, g in zip(names, c["gone"]) if g]
        bits += [f"{n} {p:.0%}" for n, p, g in zip(names, c["parts"], c["gone"]) if not g and p < 0.95]
        if c["scar"] > 0.001:
            bits.append(f"soul scarred (-{c['scar']:.0%} max HP)")
        return ", ".join(bits)

    # ---- progression -----------------------------------------------------------------
    @property
    def unlock_level(self) -> int:
        return self.level + (REINCARNATED_UNLOCK if self.pclass == PClass.REINCARNATED else 0)

    def gain_xp(self, amount: int) -> int:
        """Returns how many levels were gained."""
        self.xp += int(amount)
        gained = 0
        while self.xp >= xp_to_next(self.level):
            self.xp -= xp_to_next(self.level)
            self.level += 1
            gained += 1
            from .skills import points_for_level
            self.skill_points += points_for_level(self.level)       # +10 up to level 10, +5 after
        if self.level >= ADVANCED_LEVEL:
            self.brain_capacity = max(self.brain_capacity, BRAIN_SLOTS + 1)
        return gained

    def score(self, points: int, now: Optional[float] = None) -> None:
        if points > 0:
            self.points += points
            self.last_score_ts = now if now is not None else time.time()

    # ---- conversion ------------------------------------------------------------------
    def to_spec(self, controller: str = "human") -> Spec:
        techs = ["basic"] + (["spirit_body"] if self.pclass == PClass.CURSED_SPIRIT else []) + list(self.techniques)
        if self.six_eyes and "six_eyes" not in techs:
            techs.append("six_eyes")
        flags = {f for k in techs for f in TECHNIQUES[k].flags}
        return Spec(name=self.name, pclass=PClass(self.pclass), level=self.level,
                    grade=grade_for(self.level, techs),
                    stats=build_stats(PClass(self.pclass), self.level, techs, self.body, self.equipment,
                                      self.old_stats, self.skills),
                    techniques=techs, tech_state=self.tech_state, flags=flags,
                    equipment=self.equipment, inventory=self.inventory, vows=list(self.vows),
                    controller=controller, record=self, crimes=self.crimes)

    def to_item(self) -> dict:
        d = {k: copy.deepcopy(v) for k, v in self.__dict__.items() if k != "crimes"}
        d["crimes"] = self.crimes.to_bytes()
        d["body"] = {str(k): v for k, v in self.body.items()} if self.body else None
        return d

    @classmethod
    def from_item(cls, d: dict) -> "PlayerRecord":
        d = dict(d)
        crimes = CrimeLog.from_bytes(d.pop("crimes", None))
        if "skill_points" not in d:                    # a character from before skill points: back-pay them
            from .skills import points_through
            d["skill_points"] = points_through(int(d.get("level", 1)))
        known = {k: v for k, v in d.items() if k in cls.__dataclass_fields__}
        rec = cls(**known)
        rec.equipment = {"weapon": rec.equipment.get("weapon"), "armor": rec.equipment.get("armor")}
        rec.inventory = [k for k in rec.inventory if k in ITEMS]          # items from older saves
        rec.crimes = crimes
        return rec


# ---- NPCs ----------------------------------------------------------------------------
SPIRIT_NAMES = ["Fly Head", "Grasshopper Curse", "Bridge Lurker", "Stairwell Curse",
                "Cocoon Curse", "Disaster Curse"]
SPIRIT_TECH = {Grade.G1: [None, "disaster_flames"], Grade.SPECIAL: ["idle_transfiguration", "disaster_flames", "shrine", "disaster_plants", "disaster_tides", "festering_life", "pestilence"]}


def npc_spirit(grade: Grade, rng: np.random.Generator, name: Optional[str] = None,
               tech: Optional[str] = "auto") -> Spec:
    grade = Grade(grade)
    level = [1, 2, 4, 6, 9, 13][grade]
    if tech == "auto":
        pool = SPIRIT_TECH.get(grade, [None])
        tech = pool[int(rng.integers(len(pool)))]
    techs = ["basic", "spirit_body"] + ([tech] if tech else [])
    stats = build_stats(PClass.CURSED_SPIRIT, level, techs)
    stats[[Stat.MAX_HP, Stat.HP]] *= [0.3, 0.45, 0.7, 1.0, 1.15, 1.4][grade]
    log = CrimeLog()
    for _ in range(int(grade)):
        log.add(Crime.MURDER if rng.random() < 0.5 else Crime.ASSAULT)
    return Spec(name=name or f"{SPIRIT_NAMES[grade]} ({['G4', 'G3', 'G2', 'Semi-1', 'G1', 'Special'][grade]})",
                pclass=PClass.CURSED_SPIRIT, level=level, grade=grade, stats=stats,
                techniques=techs, flags={f for k in techs for f in TECHNIQUES[k].flags}, crimes=log,
                meta={"dmg_mult": [0.3, 0.45, 0.7, 1.0, 1.1, 1.25][grade]})


def npc_fighter(name: str, pclass: PClass, level: int, tech: Optional[str],
                rng: Optional[np.random.Generator] = None, weapon: Optional[str] = None, armor: Optional[str] = None,
                tech_state: Optional[dict] = None) -> Spec:
    """An NPC culling game player (sorcerer, reincarnated sorcerer or mutant)."""
    techs = ["basic"] + (["spirit_body"] if pclass == PClass.CURSED_SPIRIT else []) + ([tech] if tech else [])
    if weapon is None and tech:
        weapon = TECHNIQUES[tech].tool                       # the tool that comes with the technique
    equipment = {"weapon": weapon, "armor": armor}
    log = CrimeLog()
    if rng is not None:
        for _ in range(int(rng.integers(0, 3))):
            log.add(Crime(int(rng.integers(0, 5))))
    spec = Spec(name=name, pclass=pclass, level=level, grade=grade_for(level, techs),
                stats=build_stats(pclass, level, techs, equipment=equipment), techniques=techs,
                tech_state=tech_state or {}, flags={f for k in techs for f in TECHNIQUES[k].flags},
                equipment=equipment, crimes=log)
    if tech == "cursed_spirit_manipulation" and "csm" not in spec.tech_state:
        # an NPC manipulator arrives with curses already swallowed; a player has to go and find theirs
        spec.tech_state["csm"] = {"next": level // 2 + 1, "spirits": [
            {"id": i + 1, "name": f"Stored Curse {i + 1}", "grade": min(4, 1 + i % 3 + level // 8), "level": 4, "tech": None}
            for i in range(level // 2)]}
    if pclass == PClass.REINCARNATED:
        spec.meta["unlock_bonus"] = REINCARNATED_UNLOCK
    return spec


def sorcerer_killer(rng: Optional[np.random.Generator] = None) -> Spec:
    """The one NPC who carries the Inverted Spear of Heaven. It is never sold: it leaves his hands
    only when he dies."""
    spec = npc_fighter("The Sorcerer Killer", PClass.SORCERER, 14, "heavenly_restriction", rng,
                       weapon="inverted_spear")
    spec.meta["killer"] = True
    spec.inventory = ["inventory_curse", "playful_cloud"]       # what the curse wrapped round him is holding
    return spec


def roll_vessel(rng) -> int:
    """How many of Sukuna's fingers a new body can cage. A few are born strong vessels and can hold
    all twenty; for everyone else it is 0, 1 or 2 - and they are not told which."""
    if rng.random() < STRONG_VESSEL:
        return 20
    return int(rng.choice([0, 1, 2], p=[0.5, 0.3, 0.2]))


def finger_bearer(rng: np.random.Generator) -> Spec:
    """A special-grade curse grown around one of Sukuna's fingers. Kill it and the finger is yours."""
    spec = npc_spirit(Grade.SPECIAL, rng, "Finger Bearer", None)
    spec.inventory = ["sukuna_finger"]
    spec.meta.update(bearer=True, dmg_mult=1.0 + 3 * FINGER_AMP)      # the finger feeds it
    return spec


def sukuna_share(fingers: int) -> float:
    """How much of his cursed energy Sukuna can put into a technique: half with no fingers,
    all of it with twenty. It is the only thing the fingers change about him."""
    return min(1.0, SUKUNA_OUT_FLOOR + SUKUNA_OUT_FINGER * max(0, int(fingers)))


def vessel_techniques(techniques) -> list:
    """What Sukuna keeps of the body he takes: its innate technique(s)."""
    return [k for k in techniques if k in TECHNIQUES and TECHNIQUES[k].innate and k != "shrine"
            and not any(f == "remote" or f.startswith("hr_") for f in TECHNIQUES[k].flags)]


def body_hp_of(techniques, pclass=PClass.SORCERER, level: int = SUKUNA_LEVEL) -> float:
    """Maximum HP of a body with these techniques (before any soul scars)."""
    return float(build_stats(pclass, level, ["basic"] + [k for k in techniques if k != "basic"])[Stat.MAX_HP])


def sukuna_npc(fingers: int, rng: Optional[np.random.Generator] = None, vessel=(), host: str = "",
               slash: bool = False, body_hp: float = 0.0) -> Spec:
    """Sukuna walking free in a body he has taken. He is always the same Sukuna - level 20,
    every ability he ever had - and the fingers decide how much cursed energy he has to put into
    them (``sukuna_share``, and his reserves). ``vessel`` is the innate technique of the body he
    took, which is his as well - in a Ten Shadows body that is every shikigami, Mahoraga
    included. What he only learned later (the slash that cuts the world) he still has to learn."""
    fingers = max(1, int(fingers))
    spec = npc_fighter("Sukuna", PClass.REINCARNATED, SUKUNA_LEVEL, "shrine", rng)
    spec.stats[Stat.MAX_CE] = spec.stats[Stat.CE] = SUKUNA_CE_BASE       # (the fingers add the rest when he joins)
    spec.stats[Stat.EFF] = SUKUNA_EFF
    # His HP is the body's. Not told whose: a level-20 body with the vessel's technique, or his own of old.
    kept = vessel_techniques(vessel)
    hp = float(body_hp) if body_hp and body_hp > 0 else (body_hp_of(kept[:1]) if kept else float(spec.stats[Stat.MAX_HP]))
    spec.stats[Stat.MAX_HP] = spec.stats[Stat.HP] = hp
    if host:
        spec.name = f"Sukuna (in {host}'s body)"
    for k in vessel_techniques(vessel):
        spec.techniques.append(k)
        spec.flags |= set(TECHNIQUES[k].flags)
        if k == "ten_shadows":
            from .data import SHIKIGAMI
            spec.tech_state["ten_shadows"] = {"roster": {s: "tamed" for s in SHIKIGAMI}, "inherit": {},
                                              "totality": False, "wheel": {}, "world_slash": bool(slash)}
    spec.meta.update(vessel=vessel_techniques(vessel), host=host, body_hp=hp)
    spec.inventory = ["sukuna_finger"] * fingers
    spec.meta.update(sukuna=True, fingers=fingers, unlock_bonus=99)  # nothing of his is locked behind a level
    return spec
