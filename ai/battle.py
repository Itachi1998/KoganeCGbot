"""Round-based battle engine.

State for every combatant lives in numpy arrays indexed by combatant slot (stats, body
parts, statuses), so upkeep, damage-over-time, regeneration and area attacks are single
vectorised operations.  ``Combatant`` is a thin view over one row plus the Python-side
bookkeeping (techniques, pending casts, vows).

A round, Magic-style:
    upkeep      regen, damage over time, timers, domain sure-hit, adaptation wheels
    turns       in speed order; a channelled technique is released at the start of the
                caster's NEXT turn, so opponents get a window to read and disrupt it
    reactions   whenever an attack lands on someone they may answer at instant speed
                (dodge / block / counter / reinforce the targeted body part)
"""
from __future__ import annotations

import itertools
import time
import uuid
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from . import ai
from .constants import (REINCARNATED_PER_BONUS, SWITCH_BASE, SWITCH_PER, SWITCH_SPD, SWITCH_MIN, SWITCH_MAX, BUFF_TIME, CHANNEL_TIME, CHANT_TIME, MELEE_TIME, RANGED_TIME, REACT_PER, AMPLIFY_GUARD, FRAME_READ, Grade, FBE_GUARD, CLASH_MARGIN, NONLETHAL_CLASH, OPEN_EDGE, MINI_DOMAIN, INSIDE_WEAK, SIX_EYES_EFF, SUKUNA_EFF, EFF_CAP, JACKPOT_DMG, JACKPOT_STR, STALEMATE_ROUNDS, UNSEEN_PER, ANY_ARM, ANY_LEG, BLACK_FLASH_MULT, CHANNEL_AMP, CHANT_AMP, DAY, DMG_SCALE,
                        DOT_STATUSES, DUR_FACTOR, EXTRA,
                        LEGS, LIMBS, N_PARTS, N_STATS, N_STATUS, PART_ACC, PART_DMG_MULT,
                        PART_HP_FRAC, POINTS_PLAYER, POINTS_SPIRIT, SOUL_PER, STICKY, VITAL,
                        DType, Kind, Part, PClass, PState, React, Rng, Stat, Status, Target)
from . import skills
from .crimes import Crime
from .data import ITEMS, SHIKIGAMI
from .records import Spec, build_stats
from .techniques import ACTION_TECH, ACTIONS, TECHNIQUES, Action, Technique, register

S, ST = Stat, Status
STANCE_EFFECTS = ("anti_domain", "amplify", "falling_blossom")
LOCAL_STATUSES = (ST.POISON, ST.BLEED, ST.BURN, ST.CHARGED, ST.NAILED, ST.BUD)   # these sit in a body part

THROW = Action("throw", "Thrown Object", dtype=DType.PHYSICAL, rng=Rng.RANGED, sta=8,
               requires=ANY_ARM, tags=frozenset({"blunt"}))
register(Technique("field", "Battlefield", innate=False, copyable=False, actions=(THROW,)))

_ARRAYS = (("stats", (N_STATS,), float), ("part_hp", (N_PARTS,), float),
           ("part_max", (N_PARTS,), float), ("part_state", (N_PARTS,), np.int8),
           ("part_stun", (N_PARTS,), np.int8), ("part_ce", (N_PARTS,), float),
           ("part_rf", (N_PARTS,), float), ("limb_ce", (N_PARTS,), float),
           ("st_dur", (N_STATUS,), np.int16), ("st_mag", (N_STATUS,), float),
           ("st_part", (N_STATUS,), np.int8),            # the body part a status sits in (-1 = whole body)
           ("alive", (), bool))


# ---- IO -------------------------------------------------------------------------------
class IO:
    """Front-end adapter. The CLI subclasses this; a Discord bot would too."""

    def say(self, text: str) -> None:                       # public battle log
        print(text)

    def tell(self, c, text: str) -> None:                   # private to one player
        print(f"   ({c.name} only) {text}")

    def ask(self, b, c, prompt: str, options: list) -> Optional[int]:
        return None                                          # None -> the AI decides

    def turn(self, b, c) -> None:                           # commit phase: an action or a defence
        ai.act(b, c)

    def channel(self, b, c) -> None:                        # channel phase: where the cursed energy goes
        ai.channel(b, c)


class QuietIO(IO):
    def __init__(self):
        self.lines: list[str] = []

    def say(self, text):
        self.lines.append(text)

    def tell(self, c, text):
        self.lines.append(f"({c.name}) {text}")


@dataclass
class FieldObject:
    fid: str
    name: str
    role: str                 # elevation | throwable | cover | speed
    hp: float = 40.0
    weight: float = 0.0       # STR needed to throw
    power: float = 0.0
    oid: Optional[int] = None  # id of the map object it came from
    imbued: float = 0.0        # cursed energy poured into it (Boogie Woogie can swap it; it throws harder)


@dataclass
class Pending:
    act: Action
    targets: list
    part: Part
    amp: float
    chant_left: int               # 1 if an incantation is part of this cast
    arg: Optional[str]
    land_at: float = 0.0          # the moment on the timeline at which it takes effect
    parts: list = field(default_factory=list)
    seen: set = field(default_factory=set)
    loosed: bool = False          # let go before the user's technique burnt out: it still lands


@dataclass
class Domain:
    owner: str
    key: str
    name: str
    rounds: int
    tick: Optional[str]
    data: dict = field(default_factory=dict)


class Combatant:
    def __init__(self, b: "Battle", idx: int, cid: str, spec: Spec, team: int, owner: Optional[str]):
        self.b, self.idx, self.cid, self.team, self.owner = b, idx, cid, team, owner
        self.name, self.pclass, self.level, self.grade = spec.name, spec.pclass, spec.level, spec.grade
        self.techniques = list(spec.techniques)
        self.tech_state = spec.tech_state                 # shared with the PlayerRecord
        self.flags = set(spec.flags)
        self.base_traits = set(spec.traits)
        self.equipment, self.inventory = spec.equipment, spec.inventory
        self.extra_actions = list(spec.extra_actions)
        self.controller, self.kind, self.record = spec.controller, spec.kind, spec.record
        self.crimes = spec.crimes
        self.meta = dict(spec.meta)
        self.pending: Optional[Pending] = None            # the action in progress, if any
        self.plan: Optional[str] = None                   # this round's choice: attack | defend | wait
        self.guard: Optional[Action] = None               # the defence chosen for this round
        self.guard_arg: Optional[str] = None
        self.standing: Optional[Action] = None            # a defence set up to stay as the default
        self.standing_arg: Optional[str] = None
        self.standing_until = 0                           # last round it holds
        self.charge = 0.0                                 # cursed energy gathered this round, not yet used
        self.charged: list = []                           # the body parts it sits in
        self.read_by: set = set()                         # who perceived this round's gathering
        self.pos: Optional[str] = None                    # field object id, None = open ground
        self.reactions = 1
        self.fled = self.corpse = self.free_used = False
        self.last_seen: set = set()
        self.last_hit_by: Optional[str] = None
        self.granted: dict = {}                           # one-shot actions (Uzumaki extraction)
        self.cooldowns: dict = {}
        self.mult = {"out": 1.0, "str": 1.0, "tool": 1.0}
        self.dmg_mult = float(self.meta.get("dmg_mult", 1.0))   # weak curses hit softly
        self.vow_flags: set = set()
        self.sealed_parts: set = set()
        self.vow_instant = self.must_chant = False
        self.adapt: dict = self.meta.pop("adapt", {})     # tag -> adaptation progress 0..1
        self.channeling: Optional[str] = None
        self.points_gained = self.xp_gained = 0

    def __str__(self):
        return self.name

    # ---- array views -------------------------------------------------------------------
    @property
    def alive(self) -> bool:
        return bool(self.b.alive[self.idx])

    def base(self, s) -> float:
        return float(self.b.stats[self.idx, s])

    hp = property(lambda self: self.base(S.HP))
    max_hp = property(lambda self: self.base(S.MAX_HP))
    max_ce = property(lambda self: self.base(S.MAX_CE))

    @property
    def ce(self) -> float:
        return self.base(S.CE)

    @ce.setter
    def ce(self, v):
        self.b.stats[self.idx, S.CE] = max(0.0, v)

    @property
    def sta(self) -> float:
        return self.base(S.STA)

    @sta.setter
    def sta(self, v):
        self.b.stats[self.idx, S.STA] = max(0.0, v)

    def has(self, st) -> bool:
        return bool(self.b.st_dur[self.idx, st] > 0)

    def mag(self, st) -> float:
        return float(self.b.st_mag[self.idx, st])

    def usable(self, p) -> bool:
        return self.b.part_state[self.idx, p] == PState.OK and p not in self.sealed_parts

    def stat(self, s) -> float:
        """Effective stat after statuses, injuries, vows and terrain."""
        v = self.base(s)
        if s in (S.STR, S.SPD) and self.has(ST.BOOST):
            v += self.mag(ST.BOOST)
        if s == S.SPD:
            if self.has(ST.SLOW):
                v -= self.mag(ST.SLOW)
            v *= 1 - 0.3 * sum(not self.usable(p) for p in LEGS)
            obj = self.b.field.get(self.pos)
            if obj and obj.role == "speed":
                v += 3
        elif s == S.STR:
            v *= self.mult["str"] * (JACKPOT_STR if self.has(ST.JACKPOT) else 1.0)
        elif s == S.OUT:
            v *= self.mult["out"]
        return max(v, 0.0)

    # ---- derived -----------------------------------------------------------------------
    @property
    def traits(self) -> set:
        if self.channeling and self.has(ST.CHANNEL):
            return self.base_traits | set(SHIKIGAMI[self.channeling].traits)
        return self.base_traits

    @property
    def innate(self) -> list:
        return [k for k in self.techniques if TECHNIQUES[k].innate]

    @property
    def root(self) -> "Combatant":
        c = self
        while c.owner:
            c = self.b.by_cid[c.owner]
        return c

    @property
    def unlock_level(self) -> int:
        return self.level + self.meta.get("unlock_bonus", 0) + (
            self.record.unlock_level - self.record.level if self.record else 0)

    @property
    def borrows_ce(self) -> bool:
        """Ten Shadows shikigami have no cursed energy of their own: they run on their user's.
        (Puppets, released cursed spirits and Rika each carry their own.)"""
        return bool(self.meta.get("owner_ce")) and self.owner is not None

    @property
    def weapon(self):
        return ITEMS.get(self.equipment.get("weapon") or "")

    @property
    def armor(self):
        return ITEMS.get(self.equipment.get("armor") or "")

    def ts(self, key: str, default: dict) -> dict:
        return self.tech_state.setdefault(key, default)


class Battle:
    def __init__(self, server_id: str = "local", seed: Optional[int] = None, io: Optional[IO] = None,
                 colony=None, world=None, node: Optional[int] = None, now: Optional[float] = None,
                 cache=None):
        self.id = uuid.uuid4().hex[:8]
        self.server_id = server_id
        self.rng = np.random.default_rng(seed)
        self.io = io or IO()
        self.colony, self.world, self.node, self.cache = colony, world, node, cache
        self.now = now if now is not None else time.time()
        self.cap = 0
        self._alloc(16)
        self.fighters: list[Combatant] = []
        self.by_cid: dict[str, Combatant] = {}
        self.field: dict[str, FieldObject] = {}
        self.round = 0                                   # whole beats elapsed
        self.time = 0.0                                  # position inside the current round (ordering only)
        self.phase: Optional[str] = None                 # "channel" | "commit" inside a round, else None
        self.domain: Optional[Domain] = None            # the domain in force
        self.rival: Optional[Domain] = None             # a second one locked in a clash with it
        self.truces: set = set()
        self.over = False
        self.log: list[str] = []
        self._next_team = 100
        self._cid_n: dict[str, int] = {}
        self._last_kill: dict[str, int] = {}             # root cid -> round of its side's latest kill
        self.broken_oids: list = []                      # map objects broken in this fight (colony.py re-applies them)
        self._plain = False                              # the blow being resolved carries no cursed energy
        self.last_tags: set = set()                      # tags of the damage being applied (for hooks)

    # ---- persistence (Redis snapshot) --------------------------------------------------
    def __getstate__(self):
        state = dict(self.__dict__)
        state["io"] = state["world"] = state["cache"] = None
        return state

    def attach(self, io=None, world=None, cache=None):
        self.io, self.world, self.cache = io or IO(), world, cache
        return self

    def _alloc(self, cap: int) -> None:
        for name, shape, dt in _ARRAYS:
            new = np.zeros((cap,) + shape, dtype=dt)
            old = getattr(self, name, None)
            if old is not None:
                new[:len(old)] = old
            setattr(self, name, new)
        self.cap = cap

    # ---- roster ------------------------------------------------------------------------
    @property
    def n(self) -> int:
        return len(self.fighters)

    @property
    def day(self) -> int:
        epoch = self.colony.created_ts if self.colony else 0.0
        return int((self.now - epoch) // DAY)

    def new_team(self) -> int:
        self._next_team += 1
        return self._next_team

    def add(self, spec: Spec, team: int, owner: Optional[Combatant] = None) -> Combatant:
        from . import effects, vows
        if self.n == self.cap:
            self._alloc(self.cap * 2)
        i = self.n
        stats = spec.stats if spec.stats is not None else build_stats(
            spec.pclass, spec.level, spec.techniques, equipment=spec.equipment)
        self.stats[i] = stats
        self.part_max[i] = stats[S.MAX_HP] * PART_HP_FRAC
        self.part_hp[i] = self.part_max[i]
        self.part_state[i] = PState.OK
        self.part_state[i, list(EXTRA)] = PState.ABSENT
        self.st_part[i] = -1
        self.alive[i] = True
        cond = spec.record.condition if spec.record is not None else None
        if cond:                                         # injuries carry over from earlier fights
            mx = stats[S.MAX_HP] * (1 - cond["scar"])
            self.stats[i, S.MAX_HP] = mx
            self.stats[i, S.HP] = max(1.0, mx * cond["hp"])
            self.part_max[i] = mx * PART_HP_FRAC
            self.part_hp[i] = self.part_max[i]
            for p in range(6):
                if cond["gone"][p]:
                    self.part_state[i, p], self.part_hp[i, p] = PState.DESTROYED, 0.0
                else:
                    self.part_hp[i, p] = max(1.0, self.part_max[i, p] * cond["parts"][p])
        prefix = {"shikigami": "s", "spirit": "s", "puppet": "r"}.get(
            spec.kind, "p" if spec.controller == "human" else "e")
        self._cid_n[prefix] = self._cid_n.get(prefix, 0) + 1
        c = Combatant(self, i, f"{prefix}{self._cid_n[prefix]}", spec, team, owner.cid if owner else None)
        c.meta["base_max_hp"] = float(stats[S.MAX_HP])   # before soul scars
        self.fighters.append(c)
        self.by_cid[c.cid] = c
        for key in spec.vows:
            vows.apply(self, c, vows.VOWS[key], announce=False)
        held = spec.meta.get("fingers", spec.record.fingers if spec.record is not None else 0)
        if held:                                         # Sukuna's fingers amplify everything their holder does
            effects.set_fingers(self, c, held)
        effects.fire(self, "on_join", c)
        if spec.record is not None and spec.record.ce_frac < 1.0:      # spent in an earlier fight; time brings it back
            self.stats[i, S.CE] = self.stats[i, S.MAX_CE] * spec.record.rested_ce(self.now)
        return c

    def add_object(self, name: str, role: str, **kw) -> FieldObject:
        fid = name.lower().split()[0]
        while fid in self.field:
            fid += "2"
        self.field[fid] = FieldObject(fid, name, role, **kw)
        return self.field[fid]

    def hostile(self, a: Combatant, b: Combatant) -> bool:
        return a.team != b.team and frozenset((a.root.cid, b.root.cid)) not in self.truces

    def active(self, c: Combatant) -> bool:
        if not c.alive or c.fled:
            return False
        if "remote" in c.flags:                       # not here in person: present only through what they sent
            return bool(self.summons(c)) or (
                "hr_max" in c.flags and self.why_cant(c, ACTIONS["deploy_puppet"]) is None)
        return True

    def enemies(self, c: Combatant, targetable: bool = True) -> list:
        return [o for o in self.fighters if o.alive and not o.fled and self.hostile(c, o)
                and not (targetable and "remote" in o.flags)]

    def summons(self, c: Combatant, kind: Optional[str] = None) -> list:
        return [o for o in self.fighters if o.alive and o.owner == c.cid and (kind is None or o.kind == kind)]

    def corpses(self) -> list:
        return [o for o in self.fighters if o.corpse]

    def find(self, token: str) -> Optional[Combatant]:
        token = token.lower()
        if token in self.by_cid:
            return self.by_cid[token]
        hits = [c for c in self.fighters if c.name.lower().startswith(token)]
        return hits[0] if len(hits) == 1 else None

    # ---- output / input ----------------------------------------------------------------
    def say(self, text: str) -> None:
        self.log.append(text)
        self.io.say(text)

    def tell(self, c: Combatant, text: str) -> None:
        if c.root.controller == "human":
            self.io.tell(c.root, text)

    def ask(self, c: Combatant, prompt: str, options: list, weights=None) -> int:
        if c.controller == "human":                      # automated summons decide for themselves
            k = self.io.ask(self, c, prompt, options)
            if k is not None:
                return k
        w = np.asarray(weights if weights is not None else [1.0] * len(options), dtype=float)
        return int(self.rng.choice(len(options), p=w / w.sum()))

    # ---- what can a combatant do -------------------------------------------------------
    def actions_for(self, c: Combatant) -> list:
        keys = [a.key for t in c.techniques for a in TECHNIQUES[t].actions]
        keys += c.extra_actions
        mutual = self.domain_of(c) is not None and self.domain_of(c).key == "mutual_love"
        if c.has(ST.RIKA_LINK) or mutual:               # every copy is open through Rika, or inside his own domain
            keys += [a.key for t in c.tech_state.get("copy", {}).get("stored", []) for a in TECHNIQUES[t].actions]
        if c.channeling and c.has(ST.CHANNEL):
            keys += SHIKIGAMI[c.channeling].actions
        keys += [k for k, left in c.granted.items() if left > 0]
        return [ACTIONS[k] for k in dict.fromkeys(keys)]

    def costs(self, c: Combatant, act: Action) -> tuple:
        """(cursed energy, stamina). Curses pay for physical exertion with cursed energy."""
        ce = act.ce
        if ce > 0:                                       # efficiency: the same technique for less energy
            ce = max(1, int(np.ceil(ce * (1 - self.efficiency(c) / 100.0) - 1e-9)))
        if c.pclass == PClass.CURSED_SPIRIT and c.kind == "fighter":
            return ce + act.sta, 0
        return ce, act.sta

    def efficiency(self, c: Combatant) -> float:
        """Percent off cursed energy costs. The Six Eyes are always the best there is and Sukuna
        always next; everyone else has what level, class and vows give them, up to EFF_CAP."""
        root = c.root if c.borrows_ce else c
        if root.meta.get("six_eyes"):
            return SIX_EYES_EFF
        if root.meta.get("sukuna"):
            return SUKUNA_EFF
        return float(min(root.base(S.EFF), EFF_CAP))

    def ce_pool(self, c: Combatant) -> float:
        if c.borrows_ce:
            return self.ce_pool(c.root)
        pool = c.ce
        if c.has(ST.RIKA_LINK):
            pool += sum(r.ce for r in self.summons(c) if "rika" in r.base_traits)
        return pool

    def spend_ce(self, c: Combatant, amount: float) -> None:
        if c.has(ST.JACKPOT):
            return
        if c.borrows_ce:
            c = c.root
        if c.has(ST.RIKA_LINK):                      # draw on Rika's reserve first
            for r in self.summons(c):
                if "rika" in r.base_traits:
                    take = min(r.ce, amount)
                    r.ce -= take
                    amount -= take
        c.ce -= amount

    def missing_parts(self, c: Combatant, act: Action):
        for group in act.requires:
            if not any(c.usable(p) for p in group):
                return group
        return None

    def choices(self, c: Combatant, act: Action) -> list:
        from . import effects
        fn = effects.CHOICES.get(act.effect)
        return fn(self, c) if fn else []

    def why_cant(self, c: Combatant, act: Action) -> Optional[str]:
        """None if ``c`` may use ``act`` right now, else the reason."""
        from . import effects
        tech = TECHNIQUES[ACTION_TECH[act.key]]
        if "remote" in c.flags and not act.params.get("remote_ok"):
            return "your body is in the hideout - act through your puppets"
        if act.needs_status is not None and not c.has(act.needs_status):
            return f"requires {Status(act.needs_status).name}"
        if c.granted.get(act.key, 0) <= 0 and c.unlock_level < act.min_level:
            return f"unlocks at level {act.min_level}"
        if (act.min_per and c.record is not None and c.kind == "fighter" and c.granted.get(act.key, 0) <= 0
                and self.unlock_per(c) < act.min_per):
            return f"unlocks at perception {act.min_per} (yours counts as {self.unlock_per(c):.0f})"
        if tech.innate and c.has(ST.SEALED) and act.needs_status is None:
            return "your technique is sealed"
        if tech.innate and c.has(ST.AMPLIFY):
            return "Domain Amplification is up - your own technique cannot be used through it"
        if (c.has(ST.ANTI_DOMAIN) and c.meta.get("anti_hands") and act.effect not in STANCE_EFFECTS
                and any(Part.L_ARM in g or Part.R_ARM in g for g in act.requires)):
            return "both hands are holding the Hollow Wicker Basket (`drop` it first)"
        ce, sta = self.costs(c, act)
        if ce > 0 or act.react == React.REINFORCE:
            if not c.borrows_ce and c.max_ce <= 0:
                return "you have no cursed energy"
            if c.has(ST.CE_SEALED):
                return "your cursed energy is sealed"
            if not c.has(ST.JACKPOT) and self.ce_pool(c) < max(ce, 1):
                return f"needs {ce} CE"
        if sta > c.sta:
            return f"needs {sta} stamina"
        group = self.missing_parts(c, act)
        if group:
            return "needs a usable " + " or ".join(Part(p).name for p in group)
        if c.cooldowns.get(act.key, 0) > self.round:
            return f"recharging until round {c.cooldowns[act.key]}"
        if act.kind == Kind.DOMAIN and "no_domain" in c.vow_flags:
            return "a binding vow forbids your domain"
        if act.kind == Kind.DOMAIN and c.meta.get("brain_spent"):
            return "your brain has been burnt out and healed too many times to expand a domain again in this fight"
        if act.react == React.DODGE and "no_dodge" in c.vow_flags:
            return "a binding vow forbids dodging"
        if act.key == "weapon" and "no_tools" in c.vow_flags:
            return "a binding vow forbids cursed tools"
        cond = act.params.get("cond")
        if cond:
            msg = effects.CONDS[cond](self, c)
            if msg:
                return msg
        if act.target == Target.CHOICE and not self.choices(c, act):
            return "nothing to choose from"
        return None

    @staticmethod
    def unlock_per(c: Combatant) -> float:
        """Perception as it counts for unlocking techniques: trained perception, plus a reincarnated
        sorcerer's past life (awakened sorcerers have to earn theirs)."""
        bonus = REINCARNATED_PER_BONUS if c.root.pclass == PClass.REINCARNATED else 0
        if c.meta.get("sukuna"):
            bonus = 99
        return float(c.base(S.PER)) + bonus

    def elevated(self, c: Combatant) -> bool:
        obj = self.field.get(c.pos)
        return bool(obj and obj.role == "elevation")

    def can_reach(self, atk: Combatant, tgt: Combatant, act: Action) -> bool:
        if act.rng == Rng.RANGED or act.params.get("reach") or atk.pos == tgt.pos:
            return True
        if not self.elevated(atk) and not self.elevated(tgt):
            return True
        return "flight" in atk.traits or bool((self.part_state[atk.idx, list(EXTRA)] == PState.OK).any())

    # ---- taking an action --------------------------------------------------------------
    def perform(self, c: Combatant, act: Action, target: Optional[Combatant] = None,
                part: Part = Part.TORSO, chant: bool = False, arg: Optional[str] = None) -> bool:
        """Returns True if the action was taken (and the turn is spent)."""
        from . import effects
        why = self.why_cant(c, act)
        if why:
            self.tell(c, f"Can't use {act.name}: {why}.")
            return False
        t = act.target
        if t == Target.ENEMY:
            if not (target and target.alive and self.hostile(c, target) and "remote" not in target.flags):
                self.tell(c, "Pick a living enemy.")
                return False
            if not self.can_reach(c, target, act):
                self.tell(c, f"{target} is out of reach - use a ranged technique or move to them.")
                return False
        elif t == Target.CORPSE and not (target and target.corpse):
            self.tell(c, "Pick a corpse.")
            return False
        elif t == Target.ANY and target is None:
            self.tell(c, "Pick a target.")
            return False
        elif t == Target.CHOICE and arg not in [k for k, _ in self.choices(c, act)]:
            self.tell(c, "Options: " + ", ".join(f"{k} ({label})" for k, label in self.choices(c, act)))
            return False
        check = effects.VALID.get(act.effect)
        if check:
            msg = check(self, c, act, target, arg)
            if msg:
                self.tell(c, msg)
                return False
        targets = [c] if t == Target.SELF else [target] if target is not None else []
        ce, sta = self.costs(c, act)
        quick = effects.QUICK.get(act.effect)
        free = bool(quick and quick(self, c)) or c.vow_instant
        gathered = self.phase == "commit" and act.channel and not free
        if gathered:                                     # it has to have been channelled for
            missing = self.charged_for(c, act)
            if missing:
                self.tell(c, f"Can't use {act.name}: {missing}.")
                return False
            c.charge = max(0.0, c.charge - ce)           # paid out of what was gathered
        else:
            self.spend_ce(c, ce)
        c.sta -= sta
        if c.granted.get(act.key, 0) > 0:
            c.granted[act.key] -= 1
        if act.params.get("cd"):
            c.cooldowns[act.key] = self.round + act.params["cd"]

        quick = effects.QUICK.get(act.effect)
        skip = bool(quick and quick(self, c))            # nothing to activate right now
        if act.channel and not skip and c.vow_instant:   # binding vow: no activation time, once
            c.vow_instant, c.must_chant, skip = False, True, True
            self.say(f"{c} honours a binding vow: {act.name} needs no time to activate. "
                     f"Every technique from now on needs an incantation.")
        chanting = chant and act.can_chant
        spoken = bool(act.channel and not skip and (chanting or c.must_chant or act.params.get("must_chant")))
        lead = self.timing(c, act, chant=spoken, skip=skip)
        amp = (CHANNEL_AMP if act.channel else 1.0) * (CHANT_AMP if chanting else 1.0)
        c.pending = Pending(act, [x.cid for x in targets], part, amp, int(spoken), arg, land_at=self.time + lead)
        c.plan = "attack"
        if gathered:                                     # already read (or not) in the channel phase
            c.pending.parts, c.pending.seen = list(c.charged), set(c.read_by)
        elif act.channel and not skip:
            self._channel(c)                             # (outside a round: gather and be read on the spot)
            if spoken:
                self.say(f"{c} begins an incantation.")
        if lead >= 1.0:
            self.tell(c, f"{act.name} will not land until next round.")
        return True

    def defend(self, c: Combatant, act: Action, arg: Optional[str] = None) -> bool:
        """Commit this round to a defence instead of an action. It answers every attack that
        reaches you this round (each use still costs what it costs). A defence with ``hold``
        stays up as your default for that many rounds, so later rounds are free for attacking."""
        why = "that is not a defence" if act.react is None else self.why_cant(c, act)
        if why:
            self.tell(c, f"Can't defend with {act.name}: {why}.")
            return False
        if act.react == React.COVER and arg is not None and not any(s.cid == arg for s in self.summons(c)):
            self.tell(c, "That is not one of your summons.")
            return False
        c.plan, c.guard, c.guard_arg = "defend", act, arg
        hold = act.params.get("hold", 0)
        if hold:
            c.standing, c.standing_arg, c.standing_until = act, arg, self.round + hold - 1
        self.say(f"{c} takes up a defence: {act.name}" + (f" (holds for {hold} rounds)." if 1 < hold < 50
                                                           else " (until told otherwise)." if hold else "."))
        return True

    def wait(self, c: Combatant) -> bool:
        """Commit to nothing: stay watchful. You answer attacks with whatever seems best."""
        c.plan = "wait"
        self.say(f"{c} holds back and watches.")
        return True

    def defence_of(self, c: Combatant) -> Optional[Action]:
        """The defence in force for a fighter this round: the one chosen, else the standing one."""
        if c.guard is not None:
            return c.guard
        return c.standing if c.standing is not None and self.round <= c.standing_until else None

    def timing(self, c: Combatant, act: Action, chant: bool = False, skip: bool = False) -> float:
        """When in the round an action lands (0 = at once; 1.0 or more = early next round).

        activation   belongs to the technique (channelling, incantation); the same for everyone
        melee        the body has to get there: PLAYER speed
        everything else (ranged techniques, buffs, summons, domains): TECHNIQUE speed
        """
        lead = 0.0 if skip else (act.activation if act.activation is not None else CHANNEL_TIME * act.channel)
        if chant:
            lead += CHANT_TIME
        if act.kind == Kind.ATTACK and act.rng == Rng.MELEE:
            return lead + MELEE_TIME * 20.0 / (10.0 + c.stat(S.SPD) + skills.melee_speed(c))
        return lead + (RANGED_TIME if act.kind == Kind.ATTACK else BUFF_TIME) / max(act.speed, 0.1)

    def channel(self, c: Combatant, parts: list, amount: float) -> bool:
        """Channel phase: gather ``amount`` cursed energy into body parts. It leaves the pool now.
        A channelled technique can only be chosen afterwards if the parts it needs hold enough.
        Whatever is not used hardens the parts it sits in for the round."""
        parts = list(dict.fromkeys(Part(p) for p in parts))
        if amount <= 0 or not parts:
            return False
        if (not c.borrows_ce and c.max_ce <= 0) or c.has(ST.CE_SEALED):
            self.tell(c, "You have no cursed energy to gather.")
            return False
        if not c.has(ST.JACKPOT) and self.ce_pool(c) < amount:
            self.tell(c, f"You only have {self.ce_pool(c):.0f} cursed energy.")
            return False
        if any(not c.usable(p) for p in parts):
            self.tell(c, "You can only gather energy in a body part you can still use.")
            return False
        self.spend_ce(c, amount)
        c.charge, c.charged = float(amount), parts
        self.part_ce[c.idx] = 0
        self.part_ce[c.idx, parts] = amount / len(parts)
        return True

    def channel_for(self, c: Combatant, act: Action) -> bool:
        """Gather exactly what one action needs, where it needs it."""
        if self.missing_parts(c, act):
            return False
        parts = [next(q for q in g if c.usable(q)) for g in act.requires] or [Part.TORSO]
        return self.channel(c, parts, self.costs(c, act)[0])

    def charged_for(self, c: Combatant, act: Action) -> Optional[str]:
        """None if this round's gathering supports ``act``, else what is missing."""
        need = self.costs(c, act)[0]
        for group in act.requires:
            if not any(p in c.charged for p in group):
                return "you gathered no cursed energy in the " + " or ".join(Part(p).name for p in group)
        if not c.charged:
            return "you gathered no cursed energy this round"
        if c.charge + 1e-9 < need and not c.has(ST.JACKPOT):
            return f"you gathered {c.charge:.0f} cursed energy; it needs {need}"
        return None

    def _reveal(self) -> None:
        """End of the channel phase: those perceptive enough learn where energy has gathered."""
        for c in self.fighters:
            c.read_by = set()
            if not c.alive or c.fled or c.charge <= 0:
                continue
            where = " and ".join(Part(q).name for q in c.charged)
            conceal = 6 + 0.4 * c.level
            for o in self.fighters:
                if not o.alive or o is c or o.team == c.team:
                    continue
                six = "six_eyes" in o.flags or "revealed" in c.vow_flags
                per = o.stat(S.PER)
                if six and c.meta.get("intent_name"):
                    self.tell(o, f"You read {c} completely: {c.charge:.0f} cursed energy in the {where}, "
                                 f"shaped for {c.meta['intent_name']}.")
                elif six or per >= conceal + 4:
                    self.tell(o, f"You read {c}: {c.charge:.0f} cursed energy gathering in the {where}.")
                elif per >= conceal:
                    self.tell(o, f"You sense cursed energy gathering in {c}'s {where}.")
                else:
                    continue
                c.read_by.add(o.cid)

    def _settle_charge(self) -> None:
        """After everyone has committed: energy that was gathered and not used reinforces the
        parts it sits in for this round."""
        for c in self.fighters:
            if c.alive and c.charge > 0.5 and c.charged:
                self.part_rf[c.idx, c.charged] += 1.5 * c.charge / len(c.charged)
                self.tell(c, f"The {c.charge:.0f} cursed energy you did not use hardens your "
                             + " and ".join(Part(q).name for q in c.charged) + " for the round.")
            c.charge = 0.0

    def _channel(self, c: Combatant) -> None:
        """The channelling turn: cursed energy gathers in body parts and can be read."""
        p = c.pending
        parts = [next(q for q in g if c.usable(q)) for g in p.act.requires] or [Part.TORSO]
        p.parts = parts
        self.part_ce[c.idx, parts] = p.act.ce / len(parts)
        self.say(f"{c} gathers cursed energy...")
        where = " and ".join(Part(q).name for q in parts)
        conceal = 6 + 0.4 * c.level
        for o in self.fighters:
            if not o.alive or o is c or o.team == c.team:
                continue
            per = o.stat(S.PER) + (99 if "revealed" in c.vow_flags or "six_eyes" in o.flags else 0)
            if per >= conceal + 4:
                aim = ", ".join(self.by_cid[x].name for x in p.targets if x != c.cid) or "everyone nearby"
                self.tell(o, f"You read {c}: {p.act.name} ({p.act.ce} CE) building in the {where}, aimed at {aim}.")
            elif per >= conceal:
                self.tell(o, f"You sense cursed energy building in {c}'s {where}.")
            else:
                continue
            p.seen.add(o.cid)

    def _release(self, c: Combatant) -> None:
        p, c.pending = c.pending, None
        self.part_ce[c.idx] = 0
        act = p.act
        tech_key = ACTION_TECH[act.key]
        from . import effects
        cond = act.params.get("cond")                    # things may have changed since it was committed
        if cond and effects.CONDS[cond](self, c):
            self.say(f"{c}'s {act.name} comes to nothing: {effects.CONDS[cond](self, c)}.")
            return
        if (TECHNIQUES[tech_key].innate and tech_key not in c.techniques and not c.has(ST.RIKA_LINK)
                and not (self.domain_of(c) and self.domain_of(c).key == "mutual_love")
                and tech_key in c.tech_state.get("copy", {}).get("stored", [])):
            self.say(f"{c}'s {act.name} comes apart: the link to Rika is gone, and the copy with it.")
            return
        sealed = c.has(ST.SEALED) and not (p.loosed and c.meta.get("burnt"))
        if self.missing_parts(c, act) or (TECHNIQUES[tech_key].innate and (sealed or c.has(ST.AMPLIFY))):
            self.say(f"{c}'s {act.name} fizzles - the cursed energy has nowhere to go.")
            return
        decoys = [x for x in p.targets if x.startswith("obj:")]
        if decoys:                                      # the target was swapped out for an object
            for d in decoys:
                obj = self.field.get(d[4:])
                self.say(f"{c} releases {act.name} - into " + (f"the {obj.name} left in the target's place."
                                                               if obj else "empty air."))
                if obj:
                    self._break_object(obj, c)
            p.targets = [x for x in p.targets if not x.startswith("obj:")]
            if not p.targets:
                return
        targets = [self.by_cid[x] for x in p.targets]
        if act.target == Target.ENEMY:
            targets = [x for x in targets if x.alive and not x.fled and self.can_reach(c, x, act)]
            if not targets:                             # original target gone: pick another
                pool = [e for e in self.enemies(c) if self.can_reach(c, e, act)]
                if not pool:
                    self.say(f"{c}'s {act.name} disperses with nothing to hit.")
                    return
                targets = [pool[int(self.rng.integers(len(pool)))]]
        c.last_seen = p.seen
        if act.channel:
            self.say(f"{c} releases {act.name}!" + (" (amplified by incantation)" if p.amp > CHANNEL_AMP else ""))
        self.resolve(c, act, targets, p.part, p.amp, p.arg)
        c.last_seen = set()

    def resolve(self, c, act, targets, part, amp, arg) -> None:
        from . import effects
        if act.effect:
            effects.EFFECTS[act.effect](self, c, act, targets, part, amp, arg)
        elif act.kind == Kind.ATTACK:
            if act.target == Target.ALL_ENEMIES:
                self.aoe(c, act, amp)
            else:
                for t in targets:
                    self.strike(c, t, act, part, amp)
        else:                                           # plain buff
            self.say(f"{c} uses {act.name}.")
            for st, ch, dur, mag in act.statuses:
                self.add_status(c, st, ch, dur, mag)

    # ---- adaptation (Mahoraga's wheel) -------------------------------------------------
    @staticmethod
    def tags_of(act: Action, extra=()) -> set:
        return set(act.tags) | set(extra) | {ACTION_TECH.get(act.key, "?"), f"act:{act.key}"}

    def adapt_resist(self, tgt: Combatant, tags) -> float:
        if "adapt" not in tgt.traits or not tgt.adapt:
            return 0.0
        best = 0.0
        for t in tags:
            if t in TECHNIQUES:                          # knowing a technique helps it strike back (adapt_pierce);
                continue                                 # what it resists is the phenomenon, or the exact attack
            v = tgt.adapt.get(t)
            if v is not None:                           # the exact attack: immunity. Related
                best = max(best, v if t.startswith("act:") else min(v, 0.8))   # phenomena: 80%.
        return best

    def adapt_note(self, tgt: Combatant, tags) -> None:
        if "adapt" not in tgt.traits:
            return
        fresh = []
        for t in tags:
            if t not in tgt.adapt:
                tgt.adapt[t] = 0.0
                if not t.startswith("act:"):
                    fresh.append(t)
            elif tgt.adapt[t] < 1.0:                    # struck again: analysis speeds up
                tgt.adapt[t] = min(1.0, tgt.adapt[t] + 0.15)
        if fresh:
            self.say(f"   The eight-handled wheel over {tgt} begins analysing: {', '.join(sorted(fresh))}.")

    def adapt_pierce(self, atk: Combatant, tgt: Combatant) -> float:
        if "adapt" not in atk.traits:
            return 0.0
        return max([atk.adapt.get(k, 0.0) for k in tgt.innate] + [0.0])

    def carries_ce(self, atk: Combatant, act: Action) -> bool:
        """Whether a blow has cursed energy in it. Without any, it cannot hurt a curse, and a
        sorcerer it kills comes back as one."""
        if atk.pclass == PClass.CURSED_SPIRIT or atk.kind != "fighter":
            return True                                  # curses, shikigami and puppets are made of it
        if self.costs(atk, act)[0] > 0 or act.needs_status is not None:
            return True
        if atk.has(ST.BOOST) or atk.has(ST.JACKPOT) or atk.has(ST.AMBER):
            return True                                  # a body flooded with cursed energy
        if act.effect == "weapon_strike":
            return bool(atk.weapon) and not atk.weapon.mundane       # a cursed tool carries its own
        return False

    def perceives_soul(self, c: Combatant) -> bool:
        w = c.weapon
        return (c.stat(S.PER) + skills.soul_sight(c) >= SOUL_PER or "soul_strike" in c.flags
                or bool(w and "soul_strike" in w.flags))

    def passive_mult(self, atk, tgt, dtype, tags, bypass=False) -> float:
        """Technique-level defences that scale or void incoming damage."""
        if "remote" in tgt.flags:
            return 0.0
        if not bypass:
            if tgt.has(ST.INFINITY) and self.sure_hit_owner() != atk.root.cid:
                self.say(f"   It slows, and slows, and never arrives: the infinity between {atk} and {tgt}.")
                return 0.0
            if tgt.has(ST.GAG_ARMOR):
                self.say(f"   It bounces off {tgt} like a rubber prop - the bit is still running.")
                return 0.0
            if ("soul_body" in tgt.flags and not tgt.has(ST.SEALED) and dtype != DType.SOUL
                    and not self.perceives_soul(atk)):
                self.say(f"   {tgt}'s flesh warps around the blow; {atk} cannot perceive the soul, so nothing is harmed.")
                return 0.0
        r = self.adapt_resist(tgt, tags)
        soul = skills.soul_damage(atk) if "soul_body" in tgt.flags else 1.0      # trained soul perception
        if r > 0:
            self.say(f"   {tgt} has adapted ({r:.0%} resisted).")
        keep = 1.0 - r
        if "liquid" in tags and not bypass and any(o.alive and o.team == tgt.team and "rct" in o.traits
                                                   for o in self.fighters):
            self.say("   Round Deer's reverse cursed energy unravels the liquid metal before it arrives.")
            keep *= 0.25
        return keep * soul

    # ---- damage ------------------------------------------------------------------------
    def _mitigate(self, idx, parts, raw, dtype) -> np.ndarray:
        """Vectorised durability + reinforcement for any number of targets."""
        raw = np.atleast_1d(np.asarray(raw, dtype=float))
        if dtype == DType.SOUL:                         # the soul ignores the body's toughness
            return raw
        out = raw * 100.0 / (100.0 + DUR_FACTOR * self.stats[idx, S.DUR])
        used = np.minimum(self.part_rf[idx, parts], out)
        self.part_rf[idx, parts] -= used
        return out - used

    def _react(self, tgt, atk, act, part, name, dtype, bypass):
        """Which defence, if any, meets this attack.

        chose a defence this round .... that defence, every time, no questions
        has a standing defence ......... that one
        committed to an attack ......... nothing - unless a technique of theirs defends as it
                                         attacks, or their perception is high enough to be asked
        waiting ........................ whatever seems best, automatically
        """
        from . import effects
        if tgt.has(ST.STUN) or tgt.meta.get("stunned_in") == self.round:
            return None

        def usable(a):
            return (a is not None and a.react is not None and self.why_cant(tgt, a) is None
                    and not (bypass and TECHNIQUES[ACTION_TECH[a.key]].innate)
                    and not (dtype == DType.SOUL and a.react == React.REINFORCE)
                    and not (a.react == React.SWAP and not effects.swap_candidates(self, tgt, atk))
                    and not (a.react == React.COVER and not self.summons(tgt)))

        opts = [a for a in self.actions_for(tgt) if usable(a) and a.react != React.COVER]
        choice = self.defence_of(tgt)
        if choice is not None:
            choice = choice if usable(choice) else None
        elif tgt.plan == "attack":
            linked = [a for a in opts if a.params.get("while_attacking")]
            if linked:                                   # a technique that defends as it attacks
                choice = linked[0]
            elif tgt.stat(S.PER) >= REACT_PER and tgt.reactions > 0 and opts:
                choice = self._switch_window(tgt, atk, part, name, opts)
        elif tgt.plan == "wait" or tgt.controller != "human":
            choice = ai.pick_reaction(self, tgt, atk, opts) if opts and tgt.reactions > 0 else None
            tgt.reactions -= choice is not None
        elif opts and tgt.reactions > 0:                 # no choice made at all (scripted scenes): ask
            tgt.reactions -= 1
            seen = " You read this one coming." if tgt.cid in atk.last_seen else ""
            k = self.ask(tgt, f"{atk} attacks {tgt}'s {Part(part).name} with {name}.{seen} React?",
                         [f"{a.name} ({a.react.name.lower()})" for a in opts] + ["Take the hit"])
            choice = opts[k] if k < len(opts) else None
        if choice:
            if choice.react != React.REINFORCE:
                ce, sta = self.costs(tgt, choice)
                self.spend_ce(tgt, ce)
                tgt.sta -= sta
            fx = choice.params.get("on_react")
            if fx:
                effects.REACT_FX[fx](self, tgt)
        return choice

    def switch_chance(self, tgt: Combatant, atk: Combatant) -> float:
        """Odds of getting a defence up in time after dropping a committed move (constants.SWITCH_*)."""
        p = (SWITCH_BASE + SWITCH_PER * (tgt.stat(S.PER) - REACT_PER)
             + SWITCH_SPD * (tgt.stat(S.SPD) - atk.stat(S.SPD)))
        return float(np.clip(p, SWITCH_MIN, SWITCH_MAX))

    def _switch_window(self, tgt: Combatant, atk: Combatant, part, name: str, opts: list) -> Optional[Action]:
        """Perception check: tgt is committed to a move, has no defence set, and is perceptive enough
        to see this attack coming. Keep the move and take the hit - or drop the move and try to get a
        defence up, which comes off with ``switch_chance``. Either way it uses up a reaction."""
        tgt.reactions -= 1
        p = self.switch_chance(tgt, atk)
        mine = tgt.pending.act.name if tgt.pending is not None else None
        keep = f"Keep {mine} and take the hit" if mine else "Keep going and take the hit"
        if tgt.controller == "human":
            k = self.ask(tgt, f"PERCEPTION CHECK - {atk} attacks your {Part(part).name} with {name} while you are "
                              f"committed{f' to {mine}' if mine else ''}. Keep your move, or drop it for a defence "
                              f"({p:.0%} chance to get it up in time)?",
                         [keep] + [f"Switch: {a.name} ({a.react.name.lower()}, {p:.0%})" for a in opts])
            want = opts[k - 1] if k else None
        else:
            want = ai.pick_reaction(self, tgt, atk, opts)
        if want is None:
            self.tell(tgt, "You hold to your move and take what comes.")
            return None
        if tgt.pending is not None:                      # the move is given up, whether or not this works
            self.say(f"{tgt} abandons {tgt.pending.act.name} to defend.")
            tgt.pending = None
        tgt.plan, tgt.guard, tgt.guard_arg = "defend", None, None
        if self.rng.random() >= p:
            self.say(f"{tgt} tries to bring up {want.name} - too late!")
            return None
        tgt.guard = want                                 # and it stays up for the rest of the round
        self.say(f"{tgt} sees it coming and switches to {want.name}!")
        return want

    def strike(self, atk: Combatant, tgt: Combatant, act: Action, part: Part = Part.TORSO,
               amp: float = 1.0, *, power: Optional[float] = None, dtype: Optional[DType] = None,
               sure_hit: bool = False, no_react: bool = False, extra_tags=(),
               label: Optional[str] = None, nullify: bool = False, plain: Optional[bool] = None) -> float:
        """One attack against one body part. Returns damage dealt (0 on a miss).
        ``plain`` forces whether the blow is free of cursed energy (default: worked out)."""
        from . import effects
        if not tgt.alive:
            return 0.0
        plain = (not self.carries_ce(atk, act)) if plain is None else plain
        if plain and tgt.pclass == PClass.CURSED_SPIRIT:
            self.say(f"{atk}'s {label or act.name} passes through {tgt} like smoke: there is no cursed "
                     f"energy in it.")
            return 0.0
        if self.part_state[tgt.idx, part] in (PState.DESTROYED, PState.ABSENT):
            part = Part.TORSO
        power = act.power if power is None else power
        gear = atk.armor
        if (gear and act.rng == Rng.MELEE and act.effect != "weapon_strike"
                and (act.dtype == DType.PHYSICAL or act.key == "ce_strike")):
            limb = "kick" if any(Part.L_LEG in g for g in act.requires) else "fist" if act.requires else None
            power += gear.params.get(limb, 0) if limb else 0     # gauntlets and greaves hit harder
        dtype = act.dtype if dtype is None else dtype
        name = label or act.name
        tags = self.tags_of(act, extra_tags)
        pierce = self.adapt_pierce(atk, tgt)
        bypass = nullify or pierce >= 1.0 or atk.has(ST.AMPLIFY)     # amplification cancels what it touches
        perceived = tgt.cid in atk.last_seen
        ranged = act.rng == Rng.RANGED

        if not sure_hit and not no_react:               # attacks nobody saw coming cannot be answered
            if atk.meta.pop("ambush", False):
                no_react = True
                self.say(f"   {atk} strikes out of nowhere.")
            elif "unseen" in atk.traits and tgt.stat(S.PER) < UNSEEN_PER:
                no_react = True
                self.say(f"   {tgt} never sees it coming.")
        reaction = None if (sure_hit or no_react) else self._react(tgt, atk, act, part, name, dtype, bypass)
        rtype = reaction.react if reaction else None
        if rtype == React.COVER:                         # a summon steps into the blow
            mine = self.summons(tgt)
            want = tgt.guard_arg if tgt.guard is reaction else tgt.standing_arg
            sub = next((x for x in mine if x.cid == want), None) or max(mine, key=lambda x: x.hp)
            self.say(f"{sub} throws itself between {atk} and {tgt}.")
            return self.strike(atk, sub, act, part, amp, power=power, dtype=dtype, no_react=True,
                               extra_tags=extra_tags, label=label, nullify=nullify, plain=plain)
        if rtype == React.SWAP:
            sub = effects.swap_reaction(self, tgt, atk)
            if sub is not None and not isinstance(sub, Combatant):       # an imbued object takes it
                self.say(f"{atk}'s {name} lands on the {sub.name} instead.")
                sub.hp -= power * amp * 2
                if sub.hp <= 0:
                    self.say(f"   {sub.name} is destroyed.")
                    self._break_object(sub, atk)
                return 0.0
            if sub is not None:
                return self.strike(atk, sub, act, part, amp, power=power, dtype=dtype, no_react=True,
                                   extra_tags=extra_tags, label=label, nullify=nullify)

        # Electric cursed energy: lightning aimed at someone already carrying a charge is drawn to it.
        drawn = not sure_hit and "lightning" in tags and "electric_ce" in atk.flags and tgt.has(ST.CHARGED)
        if drawn:
            self.say(f"   The charge on {tgt} pulls the lightning in. It cannot miss.")
            if rtype == React.DODGE:
                self.say(f"   {tgt} moves; the lightning follows the charge.")
        elif not sure_hit:
            acc = 0.88 + PART_ACC[part] + act.acc + 0.012 * (atk.stat(S.SPD) - tgt.stat(S.SPD))
            if act.rng == Rng.MELEE:
                acc += skills.melee_acc(atk)             # trained physical speed
            if tgt.has(ST.STUN):
                acc += 0.2
            if "unseen" in tgt.traits and atk.stat(S.PER) < UNSEEN_PER:
                acc -= 0.35                              # you know it is there; you cannot say where
            if self.rng.random() > np.clip(acc, 0.25, 0.98):
                self.say(f"{atk}'s {name} misses {tgt}.")
                return 0.0
            if rtype == React.DODGE:
                obj = self.field.get(tgt.pos)
                p = (0.30 + 0.025 * (tgt.stat(S.SPD) - atk.stat(S.SPD)) + reaction.params.get("dodge", 0.0)
                     + (0.2 if perceived else 0.0) + (0.15 if obj and obj.role == "speed" else 0.0))
                if self.rng.random() < np.clip(p, 0.05, 0.9):
                    self.say(f"{tgt} dodges {atk}'s {name} ({reaction.name}).")
                    return 0.0
                self.say(f"{tgt} tries to dodge but is too slow.")

        raw = power * amp * DMG_SCALE * (1 + atk.stat(S.STR if dtype == DType.PHYSICAL else S.OUT) / 25)
        raw *= self.rng.uniform(0.9, 1.1) * (JACKPOT_DMG if atk.has(ST.JACKPOT) else 1.0) * atk.dmg_mult
        if act.rng == Rng.MELEE:
            raw *= skills.melee_mult(atk)                         # trained physical strength
            raw += 0.2 * float(self.limb_ce[atk.idx].sum())      # grown limbs hit as hard as the CE in them
            if self.costs(atk, act)[0] > 0 and self.rng.random() < 0.03 + 0.003 * atk.level:
                raw *= BLACK_FLASH_MULT
                self.say(f"   BLACK FLASH! Space distorts around {atk}'s strike.")
        if pierce > 0:
            raw *= 1 + 0.5 * pierce
        if "positive" in tags and tgt.pclass == PClass.CURSED_SPIRIT:
            raw *= 2.0

        countered = False
        if rtype == React.COUNTER:
            p = (0.30 + 0.02 * (tgt.stat(S.PER) - atk.stat(S.PER)) + 0.01 * (tgt.stat(S.SPD) - atk.stat(S.SPD))
                 + reaction.params.get("counter", 0.0) + (0.2 if perceived else 0.0))
            frames = effects._frames(atk)
            if frames and tgt.stat(S.PER) >= SOUL_PER:   # a second planned in advance can be read
                p += FRAME_READ * frames
            if self.rng.random() < np.clip(p, 0.05, 0.85):
                countered, raw = True, raw * 0.5
                self.say(f"{tgt} reads the attack and counters!")
                effects.frames_broken(self, atk, f"{tgt} was already standing where the path ended.")
            else:
                raw *= 1.2
                self.say(f"{tgt} mistimes the counter.")
        elif rtype == React.BLOCK:
            frac = min(0.9, reaction.params.get("block", 0.5) + (0.1 if perceived else 0.0))
            raw *= 1 - frac
            self.say(f"{tgt} blocks with {reaction.name} (-{frac:.0%}).")
        elif rtype == React.REINFORCE:
            est = raw * 100.0 / (100.0 + DUR_FACTOR * tgt.base(S.DUR))
            spend = float(min(self.ce_pool(tgt), reaction.params.get("max", 30) + 2 * tgt.level, np.ceil(est / 1.5)))
            self.spend_ce(tgt, spend)
            self.part_rf[tgt.idx, part] += spend * 1.5
            self.say(f"{tgt} floods the {Part(part).name} with {spend:.0f} cursed energy.")

        raw *= self.passive_mult(atk, tgt, dtype, tags, bypass)
        if "inverse" in tgt.flags and not bypass and not tgt.has(ST.SEALED) and raw > 0:
            strong = raw >= 30                           # Inverse: the strong made weak, the weak made strong
            raw *= 0.3 if strong else 1.8
            self.say(f"   Inverse: the blow lands {'far softer' if strong else 'far harder'} than it was thrown.")
        undone = (tgt.has(ST.AMPLIFY) and not nullify and raw > 0
                  and TECHNIQUES[ACTION_TECH.get(act.key, "basic")].innate)
        if undone:                                       # the technique comes apart; only the force arrives
            raw *= AMPLIFY_GUARD
            self.say(f"   {name} comes apart against {tgt}'s Domain Amplification; only the force behind it lands.")
        if sure_hit and tgt.has(ST.FBE) and raw > 0:
            raw *= FBE_GUARD
            self.say(f"   {tgt}'s Falling Blossom Emotion meets it the instant it touches.")
        worn = tgt.armor
        if worn and int(part) in worn.params.get("parts", ()) and dtype != DType.SOUL and raw > 0:
            raw *= 1 - worn.params["guard"]              # armor-type cursed tools guard the parts they cover
            self.say(f"   {tgt}'s {worn.name} take some of it.")
        cover = self.field.get(tgt.pos)
        if ranged and cover and cover.role == "cover" and raw > 0:
            cover.hp -= raw * 0.4
            raw *= 0.6
            self.say(f"   {cover.name} absorbs part of it.")
            if cover.hp <= 0:
                self.say(f"   {cover.name} is destroyed.")
                self._break_object(cover, atk)
        if nullify:                                      # technique-cancelling tools cut through reinforcement
            self.part_rf[tgt.idx, part] = 0
        dmg = float(self._mitigate(np.array([tgt.idx]), np.array([int(part)]), raw, dtype)[0])
        self.adapt_note(tgt, tags)
        self._plain = plain
        self.apply_damage(atk, tgt, part, dmg, dtype, tags, name)
        self._plain = False
        effects.fire(self, "on_hit", atk, tgt, act, part, dmg)
        if dmg > 0 and tgt.alive and not undone:
            for st, ch, dur, mag in act.statuses:
                self.add_status(tgt, st, ch, dur, mag, tags, part)
            if ("blood" in tags and atk.root.pclass == PClass.MUTANT and "body_hop" not in tgt.flags and tgt.kind == "fighter"
                    and tgt.pclass in (PClass.SORCERER, PClass.REINCARNATED)):
                self.add_status(tgt, ST.POISON, 1.0, 3, 5.0, tags, part)
        if countered and tgt.alive and atk.alive and self.can_reach(tgt, atk, ACTIONS["punch"]):
            self.strike(tgt, atk, ACTIONS["punch"], Part.TORSO, 1.3, no_react=True, label="counter-blow",
                        plain=tgt.max_ce <= 0 and not self.carries_ce(tgt, ACTIONS["punch"]))
        return dmg

    def aoe(self, atk: Combatant, act: Action, amp: float = 1.0, targets=None, sure_hit: bool = False,
            power: Optional[float] = None) -> None:
        """Area attack: one vectorised pass over every target (no reactions, torso hits)."""
        targets = [t for t in (targets if targets is not None else self.enemies(atk)) if t.alive]
        if not targets:
            self.say(f"{atk}'s {act.name} hits nothing.")
            return
        idx = np.array([t.idx for t in targets])
        parts = np.full(len(targets), int(Part.TORSO))
        tags = self.tags_of(act)
        scale = 1 + atk.stat(S.STR if act.dtype == DType.PHYSICAL else S.OUT) / 25
        raw = ((act.power if power is None else power) * amp * scale * DMG_SCALE
               * (JACKPOT_DMG if atk.has(ST.JACKPOT) else 1.0) * atk.dmg_mult * self.rng.uniform(0.9, 1.1, len(targets)))
        raw *= np.array([self.passive_mult(atk, t, act.dtype, tags,
                                           self.adapt_pierce(atk, t) >= 1 or atk.has(ST.AMPLIFY)) for t in targets])
        undone = np.array([t.has(ST.AMPLIFY) and TECHNIQUES[ACTION_TECH.get(act.key, "basic")].innate
                           for t in targets])
        raw *= np.where(undone, AMPLIFY_GUARD, 1.0)      # Domain Amplification takes the technique apart
        if sure_hit:                                     # Falling Blossom Emotion meets a sure-hit on contact
            raw *= np.array([FBE_GUARD if t.has(ST.FBE) else 1.0 for t in targets])
        if not sure_hit:                                 # cover helps against blasts
            raw *= np.array([0.6 if (o := self.field.get(t.pos)) and o.role == "cover" else 1.0 for t in targets])
        dmg = self._mitigate(idx, parts, raw, act.dtype)
        for t, d in zip(targets, dmg):
            self.adapt_note(t, tags)
            self.apply_damage(atk, t, Part.TORSO, float(d), act.dtype, tags, act.name)
            if d > 0 and t.alive and not t.has(ST.AMPLIFY):
                for st, ch, dur, mag in act.statuses:
                    self.add_status(t, st, ch, dur, mag, tags, Part.TORSO)

    def apply_damage(self, atk: Optional[Combatant], tgt: Combatant, part: Part, dmg: float,
                     dtype: DType, tags=(), name: str = "attack") -> None:
        from . import effects
        if dmg <= 0 or not tgt.alive:
            if tgt.alive:
                self.say(f"{atk or 'It'} hits {tgt} with {name} - no damage.")
            return
        i = tgt.idx
        if dtype == DType.SOUL and tgt.stat(S.PER) >= SOUL_PER and tgt.ce > 0 and not tgt.has(ST.CE_SEALED):
            guard = min(tgt.ce, dmg * 0.5)               # perceptive fighters armour the soul
            tgt.ce -= guard
            dmg -= guard
            self.say(f"   {tgt} perceives the attack on their soul and reinforces it ({guard:.0f} CE).")
        limb = part in LIMBS or part in EXTRA
        left = float(self.part_hp[i, part])
        self.part_hp[i, part] -= dmg * (1.5 if limb and "slash" in tags else 1.0)
        # Losing a limb maims but does not kill: a limb can only bleed away what it had left.
        loss = (min(dmg, left) if limb else dmg) * PART_DMG_MULT[part]
        self.stats[i, S.HP] -= loss
        if dtype == DType.SOUL:                          # soul damage is permanent
            self.stats[i, S.MAX_HP] = max(1.0, self.stats[i, S.MAX_HP] - loss * 0.5)
            self.stats[i, S.HP] = min(self.stats[i, S.HP], self.stats[i, S.MAX_HP])
        if atk:
            tgt.last_hit_by = atk.cid
        self.say(f"{atk or 'It'} hits {tgt}'s {Part(part).name} with {name}: {dmg:.0f} damage "
                 f"[{max(tgt.hp, 0):.0f}/{tgt.max_hp:.0f} HP]" + (" (soul)" if dtype == DType.SOUL else ""))
        self.last_tags = set(tags)
        effects.fire(self, "on_damage", tgt, atk, dmg)
        if tgt.has(ST.JACKPOT):                          # automatic reverse cursed technique
            self.full_restore(tgt)
            self.say(f"   {tgt}'s body rebuilds itself instantly - the jackpot is still playing.")
            return
        if self.part_hp[i, part] <= 0:
            self.part_hp[i, part] = 0
            if part in VITAL:
                self.say(f"   {tgt}'s {Part(part).name} is destroyed.")
                self.kill(tgt, atk)
                return
            self.part_state[i, part] = PState.ABSENT if part in EXTRA else PState.DESTROYED
            self.limb_ce[i, part] = 0
            self.say(f"   {tgt}'s {Part(part).name} is severed!")
            for st, _ in self.part_statuses(tgt, part):  # what was in the limb goes with the limb
                self.clear_status(tgt, st)
                self.say(f"   The {st.name.lower()} goes with it.")
            if atk:
                effects.fire(self, "on_sever", tgt, atk, part)
        elif part not in VITAL and dmg >= 0.5 * self.part_max[i, part] and self.part_state[i, part] == PState.OK:
            self.part_state[i, part] = PState.STUNNED
            self.part_stun[i, part] = 2
            self.say(f"   {tgt}'s {Part(part).name} goes numb.")
        if tgt.hp <= 0:
            self.kill(tgt, atk)

    def _break_object(self, obj: FieldObject, by: Optional[Combatant]) -> None:
        self.field.pop(obj.fid, None)
        for c in self.fighters:
            if c.pos == obj.fid:
                c.pos = None
        if obj.oid is not None and by is not None:       # property damage goes on the record
            self.broken_oids.append(obj.oid)
            if self.world is not None:
                self.world.mark_broken(obj.oid)
            if by.root.crimes is not None:
                by.root.crimes.add(Crime.VANDALISM, obj.oid, self.day)

    def add_status(self, tgt: Combatant, st, chance=1.0, dur=1, mag=1.0, tags=(), part=None) -> bool:
        """``part``: where it took hold. Poison, bleeding, burns, charges and buds sit in the limb
        that was hit - and go with that limb if it is lost."""
        if not tgt.alive or (chance < 1.0 and self.rng.random() > chance):
            return False
        if tags and self.adapt_resist(tgt, tags) >= 0.8:
            return False
        i = tgt.idx
        self.st_dur[i, st] = max(self.st_dur[i, st], dur)
        self.st_mag[i, st] = max(self.st_mag[i, st], mag)
        where = ""
        if part is not None and st in LOCAL_STATUSES and self.part_state[i, part] in (PState.OK, PState.STUNNED):
            self.st_part[i, st] = int(part)
            where = f" in the {Part(part).name}"
        self.say(f"   {tgt} is affected by {Status(st).name}{where} ({dur} rounds).")
        if st == ST.STUN:                                # stunned: rounds are lost, and so is whatever was underway
            if tgt.pending:
                self.say(f"   {tgt}'s {tgt.pending.act.name} is interrupted.")
                tgt.pending = None
                self.part_ce[i] = 0
        return True

    def clear_status(self, c: Combatant, st) -> None:
        self.st_dur[c.idx, st] = 0
        self.st_mag[c.idx, st] = 0
        self.st_part[c.idx, st] = -1

    def part_statuses(self, c: Combatant, part) -> list:
        """Statuses sitting in one body part, as (Status, beats left)."""
        i = c.idx
        return [(Status(s), int(self.st_dur[i, s])) for s in LOCAL_STATUSES
                if self.st_dur[i, s] > 0 and self.st_part[i, s] == int(part)]

    def heal(self, c: Combatant, amount: float, limbs: int = 0) -> None:
        i = c.idx
        self.stats[i, S.HP] = min(self.stats[i, S.MAX_HP], self.stats[i, S.HP] + amount)
        ok = self.part_state[i] <= PState.STUNNED
        self.part_hp[i] = np.where(ok, np.minimum(self.part_max[i], self.part_hp[i] + amount * PART_HP_FRAC),
                                   self.part_hp[i])
        for p in LIMBS:
            if limbs > 0 and self.part_state[i, p] == PState.DESTROYED:
                self.part_state[i, p] = PState.OK
                self.part_hp[i, p] = 0.5 * self.part_max[i, p]
                limbs -= 1
                self.say(f"   {c}'s {Part(p).name} regrows.")
        self.say(f"{c} recovers to {c.hp:.0f}/{c.max_hp:.0f} HP.")

    def full_restore(self, c: Combatant) -> None:
        i = c.idx
        self.stats[i, S.HP] = self.stats[i, S.MAX_HP]
        present = self.part_state[i] != PState.ABSENT
        self.part_state[i, present] = PState.OK
        self.part_hp[i] = np.where(present, self.part_max[i], self.part_hp[i])
        self.part_stun[i] = 0
        for st in DOT_STATUSES:
            self.clear_status(c, st)

    def kill(self, tgt: Combatant, killer: Optional[Combatant] = None, force: bool = False) -> None:
        from . import effects
        if not tgt.alive:
            return
        if not force and effects.death_save(self, tgt):
            return
        if tgt.has(ST.JACKPOT) and not force:
            self.full_restore(tgt)
            self.say(f"   {tgt} should be dead - the jackpot rebuilds them.")
            return
        self.alive[tgt.idx] = False
        self.stats[tgt.idx, S.HP] = 0
        tgt.pending = None
        tgt.corpse = tgt.kind == "fighter"
        self.say(f"*** {tgt} is {'killed' if tgt.kind == 'fighter' else 'destroyed'}"
                 + (f" by {killer}" if killer else "") + ". ***")
        if tgt.record:
            tgt.record.alive = False
        plain, self._plain = self._plain, False
        self._credit(killer, tgt)
        self._loot(killer, tgt)
        if killer is not None:
            self._last_kill[killer.root.cid] = self.round
        if (plain and killer is not None and tgt.kind == "fighter" and tgt.max_ce > 0
                and tgt.pclass in (PClass.SORCERER, PClass.REINCARNATED)):
            self._rise(tgt, killer)
        effects.fire(self, "on_death", tgt, killer)
        for s in self.summons(tgt):
            self.unsummon(s)
        if self.domain_of(tgt):
            self.close_domain(self.domain_of(tgt), burnout=False)

    def _loot(self, killer: Optional[Combatant], victim: Combatant) -> None:
        """The killer takes what the dead were carrying. Looted things can be sold at any price."""
        k = killer.root if killer else None
        if victim.kind != "fighter" or k is None or k is victim or k.kind != "fighter":
            return
        if k.meta.get("sukuna") and victim.record is not None and victim.record.fingers:
            self.say(f"   Sukuna reaches into {victim} and takes back what was his.")
            victim.inventory.extend(["sukuna_finger"] * victim.record.fingers)
            victim.record.fingers = 0
        taken = [v for v in victim.equipment.values() if v] + list(victim.inventory)
        if not taken:
            return
        k.inventory.extend(taken)
        if k.meta.get("sukuna"):                         # every finger he recovers is more of himself
            from . import effects
            effects.set_fingers(self, k, k.inventory.count("sukuna_finger"))
        if k.record is not None:
            k.record.looted.extend(taken)
        if victim.record is not None:
            victim.inventory.clear()
            victim.equipment.update({slot: None for slot in victim.equipment})
        self.say(f"   {k} takes from the body: {', '.join(ITEMS[x].name for x in taken)}.")

    def _rise(self, victim: Combatant, killer: Combatant) -> None:
        """A sorcerer killed without cursed energy does not stay dead."""
        from .records import npc_spirit
        tech = next((t for t in victim.innate if TECHNIQUES[t].copyable), None)
        spec = npc_spirit(max(victim.grade, Grade.G3), self.rng, f"Vengeful Curse of {victim.name}", tech)
        spec.meta.update(vengeful=True, prey=killer.root.cid)
        self.say(f"   There was no cursed energy in the blow that killed {victim}. Something of them stays, "
                 f"sours, and stands back up: {spec.name}.")
        self.add(spec, self.new_team())

    def unsummon(self, s: Combatant) -> None:
        if s.alive:
            self.alive[s.idx] = False
            self.say(f"   {s} dissolves.")
            for x in self.summons(s):
                self.unsummon(x)

    def _credit(self, killer: Optional[Combatant], victim: Combatant) -> None:
        k = killer.root if killer else None
        if k is None or k is victim.root:
            return
        if victim.kind == "fighter":
            spirit = victim.pclass == PClass.CURSED_SPIRIT
            pts = POINTS_SPIRIT if spirit else POINTS_PLAYER
            xp = 12 * (int(victim.grade) + 1) + 4 * victim.level
            if not spirit and k.crimes is not None:
                k.crimes.add(Crime.MURDER, victim.idx, self.day)
        else:
            pts, xp, spirit = 0, 5, True
        k.points_gained += pts
        k.xp_gained += xp
        if k.record:
            k.record.score(pts, self.now)
            if victim.kind == "fighter":
                k.record.kills["spirits" if spirit else "players"] += 1
            before = k.record.skill_points
            if k.record.gain_xp(xp):
                self.say(f"   {k} reaches level {k.record.level}!")
                self.tell(k, f"+{k.record.skill_points - before} skill points ({k.record.skill_points} to spend: /skills).")
        if pts:
            self.say(f"   {k} scores {pts} points (+{xp} XP).")

    # ---- domains -----------------------------------------------------------------------
    def domains(self) -> list:
        return [d for d in (self.domain, self.rival) if d is not None]

    def domain_of(self, c: Combatant) -> Optional[Domain]:
        return next((d for d in self.domains() if d.owner == c.cid), None)

    def sure_hit_owner(self) -> Optional[str]:
        """Whose sure-hit is in force. Nobody's while two domains are locked in a clash."""
        return self.domain.owner if self.domain is not None and self.rival is None else None

    def trapped(self, c: Combatant) -> bool:
        """Inside a hostile barrier. An open (barrierless) domain leaves a way out."""
        return "hr_zero" not in c.flags and any(self._holds(d, c) for d in self.domains())

    def _holds(self, d: Domain, c: Combatant) -> bool:
        """Does this domain's barrier keep ``c`` in? An open domain has none; a shell hardened on
        the outside is soft on the inside; a miniature barrier closes around one enemy only."""
        if d.data.get("open") or not self.hostile(c, self.by_cid[d.owner]):
            return False
        shell = d.data.get("shell", "normal")
        return shell == "normal" or (shell == "miniature" and d.data.get("only") == c.root.cid)

    def inside(self, owner: Combatant) -> list:
        """Everyone on the field a domain could reach, besides its owner: friend and foe alike."""
        return [o for o in self.fighters if o.alive and not o.fled and o is not owner and "remote" not in o.flags]

    def domain_reaches(self, d: Domain, c: Combatant) -> bool:
        """Is ``c`` someone this domain's sure-hit is aimed at (before any defence of theirs)?

        Every domain targets in its own way (``d.data``, set from the action's params in data.py):
          scope "enemies"  only those hostile to the owner (the default)
          scope "all"      everything inside but the owner and what is the owner's own (their
                           shikigami): allies are hit too - Malevolent Shrine, Unlimited Void...
          scope "none"     no sure-hit at all (an incomplete domain)
          spared           root ids the owner keeps out of it (Unlimited Void: whoever Gojo is touching)
          only             the one root id it closes on (a miniature barrier; a single defendant, a single
                           coffin, the one person a copied technique is turned on)
        Those with no cursed energy at all are outside every sure-hit."""
        owner = self.by_cid[d.owner]
        if not c.alive or c.fled or c is owner or "remote" in c.flags or "hr_zero" in c.root.flags:
            return False
        only = d.data.get("only")
        if only is not None and c.root.cid != only:
            return False
        if c.root.cid in d.data.get("spared", ()):
            return False
        scope = d.data.get("scope", "enemies")
        if scope == "none":
            return False
        if scope == "all":
            return c.root is not owner.root
        return self.hostile(owner, c)

    def domain_targets(self, owner: Combatant) -> list:
        """Who the sure-hit lands on this round: everyone the domain reaches (``domain_reaches``),
        except those under Domain Amplification and those behind an anti-domain technique (which
        it erodes)."""
        if self.rival is not None:
            return []                                    # clashing domains cancel each other's sure-hit
        mine = self.domain_of(owner)
        if mine is None:
            return []
        out = []
        for e in self.fighters:
            if not self.domain_reaches(mine, e):
                continue
            if e.has(ST.AMPLIFY):
                self.say(f"   {e}'s Domain Amplification neutralises the sure-hit.")
            elif e.has(ST.ANTI_DOMAIN):
                self.st_dur[e.idx, ST.ANTI_DOMAIN] -= 1  # held, but the domain grinds it down
                left = int(self.st_dur[e.idx, ST.ANTI_DOMAIN])
                self.say(f"   {e}'s {e.meta.get('anti', 'anti-domain technique')} neutralises the sure-hit"
                         + (" and is worn away." if left <= 0 else f" ({left} round(s) of it left)."))
            else:
                out.append(e)
        return out

    def shred_field(self, by: Combatant, power: float, what: str = "is cut to pieces") -> None:
        """A domain that spares nothing: every battlefield object inside takes the hit too."""
        for obj in list(self.field.values()):
            obj.hp -= power * 2
            if obj.hp <= 0:
                self.say(f"   The {obj.name} {what}.")
                self._break_object(obj, by)

    def _refinement(self, d: Domain) -> float:
        owner = self.by_cid[d.owner]
        r = owner.stat(S.OUT) * (1 + owner.level / 20) * self.rng.uniform(0.9, 1.1) * skills.refinement(owner)
        return r * (1.0 if d.data.get("lethal", True) else NONLETHAL_CLASH)

    def _clash_power(self, d: Domain, other: Domain) -> float:
        """How hard ``d`` presses on ``other``: refinement, and what each has done with its barrier.

        normal shell      strong inside, weak outside: an open domain reaches round it (OPEN_EDGE)
        reinforced shell  the conditions swapped - nothing gets at it from outside, but it is soft
                          inside, so it gives ground to another closed barrier (INSIDE_WEAK)
        miniature         reinforced, and shrunk to the size of a ball: MINI_DOMAIN harder to break
        """
        r = self._refinement(d)
        mine, theirs = d.data.get("shell", "normal"), other.data.get("shell", "normal")
        if d.data.get("open") and not other.data.get("open") and theirs == "normal":
            r *= OPEN_EDGE
        if mine != "normal" and not d.data.get("open") and not other.data.get("open"):
            r *= INSIDE_WEAK
        if mine == "miniature":
            r *= MINI_DOMAIN
        return r

    def _burn_out(self, c: Combatant, quiet: bool = False) -> None:
        if not quiet:
            self.say(f"   {c}'s technique is burnt out.")
        self.add_status(c, ST.SEALED, 1.0, 2)
        c.meta["burnt"] = True
        if c.pending is not None:
            c.pending.loosed = True                      # what was already gathered and let go still arrives

    def _shell_failed(self, d: Domain) -> None:
        """Remember that this way of building the barrier did not win (NPCs learn from it)."""
        owner = self.by_cid[d.owner]
        tried = owner.meta.setdefault("shell_failed", [])
        if d.data.get("shell", "normal") not in tried:
            tried.append(d.data.get("shell", "normal"))

    def open_domain(self, c: Combatant, key: str, name: str, rounds: int, tick: Optional[str] = None,
                    data: Optional[dict] = None, lethal: bool = True, open_barrier: bool = False,
                    shell: str = "normal") -> bool:
        """Expand a domain. Returns False if it failed to take hold.

        One domain: it simply opens.  A second, hostile one: a clash - whichever is more refined
        by CLASH_MARGIN crushes the other at once, otherwise both stand locked together with
        their sure-hits cancelled until one gives (see ``_clash``).  A third: every barrier fails.
        """
        existing = self.domains()
        if any(not self.hostile(c, self.by_cid[d.owner]) for d in existing):
            self.say(f"{c} cannot expand a domain inside their own side's.")
            return False
        new = Domain(c.cid, key, name, rounds, tick, {**(data or {}), "lethal": lethal, "open": open_barrier,
                                                      "shell": "normal" if open_barrier else shell})
        self.say(f"\n>>> DOMAIN EXPANSION: {name.upper()} <<<  ({c})")
        if c.meta.pop("last_domain", False):
            c.meta["brain_spent"] = True                 # the healed brain will not bear another after this one
        if new.data["shell"] == "reinforced":
            self.say(f"   {c} has swapped the barrier's conditions: hard as stone from outside, soft within. "
                     f"Nothing breaks in; anyone inside can break out.")
        elif new.data["shell"] == "miniature":
            foes = [e for e in self.enemies(c) if e.owner is None] or self.enemies(c)
            rival = [self.by_cid[d.owner] for d in existing if self.hostile(c, self.by_cid[d.owner])]
            one = rival[0] if rival else max(foes, key=lambda e: (e.level, e.hp), default=None)
            new.data["only"] = one.cid if one is not None else None
            self.say(f"   {c} shrinks the barrier to the size of a ball, its conditions swapped: almost nothing can "
                     f"break it, and it closes around {one if one is not None else 'no one'} alone.")
        if not existing:
            self.domain = new
            self._answer_domain(new)
            return new in self.domains()
        if len(existing) == 2:
            self.say("Three domains grind against one another and no barrier can bear it: all of them collapse.")
            for d in existing:
                self.close_domain(d)
            if not new.data.get("no_burnout"):
                self._burn_out(c, quiet=True)
            return False
        old = existing[0]
        self.say(f"DOMAIN CLASH: {name} against {old.name}.")
        c.meta["clashed"] = self.by_cid[old.owner].meta["clashed"] = self.round
        mine, theirs = self._clash_power(new, old), self._clash_power(old, new)
        if mine >= CLASH_MARGIN * theirs:
            self.say(f"   {name} is far the stronger. {old.name} is crushed at once.")
            self._shell_failed(old)
            self.close_domain(old)
            self.domain = new
            return True
        if theirs >= CLASH_MARGIN * mine:
            if old.data.get("open") and new.data["shell"] == "normal" and not open_barrier:
                self.say(f"   {old.name} has no barrier and reaches right round {name}'s, tearing the shell "
                         f"apart from outside, where it is weakest. {name} never takes hold.")
            else:
                self.say(f"   {old.name} is far the stronger. {name} never takes hold.")
            self._shell_failed(new)
            if not new.data.get("no_burnout"):
                self._burn_out(c)
            return False
        self.rival = new
        self.say("   Neither gives way. While the two domains press against each other, both sure-hits are cancelled.")
        return True

    def _answer_domain(self, new: Domain) -> None:
        """The surest answer to a domain is your own, expanded the instant theirs opens: the two
        clash from the first moment, before either sure-hit lands. It takes a domain of your own,
        the cursed energy for it and a reaction; someone in the middle of their own technique
        must also be perceptive enough (REACT_PER) to drop it in time."""
        opener = self.by_cid[new.owner]
        if self.phase != "resolve":
            return                                       # (only inside a round; staged scenes place domains by hand)
        for c in sorted(self.enemies(opener), key=lambda x: -x.stat(S.SPD)):
            if new not in self.domains() or self.rival is not None or not opener.alive:
                return
            if c.owner is not None or c.reactions <= 0 or c.has(ST.STUN) or self.domain_of(c):
                continue
            if c.pending is not None and c.stat(S.PER) < REACT_PER:
                continue
            opts = [a for a in self.actions_for(c) if a.kind == Kind.DOMAIN and self.why_cant(c, a) is None]
            if not opts:
                continue
            if c.controller == "human":
                k = self.ask(c, f"{opener} expands {new.name}. Expand your own domain against it, now?"
                                + (f" (You would abandon {c.pending.act.name}.)" if c.pending else ""),
                             [f"{a.name} ({self.costs(c, a)[0]} CE)" for a in opts] + ["No"])
                act = opts[k] if k < len(opts) else None
            else:
                act = ai.answer_domain(self, c, new, opts)
            if act is None:
                continue
            c.reactions -= 1
            if c.pending is not None:
                self.say(f"{c} lets {c.pending.act.name} go and answers with a domain of their own.")
            else:
                self.say(f"{c} answers at once with a domain of their own.")
            ce, sta = self.costs(c, act)
            self.spend_ce(c, ce)
            c.sta -= sta
            self.part_ce[c.idx] = 0
            c.pending = Pending(act, [opener.cid] if act.target == Target.ENEMY else [], Part.TORSO,
                                CHANNEL_AMP if act.channel else 1.0, 0, None, land_at=self.time)
            self._release(c)

    def _clash(self) -> None:
        """Each round two locked domains are measured again; the edge needed to win shrinks."""
        a, b = self.domain, self.rival
        b.data["clash"] = n = b.data.get("clash", 0) + 1
        need = max(1.05, CLASH_MARGIN - 0.07 * n)
        ra, rb = self._clash_power(a, b), self._clash_power(b, a)
        if ra < need * rb and rb < need * ra:
            self.say(f"The domains {a.name} and {b.name} are still locked together.")
            return
        winner, loser = (a, b) if ra >= rb else (b, a)
        self.say(f"The clash breaks: {winner.name} overwhelms {loser.name}.")
        self._shell_failed(loser)
        self.close_domain(loser)

    def close_domain(self, d: Optional[Domain] = None, burnout: bool = True) -> None:
        d = d if d is not None else self.domain
        if d is None or d not in self.domains():
            return
        if d is self.domain:
            self.domain, self.rival = self.rival, None
        else:
            self.rival = None
        owner = self.by_cid[d.owner]
        self.say(f"The domain {d.name} collapses.")
        if burnout and owner.alive and not d.data.get("no_burnout"):
            self._burn_out(owner)

    # ---- round structure ---------------------------------------------------------------
    def upkeep(self) -> None:
        from . import effects
        n = self.n
        al = self.alive[:n]
        st = self.stats[:n]
        jackpot = (self.st_dur[:n, ST.JACKPOT] > 0) & al
        fed = {s.owner for s in self.fighters if s.alive and s.owner is not None and "ce_fed" in s.base_traits}
        held = {cid: float(st[self.by_cid[cid].idx, S.CE]) for cid in fed}
        back = st[:, S.MAX_CE] * st[:, S.CE_REGEN] / 100.0      # a share of the maximum, every round
        st[:, S.CE] = np.where(al, np.minimum(st[:, S.MAX_CE], st[:, S.CE] + back), st[:, S.CE])
        for cid, ce in held.items():                     # a shikigami that lives on its user's cursed energy takes
            st[self.by_cid[cid].idx, S.CE] = ce          # what would have come back, for as long as it is out
        st[:, S.STA] = np.where(al, np.minimum(st[:, S.MAX_STA], st[:, S.STA] + st[:, S.STA_REGEN]), st[:, S.STA])
        st[jackpot, S.CE] = st[jackpot, S.MAX_CE]
        bud = np.where((self.st_dur[:n, ST.BUD] > 0) & al, self.st_mag[:n, ST.BUD], 0.0)
        st[:, S.CE] = np.maximum(st[:, S.CE] - bud, 0.0)     # Cursed Bud feeds
        dots = list(DOT_STATUSES)
        dot = (np.where(self.st_dur[:n][:, dots] > 0, self.st_mag[:n][:, dots], 0.0).sum(axis=1)) * al
        st[:, S.HP] -= dot
        for s in dots:                                   # it also eats at the limb it sits in (never the last of it)
            rows = np.flatnonzero((self.st_dur[:n, s] > 0) & (self.st_part[:n, s] >= 0) & al)
            parts = self.st_part[rows, s]
            self.part_hp[rows, parts] = np.maximum(np.minimum(self.part_hp[rows, parts], 1.0),
                                                   self.part_hp[rows, parts] - self.st_mag[rows, s])
        for i in np.flatnonzero(dot > 0):
            self.say(f"{self.fighters[i]} suffers {dot[i]:.0f} damage from "
                     + "/".join(Status(s).name.lower() for s in dots if self.st_dur[i, s] > 0) + ".")
        before = self.st_dur[:n].copy()
        ticking = np.ones(N_STATUS, dtype=bool)
        ticking[list(STICKY)] = False
        self.st_dur[:n][:, ticking] = np.maximum(self.st_dur[:n][:, ticking] - 1, 0)
        self.st_mag[:n][self.st_dur[:n] == 0] = 0
        self.st_part[:n][self.st_dur[:n] == 0] = -1
        self.part_stun[:n] = np.maximum(self.part_stun[:n] - 1, 0)
        woke = (self.part_state[:n] == PState.STUNNED) & (self.part_stun[:n] == 0)
        self.part_state[:n][woke] = PState.OK
        self.part_rf[:n] *= 0.5
        for i in np.flatnonzero(al & (st[:, S.HP] <= 0)):
            c = self.fighters[i]
            self.kill(c, self.by_cid.get(c.last_hit_by))
        for i, s in zip(*np.nonzero((before > 0) & (self.st_dur[:n] == 0))):
            if self.alive[i]:
                effects.fire(self, "on_status_end", self.fighters[i], Status(s))
        for c in list(self.fighters):
            if c.alive:
                c.reactions = 1 + (c.stat(S.SPD) >= 18)
                effects.fire(self, "on_upkeep", c)
        if self.rival is not None:
            self._clash()
        locked = self.rival is not None
        for d in self.domains():                         # d.rounds = ticks still to come
            if d not in self.domains():
                continue
            if d.rounds <= 0:
                if locked:                               # it ran out still locked: that shell did not win
                    self._shell_failed(d)
                self.close_domain(d)
                continue
            d.rounds -= 1
            if not d.tick:
                continue
            if self.rival is not None and d.data.get("lethal", True):
                self.say(f"{d.name}: its sure-hit is cancelled by the clash.")
            else:                                        # a harmless domain's rules still run mid-clash
                effects.EFFECTS[d.tick](self, self.by_cid[d.owner], d)

    # ---- a round ------------------------------------------------------------------------
    # 1. upkeep   2. everyone who is free commits ONE choice: an action, or a defence
    # 3. what was committed resolves in the order worked out by ``timing`` - player speed for
    #    blows, technique speed for techniques, activation for both. Nothing is prompted in
    #    between, except a defence for the few perceptive enough to defend while attacking.
    def _plan(self, c: Combatant) -> None:
        """Ask one fighter for this round's choice."""
        c.plan = None
        c.guard = c.guard_arg = None
        c.free_used = False
        if c.pending is not None:                        # still bringing last round's technique to bear
            c.plan = "attack"
            return
        if c.has(ST.STUN):
            self.st_dur[c.idx, ST.STUN] -= 1
            c.meta["stunned_in"] = self.round            # ...the whole round: no answering what lands in it either
            self.say(f"{c} is stunned and loses the round.")
            return
        if "remote" in c.flags:                          # commanding from somewhere else
            idle = "hr_max" not in c.flags or self.why_cant(c, ACTIONS["deploy_puppet"]) is not None
            if not self.active(c) or (idle and (c.controller != "human"
                                                or any(p.controller == "human" for p in self.summons(c)))):
                return
        self.io.turn(self, c)

    def _resolve_round(self) -> None:
        """Land everything due this round, soonest first; ties go to the faster fighter."""
        end = float(self.round)
        while not self.over:
            due = [c for c in self.fighters if c.alive and not c.fled and c.pending is not None
                   and c.pending.land_at < end]
            if not due:
                break
            c = min(due, key=lambda x: (x.pending.land_at, -x.stat(S.SPD), x.idx))
            self.time = max(self.time, c.pending.land_at)
            self._release(c)
            self.check_over()

    def play_round(self) -> None:
        self.round += 1
        self.time = float(self.round - 1)
        self.say(f"\n===== Round {self.round} =====")
        self.upkeep()
        if not self.check_over():
            order = sorted((c for c in self.fighters if c.alive and not c.fled), key=lambda x: -x.stat(S.SPD))
            self.phase = "channel"                       # 1. everyone gathers cursed energy where they mean to use it
            for c in order:
                c.charge, c.charged = 0.0, []
                c.meta.pop("intent_name", None)
                busy = c.pending is not None or c.has(ST.STUN) or "remote" in c.flags
                if c.alive and not busy and (c.max_ce > 0 or c.borrows_ce):
                    self.part_ce[c.idx] = 0
                    self.io.channel(self, c)
            self._reveal()                               #    ...and the perceptive read it
            self.phase = "commit"                        # 2. everyone commits an action or a defence
            for c in order:
                if c.alive and not c.fled and not self.over:
                    self._plan(c)
                    self.check_over()
            self._settle_charge()
            self.phase = "resolve"
            self._resolve_round()                        # 3. it all lands in stat order
            self.phase = None
            if not self.over:
                self._stalemates()
        if self.cache is not None:
            self.cache.save(self)

    def take_turn(self, c: Combatant) -> None:
        """Bring one fighter forward: land what they have committed, or let them commit something.
        (The engine itself runs on ``play_round``; this is for tests and scripted scenes.)"""
        if c.pending is not None:
            self.time = max(self.time, c.pending.land_at)
            self._release(c)
        elif c.alive and not c.fled:
            self._plan(c)
        self.check_over()

    def check_over(self) -> bool:
        if self.over:
            return True
        act = [c for c in self.fighters if self.active(c)]
        humans = [c for c in self.fighters if c.kind == "fighter" and c.controller == "human"]
        if humans and not any(self.active(h) for h in humans):
            self.over = True                             # no player left in it: the rest disperse
            return True
        if any(self.hostile(a, b) for a, b in itertools.combinations(act, 2)):
            return False
        self.over = True
        return True

    def _leave(self, c: Combatant, text: str) -> None:
        c.fled = True
        c.pending = None
        self.part_ce[c.idx] = 0
        self.say(text)
        for s in self.summons(c):
            self.unsummon(s)
        if self.domain_of(c):
            self.close_domain(self.domain_of(c), burnout=False)

    def _stalemates(self) -> None:
        """NPCs that cannot make headway give up. This is what ends fights nobody can win:
        an NPC must push its enemies to a new low within STALEMATE_ROUNDS or it withdraws."""
        for c in list(self.fighters):
            if self.over or not c.alive or c.fled or c.owner or c.controller == "human" or c.has(ST.AMBER):
                continue                                 # (nobody who has spent their life on Amber walks away)
            foes = self.enemies(c)
            if not foes:
                continue
            if self.rival is not None or self.round - c.meta.get("clashed", -99) <= 3:
                continue                                 # a battle of domains is not a stalemate while it lasts
            # Headway = the enemy principals (not their summons, which come and go) pushed to a
            # new low, or something of theirs destroyed this round.
            main = [f for f in foes if f.owner is None] or foes
            score = sum(0.5 + max(f.hp, 0.0) / max(f.meta.get("base_max_hp", f.max_hp), 1.0) for f in main)
            if score < c.meta.get("stall_best", float("inf")) - 0.001:
                c.meta["stall_best"], c.meta["stall"], c.meta["stall_main"] = score, 0, 0
                continue
            c.meta["stall_main"] = c.meta.get("stall_main", 0) + 1
            c.meta["stall"] = 0 if self._last_kill.get(c.cid) == self.round else c.meta.get("stall", 0) + 1
            if c.meta["stall"] < STALEMATE_ROUNDS and c.meta["stall_main"] < 3 * STALEMATE_ROUNDS:
                continue                                 # (clearing summons only buys so much time)
            if self.trapped(c):
                continue                                 # sealed in; it leaves when the barrier drops
            self._leave(c, f"{c} sees no way to finish this and withdraws.")
            self.check_over()

    def run(self) -> dict:
        """Play until one side is left. There is no round limit: NPCs that are getting nowhere
        withdraw (see ``_stalemates``), and human players decide for themselves."""
        while not self.over:
            self.play_round()
        return self.finish()

    def condition_of(self, c: Combatant) -> dict:
        """A survivor's injuries, as fractions, for the player record."""
        i = c.idx
        mx = max(float(self.stats[i, S.MAX_HP]), 1.0)
        base = max(c.meta.get("base_max_hp", mx), mx)
        gone = [int(self.part_state[i, p] == PState.DESTROYED) for p in range(6)]
        parts = [0.0 if g else float(np.clip(self.part_hp[i, p] / max(self.part_max[i, p], 1e-9), 0.0, 1.0))
                 for p, g in zip(range(6), gone)]
        return {"hp": float(np.clip(self.stats[i, S.HP] / mx, 0.0, 1.0)), "parts": parts, "gone": gone,
                "scar": float(1 - mx / base)}

    def finish(self) -> dict:
        self.over = True
        for c in self.fighters:                          # the price of Mythical Beast Amber
            if c.alive and c.has(ST.AMBER):
                self.say(f"\nThe fight is over, and so is {c}: the body Mythical Beast Amber remade "
                         f"crumbles to nothing.")
                self.alive[c.idx] = False
                self.stats[c.idx, S.HP] = 0
        from . import effects
        for c in list(self.fighters):
            effects.fire(self, "on_finish", c)
        for c in self.fighters:
            if c.record:                                 # write battle results back to the record
                c.record.alive = c.alive
                c.record.techniques = c.innate
                if c.alive:                              # wounds are kept; nothing resets
                    mx = float(self.stats[c.idx, S.MAX_CE])
                    c.record.ce_frac = float(np.clip(self.stats[c.idx, S.CE] / mx, 0.0, 1.0)) if mx > 0 else 1.0
                    c.record.ce_ts = float(self.now)     # cursed energy is as it was left, and returns with time
                    c.record.condition = self.condition_of(c)
                    if not c.record.injured:
                        c.record.condition = None
        winners = [c for c in self.fighters if self.active(c) and c.kind == "fighter"]
        self.say("\n===== Battle over =====")
        for c in self.fighters:
            if c.kind == "fighter":
                state = "fled" if c.fled else "alive" if c.alive else "dead"
                self.say(f"  {c.name:<28} {state:<6} +{c.points_gained} pts  +{c.xp_gained} XP")
        if self.cache is not None:
            self.cache.delete(self.server_id, self.id)
        return {"rounds": self.round, "winners": [c.name for c in winners],
                "dead": [c.name for c in self.fighters if c.kind == "fighter" and not c.alive]}

    # ---- non-technique commands --------------------------------------------------------
    def move(self, c: Combatant, fid: Optional[str]) -> bool:
        if "remote" in c.flags:
            self.tell(c, "Your body is in the hideout.")
            return False
        if fid is not None and fid not in self.field:
            self.tell(c, "No such object here.")
            return False
        if not any(c.usable(p) for p in LEGS) and "flight" not in c.traits:
            self.tell(c, "You can't move without a working leg.")
            return False
        c.pos = fid
        if c.has(ST.ANTI_DOMAIN) and not c.meta.get("anti_hands"):
            self.clear_status(c, ST.ANTI_DOMAIN)         # a simple domain is a circle you stand in
            self.say(f"{c} steps out of their Simple Domain; it fades.")
        obj = self.field.get(fid)
        self.say(f"{c} moves to {'open ground' if obj is None else obj.name}"
                 + (f" ({obj.role})." if obj else "."))
        return True

    def throw(self, c: Combatant, fid: str, target: Combatant, part: Part = Part.TORSO) -> bool:
        obj = self.field.get(fid)
        if not obj or obj.role != "throwable":
            self.tell(c, "That can't be thrown.")
            return False
        why = self.why_cant(c, THROW)
        if why or c.stat(S.STR) < obj.weight:
            self.tell(c, why or f"Too heavy - needs {obj.weight:.0f} strength.")
            return False
        if not (target and target.alive and self.hostile(c, target) and "remote" not in target.flags):
            self.tell(c, "Pick a living enemy.")
            return False
        c.sta -= THROW.sta
        self.say(f"{c} hurls the {obj.name}!" + (" It hums with cursed energy." if obj.imbued else ""))
        self._break_object(obj, c)
        self.strike(c, target, THROW, part, power=obj.power * (1.3 if obj.imbued else 1.0), label=obj.name,
                    plain=not obj.imbued and not self.carries_ce(c, THROW))
        return True

    def imbue(self, c: Combatant, fid: str, ce: float = 5.0) -> bool:
        """Free action: pour cursed energy into a field object."""
        obj = self.field.get(fid)
        if obj is None:
            self.tell(c, "No such object here.")
            return False
        if c.free_used or c.max_ce <= 0 or c.ce < ce or c.has(ST.CE_SEALED) or "remote" in c.flags:
            self.tell(c, "You can't imbue anything right now.")
            return False
        c.free_used = True
        c.ce -= ce
        obj.imbued += ce
        self.say(f"{c} pours cursed energy into the {obj.name}.")
        return True

    def dismiss(self, c: Combatant, s: Optional[Combatant]) -> bool:
        """Free: call one of your own shikigami or released spirits back. It is not destroyed, so
        it can be sent out again - the way to rotate shikigami, or to save a badly hurt one."""
        if (s is None or not s.alive or s.owner != c.cid or s.kind not in ("shikigami", "spirit")
                or s.meta.get("ritual_owner")):
            self.tell(c, "You can only dismiss your own shikigami or released spirits.")
            return False
        self.say(f"{c} calls {s.name} back.")
        self.unsummon(s)
        return True

    def release_domain(self, c: Combatant) -> bool:
        """Free: let your own domain go before it runs out (the usual burnout applies)."""
        d = self.domain_of(c)
        if d is None:
            self.tell(c, "You have no domain open.")
            return False
        self.say(f"{c} lets the domain go.")
        self.close_domain(d)
        return True

    def stance(self, c: Combatant) -> Optional[str]:
        """The one answer-to-a-domain this fighter is holding, if any."""
        if c.has(ST.AMPLIFY):
            return "Domain Amplification"
        if c.has(ST.FBE):
            return "Falling Blossom Emotion"
        return c.meta.get("anti", "Simple Domain") if c.has(ST.ANTI_DOMAIN) else None

    def drop_stance(self, c: Combatant, why: str = "lets it go") -> bool:
        """Simple Domain, Hollow Wicker Basket, Falling Blossom Emotion and Domain Amplification
        cannot be held together: raising one drops whichever was up. Also the `drop` command."""
        held = self.stance(c)
        if held is None:
            return False
        for st in (ST.ANTI_DOMAIN, ST.FBE, ST.AMPLIFY):
            self.clear_status(c, st)
        self.say(f"{c}'s {held}: {c} {why}.")
        return True

    def boost(self, c: Combatant, ce: float) -> bool:
        """Free action: burn cursed energy for stamina, strength and speed."""
        if c.free_used or ce <= 0 or c.ce < ce or c.has(ST.CE_SEALED):
            self.tell(c, "You can't convert cursed energy right now.")
            return False
        c.free_used = True
        c.ce -= ce
        c.sta = min(c.base(S.MAX_STA), c.sta + ce)
        self.add_status(c, ST.BOOST, 1.0, 2, ce / 6)
        self.say(f"{c} burns {ce:.0f} cursed energy into the body (+{ce / 6:.1f} STR/SPD).")
        return True

    def equip(self, c: Combatant, key: str) -> bool:
        item = ITEMS.get(key)
        rika_tools = c.tech_state.get("copy", {}).get("tools", []) if c.has(ST.RIKA_LINK) else []
        home = c.record is not None and self.node is not None and c.record.hideout == self.node
        if item is not None and (item.mundane or "inventory_curse" in c.inventory):
            home = True                                  # anyone can pick up a bat anywhere; the Inventory
                                                         # Curse hands over any tool it holds, mid-fight
        if key not in rika_tools and not home:           # Rika's vault is the one exception
            self.tell(c, "Cursed tools can only be changed in your hideout.")
            return False
        if not item or item.slot in ("object", "supply") or (key not in c.inventory and key not in rika_tools):
            self.tell(c, "You don't have that to equip.")
            return False
        if item.slot == "weapon" and c.vow_flags & {"no_tool_swap", "no_tools"}:
            self.tell(c, "A binding vow forbids changing cursed tools.")
            return False
        old = c.equipment.get(item.slot)
        if old:
            c.inventory.append(old)
        if key in c.inventory:
            c.inventory.remove(key)
        c.equipment[item.slot] = key
        self.say(f"{c} equips {item.name}.")
        return True

    def use_item(self, c: Combatant, key: str) -> bool:
        item = ITEMS.get(key)
        """Consume a cursed object, or use up an ordinary supply."""
        if not item or item.slot not in ("object", "supply") or key not in c.inventory:
            self.tell(c, "You don't have that to use.")
            return False
        if "kept" in item.flags:
            self.tell(c, f"The {item.name} is not consumed. It works while you carry it.")
            return False
        if item.slot == "supply":
            c.inventory.remove(key)
            self.say(f"{c} uses {item.name}.")
            for st in (ST.BLEED,):
                self.clear_status(c, st)
            self.heal(c, item.params.get("heal", 0))
            return True
        if c.max_ce <= 0:
            self.tell(c, "Without cursed energy of your own, it does nothing for you.")
            return False
        c.inventory.remove(key)
        if key == "sukuna_finger":
            from . import effects
            effects.eat_finger(self, c)
            return True
        self.say(f"{c} consumes {item.name}.")
        c.ce = min(c.max_ce, c.ce + item.params.get("ce", 0))
        return True

    def flee(self, c: Combatant) -> bool:
        if self.trapped(c):
            self.say(f"{c} cannot escape the domain's barrier.")
            return True
        foes = self.enemies(c)
        fastest = max((e.stat(S.SPD) for e in foes), default=0)
        if self.rng.random() < np.clip(0.35 + 0.03 * (c.stat(S.SPD) - fastest), 0.1, 0.9):
            self._leave(c, f"{c} escapes the fight.")
        else:
            self.say(f"{c} fails to get away.")
        return True
