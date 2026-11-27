"""Enums and tuning constants shared by every module."""
from enum import IntEnum

import numpy as np


class Part(IntEnum):
    HEAD = 0
    TORSO = 1
    L_ARM = 2
    R_ARM = 3
    L_LEG = 4
    R_LEG = 5
    EXTRA_1 = 6      # limbs grown with soul manipulation
    EXTRA_2 = 7


N_PARTS = len(Part)
VITAL = (Part.HEAD, Part.TORSO)
EXTRA = (Part.EXTRA_1, Part.EXTRA_2)
ARMS = (Part.L_ARM, Part.R_ARM) + EXTRA      # grown limbs count as arms
LEGS = (Part.L_LEG, Part.R_LEG)
LIMBS = (Part.L_ARM, Part.R_ARM, Part.L_LEG, Part.R_LEG)

# Body-part requirements are a tuple of groups; ONE part of every group must be usable.
ANY_ARM = (ARMS,)
BOTH_ARMS = ((Part.L_ARM,), (Part.R_ARM,))
ANY_LEG = (LEGS,)
HEAD_REQ = ((Part.HEAD,),)
TORSO_REQ = ((Part.TORSO,),)

PART_HP_FRAC = np.array([0.35, 0.70, 0.24, 0.24, 0.28, 0.28, 0.0, 0.0])   # share of max HP
PART_DMG_MULT = np.array([1.5, 1.0, 0.6, 0.6, 0.6, 0.6, 0.3, 0.3])         # damage -> total HP
PART_ACC = np.array([-0.20, 0.08, 0.0, 0.0, -0.05, -0.05, 0.0, 0.0])       # to-hit modifier


class PState(IntEnum):
    OK = 0
    STUNNED = 1
    DESTROYED = 2
    ABSENT = 3


class Stat(IntEnum):
    HP = 0
    MAX_HP = 1
    CE = 2
    MAX_CE = 3
    STA = 4
    MAX_STA = 5
    STR = 6
    SPD = 7
    DUR = 8
    PER = 9          # perception
    OUT = 10         # cursed energy output
    CE_REGEN = 11
    STA_REGEN = 12
    EFF = 13         # cursed energy efficiency: percent knocked off technique costs


N_STATS = len(Stat)


class Status(IntEnum):
    POISON = 0
    BLEED = 1
    BURN = 2
    STUN = 3          # lose next turn
    SLOW = 4
    BOOST = 5         # CE converted to strength and speed
    SEALED = 6        # innate technique confiscated / burnt out
    CE_SEALED = 7
    JACKPOT = 8       # infinite CE + automatic reverse cursed technique
    EXEC_SWORD = 9    # Executioner's Sword in hand
    GAG_ARMOR = 10    # comedian: nothing sticks while the bit is landing
    RIKA_LINK = 11    # full manifestation
    ANTI_DOMAIN = 12  # simple domain / hollow wicker basket
    CHANNEL = 13      # channelling a shikigami through yourself
    CHARGED = 14      # carries an electric charge: a discharge cannot miss
    AMBER = 15        # Mythical Beast Amber is active; the body will not survive it
    INFINITY = 16     # Limitless: nothing arrives
    NAILED = 17       # Straw Doll: a nail is lodged in them, a link for Resonance
    BUD = 18          # Disaster Plants: a bud feeding on their cursed energy
    FBE = 19          # Falling Blossom Emotion: automatic counter to whatever touches you
    AMPLIFY = 20      # Domain Amplification: techniques that touch you fail; your own is unusable


N_STATUS = len(Status)
DOT_STATUSES = (Status.POISON, Status.BLEED, Status.BURN)
STICKY = (Status.STUN, Status.EXEC_SWORD, Status.AMBER)      # not ticked down each round (a stun is spent by losing a round)


class Grade(IntEnum):
    G4 = 0
    G3 = 1
    G2 = 2
    SEMI1 = 3
    G1 = 4
    SPECIAL = 5


GRADE_NAME = ["Grade 4", "Grade 3", "Grade 2", "Semi-Grade 1", "Grade 1", "Special Grade"]


class PClass(IntEnum):
    SORCERER = 0
    REINCARNATED = 1
    CURSED_SPIRIT = 2
    MUTANT = 3


CLASS_NAME = ["Sorcerer", "Reincarnated Sorcerer", "Cursed Spirit", "Mutant (Death Painting)"]


class DType(IntEnum):
    PHYSICAL = 0
    CURSED = 1
    SOUL = 2


class Kind(IntEnum):
    ATTACK = 0
    DEFENSE = 1
    BUFF = 2
    HEAL = 3
    SUMMON = 4
    DOMAIN = 5
    UTILITY = 6


class Target(IntEnum):
    ENEMY = 0
    SELF = 1
    ALL_ENEMIES = 2
    CORPSE = 3
    CHOICE = 4      # argument picked from a list supplied by the technique
    ANY = 5         # any combatant, living or dead (the effect validates)
    FREE = 6        # the effect reads target and argument itself (Boogie Woogie)


class React(IntEnum):
    DODGE = 0
    BLOCK = 1
    COUNTER = 2
    REINFORCE = 3
    SWAP = 4        # trade places so the attack lands on someone or something else
    COVER = 5       # one of your summons takes the blow for you


class Rng(IntEnum):
    MELEE = 0
    RANGED = 1


# ---- culling game tuning ------------------------------------------------------------
POINTS_PLAYER = 5            # sorcerers, reincarnated sorcerers, mutants
POINTS_SPIRIT = 2            # cursed spirits
RULE_COST = 100              # points needed to add a rule to a colony
INACTIVITY_DAYS = 19         # score must change within this window
DAY = 86400.0

SOUL_PER = 12                # perception needed to perceive / reinforce the soul
REINCARNATED_UNLOCK = 6      # reincarnated sorcerers treat their level as +6 for unlocks
BRAIN_SLOTS = 2              # innate techniques one brain can hold (3 for advanced users)
ADVANCED_LEVEL = 10
CHANT_AMP = 1.5              # incantation bonus
CHANNEL_AMP = 1.4            # channelled techniques hit harder than instant strikes
EFF_CAP = 60.0               # efficiency never removes more than this percent of a cost - for anyone but these two:
SIX_EYES_EFF = 85.0          # the Six Eyes: always the highest there is, whatever the level
SUKUNA_EFF = 70.0            # Sukuna: always the second highest
CE_RECOVERY = 10.0           # percent of maximum cursed energy that comes back each round of a fight
SIX_EYES_RECOVERY = 85.0     # ...with the Six Eyes
REST_RECOVERY = 0.25         # share of maximum cursed energy that comes back per REST_STEP outside a fight
SIX_EYES_REST = 0.85         # ...with the Six Eyes
REST_STEP = 300.0            # seconds (5 minutes)
CLASH_MARGIN = 1.25          # refinement edge needed to crush another domain outright
NONLETHAL_CLASH = 1.3        # a domain whose sure-hit does no harm is that much stronger in a clash
OPEN_EDGE = 1.2              # an open (barrierless) domain attacks the other's shell from outside
MINI_DOMAIN = 1.5            # a barrier shrunk to the size of a ball is that much harder to break
INSIDE_WEAK = 0.9            # a shell hardened on the outside is soft on the inside: against another barrier
SLASH_ROUNDS = 2             # rounds Sukuna needs, once Mahoraga has adapted to Infinity, to shape the world-cutting slash
BRAIN_HEALS = 4              # times reverse cursed technique can restore a burnt-out technique in one fight
AMPLIFY_GUARD = 0.3          # share of an innate technique's damage that gets through Domain Amplification
FBE_GUARD = 0.35             # share of a sure-hit that gets past Falling Blossom Emotion
FRAME_STACKS = 4             # Projection Sorcery: most stacks of speed that can be held
FRAME_STEP = 3.5             # speed and strength gained per stack
FRAME_READ = 0.08            # counter chance a perceptive defender gains per stack
# ---- order of resolution -------------------------------------------------------------------
# Everyone commits one choice per round; nothing is timed in real life. Each action gets a
# number - when in the round it lands - worked out from stats alone, and things resolve in that
# order. 1.0 or more means it lands early in the following round instead.
MELEE_TIME = 0.4             # a speed-10 body closing and striking (shrinks with PLAYER speed)
RANGED_TIME = 0.4            # a speed-1 ranged technique crossing the field (shrinks with TECHNIQUE speed)
BUFF_TIME = 0.2              # a speed-1 buff, summon or stance taking effect (TECHNIQUE speed)
CHANNEL_TIME = 0.5           # activation of anything that has to be channelled
CHANT_TIME = 0.6             # an incantation on top of that
REACT_PER = 16               # perception needed to be offered a defence while committed to an attack
# ---- techniques are NOT balanced against each other ------------------------------------
# Every innate technique has a grade, and a stronger one is simply stronger: these multiply
# its user's cursed energy output (all technique damage, and domain refinement); the square
# root of it goes on strength, durability, HP and the cursed energy pool.
TIER_POWER = {0: 0.5, 1: 0.7, 2: 1.0, 3: 1.4, 4: 2.0, 5: 3.4}         # by Grade (4, 3, 2, semi-1, 1, special)
# How rare each grade of technique is when the culling game hands one out.
TIER_RARITY = {0: 0.15, 1: 0.27, 2: 0.30, 3: 0.15, 4: 0.10, 5: 0.03}
# ---- Sukuna's fingers -------------------------------------------------------------------------
FINGER_AMP = 0.10            # each finger a VESSEL has caged: +10% cursed energy output and strength, on every ability
SUKUNA_LEVEL = 20            # Sukuna himself is always Sukuna: every ability, the same body, whatever he has gathered.
SUKUNA_OUT_FLOOR = 0.5       # What the fingers change is his cursed energy: output is 50% with none...
SUKUNA_OUT_FINGER = 0.025    # ...+2.5% a finger (100% with all twenty)
SUKUNA_CE_BASE = 100         # ...and his reserves are this
SUKUNA_CE_FINGER = 37        # ...+37 a finger (840 with all twenty). His HP is that of the body he is in.
FINGER_CE = 25               # ...and this much more cursed energy
STRONG_VESSEL = 0.05         # share of new characters whose body can cage all twenty
FINGER_BEARERS = 5           # finger-bearing curses lurking in each colony
STALEMATE_ROUNDS = 10        # an NPC that makes no headway for this long withdraws
UNSEEN_PER = 14              # perception needed to track something that cannot be seen
JACKPOT_DMG = 2.0            # damage multiplier while a jackpot is playing
JACKPOT_STR = 1.6            # strength multiplier while a jackpot is playing
DMG_SCALE = 1.35             # global damage tuning knob
DUR_FACTOR = 3.0             # how much each point of durability mitigates
BLACK_FLASH_MULT = 2.5
# Canon lets Uzumaki extract techniques from semi-grade 1 and above; the design brief asks
# for special grade only.  Change this one constant to switch.
UZUMAKI_EXTRACT_MIN_GRADE = Grade.SPECIAL
