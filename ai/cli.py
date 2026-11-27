"""Command-line front end. No graphics - everything is typed commands."""
from __future__ import annotations

from typing import Optional

import numpy as np

from . import ai, oldstats, vows
from .battle import IO, Battle
from .colony import ColonySession
from .constants import CLASS_NAME, GRADE_NAME, Grade, Kind, Part, PClass, PState, Stat, Status, Target
from .data import ITEMS, PLAYABLE
from .effects import tame_all
from .records import (PlayerRecord, finger_bearer, npc_fighter, npc_spirit, roll_technique, roll_vessel,
                      sukuna_npc)
from .rarity import class_rarity_of, rarity_of, roll_class, roll_six_eyes
from .rules import Colony
from .storage import BattleCache, GameStore
from .techniques import ACTIONS, TECHNIQUES

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
                arg = opts[b.ask(c, f"{act.name}:", [f"{k} - {label}" for k, label in opts])][0]
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
    """``rng`` given: class and technique are rolled at the original bot's odds (rarity.py), the
    way the colony does it. Otherwise both are picked."""
    name = inp("Character name> ").strip() or f"Player {user_id}"
    six_eyes = False
    if rng is not None:
        pclass = roll_class(rng)
        out(f"The culling game makes you a {CLASS_NAME[pclass]} ({class_rarity_of(pclass)}).")
    else:
        pclass = PClass(_pick(inp, out, "Class:", CLASS_NAME))
    techs = PLAYABLE[pclass]
    if rng is not None:
        tech = roll_technique(pclass, rng)
        six_eyes = roll_six_eyes(pclass, tech, rng)
        out(f"You awaken with {TECHNIQUES[tech].name} ({rarity_of(pclass, tech)}) - a "
            f"{GRADE_NAME[TECHNIQUES[tech].grade]} technique. {TECHNIQUES[tech].desc}")
        if six_eyes:
            out("...and you were born with the Six Eyes.")
    else:
        tech = techs[_pick(inp, out, "Innate technique:",
                           [f"[{GRADE_NAME[TECHNIQUES[t].grade]}] {TECHNIQUES[t].name} - {TECHNIQUES[t].desc}" for t in techs])]
    rec = PlayerRecord(server_id, user_id, name, int(pclass), techniques=[tech], six_eyes=six_eyes)
    if rng is not None:                                      # the original bot's stat spin (oldstats.py)
        rec.old_stats = oldstats.roll(pclass, tech, six_eyes, rng)
        out("Your stats: " + ", ".join(f"{k.upper()} {v}" for k, v in rec.old_stats.items()))
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
    """Hot-seat front end over ColonySession (ai/colony.py), which holds the game itself.
    ``prepare(colony, world, players)`` is a hook for tests and scripted scenarios."""
    store, cache = GameStore(), BattleCache()
    out(f"\n=== COLONY MODE (storage: {store.backend}, battle cache: {cache.backend}) ===")
    game = ColonySession(server_id, store, cache, io=CliIO(inp, out), seed=seed, managers=["u1"],
                         battle_banner=BATTLE_HELP)
    players = game.players

    def new_player():
        uid = f"u{len(store.list_players(server_id)) + 1}"
        rec = create_character(inp, out, server_id, uid, rng=None if free_pick else game.rng)
        if not game.add_player(rec, out):
            out("That user already has a character in this colony.")
            return None
        return rec

    if not players and new_player() is None:
        return
    if prepare is not None:
        prepare(game.colony, game.world, players)
    cur = 0
    out(WORLD_HELP)
    while True:
        players[:] = [p for p in players if p.alive]
        if not players:
            out("Everyone is dead. The culling game goes on without you.")
            game.save()
            return
        cur %= len(players)
        me = players[cur]
        game.steer(me)
        node = game.world.nodes[me.node]
        line = inp(f"\n[day {game.day()}] {me.name} @ {node.name} ({me.points} pts)> ")
        tokens = line.split()
        if not tokens:
            continue
        cmd, rest = tokens[0].lower(), tokens[1:]
        if cmd in ("quit", "exit"):
            game.save()
            return
        elif cmd == "help":
            out(WORLD_HELP)
        elif cmd == "save":
            game.save()
            out("Saved.")
        elif cmd == "switch" and rest and rest[0].isdigit():
            cur = int(rest[0]) - 1
        elif cmd == "new":
            new_player()
        else:
            game.command(me, line, out)


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
