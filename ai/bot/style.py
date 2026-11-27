"""The look of the original bot (cogs/*.py), in one place.

Headings are backtick-wrapped markdown (# `Welcome to the Culling Games`), stat lines are
`Label:` **value**, containers have a blurple accent and the bot's avatar as a thumbnail.
"""
from __future__ import annotations

from typing import Iterable, Optional

import discord

BLURPLE = discord.Colour.blurple()
LOBBY = discord.Colour.from_rgb(255, 251, 86)        # the lobby embed's yellow
DANGER = discord.Colour.from_rgb(255, 0, 0)
ASH = discord.Colour.ash_embed()

# Health / cursed energy bar emoji from the original battle cog.
HEART, HALF_HEART = "<:fullheart:1401327640018944070>", "<:halfheart:1401327657060270160>"
CE, HALF_CE = "<:fullce:1401327669328740405>", "<:halfce:1401327682540666951>"
SLOTS = "<a:slots:1364792630155804722>"

TEXT_LIMIT = 3800                                     # a TextDisplay holds 4000 characters


def heading(text: str, level: int = 1) -> str:
    return f"{'#' * level} `{text}`"


def stat(label: str, value) -> str:
    return f"`{label}:` **{value}**"


def bar(cur: float, mx: float, full: str = HEART, half: str = HALF_HEART, segments: int = 4) -> str:
    """Four segments and a percentage, like the original lobby/battle bars."""
    frac = 0.0 if mx <= 0 else max(0.0, min(1.0, cur / mx))
    halves = round(frac * segments * 2)
    out = full * (halves // 2) + (half if halves % 2 else "")
    return f"{out or '-'} `{frac:.0%}`"


def avatar_url(bot: discord.Client) -> Optional[str]:
    user = bot.user
    if user is None:
        return None
    return (user.avatar or user.default_avatar).url


def chunks(lines: Iterable[str], limit: int = TEXT_LIMIT) -> list:
    """Split text into pieces that fit one TextDisplay (long lines are cut)."""
    out, cur = [], ""
    for line in lines:
        for piece in [line[i:i + limit] for i in range(0, max(len(line), 1), limit)]:
            if len(cur) + len(piece) + 1 > limit:
                out.append(cur)
                cur = ""
            cur += piece + "\n"
    if cur.strip():
        out.append(cur)
    return out


def code(text: str) -> str:
    return "```\n" + text.replace("```", "'''") + "\n```"


def panel(bot: Optional[discord.Client], title: Optional[str], *texts: str, accent=BLURPLE,
          thumbnail: bool = True, rows: Iterable[discord.ui.ActionRow] = (),
          view: Optional[discord.ui.LayoutView] = None, timeout: Optional[float] = 180) -> discord.ui.LayoutView:
    """A Components V2 message in the original style: container, heading + thumbnail, text, rows."""
    view = view or discord.ui.LayoutView(timeout=timeout)
    container = discord.ui.Container(accent_colour=accent)
    url = avatar_url(bot) if (bot is not None and thumbnail) else None
    if title:
        head = discord.ui.TextDisplay(heading(title))
        container.add_item(discord.ui.Section(head, accessory=discord.ui.Thumbnail(url)) if url else head)
    for t in texts:
        if t:
            container.add_item(discord.ui.TextDisplay(t[:4000]))
    for row in rows:
        container.add_item(row)
    view.add_item(container)
    return view
