"""Colony map: a layered node graph (Slay the Spire style) with roaming enemies.

The map is rebuilt from its seed, so only the *changes* are persisted: one bit per object
for "broken", one for "looted", and the roamers' positions.  Enemies are not pinned to
nodes - every tick they step toward the nearest player, unless that player is in a hideout.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from .constants import DAY, FINGER_BEARERS, GRADE_NAME, Grade
from .crimes import Crime
from .records import finger_bearer, npc_spirit, sorcerer_killer, sukuna_npc

#            name               role         breakable weight power  hp  loot
TEMPLATES = (("Vending Machine", "throwable", True, 13, 20, 30, None),
             ("Parked Car", "throwable", True, 18, 30, 60, None),
             ("Concrete Wall", "cover", True, 0, 0, 50, None),
             ("Rooftop", "elevation", False, 0, 0, 0, None),
             ("Guard Rail", "speed", True, 0, 0, 20, None),
             ("Supply Crate", "cover", True, 0, 0, 15, "cursed_relic"),
             ("Street Sign", "throwable", True, 9, 14, 10, None))
STREETS = ["Crossing", "Underpass", "Arcade Street", "Station Front", "Overpass", "Back Alley", "Plaza"]
BUILDINGS = ["Pachinko Parlour", "Hospital", "Apartment Block", "Theatre", "Stadium", "Mall", "Courthouse"]
NEVER = float(10 ** 15)        # a respawn time that never comes
# Grade 4 to Grade 1 curses have no timer: killed, they re-form at once somewhere far off.
# Special grade and up take time, and Sukuna longest of all.
RESPAWN_HOURS = {"curse": 24, "bearer": 48, "killer": 72, "sukuna": 168}   # special-grade curse / ...
TOTAL_FINGERS = 20             # bearers and Sukuna come back only while fewer than this are in play
FINGER_RECHECK = 6             # hours before trying again when the fingers are all accounted for


@dataclass
class MapObject:
    oid: int
    name: str
    role: str
    breakable: bool
    weight: float
    power: float
    hp: float
    loot: Optional[str]


@dataclass
class Node:
    nid: int
    layer: int
    kind: str                     # street | building | shop | hideout
    name: str
    edges: list = field(default_factory=list)
    objects: list = field(default_factory=list)


@dataclass
class Roamer:
    rid: int
    grade: int
    node: int
    respawn_at: float = 0.0       # 0 = on the map
    kind: str = "curse"           # curse | killer (the Sorcerer Killer) | bearer (finger bearer) | sukuna
    fingers: int = 0              # for Sukuna: how many of his fingers he has gathered
    vessel: list = field(default_factory=list)   # ...the innate technique(s) of the body he took
    host: str = ""                # ...and whose body it was
    slash: bool = False           # ...and whether he has learned the slash that cuts the world
    body_hp: float = 0.0          # ...and that body's maximum HP, which is his
    engaged: bool = False         # in a fight right now (not saved): it neither moves nor joins another

    @property
    def label(self) -> str:
        return {"killer": "the Sorcerer Killer", "bearer": "a Finger Bearer (special grade)",
                "sukuna": f"SUKUNA ({self.fingers} finger{'s' if self.fingers != 1 else ''}"
                          + (f", in {self.host}'s body" if self.host else "") + ")"}.get(
                    self.kind, f"{GRADE_NAME[self.grade]} curse")


class World:
    def __init__(self, seed: int = 0, layers: int = 6):
        self.seed, self.layers = seed, layers
        rng = np.random.default_rng(seed)
        self.nodes: dict[int, Node] = {}
        self.objects: dict[int, MapObject] = {}
        rows = []
        for layer in range(layers):
            row = []
            count = 1 if layer == 0 else int(rng.integers(2, 5))
            kinds = ["street"] if layer == 0 else [str(k) for k in rng.choice(
                ["street", "building", "hideout"], size=count, p=[0.5, 0.33, 0.17])]
            for j in [j for j, k in enumerate(kinds) if k == "hideout"][1:]:
                kinds[j] = "street"                           # hideouts are side rooms: one per layer at most
            for kind in kinds:
                nid = len(self.nodes)
                base = {"street": STREETS, "building": BUILDINGS}.get(kind)
                name = (str(rng.choice(base)) if base else kind.title()) + f" #{nid}"
                node = Node(nid, layer, kind, name)
                for _ in range(int(rng.integers(1, 4)) if kind != "hideout" else 0):
                    t = TEMPLATES[int(rng.integers(len(TEMPLATES)))]
                    oid = len(self.objects)
                    self.objects[oid] = MapObject(oid, *t)
                    node.objects.append(oid)
                self.nodes[nid] = node
                row.append(nid)
            rows.append(row)
        for a, nxt in zip(rows, rows[1:]):                   # every node links forward and is reachable
            for nid in a:
                for m in rng.choice(nxt, size=min(len(nxt), int(rng.integers(1, 3))), replace=False):
                    self._link(nid, int(m))
            for m in nxt:
                if not any(m in self.nodes[x].edges for x in a):
                    self._link(int(rng.choice(a)), m)
            # Roamers never path through hideouts, so the open nodes must connect on their own.
            oa = [x for x in a if self.nodes[x].kind != "hideout"]
            on = [x for x in nxt if self.nodes[x].kind != "hideout"]
            for x in oa:
                if not any(m in self.nodes[x].edges for m in on):
                    self._link(x, int(rng.choice(on)))
            for m in on:
                if not any(x in self.nodes[m].edges for x in oa):
                    self._link(int(rng.choice(oa)), m)
        # Exactly one shop per colony, somewhere in the middle of the map.
        mid = [n for n in self.nodes.values() if n.kind != "hideout" and 0 < n.layer < layers - 1]
        shop = mid[int(rng.integers(len(mid)))]
        shop.kind, shop.name = "shop", f"Cursed Tool Shop #{shop.nid}"
        self.shop = shop.nid
        self.broken = np.zeros(len(self.objects), dtype=bool)
        self.looted = np.zeros(len(self.objects), dtype=bool)
        # One medic per colony. They are not a fighter and never stay put for long.
        self.medic = int(rng.choice([n.nid for n in self.nodes.values() if n.kind != "hideout" and n.layer > 0]))
        open_nodes = [n.nid for n in self.nodes.values() if n.kind != "hideout" and n.layer > 0]
        grades = rng.choice(6, size=layers + 2, p=[0.3, 0.25, 0.2, 0.12, 0.08, 0.05])
        self.roamers = []
        for i, g in enumerate(grades):                        # the deeper the node, the worse the curse
            nid = int(rng.choice(open_nodes))
            self.roamers.append(Roamer(i, min(int(g), self.nodes[nid].layer), nid))
        # One Sorcerer Killer per colony: no cursed energy, and the only Inverted Spear of Heaven.
        # He starts at the far end of the map; kill him and he does not come back.
        deep = max(n.nid for n in self.nodes.values() if n.kind != "hideout")
        self.roamers.append(Roamer(len(self.roamers), int(Grade.SPECIAL), deep, kind="killer"))
        self.roamers += self._bearers(len(self.roamers))
        self.news: list = []                                  # things the colony hears about (Sukuna's progress)
        # Ordinary things lying around, found by searching a node once. Own generator, so the
        # map layout above is unchanged by it.
        finds = np.random.default_rng(seed + 7919)
        self.finds: dict[int, list] = {}
        for n in self.nodes.values():
            pool, count = {"street": (["bat", "knife", "bandage"], finds.integers(0, 2)),
                           "building": (["bandage", "knife", "sword", "bat", "bandage", "gun"],
                                        finds.integers(1, 3))}.get(n.kind, ([], 0))
            self.finds[n.nid] = [str(finds.choice(pool)) for _ in range(int(count))]
        self.searched = np.zeros(len(self.nodes), dtype=bool)

    def _link(self, a: int, b: int) -> None:
        if b not in self.nodes[a].edges:
            self.nodes[a].edges.append(b)
            self.nodes[b].edges.append(a)

    # ---- persistence: only the deltas --------------------------------------------------
    def state(self) -> dict:
        return {"seed": self.seed, "layers": self.layers,
                "broken": np.packbits(self.broken).tobytes(),
                "looted": np.packbits(self.looted).tobytes(),
                "searched": np.packbits(self.searched).tobytes(),
                "roamers": [[r.rid, r.grade, r.node, r.respawn_at, r.kind, r.fingers, list(r.vessel), r.host, r.slash, r.body_hp]
                            for r in self.roamers],
                "medic": self.medic}

    @classmethod
    def from_state(cls, st: dict) -> "World":
        w = cls(int(st["seed"]), int(st["layers"]))
        n = len(w.objects)
        w.broken = np.unpackbits(np.frombuffer(bytes(st["broken"]), dtype=np.uint8))[:n].astype(bool)
        w.looted = np.unpackbits(np.frombuffer(bytes(st["looted"]), dtype=np.uint8))[:n].astype(bool)
        if "searched" in st:
            w.searched = np.unpackbits(np.frombuffer(bytes(st["searched"]), dtype=np.uint8))[:len(w.nodes)].astype(bool)
        killer = [r for r in w.roamers if r.kind == "killer"]
        bearers = [r for r in w.roamers if r.kind == "bearer"]
        w.roamers = [Roamer(int(r[0]), int(r[1]), int(r[2]), float(r[3]), str(r[4]) if len(r) > 4 else "curse",
                            int(r[5]) if len(r) > 5 else 0, list(r[6]) if len(r) > 6 else [],
                            str(r[7]) if len(r) > 7 else "", bool(r[8]) if len(r) > 8 else False,
                            float(r[9]) if len(r) > 9 else 0.0)
                     for r in st["roamers"]]
        if not any(r.kind == "bearer" for r in w.roamers):    # a save from before the fingers
            w.roamers += bearers
        if not any(r.kind == "killer" for r in w.roamers):    # a save from before he existed
            w.roamers += killer
        for r in w.roamers:                                   # killed when one-of-a-kinds never came back:
            if r.respawn_at >= NEVER:                         # they return at the next tick
                r.respawn_at = 1.0
        w.medic = int(st.get("medic", w.medic))
        return w

    def search(self, rec, day: int) -> str:
        """Turn a node over for ordinary things: bandages, knives, bats, the odd gun."""
        if self.searched[rec.node]:
            return "This place has already been picked clean."
        self.searched[rec.node] = True
        found = self.finds.get(rec.node, [])
        if not found:
            return "You search and find nothing worth carrying."
        rec.inventory.extend(found)
        note = ""
        if self.nodes[rec.node].kind == "building":           # it belonged to someone
            rec.crimes.add(Crime.THEFT, rec.node, day)
            note = " (Judgeman takes note.)"
        return "You find: " + ", ".join(found) + "." + note

    # ---- interaction (everything here goes on the player's record) ---------------------
    def mark_broken(self, oid: int) -> None:
        self.broken[oid] = True

    def enter(self, rec, nid: int, day: int) -> str:
        if nid not in self.nodes[rec.node].edges:
            return "You can't get there from here."
        rec.node = nid
        node = self.nodes[nid]
        if node.kind == "building":
            rec.crimes.add(Crime.TRESPASS, nid, day)
            return f"You force your way into {node.name}. (Judgeman takes note.)"
        return f"You arrive at {node.name}."

    def interact(self, rec, oid: int, verb: str, day: int) -> str:
        if oid not in self.nodes[rec.node].objects:
            return "That isn't here."
        obj = self.objects[oid]
        if verb == "break":
            if not obj.breakable or self.broken[oid]:
                return "It can't be broken."
            self.broken[oid] = True
            rec.crimes.add(Crime.VANDALISM, oid, day)
            return f"You smash the {obj.name}. (Judgeman takes note.)"
        if verb == "loot":
            if not obj.loot or self.looted[oid]:
                return "Nothing to take."
            self.looted[oid] = True
            rec.inventory.append(obj.loot)
            rec.crimes.add(Crime.THEFT, oid, day)
            return f"You take a {obj.loot} from the {obj.name}. (Judgeman takes note.)"
        return "You can break or loot objects."

    def field_objects(self, nid: int) -> list:
        """Intact map objects at a node, as keyword dicts for Battle.add_object."""
        return [dict(name=o.name, role=o.role, hp=o.hp or 40, weight=o.weight, power=o.power, oid=o.oid)
                for o in (self.objects[i] for i in self.nodes[nid].objects) if not self.broken[o.oid]]

    # ---- roaming -----------------------------------------------------------------------
    def _step_toward(self, src: int, goals: set, max_hops: int = 2) -> Optional[int]:
        """First step of the shortest hideout-free path from src to any goal within range."""
        seen, queue = {src: None}, deque([(src, 0)])
        while queue:
            cur, dist = queue.popleft()
            if cur in goals and cur != src:
                while seen[cur] != src:
                    cur = seen[cur]
                return cur
            if dist < max_hops:
                for nxt in self.nodes[cur].edges:
                    if nxt not in seen and self.nodes[nxt].kind != "hideout":
                        seen[nxt] = cur
                        queue.append((nxt, dist + 1))
        return None

    def _bearers(self, first_id: int) -> list:
        """Finger-bearing curses: special grade, each grown around one of Sukuna's fingers. They lurk
        where they are (deep in the map) and never come back once killed. Own generator, so the
        rest of the map does not depend on them."""
        gen = np.random.default_rng(self.seed + 4243)
        deep = [n.nid for n in self.nodes.values() if n.kind in ("street", "building") and n.layer >= 2]
        spots = gen.choice(deep, size=min(FINGER_BEARERS, len(deep)), replace=False)
        return [Roamer(first_id + i, int(Grade.SPECIAL), int(nid), kind="bearer") for i, nid in enumerate(spots)]

    def fingers_in_play(self, held: int = 0) -> int:
        """Fingers in bearers, in Sukuna, and (``held``) carried or caged by players."""
        return (self.fingers_left() + sum(r.fingers for r in self.roamers if r.kind == "sukuna" and not r.respawn_at)
                + int(held))

    def _respawn(self, r: Roamer, now: float, rng, open_nodes: list, held: int) -> bool:
        """Bring a defeated roamer back. False when it has to wait (all twenty fingers are taken)."""
        if r.kind in ("bearer", "sukuna") and self.fingers_in_play(held) >= TOTAL_FINGERS:
            r.respawn_at = now + FINGER_RECHECK * 3600
            return False
        if r.kind == "bearer":                                # a new curse grows around a finger, deep in
            deep = [n.nid for n in self.nodes.values() if n.kind in ("street", "building") and n.layer >= 2]
            r.respawn_at, r.node = 0.0, int(rng.choice(deep or open_nodes))
            self.news.append(f"A new Finger Bearer has grown around one of Sukuna's fingers at node {r.node}.")
            return True
        r.respawn_at, r.node = 0.0, int(rng.choice(open_nodes))
        if r.kind == "sukuna":                                # reincarnated again, around one finger
            r.fingers = 1
            self.news.append(f"Sukuna has returned to this colony around a single finger, at node {r.node}.")
        return True

    def fingers_left(self) -> int:
        return sum(1 for r in self.roamers if r.kind == "bearer" and not r.respawn_at)

    def sukuna(self):
        return next((r for r in self.roamers if r.kind == "sukuna" and not r.respawn_at), None)

    def _sukuna_takes(self, r: Roamer) -> None:
        for x in self.roamers:
            if x.kind == "bearer" and not x.respawn_at and x.node == r.node:
                x.respawn_at = NEVER
                r.fingers += 1
                self.news.append(f"Sukuna has torn a finger out of the bearer at node {r.node}. "
                                 f"He holds {r.fingers} now; {self.fingers_left()} bearer(s) remain.")

    def tick(self, players: list, now: float, rng: np.random.Generator, held: int = 0) -> list:
        """Move every roamer one node. Returns [(node id, [roamers])] where a fight starts.
        ``held``: Sukuna's fingers carried or caged by players (respawns keep the total at twenty)."""
        prey = {p.node for p in players if p.alive and self.nodes[p.node].kind != "hideout"}
        open_nodes = [n.nid for n in self.nodes.values() if n.kind != "hideout" and n.layer > 0]
        for r in self.roamers:
            if r.engaged:                                     # busy fighting somebody
                continue
            if r.respawn_at:
                if now < r.respawn_at or not self._respawn(r, now, rng, open_nodes, held):
                    continue
            if r.kind == "bearer":                            # it lurks where it is
                continue
            if r.kind == "sukuna":                            # he goes after his fingers: bearers first, then
                self._sukuna_takes(r)                         # anyone carrying or caging one
                if r.node in prey:
                    continue
                goals = {x.node for x in self.roamers if x.kind == "bearer" and not x.respawn_at}
                goals |= {p.node for p in players if p.alive and getattr(p, "fingers", 0)
                          and self.nodes[p.node].kind != "hideout"}
                step = self._step_toward(r.node, goals or prey, max_hops=99)
                if step is None:
                    options = [e for e in self.nodes[r.node].edges if self.nodes[e].kind != "hideout"]
                    step = int(rng.choice(options)) if options else r.node
                r.node = step
                self._sukuna_takes(r)
                continue
            if r.node in prey:
                continue
            step = self._step_toward(r.node, prey)
            if step is None:                                  # nobody near: wander
                options = [e for e in self.nodes[r.node].edges if self.nodes[e].kind != "hideout"]
                step = int(rng.choice(options)) if options else r.node
            r.node = step
        if rng.random() < 0.5:                                # the medic makes their rounds
            options = [e for e in self.nodes[self.medic].edges if self.nodes[e].kind != "hideout"]
            if options:
                self.medic = int(rng.choice(options))
        fights: dict[int, list] = {}
        for r in self.roamers:
            if not r.respawn_at and not r.engaged and r.node in prey and len(fights.get(r.node, ())) < 3:
                fights.setdefault(r.node, []).append(r)       # at most three join one fight
        return sorted(fights.items())

    def defeat(self, r: Roamer, now: float, rng: np.random.Generator) -> None:
        special = r.kind != "curse" or Grade(r.grade) >= Grade.SPECIAL
        if special:                                           # special grade and up take time to come back
            r.respawn_at = now + RESPAWN_HOURS.get(r.kind, RESPAWN_HOURS["curse"]) * 3600
            if r.kind == "sukuna":                            # what he held is the killer's now
                r.fingers, r.vessel, r.host, r.slash, r.body_hp = 0, [], "", False, 0.0
        else:                                                 # grade 4 to 1: no timer, re-form far away
            far = [n.nid for n in self.nodes.values() if n.kind != "hideout" and n.layer >= self.layers - 2]
            r.node = int(rng.choice(far))

    def spec_for(self, r: Roamer, rng: np.random.Generator):
        if r.kind == "killer":
            return sorcerer_killer(rng)
        if r.kind == "bearer":
            return finger_bearer(rng)
        if r.kind == "sukuna":
            spec = sukuna_npc(r.fingers, rng, r.vessel, r.host, r.slash, r.body_hp)
            spec.meta["roamer_id"] = r.rid
            return spec
        return npc_spirit(Grade(r.grade), rng)

    def hops(self, a: int, b: int) -> int:
        """Shortest walking distance between two nodes."""
        seen, queue = {a}, deque([(a, 0)])
        while queue:
            cur, dist = queue.popleft()
            if cur == b:
                return dist
            for nxt in self.nodes[cur].edges:
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append((nxt, dist + 1))
        return -1

    def medic_rumour(self, at: int, exact: bool = False) -> str:
        """What a player can learn about the medic's whereabouts from where they stand."""
        if at == self.medic:
            return "The medic is right here. (`treat`)"
        d = self.hops(at, self.medic)
        if exact or d == 1:
            return f"The medic is at node {self.medic}: {self.nodes[self.medic].name} ({d} away)."
        closer = [e for e in self.nodes[at].edges if self.hops(e, self.medic) < d]
        return (f"Word is the medic is about {d} nodes from here; the trail leads toward node "
                f"{closer[0]}. They keep moving.")

    def describe(self, at: int) -> str:
        lines = []
        for layer in range(self.layers):
            row = [n for n in self.nodes.values() if n.layer == layer]
            lines.append("  ".join(
                f"{'*' if n.nid == at else ' '}[{n.nid}:{n.kind[:5]}->{','.join(map(str, sorted(e for e in n.edges if self.nodes[e].layer > layer)))}]"
                for n in row))
        return "\n".join(lines)
