"""/learn (paged help, like the original utils cog) and the owner's ,colony command."""
from __future__ import annotations

import discord
from discord.ext import commands

from ...cli import BATTLE_HELP, WORLD_HELP
from ...rarity import class_odds, technique_odds
from ...techniques import TECHNIQUES
from .. import style
from .character import SHORT_CLASS


def creation_pages() -> list:
    pages = [style.heading("How to create a player", 2) + "\n"
             "Use `/create` and press **Spin**. The culling game rolls your class, then a technique your class "
             "can awaken - at the same odds the bot has always used. One character per colony (server); "
             "`/delete` lets you start again.\n\n" + style.heading("Class odds", 3) + "\n```py\n"
             + "\n".join(f"* {SHORT_CLASS[k]}: {p:.1%}" for k, p in sorted(class_odds().items(), key=lambda x: -x[1]))
             + "```\nA sorcerer who rolls Copy or Construction has a 1 in 2 chance of the **Six Eyes** "
             "(Limitless always has them): the best cursed energy efficiency and recovery there is."]
    for pclass in class_odds():
        odds = sorted(technique_odds(pclass).items(), key=lambda x: x[1])
        pages.append(style.heading(f"{SHORT_CLASS[pclass]} techniques", 2) + "\n```py\n"
                     + "\n".join(f"{TECHNIQUES[k].name:<32} {p:6.2%}" for k, p in odds) + "```")
    return pages


def text_pages(text: str, title: str) -> list:
    return [style.heading(title, 2) + "\n" + style.code(p.rstrip("\n")) for p in style.chunks(text.split("\n"), 3600)]


class Pager(discord.ui.LayoutView):
    """The original Pagination (◀️ ▶️ ⏭️, author only) as a Components V2 view."""

    def __init__(self, bot, author_id: int, pages: list, index: int = 0):
        super().__init__(timeout=100)
        self.bot, self.author_id, self.pages, self.index = bot, author_id, pages, index
        container = discord.ui.Container(accent_colour=style.BLURPLE)
        container.add_item(discord.ui.TextDisplay(pages[index][:4000]))
        container.add_item(discord.ui.TextDisplay(f"-# Page {index + 1}/{len(pages)}"))
        if len(pages) > 1:
            row = discord.ui.ActionRow()
            for emoji, step, disabled in (("◀️", -1, index == 0), ("▶️", 1, index == len(pages) - 1),
                                          ("⏮️" if index > len(pages) // 2 else "⏭️", 0, False)):
                b = discord.ui.Button(emoji=emoji, style=discord.ButtonStyle.blurple, disabled=disabled)
                b.callback = self._go(step)
                row.add_item(b)
            container.add_item(row)
        self.add_item(container)

    async def interaction_check(self, itx: discord.Interaction) -> bool:
        if itx.user.id != self.author_id:
            await itx.response.send_message(embed=discord.Embed(
                description="Only the author of the command can perform this action.", color=16711680), ephemeral=True)
            return False
        return True

    def _go(self, step: int):
        async def cb(itx: discord.Interaction):
            n = len(self.pages)
            i = (self.index + step) if step else (0 if self.index > n // 2 else n - 1)
            await itx.response.edit_message(view=Pager(self.bot, self.author_id, self.pages, max(0, min(n - 1, i))))
        return cb


class Utils(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_group(name="learn", description="Learn how to play the game", invoke_without_command=True)
    async def learn(self, ctx: commands.Context) -> None:
        await ctx.send(view=style.panel(self.bot, "Tutorial", "Choose a game concept to learn about!\n"
                                        "`/learn create` · `/learn colony` · `/learn battle` · `/learn lobby`"),
                       ephemeral=True)

    @learn.command(name="create", description="Learn how to create a character")
    async def create(self, ctx):
        await ctx.send(view=Pager(self.bot, ctx.author.id, creation_pages()), ephemeral=True)

    @learn.command(name="colony", description="Learn the colony commands")
    async def colony(self, ctx):
        intro = (style.heading("Playing the colony", 2) + "\nEvery colony command is a slash command (`/look`, "
                 "`/go`, `/search`, `/shop`...), or type any of them with `/do` (or `,c`): `/do break 4`.\n"
                 "Commands that take time (moving, waiting, searching) let the curses move too. **Fights need a "
                 "lobby**: if you are on a lobby team and curses reach you, the fight starts in the lobby's thread; "
                 "if you are not in a lobby, they pass you by (see `/learn lobby`).")
        await ctx.send(view=Pager(self.bot, ctx.author.id, [intro] + text_pages(WORLD_HELP, "Colony commands")),
                       ephemeral=True)

    @learn.command(name="battle", description="Learn how battles work")
    async def battle(self, ctx):
        intro = (style.heading("Fighting", 2) + "\nWhen it is your move the bot pings you: press **Open controls**. "
                 "Pick an action, a target and a body part, then **Commit** - or pick a defence. In the channel phase "
                 "you gather cursed energy for a technique first. **Type a command** accepts anything below.")
        await ctx.send(view=Pager(self.bot, ctx.author.id, [intro] + text_pages(BATTLE_HELP, "Battle commands")),
                       ephemeral=True)

    @learn.command(name="lobby", description="Learn how lobbies work")
    async def lobby(self, ctx):
        await ctx.send(view=Pager(self.bot, ctx.author.id, [
            style.heading("Lobbies", 2) + "\n**Fights need a lobby.** Outside one you can move and do everything "
            "else, but no curse or player can attack you, and you can't attack anyone.\n"
            "`/lobby create` opens a lobby thread. Join a team and Ready Up. The owner then picks:\n"
            "* **Hunt** - fight the curses at the owner's node, with every lobby player there (saved)\n"
            "* **PvP** - Team A against Team B at the owner's node (saved; Judgeman hears of it)\n"
            "* **Spar** - practice against opponents the owner adds (nothing is saved)\n"
            "Curses that reach lobby players while time passes fight them in the lobby's thread. "
            "`/lobby leave` takes you out of reach."]),
            ephemeral=True)

    @commands.command(name="colony", description="Set up a colony for every server (owner only)")
    async def colony_setup(self, ctx: commands.Context) -> None:
        if not await self.bot.is_owner(ctx.author):
            await ctx.send("You are not the owner of this bot")
            return
        for guild in self.bot.guilds:
            self.bot.runtime.session(guild)
        await ctx.send(f"Colonies ready for {len(self.bot.guilds)} server(s).")

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        self.bot.runtime.session(guild)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Utils(bot))
