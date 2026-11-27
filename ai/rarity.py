"""Character-creation odds, carried over unchanged from the original bot (cogs/character_cog.py).

The original bot rolled a class and then an innate technique with ``weight_system``.  Every
number here is the one that bot used, and ``weight_system`` is a line-for-line port of its
algorithm, so a new character has exactly the same chance of each class, each technique and
the Six Eyes as before.

How ``weight_system`` works (it is not a plain weighted pick):
    1. Roll 1..sum(bands) and walk the bands (legend 5, rare 15, uncommon 30, common 50) to find
       which band the roll fell in; the leftover roll inside that band becomes ``value``.
    2. Every entry whose rarity number is >= ``value`` is eligible; one is picked uniformly.
A LOW rarity number therefore means RARE: "Rarity 5" (legend) is only eligible when ``value``
comes out at 5 or less.

Only the four player types the original bot had are rolled: Sorcerer, Cursed Spirit ("Curse")
and Reincarnated ("Reincarnate").  The Mutant (Death Painting) class is never rolled for a new
player - it exists for NPCs.  Set MUTANT_ROLL_WEIGHT above 0 to let players roll it.
"""
from __future__ import annotations

from typing import Optional

from .constants import PClass

# ---- the bands the original weight_system rolled against ------------------------------------
CLASS_BANDS = {"rare": 20, "uncommon": 30, "common": 50}
TECH_BANDS = {"legend": 5, "rare": 15, "uncommon": 30, "common": 50}

# ---- player types (original: {"Sorcerer": 50, "Curse": 30, "Reincarnate": 15}) -------------------
CLASS_RARITY = {PClass.SORCERER: 50, PClass.CURSED_SPIRIT: 30, PClass.REINCARNATED: 15}
MUTANT_ROLL_WEIGHT = 0          # 0 = never rolled (the original bot had no Mutant class)

# ---- techniques, per player type --------------------------------------------------------------
# Keys are ai/data.py technique keys; the comment is the original player_tech.py name.
TECH_RARITY = {
    PClass.SORCERER: {
        "antigravity_system": 15,            # anti_gravity
        "auspicious_beasts": 50,             # auspicious_beasts_summon
        "black_bird": 50,                    # bird_manip
        "blood_manipulation": 50,            # blood_manip
        "boogie_woogie": 30,                 # boogie_woogie
        "comedian": 15,                      # comedian
        "construction": 15,                  # construction (may roll the Six Eyes)
        "copy": 15,                          # copy (may roll the Six Eyes)
        "cursed_speech": 50,                 # cursed_speech
        "cursed_spirit_manipulation": 5,     # cursed_spirit_manip
        "puppet_manipulation": 15,           # hr_max (Mechamaru: heavenly restriction, maximum CE)
        "heavenly_restriction": 15,          # hr_zero (zero cursed energy)
        "limitless": 5,                      # limitless (always has the Six Eyes)
        "projection_sorcery": 30,            # projection_sorcery
        "star_rage": 15,                     # star_rage
        "straw_doll": 30,                    # straw_doll
        "ten_shadows": 5,                    # ten_shadows
    },
    PClass.REINCARNATED: {
        "blood_manipulation": 50,            # blood_manip
        "body_hop": 5,                       # body_hop
        "granite_blast": 30,                 # ce_discharge (Ryu Ishigori)
        "construction": 15,                  # construction
        "contractual_recreation": 10,        # contractual_recreation
        "cursed_speech": 50,                 # cursed_speech
        "explosive_flesh": 50,               # explosive_flesh
        "ice_formation": 15,                 # ice_manip
        "mythical_beast_amber": 15,          # mba
        "shrine": 5,                         # shrine
        "sky_manipulation": 15,              # sky_manip
        "ten_shadows": 5,                    # ten_shadows
    },
    PClass.CURSED_SPIRIT: {
        "disaster_flames": 10,               # disaster_flames
        "disaster_tides": 50,                # disaster_tides
        "idle_transfiguration": 5,           # idle_transfig
        "disaster_plants": 35,               # natures_wrath
        "projection_sorcery": 30,            # projection_sorcery
    },
    PClass.MUTANT: {
        "blood_manipulation": 50,
    },
}

# The original gave copy and construction a 1-in-2 chance of coming with the Six Eyes - for
# sorcerers only (its reincarnate roll never checked).  Limitless always has them (data.py flag).
SIX_EYES_CHANCE = {PClass.SORCERER: {"copy": 0.5, "construction": 0.5}}

# Techniques that exist in the ai engine but were not in the original creation pools (ai/data.py
# PLAYABLE) are in the roll too, each with a rarity number from its grade: special grade rolls as
# a legend (5), grade 1 as rare (15), semi-grade 1 as uncommon (30), the rest as common (50).
# The original techniques keep their own numbers. Set False to roll the original pools only.
INCLUDE_NEW_TECHNIQUES = True
GRADE_TO_RARITY = {5: 5, 4: 15, 3: 30, 2: 50, 1: 50, 0: 50}


def weight_system(bands: dict, entries: dict, rng) -> object:
    """Port of the original ``weight_system``: ``entries`` maps anything -> rarity number."""
    choice = int(rng.integers(1, sum(bands.values()) + 1))
    value = 0
    while value == 0:
        for weight in bands.values():
            if choice <= weight:
                value = choice
                break
            choice -= weight
    eligible = [k for k, r in entries.items() if r >= value]
    return eligible[int(rng.integers(len(eligible)))]


def band_name(rarity: int, bands: dict = TECH_BANDS) -> Optional[str]:
    """The label the original showed after creation ("legend", "rare", "uncommon", "common")."""
    return next((name for name, w in bands.items() if w >= rarity), None)


def class_pool() -> dict:
    pool = dict(CLASS_RARITY)
    if MUTANT_ROLL_WEIGHT > 0:
        pool[PClass.MUTANT] = MUTANT_ROLL_WEIGHT
    return pool


def technique_pool(pclass) -> dict:
    pclass = PClass(pclass)
    pool = dict(TECH_RARITY[pclass])
    if INCLUDE_NEW_TECHNIQUES:
        from .data import PLAYABLE
        from .techniques import TECHNIQUES
        for k in PLAYABLE[pclass]:
            pool.setdefault(k, GRADE_TO_RARITY[int(TECHNIQUES[k].grade)])
    return pool


def roll_class(rng) -> PClass:
    return PClass(weight_system(CLASS_BANDS, class_pool(), rng))


def roll_six_eyes(pclass, tech: str, rng) -> bool:
    """Whether a freshly rolled technique comes with the Six Eyes (beyond Limitless, which always does)."""
    p = SIX_EYES_CHANCE.get(PClass(pclass), {}).get(tech, 0.0)
    return bool(p) and bool(rng.random() < p)


def roll_technique(pclass, rng) -> str:
    return weight_system(TECH_BANDS, technique_pool(pclass), rng)


def rarity_of(pclass, tech: str) -> Optional[str]:
    r = technique_pool(pclass).get(tech)
    return band_name(r) if r is not None else None


def class_rarity_of(pclass) -> Optional[str]:
    r = class_pool().get(PClass(pclass))
    return band_name(r, TECH_BANDS) if r is not None else None     # the original labelled classes with TECH_BANDS too


def odds(bands: dict, entries: dict) -> dict:
    """Exact chance of each entry under ``weight_system`` (for showing players their odds)."""
    total = sum(bands.values())
    p_value = {}
    for w in bands.values():                         # a roll inside a band of width w leaves 1..w
        for v in range(1, w + 1):
            p_value[v] = p_value.get(v, 0.0) + 1.0 / total
    out = {k: 0.0 for k in entries}
    for v, pv in p_value.items():
        eligible = [k for k, r in entries.items() if r >= v]
        for k in eligible:
            out[k] += pv / len(eligible)
    return out


def class_odds() -> dict:
    return odds(CLASS_BANDS, class_pool())


def technique_odds(pclass) -> dict:
    return odds(TECH_BANDS, technique_pool(pclass))
