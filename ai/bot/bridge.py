"""Runs the (synchronous) battle engine against Discord (asynchronous).

The engine blocks inside ``IO.channel`` / ``IO.turn`` / ``IO.ask`` until a player decides.  So a
battle runs in a worker thread (``asyncio.to_thread``) with a ``DiscordIO``:

* ``say``   lines are buffered and posted to the battle's channel in batches;
* ``tell``  private lines are kept per player and shown only in that player's ephemeral panel;
* ``channel`` / ``turn``  post "your move" with an **Open controls** button and block on a queue.
  The panel (ephemeral, only that player can use it) turns clicks into the CLI's own command
  lines ("use dismantle e1 head chant", "defend dodge", "wait") and puts them on the queue; the
  battle thread runs them through ``cli.battle_command`` / ``cli.channel_command`` and answers.
  Nobody waits forever: on timeout a fighter waits (turn) or gathers nothing (channel phase);
* ``ask``  posts buttons for the asked player; on timeout the engine decides (returns None).

The engine's state is only read on the event loop while the battle thread is parked waiting for
that same player's input, so the two never touch it at once.
"""
from __future__ import annotations

import asyncio
import queue
import threading
import time
from collections import defaultdict
from typing import Optional

import discord

from .. import ai
from ..battle import IO
from ..cli import BATTLE_HELP, PART_LABEL, battle_command, channel_command, limb_line, vitals
from ..constants import Kind, Part, PState, Target
from . import style

TURN_TIMEOUT = 180.0          # seconds a player has to commit (then they wait)
CHANNEL_TIMEOUT = 120.0       # ...to gather cursed energy (then they gather nothing)
ASK_TIMEOUT = 60.0            # ...to answer a question (then the engine decides)
MENTIONS = discord.AllowedMentions(users=True, roles=False, everyone=False)
# Components V2 messages hold at most 4000 characters of text in total. The battle feed is ONE
# message per battle, edited as the fight goes on. When the next lines would not fit, the feed
# turns a page: the message shows the newest page, and its arrow buttons let anyone leaf back
# through the earlier ones (privately, so the live page stays put for everyone else).
# Measured (ai engine battles, 20 seeds each): rounds per full message - 1v1 median 9 (7-12),
# 2v2 median 6 (5-8), three teams of two median 4 (2-8).
FEED_LIMIT = 4000 - len(style.code("")) - 40          # (room for the page line)


def domain_line(b) -> str:
    """The domain(s) in force, and how a clash stands, in a line or two."""
    def describe(d):
        owner = b.by_cid.get(d.owner)
        shape = "open (no barrier)" if d.data.get("open") else f"{d.data.get('shell', 'normal')} barrier"
        sure = "sure-hit" if d.data.get("lethal", True) else "no harm by itself"
        return f"**{d.name}** ({owner.name if owner else '?'}; {shape}; {sure}; {d.rounds} round(s) left)"
    if b.domain is None:
        return ""
    if b.rival is None:
        return f"🌀 Domain: {describe(b.domain)}"
    n = b.rival.data.get("clash", 0)
    return (f"⚔️ **DOMAIN CLASH** (round {n}): {describe(b.domain)} against {describe(b.rival)}. While they are "
            f"locked, neither sure-hit lands; each round the more refined domain gains, and one breaks.")


def user_of(c) -> Optional[str]:
    """The Discord user id that controls a combatant (its root's player record), if any."""
    rec = getattr(c.root, "record", None)
    return str(rec.user_id) if rec is not None else None


class Prompt:
    """One decision the battle thread is waiting on."""

    def __init__(self, kind: str, b, c, user_id: str):
        self.kind = kind                      # "channel" | "turn"
        self.b, self.c, self.user_id = b, c, user_id
        self.requests: "queue.Queue" = queue.Queue()
        self.open = True
        self.busy = False                     # a request is being run on the battle thread
        self.round = b.round


class DiscordIO(IO):
    def __init__(self, bot: discord.Client, channel, loop: asyncio.AbstractEventLoop,
                 turn_timeout: float = TURN_TIMEOUT, channel_timeout: float = CHANNEL_TIMEOUT,
                 ask_timeout: float = ASK_TIMEOUT):
        self.bot, self.dest, self.loop = bot, channel, loop    # (self.channel is IO.channel)
        self.turn_timeout, self.channel_timeout, self.ask_timeout = turn_timeout, channel_timeout, ask_timeout
        self.public: list = []
        self.feed_msg = None                  # the battle's one feed message, edited as lines arrive
        self.pages: list = []                 # its pages of text; the last one is live
        self.private: dict = defaultdict(list)
        self.prompts: dict = {}               # user id -> the Prompt they are being asked
        self._lock = threading.Lock()

    # ---- plumbing ------------------------------------------------------------------------
    def _post(self, coro, wait: bool = True):
        """Run a coroutine on the bot's loop from the battle thread."""
        fut = asyncio.run_coroutine_threadsafe(coro, self.loop)
        if not wait:
            return fut
        try:
            return fut.result(timeout=60)
        except Exception as e:                # a failed post must not kill the battle
            print(f"[bot] post failed: {type(e).__name__}: {e}")
            return None

    def _send(self, build):
        """Post a view. ``build`` makes it: discord.py views must be created on the event loop."""
        async def go():
            return await self.dest.send(view=build(), allowed_mentions=MENTIONS)
        return self._post(go())

    def _edit(self, message, build) -> None:
        async def go():
            await _quiet_edit(message, build())
        self._post(go(), wait=False)

    def flush(self) -> None:
        """Add what has been said to the feed: onto the live page, or onto a new page when it is full."""
        with self._lock:
            lines, self.public = self.public, []
        text = "\n".join(lines).strip("\n")
        if not text:
            return
        for piece in style.chunks(text.split("\n"), FEED_LIMIT):
            piece = piece.rstrip("\n")
            if self.pages and len(self.pages[-1]) + 1 + len(piece) <= FEED_LIMIT:
                self.pages[-1] += "\n" + piece
            else:
                self.pages.append(piece)
        if self.feed_msg is None:
            self.feed_msg = self._send(lambda: FeedView(self.pages))
        else:
            self._post(_quiet_edit(self.feed_msg, lambda: FeedView(self.pages)))    # waited: edits stay in order

    def take_private(self, user_id: str) -> list:
        with self._lock:
            notes, self.private[user_id] = self.private[user_id], []
        return notes

    # ---- IO ---------------------------------------------------------------------------------
    def say(self, text: str) -> None:
        with self._lock:
            self.public.append(str(text))
            big = sum(len(x) + 1 for x in self.public) > 3500
        if big:
            self.flush()

    def tell(self, c, text: str) -> None:
        uid = user_of(c)
        if uid is not None:
            with self._lock:
                self.private[uid].append(str(text))

    def channel(self, b, c) -> None:
        if c.controller != "human" or user_of(c) is None:
            return ai.channel(b, c)
        self._prompt("channel", b, c)

    def turn(self, b, c) -> None:
        if c.controller != "human" or user_of(c) is None:
            return ai.act(b, c)
        self._prompt("turn", b, c)

    def _prompt(self, kind: str, b, c) -> None:
        uid = user_of(c)
        self.flush()
        p = Prompt(kind, b, c, uid)
        self.prompts[uid] = p
        what = ("gather cursed energy where you mean to use it" if kind == "channel"
                else "commit an action or a defence")
        limit = self.channel_timeout if kind == "channel" else self.turn_timeout
        text = (f"<@{uid}> {style.heading(f'Round {b.round}', 3)} - **{c.name}** `[{c.cid}]`: {what}. "
                f"You have {int(limit)} seconds." + (f"\n{domain_line(b)}" if b.domain else ""))
        call = self._send(lambda: CallView(self, p, text))
        handler = channel_command if kind == "channel" else battle_command
        deadline = time.monotonic() + limit
        try:
            while True:
                try:
                    line, reply = p.requests.get(timeout=max(0.1, deadline - time.monotonic()))
                    timed_out = False
                except queue.Empty:
                    line, reply, timed_out = ("none" if kind == "channel" else "wait"), None, True
                out: list = []
                try:
                    done = bool(handler(b, c, line, out.append))
                except Exception as e:        # a bad command is the player's problem, not the battle's
                    out.append(f"That did not work ({type(e).__name__}: {e}).")
                    done = False
                if timed_out:
                    b.say(f"{c.name} hesitates too long" + (" and gathers nothing." if kind == "channel" else "."))
                    done = True
                if done:
                    p.open = False                    # closed BEFORE the reply: nothing new can be queued
                p.busy = False
                if reply is not None:
                    self.loop.call_soon_threadsafe(_resolve, reply, ("\n".join(out), done))
                if done:
                    break
        finally:
            p.open = False
            self.prompts.pop(uid, None)
            while True:                               # anything that slipped in as it closed gets an answer
                try:
                    _, late = p.requests.get_nowait()
                except queue.Empty:
                    break
                if late is not None:
                    self.loop.call_soon_threadsafe(_resolve, late, ("That moment has passed.", True))
            if call is not None:                       # the ping has done its job: keep the feed at the bottom
                self._post(_quiet_delete(call), wait=False)

    def ask(self, b, c, prompt: str, options: list) -> Optional[int]:
        uid = user_of(c)
        if uid is None or not options:
            return None
        self.flush()
        answer: dict = {}
        event = threading.Event()
        msg = self._send(lambda: AskView(uid, prompt, options, answer, event, self.ask_timeout))
        if msg is None:
            return None
        event.wait(self.ask_timeout + 2)
        k = answer.get("k")
        self._post(_quiet_delete(msg), wait=False)    # answered (the feed says what came of it): out of the way
        if k is None:
            self.tell(c, f"No answer to \"{prompt[:80]}...\" - instinct decided.")
        return k


def _resolve(fut: asyncio.Future, value) -> None:
    if not fut.done():
        fut.set_result(value)


class FeedView(discord.ui.LayoutView):
    """A page of the battle feed. ``index`` None = the live (last) page, shown on the shared message;
    its arrows open the earlier pages for whoever clicks, as a private copy they can leaf through."""

    def __init__(self, pages: list, index: Optional[int] = None):
        super().__init__(timeout=None if index is None else 300)
        self.pages, self.index = pages, index
        n = len(pages)
        i = n - 1 if index is None else max(0, min(index, n - 1))
        container = discord.ui.Container(accent_colour=style.ASH)
        container.add_item(discord.ui.TextDisplay(style.code(pages[i])))
        if n > 1 or index is not None:
            container.add_item(discord.ui.TextDisplay(f"-# Page {i + 1}/{n}" + (" (live)" if index is None else "")))
            row = discord.ui.ActionRow()
            for emoji, target, off in (("◀️", i - 1, i == 0), ("▶️", i + 1, i >= n - 1)):
                btn = discord.ui.Button(emoji=emoji, style=discord.ButtonStyle.blurple, disabled=off)
                btn.callback = self._go(target)
                row.add_item(btn)
            container.add_item(row)
        self.add_item(container)

    def _go(self, target: int):
        async def cb(itx: discord.Interaction) -> None:
            view = FeedView(self.pages, target)
            if self.index is None:                    # from the shared message: a private copy
                await itx.response.send_message(view=view, ephemeral=True)
            else:
                await itx.response.edit_message(view=view)
        return cb


async def _quiet_edit(message: discord.Message, view) -> None:
    try:
        await message.edit(view=view() if callable(view) else view)
    except discord.HTTPException:
        pass


async def _quiet_delete(message: discord.Message) -> None:
    try:
        await message.delete()
    except discord.HTTPException:
        pass


async def run_battle(b, io: DiscordIO, pool=None) -> dict:
    """Play a battle to the end on a battle thread; returns ``Battle.finish()``'s result."""
    loop = asyncio.get_running_loop()
    try:
        return await loop.run_in_executor(pool, b.run)
    finally:
        await loop.run_in_executor(pool, io.flush)


# ======================================================================================
# Views
# ======================================================================================
class CallView(discord.ui.LayoutView):
    """Public "your move" message. Only the player whose move it is can open the controls."""

    def __init__(self, io: DiscordIO, p: Prompt, text: str):
        super().__init__(timeout=max(io.turn_timeout, io.channel_timeout) + 30)
        self.io, self.p = io, p
        button = discord.ui.Button(label="Open controls", style=discord.ButtonStyle.blurple, emoji="🎮")
        button.callback = self.open_panel
        container = discord.ui.Container(discord.ui.TextDisplay(text), accent_colour=style.BLURPLE)
        container.add_item(discord.ui.ActionRow(button))
        self.add_item(container)

    async def open_panel(self, itx: discord.Interaction) -> None:
        if str(itx.user.id) != self.p.user_id:
            await itx.response.send_message("It is not your move.", ephemeral=True)
            return
        if not self.p.open:
            await itx.response.send_message("That moment has passed.", ephemeral=True)
            return
        if self.p.busy:
            await itx.response.send_message("Still working on your last command - try again in a moment.",
                                            ephemeral=True)
            return
        panel = ControlPanel(self.io, self.p)
        await itx.response.send_message(view=panel.render(), ephemeral=True)


class AskView(discord.ui.LayoutView):
    def __init__(self, uid: str, prompt: str, options: list, answer: dict, event: threading.Event, timeout: float):
        super().__init__(timeout=timeout)
        self.uid, self.prompt, self.answer, self.event = uid, prompt, answer, event
        container = discord.ui.Container(discord.ui.TextDisplay(f"<@{uid}> **{prompt}**"), accent_colour=style.BLURPLE)
        options = list(options)[:25]
        for i in range(0, len(options), 5):
            row = discord.ui.ActionRow()
            for k, label in enumerate(options[i:i + 5], start=i):
                btn = discord.ui.Button(label=str(label)[:80], style=discord.ButtonStyle.secondary)
                btn.callback = self._pick(k, str(label))
                row.add_item(btn)
            container.add_item(row)
        self.add_item(container)

    def _pick(self, k: int, label: str):
        async def callback(itx: discord.Interaction) -> None:
            if str(itx.user.id) != self.uid:
                await itx.response.send_message("This question is not for you.", ephemeral=True)
                return
            if self.event.is_set():
                await itx.response.send_message("Already answered.", ephemeral=True)
                return
            self.answer["k"] = k
            self.event.set()
            self.stop()
            await itx.response.edit_message(view=style.panel(None, None, f"<@{self.uid}> {self.prompt}\n> **{label}**",
                                                             accent=style.ASH, thumbnail=False))
        return callback

    async def on_timeout(self) -> None:
        self.event.set()


class CommandModal(discord.ui.Modal, title="Battle command"):
    line = discord.ui.TextInput(label="Command (as in /learn battle)", placeholder="throw f2 e1 head",
                                max_length=200)

    def __init__(self, panel: "ControlPanel"):
        super().__init__()
        self.panel = panel

    async def on_submit(self, itx: discord.Interaction) -> None:
        await self.panel.submit(itx, str(self.line.value))


class ControlPanel:
    """The ephemeral controls for one decision. Every change re-renders the whole panel."""

    def __init__(self, io: DiscordIO, p: Prompt):
        self.io, self.p = io, p
        self.act_key: Optional[str] = None
        self.target: Optional[str] = None
        self.part: str = "torso"
        self.chant = False
        self.feedback: list = []

    # ---- what the player can pick ------------------------------------------------------
    @property
    def b(self):
        return self.p.b

    @property
    def c(self):
        return self.p.c

    def _available(self) -> list:
        b, c = self.b, self.c
        out = []
        for a in b.actions_for(c):
            if a.react is not None:
                continue
            why = b.why_cant(c, a)
            if why is None and b.phase == "commit" and a.channel:
                why = b.charged_for(c, a)
            if self.p.kind == "channel" and not a.channel:
                continue
            if why is None:
                out.append(a)
        return out

    def _reactions(self) -> list:
        return [a for a in self.b.actions_for(self.c) if a.react is not None and self.b.why_cant(self.c, a) is None]

    def _act(self):
        return next((a for a in self.b.actions_for(self.c) if a.key == self.act_key), None)

    def _targets(self, act) -> list:
        """(value, label) pairs for the chosen action."""
        b, c = self.b, self.c
        if act is None:
            return []
        if act.target == Target.CHOICE:
            return [(str(k), str(label)) for k, label in b.choices(c, act)]
        if act.target == Target.ENEMY:
            pool = b.enemies(c)
        elif act.target in (Target.ANY, Target.CORPSE, Target.FREE):
            pool = [x for x in b.fighters if x is not c and (x.alive or x.corpse)]
        else:
            return []
        return [(x.cid, f"{x.name} [{x.cid}]" + ("" if x.alive else " (corpse)")) for x in pool]

    def _parts(self) -> list:
        tgt = self.b.by_cid.get(self.target) if self.target else None
        if tgt is None:
            return [("torso", "torso")]
        return [(PART_LABEL[p].replace(".", ""), PART_LABEL[p]) for p in Part
                if self.b.part_state[tgt.idx, p] in (PState.OK, PState.STUNNED)]

    # ---- rendering -------------------------------------------------------------------------
    def render(self) -> discord.ui.LayoutView:
        b, c, p = self.b, self.c, self.p
        view = discord.ui.LayoutView(timeout=max(self.io.turn_timeout, self.io.channel_timeout) + 30)
        notes = self.io.take_private(p.user_id)
        self.feedback += notes
        head = style.heading(f"Round {b.round} - {c.name} [{c.cid}]", 3)
        phase = ("**Channel phase.** Gather cursed energy in the parts a technique needs (it leaves your pool "
                 "now); only techniques that need it are listed." if p.kind == "channel" else
                 "**Commit an action or a defence.**") + (f"\n{domain_line(b)}" if b.domain else "")
        body = (f"{head}\n{phase}\n" + style.stat("HP", f"{max(c.hp, 0):.0f}/{c.max_hp:.0f}") + " "
                + style.bar(c.hp, c.max_hp) + "\n" + style.stat("CE", f"{b.ce_pool(c):.0f}/{c.max_ce:.0f}") + " "
                + style.bar(b.ce_pool(c), c.max_ce, style.CE, style.HALF_CE) + "\n"
                + style.code(vitals(b, c) + "\n" + limb_line(b, c)))
        container = discord.ui.Container(discord.ui.TextDisplay(body[:4000]), accent_colour=style.BLURPLE)
        if self.feedback:
            container.add_item(discord.ui.TextDisplay(style.code("\n".join(self.feedback)[-1800:])))
            self.feedback = []
        acts = self._available()[:25]
        if acts:
            sel = discord.ui.Select(placeholder="Gather for a technique..." if p.kind == "channel" else "Choose an action...",
                                    options=[discord.SelectOption(
                                        label=a.name[:100], value=a.key, default=a.key == self.act_key,
                                        description=self._describe(a)[:100]) for a in acts])
            sel.callback = self._on_action
            container.add_item(discord.ui.ActionRow(sel))
        act = self._act()
        if p.kind == "turn" and act is not None:
            targets = self._targets(act)[:25]
            if targets:
                tsel = discord.ui.Select(placeholder="Target..." if act.target != Target.CHOICE else "Which one...",
                                         options=[discord.SelectOption(label=lab[:100], value=v, default=v == self.target)
                                                  for v, lab in targets])
                tsel.callback = self._on_target
                container.add_item(discord.ui.ActionRow(tsel))
            if act.target == Target.ENEMY and self.target:
                psel = discord.ui.Select(placeholder="Body part (default torso)...",
                                         options=[discord.SelectOption(label=lab, value=v, default=v == self.part)
                                                  for v, lab in self._parts()])
                psel.callback = self._on_part
                container.add_item(discord.ui.ActionRow(psel))
        if p.kind == "turn":
            guards = self._reactions()[:25]
            if guards:
                dsel = discord.ui.Select(placeholder="...or defend this round with...",
                                         options=[discord.SelectOption(label=a.name[:100], value=a.key,
                                                                       description=(a.desc or "")[:100] or None)
                                                  for a in guards])
                dsel.callback = self._on_defend
                container.add_item(discord.ui.ActionRow(dsel))
        row = discord.ui.ActionRow()
        if p.kind == "turn":
            row.add_item(self._button("Commit", discord.ButtonStyle.green, self._on_commit, disabled=act is None))
            if act is not None and act.can_chant:
                row.add_item(self._button("Chant: on" if self.chant else "Chant: off",
                                          discord.ButtonStyle.blurple if self.chant else discord.ButtonStyle.secondary,
                                          self._on_chant))
            row.add_item(self._button("Wait", discord.ButtonStyle.secondary, self._line("wait")))
            row.add_item(self._button("Flee", discord.ButtonStyle.red, self._line("flee")))
        else:
            row.add_item(self._button("Gather", discord.ButtonStyle.green, self._on_commit, disabled=act is None))
            row.add_item(self._button("Gather nothing", discord.ButtonStyle.secondary, self._line("none")))
        container.add_item(row)
        info = discord.ui.ActionRow()
        info.add_item(self._button("Status", discord.ButtonStyle.secondary, self._line("status"), emoji="📋"))
        info.add_item(self._button("All actions", discord.ButtonStyle.secondary, self._line("actions"), emoji="📜"))
        info.add_item(self._button("Type a command", discord.ButtonStyle.secondary, self._on_modal, emoji="⌨️"))
        info.add_item(self._button("Help", discord.ButtonStyle.secondary, self._on_help, emoji="❔"))
        container.add_item(info)
        view.add_item(container)
        view.interaction_check = self._check
        return view

    def _describe(self, a) -> str:
        ce, sta = self.b.costs(self.c, a)
        when = self.b.timing(self.c, a)
        bits = [f"{ce} CE" if ce else "", f"{sta} STA" if sta else "", f"pow {a.power:g}" if a.power else "",
                "ranged" if a.rng else "", "chant ok" if a.can_chant else "",
                f"lands {when:.2f}" + (" (next round)" if when >= 1 else "")]
        return " · ".join(x for x in bits if x) or Kind(a.kind).name.lower()

    @staticmethod
    def _button(label, style_, callback, disabled=False, emoji=None) -> discord.ui.Button:
        btn = discord.ui.Button(label=label, style=style_, disabled=disabled, emoji=emoji)
        btn.callback = callback
        return btn

    async def _check(self, itx: discord.Interaction) -> bool:
        if str(itx.user.id) != self.p.user_id:
            await itx.response.send_message("These are not your controls.", ephemeral=True)
            return False
        if not self.p.open:
            await itx.response.edit_message(view=style.panel(None, None, "That moment has passed.",
                                                             accent=style.ASH, thumbnail=False))
            return False
        if self.p.busy:
            await itx.response.send_message("Still working on your last command.", ephemeral=True)
            return False
        return True

    # ---- callbacks ------------------------------------------------------------------------
    async def _on_action(self, itx: discord.Interaction) -> None:
        self.act_key = itx.data["values"][0]
        act = self._act()
        targets = self._targets(act)
        self.target = targets[0][0] if len(targets) == 1 else None
        self.part, self.chant = "torso", False
        await itx.response.edit_message(view=self.render())

    async def _on_target(self, itx: discord.Interaction) -> None:
        self.target = itx.data["values"][0]
        await itx.response.edit_message(view=self.render())

    async def _on_part(self, itx: discord.Interaction) -> None:
        self.part = itx.data["values"][0]
        await itx.response.edit_message(view=self.render())

    async def _on_chant(self, itx: discord.Interaction) -> None:
        self.chant = not self.chant
        await itx.response.edit_message(view=self.render())

    async def _on_defend(self, itx: discord.Interaction) -> None:
        await self.submit(itx, f"defend {itx.data['values'][0]}")

    async def _on_commit(self, itx: discord.Interaction) -> None:
        act = self._act()
        if act is None:
            await itx.response.send_message("Choose something first.", ephemeral=True)
            return
        if self.p.kind == "channel":
            await self.submit(itx, f"channel {act.key}")
            return
        line = f"use {act.key}"
        if act.target == Target.CHOICE:
            if not self.target:
                await itx.response.send_message("Choose which one first.", ephemeral=True)
                return
            line += f" {self.target}"
        elif self.target:
            line += f" {self.target}"
            if act.target == Target.ENEMY:
                line += f" {self.part}"
        if self.chant:
            line += " chant"
        await self.submit(itx, line)

    async def _on_modal(self, itx: discord.Interaction) -> None:
        await itx.response.send_modal(CommandModal(self))

    async def _on_help(self, itx: discord.Interaction) -> None:
        await itx.response.send_message(view=style.panel(None, "Battle", style.code(BATTLE_HELP[:3900]),
                                                         thumbnail=False), ephemeral=True)

    def _line(self, line: str):
        async def callback(itx: discord.Interaction) -> None:
            await self.submit(itx, line)
        return callback

    async def submit(self, itx: discord.Interaction, line: str) -> None:
        """Hand a command line to the battle thread and show what came of it."""
        if not self.p.open or self.p.busy:
            await itx.response.send_message("That moment has passed." if not self.p.open
                                            else "Still working on your last command.", ephemeral=True)
            return
        await itx.response.defer()
        fut = asyncio.get_running_loop().create_future()
        self.p.busy = True
        self.p.requests.put((line, fut))
        try:
            text, done = await asyncio.wait_for(fut, timeout=max(self.io.ask_timeout, 30) + 60)
        except asyncio.TimeoutError:
            self.p.busy = False
            return
        listing = line.split()[0] in ("status", "actions", "help")
        if listing and text:                              # long read-outs go in their own messages
            for piece in style.chunks(text.split("\n"), 3800):
                await itx.followup.send(view=style.panel(None, None, style.code(piece), thumbnail=False),
                                        ephemeral=True)
            text = ""
        if done:
            await itx.edit_original_response(view=style.panel(
                None, None, f"**Committed:** `{line}`" + (f"\n{style.code(text)}" if text.strip() else ""),
                accent=style.ASH, thumbnail=False))
            return
        if text:
            self.feedback.append(text)
        if self.p.open:
            await itx.edit_original_response(view=self.render())
