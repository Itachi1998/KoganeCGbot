"""Behaviour for techniques.  Data in data.py names these handlers by string.

Registries
    EFFECTS   name -> fn(b, c, act, targets, part, amp, arg)      what an action does
              (domain ticks use the same registry with fn(b, owner, domain))
    CHOICES   name -> fn(b, c) -> [(key, label)]                   options for CHOICE actions
    VALID     name -> fn(b, c, act, target, arg) -> error | None   checked before paying
    CONDS     name -> fn(b, c) -> error | None                     availability conditions
    REACT_FX  name -> fn(b, c)                                      side effects of a reaction
    HOOKS     event -> [fn(b, c, *args)]                            passives
"""
from __future__ import annotations

import copy
from collections import defaultdict

import numpy as np

from .constants import (BRAIN_HEALS, SLASH_ROUNDS, CE_RECOVERY, SIX_EYES_EFF, SIX_EYES_RECOVERY, SUKUNA_EFF, FINGER_AMP, FINGER_CE, SUKUNA_CE_BASE, SUKUNA_CE_FINGER, SUKUNA_LEVEL, TIER_POWER, FRAME_STACKS, FRAME_STEP, UNSEEN_PER, DUR_FACTOR, EFF_CAP, PART_HP_FRAC, Rng, Target, ADVANCED_LEVEL, BRAIN_SLOTS, EXTRA, LIMBS, N_STATS, UZUMAKI_EXTRACT_MIN_GRADE,
                        DType, Grade, GRADE_NAME, Kind, Part, PClass, PState, Stat, Status)
from .crimes import CRIME_INFO, FABRICATED
from .data import JOKES, MERGE_NAMES, SHIKI_ORDER, SHIKIGAMI
from .records import Spec, build_stats, npc_spirit, sukuna_share
from .techniques import ACTION_TECH, ACTIONS, TECHNIQUES

S, ST = Stat, Status
EFFECTS, CHOICES, VALID, CONDS, REACT_FX = {}, {}, {}, {}, {}
QUICK = {}        # name -> fn(b, c) -> bool: a channelled action that resolves at once right now
AI_PICK = {}      # name -> fn(b, c) -> (target, part, arg) | None, for Target.FREE actions
HOOKS = defaultdict(list)


def _reg(table, name):
    def deco(fn):
        table[name] = fn
        return fn
    return deco


def effect(name): return _reg(EFFECTS, name)
def choices(name): return _reg(CHOICES, name)
def valid(name): return _reg(VALID, name)
def cond(name): return _reg(CONDS, name)
def react_fx(name): return _reg(REACT_FX, name)


def hook(event):
    def deco(fn):
        HOOKS[event].append(fn)
        return fn
    return deco


def fire(b, event, c, *args):
    for fn in HOOKS[event]:
        fn(b, c, *args)


def summon_spec(name, kind, level, *, hp, ce=40, sta=60, str_=10, spd=10, dur=8, per=8, out=10,
                actions=(), traits=(), meta=None, controller="ai", grade=Grade.G2) -> Spec:
    s = np.zeros(N_STATS)
    s[[S.MAX_HP, S.HP]] = hp
    s[[S.MAX_CE, S.CE]] = ce
    s[[S.MAX_STA, S.STA]] = sta
    s[S.STR], s[S.SPD], s[S.DUR], s[S.PER], s[S.OUT] = str_, spd, dur, per, out
    s[S.CE_REGEN], s[S.STA_REGEN] = CE_RECOVERY, 6
    return Spec(name=name, pclass=PClass.SORCERER, level=level, grade=grade, stats=s, techniques=[],
                extra_actions=list(actions), traits=set(traits), kind=kind, meta=meta or {},
                controller=controller)


# ======================================================================================
# Generic
# ======================================================================================
@cond("has_weapon")
def _has_weapon(b, c):
    if not c.weapon:
        return "no weapon in hand"
    return "a gun is for `shoot`" if "ranged" in c.weapon.flags else None


@cond("has_gun")
def _has_gun(b, c):
    w = c.weapon
    if not w or "ranged" not in w.flags:
        return "no gun in hand"
    return None if c.meta.setdefault("ammo", w.params.get("ammo", 0)) > 0 else "out of ammunition"


@cond("plain_weapon")
def _plain_weapon(b, c):
    w = c.weapon
    if not w or "ranged" in w.flags:
        return "no ordinary melee weapon in hand"
    return None if w.mundane else "your cursed tool already carries cursed energy"


@cond("not_spirit")
def _not_spirit(b, c):
    return "cursed spirits cannot produce positive energy" if c.pclass == PClass.CURSED_SPIRIT else None


@effect("weapon_strike")
def weapon_strike(b, c, act, targets, part, amp, arg):
    w = c.weapon
    ramp = w.params.get("ramp", 0)
    power = act.power + w.power + 0.5 * w.params.get("str_scale", 0) * c.stat(S.STR) + c.meta.get("ramp", 0)
    cancel = "disrupt" in w.flags
    if "ranged" in w.flags:
        c.meta["ammo"] = c.meta.get("ammo", w.params.get("ammo", 0)) - 1
    plain = w.mundane and not b.carries_ce(c, act)      # an ordinary weapon, and nothing poured into it
    for t in targets:
        d = b.strike(c, t, act, part, amp * c.mult["tool"], power=power, dtype=w.dtype,
                     extra_tags=w.tags, label=w.name + (" (infused)" if w.mundane and not plain else ""),
                     nullify="nullify" in w.flags, plain=plain)
        if d > 0 and t.alive and w.params.get("stun"):
            b.add_status(t, ST.STUN, w.params["stun"], 1)
        if d > 0 and ramp:                              # Dragon-Bone keeps what it is hit with
            c.meta["ramp"] = min(12, c.meta.get("ramp", 0) + ramp)
        if d > 0 and cancel and t.alive and t.pending:
            b.say(f"   {w.name} disperses the cursed energy {t} was channelling.")
            t.pending = None
            b.part_ce[t.idx] = 0


@effect("heal")
def heal(b, c, act, targets, part, amp, arg):
    b.say(f"{c} uses {act.name}.")
    base = c.meta.get("base_max_hp", c.max_hp)
    if act.params.get("scar") and base > c.max_hp + 0.5:     # a soul manipulator can smooth its own soul
        b.stats[c.idx, S.MAX_HP] = base
        b.part_max[c.idx, :6] = base * PART_HP_FRAC[:6]
        b.say(f"   {c} smooths the scars out of its own soul.")
    b.heal(c, act.params.get("frac", 0.3) * c.max_hp, act.params.get("limbs", 0))


@valid("heal_other")
def _heal_other_valid(b, c, act, t, arg):
    if t is None or t is c or not t.alive or t.team != c.team:
        return "Pick a living ally."
    if t.pclass == PClass.CURSED_SPIRIT or t.kind == "puppet":
        return "Reverse cursed energy can't mend that."
    return None


@effect("heal_other")
def heal_other(b, c, act, targets, part, amp, arg):
    t = targets[0]
    b.say(f"{c} pours reverse cursed energy into {t}.")
    b.heal(t, act.params["frac"] * t.max_hp, act.params.get("limbs", 0))


@effect("aura_heal")
def aura_heal(b, c, act, targets, part, amp, arg):
    team = [o for o in b.fighters if o.alive and o.team == c.team]
    t = min(team, key=lambda o: o.hp / max(o.max_hp, 1))
    b.say(f"{c} bathes {t} in reverse cursed energy.")
    b.heal(t, act.params["frac"] * t.max_hp, 1)


@effect("multi_hit")
def multi_hit(b, c, act, targets, part, amp, arg):
    for t in targets:
        for n in range(act.params.get("hits", 2)):
            if t.alive:
                b.strike(c, t, act, part, amp, no_react=n > 0)


@effect("cleave")
def cleave(b, c, act, targets, part, amp, arg):
    for t in targets:                                   # adjusts to the target's toughness
        b.strike(c, t, act, part, amp, power=act.power + 0.8 * t.base(S.DUR) + t.level)


def choose_touched(b, c) -> list:
    """Unlimited Void floods everyone inside it except Gojo and whoever he is touching: one ally per
    usable hand. Returns the root ids he keeps hold of (their own shikigami are spared with them)."""
    hands = sum(1 for p in (Part.L_ARM, Part.R_ARM) if c.usable(p))
    allies = [o for o in b.inside(c) if o.owner is None and o.root is not c.root and not b.hostile(c, o)]
    held: list = []
    while len(held) < hands:
        pool = [o for o in allies if o.cid not in held]
        if not pool:
            break
        if c.controller == "human":
            k = b.ask(c, "Unlimited Void reaches everyone inside you are NOT touching - allies too. "
                         f"Take hold of someone ({hands - len(held)} hand(s) free)?",
                      [f"Hold {o.name}" for o in pool] + ["Nobody" if not held else "Nobody else"],
                      [1.0] + [0.0] * len(pool))                 # (no answer: he grabs the first)
            if k >= len(pool):
                break
            held.append(pool[k].cid)
        else:
            held.append(max(pool, key=lambda o: (o.controller == "human", o.level)).cid)
    for cid in held:
        b.say(f"   {c} keeps a hand on {b.by_cid[cid]}: the Void passes them by.")
    left = [o for o in allies if o.cid not in held]
    if left:
        b.say(f"   Out of reach of {c}'s hands: {', '.join(o.name for o in left)}. The Void does not tell friend from foe.")
    return held


@effect("domain")
def generic_domain(b, c, act, targets, part, amp, arg):
    p = act.params
    data = {k: p[k] for k in ("scope", "objects") if k in p}      # how this domain targets (battle.domain_reaches)
    if p.get("touch"):
        data["spared"] = choose_touched(b, c)
    if b.open_domain(c, act.key, p["name"], p["rounds"] - 1, p["tick"], data, lethal=p.get("lethal", True),
                     open_barrier=p.get("open", False), shell=p.get("shell", "normal")) and b.rival is None:
        EFFECTS[p["tick"]](b, c, b.domain_of(c))        # the sure-hit lands at once


@effect("shrine_tick")
def shrine_tick(b, owner, d):
    """Malevolent Shrine has no barrier and no favourites: Cleave for everything with cursed energy,
    Dismantle for everything without, on everyone and everything in range but Sukuna and what is his."""
    b.say("Malevolent Shrine: slashes fill everything in range. Nothing in it is spared - friend, foe or stone.")
    hit = b.domain_targets(owner)
    friends = [t for t in hit if not b.hostile(owner, t)]
    if friends:
        b.say(f"   {', '.join(t.name for t in friends)}: on {owner}'s side, and inside it all the same.")
    b.aoe(owner, ACTIONS["dismantle"], targets=hit, sure_hit=True, power=13)
    if d.data.get("objects"):
        b.shred_field(owner, 13)


@effect("coffin_tick")
def coffin_tick(b, owner, d):
    b.say("Coffin of the Iron Mountain: the air itself burns.")
    b.aoe(owner, ACTIONS["ember_insects"], targets=b.domain_targets(owner), sure_hit=True, power=10)


@effect("sep_tick")
def sep_tick(b, owner, d):
    b.say("Self-Embodiment of Perfection: every soul inside is within reach.")
    for t in b.domain_targets(owner):
        b.strike(owner, t, ACTIONS["soul_touch"], Part.TORSO, sure_hit=True, power=16)


@hook("on_upkeep")
def _wheel_turns(b, c):
    """Mahoraga's adaptation advances every round for everything it has been hit by."""
    if "adapt" not in c.traits or not c.adapt:
        return
    done = []
    moving = False
    for tag, v in c.adapt.items():
        if v < 1.0:
            moving = True
            c.adapt[tag] = min(1.0, v + 0.34)
            if c.adapt[tag] >= 1.0 and not tag.startswith("act:"):
                done.append(tag)
    if moving:
        b.say(f"The wheel above {c} turns." + (f" Adaptation complete: {', '.join(sorted(done))}." if done else ""))
        if done:
            b.heal(c, 0.1 * c.max_hp)


# ======================================================================================
# Deadly Sentencing (Higuruma)
# ======================================================================================
@valid("deadly_sentencing")
def _ds_valid(b, c, act, target, arg):
    if target is not None and "hr_zero" in target.root.flags:
        return f"{target} has no cursed energy - the domain cannot register them as a defendant."
    return None


def judgeman_pick(b, t, heavier):
    """Judgeman knows everything about the defendant... and sometimes invents the rest."""
    ev = t.root.crimes.pick(b.rng, heavier) if t.root.crimes is not None else None
    if ev is not None and b.rng.random() > 0.25:
        code, ref, day = ev
        label, sev = CRIME_INFO[code]
        return f"{label} (day {day} of the colony, case file #{ref})", sev, True
    pool = [f for f in FABRICATED if not heavier or f[1] >= 2]
    label, sev = pool[int(b.rng.integers(len(pool)))]
    return label, sev, False


@effect("deadly_sentencing")
def deadly_sentencing(b, c, act, targets, part, amp, arg):
    t = targets[0]
    # Non-lethal: the "sure-hit" is only the rules of the court, so anti-domain techniques do
    # nothing against it, and it is stronger in a clash.  Even locked against another domain the
    # trial is held; the verdict stands and the court then closes.
    if not b.open_domain(c, "ds_domain", "Deadly Sentencing", 0, None, {"no_burnout": True}, lethal=False):
        return
    court = b.domain_of(c)
    c.meta["court_held"] = True
    b.say("A courtroom ringed with guillotines. All violence is prohibited. Judgeman opens its stitched eyes.")
    if t.pending:
        b.say(f"   {t}'s {t.pending.act.name} dissolves - violence is not permitted in court.")
        t.pending = None
        b.part_ce[t.idx] = 0
    sentence = 0
    for trial in range(2):                              # the original trial and one retrial
        label, sev, real = judgeman_pick(b, t, heavier=trial > 0)
        b.say(f'Judgeman: "{t} is suspected of {label}."')
        b.tell(c, "Evidence envelope: " + ("the record supports the charge." if real
                                           else "there is nothing on record - the charge is invented."))
        plea = b.ask(t, "Your statement to the court?",
                     ["Remain silent", "Confess", "Deny the charge"], [0.4, 0.15, 0.45])
        b.say(f"{t} " + ("remains silent.", "confesses.", "denies the charge.")[plea])
        p = {(True, 0): 0.75, (True, 2): 0.60, (False, 0): 0.45, (False, 2): 0.25}.get((real, plea), 1.0)
        p = float(np.clip(p + 0.02 * (c.stat(S.PER) - t.stat(S.PER)), 0.05, 0.95)) if plea != 1 else 1.0
        if b.rng.random() >= p:
            b.say('Judgeman: "NOT GUILTY."')
            sentence = 0
            break
        if real and plea == 2 and sev < 2:
            sev += 1
            b.say("   Lying to the court aggravates the sentence.")
        sentence = sev
        b.say('Judgeman: "GUILTY. ' + ("DEATH PENALTY." if sev >= 3 else "CONFISCATION.") + '"')
        if trial == 0 and b.ask(t, "Demand a retrial? The new charge may be graver.",
                                ["Accept the verdict", "Demand a retrial"], [0.65, 0.35]) == 1:
            b.say(f"{t} demands a retrial. The first verdict is set aside.")
            sentence = 0
            continue
        break
    b.close_domain(court, burnout=False)
    if sentence >= 3:
        b.say(f"{c}'s gavel becomes the Executioner's Sword. One cut is death.")
        b.add_status(c, ST.EXEC_SWORD, 1.0, 99)
    if sentence >= 1:
        if t.innate:
            b.say(f"{t}'s cursed technique is confiscated.")
            b.add_status(t, ST.SEALED, 1.0, 3 + sentence)
        else:
            b.say(f"{t} has no technique to take - their cursed energy is confiscated instead.")
            b.add_status(t, ST.CE_SEALED, 1.0, 3 + sentence)


@effect("execute")
def execute(b, c, act, targets, part, amp, arg):
    t = targets[0]
    if b.strike(c, t, act, part, power=1.0, label="the Executioner's Sword") > 0:
        b.clear_status(c, ST.EXEC_SWORD)
        if t.alive:
            b.say(f"   The sentence is carried out on {t}.")
            b.kill(t, c, force=True)


# ======================================================================================
# Comedian (Takaba)
# ======================================================================================
def _confidence(c):
    return c.ts("comedian", {"confidence": 3})


@cond("confident")
def _confident(b, c):
    return None if _confidence(c)["confidence"] > 0 else "you doubt you're funny - the technique won't answer (Pep Talk first)"


@cond("doubting")
def _doubting(b, c):
    return None if _confidence(c)["confidence"] < 3 else "you're already sure you're hilarious"


@effect("pep_talk")
def pep_talk(b, c, act, targets, part, amp, arg):
    _confidence(c)["confidence"] = 3
    b.say(f"{c} slaps both cheeks. \"I'm funny. I'm FUNNY!\" Confidence restored.")


def _gag(b, c, t, outcome, mag) -> bool:
    """Apply a joke outcome. Returns False if the bit bombed."""
    tags = {"comedian", "gag"}
    if outcome in ("none", "backfire"):
        return False
    resist = b.adapt_resist(t, tags)
    b.adapt_note(t, tags)
    if resist >= 0.8:
        b.say(f"   {t} has adapted to the bit. Nothing happens.")
        return False
    if outcome == "bonk":
        b.apply_damage(c, t, Part.HEAD, 12 * mag * (1 - resist), DType.PHYSICAL, tags, "the punchline")
    elif outcome == "stun":
        b.add_status(t, ST.STUN, 1.0, 1)
    elif outcome == "heal":
        b.heal(c, 16 * mag, 1)
    elif outcome == "fizzle":
        if t.pending:
            b.say(f"   {t}'s {t.pending.act.name} is ruined.")
            t.pending = None
            b.part_ce[t.idx] = 0
        t.ce -= 12 * mag
        b.say(f"   {t} loses {12 * mag:.0f} cursed energy.")
    return True


@effect("comedian_joke")
def comedian_joke(b, c, act, targets, part, amp, arg):
    t = targets[0]
    st = _confidence(c)
    order = list(b.rng.permutation(len(JOKES)))
    chain, limit = 0, 2 + c.level // 4
    while order and t.alive:
        joke = JOKES[order.pop()]
        b.say(f'{c}: "{joke.setup}"')
        none_w = min(0.6, 0.15 + 0.03 * t.stat(S.PER))       # sharp opponents refuse the bait
        w = [none_w if o.outcome in ("none", "backfire") else (1 - none_w) for o in joke.options]
        opt = joke.options[b.ask(t, f"{c} is waiting for your answer:", [o.text for o in joke.options], w)]
        b.say(f'{t}: "{opt.text}"')
        b.say("   " + opt.result)
        if not _gag(b, c, t, opt.outcome, amp * (1 + 0.3 * chain)):
            st["confidence"] -= 2 if opt.outcome == "backfire" else 1
            b.say(f"   The bit bombs. {c}'s confidence wavers ({max(st['confidence'], 0)}/3).")
            break
        chain += 1
        b.add_status(c, ST.GAG_ARMOR, 1.0, 1)        # untouchable until the next round begins
        if chain >= limit or c.ce < 4 or not t.alive:
            break
        if b.ask(c, "Chain another joke? (4 CE)", ["Keep going", "Stop"], [0.8, 0.2]) == 1:
            break
        c.ce -= 4
    if chain >= 2:
        b.say(f"   {chain}-joke combo!")


# ======================================================================================
# Idle Death Gamble (Hakari)
# ======================================================================================
REACH = ("green", "red", "gold")


def idg_spin(b, c):
    d = b.domain_of(c)
    if d is None:
        return
    st = c.ts("idg", {"kakuhen": False, "jackpots": 0})
    fails = d.data.setdefault("fails", 0)
    # The house is the gambler: every miss raises the odds, probability-change mode raises
    # them further, and the fourth spin of a domain can't lose.
    p = 1.0 if fails >= 3 else min(0.95, 0.22 + 0.14 * fails + (0.45 if st["kakuhen"] else 0.0))
    tier = REACH[min(2, int(p * 3))]
    if b.rng.random() < p:
        odd = b.rng.random() < 0.75
        n = int(b.rng.choice([1, 3, 5, 7] if odd else [2, 4, 6]))
        b.say(f"   [{n}|{n}|{n}]  {tier.upper()} REACH... JACKPOT!")
        st["kakuhen"], st["jackpots"] = odd, st["jackpots"] + 1
        b.say(f"   The jackpot theme starts playing. {c} overflows with cursed energy; the body heals itself."
              + (" Odd number: the next domain starts in probability-change mode." if odd else ""))
        b.add_status(c, ST.JACKPOT, 1.0, 4)             # 4 rounds for 4 minutes 11 seconds
        b.full_restore(c)
        c.ce = c.max_ce
        b.close_domain(d, burnout=False)
    else:
        a, x = int(b.rng.integers(1, 8)), int(b.rng.integers(1, 8))
        reels = [a, a, x if x != a else a % 7 + 1] if b.rng.random() < 0.6 else list(b.rng.permutation(7)[:3] + 1)
        d.data["fails"] = fails + 1
        b.say(f"   [{reels[0]}|{reels[1]}|{reels[2]}]  " + (f"{tier} reach... miss." if reels[0] == reels[1] else "no reach."))


@cond("no_jackpot")
def _no_jackpot(b, c):
    return "the jackpot round is still playing" if c.has(ST.JACKPOT) else None


@effect("idle_death_gamble")
def idle_death_gamble(b, c, act, targets, part, amp, arg):
    if not b.open_domain(c, "idg_domain", "Idle Death Gamble", 4, "idg_tick", {"no_burnout": True}, lethal=False):
        return
    b.say("A train platform, turnstiles, reels spinning overhead. The rules pour into everyone's head; "
          "nothing here can hurt you - yet.")
    idg_spin(b, c)


@effect("idg_tick")
def idg_tick(b, owner, d):
    b.say(f"Idle Death Gamble: {owner} spins.")
    idg_spin(b, owner)


@effect("idg_attack")
def idg_attack(b, c, act, targets, part, amp, arg):
    for t in targets:
        hit = b.strike(c, t, act, part, amp)
        d = b.domain_of(c)
        if hit > 0 and d and d.key == "idg_domain":
            b.say("   The hit drops a ball into the start pocket - bonus spin!")
            idg_spin(b, c)


@hook("on_upkeep")
def _jackpot_heal(b, c):
    if c.has(ST.JACKPOT):
        b.full_restore(c)


@hook("on_status_end")
def _status_end(b, c, st):
    if st == ST.JACKPOT:
        b.say(f"The music stops. {c}'s jackpot round is over.")
    elif st == ST.RIKA_LINK:
        b.say(f"{c}'s connection to Rika lapses; the copied techniques go quiet.")
    elif st == ST.CHANNEL:
        c.channeling = None
        b.say(f"{c} lets the shikigami's power sink back into shadow.")
    elif st == ST.SEALED:
        c.meta.pop("burnt", None)
        b.say(f"{c}'s technique returns.")


# ======================================================================================
# Body Hop (Kenjaku)
# ======================================================================================
@valid("body_hop")
def _hop_valid(b, c, act, target, arg):
    if target is None or not target.corpse:
        return "Pick a corpse."
    if target.pclass == PClass.CURSED_SPIRIT:
        return "An exorcised curse leaves no body to take."
    return None


@effect("body_hop")
def body_hop(b, c, act, targets, part, amp, arg):
    corpse = targets[0]
    i, j = c.idx, corpse.idx
    for s in (S.MAX_HP, S.MAX_STA, S.STR, S.SPD, S.DUR):
        b.stats[i, s] = b.stats[j, s]
    fresh = corpse.meta.get("base_max_hp", float(b.stats[j, S.MAX_HP]))    # the body, minus its soul scars
    b.stats[i, S.MAX_HP] = c.meta["base_max_hp"] = fresh
    b.part_max[i] = b.part_max[j] * fresh / max(float(b.stats[j, S.MAX_HP]), 1e-9)
    b.part_state[i] = np.where(b.part_state[i] == PState.ABSENT, PState.ABSENT, PState.OK)
    b.full_restore(c)
    b.say(f"{c} opens {corpse.name}'s skull and settles in. The stitches close across the forehead.")

    advanced = c.level >= ADVANCED_LEVEL
    slots = (BRAIN_SLOTS + 1 if advanced else BRAIN_SLOTS) - 1         # body_hop itself takes one
    if c.record:
        slots = max(slots, c.record.brain_capacity - 1)
    new = [k for k in corpse.innate if TECHNIQUES[k].copyable and k not in c.techniques]
    old = [k for k in c.innate if k != "body_hop"]
    keep = new + (old if advanced else [])
    if not advanced and old:
        b.say(f"   The old body's technique ({', '.join(TECHNIQUES[k].name for k in old)}) is left behind.")
    while len(keep) > slots:                            # a brain only holds so many techniques
        drop = b.ask(c, "Your brain can't hold them all. Which technique do you let go?",
                     [TECHNIQUES[k].name for k in keep], [0.01] * (len(keep) - 1) + [1.0])
        b.say(f"   {c} lets go of {TECHNIQUES[keep[drop]].name}.")
        keep.pop(drop)
    c.techniques = [k for k in c.techniques if not TECHNIQUES[k].innate] + ["body_hop"] + keep
    all_flags = {f for t in TECHNIQUES.values() for f in t.flags}
    c.flags = (c.flags - all_flags) | {f for k in c.techniques for f in TECHNIQUES[k].flags}
    for key, val in corpse.tech_state.items():          # shikigami rosters, stored spirits, ...
        c.tech_state.setdefault(key, copy.deepcopy(val))
    if new:
        b.say(f"   {c} now wields {', '.join(TECHNIQUES[k].name for k in new)}.")
    c.ts("body_hop", {"bodies": []})["bodies"].append(corpse.name)
    if c.record:
        c.record.body = {int(s): float(b.stats[i, s]) for s in (S.MAX_HP, S.MAX_STA, S.STR, S.SPD, S.DUR)}
    corpse.corpse = False
    fire(b, "on_join", c)


# ======================================================================================
# Copy (Yuta) and Rika
# ======================================================================================
def _copy(c):
    st = c.ts("copy", {})
    st.setdefault("stored", [])
    st.setdefault("tools", [])
    return st


def _rika(b, c):
    return next((r for r in b.summons(c) if "rika" in r.base_traits), None)


@cond("has_rika")
def _has_rika(b, c):
    return None if _rika(b, c) else "Rika must be manifested first"


@cond("no_rika")
def _no_rika(b, c):
    return "Rika is already here" if _rika(b, c) else None


@hook("on_sever")
def _copy_on_sever(b, victim, atk, part):
    user = atk.root
    if "copy" not in user.techniques or part not in LIMBS:
        return
    st = _copy(user)
    new = [k for k in victim.innate if TECHNIQUES[k].copyable and k not in st["stored"] and k not in user.techniques]
    if new:
        st["stored"].append(new[0])
        b.say(f"   Rika swallows the severed limb. {user} has copied {TECHNIQUES[new[0]].name}.")


@effect("summon_rika")
def summon_rika(b, c, act, targets, part, amp, arg):
    lv = c.level
    b.add(summon_spec("Rika", "shikigami", lv, hp=140 + 10 * lv, ce=250 + 20 * lv, str_=18 + 0.5 * lv,
                      spd=13, dur=12, per=10, out=14 + 0.5 * lv, traits=("rika",),
                      actions=("rika_claw", "rika_beam", "block")), c.team, c)
    b.say(f"Rika unfolds behind {c}, a vault of cursed energy and stored tools.")


@effect("full_manifestation")
def full_manifestation(b, c, act, targets, part, amp, arg):
    rika = _rika(b, c)
    if rika is None:                                    # she fell before the ring was on
        b.say(f"{c} reaches for Rika, and she is gone.")
        return
    st = _copy(c)
    b.add_status(c, ST.RIKA_LINK, 1.0, 5)               # five rounds for five minutes
    refill = min(rika.ce, c.max_ce - c.ce)
    rika.ce -= refill
    c.ce += refill
    names = ", ".join(TECHNIQUES[k].name for k in st["stored"]) or "nothing copied yet"
    b.say(f"{c} slips on the ring. Full manifestation: Rika's reserve and every copy are open. [{names}]")


@hook("on_death")
def _rika_dies(b, c, killer):
    if "rika" in c.base_traits and c.owner:
        b.clear_status(b.by_cid[c.owner], ST.RIKA_LINK)


# ======================================================================================
# Ten Shadows
# ======================================================================================
def ts_state(c):
    return scout_state(c.tech_state, "ten_shadows")


def tame_all(tech_state: dict, mahoraga: bool = False) -> dict:
    """Convenience for veteran / NPC users."""
    st = tech_state.setdefault("ten_shadows", {"roster": {}, "inherit": {}, "totality": False, "wheel": {}})
    st["roster"] = {k: ("tamed" if (k != "mahoraga" or mahoraga) else "untamed") for k in SHIKI_ORDER}
    return tech_state


def _on_field(b, c) -> set:
    return {k for s in b.summons(c, "shikigami") for k in s.meta.get("shiki", ())}


def _free_tamed(b, c) -> list:
    st, out = ts_state(c), _on_field(b, c)
    out |= {e["id"] for e in st["out"]}                 # those roaming the colony cannot be called here
    return [k for k in SHIKI_ORDER if st["roster"][k] == "tamed" and k not in out]


def shiki_spec(b, owner, keys, ritual=False) -> Spec:
    st = ts_state(owner)
    inherited = [h for k in keys for h in st["inherit"].get(k, [])]
    defs = [SHIKIGAMI[k] for k in keys]
    everyone = defs + [SHIKIGAMI[h] for h in inherited]
    bonus = (1 + 0.03 * (owner.level - 1)) * (1 + 0.15 * len(inherited))
    name = defs[0].name if len(keys) == 1 else MERGE_NAMES.get(
        frozenset(keys), "Chimera (" + " + ".join(d.name for d in defs) + ")")
    if keys == ["divine_dogs"] and st["totality"]:
        name, bonus = "Divine Dog: Totality", bonus * 1.5
    elif inherited:
        name += " [Totality]"

    def best(attr):                                     # strongest parent plus a share of the rest
        v = sorted((getattr(d, attr) for d in defs), reverse=True)
        return (v[0] + 0.3 * sum(v[1:])) * bonus

    meta = {"shiki": list(keys), "ritual_owner": owner.cid if ritual else None, "helped": False,
            "owner_ce": not ritual}                     # a tamed shikigami runs on its user's cursed energy
    if "mahoraga" in keys and not ritual:
        meta["adapt"] = st["wheel"]                     # arrives with adaptations already made
    spec = summon_spec(name, "shikigami", owner.level, ce=40 if ritual else 0,
                       hp=sum(d.hp for d in defs) * (0.7 if len(defs) > 1 else 1.0) * bonus,
                       str_=best("str_"), spd=best("spd"), dur=best("dur"), per=best("per"),
                       out=10 + 0.5 * owner.level,
                       traits={t for d in everyone for t in d.traits},
                       actions=tuple(dict.fromkeys(a for d in everyone for a in d.actions)) + ("dodge",),
                       meta=meta, grade=owner.grade)       # a shikigami is as strong as its summoner
    # ...and as strong as the technique it belongs to: the same boost its user's body gets.
    power = TIER_POWER[int(TECHNIQUES["ten_shadows"].grade)] ** 0.5
    spec.stats[[S.MAX_HP, S.HP]] *= power
    spec.meta["dmg_mult"] = power
    return spec


@hook("on_join")
def _ten_shadows_join(b, c):
    if "ten_shadows" in c.techniques:
        c.adapt = ts_state(c)["wheel"]                  # the user can bear the wheel's burden


def _scout_enters(b, c, spec, entry):
    """Put something the player sent out into the colony onto the field of a fight at its node."""
    spec.controller = "human" if (c.controller == "human" and not entry.get("auto")) else "ai"
    spec.meta["scout"] = entry["id"]
    p = b.add(spec, c.team, c)
    hp = float(np.clip(entry.get("hp", 1.0), 0.05, 1.0))
    b.stats[p.idx, S.HP] = p.max_hp * hp
    b.part_hp[p.idx] = b.part_max[p.idx] * hp
    return p


@hook("on_join")
def _scouts_join(b, c):
    """A player's spirits and shikigami already standing at this node are part of the fight,
    whether the player is here in person or only watching through them."""
    if c.meta.get("remote_scout"):
        c.flags.add("remote")
    if c.record is None or b.node is None or c.meta.get("scouts_in") or c.kind != "fighter":
        return
    c.meta["scouts_in"] = True
    if "cursed_spirit_manipulation" in c.techniques:
        st = _csm(c)
        stored = {s["id"]: s for s in st["spirits"]}
        for e in st["out"]:
            sp = stored.get(e["id"])
            if sp and e["node"] == b.node:
                spec = npc_spirit(Grade(sp["grade"]), b.rng, sp["name"], sp["tech"])
                spec.kind, spec.meta = "spirit", {**spec.meta, "csm_id": sp["id"]}
                _scout_enters(b, c, spec, e)
    if "ten_shadows" in c.techniques:
        for e in ts_state(c)["out"]:
            if e["node"] == b.node:
                _scout_enters(b, c, shiki_spec(b, c, [e["id"]]), e)


@hook("on_finish")
def _scouts_after_battle(b, c):
    """Damage stays on a scout; a destroyed one is struck from the list of those out."""
    if c.record is None or b.node is None or c.kind != "fighter":
        return
    mine = {p.meta["scout"]: p for p in b.fighters if p.owner == c.cid and "scout" in p.meta}
    for key in ("csm", "ten_shadows"):
        if key not in c.tech_state:
            continue
        st = scout_state(c.tech_state, key)
        alive_ids = {s["id"] for s in st["spirits"]} if key == "csm" else {
            k for k, v in st["roster"].items() if v == "tamed"}
        for e in list(st["out"]):
            p = mine.get(e["id"]) if e["node"] == b.node else None
            if e["id"] not in alive_ids or (p is not None and p.meta.get("destroyed")) or not c.alive:
                st["out"].remove(e)
            elif p is not None:
                e["hp"] = float(np.clip(p.hp / max(p.max_hp, 1.0), 0.05, 1.0))


@choices("summon_shikigami")
def _summon_choices(b, c):
    if len(b.summons(c, "shikigami")) >= (3 if c.level >= 12 else 2):
        return []
    return [(k, f"{SHIKIGAMI[k].name}, +{SHIKIGAMI[k].cost} CE") for k in _free_tamed(b, c)]


@valid("summon_shikigami")
def _summon_valid(b, c, act, target, arg):
    need = act.ce + sum(SHIKIGAMI[k].cost for k in (arg or "").split("+") if k in SHIKIGAMI)
    return None if c.has(ST.JACKPOT) or b.ce_pool(c) >= need else f"needs {need} CE in total"


VALID["merge_shikigami"] = _summon_valid


@effect("summon_shikigami")
def summon_shikigami(b, c, act, targets, part, amp, arg):
    keys = arg.split("+")
    if not _in_garden(b, c):                            # inside Chimera Shadow Garden they cost nothing extra
        b.spend_ce(c, sum(SHIKIGAMI[k].cost for k in keys))
    if c.channeling in keys:                            # the wheel goes back into the shadow it came from
        b.say(f"{c} takes hold of what they were channelling and throws it into their own shadow.")
        c.channeling = None
        b.clear_status(c, ST.CHANNEL)
    rabbits = any("swarm" in x.base_traits for x in b.summons(c, "shikigami"))
    hidden = _tiger_out(b, c) or _in_garden(b, c)
    s = b.add(shiki_spec(b, c, keys), c.team, c)
    if rabbits and not hidden:                          # Rabbit Escape: a storm of decoys to arrive behind
        s.meta["ambush"] = True
        b.say(f"Behind the storm of rabbits nobody sees {s.name} arrive.")
    elif hidden:                                        # Tiger Funeral hides the arrival
        s.meta["ambush"] = True
        b.say(f"No sign, no shadow: {s.name} is simply there, beside something nobody can see.")
    else:
        b.say(f"{c} forms the shadow sign. {s.name} rises from the shadow.")


@choices("merge_shikigami")
def _merge_choices(b, c):
    free = [k for k in _free_tamed(b, c) if k != "mahoraga"]
    if len(b.summons(c, "shikigami")) >= (3 if c.level >= 12 else 2):
        return []
    return [(f"{a}+{x}", MERGE_NAMES.get(frozenset((a, x)), f"{SHIKIGAMI[a].name} + {SHIKIGAMI[x].name}"))
            for n, a in enumerate(free) for x in free[n + 1:]]


EFFECTS["merge_shikigami"] = summon_shikigami


@choices("taming_ritual")
def _ritual_choices(b, c):
    st = ts_state(c)
    return [(k, SHIKIGAMI[k].name) for k in SHIKI_ORDER if st["roster"][k] == "untamed"]


@effect("taming_ritual")
def taming_ritual(b, c, act, targets, part, amp, arg):
    s = b.add(shiki_spec(b, c, [arg], ritual=True), b.new_team())
    b.say(f'{c}: "With this treasure, I summon..." {s.name} answers, untamed and hostile to everyone present. '
          f"Only a kill by {c} alone will bind it.")


@choices("channel_shikigami")
def _channel_choices(b, c):
    return [(k, SHIKIGAMI[k].name) for k in _free_tamed(b, c)]


@effect("channel_shikigami")
def channel_shikigami(b, c, act, targets, part, amp, arg):
    c.channeling = arg
    b.add_status(c, ST.CHANNEL, 1.0, 12 if arg == "mahoraga" else 6)  # the wheel stays as long as he bears it
    d = SHIKIGAMI[arg]
    if arg == "mahoraga":
        c.adapt = ts_state(c)["wheel"]
        b.say(f"The eight-handled wheel appears over {c}'s head. They will adapt in Mahoraga's place.")
    else:
        b.say(f"{c} channels {d.name} through their own body ({', '.join(d.traits)}).")


@hook("on_damage")
def _ritual_help(b, tgt, atk, dmg):
    owner = tgt.meta.get("ritual_owner")
    if owner and atk is not None and atk.root.cid != owner:
        tgt.meta["helped"] = True


@hook("on_death")
def _shikigami_dies(b, c, killer):
    keys = c.meta.get("shiki")
    if not keys:
        return
    ritual_owner = c.meta.get("ritual_owner")
    if ritual_owner:
        owner = b.by_cid[ritual_owner]
        solo = killer is not None and killer.root.cid == ritual_owner and not c.meta["helped"]
        if solo and owner.alive:
            ts_state(owner)["roster"][keys[0]] = "tamed"
            b.say(f"   The ritual is complete. {SHIKIGAMI[keys[0]].name} kneels to {owner}.")
        else:
            b.say(f"   The ritual is void - {owner} did not exorcise it alone. {SHIKIGAMI[keys[0]].name} stays untamed.")
        return
    owner = b.by_cid[c.owner]
    st = ts_state(owner)
    for k in keys:
        if k == "divine_dogs" and not st["totality"]:
            st["totality"] = True
            b.say("   One Divine Dog is gone; its power pours into the other. Divine Dog: Totality.")
            continue
        st["roster"][k] = "dead"
        heirs = [h for h in SHIKI_ORDER if st["roster"][h] == "tamed" and h not in keys]
        if heirs:
            st["inherit"].setdefault(heirs[0], []).extend([k] + st["inherit"].pop(k, []))
            b.say(f"   {SHIKIGAMI[k].name} is destroyed for good. Its power passes to {SHIKIGAMI[heirs[0]].name}.")
        else:
            b.say(f"   {SHIKIGAMI[k].name} is destroyed for good.")


# ======================================================================================
# Cursed Spirit Manipulation (Geto)
# ======================================================================================
def scout_state(tech_state: dict, key: str) -> dict:
    """A player's stored spirits ("csm") or shikigami roster ("ten_shadows"), with the list of
    the ones currently out in the colony: [{"id", "node", "auto", "hp"}]."""
    fresh = {"spirits": [], "next": 1} if key == "csm" else {
        "roster": {k: ("tamed" if k == "divine_dogs" else "untamed") for k in SHIKI_ORDER},
        "inherit": {}, "totality": False, "wheel": {}}
    st = tech_state.setdefault(key, fresh)
    st.setdefault("out", [])
    return st


def _csm(c):
    return scout_state(c.tech_state, "csm")


def _away(b, st) -> set:
    """Ids out in the colony somewhere other than this fight: not available here."""
    return {e["id"] for e in st["out"] if b.node is None or e["node"] != b.node}


def _released(b, c) -> set:
    return {s.meta["csm_id"] for s in b.summons(c, "spirit") if "csm_id" in s.meta}


@cond("has_spirits")
def _has_spirits(b, c):
    return None if _csm(c)["spirits"] else "no stored spirits"


@valid("absorb")
def _absorb_valid(b, c, act, t, arg):
    if t is None or t.kind != "fighter" or t.pclass != PClass.CURSED_SPIRIT or not (t.alive or t.corpse):
        return "Only cursed spirits can be absorbed."
    if t.alive:
        if not b.hostile(c, t):
            return "Not an enemy."
        if c.grade - t.grade >= 2:                      # far weaker curses submit instantly
            return None
        limit = 0.15 if t.grade >= Grade.SPECIAL else 0.35
        if t.hp > limit * t.max_hp:
            return f"{t} is too strong to swallow - bring it under {limit:.0%} HP first."
    return None


@effect("absorb")
def absorb(b, c, act, targets, part, amp, arg):
    t = targets[0]
    st = _csm(c)
    st["spirits"].append({"id": st["next"], "name": t.name, "grade": int(t.grade), "level": t.level,
                          "tech": (t.innate or [None])[0]})
    st["next"] += 1
    b.say(f"{c} compresses {t} into a black orb and swallows it.")
    if t.alive:
        b.alive[t.idx] = False
        t.pending = None
        b._credit(c, t)
        b._loot(c, t)                                   # whatever it was carrying (a finger, say) is left behind
        for s in b.summons(t):
            b.unsummon(s)
        if b.domain_of(t):
            b.close_domain(b.domain_of(t), burnout=False)
    t.corpse = False


@choices("release_spirit")
def _release_choices(b, c):
    out = _released(b, c)
    if len(out) >= 3:
        return []
    st = _csm(c)
    out |= {e["id"] for e in st["out"]}                 # those roaming the colony are not in hand
    return [(str(s["id"]), f"{s['name']}") for s in st["spirits"] if s["id"] not in out]


@effect("release_spirit")
def release_spirit(b, c, act, targets, part, amp, arg):
    sp = next(s for s in _csm(c)["spirits"] if str(s["id"]) == arg)
    spec = npc_spirit(Grade(sp["grade"]), b.rng, sp["name"], sp["tech"])
    spec.kind, spec.meta = "spirit", {**spec.meta, "csm_id": sp["id"]}
    b.add(spec, c.team, c)
    b.say(f"{c} releases {sp['name']}.")


@hook("on_death")
def _spirit_dies(b, c, killer):
    if "csm_id" in c.meta and c.owner:
        st = _csm(b.by_cid[c.owner])
        st["spirits"] = [s for s in st["spirits"] if s["id"] != c.meta["csm_id"]]


@effect("cursed_swarm")
def cursed_swarm(b, c, act, targets, part, amp, arg):
    for t in targets:
        b.strike(c, t, act, part, amp, power=act.power + min(12.0, 1.5 * len(_csm(c)["spirits"])))


@valid("uzumaki")
def _uzumaki_valid(b, c, act, target, arg):
    need = 2 if act.params.get("all") else 1
    st = _csm(c)
    have = len([s for s in st["spirits"] if s["id"] not in _away(b, st)])
    return None if have >= need else f"needs {need} stored spirit(s) on hand"


@effect("uzumaki")
def uzumaki(b, c, act, targets, part, amp, arg):
    st = _csm(c)
    away = _away(b, st)
    hand = [s for s in st["spirits"] if s["id"] not in away]
    if not hand:
        b.say(f"{c} has no spirits on hand to spend.")
        return
    if act.params.get("all"):
        spent, mult = hand, 1.0
    else:                                               # mini: one spirit, compressed harder
        spent, mult = [max(hand, key=lambda s: s["grade"])], 1.6
    st["spirits"] = [s for s in st["spirits"] if s not in spent]
    gone = {s["id"] for s in spent}
    for s in b.summons(c, "spirit"):
        if s.meta.get("csm_id") in gone:
            b.unsummon(s)
    power = mult * sum(8 + 7 * s["grade"] for s in spent)
    b.say(f"{c} crushes {len(spent)} spirit(s) into a single spiral of cursed energy.")
    for t in targets:
        b.strike(c, t, act, part, amp, power=power)
    for s in spent:                                     # technique extraction
        if s["grade"] >= UZUMAKI_EXTRACT_MIN_GRADE and s["tech"]:
            atk = [a for a in TECHNIQUES[s["tech"]].actions if a.kind == Kind.ATTACK]
            if atk:
                best = max(atk, key=lambda a: a.power)
                c.granted[best.key] = c.granted.get(best.key, 0) + 1
                b.say(f"   Extracted from {s['name']}: one use of {best.name}.")


@react_fx("spend_spirit")
def _spend_spirit(b, c):
    st, out = _csm(c), _released(b, c)
    pool = [s for s in st["spirits"] if s["id"] not in out] or st["spirits"]
    weakest = min(pool, key=lambda s: s["grade"])
    st["spirits"].remove(weakest)
    for s in b.summons(c, "spirit"):
        if s.meta.get("csm_id") == weakest["id"]:
            b.unsummon(s)
    b.say(f"   {c} throws {weakest['name']} in the way.")


# ======================================================================================
# Idle Transfiguration (Mahito)
# ======================================================================================
@choices("spawn_limb")
def _limb_choices(b, c):
    if not (b.part_state[c.idx, list(EXTRA)] == PState.ABSENT).any() or c.has(ST.CE_SEALED):
        return []
    return [(str(x), f"{x} CE") for x in (10, 20, 40) if c.ce >= x]


@effect("spawn_limb")
def spawn_limb(b, c, act, targets, part, amp, arg):
    ce = int(arg)
    c.ce -= ce
    slot = next(p for p in EXTRA if b.part_state[c.idx, p] == PState.ABSENT)
    b.part_state[c.idx, slot] = PState.OK
    b.part_max[c.idx, slot] = b.part_hp[c.idx, slot] = ce * 1.5
    b.limb_ce[c.idx, slot] = ce
    b.say(f"{c} reshapes their soul and a new limb tears free, packed with {ce} cursed energy. "
          f"Their reach extends.")


@effect("transfigured_human")
def transfigured_human(b, c, act, targets, part, amp, arg):
    if len(b.summons(c)) >= 3:
        b.say(f"{c} has no more bodies to spare.")
        return
    b.add(summon_spec("Transfigured Human", "spirit", c.level, hp=35 + 3 * c.level, str_=9, spd=8, dur=4,
                      actions=("flail",)), c.team, c)
    b.say(f"{c} flicks out a shrunken human; it swells into a screaming puppet.")


# ======================================================================================
# Puppet Manipulation (heavenly restriction: a body traded for range and reserves)
# ======================================================================================
PUPPET_CHARGE = 80.0


def _puppets(c_or_state):
    """Puppet bookkeeping kept on the player: energy banked, puppets in the hideout, puppets out."""
    st = c_or_state if isinstance(c_or_state, dict) else c_or_state.ts("puppets", {"bank": 0.0, "stock": 3})
    st.setdefault("out", [])        # [{"id", "node", "hp"}] - puppets walking the colony
    st.setdefault("sel", None)      # id of the one the player is currently steering on the map
    st.setdefault("next", 1)
    return st


def _puppet_spec(c, pid: int, manual: bool, charge: float = 0.0) -> Spec:
    """A puppet carries its own cursed energy: a built-in reserve plus whatever charge the
    puppeteer banked into it when it left the hideout."""
    lv = c.level
    return summon_spec(f"Puppet Mk.{pid}", "puppet", lv, hp=70 + 6 * lv, ce=60 + 6 * lv + charge,
                       str_=14 + 0.5 * lv, spd=11,
                       dur=12, per=9, out=c.base(S.OUT),
                       actions=("sword_option", "ultra_cannon", "ultra_shield", "dodge"),
                       controller="human" if manual else "ai", meta={"pup_id": pid})


@hook("on_join")
def _puppeteer_join(b, c):
    if "hr_max" not in c.flags or c.meta.get("hr_ready"):
        return
    c.meta["hr_ready"] = True
    st = _puppets(c)
    home = c.meta.get("at_hideout") or (c.record is not None and b.node is not None and c.record.hideout == b.node)
    if not home:
        c.flags.add("remote")
    if c.record is not None and b.node is not None:     # puppets already standing at this node fight
        for entry in st["out"]:
            if entry["node"] == b.node:
                p = b.add(_puppet_spec(c, entry["id"], c.controller == "human", entry.get("charge", 0.0)),
                          c.team, c)
                b.stats[p.idx, S.HP] = max(1.0, p.max_hp * entry.get("hp", 1.0))
                b.part_hp[p.idx] = b.part_max[p.idx] * max(entry.get("hp", 1.0), 0.05)


@hook("on_death")
def _puppet_destroyed(b, c, killer):
    if c.kind != "fighter":                             # puppets, shikigami and released spirits
        c.meta["destroyed"] = True


@hook("on_finish")
def _puppets_after_battle(b, c):
    """Write surviving puppets' damage back to the map; wrecked ones are gone."""
    if "hr_max" not in c.flags or c.record is None or b.node is None:
        return
    st = _puppets(c)
    here = {p.meta.get("pup_id"): p for p in b.fighters if p.kind == "puppet" and p.owner == c.cid}
    for entry in list(st["out"]):
        p = here.get(entry["id"])
        if p is None or entry["node"] != b.node:
            continue
        if p.meta.get("destroyed") or not c.alive:
            st["out"].remove(entry)
        else:
            entry["hp"] = float(np.clip(p.hp / max(p.max_hp, 1.0), 0.05, 1.0))


@choices("deploy_puppet")
def _puppet_choices(b, c):
    # Reinforcements come out of the hideout: only possible when the fight is there
    # (or in an arena fight, which has no map).
    if b.node is not None and "remote" in c.flags:
        return []
    if _puppets(c)["stock"] <= 0 or len(b.summons(c, "puppet")) >= 3:
        return []
    return [("manual", "you give its orders"), ("auto", "it picks its own targets")]


@effect("deploy_puppet")
def deploy_puppet(b, c, act, targets, part, amp, arg):
    st = _puppets(c)
    st["stock"] -= 1
    pid, st["next"] = st["next"], st["next"] + 1
    manual = arg == "manual" and c.controller == "human"
    charge = min(st["bank"], PUPPET_CHARGE)             # energy stored up while hiding goes into the puppet
    st["bank"] -= charge
    spec = _puppet_spec(c, pid, manual, charge)
    b.add(spec, c.team, c)
    if c.record is not None and b.node is not None:
        st["out"].append({"id": pid, "node": b.node, "hp": 1.0, "charge": charge})
    b.say(f"{c} sends {spec.name} into the fight ({'manual' if manual else 'automated'}). "
          f"{st['stock']} left in the hideout.")


# ======================================================================================
# Tiger Funeral (its technique was never shown; built from fan ideas)
#   unseen   hard to hit and impossible to answer unless your perception is high
#   fear     skin contact in either direction paralyses with dread; how long depends on the
#            grade gap between the Ten Shadows user and the victim, and Funeral Hold keeps
#            the victim frozen for as long as the tiger stays in contact
#   ambush   while it is out, the user's other shikigami arrive instantly and unannounced
# ======================================================================================
def _tiger_out(b, c) -> bool:
    return "unseen" in c.traits or any("unseen" in s.traits for s in b.summons(c, "shikigami"))


QUICK["summon_shikigami"] = QUICK["merge_shikigami"] = _tiger_out


def fear(b, src, victim) -> bool:
    if not victim.alive or victim.team == src.team:
        return False
    if victim.has(ST.STUN) or victim.meta.get("fear_until", 0) > b.round:
        return False                                    # already frozen, or still braced against it
    tags = {"fear"}
    b.adapt_note(victim, tags)
    gap = int(src.root.grade) - int(victim.root.grade)
    if gap <= -2 or b.adapt_resist(victim, tags) >= 0.8:
        b.say(f"   Dread pours off {src}, but {victim} is far too strong to freeze.")
        victim.meta["fear_until"] = b.round + 3
        return False
    turns = 1 if gap <= 0 else 2 if gap <= 2 else 3
    b.say(f"   Contact. Every instinct {victim} has says predator - they lock up, paralysed with dread.")
    b.add_status(victim, ST.STUN, 1.0, turns)
    victim.meta["fear_until"] = b.round + turns + 2
    return True


@hook("on_hit")
def _fear_contact(b, atk, tgt, act, part, dmg):
    if act.rng != Rng.MELEE or act.key == "weapon" or act.effect == "funeral_hold":
        return                                          # only bare contact carries it
    if "fear" in tgt.traits and tgt.alive and atk.alive:
        fear(b, tgt, atk)
    if "fear" in atk.traits and tgt.alive:
        fear(b, atk, tgt)


@effect("funeral_hold")
def funeral_hold(b, c, act, targets, part, amp, arg):
    for t in targets:
        held = t.has(ST.STUN)
        dmg = b.strike(c, t, act, part, amp)
        if dmg <= 0 or not t.alive:
            continue
        if not held:
            fear(b, c, t)
            continue
        gap = int(c.root.grade) - int(t.root.grade)     # constant contact: the stronger side wins out
        p = 0.8 if gap >= 1 else 0.5 if gap >= -1 else 0.0
        if b.st_dur[t.idx, ST.STUN] < 3 and b.rng.random() < p:
            b.st_dur[t.idx, ST.STUN] += 1
            b.say(f"   {c} does not let go. {t} stays frozen.")
        else:
            b.say(f"   {t} starts to fight the dread off.")


# ======================================================================================
# Mythical Beast Amber (Kashimo)
# ======================================================================================
@hook("on_hit")
def _electric_ce(b, atk, tgt, act, part, dmg):
    """Cursed energy with the properties of electricity: it shocks and leaves a charge."""
    if "electric_ce" not in atk.flags or dmg <= 0 or not tgt.alive or act.effect == "discharge":
        return
    staff = act.effect == "weapon_strike" and atk.weapon is not None and "conductor" in atk.weapon.flags
    if b.costs(atk, act)[0] <= 0 and not atk.has(ST.AMBER) and not staff:
        return                                          # only blows that carry cursed energy
    tags = {"lightning"}
    if b.adapt_resist(tgt, tags) >= 0.8:
        return
    if b.part_state[tgt.idx, part] not in (PState.OK, PState.STUNNED):
        part = Part.TORSO
    b.say(f"   {atk}'s cursed energy crackles through {tgt}.")
    b.apply_damage(atk, tgt, part, 3 + 0.4 * atk.level, DType.CURSED, tags, "the shock")
    if tgt.alive:
        b.add_status(tgt, ST.CHARGED, 1.0, 4, part=part)


@valid("discharge")
def _discharge_valid(b, c, act, t, arg):
    if t is not None and not t.has(ST.CHARGED):
        return f"{t} carries no charge - land a blow with your cursed energy on them first."
    return None


@effect("discharge")
def discharge(b, c, act, targets, part, amp, arg):
    for t in targets:
        b.clear_status(t, ST.CHARGED)
        b.say(f"The charge on {t} answers the one {c} is holding. Lightning jumps the gap; it cannot miss.")
        b.strike(c, t, act, part, amp, sure_hit=True)


@cond("no_amber")
def _no_amber(b, c):
    return "you have already transformed" if c.has(ST.AMBER) else None


@valid("amber")
def _amber_valid(b, c, act, target, arg):
    if c.controller == "human" and b.ask(
            c, "Mythical Beast Amber can be used once. Your body will not outlast this battle, win or lose. "
               "Activate it?", ["Not yet", "Activate"]) != 1:
        return "You hold it back."
    return None


AMBER_BUFF = ((S.STR, 1.8), (S.SPD, 1.6), (S.DUR, 1.5), (S.PER, 2.0), (S.OUT, 1.6))


@effect("amber")
def amber(b, c, act, targets, part, amp, arg):
    for stat, mult in AMBER_BUFF:
        b.stats[c.idx, stat] *= mult
    b.add_status(c, ST.AMBER, 1.0, 99)
    b.say(f"{c} lets the technique run for the first and last time. Flesh turns to living current: "
          f"stronger, faster, harder, and aware of everything. There is no way back from this.")


# ======================================================================================
# Boogie Woogie (Todo)
# ======================================================================================
def _is_object(x) -> bool:
    return hasattr(x, "fid")


def _swappable(b, x) -> bool:
    """Boogie Woogie grabs cursed energy: fighters with none cannot be moved."""
    return x.alive and not x.fled and "remote" not in x.flags and (x.max_ce > 0 or x.borrows_ce)


def _boogie_pair(b, c, target, arg):
    other = (b.by_cid.get(arg) or b.field.get(arg)) if arg else None
    if target is not None and other is not None:
        return target, other
    return c, (target if target is not None else other)


def do_swap(b, x, y) -> None:
    """Trade places. Attacks already channelled at a place land on whatever is there now."""
    if _is_object(x):
        x, y = y, x
    aimed = [q.pending for q in b.fighters if q.alive and q.pending and q.pending.act.target == Target.ENEMY]
    if _is_object(y):                                   # a fighter and an imbued object
        loose = y.role == "throwable"
        x.pos = None if loose else y.fid
        token = "obj:" + (y.fid if loose else "")       # a loose object is left behind as a decoy
        for p in aimed:
            p.targets = [token if t == x.cid else t for t in p.targets]
        return
    x.pos, y.pos = y.pos, x.pos
    for p in aimed:
        p.targets = [y.cid if t == x.cid else x.cid if t == y.cid else t for t in p.targets]


@valid("boogie_woogie")
def _boogie_valid(b, c, act, target, arg):
    x, y = _boogie_pair(b, c, target, arg)
    if y is None or x is y or (_is_object(x) and _is_object(y)):
        return ("Name what to swap: one thing trades places with you, two things trade with each other "
                "(`use boogie_woogie e1`, `use boogie_woogie p2 e1`, `use boogie_woogie e1 car`).")
    for e in (x, y):
        if _is_object(e):
            if e.imbued <= 0:
                return f"The {e.name} holds no cursed energy - `imbue {e.fid}` first."
        elif not _swappable(b, e):
            return f"{e} has no cursed energy for Boogie Woogie to take hold of."
    return None


@effect("boogie_woogie")
def boogie_woogie(b, c, act, targets, part, amp, arg):
    x, y = _boogie_pair(b, c, targets[0] if targets else None, arg)
    do_swap(b, x, y)
    b.say(f"{c} claps. {x.name} and {'the ' if _is_object(y) else ''}{y.name} have traded places.")


def swap_candidates(b, tgt, atk) -> list:
    """What a defender could put in the attack's path: other enemies first, then imbued objects."""
    foes = [e for e in b.enemies(tgt) if e is not atk and _swappable(b, e)]
    return foes or [o for o in b.field.values() if o.imbued > 0]


def swap_reaction(b, tgt, atk):
    """Returns whatever now stands where the defender was, or None if the attacker saw through it."""
    read = float(np.clip(0.1 + 0.04 * (atk.stat(S.PER) - tgt.stat(S.PER)), 0.0, 0.5))
    if b.rng.random() < read:
        b.say(f"{tgt} claps - but {atk} reads the switch and follows.")
        return None
    pool = swap_candidates(b, tgt, atk)
    sub = pool[int(b.rng.integers(len(pool)))]
    do_swap(b, tgt, sub)
    b.say(f"{tgt} claps. {'The ' if _is_object(sub) else ''}{sub.name} is standing where {tgt} was.")
    return sub


def _boogie_ai(b, c):
    """Pull an ally (or yourself) out from under a channelled attack and leave an enemy there."""
    for e in b.enemies(c):
        p = e.pending
        if not p or p.act.target != Target.ENEMY:
            continue
        for cid in p.targets:
            v = b.by_cid.get(cid)
            if v is None or v.team != c.team or not _swappable(b, v):
                continue
            subs = [o for o in b.enemies(c) if o is not e and o is not v and _swappable(b, o)]
            if subs:
                return v, Part.TORSO, subs[0].cid
            objs = [o for o in b.field.values() if o.imbued > 0 and o.role == "throwable"]
            if objs:
                return v, Part.TORSO, objs[0].fid
    return None


AI_PICK["boogie_woogie"] = _boogie_ai


@valid("swap_strike")
def _swap_strike_valid(b, c, act, target, arg):
    if target is not None and not _swappable(b, target):
        return f"{target} has no cursed energy for Boogie Woogie to take hold of."
    return None


@effect("swap_strike")
def swap_strike(b, c, act, targets, part, amp, arg):
    for t in targets:
        c.pos = t.pos
        b.say(f"{c} claps and is beside {t} before the sound fades.")
        b.strike(c, t, act, part, amp, no_react=True)


# ======================================================================================
# Limitless (Gojo)
# ======================================================================================
@hook("on_join")
def _six_eyes(b, c):
    if "six_eyes" in c.flags and not c.meta.get("six_eyes"):
        c.meta["six_eyes"] = True                       # near-perfect efficiency and perception: the best
        b.stats[c.idx, S.EFF] = SIX_EYES_EFF            # there is at any level, and almost all of it back
        b.stats[c.idx, S.CE_REGEN] = SIX_EYES_RECOVERY  # every round
        b.stats[c.idx, S.PER] += 6
        b.say(f"{c}'s Six Eyes are open: every flow of cursed energy on the field is laid bare to them.")


@effect("blue")
def blue(b, c, act, targets, part, amp, arg):
    for t in targets:
        if b.strike(c, t, act, part, amp) > 0 and t.alive and t.pos is not None:
            t.pos = None
            b.say(f"   {t} is dragged into the open.")


@effect("void_tick")
def void_tick(b, owner, d):
    b.say("Unlimited Void: everything, forever, all at once - for everyone " + (
          f"{owner} is not touching." if d.data.get("scope") == "all" else "inside."))
    for t in b.domain_targets(owner):
        b.strike(owner, t, ACTIONS["void_domain"], Part.HEAD, sure_hit=True, power=9)
        b.add_status(t, ST.STUN, 1.0, 2, 1.0, {"void"})       # it does not let go the moment the barrier does


# ======================================================================================
# Ratio Technique (Nanami)
# ======================================================================================
@effect("ratio_strike")
def ratio_strike(b, c, act, targets, part, amp, arg):
    edge = 4 if c.equipment.get("weapon") == "blunt_sword" else 0     # the technique's own blade
    for t in targets:                                   # the forced weak point cancels durability
        b.strike(c, t, act, part, amp, power=(act.power + edge) * (100 + DUR_FACTOR * t.base(S.DUR)) / 100)


@effect("collapse")
def collapse(b, c, act, targets, part, amp, arg):
    b.aoe(c, act, amp)
    for obj in [o for o in b.field.values() if o.role == "cover"]:
        b.say(f"   The {obj.name} comes apart along its seven-to-three line.")
        b._break_object(obj, c)


@cond("overtime_ready")
def _overtime_ready(b, c):
    if c.meta.get("overtime"):
        return "you are already on overtime"
    return None if b.round >= 4 else "working hours are not over (from round 4)"


@effect("overtime")
def overtime(b, c, act, targets, part, amp, arg):
    c.meta["overtime"] = True
    c.mult["out"] *= 1.4
    c.mult["str"] *= 1.4
    b.say(f"{c} checks the time. Overtime: the restraint comes off (+40% output and strength).")


# ======================================================================================
# Cursed Speech (Inumaki)
# ======================================================================================
@effect("speech")
def speech(b, c, act, targets, part, amp, arg):
    p = act.params
    for t in targets:
        gap = int(t.root.grade) - int(c.grade)          # how far above the speaker the listener is
        b.say(f'{c}: "{act.name.split(": ")[1]}."')
        shielded = gap >= 0 and t.max_ce > 0 and t.ce >= 12 and not t.has(ST.CE_SEALED)
        if shielded:                                    # an equal can guard their ears with cursed energy
            t.ce -= 12
            b.say(f"   {t} wraps their hearing in cursed energy and the word slides off.")
        elif p["cmd"] == "stop":
            b.add_status(t, ST.STUN, 1.0, 2 if gap <= -2 else 1, 1.0, {"speech"})
        else:
            b.strike(c, t, act, part, amp, sure_hit=True)
        strain = p["strain"] * (1 + 0.5 * max(gap, 0)) * (2 if shielded else 1)
        b.apply_damage(None, c, Part.HEAD, strain, DType.CURSED, (), "the backlash in the throat")


# ======================================================================================
# Straw Doll (Nobara)
# ======================================================================================
@valid("resonance")
def _resonance_valid(b, c, act, t, arg):
    if t is None or t.has(ST.NAILED) or (b.part_state[t.idx, list(LIMBS)] == PState.DESTROYED).any():
        return None
    return f"There is no link to {t}: put a nail in them, or use a limb they have lost."


@effect("resonance")
def resonance(b, c, act, targets, part, amp, arg):
    for t in targets:
        b.clear_status(t, ST.NAILED)
        b.say(f"{c} drives a nail through the effigy. The blow travels the link straight to {t}'s soul.")
        b.strike(c, t, act, part, amp, sure_hit=True)


# ======================================================================================
# Projection Sorcery (Naobito / Naoya)
# ======================================================================================
def _frames(c) -> int:
    return c.meta.get("frames", 0) if c.has(ST.BOOST) else 0


@effect("frame_rush")
def frame_rush(b, c, act, targets, part, amp, arg):
    n = min(FRAME_STACKS, _frames(c) + 1)
    c.meta["frames"] = n
    b.clear_status(c, ST.BOOST)
    b.add_status(c, ST.BOOST, 1.0, 3, FRAME_STEP * n)
    b.say(f"{c} lays out the next second in twenty-four frames and steps into it. "
          f"Stack {n} of {FRAME_STACKS} (+{FRAME_STEP * n:g} speed and strength).")


def frames_broken(b, c, why: str) -> None:
    """A Projection Sorcery user who cannot finish the second they planned loses everything
    stacked on it - and, if enough was stacked, is caught in a frame themselves."""
    n = _frames(c)
    if not n:
        return
    c.meta["frames"] = 0
    b.clear_status(c, ST.BOOST)
    b.say(f"   {why} {c}'s planned second falls apart: {n} stack(s) gone.")
    if n >= 2 and c.alive:
        b.say(f"   {c} broke their own rule and is frozen in a frame.")
        b.add_status(c, ST.STUN, 1.0, 1)


@hook("on_status_end")
def _frames_lapse(b, c, st):
    if st == ST.BOOST:
        c.meta["frames"] = 0


@effect("frame_freeze")
def frame_freeze(b, c, act, targets, part, amp, arg):
    for t in targets:
        had = _frames(c)
        if b.strike(c, t, act, part, amp, power=act.power + 2 * had) > 0:
            if not t.alive or (had and not _frames(c)):
                continue                                # (a counter already broke the stack)
            if t.stat(S.SPD) >= c.stat(S.SPD):
                b.say(f"   {t} is fast enough to keep to twenty-four frames a second.")
            elif t.stat(S.PER) >= UNSEEN_PER:
                b.say(f"   {t} sees the rule and moves by it.")
            else:
                b.say(f"   {t} cannot move at twenty-four frames a second and is caught in one.")
                b.add_status(t, ST.STUN, 1.0, 1, 1.0, {"projection_sorcery"})
        else:
            frames_broken(b, c, "The touch never lands.")


# ======================================================================================
# Construction (Mai / Yorozu)
# ======================================================================================
@cond("no_cover")
def _no_cover(b, c):
    obj = b.field.get(c.pos)
    return "you are already behind cover" if obj and obj.role == "cover" else None


@effect("construct_wall")
def construct_wall(b, c, act, targets, part, amp, arg):
    obj = b.add_object("Constructed barricade", "cover", hp=45.0)
    c.pos = obj.fid
    b.say(f"{c} builds a barricade out of cursed energy and gets behind it.")


# ======================================================================================
# Jacob's Ladder (Angel)
# ======================================================================================
@hook("on_join")
def _winged(b, c):
    if "winged" in c.flags:
        c.base_traits.add("flight")


EXTINGUISHABLE = (ST.BOOST, ST.GAG_ARMOR, ST.INFINITY, ST.ANTI_DOMAIN, ST.JACKPOT, ST.RIKA_LINK, ST.CHANNEL)


@effect("extinguish")
def extinguish(b, c, act, targets, part, amp, arg):
    p = act.params
    for t in targets:
        marked = t.pclass in (PClass.CURSED_SPIRIT, PClass.REINCARNATED) or t.kind != "fighter"
        if b.strike(c, t, act, part, amp * (p.get("purge", 1.0) if marked else 1.0), nullify=True) <= 0 or not t.alive:
            continue
        out = [st for st in EXTINGUISHABLE if t.has(st)]
        for st in out:
            b.clear_status(t, st)
        if out:
            b.say(f"   The light puts out {', '.join(Status(st).name.lower() for st in out)} on {t}.")
        if p.get("seal"):
            b.add_status(t, ST.SEALED, 1.0, p["seal"])


# ======================================================================================
# Disaster Plants (Hanami) and Disaster Tides (Dagon)
# ======================================================================================
@effect("flower_field")
def flower_field(b, c, act, targets, part, amp, arg):
    b.say(f"Flowers open across the ground around {c}. The urge to fight drains away.")
    for t in b.enemies(c):
        b.add_status(t, ST.SLOW, 1.0, 3, 4.0, {"wood"})


@effect("skandha_tick")
def skandha_tick(b, owner, d):
    b.say("Horizon of the Captivating Skandha: the sea itself has teeth.")
    b.aoe(owner, ACTIONS["death_swarm"], targets=b.domain_targets(owner), sure_hit=True, power=12)


# ======================================================================================
# Answers to a domain: Simple Domain, Hollow Wicker Basket, Falling Blossom Emotion,
# Domain Amplification
# ======================================================================================
BIG_THREE = ("limitless", "ten_shadows", "projection_sorcery", "blood_manipulation",   # Gojo, Zen'in, Kamo
             "blazing_courage", "paralyzing_gaze")


@cond("ancient")
def _ancient(b, c):
    old = c.pclass == PClass.REINCARNATED or "body_hop" in c.flags
    return None if old else "an art from an older age: only reincarnated sorcerers know it"


@cond("big_three")
def _big_three(b, c):
    return None if any(k in c.techniques for k in BIG_THREE) else "a secret of the three great clans"


@effect("anti_domain")
def anti_domain(b, c, act, targets, part, amp, arg):
    p = act.params
    b.drop_stance(c, f"gives it up for a {p['anti']}")   # one answer to a domain at a time
    c.meta["anti"], c.meta["anti_hands"] = p["anti"], bool(p.get("hands"))
    b.add_status(c, ST.ANTI_DOMAIN, 1.0, p["rounds"])
    b.say(f"{c} raises a {p['anti']}." + (" Both hands are bound to the sign." if p.get("hands") else
                                           " They must hold their ground inside it."))


@effect("amplify")
def amplify(b, c, act, targets, part, amp, arg):
    b.drop_stance(c, "gives it up for Domain Amplification")
    b.clear_status(c, ST.INFINITY)                      # nothing of your own technique runs through it
    if c.pending and TECHNIQUES[ACTION_TECH[c.pending.act.key]].innate:
        c.pending = None
        b.part_ce[c.idx] = 0
    b.add_status(c, ST.AMPLIFY, 1.0, 2)
    b.say(f"{c} wraps their body in an empty domain. Techniques that touch it come apart; "
          f"their own is out of reach while it lasts.")


@effect("falling_blossom")
def falling_blossom(b, c, act, targets, part, amp, arg):
    b.drop_stance(c, "gives it up for Falling Blossom Emotion")
    b.add_status(c, ST.FBE, 1.0, 3)
    b.say(f"{c} lets cursed energy settle over their skin like falling petals: whatever touches it is struck.")


@hook("on_hit")
def _falling_blossom(b, atk, tgt, act, part, dmg):
    if tgt.has(ST.FBE) and act.rng == Rng.MELEE and atk.alive and tgt.alive and atk.team != tgt.team:
        b.apply_damage(tgt, atk, Part.TORSO, 4 + 0.6 * tgt.level, DType.CURSED, (), "Falling Blossom Emotion")


@cond("has_summon")
def _has_summon(b, c):
    return None if b.summons(c) else "you have nothing summoned to stand in the way"


# ======================================================================================
# Death saves: Miracles (Haruta) and a cursed corpse's spare cores (Panda)
# ======================================================================================
def death_save(b, c) -> bool:
    """Called when something would kill ``c``. True if they are still standing after all."""
    kind = "miracles" if "miracles" in c.flags else "cores" if "cores" in c.flags else None
    if kind is None or c.has(ST.SEALED) and kind == "miracles":
        return False
    left = c.meta.setdefault("saves", 2)
    if left <= 0:
        return False
    c.meta["saves"] = left - 1
    i = c.idx
    b.stats[i, S.HP] = 0.3 * b.stats[i, S.MAX_HP]
    for p in (Part.HEAD, Part.TORSO):
        b.part_hp[i, p] = max(b.part_hp[i, p], 0.3 * b.part_max[i, p])
    b.say(f"   {c} should be dead. " + ("A stored miracle is spent instead" if kind == "miracles"
                                        else "A core shatters, and another takes over") + f" ({left - 1} left).")
    return True


# ======================================================================================
# Star Rage (Yuki), Sky Manipulation (Uro), Anti-Gravity System (Kenjaku)
# ======================================================================================
@cond("no_garuda")
def _no_garuda(b, c):
    return "Garuda is already out" if any("garuda" in s.base_traits for s in b.summons(c)) else None


@effect("summon_garuda")
def summon_garuda(b, c, act, targets, part, amp, arg):
    lv = c.level
    b.add(summon_spec("Garuda", "shikigami", lv, hp=120 + 8 * lv, ce=60, str_=24 + 0.6 * lv, spd=15, dur=14, per=10,
                      traits=("garuda", "flight"), actions=("garuda_kick", "dodge"), grade=c.grade), c.team, c)
    b.say(f"Garuda coils out of the air beside {c}, heavy with borrowed mass.")


@effect("black_hole")
def black_hole(b, c, act, targets, part, amp, arg):
    b.say(f"{c} lets the mass run away with itself. For an instant there is a black hole where she stood.")
    b.aoe(c, act, amp, sure_hit=True)
    if c.alive:
        b.kill(c, None, force=True)


@effect("unanswerable")
def unanswerable(b, c, act, targets, part, amp, arg):
    for t in targets:                                   # nothing to block: the blow is in the space itself
        b.strike(c, t, act, part, amp, no_react=True)


@effect("sky_tick")
def sky_tick(b, owner, d):
    b.say("The sky itself is a pane of glass, and it breaks on everyone inside.")
    b.aoe(owner, ACTIONS["thin_ice_breaker"], targets=b.domain_targets(owner), sure_hit=True, power=14)


@effect("womb_tick")
def womb_tick(b, owner, d):
    b.say("Womb Profusion: gravity folds in on everything in reach.")
    b.aoe(owner, ACTIONS["gravity_press"], targets=b.domain_targets(owner), sure_hit=True, power=15)


# ======================================================================================
# The moves the canon fights needed from techniques that already existed
# ======================================================================================
def _love_blades(c) -> list:
    """Copied techniques that can fill Authentic Mutual Love's barrier: those with an attack in them."""
    return [k for k in _copy(c)["stored"] if any(a.kind == Kind.ATTACK for a in TECHNIQUES[k].actions)]


@effect("mutual_love")
def mutual_love(b, c, act, targets, part, amp, arg):
    """Yuta chooses ONE copied technique to imbue the barrier with, and it is turned on the one enemy
    he names - a sure-hit, every round, for as long as the domain stands."""
    stored = _love_blades(c)
    tech = None
    if stored:
        ranked = sorted(stored, key=lambda k: -max(a.power for a in TECHNIQUES[k].actions if a.kind == Kind.ATTACK))
        if c.controller == "human" and len(ranked) > 1:
            k = b.ask(c, "Authentic Mutual Love: which copied technique fills the barrier? It becomes the sure-hit.",
                      [TECHNIQUES[x].name for x in ranked[:24]], [1.0] + [0.0] * (len(ranked[:24]) - 1))
            tech = ranked[k]
        else:
            tech = ranked[0]
    target = targets[0] if targets else None
    data = {"only": target.root.cid if target is not None else None, "copied": tech}
    if b.open_domain(c, "mutual_love", "Authentic Mutual Love", 2, "mutual_love_tick", data) and b.rival is None:
        mutual_love_tick(b, c, b.domain_of(c))


@effect("mutual_love_tick")
def mutual_love_tick(b, owner, d):
    tech = TECHNIQUES.get(d.data.get("copied") or "")
    if tech is None:
        b.say("Authentic Mutual Love: a field of blades, and nothing copied to fill them with.")
        return
    marked = b.by_cid.get(d.data.get("only") or "")
    if marked is None or not marked.alive or marked.fled:        # the one it was turned on is gone: the next
        foes = [e for e in b.enemies(owner) if e.owner is None] or b.enemies(owner)
        marked = max(foes, key=lambda e: (e.level, e.hp), default=None)
        d.data["only"] = marked.root.cid if marked is not None else None
        if marked is not None:
            b.say(f"Authentic Mutual Love turns on {marked}.")
    best = max((a for a in tech.actions if a.kind == Kind.ATTACK), key=lambda a: a.power)
    hit = [t for t in b.domain_targets(owner) if t.owner is None] or b.domain_targets(owner)
    if not hit:
        b.say(f"Authentic Mutual Love: the barrier holds {best.name}, with nobody left to turn it on.")
        return
    b.say(f"Authentic Mutual Love: the barrier is {tech.name} now. {best.name} cannot miss {hit[0]}.")
    b.aoe(owner, best, targets=hit[:1], sure_hit=True)


@effect("world_slash")
def world_slash(b, c, act, targets, part, amp, arg):
    for t in targets:                                   # it cuts the space the target occupies
        b.strike(c, t, act, part, amp, nullify=True)


def _in_garden(b, c) -> bool:
    return b.domain_of(c) is not None and b.domain_of(c).key == "shadow_garden"


@effect("shadow_garden")
def shadow_garden(b, c, act, targets, part, amp, arg):
    # Incomplete, so it does not burn his technique out when it ends - but he carries whatever sinks into it.
    if b.open_domain(c, "shadow_garden", "Chimera Shadow Garden", 4, None, {"no_burnout": True, "weight": 0},
                     lethal=False):
        b.say("Shadow floods the ground like deep water. Anything of his can rise from anywhere in it.")


@cond("in_garden")
def _in_garden_cond(b, c):
    return None if _in_garden(b, c) else "only inside your own Chimera Shadow Garden"


QUICK["summon_shikigami"] = QUICK["merge_shikigami"] = lambda b, c: _tiger_out(b, c) or _in_garden(b, c)


@cond("no_true_form")
def _no_true_form(b, c):
    return "you have already taken that shape" if c.meta.get("true_form") else None


@effect("true_form")
def true_form(b, c, act, targets, part, amp, arg):
    c.meta["true_form"] = True
    for stat, mult in ((S.DUR, 1.8), (S.STR, 1.5), (S.SPD, 1.2)):
        b.stats[c.idx, stat] *= mult
    b.say(f"{c} grasps the true shape of their own soul: Instant Spirit Body of Distorted Killing.")


# ======================================================================================
# Lower-grade techniques
# ======================================================================================
@cond("has_crows")
def _has_crows(b, c):
    return None if c.meta.setdefault("crows", 2) > 0 else "no crows left"


@effect("bird_strike")
def bird_strike(b, c, act, targets, part, amp, arg):
    c.meta["crows"] = c.meta.get("crows", 2) - 1
    b.say(f"A crow folds its wings and falls like a spear, its life the price ({c.meta['crows']} left).")
    for t in targets:
        b.strike(c, t, act, part, amp)


@cond("no_sight")
def _no_sight(b, c):
    return "the crows are already watching" if c.meta.get("crow_sight") else None


@effect("crow_sight")
def crow_sight(b, c, act, targets, part, amp, arg):
    c.meta["crow_sight"] = True
    b.stats[c.idx, S.PER] += 5
    b.say(f"{c} sees through a dozen pairs of eyes at once (+5 perception).")


REGROW_PER_CE = 0.2       # Explosive Flesh: HP of his own blown-off flesh regrown per point of cursed energy
                          # (teeth are 15 cursed energy, an eye 60: the price moves from his head to his reserves)
JELLY_BASE, JELLY_PER_CE = 10, 0.4    # Moon Dregs: the jellyfish's HP = base + this much of its user's maximum cursed energy


@effect("flesh_bomb")
def flesh_bomb(b, c, act, targets, part, amp, arg):
    before, hp = float(b.part_hp[c.idx, Part.HEAD]), c.hp
    b.apply_damage(None, c, Part.HEAD, act.params["price"], DType.PHYSICAL, (), "what it cost to throw")
    c.meta["flesh_owed"] = c.meta.get("flesh_owed", 0.0) + max(0.0, before - float(b.part_hp[c.idx, Part.HEAD]))
    c.meta["flesh_owed_hp"] = c.meta.get("flesh_owed_hp", 0.0) + max(0.0, hp - c.hp)    # (a head wound costs more than itself)
    for t in targets:
        if c.alive:
            b.strike(c, t, act, part, amp)


@valid("seance")
def _seance_valid(b, c, act, target, arg):
    return None if target is not None and target.corpse else "Pick a corpse."


@effect("seance")
def seance(b, c, act, targets, part, amp, arg):
    body = targets[0]
    for stat in (S.STR, S.SPD, S.DUR):
        b.stats[c.idx, stat] = max(b.stats[c.idx, stat], b.stats[body.idx, stat])
    b.say(f"{c} swallows a piece of {body.name} and speaks the name. The body that answers is not their own.")


@cond("no_ritual")
def _no_ritual(b, c):
    return "the ritual is already in force" if c.meta.get("ritual") else None


@effect("forbidden_area")
def forbidden_area(b, c, act, targets, part, amp, arg):
    c.meta["ritual"] = True
    for o in b.fighters:
        if o.alive and o.team == c.team:
            o.mult["out"] *= 1.4
    b.say(f"{c} completes the dance. Everyone on her side burns 40% brighter.")


@effect("gaze")
def gaze(b, c, act, targets, part, amp, arg):
    for t in targets:
        gap = int(t.root.grade) - int(c.grade)
        b.say(f"{c}'s eye opens on {t}.")
        b.add_status(t, ST.STUN, 1.0, 2 if gap <= -2 else 1, 1.0, {"gaze"})
        if gap >= 0:                                    # holding an equal or better tears at the eye
            b.apply_damage(None, c, Part.HEAD, 8 + 6 * gap, DType.CURSED, (), "the strain on the eye")


@effect("create_corpse")
def create_corpse(b, c, act, targets, part, amp, arg):
    if len(b.summons(c)) >= 3:
        b.say(f"{c} has no more dolls to wake.")
        return
    lv = c.level
    b.add(summon_spec("Cursed Corpse", "puppet", lv, hp=60 + 5 * lv, ce=50, str_=12 + 0.5 * lv, spd=10, dur=10,
                      actions=("doll_strike", "block"), grade=c.grade), c.team, c)
    b.say(f"A stitched doll sits up beside {c} and looks around for something to hit.")


@cond("no_jellyfish")
def _no_jellyfish(b, c):
    if any("jellyfish" in s.base_traits for s in b.summons(c)):
        return "Moon Dregs is already out"
    return None                                         # (how many more there can be is a matter of cursed energy)


@effect("summon_jellyfish")
def summon_jellyfish(b, c, act, targets, part, amp, arg):
    hp = int(JELLY_BASE + JELLY_PER_CE * c.max_ce)        # it is made of its user's cursed energy
    b.add(summon_spec("Moon Dregs", "shikigami", c.level, hp=hp, ce=30, str_=8, spd=9, dur=6,
                      traits=("jellyfish", "ce_fed"), actions=("jelly_sting", "block"), grade=c.grade), c.team, c)
    left = int(b.ce_pool(c) // max(b.costs(c, act)[0], 1))
    b.say(f"A pale jellyfish drifts up behind {c}, tentacles trailing ({hp} HP). "
          f"{c} has the cursed energy for {left} more." if left else
          f"A pale jellyfish drifts up behind {c}, tentacles trailing ({hp} HP). {c} has not the cursed energy for another.")


# ======================================================================================
# Chimera Shadow Garden carries weight; receipts run out (Megumi against Reggie Star)
# ======================================================================================
GARDEN_LIMIT = 4          # how much sunk weight a Shadow Garden's owner can bear


def enemy_garden(b, c):
    return next((d for d in b.domains() if d.key == "shadow_garden" and b.hostile(c, b.by_cid[d.owner])), None)


def sink(b, c, tons: int, what: str) -> bool:
    """Drop something heavy into an enemy's Shadow Garden. Its owner carries everything in it:
    slowed and drained each round, and crushed if it passes GARDEN_LIMIT."""
    d = enemy_garden(b, c)
    if d is None or tons <= 0:
        return False
    owner = b.by_cid[d.owner]
    w = d.data["weight"] = d.data.get("weight", 0) + tons
    b.say(f"{c} lets the {what} sink into the shadow. Everything in there is {owner}'s to carry "
          f"(weight {w}; more than {GARDEN_LIMIT} cannot be borne).")
    if w > GARDEN_LIMIT:
        b.say(f"   It is more than {owner} can bear. The shadow gives way under it.")
        b.close_domain(d, burnout=False)
        b.apply_damage(c, owner, Part.TORSO, 18.0 * w, DType.PHYSICAL, (), "the weight in the shadow")
        if owner.alive:
            b.add_status(owner, ST.STUN, 1.0, 1)
    return True


@hook("on_upkeep")
def _garden_burden(b, c):
    d = b.domain_of(c)
    w = d.data.get("weight", 0) if d is not None and d.key == "shadow_garden" else 0
    if w:
        c.sta -= 4 * w
        b.st_dur[c.idx, ST.SLOW] = max(b.st_dur[c.idx, ST.SLOW], 1)
        b.st_mag[c.idx, ST.SLOW] = max(b.st_mag[c.idx, ST.SLOW], 2.0 * w)
        b.say(f"{c} strains under the weight sunk in the shadow (-{4 * w} stamina, slowed).")
        b.apply_damage(None, c, Part.TORSO, 5.0 * w, DType.PHYSICAL, (), "the strain of carrying it")


def _receipts(c) -> int:
    return c.meta.setdefault("receipts", 5 + c.level // 2)


@cond("has_receipts")
def _has_receipts(b, c):
    return None if _receipts(c) > 0 else "you are out of receipts"


@effect("receipt")
def receipt(b, c, act, targets, part, amp, arg):
    c.meta["receipts"] = _receipts(c) - 1
    if act.kind == Kind.HEAL:
        return heal(b, c, act, targets, part, amp, arg)
    if sink(b, c, act.params.get("tons", 0), act.name.split(": ")[-1].lower()):
        return
    for t in targets:
        b.strike(c, t, act, part, amp)


@react_fx("spend_receipt")
def _spend_receipt(b, c):
    c.meta["receipts"] = _receipts(c) - 1


@hook("on_damage")
def _soaked(b, tgt, atk, dmg):
    if "water" in b.last_tags and "contractual_recreation" in tgt.techniques and _receipts(tgt) > 0:
        lost = min(2, _receipts(tgt))
        tgt.meta["receipts"] -= lost
        b.say(f"   The water turns {lost} of {tgt}'s receipts to pulp ({tgt.meta['receipts']} left).")


# ======================================================================================
# The remaining techniques from the canon fights
# ======================================================================================
@effect("grave_tick")
def grave_tick(b, owner, d):
    n = d.data["count"] = d.data.get("count", 0) + 1
    inside = b.domain_targets(owner)
    b.say(f"Graveyard Domain: {('one', 'two', 'three')[min(n, 3) - 1]}.")
    if n == 1:
        for t in inside:
            b.say(f"   A coffin closes over {t} and the earth closes over the coffin.")
            b.add_status(t, ST.STUN, 1.0, 1, 1.0, {"disease"})
    for t in inside:
        b.apply_damage(owner, t, Part.TORSO, 8.0, DType.CURSED, {"disease"}, "the weight of the grave")
    if n >= 3:
        for t in inside:
            if t.alive:
                b.say(f"   {t} is still inside on the third count. The disease takes hold.")
                b.add_status(t, ST.POISON, 1.0, 5, 14.0, {"disease"}, Part.TORSO)


@effect("time_cell_tick")
def time_cell_tick(b, owner, d):
    b.say("Time Cell Moon Palace: every cell inside is held to twenty-four frames, each on its own clock.")
    for t in b.domain_targets(owner):
        b.strike(owner, t, ACTIONS["frame_freeze"], Part.TORSO, sure_hit=True, power=18)
        b.add_status(t, ST.STUN, 1.0, 1, 1.0, {"projection_sorcery"})


def _sphere(b, c, t, amp=1.0, sure_hit=False):
    """A perfect sphere touches at one point: whatever the target's durability, it counts for nothing."""
    act = ACTIONS["true_sphere"]
    return b.strike(c, t, act, Part.TORSO, amp, sure_hit=sure_hit,
                    power=act.power * (100 + DUR_FACTOR * t.base(S.DUR)) / 100)


@effect("true_sphere")
def true_sphere(b, c, act, targets, part, amp, arg):
    for t in targets:
        _sphere(b, c, t, amp)


def _break_sphere(b, d) -> bool:
    """Only a finished adaptation can meet the True Sphere: a shikigami that adapts (Mahoraga) and has
    already been shown Construction. It pierces the sphere, and the domain goes with it."""
    owner = b.by_cid[d.owner]
    breaker = next((t for t in b.enemies(owner) if "adapt" in t.base_traits and t.adapt.get("construct", 0) >= 1.0), None)
    if breaker is None:
        return False
    b.say(f"{breaker} has already adapted to Construction. It drives its blade through the True Sphere, "
          f"and the domain comes apart with it.")
    b.close_domain(d)
    if owner.alive:
        b.add_status(owner, ST.STUN, 1.0, 1)
    return True


@hook("on_join")
def _arrives_adapted(b, c):
    if "adapt" in c.base_traits:                        # summoned into an open Threefold Affliction
        for d in b.domains():
            if d.key == "threefold_affliction" and b.hostile(c, b.by_cid[d.owner]):
                _break_sphere(b, d)


@effect("sphere_tick")
def sphere_tick(b, owner, d):
    n = d.data["count"] = d.data.get("count", 0) + 1
    if n == 1:
        b.say("Threefold Affliction: overhead, a perfect sphere begins to take shape.")
        return
    if n == 2:
        b.say("Threefold Affliction: the True Sphere is complete, and it is coming down.")
        return
    if _break_sphere(b, d):
        return
    b.say("Threefold Affliction: the True Sphere lands. It cannot miss.")
    for t in b.domain_targets(owner):
        _sphere(b, owner, t, sure_hit=True)


@effect("summon_trail")
def summon_trail(b, c, act, targets, part, amp, arg):
    if sum("trail" in s.base_traits for s in b.summons(c)) >= 2:
        b.say(f"{c} already has both shikigami out.")
        return
    b.add(summon_spec("Trail Shikigami", "shikigami", c.level, hp=50 + 4 * c.level, ce=30, str_=10, spd=14, dur=8,
                      traits=("trail", "flight"), actions=("doll_strike", "dodge"), grade=c.grade), c.team, c)
    b.say(f"A shikigami streaks away from {c}. Where it has been is his now.")


@hook("on_upkeep")
def _territory_grows(b, c):
    if "shikigami_territory" in c.techniques:
        n = sum("trail" in s.base_traits for s in b.summons(c))
        if n:
            c.meta["territory"] = min(6, c.meta.get("territory", 0) + n)


@effect("territory_strike")
def territory_strike(b, c, act, targets, part, amp, arg):
    for t in targets:
        b.strike(c, t, act, part, amp, power=act.power + 5 * c.meta.get("territory", 0))


@effect("offbeat")
def offbeat(b, c, act, targets, part, amp, arg):
    for t in targets:
        if b.strike(c, t, act, part, amp) > 0 and t.alive:
            if t.has(ST.BOOST):
                b.clear_status(t, ST.BOOST)
                t.meta["frames"] = 0
                b.say(f"   {t} loses the beat, and everything riding on it.")
            b.add_status(t, ST.SLOW, 1.0, 2, 4.0)


@effect("heart_catch")
def heart_catch(b, c, act, targets, part, amp, arg):
    for t in targets:
        b.say(f"{c} closes a hand on nothing, and {t}'s heart is in it.")
        if int(t.root.grade) - int(c.grade) <= 1:
            b.add_status(t, ST.STUN, 1.0, 1, 1.0, {"heart"})
        else:                                           # too strong to hold: only pulled off balance
            t.guard = t.standing = None
            b.drop_stance(t, "is dragged out of it")
            b.say(f"   {t} tears free, guard down.")


@effect("g_pen")
def g_pen(b, c, act, targets, part, amp, arg):
    for t in targets:
        if b.strike(c, t, act, part, amp) > 0:
            c.meta["ink"] = c.meta.get("ink", 0) + 1
            b.say(f"   {c} has ink. The next page starts to draw itself.")


@cond("has_ink")
def _has_ink(b, c):
    return None if c.meta.get("ink", 0) > 0 else "you need your opponent's blood for ink first"


@valid("evacuate")
def _evacuate_valid(b, c, act, t, arg):
    return None if t is not None and t.alive and t.team == c.team else "Pick yourself or a living ally."


@effect("evacuate")
def evacuate(b, c, act, targets, part, amp, arg):
    t = targets[0]
    if b.trapped(t):
        b.say(f"{c} reaches for somewhere else, and the domain's barrier holds {t} where they are.")
    else:
        b._leave(t, f"{c} folds the space between here and there. {t} is gone from the fight.")


def _clones(b, c) -> int:
    return sum("clone" in s.base_traits for s in b.summons(c))


@effect("make_clone")
def make_clone(b, c, act, targets, part, amp, arg):
    if _clones(b, c) >= 4:
        b.say(f"{c} cannot split any further.")
        return
    b.add(summon_spec(f"Clone of {c.name}", "spirit", c.level, hp=30 + 3 * c.level, ce=20, str_=0.7 * c.base(S.STR),
                      spd=c.base(S.SPD), dur=5, traits=("clone",), actions=("doll_strike", "dodge"), grade=c.grade),
          c.team, c)
    b.say(f"{c} steps sideways out of himself. Now there are {_clones(b, c) + 1} of him.")


@effect("gang_up")
def gang_up(b, c, act, targets, part, amp, arg):
    for t in targets:
        b.strike(c, t, act, part, amp, power=act.power + 4 * _clones(b, c))


@effect("iai")
def iai(b, c, act, targets, part, amp, arg):
    weapon_strike(b, c, act, targets, part, amp, arg)


@valid("dohyo")
def _dohyo_valid(b, c, act, t, arg):
    if t is not None and t.has(ST.SEALED):
        return f"{t.name} is already in the ring"         # (and an NPC gets on with the wrestling)
    return None


@effect("dohyo")
def dohyo(b, c, act, targets, part, amp, arg):
    for t in targets:
        b.say(f"{c} stamps, and a ring is drawn around {t}. In the ring there is only sumo.")
        b.drop_stance(t, "has no place in the ring")
        b.add_status(t, ST.SEALED, 1.0, 2)


# ======================================================================================
# Reverse cursed technique is a matter of who, not of level
# ======================================================================================
@cond("can_rct")
def _can_rct(b, c):
    from .data import RCT_TECHNIQUES
    if c.pclass == PClass.CURSED_SPIRIT:
        return "cursed spirits cannot produce positive energy"
    return None if RCT_TECHNIQUES & set(c.techniques) else "you have never grasped reverse cursed technique"


@cond("seen_mahoraga")
def _seen_mahoraga(b, c):
    """The slash that cuts the world was modelled on Mahoraga's adaptation to Infinity."""
    st = c.tech_state.get("ten_shadows", {})
    if "ten_shadows" not in c.techniques or st.get("roster", {}).get("mahoraga") != "tamed":
        return "it is learned from Mahoraga's adaptation: it takes Ten Shadows as well, with Mahoraga tamed"
    if st.get("world_slash"):
        return None
    if st.get("wheel", {}).get("limitless", 0.0) < 1.0:
        return "locked until Mahoraga's wheel has adapted to Infinity (bear the wheel or summon Mahoraga against Limitless)"
    left = max(1, c.meta.get("slash_at", b.round + SLASH_ROUNDS) - b.round)
    return f"the wheel has shown the way; the slash is still taking shape ({left} more round{'s' if left != 1 else ''})"


@hook("on_upkeep")
def _flesh_regrows(b, c):
    """Explosive Flesh comes with the reverse cursed technique to undo it: the teeth and eyes he
    has thrown grow back at the start of the next round, for cursed energy. Only what he
    destroyed himself - a wound someone else gave him is not part of the technique."""
    owed = c.meta.get("flesh_owed", 0.0)
    if owed <= 0 or not c.alive or b.part_state[c.idx, Part.HEAD] == PState.DESTROYED:
        return
    if c.has(ST.SEALED) or c.has(ST.CE_SEALED):
        return                                          # no technique, no regrowing; it waits
    i = c.idx
    owed = min(owed, float(b.part_max[i, Part.HEAD] - b.part_hp[i, Part.HEAD]))
    amount = min(owed, REGROW_PER_CE * b.ce_pool(c))
    if amount <= 0:
        c.meta["flesh_owed"] = owed
        return
    b.spend_ce(c, int(np.ceil(amount / REGROW_PER_CE)))
    back = c.meta.get("flesh_owed_hp", amount) * amount / max(c.meta.get("flesh_owed", amount), amount)
    b.part_hp[i, Part.HEAD] += amount
    b.stats[i, S.HP] = min(b.stats[i, S.MAX_HP], b.stats[i, S.HP] + back)
    c.meta["flesh_owed"], c.meta["flesh_owed_hp"] = owed - amount, max(0.0, c.meta.get("flesh_owed_hp", back) - back)
    b.say(f"{c}'s teeth and eyes grow back ({back:.0f} HP, reverse cursed technique).")


@hook("on_upkeep")
def _world_slash_takes_shape(b, c):
    """Mahoraga adapts to Infinity; Sukuna watches how, and two rounds later can do it himself."""
    if c.kind != "fighter" or "shrine" not in c.techniques or "ten_shadows" not in c.techniques:
        return
    st = ts_state(c)
    if (st.get("world_slash") or st.get("roster", {}).get("mahoraga") != "tamed"
            or st.get("wheel", {}).get("limitless", 0.0) < 1.0):
        return
    if "slash_at" not in c.meta:
        c.meta["slash_at"] = b.round + SLASH_ROUNDS
        b.say(f"{c} has watched the wheel adapt to Infinity. Not the technique - the space it sits in. "
              f"A slash on that model begins to take shape ({SLASH_ROUNDS} rounds).")
    elif b.round >= c.meta["slash_at"]:
        st["world_slash"] = True
        b.say(f"{c} has it: Dismantle, extended to the world itself. The slash that cuts the world is his from now on.")


@cond("can_restore")
def _can_restore(b, c):
    """A burnt-out technique is a burnt-out brain, and a brain can be healed - a few times."""
    no = _can_rct(b, c)
    if no:
        return no
    if not (c.meta.get("burnt") and c.has(ST.SEALED) and b.st_dur[c.idx, ST.SEALED] <= 2):
        return "your technique is not burnt out"
    if c.meta.get("brain_heals", 0) >= BRAIN_HEALS:
        return "your brain cannot take being healed like that again in this fight"
    return None


@effect("restore_technique")
def restore_technique(b, c, act, targets, part, amp, arg):
    n = c.meta["brain_heals"] = c.meta.get("brain_heals", 0) + 1
    b.clear_status(c, ST.SEALED)
    c.meta.pop("burnt", None)
    b.say(f"{c} turns reverse cursed technique on their own brain: the burnt-out technique is back at once "
          f"({n} of {BRAIN_HEALS}).")
    if n >= BRAIN_HEALS:
        c.meta["last_domain"] = True
        b.say(f"   The damage is adding up. {c} has one more domain left in this fight, and no more healing like this.")


@cond("can_rct_out")
def _can_rct_out(b, c):
    from .data import RCT_OUTPUT_TECHNIQUES
    if c.pclass == PClass.CURSED_SPIRIT:
        return "cursed spirits cannot produce positive energy"
    return None if RCT_OUTPUT_TECHNIQUES & set(c.techniques) else "you cannot output reverse cursed energy into another body"


# ======================================================================================
# Ten Shadows at its highest level (Sukuna against Yorozu)
# ======================================================================================
@cond("dogs_tamed")
def _dogs_tamed(b, c):
    return None if ts_state(c)["roster"].get("divine_dogs") == "tamed" else "the Divine Dogs are gone"


@cond("armor_up")
def _armor_up(b, c):
    d = b.defence_of(c)
    return None if d is not None and d.key == "insect_armor" else "Insect Armor is not up"


@effect("elephant_drop")
def elephant_drop(b, c, act, targets, part, amp, arg):
    for t in targets:
        if b.strike(c, t, act, part, amp) > 0 and t.alive and (t.standing is not None or t.guard is not None):
            b.say(f"   {t}'s {(t.guard or t.standing).name} is crushed flat under it.")
            t.standing = t.guard = None


@effect("ox_charge")
def ox_charge(b, c, act, targets, part, amp, arg):
    run = min(3, b.round - c.meta.get("ran_from", b.round))
    c.meta["ran_from"] = b.round
    for t in targets:
        b.strike(c, t, act, part, amp, power=act.power + 10 * run)


@hook("on_join")
def _ox_starts_running(b, c):
    if "charge" in c.base_traits:
        c.meta["ran_from"] = b.round


# ======================================================================================
# Sukuna's fingers
# ======================================================================================
def set_fingers(b, c, n: int) -> None:
    """Sukuna's cursed energy amplifies everything a vessel does: output, strength, reserves.
    For Sukuna himself the fingers are how much cursed energy he has to put into a technique
    (records.sukuna_share): output, reserves and how fast they refill - nothing else about him."""
    old = c.meta.get("fingers_held", 0)
    own = bool(c.meta.get("sukuna"))
    new_mult = sukuna_share(n) if own else 1 + FINGER_AMP * n
    for k in (("out",) if own else ("out", "str")):
        c.mult[k] *= new_mult / c.meta.get("finger_mult", 1.0)
    c.meta["finger_mult"] = new_mult
    per = SUKUNA_CE_FINGER if own else FINGER_CE
    b.stats[c.idx, S.MAX_CE] += per * (n - old)
    b.stats[c.idx, S.CE] += per * (n - old)
    c.meta["fingers_held"] = n


def eat_finger(b, c) -> None:
    b.say(f"{c} swallows one of Sukuna's fingers.")
    held = c.meta.get("fingers_held", 0)
    if c.meta.get("sukuna"):
        set_fingers(b, c, held + 1)
        return
    limit = c.record.vessel if c.record is not None else c.meta.get("vessel", 0)
    if held + 1 > limit:
        return overtaken(b, c, held + 1)
    set_fingers(b, c, held + 1)
    if c.record is not None:
        c.record.fingers = held + 1
    b.say(f"   The body cages it. Sukuna's cursed energy runs under everything {c} does now "
          f"({held + 1} finger{'s' if held else ''}: +{FINGER_AMP * (held + 1):.0%} output and strength).")


def overtaken(b, c, eaten: int) -> None:
    """More fingers than the vessel can cage: the player is gone and Sukuna has the body."""
    old = c.name
    b.say(f"   It is more than {old}'s body can cage. Markings spread across the face, a second pair of eyes "
          f"opens beneath the first. {old} is gone. Sukuna is awake.")
    if c.record is not None:
        c.record.alive = False
        c.record.fingers = 0
        c.record = None
    fingers = eaten + c.inventory.count("sukuna_finger")           # he swallows the rest himself
    c.inventory = [k for k in c.inventory if k != "sukuna_finger"] + ["sukuna_finger"] * fingers
    c.name, c.controller, c.team, c.owner = f"Sukuna (in {old}'s body)", "ai", b.new_team(), None
    c.pclass, c.grade, c.level = PClass.REINCARNATED, Grade.SPECIAL, SUKUNA_LEVEL     # he is Sukuna, whatever the body was
    if "shrine" not in c.techniques:
        c.techniques.append("shrine")                               # his own technique, beside the body's
    c.meta.update(sukuna=True, unlock_bonus=99, host=old)        # nothing of his is locked behind a level
    body_hp = float(c.meta.get("base_max_hp", b.stats[c.idx, S.MAX_HP]))     # the flesh is still the vessel's
    c.meta["body_hp"] = body_hp
    if "ten_shadows" in c.techniques:                            # what the vessel never tamed, he does
        ts_state(c)["roster"]["mahoraga"] = "tamed"
        b.say(f"   The Ten Shadows are his now - Mahoraga with them.")
    c.flags.discard("remote")
    stats = build_stats(PClass.REINCARNATED, c.level, ["basic", "shrine"])
    stats[S.MAX_CE] = stats[S.CE] = SUKUNA_CE_BASE               # (the fingers add the rest, below)
    stats[S.MAX_HP] = stats[S.HP] = body_hp                      # his HP is the body's, whoever's it was
    stats[S.EFF] = SUKUNA_EFF
    if c.meta.get("six_eyes"):                                   # ...and so are its eyes
        stats[S.EFF], stats[S.CE_REGEN] = SIX_EYES_EFF, SIX_EYES_RECOVERY
    b.stats[c.idx] = stats
    b.part_max[c.idx, :6] = stats[S.MAX_HP] * PART_HP_FRAC[:6]
    c.meta["base_max_hp"] = float(stats[S.MAX_HP])
    b.st_dur[c.idx] = 0
    b.st_mag[c.idx] = 0
    b.full_restore(c)
    c.mult.update(out=1.0, str=1.0)
    c.meta["fingers_held"], c.meta["finger_mult"] = 0, 1.0
    set_fingers(b, c, fingers)
    c.pending = c.guard = c.standing = None
    c.plan = None
    b.say(f"   He has {fingers} finger{'s' if fingers != 1 else ''}, and everyone here is in his way.")
