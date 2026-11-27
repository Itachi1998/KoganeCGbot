"""NPC decision making: pick an action, a target, a body part and a reaction."""
from __future__ import annotations

from .constants import LIMBS, STALEMATE_ROUNDS, Kind, Part, PClass, PState, React, Stat, Status, Target



PART_WEIGHT = {Part.TORSO: 0.45, Part.HEAD: 0.15, Part.L_ARM: 0.1, Part.R_ARM: 0.1,
               Part.L_LEG: 0.1, Part.R_LEG: 0.1, Part.EXTRA_1: 0.05, Part.EXTRA_2: 0.05}


def _domain_threat(b, c) -> bool:
    """A lethal sure-hit is bearing down on c right now."""
    return (b.rival is None and b.domain is not None and b.domain.data.get("lethal", True)
            and b.domain_reaches(b.domain, c))           # (an ally's domain can reach you too: Malevolent Shrine)


def _domain_coming(b, c, enemies) -> bool:
    """...or c has read an enemy gathering one."""
    return any(e.pending and e.pending.act.kind == Kind.DOMAIN and c.cid in e.pending.seen for e in enemies)


def _kept_up(b, c):
    """A defence this fighter simply keeps running (Infinity), if it has lapsed and would help."""
    foes = b.enemies(c)
    if _domain_threat(b, c) or b.sure_hit_owner() == c.root.cid or (foes and all(e.has(Status.STUN) for e in foes)):
        return None                                     # it does not stop a sure-hit; and nobody stunned is a threat
    return next((a for a in b.actions_for(c) if a.params.get("keep_up") and b.why_cant(c, a) is None
                 and not all(c.has(st) for st, *_ in a.statuses)), None)


SHELLS = ("normal", "reinforced", "miniature")


def _shell(b, c) -> str:
    """How an NPC that can set its barrier's conditions builds the next one. It starts with an
    ordinary barrier, and moves on when one has failed: a shell torn open from outside is
    reinforced next time; if that does not win either, the barrier is shrunk."""
    have = [a.params.get("shell", "normal") for a in b.actions_for(c)
            if a.kind == Kind.DOMAIN and b.why_cant(c, a) is None]
    failed = c.meta.get("shell_failed", [])
    facing_open = any(d.data.get("open") and b.hostile(c, b.by_cid[d.owner]) for d in b.domains())
    for s in SHELLS:
        if s in have and s not in failed and not (s == "normal" and facing_open and len(have) > 1):
            return s
    return max(have, key=SHELLS.index) if have else "normal"


def _wants_wheel(b, c, enemies) -> bool:
    """Everyone is behind Infinity, nothing of this fighter's has adapted to it, and Mahoraga's
    wheel is there to be borne: put it overhead and let it learn."""
    from . import effects
    return bool(enemies and all(e.has(Status.INFINITY) for e in enemies) and c.channeling != "mahoraga"
                and "ten_shadows" in c.techniques and "mahoraga" in effects._free_tamed(b, c)
                and not any(b.adapt_pierce(c, e) >= 1.0 for e in enemies))


def answer_domain(b, c, new, opts):
    """An enemy's domain is opening this instant: expand against it? (None = no.)"""
    if not new.data.get("lethal", True):
        return None                                     # a court or a pachinko hall harms nobody by itself
    want = _shell(b, c)
    return next((a for a in opts if a.params.get("shell", "normal") == want), opts[0])


def _walled_off(b, c, a, enemies) -> bool:
    """Every enemy stands behind Infinity and this attack has no way through it."""
    if not all(e.has(Status.INFINITY) for e in enemies):
        return False
    w = c.weapon
    return not (b.sure_hit_owner() == c.root.cid or c.has(Status.AMPLIFY) or a.effect == "world_slash"
                or (a.effect == "weapon_strike" and w and "nullify" in w.flags)
                or any(b.adapt_pierce(c, e) >= 1.0 for e in enemies))


def score(b, c, a, enemies, hpf) -> float:
    k = a.kind
    if k == Kind.ATTACK:
        if not enemies:
            return 0.0
        if _walled_off(b, c, a, enemies):
            return 1.0                                   # it would only stop in the air
        if a.key == "execute":
            return 100.0
        if a.key == "funeral_hold":                  # worth it only on someone already frozen
            return 34.0 if any(e.has(Status.STUN) for e in enemies) else 0.0
        if "ai" in a.params:
            return a.params["ai"]
        if a.effect == "flesh_bomb":
            from .effects import REGROW_PER_CE
            if b.part_hp[c.idx, Part.HEAD] - a.params["price"] < 0.5 * b.part_max[c.idx, Part.HEAD]:
                return 0.0                               # not at the price of its own head
            if b.ce_pool(c) < b.costs(c, a)[0] + a.params["price"] / REGROW_PER_CE + 10:
                return 0.0                               # nor one it cannot afford to grow back, with something over
        if a.key == "weapon":
            w = c.weapon
            return a.power + w.power + 0.5 * w.params.get("str_scale", 0) * c.stat(Stat.STR) + 4
        if a.target == Target.ALL_ENEMIES:
            return a.power * min(len(enemies), 3) * 0.7
        return a.power + 4
    if k == Kind.HEAL:
        if a.effect == "heal_other":                     # mend whichever ally is worst off
            allies = [o for o in b.fighters if o.alive and o.team == c.team and o is not c
                      and o.pclass != PClass.CURSED_SPIRIT and o.kind != "puppet"]
            worst = min((o.hp / max(o.max_hp, 1) for o in allies), default=1.0)
            return 60 * (1 - worst) if worst < 0.5 else 0.0
        if a.effect == "aura_heal":
            team = [o for o in b.fighters if o.alive and o.team == c.team]
            hpf = min(o.hp / max(o.max_hp, 1) for o in team)
        lost = int((b.part_state[c.idx, list(LIMBS)] == PState.DESTROYED).sum())
        return 110 * (1 - hpf) + 20 * lost if (hpf < 0.6 or lost) else 0.0
    if a.key in ("summon_rika", "full_manifestation"):   # Rika comes out when there is no other way
        lost = int((b.part_state[c.idx, list(LIMBS)] == PState.DESTROYED).sum())
        pushed = hpf < 0.5 or lost or c.meta.get("stall", 0) >= 4
        return (45.0 if a.key == "full_manifestation" else 40.0) if pushed and enemies else 0.0
    if k == Kind.DOMAIN:
        if not enemies or b.rival is not None or b.domain_of(c):
            return 0.0
        if a.key == "ds_domain" and not c.meta.get("court_held"):
            return 95.0                                  # the court is how this technique starts a fight
        if a.params.get("shell", "normal") != _shell(b, c):
            return 0.0                                   # (one way of building the barrier at a time)
        if b.domain is None:                             # a sure-hit is also the way past a defence nothing else gets through
            if _domain_coming(b, c, enemies):
                return 95.0                              # expand against the one that is being gathered
            return 75.0 if all(e.has(Status.INFINITY) for e in enemies) else 38.0
        if not b.hostile(c, b.by_cid[b.domain.owner]):
            return 0.0
        return 200.0 if b.domain.rounds >= 1 else 0.0    # worth it only if theirs will still be standing when yours opens
    if k == Kind.SUMMON:
        if a.key == "taming_ritual":                 # the suicidal trump card
            return 35.0 if hpf < 0.25 else 0.0
        return 26.0 if len(b.summons(c)) < 2 else 3.0
    if k == Kind.BUFF:
        if a.effect in ("anti_domain", "amplify", "falling_blossom"):
            threat = _domain_threat(b, c) or _domain_coming(b, c, enemies)      # only worth it against a domain...
            covered = c.has(Status.ANTI_DOMAIN) or c.has(Status.AMPLIFY) or c.has(Status.FBE)
            if threat and not covered:
                return 55.0
            if a.effect == "amplify" and not threat and b.stance(c) is None and any(   # ...or to get through a defence
                    e.has(Status.INFINITY) or e.has(Status.GAG_ARMOR)
                    or ("soul_body" in e.flags and not b.perceives_soul(c)) for e in enemies):
                return 42.0
            return 0.0
        if a.effect:
            return a.params.get("ai", 10)
        if all(c.has(st) for st, *_ in a.statuses):
            return 0.0
        if a.params.get("keep_up"):
            return 130.0 if _kept_up(b, c) is not None else 4.0
        return a.params.get("ai", 16.0)
    if a.effect == "channel_shikigami":              # Infinity in the way and Mahoraga to hand: bear the wheel
        return 85.0 if _wants_wheel(b, c, enemies) else a.params.get("ai", 10)
    if a.key == "black_hole":                        # only when there is nothing left to lose
        return 80.0 if hpf < 0.2 and enemies else 0.0
    if a.key == "amber":                             # the last resort: it costs the user's life
        cornered = hpf < 0.4 or c.meta.get("stall", 0) >= STALEMATE_ROUNDS - 4      # losing, or getting nowhere
        return 75.0 if cornered and enemies else 0.0
    if a.key == "body_hop":                          # only abandon a body that is failing
        return 45.0 if hpf < 0.5 else 0.0
    return a.params.get("ai", 10)


def pick_part(b, c, tgt) -> Part:
    p = tgt.pending
    if p and c.cid in p.seen and b.rng.random() < 0.6:   # read the channel: go for that limb
        live = [q for q in p.parts if tgt.usable(q)]
        if live:
            return Part(live[int(b.rng.integers(len(live)))])
    parts = [q for q in Part if b.part_state[tgt.idx, q] in (PState.OK, PState.STUNNED)]
    w = [PART_WEIGHT[q] for q in parts]
    return Part(parts[int(b.rng.choice(len(parts), p=[x / sum(w) for x in w]))])


def pick(b, c, a, enemies):
    """(target, part, arg) or None when the action has nothing valid to aim at."""
    from . import effects
    check = effects.VALID.get(a.effect)
    ok = (lambda t, arg=None: check(b, c, a, t, arg) is None) if check else (lambda t, arg=None: True)
    rng = b.rng
    t = a.target
    if t == Target.FREE:
        chooser = effects.AI_PICK.get(a.effect)
        return chooser(b, c) if chooser else None
    if t == Target.ENEMY:
        pool = [e for e in enemies if b.can_reach(c, e, a) and ok(e)]
        if not b.carries_ce(c, a):                      # no cursed energy in it: useless against a curse
            pool = [e for e in pool if e.pclass != PClass.CURSED_SPIRIT]
        prey = [e for e in pool if e.cid == c.meta.get("prey")]
        if prey:
            return prey[0], pick_part(b, c, prey[0]), None
        if a.key == "funeral_hold":
            pool = [e for e in pool if e.has(Status.STUN)]
        if not pool:
            return None
        prey = [e for e in pool if e.cid == c.meta.get("ritual_owner")]
        if prey:
            tgt = prey[0]
        elif rng.random() < 0.6:
            tgt = min(pool, key=lambda e: e.hp / max(e.max_hp, 1))
        else:
            tgt = pool[int(rng.integers(len(pool)))]
        return tgt, pick_part(b, c, tgt), None
    if t in (Target.CORPSE, Target.ANY):
        pool = [x for x in b.fighters if x is not c and (x.corpse or (t == Target.ANY and x.alive)) and ok(x)]
        if pool and a.effect == "heal_other":
            return min(pool, key=lambda x: x.hp / max(x.max_hp, 1)), Part.TORSO, None
        return (pool[int(rng.integers(len(pool)))], Part.TORSO, None) if pool else None
    if t == Target.CHOICE:
        opts = [k for k, _ in b.choices(c, a) if ok(None, k)]
        if a.effect == "channel_shikigami" and "mahoraga" in opts and _wants_wheel(b, c, enemies):
            return None, Part.TORSO, "mahoraga"
        return (None, Part.TORSO, opts[int(rng.integers(len(opts)))]) if opts else None
    if t == Target.ALL_ENEMIES and not enemies:
        return None
    return (None, Part.TORSO, None) if ok(None) else None


def _defends(b, c, enemies) -> bool:
    """Decide whether this round goes to a defence rather than an action."""
    rng = b.rng
    guards = [a for a in b.actions_for(c) if a.react is not None and b.why_cant(c, a) is None]
    if not guards or not enemies or b.defence_of(c) is not None:
        return False                                    # nothing to defend with, or a standing defence is up
    if not c.meta.get("court_held") and any(a.key == "ds_domain" and b.why_cant(c, a) is None
                                            for a in b.actions_for(c)):
        return False                                    # the court comes first, whatever is coming
    if _domain_threat(b, c) and not (c.has(Status.ANTI_DOMAIN) or c.has(Status.AMPLIFY) or c.has(Status.FBE)) and any(
            (a.kind == Kind.DOMAIN or a.effect in ("anti_domain", "amplify", "falling_blossom"))
            and a.react is None and b.why_cant(c, a) is None for a in b.actions_for(c)):
        return False                                    # no dodging a sure-hit: answer the domain itself
    if _kept_up(b, c) is not None:
        return False                                    # the wall goes back up before anything else
    hpf = c.hp / max(c.max_hp, 1)
    by = {a.react: a for a in guards}
    cover = by.get(React.COVER)
    if cover and (hpf < 0.6 or rng.random() < 0.25):    # let a summon stand in front, then go back to attacking
        return b.defend(c, cover)
    held = [a for a in guards if a.params.get("hold") and a.react != React.COVER]
    if held and rng.random() < (0.5 if hpf < 0.7 else 0.2):
        return b.defend(c, held[-1])                    # a guard that stays up is worth a round
    seen = [e for e in enemies if e.pending and c.cid in e.pending.seen and c.cid in e.pending.targets
            and e.pending.land_at < b.round]            # ...and it arrives this round, not the next
    seen += [e for e in enemies if c.cid in e.read_by and e.charge >= 18 and rng.random() < 0.5]
    if seen or (hpf < 0.35 and rng.random() < 0.4):     # something big is gathering, or badly hurt
        pool = [a for a in guards if a.react != React.COVER]
        pick = pick_reaction(b, c, seen[0] if seen else enemies[0], pool) if pool else None
        return bool(pick) and b.defend(c, pick)
    return False


def _ranked(b, c, enemies):
    """Everything this fighter could do now, best first, as (action, target, part, chant, arg)."""
    rng = b.rng
    usable = [a for a in b.actions_for(c) if a.react is None and b.why_cant(c, a) is None]
    hpf = c.hp / max(c.max_hp, 1)
    ranked = sorted(((score(b, c, a, enemies, hpf) * rng.uniform(0.75, 1.25), a.key, a) for a in usable),
                    key=lambda x: -x[0])
    for sc, _, a in ranked:
        if sc <= 0:
            break
        choice = pick(b, c, a, enemies)
        if choice is not None:
            target, part, arg = choice
            yield a, target, part, a.can_chant and rng.random() < 0.3, arg


def channel(b, c) -> None:
    """Channel phase for an NPC: settle on what it means to do and gather energy for it."""
    plan = next(_ranked(b, c, b.enemies(c)), None)
    c.meta["intent"] = plan
    if plan is not None and plan[0].channel and b.channel_for(c, plan[0]):
        c.meta["intent_name"] = plan[0].name


def act(b, c) -> None:
    rng = b.rng
    enemies = b.enemies(c)
    if c.has(Status.ANTI_DOMAIN) and c.meta.get("anti_hands") and not _domain_threat(b, c) and not any(
            e.pending and e.pending.act.kind == Kind.DOMAIN and c.cid in e.pending.seen for e in enemies):
        b.drop_stance(c, "lets the hand sign go")       # no domain to answer: free the hands
    if "boogie_woogie" in c.techniques and c.ce > 25 and rng.random() < 0.35:
        plain = [o for o in b.field.values() if not o.imbued]       # prepare something to swap with
        if plain:
            b.imbue(c, plain[int(rng.integers(len(plain)))].fid)
    for s in b.summons(c, "shikigami"):                 # pull a shikigami back before it is destroyed for good
        if s.meta.get("owner_ce") and s.hp < 0.2 * s.max_hp and rng.random() < 0.6:
            b.dismiss(c, s)
    garden = b.domain_of(c)
    if garden is not None and garden.data.get("weight", 0) >= 3:
        b.release_domain(c)                             # one more car would crush him
    if _defends(b, c, enemies):
        return
    wall = _kept_up(b, c)
    if wall is not None and enemies and b.perform(c, wall, None, Part.TORSO, False, None):
        c.meta.pop("intent", None)
        return
    intent = c.meta.pop("intent", None)                 # what it gathered energy for
    if intent is not None and b.perform(c, *intent):
        return
    for plan in _ranked(b, c, enemies):
        if b.perform(c, *plan):
            return
    for e in enemies:                                   # can't reach anyone: close the distance
        if b.elevated(e) and c.pos != e.pos and b.move(c, e.pos):
            return
    if b.elevated(c) and enemies and b.move(c, None):
        return
    b.say(f"{c} waits.")


def pick_reaction(b, tgt, atk, opts):
    by = {a.react: a for a in opts}                     # later (technique) entries win
    rng = b.rng
    perceived = tgt.cid in atk.last_seen
    if rng.random() < 0.1:
        return None
    if React.SWAP in by and rng.random() < 0.7:         # let someone else take it
        return by[React.SWAP]
    if React.COUNTER in by and (perceived or rng.random() < 0.2):
        return by[React.COUNTER]
    if React.DODGE in by and tgt.stat(Stat.SPD) >= atk.stat(Stat.SPD) - 2:
        return by[React.DODGE]
    if React.BLOCK in by:
        return by[React.BLOCK]
    if React.REINFORCE in by and b.ce_pool(tgt) > 15:
        return by[React.REINFORCE]
    return next(iter(by.values()))
