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
        with self._lock:
            lines, self.public = self.public, []
        text = "\n".join(lines).strip("\n")
        for piece in style.chunks(text.split("\n"), 3900):
            self._send(lambda piece=piece: style.panel(None, None, style.code(piece.rstrip("\n")),
                                                        accent=style.ASH, thumbnail=False))

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
                f"You have {int(limit)} seconds.")
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
                p.busy = False
                if reply is not None:
                    self.loop.call_soon_threadsafe(_resolve, reply, ("\n".join(out), done))
                if done:
                    break
        finally:
            p.open = False
            self.prompts.pop(uid, None)
            if call is not None:
                done_text = f"~~Round {b.round}: {c.name}'s {'channel phase' if kind == 'channel' else 'turn'}~~ - done."
                self._edit(call, lambda: style.panel(None, None, done_text, accent=style.ASH, thumbnail=False))

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
        if k is None:
            self._edit(msg, lambda: style.panel(None, None, f"<@{uid}> {prompt}\n*No answer: instinct decides.*",
                                                accent=style.ASH, thumbnail=False))
        return k


def _resolve(fut: asyncio.Future, value) -> None:
    if not fut.done():
        fut.set_result(value)


async def _quiet_edit(message: discord.Message, view) -> None:
    try:
        await message.edit(view=view)
    except discord.HTTPException:
        pass


async def run_battle(b, io: DiscordIO) -> dict:
    """Play a battle to the end in a worker thread; returns ``Battle.finish()``'s result."""
    try:
        return await asyncio.to_thread(b.run)
    finally:
        await asyncio.to_thread(io.flush)


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
                 "**Commit an action or a defence.**" + (" Domain: " + b.domain.name if b.domain else ""))
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
