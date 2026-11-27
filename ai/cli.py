"""Command-line front end. No graphics - everything is typed commands."""
from __future__ import annotations

import time
from types import SimpleNamespace
from typing import Optional

import numpy as np

from . import ai, vows
from .battle import IO, Battle
from .constants import (PART_HP_FRAC, CLASS_NAME, DAY, GRADE_NAME, Grade, Kind, Part, PClass, PState, Stat, Status,
                        REST_RECOVERY, SIX_EYES_RECOVERY, SIX_EYES_REST,
                        Target)
from .crimes import Crime
from .data import ITEMS, PLAYABLE, SHIKIGAMI
from .effects import PUPPET_CHARGE, scout_state
from .effects import _puppets as puppet_state
from .effects import tame_all
from .records import (PlayerRecord, finger_bearer, grade_for, npc_fighter, npc_spirit, roll_technique, roll_vessel,
                      sukuna_npc, vessel_techniques, xp_to_next)
from .rules import RULES, Colony, buy_rule, enforce_inactivity, transfer_points
from .storage import BattleCache, GameStore
from .techniques import ACTIONS, TECHNIQUES
from .world import Roamer, World

PART_ALIASES = {"head": Part.HEAD, "torso": Part.TORSO, "chest": Part.TORSO, "larm": Part.L_ARM,
                "l_arm": Part.L_ARM, "leftarm": Part.L_ARM, "rarm": Part.R_ARM, "r_arm": Part.R_ARM,
                "rightarm": Part.R_ARM, "lleg": Part.L_LEG, "l_leg": Part.L_LEG, "leftleg": Part.L_LEG,
                "rleg": Part.R_LEG, "r_leg": Part.R_LEG, "rightleg": Part.R_LEG,
                "extra1": Part.EXTRA_1, "extra2": Part.EXTRA_2}

BATTLE_HELP = """Each round you commit ONE choice - an action or a defence - and so does everyone else.
Then everything resolves in an order worked out from stats alone:
  blows land sooner the higher your SPEED; ranged techniques and buffs by the TECHNIQUE'S speed;
  anything channelled takes longer; an incantation, or the heaviest techniques, land next round.
What lands first can break what lands later (sever the arm it needs, stun its user).

First, the channel phase: before anyone commits, everyone gathers cursed energy in the body
parts they mean to use (`channel <technique>`, or `channel <parts> <amount>`, or `none`). It
leaves your pool at once. A technique that needs channelling can only be chosen if the parts it
requires hold enough; anything you gathered and did not use hardens those parts for the round.
Fighters with enough perception are told where your energy has gathered before they choose -
and you are told about theirs. Punches, kicks, weapons, defences and stances need no gathering.

Attack or defend:
  - Choose an action and you are committed: you do not get to defend this round, unless your
    perception is 16+ (then you are asked when something reaches you), your technique defends
    as it attacks (Boogie Woogie), or a standing defence is already up.
  - Choose a defence (`defend dodge`, `defend block`, `defend counter`, `defend reinforce`, or a
    technique's own) and it answers every attack that reaches you this round.
  - Some defences stay up as your default once set, leaving later rounds free for attacking:
    Infinity, Simple Domain and the other stances; technique guards marked "holds N rounds";
    and `defend cover [summon]`, which has one of your summons take blows aimed at you.
  - `wait` commits to nothing: you answer attacks with whatever looks best, automatically.
  - When an enemy's domain opens and you have one of your own (and a reaction left), you are
    asked whether to expand against it at once. In the middle of a technique that takes
    perception 16+, and the technique is dropped.

Battle commands
  status                      the clock; everyone's HP / max HP, every limb's HP and what is in
                              it (poison, bleeding, numb...), energy, speed, position
  actions                     what you can use right now, how long each takes to land, and why not
  attack <target> [part]      weapon strike if armed, otherwise a punch
  defend <defence> [summon]   commit this round to a defence (see above); `wait` to hold back
  use <action> [target] [part] [chant]
                              any action from `actions`; `chant` adds an incantation (+1 beat)
                              for +50% on techniques that allow it. Choice actions take the
                              option instead of a target:  use summon_shikigami nue
  move <object|ground>        climb a rooftop, take cover, get on a rail
  throw <object> <target> [part]
  boost <ce>                  free: burn cursed energy into stamina, strength and speed
  dismiss <summon>            free: call a shikigami or released spirit back unharmed, to make
                              room for another or to save a badly hurt one
  release                     free: let your own domain go before it runs out
  drop                        free: let go of a Simple Domain, Hollow Wicker Basket, Falling
                              Blossom Emotion or Domain Amplification. Only one can be held at
                              a time; raising another drops the first.
  imbue <object>              free: pour 5 cursed energy into an object (it throws harder, and
                              Boogie Woogie can swap with it). One free action per turn.
  item <object>               consume a cursed object (Cursed Relic, Sukuna's Finger)
  auto [id] | manual <id>     your puppets, shikigami and released spirits each take their own
                              turn. `manual s1` lets you command one on its turn; `auto` hands
                              it back to its own judgement. Free.
  item bandage                ordinary supplies work the same way
  equip <item>                cursed tools: only if this fight is in your own hideout (or from
                              Rika's vault). Ordinary weapons (bat, knife, katana, gun): anywhere.
                              An ordinary weapon holds no cursed energy - it cannot hurt a curse,
                              and a sorcerer killed with one rises as a curse. Use
                              `use infused_strike` / `use infused_shot` to pour energy in.
  vow [key]                   list binding vows / swear one (free)
  spare <target> <points>     buy mercy (needs the Point Transfer rule)
  flee | pass | help
Parts: head torso larm rarm lleg rleg (extra1 extra2).  Targets: the id in brackets (e1, p2, s1)."""


class CliIO(IO):
    def __init__(self, inp=input, out=print):
        self.inp, self.out = inp, out

    def say(self, text):
        self.out(text)

    def tell(self, c, text):
        self.out(f"   [{c.name} only] {text}")

    def ask(self, b, c, prompt, options):
        self.out(f"\n[{c.root.name}] {prompt}")
        for i, o in enumerate(options, 1):
            self.out(f"   {i}) {o}")
        while True:
            s = self.inp("choice> ").strip()
            if s.isdigit() and 1 <= int(s) <= len(options):
                return int(s) - 1

    def channel(self, b, c):
        if c.controller != "human":
            return ai.channel(b, c)
        self.out(f"\n-- Round {b.round}, channel phase: {c.name} [{c.cid}] - where do you gather cursed energy?")
        self.out(f"   {vitals(b, c)}")
        self.out("   `channel <technique>` gathers what it needs where it needs it; `channel <part...> <amount>` "
                 "is free-form; `none` gathers nothing.")
        while not channel_command(b, c, self.inp(f"{c.name} (channel)> "), self.out):
            pass

    def turn(self, b, c):
        if c.controller != "human":
            return ai.act(b, c)
        self.out(f"\n-- Round {b.round}: {c.name} [{c.cid}], commit an action or a defence  (type `help`)")
        self.out(f"   {vitals(b, c)}")
        self.out(f"   {limb_line(b, c)}")
        while not battle_command(b, c, self.inp(f"{c.name}> "), self.out):
            pass


# ---- battle display ------------------------------------------------------------------
PART_LABEL = {Part.HEAD: "head", Part.TORSO: "torso", Part.L_ARM: "l.arm", Part.R_ARM: "r.arm",
              Part.L_LEG: "l.leg", Part.R_LEG: "r.leg", Part.EXTRA_1: "limb+1", Part.EXTRA_2: "limb+2"}


def limb_line(b, c) -> str:
    """Every body part: HP out of its maximum, whether it is numb or gone, and what is in it."""
    out = []
    for p in Part:
        s = b.part_state[c.idx, p]
        if s == PState.ABSENT:
            continue
        if s == PState.DESTROYED:
            out.append(f"{PART_LABEL[p]} GONE")
            continue
        notes = (["numb"] if s == PState.STUNNED else []) + [f"{st.name.lower()} {left}" for st, left in b.part_statuses(c, p)]
        if b.part_rf[c.idx, p] >= 1:
            notes.append(f"reinforced {b.part_rf[c.idx, p]:.0f}")
        out.append(f"{PART_LABEL[p]} {max(b.part_hp[c.idx, p], 0):.0f}/{b.part_max[c.idx, p]:.0f}"
                   + (f" [{', '.join(notes)}]" if notes else ""))
    return " · ".join(out)


def vitals(b, c) -> str:
    """HP against max HP (and what max HP was before soul scars), cursed energy and how fast it returns."""
    base = c.meta.get("base_max_hp", c.max_hp)
    scar = f" (max was {base:.0f} before soul damage)" if base > c.max_hp + 0.5 else ""
    regen = b.stats[(c.root if c.borrows_ce else c).idx, Stat.CE_REGEN]
    pool = "runs on its user's" if c.borrows_ce else (
        f"{b.ce_pool(c):.0f}/{c.max_ce:.0f} (+{regen:.0f}% = {regen * c.max_ce / 100:.0f} a round)")
    return f"HP {max(c.hp, 0):.0f}/{c.max_hp:.0f}{scar}  CE {pool}  STA {c.sta:.0f}/{c.base(Stat.MAX_STA):.0f}"


def show_status(b, viewer, out) -> None:
    out(f"Round {b.round}" + (f" | Domain: {b.domain.name}" if b.domain else "")
        + (f" locked in a clash with {b.rival.name} (sure-hits cancelled)" if b.rival else ""))
    for c in b.fighters:
        if not c.alive:
            if c.corpse:
                out(f"  [{c.cid}] {c.name} - corpse")
            continue
        rel = "you" if c is viewer else "ally" if c.team == viewer.team else "ENEMY"
        sts = [f"{Status(s).name.lower()}({b.st_dur[c.idx, s]})" for s in Status
               if c.has(s) and b.st_part[c.idx, s] < 0]    # (statuses in a limb are shown on that limb)
        if c.meta.get("frames") and c.has(Status.BOOST):
            sts.append(f"frames x{c.meta['frames']}")
        where = b.field[c.pos].name if c.pos in b.field else "ground"
        extra = ""
        six = "six_eyes" in viewer.root.flags and c.team != viewer.team
        if c.pending and six:                             # the Six Eyes see the technique itself
            p = c.pending
            extra = (f" | channelling {p.act.name} ({b.costs(c, p.act)[0]} CE) in "
                     + "+".join(Part(q).name for q in p.parts))
        elif c.pending and c.team == viewer.team:
            extra = f" | bringing {c.pending.act.name} to bear"
        elif c.pending and viewer.cid in c.pending.seen:
            extra = " | channelling in " + "+".join(Part(q).name for q in c.pending.parts)
        elif c.pending:
            extra = " | mid-action"
        if six:
            extra += " | technique: " + (", ".join(TECHNIQUES[t].name for t in c.innate) or "none")
        # How much cursed energy someone holds is only visible to those who can read it.
        reads = (c.team == viewer.team or six or "revealed" in c.vow_flags
                 or viewer.root.stat(Stat.PER) >= 10 + 0.4 * c.level)
        ce = f"{c.ce:>4.0f}" if reads else "   ?"
        held = b.stance(c)
        if c.charge > 0 and (c.team == viewer.team or viewer.cid in c.read_by):   # energy you can see gathering
            extra += " | energy in " + "+".join(Part(q).name for q in c.charged)
        if c.team == viewer.team and b.defence_of(c) is not None:      # your side's defences are no secret to you
            extra += f" | defence: {b.defence_of(c).name}"
        remote = " (remote - untargetable)" if "remote" in c.flags else ""
        base = c.meta.get("base_max_hp", c.max_hp)
        scar = f" (was {base:.0f})" if base > c.max_hp + 0.5 else ""
        out(f"  [{c.cid}] {c.name:<24} {rel:<5} HP {c.hp:>4.0f}/{c.max_hp:<4.0f}{scar} CE {ce} "
            f"STA {c.sta:>3.0f} SPD {c.stat(Stat.SPD):>2.0f} @{where}{remote}"
            + (f" | {' '.join(sts)}" if sts else "") + (f" | holding {held}" if held else "") + extra)
        out(f"        {limb_line(b, c)}")
    if b.field:
        out("  Field: " + ", ".join(f"{o.fid} ({o.name}, {o.role}{', imbued' if o.imbued else ''})"
                                    for o in b.field.values()))


def channel_command(b, c, line: str, out=print) -> bool:
    """One command in the channel phase. Returns True when the fighter is done gathering."""
    tokens = [t.lower() for t in line.split()]
    if tokens[:1] == ["channel"]:
        tokens = tokens[1:]
    if not tokens or tokens[0] in ("none", "skip", "pass", "wait"):
        return True
    if tokens[0] in ("help", "?"):
        out(BATTLE_HELP)
    elif tokens[0] in ("status", "look", "s"):
        show_status(b, c, out)
    elif tokens[0] in ("actions", "a"):
        show_actions(b, c, out)
    elif tokens[0] in PART_ALIASES:                       # free-form: parts, then how much
        parts = [PART_ALIASES[t] for t in tokens if t in PART_ALIASES]
        amount = next((float(t) for t in tokens if t.replace(".", "", 1).isdigit()), 0.0)
        if amount <= 0:
            out("Say how much: `channel rarm larm 20`.")
        elif b.channel(c, parts, amount):
            out(f"You gather {amount:.0f} cursed energy in your " + " and ".join(Part(p).name for p in parts) + ".")
            return True
    else:
        mine = {a.key: a for a in b.actions_for(c) if a.channel}
        hits = [k for k in mine if k == tokens[0]] or [k for k in mine if k.startswith(tokens[0])]
        if not hits and any(a.key == tokens[0] for a in b.actions_for(c)):
            out("That needs no gathering. You gather nothing.")
            return True
        if len(hits) != 1:
            out("Techniques that need gathering: " + ", ".join(mine) + ". Or name body parts and an amount.")
        elif b.why_cant(c, mine[hits[0]]):
            out(f"Can't prepare {mine[hits[0]].name}: {b.why_cant(c, mine[hits[0]])}.")
        elif b.channel_for(c, mine[hits[0]]):
            c.meta["intent_name"] = mine[hits[0]].name
            out(f"You gather {c.charge:.0f} cursed energy in your " + " and ".join(Part(p).name for p in c.charged)
                + f" for {mine[hits[0]].name}.")
            return True
    return False


def show_actions(b, c, out) -> None:
    for a in b.actions_for(c):
        ce, sta = b.costs(c, a)
        why = b.why_cant(c, a)
        if why is None and b.phase == "commit" and a.channel and a.react is None:
            why = b.charged_for(c, a)                    # not gathered for this round
        kind = f"reaction:{a.react.name.lower()}" if a.react is not None else Kind(a.kind).name.lower()
        when = b.timing(c, a)                            # lower lands sooner; 1.00+ lands next round
        lead = ((f"holds {a.params['hold']} rounds" if a.params.get("hold", 0) < 50 else "holds") if a.params.get("hold")
                else "") if a.react is not None else (f"order {when:.2f}" + (" (next round)" if when >= 1 else ""))
        bits = [kind, lead, f"{ce} CE" if ce else "", f"{sta} STA" if sta else "",
                f"pow {a.power:g}" if a.power else "", "ranged" if a.rng else "",
                "channel" if a.channel else "", "chant ok" if a.can_chant else ""]
        out(f"  {a.key:<20} {a.name:<34} {' '.join(x for x in bits if x)}" + (f"   [x {why}]" if why else ""))


def _parse_tail(b, tokens):
    target, part, chant, arg = None, Part.TORSO, False, None
    for tok in tokens:
        low = tok.lower()
        if low == "chant":
            chant = True
        elif low in PART_ALIASES:
            part = PART_ALIASES[low]
        elif b.find(low) is not None:
            if target is None:
                target = b.find(low)
            else:                                        # a second name (Boogie Woogie swaps two things)
                arg = b.find(low).cid
        else:
            arg = low
    return target, part, chant, arg


def battle_command(b, c, line: str, out=print) -> bool:
    """Run one typed command. Returns True when it used up the turn."""
    tokens = line.split()
    if not tokens:
        return False
    cmd, rest = tokens[0].lower(), tokens[1:]
    if cmd in ("help", "?"):
        out(BATTLE_HELP)
    elif cmd in ("status", "look", "s"):
        show_status(b, c, out)
    elif cmd in ("actions", "a"):
        show_actions(b, c, out)
    elif cmd in ("pass", "wait"):
        return b.wait(c)
    elif cmd == "defend":
        mine = {a.key: a for a in b.actions_for(c) if a.react is not None}
        key = rest[0].lower() if rest else ""
        hits = [k for k in mine if k == key] or [k for k in mine if k.startswith(key) and key]
        if len(hits) != 1:
            out("Defences you have: " + ", ".join(mine))
            return False
        who = b.find(rest[1]) if len(rest) > 1 else None
        return b.defend(c, mine[hits[0]], who.cid if who else None)
    elif cmd == "flee":
        return b.flee(c)
    elif cmd in ("auto", "manual"):
        p = b.find(rest[0]) if rest else (c if c.kind != "fighter" else None)
        if p is None or p.kind == "fighter" or p.root is not c.root or not p.alive:
            out("Name one of your own puppets, shikigami or spirits (their ids are in `status`).")
        else:
            p.controller = "ai" if cmd == "auto" else "human"
            b.say(f"{p.name} is now {'automated' if cmd == 'auto' else 'under manual control'}.")
            if p is c and cmd == "auto":
                ai.act(b, c)
                return True
    elif cmd == "dismiss":
        b.dismiss(c, b.find(rest[0]) if rest else None)
    elif cmd == "release":
        b.release_domain(c)
    elif cmd == "drop":
        if not b.drop_stance(c):
            out("You are not holding a Simple Domain, Hollow Wicker Basket, Falling Blossom Emotion "
                "or Domain Amplification.")
    elif cmd == "imbue" and rest:
        b.imbue(c, rest[0].lower())
    elif cmd == "boost" and rest:
        b.boost(c, float(rest[0])) if rest[0].replace(".", "", 1).isdigit() else out("boost <amount>")
    elif cmd == "equip" and rest:
        b.equip(c, rest[0].lower())
    elif cmd == "item" and rest:
        return b.use_item(c, rest[0].lower())
    elif cmd == "move" and rest:
        return b.move(c, None if rest[0].lower() == "ground" else rest[0].lower())
    elif cmd == "throw" and len(rest) >= 2:
        target, part, _, _ = _parse_tail(b, rest[1:])
        return b.throw(c, rest[0].lower(), target, part)
    elif cmd == "vow":
        if not rest:
            for v in vows.VOWS.values():
                out(f"  {v.key:<16} {v.name}: {v.desc}")
        elif rest[0].lower() in vows.VOWS:
            vows.apply(b, c, vows.VOWS[rest[0].lower()])
        else:
            out("No such vow.")
    elif cmd == "spare" and len(rest) == 2 and rest[1].isdigit():
        target = b.find(rest[0])
        return bool(target) and vows.spare(b, c, target, int(rest[1]))
    elif cmd in ("attack", "use"):
        if cmd == "attack":
            key = next((k for k in ("weapon", "shoot") if b.why_cant(c, ACTIONS[k]) is None), "punch")
        elif not rest:
            out("use <action> ...")
            return False
        else:
            key, rest = rest[0].lower(), rest[1:]
        mine = {a.key: a for a in b.actions_for(c)}
        hits = [k for k in mine if k == key] or [k for k in mine if k.startswith(key)]
        if len(hits) != 1:
            out("Unknown or ambiguous action - see `actions`." if not hits else "Did you mean: " + ", ".join(hits))
            return False
        act = mine[hits[0]]
        if act.react is not None:                         # same as `defend <it>`
            who = b.find(rest[0]) if rest else None
            return b.defend(c, act, who.cid if who else None)
        target, part, chant, arg = _parse_tail(b, rest)
        if act.target == Target.ENEMY and target is None:
            foes = b.enemies(c)
            if len(foes) == 1:
                target = foes[0]
        if act.target == Target.CHOICE and arg is None:
            opts = b.choices(c, act)
            if opts and b.why_cant(c, act) is None:
                arg = opts[b.io.ask(b, c, f"{act.name}:", [f"{k} - {label}" for k, label in opts])][0]
        return b.perform(c, act, target, part, chant, arg)
    else:
        out("Unknown command. Type `help`.")
    return False


# ---- shared setup helpers ------------------------------------------------------------
def _pick(inp, out, prompt: str, options: list, default: int = 0) -> int:
    out(prompt)
    for i, o in enumerate(options, 1):
        out(f"   {i}) {o}")
    s = inp(f"choice [{default + 1}]> ").strip()
    return int(s) - 1 if s.isdigit() and 1 <= int(s) <= len(options) else default


def _int(inp, prompt: str, default: int, lo: int, hi: int) -> int:
    s = inp(f"{prompt} [{default}]> ").strip()
    return max(lo, min(hi, int(s))) if s.lstrip("-").isdigit() else default


def create_character(inp, out, server_id: str, user_id: str, ask_level: bool = False, rng=None) -> PlayerRecord:
    """``rng`` given: the technique is rolled by rarity (how the colony does it). Otherwise it is picked."""
    name = inp("Character name> ").strip() or f"Player {user_id}"
    pclass = PClass(_pick(inp, out, "Class:", CLASS_NAME))
    techs = PLAYABLE[pclass]
    if rng is not None:
        tech = roll_technique(pclass, rng)
        out(f"You awaken with {TECHNIQUES[tech].name} - a {GRADE_NAME[TECHNIQUES[tech].grade]} technique. "
            f"{TECHNIQUES[tech].desc}")
    else:
        tech = techs[_pick(inp, out, "Innate technique:",
                           [f"[{GRADE_NAME[TECHNIQUES[t].grade]}] {TECHNIQUES[t].name} - {TECHNIQUES[t].desc}" for t in techs])]
    rec = PlayerRecord(server_id, user_id, name, int(pclass), techniques=[tech])
    rec.level = _int(inp, "Level", 6, 1, 20) if ask_level else 1
    if rng is not None:                                      # how many of Sukuna's fingers this body can cage
        rec.vessel = roll_vessel(rng)
        if rec.vessel >= 20:
            out("You are one in twenty: a strong vessel. Your body could cage all of Sukuna's fingers.")
    if tech == "ten_shadows" and rec.unlock_level >= 6:      # veterans start with part of the roster
        tame_all(rec.tech_state)
    if TECHNIQUES[tech].tool:                                # some techniques come with their own cursed tool
        rec.equipment["weapon"] = TECHNIQUES[tech].tool
        out(f"Your technique comes with a cursed tool: {ITEMS[TECHNIQUES[tech].tool].name}.")
    return rec


def standard_field(b: Battle) -> None:
    b.add_object("Rooftop", "elevation")
    b.add_object("Car", "throwable", weight=16, power=28)
    b.add_object("Vending machine", "throwable", weight=12, power=18)
    b.add_object("Wall", "cover", hp=50)
    b.add_object("Rail", "speed")


# ---- arena: straight into a fight ----------------------------------------------------
NPC_ROSTER = [("Curse user (Shrine)", PClass.REINCARNATED, "shrine"),
              ("Lawyer (Deadly Sentencing)", PClass.SORCERER, "deadly_sentencing"),
              ("Comedian", PClass.SORCERER, "comedian"),
              ("Gambler (Idle Death Gamble)", PClass.SORCERER, "idle_death_gamble"),
              ("Shadow user (Ten Shadows)", PClass.SORCERER, "ten_shadows"),
              ("Spirit manipulator", PClass.SORCERER, "cursed_spirit_manipulation"),
              ("Copy user", PClass.SORCERER, "copy"),
              ("Body hopper", PClass.REINCARNATED, "body_hop"),
              ("Death Painting (Blood)", PClass.MUTANT, "blood_manipulation"),
              ("Zero-energy fighter", PClass.SORCERER, "heavenly_restriction"),
              ("Puppeteer", PClass.SORCERER, "puppet_manipulation"),
              ("Patchwork curse (Soul)", PClass.CURSED_SPIRIT, "idle_transfiguration"),
              ("Volcano curse (Flames)", PClass.CURSED_SPIRIT, "disaster_flames"),
              ("Thunder god (Mythical Beast Amber)", PClass.REINCARNATED, "mythical_beast_amber"),
              ("Brawler (Boogie Woogie)", PClass.SORCERER, "boogie_woogie"),
              ("The honoured one (Limitless)", PClass.SORCERER, "limitless"),
              ("Salaryman (Ratio)", PClass.SORCERER, "ratio"),
              ("Cursed Speech user", PClass.SORCERER, "cursed_speech"),
              ("Straw Doll user", PClass.SORCERER, "straw_doll"),
              ("Projection Sorcery user", PClass.SORCERER, "projection_sorcery"),
              ("Construction user", PClass.SORCERER, "construction"),
              ("Cannon (Granite Blast)", PClass.REINCARNATED, "granite_blast"),
              ("Frost user (Ice Formation)", PClass.REINCARNATED, "ice_formation"),
              ("Angel (Jacob's Ladder)", PClass.REINCARNATED, "jacobs_ladder"),
              ("Forest curse (Plants)", PClass.CURSED_SPIRIT, "disaster_plants"),
              ("Sea curse (Tides)", PClass.CURSED_SPIRIT, "disaster_tides"),
              ("The Sorcerer Killer (carries the Inverted Spear of Heaven)", PClass.SORCERER, "heavenly_restriction"),
              ("Receipt man (Contractual Re-creation)", PClass.REINCARNATED, "contractual_recreation"),
              ("Cockroach curse (Festering Life)", PClass.CURSED_SPIRIT, "festering_life"),
              ("Disease curse (Pestilence)", PClass.CURSED_SPIRIT, "pestilence"),
              ("Territory user (Shikigami Territory)", PClass.REINCARNATED, "shikigami_territory"),
              ("Rhythm fighter (Hakuna Laana)", PClass.SORCERER, "hakuna_laana"),
              ("Star Rage user", PClass.SORCERER, "star_rage"),
              ("Sky Manipulation user", PClass.REINCARNATED, "sky_manipulation"),
              ("Finger Bearer (special grade; drops one of Sukuna's fingers)", PClass.CURSED_SPIRIT, "finger_bearer"),
              ("Sukuna (the level you enter next is how many fingers he has, 1-20)", PClass.REINCARNATED, "sukuna"),
              ("Sukuna in a Ten Shadows vessel (fingers next, 1-20; against Limitless he can learn to cut the world)",
               PClass.REINCARNATED, "sukuna_megumi")]


def arena(inp=input, out=print, seed: Optional[int] = None) -> None:
    out("\n=== ARENA: build a fight ===")
    rng = np.random.default_rng(seed)
    colony = Colony("arena", "Arena", rules=["point_transfer"])
    b = Battle("arena", seed=seed, io=CliIO(inp, out), colony=colony, cache=BattleCache())
    n = _int(inp, "How many human players", 1, 1, 4)
    ffa = n > 1 and _pick(inp, out, "Players are:", ["allies (co-op)", "enemies (free for all)"]) == 1
    for i in range(n):
        out(f"\n-- Player {i + 1} --")
        rec = create_character(inp, out, "arena", f"u{i + 1}", ask_level=True)
        rec.points = 20
        rec.inventory += ["cursed_relic", "bandage"]
        for slot, prompt in (("weapon", "Cursed tool to carry in:"), ("armor", "Armor-type cursed tool to wear:")):
            tools = [it for it in ITEMS.values() if it.slot == slot and it.shop]   # no hideout here: arm up now
            have = ITEMS[rec.equipment[slot]].name if rec.equipment.get(slot) else "nothing"
            k = _pick(inp, out, prompt, [f"keep what you have ({have})"] + [f"{it.name} - {it.desc}" for it in tools])
            if k:
                rec.equipment[slot] = tools[k - 1].key
        b.add(rec.to_spec("human"), i if ffa else 0)
    out("\n-- Opponents --")
    for _ in range(_int(inp, "Cursed spirits", 2, 0, 6)):
        g = _pick(inp, out, "Grade:", GRADE_NAME, 2)
        b.add(npc_spirit(Grade(g), rng), 50)
    for _ in range(_int(inp, "NPC culling game players", 0, 0, 4)):
        k = _pick(inp, out, "Opponent:", [r[0] for r in NPC_ROSTER])
        name, pclass, tech = NPC_ROSTER[k]
        level = _int(inp, "Their level", 6, 1, 20)
        if tech == "finger_bearer":
            b.add(finger_bearer(rng), 50)
        elif tech == "sukuna":                               # the "level" asked for is his finger count
            b.add(sukuna_npc(level, rng), 50)
        elif tech == "sukuna_megumi":
            b.add(sukuna_npc(level, rng, ["ten_shadows"], "Megumi"), 50)
        else:
            b.add(npc_fighter(name, pclass, level, tech, rng,
                              weapon="inverted_spear" if name.startswith("The Sorcerer Killer") else None,
                              tech_state=tame_all({}) if tech == "ten_shadows" else None), 50)
    standard_field(b)
    out("\n" + BATTLE_HELP + "\n")
    b.run()


# ---- colony mode: map, roaming enemies, persistence ----------------------------------
WORLD_HELP = """Colony commands
  map | look | me              where things are / what's here / your sheet
  go <node>                    move along an edge (entering a building is trespass)
  deploy | puppets | puppet <id> | recall
                               puppeteers only. Your body never leaves the hideout: `deploy`
                               sends a puppet out, `puppet <id>` picks which one you steer,
                               `recall` (at the hideout) puts it back. No puppet out, no moving.
  scouts | send <id> [auto] | order <id> <node|auto|manual> | recall <id>
                               spirit manipulators and Ten Shadows users: send a stored spirit
                               or a tamed shikigami out into the colony. You see whatever it
                               sees (`scouts`, `look`). Order it node by node, or leave it on
                               `auto` to hunt curses on its own.
  break <obj#> | loot <obj#>   interact with objects here (it all goes on your record)
  wait [hours]                 let time pass; enemies keep moving toward you
  rest                         in a hideout: claim it and lie low; NPCs won't follow you in.
                               Resting does not heal - nothing heals on its own.
  heal [player]                reverse cursed technique on yourself, or on a player here
  medic | treat                where the colony's medic was last seen / be treated (same node)
  equip <item> | unequip <weapon|armor> | stash <item>
                               cursed tools change hands only in your own hideout
                               (stash: Copy users put a tool in Rika's vault)
  fingers | eat                Sukuna's fingers: where the Finger Bearers lurk, what you hold; eat one.
                               If your body can cage it, it amplifies everything you do for good.
                               If it cannot, Sukuna takes the body - you lose the character, and he
                               walks the colony gathering the rest.
  search                       turn this node over for ordinary things (bandages, knives, bats...)
  use <item>                   use a bandage on yourself
  shop | buy <item> | sell <item>
                               the colony's one shop; selling to the shop pays half price
  sell <item> <price> | market | buy #<n> | unlist <n>
                               put a cursed tool up for other players at your own price: at most
                               double its shop price - unless you took it from the dead, then
                               any price. Sold when another player buys it.
  rules | addrule <key>        colony rules cost 100 points each
  give <player> <points>       needs the Point Transfer rule
  pvp <player>                 attack another player at your node (works in hideouts too)
  players | switch <n> | new   hot-seat several characters
  save | quit"""


def colony_mode(inp=input, out=print, server_id: str = "local", seed: Optional[int] = None,
                prepare=None, free_pick: bool = False) -> None:
    """``prepare(colony, world, players)`` is a hook for tests and scripted scenarios."""
    store, cache = GameStore(), BattleCache()
    out(f"\n=== COLONY MODE (storage: {store.backend}, battle cache: {cache.backend}) ===")
    rng = np.random.default_rng(seed)
    colony = store.get_colony(server_id)
    if colony is None:
        colony = Colony(server_id, "Tokyo No. 1 Colony", managers=["u1"], map_seed=int(rng.integers(1 << 30)))
        store.put_colony(colony)
    saved = store.get_map(server_id)
    world = World.from_state(saved) if saved else World(colony.map_seed)
    players = [p for p in store.list_players(server_id) if p.alive]
    now = max([time.time(), colony.clock] + [p.last_score_ts for p in players])
    io = CliIO(inp, out)

    def save():
        colony.clock = now
        store.put_colony(colony)
        store.put_map(server_id, world.state())
        for p in players:
            store.put_player(p)

    def day():
        return int((now - colony.created_ts) // DAY)

    def fight(sides, node, label):
        """sides: list of (spec, team). Runs a battle at a node and writes results back."""
        b = Battle(server_id, seed=int(rng.integers(1 << 30)), io=io, colony=colony, world=world,
                   node=node, now=now, cache=cache)
        added = [b.add(spec, team) for spec, team in sides]
        for kw in world.field_objects(node):
            b.add_object(**kw)
        out(f"\n*** {label} ***\n" + BATTLE_HELP + "\n")
        b.run()
        for p in players:
            steer(p)
        for c in b.fighters:                              # a curse born in the fight stays in the colony
            if c.meta.get("vengeful") and c.alive:
                world.roamers.append(Roamer(max(r.rid for r in world.roamers) + 1, int(c.grade), node))
            if c.meta.get("sukuna") and c.alive and "roamer_id" not in c.meta:     # a vessel that could not hold him
                held = c.inventory.count("sukuna_finger")
                world.roamers.append(Roamer(max(r.rid for r in world.roamers) + 1, int(Grade.SPECIAL), node,
                                            kind="sukuna", fingers=held, vessel=vessel_techniques(c.techniques),
                                            host=c.meta.get("host", ""),
                                            slash=bool(c.tech_state.get("ten_shadows", {}).get("world_slash")),
                                            body_hp=float(c.meta.get("body_hp", c.max_hp))))
                out(f"\n!!! SUKUNA walks {colony.name} with {held} finger(s). He will gather the rest: the Finger "
                    f"Bearers first, then anyone carrying or caging one.")
        return added

    def is_puppeteer(p):
        return "puppet_manipulation" in p.techniques

    def present(p, nid):
        """A player's fighter for a battle at nid: in person, or commanding scouts from afar."""
        spec = p.to_spec("human")
        if not is_puppeteer(p) and p.node != nid:
            spec.meta["remote_scout"] = True
        return spec

    def steer(p):
        """A puppeteer's map position is the puppet they are steering, or their body if none is out."""
        if not is_puppeteer(p):
            return
        if p.hideout is None:                             # the body needs somewhere to stay
            p.hideout = min((n.nid for n in world.nodes.values() if n.kind == "hideout"),
                            key=lambda n: world.hops(0, n))
        st = puppet_state(p.tech_state.setdefault("puppets", {"bank": 0.0, "stock": 3}))
        ids = {e["id"]: e for e in st["out"]}
        if st["sel"] not in ids:
            st["sel"] = next(iter(ids), None)
        p.node = ids[st["sel"]]["node"] if st["sel"] is not None else p.hideout

    def where(p):
        """Every node this player can be found at: in person, or through what they sent out."""
        if not is_puppeteer(p):
            return [p.node] + [e["node"] for _, e, _ in scouts_of(p)]
        return [e["node"] for e in puppet_state(p.tech_state["puppets"])["out"]] + [p.hideout]

    def scouts_of(p):
        """[(kind, entry, name)] for every spirit and shikigami this player has out in the colony."""
        found = []
        if "cursed_spirit_manipulation" in p.techniques:
            st = scout_state(p.tech_state, "csm")
            stored = {s["id"]: s for s in st["spirits"]}
            found += [("spirit", e, stored[e["id"]]["name"]) for e in st["out"] if e["id"] in stored]
        if "ten_shadows" in p.techniques:
            found += [("shikigami", e, SHIKIGAMI[e["id"]].name)
                      for e in scout_state(p.tech_state, "ten_shadows")["out"]]
        return found

    def sight(nid):
        """What can be seen at a node (your own eyes or a scout's)."""
        n = world.nodes[nid]
        curses = [r.label for r in world.roamers if not r.respawn_at and r.node == nid]
        others = [p.name for p in players if nid in where(p)]
        intact = sum(not world.broken[o] for o in n.objects)
        return (f"node {nid} {n.name} [{n.kind}] -> {', '.join(map(str, n.edges))} | curses: "
                f"{', '.join(curses) or 'none'} | players: {', '.join(others) or 'none'} | {intact} intact object(s)"
                + (" | THE MEDIC IS HERE" if world.medic == nid else ""))

    def new_player():
        uid = f"u{len(store.list_players(server_id)) + 1}"
        rec = create_character(inp, out, server_id, uid, rng=None if free_pick else rng)
        rec.created_ts = rec.last_score_ts = now
        if not store.put_player(rec, new_only=True):
            out("That user already has a character in this colony.")
            return None
        players.append(rec)
        steer(rec)
        if is_puppeteer(rec):
            out(f"Your body is sealed in a hideout at node {rec.hideout}. It cannot travel: "
                f"`deploy` a puppet and steer that instead.")
        return rec

    for p in players:
        steer(p)
    if not players and new_player() is None:
        return
    if prepare is not None:
        prepare(colony, world, players)
    cur = 0
    out(WORLD_HELP)
    while True:
        players[:] = [p for p in players if p.alive]
        if not players:
            out("Everyone is dead. The culling game goes on without you.")
            save()
            return
        cur %= len(players)
        me = players[cur]
        steer(me)
        node = world.nodes[me.node]
        tokens = inp(f"\n[day {day()}] {me.name} @ {node.name} ({me.points} pts)> ").split()
        if not tokens:
            continue
        cmd, rest = tokens[0].lower(), tokens[1:]
        spend = 0.0                                       # hours of game time this command takes
        if cmd in ("quit", "exit"):
            save()
            return
        elif cmd == "help":
            out(WORLD_HELP)
        elif cmd == "save":
            save()
            out("Saved.")
        elif cmd == "map":
            out(world.describe(me.node))
        elif cmd == "look":
            out(f"{node.name} [{node.kind}] -> " + ", ".join(f"{e}:{world.nodes[e].name}" for e in node.edges))
            for oid in node.objects:
                o = world.objects[oid]
                state = "broken" if world.broken[oid] else "looted" if world.looted[oid] else "intact"
                out(f"   obj#{oid} {o.name} ({o.role}, {state})")
            here = [p.name + (" (puppet)" if is_puppeteer(p) and p.hideout != me.node else "")
                    for p in players if me.node in where(p) and p is not me]
            near = [f"{r.label} at node {r.node}" for r in world.roamers
                    if not r.respawn_at and (r.node == me.node or r.node in node.edges)]
            out("   Players here: " + (", ".join(here) or "none") + " | Nearby: " + (", ".join(near) or "quiet"))
            if world.medic == me.node:
                out("   The colony's medic is here. (`treat`)")
            for kind, e, name in scouts_of(me):           # what your scouts see
                out(f"   Through {name}: {sight(e['node'])}")
        elif cmd == "me":
            left = colony.inactivity_days - (now - me.last_score_ts) / DAY
            out(f"{me.name}: {CLASS_NAME[me.pclass]}, level {me.level} ({me.xp}/{xp_to_next(me.level)} XP), "
                f"{GRADE_NAME[grade_for(me.level, me.techniques)]}, {me.points} points")
            out(f"   Techniques: {', '.join(TECHNIQUES[t].name for t in me.techniques)} "
                f"(brain capacity {me.brain_capacity})")
            out(f"   Condition: {me.condition_text()}")
            stats = me.to_spec().stats
            cond = me.condition or {"hp": 1.0, "parts": [1.0] * 6, "gone": [0] * 6, "scar": 0.0}
            mx = stats[Stat.MAX_HP] * (1 - cond["scar"])
            out(f"   HP {mx * cond['hp']:.0f}/{mx:.0f}"
                + (f" (max was {stats[Stat.MAX_HP]:.0f} before soul damage)" if cond["scar"] > 0.001 else "")
                + " | " + " · ".join(
                    f"{PART_LABEL[Part(i)]} " + ("GONE" if cond["gone"][i] else
                                                 f"{mx * PART_HP_FRAC[i] * cond['parts'][i]:.0f}/{mx * PART_HP_FRAC[i]:.0f}")
                    for i in range(6)))
            six = any("six_eyes" in TECHNIQUES[k].flags for k in me.techniques if k in TECHNIQUES)
            pct = SIX_EYES_RECOVERY if six else stats[Stat.CE_REGEN]
            have = me.rested_ce(now)
            out(f"   Cursed energy {have * stats[Stat.MAX_CE]:.0f}/{stats[Stat.MAX_CE]:.0f}"
                + ("" if have >= 0.999 else f" ({have:.0%}: still coming back from the last fight)")
                + f". It returns {pct:.0f}% of the maximum a round in a fight and "
                  f"{(SIX_EYES_REST if six else REST_RECOVERY):.0%} every 5 minutes outside one.")
            out(f"   Stamina {stats[Stat.MAX_STA]:.0f}, {stats[Stat.STA_REGEN]:.1f} a round; full again between fights.")
            out(f"   Cursed energy efficiency: {me.efficiency:.0f}% off technique costs"
                + (" (the Six Eyes: the highest there is)" if six else ""))
            out("   Vessel: " + ("strong - it can cage all twenty of Sukuna's fingers" if me.vessel >= 20 else
                                 "ordinary - nobody knows how many fingers it can take, if any")
                + f". Fingers caged: {me.fingers}"
                + (f" (+{10 * me.fingers}% output and strength on everything)." if me.fingers else "."))
            if "limitless" in me.techniques:
                out("   Six Eyes: +35 efficiency and +6 perception in a fight; you read every technique as it "
                    "is channelled, and see every enemy's technique and cursed energy in `status`.")
            out(f"   Gear: {me.equipment} | Bag: {me.inventory} | Vows: {me.vows or 'none'}")
            out(f"   Record: {me.crimes.summary()} | Kills: {me.kills} | {left:.1f} days until technique removal")
        elif cmd == "go" and rest and rest[0].isdigit():
            pst = puppet_state(me.tech_state["puppets"]) if is_puppeteer(me) else None
            if pst is not None and pst["sel"] is None:
                out("Your body cannot leave the hideout. `deploy` a puppet first.")
            else:
                msg = world.enter(me, int(rest[0]), day())
                out(msg)
                spend = 1.0 if "can't" not in msg else 0.0
                if pst is not None:                       # it is the puppet that walked
                    next(e for e in pst["out"] if e["id"] == pst["sel"])["node"] = me.node
        elif cmd in ("scouts", "send", "order") or (cmd == "recall" and not is_puppeteer(me)):
            kinds = [k for k in ("csm", "ten_shadows") if {"csm": "cursed_spirit_manipulation"}.get(k, k) in me.techniques]
            if not kinds:
                out("Only spirit manipulators and Ten Shadows users can send something out.")
                continue
            mine = scouts_of(me)
            key = rest[0].lower() if rest else ""
            pick = next(((k, e, n) for k, e, n in mine if str(e["id"]) == key), None)
            if cmd == "scouts":
                for k in kinds:
                    st = scout_state(me.tech_state, k)
                    gone = {e["id"] for e in st["out"]}
                    if k == "csm":
                        ready = [f"{s['id']}: {s['name']}" for s in st["spirits"] if s["id"] not in gone]
                        out("Stored spirits (each has its own cursed energy): " + (", ".join(ready) or "none"))
                    else:
                        ready = [f"{x}: {SHIKIGAMI[x].name}" for x, v in st["roster"].items() if v == "tamed" and x not in gone]
                        out("Tamed shikigami in your shadow (they run on YOUR cursed energy): " + (", ".join(ready) or "none"))
                for kind, e, name in mine:
                    out(f"  {e['id']}: {name} ({kind}, {'auto' if e.get('auto') else 'manual'}, {e['hp']:.0%}) sees "
                        + sight(e["node"]))
                if not mine:
                    out("  Nothing is out. `send <id>` releases one where you stand.")
            elif cmd == "send":
                st_c = scout_state(me.tech_state, "csm") if "csm" in kinds else None
                st_s = scout_state(me.tech_state, "ten_shadows") if "ten_shadows" in kinds else None
                spirit = st_c and next((s for s in st_c["spirits"] if str(s["id"]) == key), None)
                auto = len(rest) > 1 and rest[1].lower() == "auto"
                if pick is not None:
                    out("That one is already out.")
                elif spirit:
                    if len(st_c["out"]) >= 3:
                        out("You can keep three spirits in the field at most.")
                    else:
                        st_c["out"].append({"id": spirit["id"], "node": me.node, "auto": auto, "hp": 1.0})
                        out(f"You spit out the orb. {spirit['name']} unfolds and waits for orders"
                            + (" - then lopes off to hunt." if auto else "."))
                elif st_s and st_s["roster"].get(key) == "tamed":
                    if len(st_s["out"]) >= (3 if me.level >= 12 else 2):
                        out("You cannot hold that many shikigami in the world at once.")
                    else:
                        st_s["out"].append({"id": key, "node": me.node, "auto": auto, "hp": 1.0})
                        out(f"{SHIKIGAMI[key].name} rises out of your shadow"
                            + (" and slips away to hunt." if auto else " and waits for orders."))
                else:
                    out("You have nothing by that id to send. See `scouts`.")
            elif pick is None:
                out("Nothing of yours is out under that id. See `scouts`.")
            elif cmd == "recall":
                kind, e, name = pick
                if kind == "spirit" and e["node"] != me.node:
                    out(f"{name} has to come back to you first (it is at node {e['node']}).")
                else:
                    scout_state(me.tech_state, "csm" if kind == "spirit" else "ten_shadows")["out"].remove(e)
                    out(f"{name} " + ("is swallowed again." if kind == "spirit" else "sinks back into your shadow."))
            else:                                         # order <id> <node|auto|manual>
                kind, e, name = pick
                what = rest[1].lower() if len(rest) > 1 else ""
                if what in ("auto", "manual"):
                    e["auto"] = what == "auto"
                    out(f"{name} " + ("will hunt on its own." if e["auto"] else "holds until you order it."))
                elif what.isdigit() and int(what) in world.nodes[e["node"]].edges:
                    e["node"], e["auto"] = int(what), False
                    out(f"{name} moves. It sees: {sight(e['node'])}")
                    spend = 1.0
                else:
                    out(f"`order {e['id']} <node>` (one of {world.nodes[e['node']].edges}), or auto / manual.")
        elif cmd in ("deploy", "puppets", "puppet", "recall"):
            if not is_puppeteer(me):
                out("Only a puppeteer has puppets.")
                continue
            pst = puppet_state(me.tech_state["puppets"])
            cur_p = next((e for e in pst["out"] if e["id"] == pst["sel"]), None)
            if cmd == "puppets":
                out(f"Body: hideout at node {me.hideout}. In the hideout: {pst['stock']} puppet(s). "
                    f"Banked cursed energy: {pst['bank']:.0f}.")
                for e in pst["out"]:
                    out(f"  {'>' if e['id'] == pst['sel'] else ' '} Puppet Mk.{e['id']}  node {e['node']}: "
                        f"{world.nodes[e['node']].name}  ({e['hp']:.0%} intact)")
                if not pst["out"]:
                    out("  No puppet is out. `deploy` one to move through the colony.")
            elif cmd == "deploy":
                if pst["stock"] <= 0 or len(pst["out"]) >= 3:
                    out("No puppet left to send (3 at most; `rest` in the hideout rebuilds wrecked ones).")
                else:
                    pst["stock"] -= 1
                    charge = min(pst["bank"], PUPPET_CHARGE)      # banked energy goes into the puppet
                    pst["bank"] -= charge
                    pst["out"].append({"id": pst["next"], "node": me.hideout, "hp": 1.0, "charge": charge})
                    pst["sel"], pst["next"] = pst["next"], pst["next"] + 1
                    out(f"Puppet Mk.{pst['sel']} walks out of the hideout. You are steering it now.")
            elif cmd == "puppet":
                pick = next((e for e in pst["out"] if rest and rest[0].lstrip("mk.#") == str(e["id"])), None)
                if pick is None:
                    out("No such puppet out there. See `puppets`.")
                else:
                    pst["sel"] = pick["id"]
                    out(f"You are steering Puppet Mk.{pick['id']} at node {pick['node']}.")
            elif cur_p is None or cur_p["node"] != me.hideout:
                out("Walk the puppet back to your hideout first.")
            else:
                pst["out"].remove(cur_p)
                pst["stock"] += 1
                out(f"Puppet Mk.{cur_p['id']} is back on its rack.")
            steer(me)
        elif cmd in ("break", "loot") and rest and rest[0].lstrip("#").isdigit():
            out(world.interact(me, int(rest[0].lstrip("#")), cmd, day()))
        elif cmd == "wait":
            spend = float(rest[0]) if rest and rest[0].replace(".", "", 1).isdigit() else 1.0
        elif cmd == "rest":
            if node.kind != "hideout":
                out("You can only rest in a hideout.")
            elif is_puppeteer(me) and me.node != me.hideout:
                out("That is someone else's bolt-hole. Your body, and your workshop, are at "
                    f"node {me.hideout}.")
            else:
                me.hideout = me.node
                if is_puppeteer(me):                      # rebuild what was wrecked
                    pst = puppet_state(me.tech_state["puppets"])
                    pst["stock"] = 3 - len(pst["out"])
                out("You bar the door. This is your hideout now; wandering curses won't find you here. "
                    "You can change cursed tools here. Your wounds stay as they are.")
                spend = 8.0
        elif cmd in ("heal", "treat") and is_puppeteer(me) and me.node != me.hideout:
            out("A puppet cannot be healed, and it cannot heal. Your body is back in the hideout.")
        elif cmd == "heal":
            who = me if not rest else next((p for p in players if p.node == me.node and p is not me
                                            and p.name.lower().startswith(rest[0].lower())), None)
            if who is None:
                out("No such player at this node.")
            elif not who.injured:
                out(f"{who.name} is unhurt.")
            elif who is me and not me.can_self_heal:
                out("You have no way to heal yourself. Track down the medic (`medic`) or a player who can "
                    "output reverse cursed energy.")
            elif who is not me and not me.can_heal_others:
                out("You can't output reverse cursed energy into someone else (level 12 with Shrine or Copy only).")
            elif who is not me and who.pclass == PClass.CURSED_SPIRIT:
                out("Reverse cursed energy would destroy a cursed spirit, not mend it.")
            else:
                if who is me:                             # curses rebuild with cursed energy, sorcerers with RCT
                    who.mend(0.3 if me.pclass == PClass.CURSED_SPIRIT else 0.4, 1)
                else:
                    who.mend(0.25, 1)
                out(f"An hour of concentration. {who.name}: {who.condition_text()}")
                spend = 1.0
        elif cmd == "medic":
            out(world.medic_rumour(me.node, exact=colony.has("score_board")))
        elif cmd == "treat":
            if world.medic != me.node:
                out("The medic isn't here. " + world.medic_rumour(me.node, exact=colony.has("score_board")))
            elif me.pclass == PClass.CURSED_SPIRIT:
                out("The medic works with reverse cursed energy. It would kill you.")
            elif not me.injured:
                out("The medic looks you over: nothing to fix.")
            elif not me.mendable:
                out("The medic shakes their head. The body is fine; the damage is to your soul, and no "
                    "reverse cursed technique reaches that.")
            else:
                me.mend(1.0, 4)
                me.mend(1.0)
                out("The medic works in silence: limbs regrown, wounds closed."
                    + (" The scars on your soul are beyond them." if me.injured else " You are whole again."))
                spend = 1.0
        elif cmd in ("equip", "unequip", "stash") and rest:
            key = rest[0].lower()
            it = ITEMS.get(key)
            worn = ITEMS.get(me.equipment.get(key) or "") if cmd == "unequip" and key in me.equipment else it
            if me.hideout != me.node and not (worn is not None and worn.mundane and cmd != "stash"):
                out("Cursed tools can only be changed in your own hideout (`rest` in a hideout to claim it).")
            elif cmd == "unequip":
                slot = key if key in me.equipment else it.slot if it and me.equipment.get(it.slot) == key else None
                if not slot or not me.equipment.get(slot):
                    out("Nothing equipped there.")
                elif slot == "weapon" and "tool_devotion" in me.vows:
                    out("Your binding vow forbids putting this tool down.")
                else:
                    me.inventory.append(me.equipment[slot])
                    me.equipment[slot] = None
                    out(f"You put away your {slot}.")
            elif not it or it.slot in ("object", "supply") or key not in me.inventory:
                out("You don't have that in your bag to equip.")
            elif cmd == "stash":
                if "copy" not in me.techniques or it.slot != "weapon":
                    out("Only a Copy user can store weapons in Rika's vault.")
                else:
                    me.inventory.remove(key)
                    me.tech_state.setdefault("copy", {"stored": [], "tools": []})["tools"].append(key)
                    out(f"Rika swallows the {it.name}. You can draw it during a full manifestation.")
            elif it.slot == "weapon" and "tool_devotion" in me.vows:
                out("Your binding vow forbids wielding another tool.")
            else:
                me.inventory.remove(key)
                if me.equipment.get(it.slot):
                    me.inventory.append(me.equipment[it.slot])
                me.equipment[it.slot] = key
                out(f"You equip the {it.name}.")
        elif cmd == "fingers":
            held = me.inventory.count("sukuna_finger")
            out(f"You carry {held} of Sukuna's fingers and have caged {me.fingers}. "
                + ("Your body is a strong vessel." if me.vessel >= 20 else "Whether your body can take another, nobody can say."))
            out(f"Finger Bearers still lurking in this colony: {world.fingers_left()}. They are special-grade curses "
                "and stay where they are; kill one and its finger is yours.")
            for r in world.roamers:
                if r.kind == "bearer" and not r.respawn_at and (colony.has("score_board") or world.hops(me.node, r.node) <= 2):
                    out(f"   One lurks at node {r.node}: {world.nodes[r.node].name} ({world.hops(me.node, r.node)} away).")
            if world.sukuna():
                k = world.sukuna()
                body = f", in {k.host}'s body" + (" - a Ten Shadows body" if "ten_shadows" in k.vessel else "") if k.host else ""
                out(f"   SUKUNA walks this colony with {k.fingers} finger(s){body}. He is gathering the rest, and he "
                    f"was last seen at node {k.node}.")
        elif cmd == "eat" or (cmd == "use" and rest and rest[0].lower() == "sukuna_finger"):
            if "sukuna_finger" not in me.inventory:
                out("You have none of Sukuna's fingers.")
            else:
                me.inventory.remove("sukuna_finger")
                if "sukuna_finger" in me.looted:
                    me.looted.remove("sukuna_finger")
                if me.fingers + 1 > me.vessel:                # more than this body can cage
                    total = me.fingers + 1 + me.inventory.count("sukuna_finger")
                    out(f"\n!!! You swallow the finger. It is more than your body can cage. Markings spread across "
                        f"your face, a second pair of eyes opens beneath your own - and {me.name} is gone.")
                    out(f"!!! SUKUNA walks {colony.name} with {total} finger(s). He will gather the rest: the Finger "
                        f"Bearers first, then anyone carrying or caging one.")
                    me.alive, me.fingers = False, 0
                    world.roamers.append(Roamer(max(r.rid for r in world.roamers) + 1, int(Grade.SPECIAL), me.node,
                                                kind="sukuna", fingers=total, vessel=vessel_techniques(me.techniques),
                                                host=me.name, body_hp=float(me.to_spec().stats[Stat.MAX_HP])))
                    if "ten_shadows" in me.techniques:
                        out("!!! Yours was a Ten Shadows body. Every shikigami is his now, Mahoraga with them - and "
                            "with Mahoraga, in time, the slash that cuts the world.")
                else:
                    me.fingers += 1
                    out(f"You swallow the finger, and your body cages it. Sukuna's cursed energy runs under everything "
                        f"you do now: +{10 * me.fingers}% output and strength, +{25 * me.fingers} cursed energy.")
        elif cmd == "search":
            out(world.search(me, day()))
            spend = 1.0
        elif cmd == "use" and rest:
            it = ITEMS.get(rest[0].lower())
            if not it or it.key not in me.inventory or it.slot not in ("supply", "object"):
                out("You don't have that to use.")
            elif it.slot == "object":
                out("A cursed object is consumed in battle (`item`).")
            elif not me.mendable:
                out("You have no wounds it would help.")
            else:
                me.inventory.remove(it.key)
                me.mend(it.params["heal"] / float(me.to_spec().stats[Stat.MAX_HP]))
                out(f"You use the {it.name}. {me.condition_text()}")
        elif cmd in ("shop", "market"):
            out(f"The colony's only shop is at node {world.shop}: {world.nodes[world.shop].name}."
                + ("" if node.kind == "shop" else " You have to be there to trade."))
            if cmd == "shop":
                for it in ITEMS.values():
                    if it.shop:
                        out(f"  {it.key:<18} buy {it.cost:>3}  sell {it.cost // 2:>3}  {it.name} [{it.kind}] {it.desc}")
            out("Offered by other players (`buy #<n>`):" if colony.market else "No player has anything up for sale.")
            for n, offer in enumerate(colony.market, 1):
                who = next((p.name for p in players if p.user_id == offer["seller"]), "someone gone")
                out(f"  #{n} {ITEMS[offer['item']].name:<26} {offer['price']:>5} pts   from {who}"
                    + ("  (taken from the dead)" if offer["looted"] else ""))
        elif cmd == "unlist" and rest and rest[0].lstrip("#").isdigit():
            n = int(rest[0].lstrip("#")) - 1
            if not 0 <= n < len(colony.market) or colony.market[n]["seller"] != me.user_id:
                out("That is not one of your offers. See `market`.")
            elif node.kind != "shop":
                out(f"The colony's only shop is at node {world.shop}.")
            else:
                offer = colony.market.pop(n)
                me.inventory.append(offer["item"])
                if offer["looted"]:
                    me.looted.append(offer["item"])
                out(f"You take the {ITEMS[offer['item']].name} back.")
        elif cmd in ("buy", "sell") and rest:
            key = rest[0].lower()
            it = ITEMS.get(key)
            if node.kind != "shop":
                out(f"The colony's only shop is at node {world.shop}.")
            elif cmd == "buy" and key.startswith("#") and key[1:].isdigit():      # another player's offer
                n = int(key[1:]) - 1
                offer = colony.market[n] if 0 <= n < len(colony.market) else None
                if offer is None:
                    out("No such offer. See `market`.")
                elif offer["seller"] == me.user_id:
                    out("That is your own offer (`unlist` takes it back).")
                elif me.points < offer["price"]:
                    out(f"That costs {offer['price']} points; you have {me.points}.")
                else:
                    colony.market.pop(n)
                    me.points -= offer["price"]
                    seller = next((p for p in players if p.user_id == offer["seller"]), None)
                    if seller is not None:                # a sale is not a score: no clock reset
                        seller.points += offer["price"]
                    me.inventory.append(offer["item"])
                    out(f"Bought {ITEMS[offer['item']].name} for {offer['price']} points"
                        + (f" from {seller.name}." if seller else "."))
            elif not it:
                out("No such item. See `shop`.")
            elif cmd == "buy":
                if not it.shop:
                    out("The shop does not stock that.")
                elif me.points < it.cost:
                    out(f"{it.name} costs {it.cost} points; you have {me.points}.")
                else:
                    me.points -= it.cost
                    me.inventory.append(it.key)
                    out(f"Bought {it.name}. It's in your bag"
                        + ("; consume it in battle with `item`." if it.slot == "object"
                           else "; equip it in your hideout."))
            elif it.key not in me.inventory:
                out("That isn't in your bag. (Something equipped has to come off in your hideout first.)")
            elif it.mundane:
                out("The shop deals only in cursed tools and cursed objects.")
            elif len(rest) == 1:                          # straight to the shopkeeper
                me.inventory.remove(it.key)
                if it.key in me.looted:
                    me.looted.remove(it.key)
                me.points += it.cost // 2                # a sale is not a score: the 19-day clock keeps running
                out(f"Sold {it.name} for {it.cost // 2} points.")
            elif not rest[1].isdigit() or int(rest[1]) < 1:
                out("`sell <item> <price>` - the price is a whole number of points.")
            else:                                         # offered to other players at your price
                price, looted = int(rest[1]), it.key in me.looted
                if not looted and price > 2 * it.cost:
                    out(f"You may ask at most {2 * it.cost} for a {it.name} (double its shop price of {it.cost}). "
                        f"Only tools taken from the dead can go for any price.")
                else:
                    me.inventory.remove(it.key)
                    if looted:
                        me.looted.remove(it.key)
                    colony.market.append({"seller": me.user_id, "item": it.key, "price": price, "looted": looted})
                    out(f"Your {it.name} is up for {price} points. It stays yours until someone buys it.")
        elif cmd == "rules":
            for r in RULES.values():
                out(f"  {'[ADDED]' if colony.has(r.key) else f'{r.cost:>3} pts'}  {r.key:<16} {r.desc}")
        elif cmd == "addrule" and rest:
            out(buy_rule(colony, me, rest[0].lower()))
        elif cmd == "give" and len(rest) == 2 and rest[1].isdigit():
            other = next((p for p in players if p.name.lower().startswith(rest[0].lower()) and p is not me), None)
            err = transfer_points(colony, me, other, int(rest[1]), now) if other else "No such player."
            out(err or f"Transferred {rest[1]} points to {other.name}.")
        elif cmd == "players":
            for i, p in enumerate(players, 1):
                out(f"  {i}) {p.name} L{p.level} @ node {p.node}" + (f", {p.points} pts" if colony.has("score_board") or p is me else ""))
        elif cmd == "switch" and rest and rest[0].isdigit():
            cur = int(rest[0]) - 1
        elif cmd == "new":
            new_player()
        elif cmd == "pvp" and rest:
            foe = next((p for p in players if me.node in where(p) and p is not me
                        and p.name.lower().startswith(rest[0].lower())), None)
            if foe is None:
                out("No such player at this node.")
            else:
                me.crimes.add(Crime.ASSAULT, me.node, day())
                fight([(present(me, me.node), 0), (present(foe, me.node), 1)], me.node, f"{me.name} attacks {foe.name}!")
                spend = 1.0
        else:
            out("Unknown command. Type `help`.")

        while spend > 0:                                  # the world moves an hour at a time
            step = min(1.0, spend)
            spend -= step
            now += step * 3600
            for p in players:
                st = p.tech_state.get("puppets")
                if st is not None:                        # the restricted body stores energy over time
                    st["bank"] = min(400.0, st["bank"] + 40 * step / 24)
            hunted = {r.node for r in world.roamers if not r.respawn_at}
            for p in players:                             # scouts on auto go looking for curses
                for kind, e, name in scouts_of(p):
                    if e.get("auto") and e["node"] not in hunted:
                        step = world._step_toward(e["node"], hunted)
                        ways = [x for x in world.nodes[e["node"]].edges if world.nodes[x].kind != "hideout"]
                        e["node"] = step if step is not None else int(rng.choice(ways)) if ways else e["node"]
            found = [SimpleNamespace(node=n, alive=True, fingers=p.fingers + p.inventory.count("sukuna_finger"))
                     for p in players if p.alive for n in where(p)]
            fights = world.tick(found, now, rng)
            for line in world.news:                       # what Sukuna has been doing
                out("\n!!! " + line)
            world.news.clear()
            for nid, roamers in fights:
                party = [p for p in players if p.alive and nid in where(p)]
                if not party:
                    continue
                specs = [world.spec_for(r, rng) for r in roamers]
                added = fight([(present(p, nid), 0) for p in party] + [(s, 50) for s in specs], nid,
                              f"Curses close in at {world.nodes[nid].name}: " + ", ".join(s.name for s in specs))
                for r, c in zip(roamers, added[len(party):]):
                    if not c.alive:
                        world.defeat(r, now, rng)
                    elif r.kind == "sukuna":              # he keeps whatever he took back, and what he learned
                        r.fingers = c.inventory.count("sukuna_finger")
                        r.slash = r.slash or bool(c.tech_state.get("ten_shadows", {}).get("world_slash"))
                spend = 0
            for p in enforce_inactivity(players, colony, now):
                out(f"\n!!! {p.name}'s score has not changed in {colony.inactivity_days} days. "
                    f"Their cursed technique is removed. {p.name} is dead.")
        save()


# ---- demos: scripted AI showcases ----------------------------------------------------
def _demo_battle(seed, sides, objects=True):
    b = Battle("demo", seed=seed, colony=Colony("demo", rules=["point_transfer"]))
    for spec, team in sides:
        b.add(spec, team)
    if objects:
        standard_field(b)
    return b


def demo(which: str = "all", out=print) -> None:
    rng = np.random.default_rng(1)
    shows = {
        "court": ("Deadly Sentencing vs. a Shrine user with blood on their hands",
                  lambda: _demo_battle(11, [(npc_fighter("Higuruma", PClass.SORCERER, 9, "deadly_sentencing", rng), 0),
                                            (npc_fighter("Curse User", PClass.REINCARNATED, 7, "shrine", rng), 1)])),
        "comedian": ("Comedian vs. a Grade 1 curse",
                     lambda: _demo_battle(5, [(npc_fighter("Takaba", PClass.SORCERER, 8, "comedian", rng), 0),
                                              (npc_spirit(Grade.G1, rng), 1)])),
        "gamble": ("Idle Death Gamble vs. a Special Grade",
                   lambda: _demo_battle(3, [(npc_fighter("Hakari", PClass.SORCERER, 10, "idle_death_gamble", rng), 0),
                                            (npc_spirit(Grade.SPECIAL, rng, tech="disaster_flames"), 1)])),
        "shadows": ("Ten Shadows (veteran) vs. Shrine: merges, totality, the wheel",
                    lambda: _demo_battle(8, [(npc_fighter("Shadow User", PClass.REINCARNATED, 12, "ten_shadows", rng,
                                                          tech_state=tame_all({}, mahoraga=True)), 0),
                                             (npc_fighter("Curse User", PClass.REINCARNATED, 12, "shrine", rng), 1)])),
        "spirits": ("Cursed Spirit Manipulation vs. three curses",
                    lambda: _demo_battle(4, [(npc_fighter("Geto", PClass.SORCERER, 11, "cursed_spirit_manipulation", rng), 0),
                                             (npc_spirit(Grade.G3, rng), 1), (npc_spirit(Grade.G2, rng), 1),
                                             (npc_spirit(Grade.SEMI1, rng), 1)])),
        "soul": ("Soul manipulation vs. a blunt sorcerer and a zero-energy fighter",
                 lambda: _demo_battle(6, [(npc_fighter("Patchwork Curse", PClass.CURSED_SPIRIT, 9, "idle_transfiguration", rng), 0),
                                          (npc_fighter("Rookie", PClass.SORCERER, 4, "comedian", rng), 1),
                                          (npc_fighter("Zero", PClass.SORCERER, 8, "heavenly_restriction", rng, weapon="playful_cloud"), 1)])),
        "copy": ("Copy + Rika vs. a Death Painting",
                 lambda: _demo_battle(9, [(npc_fighter("Copy User", PClass.SORCERER, 10, "copy", rng), 0),
                                          (npc_fighter("Choso", PClass.MUTANT, 9, "blood_manipulation", rng), 1)])),
        "amber": ("Mythical Beast Amber vs. a Special Grade",
                  lambda: _demo_battle(13, [(npc_fighter("Kashimo", PClass.REINCARNATED, 10, "mythical_beast_amber", rng), 0),
                                            (npc_spirit(Grade.SPECIAL, rng, tech="disaster_flames"), 1)])),
        "boogie": ("Boogie Woogie and a partner vs. two Shrine users",
                   lambda: _demo_battle(14, [(npc_fighter("Todo", PClass.SORCERER, 10, "boogie_woogie", rng), 0),
                                             (npc_fighter("Partner", PClass.MUTANT, 8, "blood_manipulation", rng), 0),
                                             (npc_fighter("Curse User A", PClass.REINCARNATED, 8, "shrine", rng), 1),
                                             (npc_fighter("Curse User B", PClass.REINCARNATED, 8, "shrine", rng), 1)])),
        "puppets": ("Remote puppeteer vs. a body hopper",
                    lambda: _demo_battle(2, [(npc_fighter("Puppeteer", PClass.SORCERER, 8, "puppet_manipulation", rng), 0),
                                             (npc_fighter("Body Hopper", PClass.REINCARNATED, 10, "body_hop", rng), 1),
                                             (npc_fighter("Bystander", PClass.SORCERER, 1, "deadly_sentencing", rng), 2)])),
    }
    for key, (title, build) in shows.items():
        if which in ("all", key):
            out(f"\n\n################ DEMO: {title} ################")
            b = build()
            b.io = CliIO(out=out)
            b.run()
    if which not in shows and which != "all":
        out("Demos: all, " + ", ".join(shows))


def main(argv: list) -> None:
    mode = argv[0] if argv else ""
    if mode == "demo":
        return demo(argv[1] if len(argv) > 1 else "all")
    if mode == "arena":
        return arena()
    if mode == "colony":
        return colony_mode(server_id=argv[1] if len(argv) > 1 else "local")
    print("CULLING GAME\n  1) Arena - set up a fight and play it\n  2) Colony - map, roaming curses, saved characters"
          "\n  3) Demo - watch AI showcase fights")
    choice = input("choice [1]> ").strip()
    {"2": colony_mode, "3": demo}.get(choice, arena)()
