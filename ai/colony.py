"""A colony as a game session, independent of any front end.

This is the body of the command-line colony mode, moved into a class so the CLI
(cli.colony_mode) and the Discord bot (ai/bot) run exactly the same game.
``command(me, line, out)`` runs one world command for one player: whatever it reports goes to
``out``, and any fight it starts is played through ``self.io`` (the front end's battle adapter)
and blocks until it is over.  Front ends must not run two commands on one session at once.
"""
from __future__ import annotations

import re
import threading
import time
from types import SimpleNamespace
from typing import Callable, Optional

import numpy as np

from .battle import IO, Battle
from .constants import (PART_HP_FRAC, CLASS_NAME, DAY, GRADE_NAME, Grade, Part, PClass, Stat,
                        REST_RECOVERY, SIX_EYES_RECOVERY, SIX_EYES_REST)
from . import skills
from .crimes import Crime
from .data import ITEMS, SHIKIGAMI
from .effects import PUPPET_CHARGE, scout_state
from .effects import _puppets as puppet_state
from .records import PlayerRecord, grade_for, has_six_eyes, vessel_techniques, xp_to_next
from .rules import RULES, Colony, buy_rule, enforce_inactivity, transfer_points
from .storage import BattleCache, GameStore
from .techniques import TECHNIQUES
from .world import Roamer, World

PART_LABEL = {Part.HEAD: "head", Part.TORSO: "torso", Part.L_ARM: "l.arm", Part.R_ARM: "r.arm",
              Part.L_LEG: "l.leg", Part.R_LEG: "r.leg", Part.EXTRA_1: "limb+1", Part.EXTRA_2: "limb+2"}


NAME_MIN, NAME_MAX = 2, 24


def clean_name(raw) -> tuple:
    """A character name a player typed -> (name, None) or (None, why not). Markdown, mentions and
    line breaks are stripped so a name cannot ping anyone or break the bot's layouts."""
    name = re.sub(r"[`*~|<>@#\\\[\](){}:/]", "", str(raw or "").replace("_", " "))
    name = " ".join(name.split())
    if len(name) < NAME_MIN:
        return None, f"A character's name needs at least {NAME_MIN} letters or digits."
    if len(name) > NAME_MAX:
        return None, f"A character's name can be at most {NAME_MAX} characters."
    if not any(ch.isalnum() for ch in name):
        return None, "A character's name needs letters or digits in it."
    return name, None


class ColonyBusy(RuntimeError):
    """The colony's lock could not be had in time (another process is holding it)."""


LOCK_TTL = 30.0            # seconds the colony lock survives its holder dying mid-command
FIGHT_TTL = 120.0          # seconds a "fighting" / "engaged" mark survives its process dying mid-fight


class ColonySession:
    def __init__(self, server_id: str, store: Optional[GameStore] = None, cache: Optional[BattleCache] = None,
                 io: Optional[IO] = None, seed: Optional[int] = None, name: str = "Tokyo No. 1 Colony",
                 managers=(), battle_banner: Optional[str] = None):
        self.server_id = str(server_id)
        self.store = store or GameStore()
        self.cache = cache if cache is not None else BattleCache()
        self._tls = threading.local()                 # each command thread plays its fights through its own io
        self._default_io = io or IO()
        # Many fights at once, in one process or several. A front end that runs commands on several
        # threads brackets each one with ``acquire()`` / ``release()`` and sets ``concurrent``:
        #   the lock      this process's ``lock``, then the colony's lock in Redis (``cache``), so two
        #                 bot processes never work on one colony at the same moment;
        #   catching up   every save bumps the colony's version in Redis; ``acquire`` reloads the
        #                 colony from the database when another process has saved since (``sync``);
        #   fights        a fight saves, lets go of the lock while it is played and takes it back at
        #                 the end. Its players (``in_battle``) and roamers (``Roamer.engaged``) are
        #                 marked busy in Redis for as long as it lasts (a heartbeat keeps the marks
        #                 alive; they lapse by themselves if the process dies). The process playing
        #                 a fight owns its fighters' records until it ends: nobody else may change them.
        self.lock = threading.Lock()
        self.concurrent = False
        self._name = f"colony:{self.server_id}"
        self._mine: dict = {}                         # user id -> record, for fights THIS process is playing
        self._my_roamers: set = set()                 # roamer ids engaged by this process's fights
        self._sparring: set = set()                   # user ids in a lobby spar played by this process
        self._beat: Optional[threading.Thread] = None
        if getattr(self.store, "coord", None) is None:
            self.store.coord = self.cache             # the store's game-wide items coordinate through it too
        self.battle_banner = battle_banner            # extra text when a fight starts (the CLI prints its help)
        # Front-end hooks (the CLI leaves them as they are; the Discord bot ties fights to lobbies):
        self.can_fight: Callable = lambda p: True     # may this player be attacked / fight at all?
        self.pvp_check: Callable = lambda me, foe: None   # an error message, or None to allow a PvP fight
        self.io_for: Callable = lambda party: self.io     # where a fight involving these players is shown
        # The clock the 19-day rule runs on. The colony's own clock moves with every command anyone
        # gives, which suits one hot-seat table; a server full of players sets this to real time,
        # so nobody else's commands can run a character's 19 days out.
        self.idle_clock: Callable = lambda: self.now
        self.rng = np.random.default_rng(seed)
        token = self.cache.acquire(self._name, ttl=LOCK_TTL, wait=LOCK_TTL)     # (two processes founding it at once)
        try:
            colony = self.store.get_colony(self.server_id)
            if colony is None:
                colony = Colony(self.server_id, name, managers=list(managers),
                                map_seed=int(self.rng.integers(1 << 30)))
                self.store.put_colony(colony)
            self.colony = colony
            saved = self.store.get_map(self.server_id)
            self.world = World.from_state(saved) if saved else World(colony.map_seed)
            self.players = [p for p in self.store.list_players(self.server_id) if p.alive]
            self._ver = self.cache.version(self._name)
        finally:
            self.cache.release(self._name, token)
        self.now = max([time.time(), colony.clock] + [p.last_score_ts for p in self.players])
        for p in self.players:
            self.steer(p)

    @property
    def io(self) -> IO:
        return getattr(self._tls, "io", self._default_io)

    @io.setter
    def io(self, value: IO) -> None:
        self._tls.io = value

    # ---- the lock, and keeping up with other processes ------------------------------------------
    def acquire(self, wait: float = 30.0, keep=()) -> None:
        """Take the colony for one command. Raises ColonyBusy if another process keeps it too long."""
        self.lock.acquire()
        try:
            self._tls.me = getattr(self._tls, "me", None) if keep else None      # (a new command starts clean)
            token = self.cache.acquire(self._name, ttl=LOCK_TTL, wait=wait)
            if token is None:
                raise ColonyBusy(self.server_id)
            self._tls.token = token
            self.sync(keep)
            self._tls.held = True
        except BaseException:
            self.cache.release(self._name, getattr(self._tls, "token", None))
            self._tls.token = None
            self.lock.release()
            raise

    def release(self) -> None:
        """Let the colony go (a no-op if this thread does not hold it)."""
        if not getattr(self._tls, "held", False):
            return
        self._tls.held = False
        token, self._tls.token = getattr(self._tls, "token", None), None
        self.cache.release(self._name, token)
        self.lock.release()

    def enter_spar(self, user_ids) -> None:
        """Mark players busy for a practice fight the colony itself does not run (the lobby's spar):
        nothing can ambush or attack them, and they cannot give colony commands, until it is over."""
        ids = {str(u) for u in user_ids}
        self._sparring |= ids
        self.cache.mark(self._name + ":fighting", ids, self._mark_ttl())

    def leave_spar(self, user_ids) -> None:
        ids = {str(u) for u in user_ids}
        self._sparring -= ids
        self.cache.unmark(self._name + ":fighting", ids)

    def sync(self, keep=()) -> None:
        """Catch up with what other processes did: reload if the colony was saved elsewhere, and
        learn which roamers are busy in somebody's fight."""
        ver = self.cache.version(self._name)
        if ver != self._ver:
            self.reload(keep)
            self._ver = ver
        busy = self.cache.marked(self._name + ":engaged")
        for r in self.world.roamers:
            r.engaged = str(r.rid) in busy

    def reload(self, keep=()) -> None:
        """Re-read the colony, the map and the players from the database, in place: everything that
        holds this session's colony / world / players list sees the new state. The records of
        ``keep`` and of players in fights this process is playing are NOT replaced - their fight is
        the newest thing that has happened to them."""
        colony = self.store.get_colony(self.server_id)
        if colony is not None:
            self.colony.__dict__.update(colony.__dict__)
        saved = self.store.get_map(self.server_id)
        if saved:
            news = self.world.news
            self.world.__dict__.update(World.from_state(saved).__dict__)
            self.world.news = news
        held = {p.user_id: p for p in keep}
        held.update(self._mine)
        fresh = {p.user_id: p for p in self.store.list_players(self.server_id) if p.alive}
        merged = [held.get(uid, p) for uid, p in fresh.items()]
        merged += [p for uid, p in held.items() if uid not in fresh and p.alive and p.server_id == self.server_id]
        self.players[:] = merged
        self.now = max(self.now, self.colony.clock)
        for p in self.players:
            self.steer(p)

    @property
    def in_battle(self) -> set:
        """User ids of everyone in a fight in this colony right now (any process). A snapshot."""
        return self.cache.marked(self._name + ":fighting")

    def _heartbeat(self) -> None:
        """Keep this process's fighting / engaged marks alive while its fights last."""
        while True:
            time.sleep(FIGHT_TTL / 3)
            try:
                self.cache.mark(self._name + ":fighting", list(self._mine) + list(self._sparring), FIGHT_TTL)
                self.cache.mark(self._name + ":engaged", list(self._my_roamers), FIGHT_TTL)
            except Exception as e:                        # Redis hiccup: try again next beat
                print(f"[colony] heartbeat failed: {type(e).__name__}: {e}")

    def _mark_ttl(self) -> float:
        if not self.concurrent:
            return 6 * 3600.0                             # one thread, no heartbeat: the fight itself clears them
        if self._beat is None:
            self._beat = threading.Thread(target=self._heartbeat, daemon=True, name=f"beat-{self.server_id}")
            self._beat.start()
        return FIGHT_TTL

    # ---- bookkeeping -------------------------------------------------------------------
    def save(self, only=None) -> None:  # noqa: C901
        """Write the colony, the map and the players (``only``: just these players - after a fight,
        only the fighters changed). Items that have not changed are not written (storage._put)."""
        self.cache.extend(self._name, getattr(self._tls, "token", None), LOCK_TTL)    # a big save takes a moment
        self.colony.clock = self.now
        self.collect_sales(only)
        before = self.store.writes
        self.store.put_colony(self.colony)
        self.store.put_map(self.server_id, self.world.state())
        for p in (self.players if only is None else only):
            if p.server_id == self.server_id:             # (someone who has just left for another colony)
                self.store.put_player(p)
        if self.store.writes != before:                   # tell the other processes there is something new
            self._ver = self.cache.bump(self._name)
        self.update_leaderboard()

    # ---- the global leaderboard and global market (GLOBAL items in the store) ----------------
    LEADERBOARD_SIZE = 200

    def board_entry(self, p) -> dict:
        return {"name": p.name, "colony": self.colony.name, "server": self.server_id, "points": p.points,
                "level": p.level, "kills": p.kills.get("players", 0), "curses": p.kills.get("spirits", 0),
                "rules": getattr(p, "rules_added", 0), "node": p.node}

    def update_leaderboard(self) -> None:
        """This colony's living players on the game-wide board (top LEADERBOARD_SIZE by points)."""
        mine = {f"{self.server_id}:{p.user_id}": self.board_entry(p) for p in self.players if p.alive}

        def fn(d):
            entries = {k: v for k, v in d.get("entries", {}).items() if not k.startswith(self.server_id + ":")}
            entries.update(mine)
            top = sorted(entries.items(), key=lambda kv: (-kv[1]["points"], -kv[1]["level"]))[:self.LEADERBOARD_SIZE]
            d["entries"] = dict(top)
        self.store.update_global("LEADERBOARD", fn)

    def leaderboard(self, scope: str = "colony", n: int = 15) -> str:
        if not self.colony.has("score_board"):
            return ("Nobody here can see the score board yet: a player has to add the Open Score Board rule "
                    "(`addrule score_board`, 100 points).")
        if scope == "global":
            rows = list(self.store.get_global("LEADERBOARD").get("entries", {}).values())
            title = "Culling Game - all colonies"
        else:
            rows = [self.board_entry(p) for p in self.players if p.alive]
            title = f"{self.colony.name}"
        rows.sort(key=lambda e: (-e["points"], -e["level"]))
        out = [f"{title}: top {min(n, len(rows))} of {len(rows)}",
               f"{'#':>3} {'name':<20} {'pts':>5} {'lvl':>3} {'kills':>5} {'rules':>5}  where"]
        for i, e in enumerate(rows[:n], 1):
            where = f"{e['colony']} node {e['node']}" if scope == "global" else f"node {e['node']}"
            out.append(f"{i:>3} {e['name'][:20]:<20} {e['points']:>5} {e['level']:>3} {e['kills']:>5} {e['rules']:>5}  {where}")
        return "\n".join(out)

    def collect_sales(self, only=None) -> None:
        """Points owed to this colony's players for things they sold (global market, or a local sale
        made while they were in a fight). Taken off the books and paid in one atomic step."""
        book = self.store.get_global("MARKET").get("payouts", {})
        prefix = self.server_id + ":"
        if not any(k.startswith(prefix) for k in book):
            return
        busy = self.in_battle
        pool = self.players if only is None else only          # (only those this save will write)
        mine = set(self._mine)
        due = {f"{prefix}{p.user_id}": p for p in pool if p.alive and p.server_id == self.server_id
               and (p.user_id not in busy or p.user_id in mine)}
        taken: dict = {}

        def take(d):
            pay = d.get("payouts", {})
            for k in due:
                if k in pay:
                    taken[k] = pay.pop(k)
        if any(k in book for k in due):
            self.store.update_global("MARKET", take)
        for k, points in taken.items():
            due[k].points += points                       # a sale is not a score: no clock reset

    def global_market(self, me, verb: str, args: list, at_shop: bool) -> str:
        """market global | sell <item> <price> global | buy g<n> | unlist g<n>."""
        mkt = self.store.get_global("MARKET")
        offers = mkt.get("offers", [])
        if verb == "list":
            if not offers:
                return "Nothing is up for sale on the global market."
            return "Global market (every colony; `buy g<n>` at your shop):\n" + "\n".join(
                f"  g{o['id']} {ITEMS[o['item']].name:<26} {o['price']:>5} pts   from {o['name']} ({o['colony']})"
                + ("  (taken from the dead)" if o["looted"] else "") for o in offers)
        if not at_shop:
            return f"Trading happens at the colony's shop (node {self.world.shop})."
        if verb == "sell":
            key, price = args[0].lower(), args[1]
            it = ITEMS.get(key)
            if it is None or key not in me.inventory:
                return "That isn't in your bag."
            if it.mundane:
                return "Only cursed tools and cursed objects are traded."
            looted = key in me.looted
            if not looted and price > 2 * it.cost:
                return f"You may ask at most {2 * it.cost} for a {it.name} (twice its shop price)."
            me.inventory.remove(key)
            if looted:
                me.looted.remove(key)

            def add(d):
                d.setdefault("offers", []).append({"id": d.get("next", 1), "seller": me.user_id, "server": self.server_id,
                                                   "name": me.name, "colony": self.colony.name, "item": key,
                                                   "price": price, "looted": looted})
                d["next"] = d.get("next", 1) + 1
            self.store.update_global("MARKET", add)
            return f"Your {it.name} is on the global market for {price} points. Every colony can see it."
        oid = int(args[0].lstrip("gG#")) if args and args[0].lstrip("gG#").isdigit() else -1
        offer = next((o for o in offers if o["id"] == oid), None)
        if offer is None:
            return "No such offer. See `market global`."
        mine = offer["seller"] == me.user_id and offer["server"] == self.server_id
        if verb == "unlist" and not mine:
            return "That is not your offer."
        if verb == "buy" and mine:
            return "That is your own offer (`unlist g<n>` takes it back)."
        if verb == "buy" and me.points < offer["price"]:
            return f"That costs {offer['price']} points; you have {me.points}."
        taken: list = []

        def take(d):                                      # decided inside the update: another colony (or another
            live = next((o for o in d.get("offers", []) if o["id"] == oid), None)     # process) may have got there first
            if live is None:
                return
            d["offers"].remove(live)
            taken.append(live)
            if verb == "buy":
                k = f"{live['server']}:{live['seller']}"
                pay = d.setdefault("payouts", {})
                pay[k] = pay.get(k, 0) + live["price"]
        self.store.update_global("MARKET", take)
        if not taken:
            return "That offer has just gone. See `market global`."
        offer = taken[0]
        me.inventory.append(offer["item"])
        if verb == "unlist":
            if offer["looted"]:
                me.looted.append(offer["item"])
            return f"You take the {ITEMS[offer['item']].name} back."
        me.points -= offer["price"]                       # only once the sale is on the books
        return (f"Bought {ITEMS[offer['item']].name} for {offer['price']} points from {offer['name']} of "
                f"{offer['colony']}. They are paid the next time their colony moves.")

    def day(self) -> int:
        return int((self.now - self.colony.created_ts) // DAY)

    @staticmethod
    def find_player(token: str, pool: list):
        """A player named in a command: ``id:<user id>`` (what the Discord bot sends, exact), or the
        start of a character's name (what a person types)."""
        token = token.strip()
        if token.lower().startswith("id:"):
            return next((p for p in pool if p.user_id == token[3:]), None)
        low = token.lower()
        return (next((p for p in pool if p.name.lower() == low), None)
                or next((p for p in pool if p.name.lower().startswith(low)), None))

    def player(self, user_id) -> Optional[PlayerRecord]:
        """The living character a user has in this colony."""
        return next((p for p in self.players if p.user_id == str(user_id) and p.alive), None)

    def name_taken(self, name: str, user_id=None) -> bool:
        """Is a living character here already called that (someone else's)?"""
        low = name.lower()
        return any(p.alive and p.name.lower() == low and p.user_id != str(user_id) for p in self.players)

    def _pack_up(self, p: PlayerRecord) -> None:
        """Before a character leaves this colony: take their offers off the colony's market (back
        into the bag), and call back whatever they had out in it."""
        for offer in [o for o in self.colony.market if o["seller"] == p.user_id]:
            self.colony.market.remove(offer)
            p.inventory.append(offer["item"])
            if offer["looted"]:
                p.looted.append(offer["item"])
        for key in ("csm", "ten_shadows"):
            st = p.tech_state.get(key)
            if isinstance(st, dict) and st.get("out"):
                st["out"] = []
        pst = p.tech_state.get("puppets")
        if isinstance(pst, dict) and pst.get("out"):
            pst["stock"] = pst.get("stock", 0) + len(pst["out"])
            pst["out"], pst["sel"] = [], None

    def exchange(self, other: "ColonySession", user_id) -> str:
        """Colony transfer (both colonies need the Free Passage rule). One character per colony: if
        the user also has a living character in the other colony, the two trade places - each moves
        to the other's colony. The caller holds BOTH colonies (acquire them in server-id order)."""
        from .rules import can_move_player
        uid = str(user_id)
        me = self.player(uid)
        if me is None:
            return "You have no living character in this colony."
        if other is self or other.server_id == self.server_id:
            return "That is the colony you are in."
        if not can_move_player(self.colony, other.colony):
            return "Both colonies must have added the Free Passage rule."
        theirs = other.player(uid)
        if uid in self.in_battle or uid in other.in_battle:
            return "Not while one of your characters is in a fight."
        if other.name_taken(me.name, uid) or (theirs is not None and self.name_taken(theirs.name, uid)):
            return "A character with that name already lives there. (Names are unique within a colony.)"
        shift = other.now - self.now                      # each colony keeps its own clock: carry elapsed time over
        self._pack_up(me)
        self.players[:] = [p for p in self.players if p is not me]
        if theirs is not None:
            other._pack_up(theirs)
            other.players[:] = [p for p in other.players if p is not theirs]
        for rec, src, dst, delta in ((me, self, other, shift),) + (((theirs, other, self, -shift),) if theirs else ()):
            rec.server_id, rec.node, rec.hideout = dst.server_id, 0, None
            rec.last_score_ts += delta
            rec.created_ts += delta
            rec.ce_ts += delta if rec.ce_ts else 0.0
            dst.players.append(rec)
            dst.steer(rec)
        self.store.put_player(me)                         # the arrival first: a crash here duplicates, never loses
        if theirs is not None:
            self.store.put_player(theirs)                 # (it takes the slot the mover left)
        else:
            self.store._delete(f"SERVER#{self.server_id}", f"PLAYER#{uid}")
        self.save()
        other.save()
        self._ver = self.cache.bump(self._name)           # the players changed even if no other item did
        other._ver = other.cache.bump(other._name)
        if theirs is not None:
            return (f"{me.name} leaves {self.colony.name} for {other.colony.name}, and {theirs.name} comes the "
                    f"other way: one character per colony, so they trade places.")
        return f"{me.name} leaves {self.colony.name} for {other.colony.name}."

    def add_player(self, rec: PlayerRecord, out: Callable = print) -> bool:
        """A new character joins. False if that user already has a living one here; a dead one is replaced."""
        rec.created_ts = rec.last_score_ts = self.now
        if not self.store.put_player(rec, new_only=True):
            old = self.store.get_player(self.server_id, rec.user_id)
            if old is not None and old.alive:
                return False
            self.store.put_player(rec)
        self.players[:] = [p for p in self.players if p.user_id != rec.user_id] + [rec]   # in place: front ends hold it
        self.steer(rec)
        if self.is_puppeteer(rec):
            out(f"Your body is sealed in a hideout at node {rec.hideout}. It cannot travel: "
                f"`deploy` a puppet and steer that instead.")
        self.save()
        self._ver = self.cache.bump(self._name)           # (the player item was written before the save counted)
        return True

    def remove_player(self, user_id) -> Optional[PlayerRecord]:
        """Delete a user's character here (alive or dead) and take their offers off the market."""
        rec = self.store.get_player(self.server_id, str(user_id))
        if rec is None:
            return None
        self.players[:] = [p for p in self.players if p.user_id != str(user_id)]
        self.store._delete(f"SERVER#{self.server_id}", f"PLAYER#{user_id}")
        self.colony.market = [o for o in self.colony.market if o["seller"] != str(user_id)]
        self.save()
        self._ver = self.cache.bump(self._name)
        return rec

    # ---- helpers (formerly closures inside cli.colony_mode) -------------------------------
    def fight(self, sides, node, label):
        """sides: list of (spec, team). Runs a battle at a node and writes results back."""
        world, colony, rng = self.world, self.colony, self.rng
        party = [spec.record for spec, _ in sides if spec.record is not None]
        io = self.io_for(party) if party else self.io
        b = Battle(self.server_id, seed=int(rng.integers(1 << 30)), io=io, colony=colony, world=world,
                   node=node, now=self.now, cache=self.cache)
        added = [b.add(spec, team) for spec, team in sides]
        for kw in world.field_objects(node):
            b.add_object(**kw)
        io.say(f"\n*** {label} ***" + (f"\n{self.battle_banner}\n" if self.battle_banner else ""))
        me = getattr(self._tls, "me", None)               # whoever gave the command that led here
        mine = list(party)
        for extra in [me] + list(getattr(self._tls, "touched", ())):      # ...and whoever it has changed so far
            if extra is not None and extra.alive and extra not in mine:
                mine.append(extra)
        ids = {p.user_id for p in mine}                   # all of them are busy until this is over
        self.save(only=mine)                              # what matters of this command so far, before letting go
        self._mine.update({p.user_id: p for p in mine})
        try:
            self.cache.mark(self._name + ":fighting", ids, self._mark_ttl())
            if self.concurrent:
                self.release()                            # the colony carries on while this is fought
            try:
                b.run()
            finally:
                try:
                    if hasattr(io, "flush"):
                        io.flush()                        # (outside the lock: it waits on Discord)
                finally:
                    if self.concurrent:
                        self._retake(mine)
        finally:                                          # whatever went wrong, nobody stays marked busy
            for uid in ids:
                self._mine.pop(uid, None)
            try:
                self.cache.unmark(self._name + ":fighting", ids)
            except Exception as e:
                print(f"[colony] could not clear fight marks (they lapse in {FIGHT_TTL:.0f}s): {type(e).__name__}: {e}")
        for oid in b.broken_oids:                         # (the map may have been reloaded under the fight)
            self.world.mark_broken(oid)
        for p in self.players:
            self.steer(p)
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
                io.say(f"\n!!! SUKUNA walks {colony.name} with {held} finger(s). He will gather the rest: "
                            f"the Finger Bearers first, then anyone carrying or caging one.")
        for spec, _ in sides:                             # every character who fought, with their stats
            if spec.record is not None:
                try:
                    self.cache.save_character(spec.record, {"last_battle": {"node": node, "label": label,
                                                                            "rounds": b.round}})
                except Exception as e:                    # a cache outage must not lose the fight
                    print(f"[colony] character snapshot failed: {type(e).__name__}: {e}")
        self.save(only=party)                             # and for good, in the database
        return added

    def _retake(self, party) -> None:
        """Take the colony back after a fight. The fight's results must not be lost: wait as long as
        it takes, and if the lock truly cannot be had, write the fighters' records regardless."""
        for attempt in range(10):
            try:
                self.acquire(wait=30.0, keep=party)
                return
            except ColonyBusy:
                print(f"[colony] {self.server_id}: still waiting for the colony after a fight ({attempt + 1})")
        for p in party:
            self.store.put_player(p)
        self.cache.bump(self._name)
        raise ColonyBusy(self.server_id)

    def encounter(self, nid, roamers, party=None):
        """Roamers fight the players present at a node. Returns the combatants, or None if nobody is there."""
        world, rng = self.world, self.rng
        party = party if party is not None else [p for p in self.players if p.alive and self.can_fight(p)
                                                 and nid in self.where(p)]
        busy = self.in_battle
        party = [p for p in party if p.alive and p.user_id not in busy and nid in self.where(p)]
        live = {r.rid: r for r in world.roamers}          # (callers may hold roamers from before another fight,
        roamers = [live[r.rid] for r in roamers if r.rid in live and not live[r.rid].engaged     # or a reload)
                   and not live[r.rid].respawn_at and live[r.rid].node == nid]
        if not party or not roamers:
            return None
        specs = [world.spec_for(r, rng) for r in roamers]
        rids = [r.rid for r in roamers]
        for r in roamers:
            r.engaged = True
        self._my_roamers.update(rids)
        self.cache.mark(self._name + ":engaged", rids, self._mark_ttl())
        try:
            added = self.fight([(self.present(p, nid), 0) for p in party] + [(sp, 50) for sp in specs], nid,
                               f"Curses close in at {world.nodes[nid].name}: " + ", ".join(sp.name for sp in specs))
        finally:
            self.cache.unmark(self._name + ":engaged", rids)
            self._my_roamers.difference_update(rids)
            live = {r.rid: r for r in world.roamers}      # the map may have been reloaded meanwhile
            for rid in rids:
                if rid in live:
                    live[rid].engaged = False
        for rid, c in zip(rids, added[len(party):]):
            r = live.get(rid)
            if r is None:
                continue
            if not c.alive:
                world.defeat(r, self.now, rng)
            elif r.kind == "sukuna":                      # he keeps whatever he took back, and what he learned
                r.fingers = c.inventory.count("sukuna_finger")
                r.slash = r.slash or bool(c.tech_state.get("ten_shadows", {}).get("world_slash"))
        return added

    @staticmethod
    def is_puppeteer(p):
        return "puppet_manipulation" in p.techniques

    def present(self, p, nid):
        """A player's fighter for a battle at nid: in person, or commanding scouts from afar."""
        spec = p.to_spec("human")
        if not self.is_puppeteer(p) and p.node != nid:
            spec.meta["remote_scout"] = True
        return spec

    def steer(self, p):
        """A puppeteer's map position is the puppet they are steering, or their body if none is out."""
        if not self.is_puppeteer(p):
            return
        world = self.world
        if p.hideout is None:                             # the body needs somewhere to stay
            p.hideout = min((n.nid for n in world.nodes.values() if n.kind == "hideout"),
                            key=lambda n: world.hops(0, n))
        st = puppet_state(p.tech_state.setdefault("puppets", {"bank": 0.0, "stock": 3}))
        ids = {e["id"]: e for e in st["out"]}
        if st["sel"] not in ids:
            st["sel"] = next(iter(ids), None)
        p.node = ids[st["sel"]]["node"] if st["sel"] is not None else p.hideout

    def where(self, p):
        """Every node this player can be found at: in person, or through what they sent out."""
        if not self.is_puppeteer(p):
            return [p.node] + [e["node"] for _, e, _ in self.scouts_of(p)]
        return [e["node"] for e in puppet_state(p.tech_state["puppets"])["out"]] + [p.hideout]

    @staticmethod
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

    def sight(self, nid):
        """What can be seen at a node (your own eyes or a scout's)."""
        world = self.world
        n = world.nodes[nid]
        curses = [r.label for r in world.roamers if not r.respawn_at and r.node == nid]
        others = [p.name for p in self.players if nid in self.where(p)]
        intact = sum(not world.broken[o] for o in n.objects)
        return (f"node {nid} {n.name} [{n.kind}] -> {', '.join(map(str, n.edges))} | curses: "
                f"{', '.join(curses) or 'none'} | players: {', '.join(others) or 'none'} | {intact} intact object(s)"
                + (" | THE MEDIC IS HERE" if world.medic == nid else ""))

    # ---- one world command -----------------------------------------------------------------
    def command(self, me: PlayerRecord, line: str, out: Callable = print) -> None:
        """Run one colony command for ``me``, let the hours it takes pass, and save."""
        self.players[:] = [p for p in self.players if p.alive]
        if not me.alive:
            out("You are dead. Create a new character.")
            return
        if me.user_id in self.in_battle:
            out("You are in a fight, or one your last command set off is still being played. Wait until it is over "
                "(a fighter's controls are in the battle's channel).")
            return
        self._tls.me, self._tls.touched = me, []
        tokens = line.split()
        if not tokens:
            return
        colony, world, players, now = self.colony, self.world, self.players, self.now
        day, where, sight, steer, present, fight = self.day, self.where, self.sight, self.steer, self.present, self.fight
        scouts_of, is_puppeteer = self.scouts_of, self.is_puppeteer
        steer(me)
        node = world.nodes[me.node]
        cmd, rest = tokens[0].lower(), tokens[1:]
        spend = 0.0                                       # hours of game time this command takes
        if cmd == "map":
            out(world.describe(me.node))
        elif cmd == "look":
            out(f"{node.name} [{node.kind}] -> " + ", ".join(f"{e}:{world.nodes[e].name}" for e in node.edges))
            for oid in node.objects:
                o = world.objects[oid]
                state = "broken" if world.broken[oid] else "looted" if world.looted[oid] else "intact"
                out(f"   obj#{oid} {o.name} ({o.role}, {state})")
            here = [p.name + (" (puppet)" if is_puppeteer(p) and p.hideout != me.node else "")
                    for p in players if me.node in where(p) and p is not me]
            reach = skills.sight_range(me)                # navigation: see further
            near = [f"{r.label} at node {r.node}" for r in world.roamers
                    if not r.respawn_at and 0 <= world.hops(me.node, r.node) <= reach]
            out("   Players here: " + (", ".join(here) or "none") + " | Nearby: " + (", ".join(near) or "quiet"))
            if world.medic == me.node:
                out("   The colony's medic is here. (`treat`)")
            for kind, e, name in scouts_of(me):           # what your scouts see
                out(f"   Through {name}: {sight(e['node'])}")
        elif cmd == "me":
            left = min(colony.inactivity_days, colony.inactivity_days - (self.idle_clock() - me.last_score_ts) / DAY)
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
            six = has_six_eyes(me.techniques, me.six_eyes)
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
                spend = skills.travel_hours(me) if "can't" not in msg else 0.0   # navigation: quicker
                if pst is not None:                       # it is the puppet that walked
                    next(e for e in pst["out"] if e["id"] == pst["sel"])["node"] = me.node
        elif cmd in ("scouts", "send", "order") or (cmd == "recall" and not is_puppeteer(me)):
            kinds = [k for k in ("csm", "ten_shadows") if {"csm": "cursed_spirit_manipulation"}.get(k, k) in me.techniques]
            if not kinds:
                out("Only spirit manipulators and Ten Shadows users can send something out.")
                return
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
                return
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
            spend = min(24.0, float(rest[0]) if rest and rest[0].replace(".", "", 1).isdigit() else 1.0)
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
            who = me if not rest else self.find_player(rest[0], [p for p in players if p.node == me.node
                                                                 and p is not me])
            if who is None:
                out("No such player at this node.")
            elif who is not me and who.user_id in self.in_battle:
                out(f"{who.name} is in a fight. Wait until it is over.")
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
                    self._tls.touched.append(who)
                out(f"An hour of concentration. {who.name}: {who.condition_text()}")
                spend = 1.0
        elif cmd == "medic":
            out(world.medic_rumour(me.node, exact=colony.has("score_board") or skills.get(me, "navigation") >= 10))
        elif cmd == "treat":
            if world.medic != me.node:
                out("The medic isn't here. " + world.medic_rumour(me.node, exact=colony.has("score_board") or skills.get(me, "navigation") >= 10))
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
        elif cmd in ("leaderboard", "lb", "board"):
            out(self.leaderboard("global" if rest and rest[0].lower() == "global" else "colony"))
        elif cmd == "market" and rest and rest[0].lower() == "global":
            out(self.global_market(me, "list", [], node.kind == "shop"))
        elif cmd == "sell" and len(rest) == 3 and rest[2].lower() == "global" and rest[1].isdigit():
            out(self.global_market(me, "sell", [rest[0], int(rest[1])], node.kind == "shop"))
        elif cmd in ("buy", "unlist") and rest and rest[0].lower().startswith("g") and rest[0][1:].isdigit():
            out(self.global_market(me, cmd, rest, node.kind == "shop"))
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
                    if seller is not None and seller.user_id not in self.in_battle:
                        seller.points += offer["price"]   # a sale is not a score: no clock reset
                        self._tls.touched.append(seller)
                    else:                                 # mid-fight (their record is the fight's) or gone: owed
                        key, owed = f"{self.server_id}:{offer['seller']}", offer["price"]

                        def book(d):
                            pay = d.setdefault("payouts", {})
                            pay[key] = pay.get(key, 0) + owed
                        self.store.update_global("MARKET", book)
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
            other = self.find_player(rest[0], [p for p in players if p is not me])
            err = ("No such player." if other is None else
                   f"{other.name} is in a fight. Give it to them when it is over." if other.user_id in self.in_battle
                   else transfer_points(colony, me, other, int(rest[1]), now))
            if not err:
                self._tls.touched.append(other)
            out(err or f"Transferred {rest[1]} points to {other.name}.")
        elif cmd == "players":
            for i, p in enumerate(players, 1):
                out(f"  {i}) {p.name} L{p.level} @ node {p.node}" + (f", {p.points} pts" if colony.has("score_board") or p is me else ""))
        elif cmd == "pvp" and rest:
            foe = self.find_player(rest[0], [p for p in players if me.node in where(p) and p is not me])
            err = (("No such player at this node." if foe is None else None)
                   or (f"{foe.name} is already in a fight." if foe.user_id in self.in_battle else None)
                   or self.pvp_check(me, foe))
            if err:
                out(err)
            else:
                me.crimes.add(Crime.ASSAULT, me.node, day())
                fight([(present(me, me.node), 0), (present(foe, me.node), 1)], me.node, f"{me.name} attacks {foe.name}!")
                spend = 1.0
        elif cmd == "skills":
            out(skills_text(me))
        elif cmd in ("upgrade", "train") and len(rest) >= 1:
            n = int(rest[1]) if len(rest) > 1 and rest[1].isdigit() else 1
            out(skills.spend(me, rest[0], n))
        else:
            out("Unknown command. Type `help`.")
            return

        self.advance(spend, out)
        self.save()

    def advance(self, spend: float, out: Callable = print) -> None:
        """The world moves an hour at a time: roamers close in, fights break out, idle players die."""
        world, colony, players, rng = self.world, self.colony, self.players, self.rng
        where, scouts_of = self.where, self.scouts_of
        now = self.now
        while spend > 0:                                  # the world moves an hour at a time
            step = min(1.0, spend)
            spend -= step
            self.now += step * 3600
            now = self.now
            fighting = self.in_battle                     # (their records belong to their fights for now)
            for p in players:
                st = p.tech_state.get("puppets")
                if st is not None and p.user_id not in fighting:      # the restricted body stores energy over time
                    st["bank"] = min(400.0, st["bank"] + 40 * step / 24)
            hunted = {r.node for r in world.roamers if not r.respawn_at}
            for p in players:                             # scouts on auto go looking for curses
                if p.user_id in fighting:
                    continue
                for kind, e, name in scouts_of(p):
                    if e.get("auto") and e["node"] not in hunted:
                        step = world._step_toward(e["node"], hunted)
                        ways = [x for x in world.nodes[e["node"]].edges if world.nodes[x].kind != "hideout"]
                        e["node"] = step if step is not None else int(rng.choice(ways)) if ways else e["node"]
            busy = self.in_battle                         # (one look per hour, not one per player)
            found = [SimpleNamespace(node=n, alive=True, fingers=p.fingers + p.inventory.count("sukuna_finger"))
                     for p in players if p.alive and self.can_fight(p) and p.user_id not in busy
                     for n in where(p)]
            held = sum(p.fingers + p.inventory.count("sukuna_finger") for p in players if p.alive)
            fights = world.tick(found, now, rng, held)
            for line in world.news:                       # what Sukuna has been doing
                out("\n!!! " + line)
            world.news.clear()
            for nid, roamers in fights:                  # only players who can fight (in a lobby, on Discord)
                busy = self.in_battle
                party = [p for p in players if p.alive and self.can_fight(p) and nid in where(p)
                         and p.user_id not in busy]
                if party and rng.random() < skills.evade_chance(party):    # navigation: slip away
                    guide = max(party, key=lambda p: skills.get(p, "navigation"))
                    out(f"\n{guide.name} spots {', '.join(r.label for r in roamers)} first and leads the way "
                        f"around them at {world.nodes[nid].name}.")
                    continue
                if self.encounter(nid, roamers, party) is None:
                    continue
                spend = 0
            busy = self.in_battle
            for p in enforce_inactivity([x for x in players if x.user_id not in busy], colony, self.idle_clock()):
                out(f"\n!!! {p.name}'s score has not changed in {colony.inactivity_days} days. "
                    f"Their cursed technique is removed. {p.name} is dead.")


def skills_text(rec) -> str:
    """Skill points, what each skill holds and does, and the techniques perception still locks."""
    from .constants import REINCARNATED_PER_BONUS
    lines = [f"Skill points to spend: {rec.skill_points}   (+10 a level up to level 10, +5 after; "
             f"`upgrade <skill> [points]`, at most {skills.SKILL_CAP} in each)"]
    for key, (name, what) in skills.SKILLS.items():
        lines.append(f"  {key:<11} {skills.get(rec, key):>3}  {name}: {what}")
    per = (float(rec.to_spec().stats[Stat.PER]) + (REINCARNATED_PER_BONUS if rec.pclass == PClass.REINCARNATED else 0)
           + (6 if has_six_eyes(rec.techniques, rec.six_eyes) else 0))           # the Six Eyes: +6 in a fight
    locked = sorted(((a.min_per, a.name, TECHNIQUES[t].name) for t in rec.techniques if t in TECHNIQUES
                     for a in TECHNIQUES[t].actions if a.min_per > per), key=lambda x: x[0])
    lines.append(f"Perception for unlocks: {per:.0f}" + (" (incl. +6 from a past life)"
                                                         if rec.pclass == PClass.REINCARNATED else ""))
    lines += [f"  locked until perception {p}: {name} ({tech})" for p, name, tech in locked] or ["  nothing locked"]
    return "\n".join(lines)

