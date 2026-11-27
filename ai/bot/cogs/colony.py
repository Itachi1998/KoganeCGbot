"""The colony: map, movement, curses closing in, the shop, the medic, rules - as slash commands.

Every command here is a line for ai/colony.py's ColonySession.command, so Discord and the CLI play
the same game. Commands that let time pass can start a fight; it is played in the channel where
the command was used, through the battle controls (ai/bot/bridge.py).
"""
from __future__ import annotations

from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from ...data import ITEMS
from ...colony import skills_text
from ...rules import RULES
from ...skills import SKILLS
from .. import style

INFO = ("look", "map", "me", "medic", "fingers", "shop", "market", "rules", "scouts", "puppets", "players",
        "leaderboard", "skills")


async def reply(ctx: commands.Context, view: discord.ui.LayoutView, ephemeral: bool = False) -> None:
    """Send, falling back to the channel when the interaction has expired (a long fight)."""
    try:
        await ctx.send(view=view, ephemeral=ephemeral)
    except discord.HTTPException:
        await ctx.channel.send(view=view)


class ShopView(discord.ui.LayoutView):
    """The original Cursed Tool Shop layout: header + thumbnail, separator, one block per tool, a select."""

    def __init__(self, cog: "Colony", ctx: commands.Context, note: str = ""):
        super().__init__(timeout=180)
        self.cog, self.ctx = cog, ctx
        url = style.avatar_url(cog.bot)
        head = discord.ui.TextDisplay(style.heading("Cursed Tool Shop") + (f"\n{note}" if note else ""))
        container = discord.ui.Container(discord.ui.Section(head, accessory=discord.ui.Thumbnail(url)) if url else head)
        container.add_item(discord.ui.Separator(spacing=discord.SeparatorSpacing.large))
        stock = [it for it in ITEMS.values() if it.shop]
        blocks = [f"### `{it.name}`\n> **Cost:** `{it.cost}` · **Sells for:** `{it.cost // 2}` · *{it.slot}*\n> {it.desc}"
                  for it in stock]
        for piece in style.chunks(blocks, 3500):
            container.add_item(discord.ui.TextDisplay(piece))
        container.add_item(discord.ui.Separator(spacing=discord.SeparatorSpacing.large))
        sel = discord.ui.Select(placeholder="Buy a cursed tool...", options=[
            discord.SelectOption(label=it.name[:100], value=it.key, description=f"{it.cost} points")
            for it in stock[:25]])
        sel.callback = self.buy
        container.add_item(discord.ui.ActionRow(sel))
        self.add_item(container)
        close = discord.ui.Button(label="Close", style=discord.ButtonStyle.blurple)
        close.callback = self.close
        self.add_item(discord.ui.ActionRow(close))

    async def buy(self, itx: discord.Interaction) -> None:
        await itx.response.defer(ephemeral=True, thinking=True)
        text = await self.cog.rt.command(itx.guild, itx.channel, itx.user.id, f"buy {itx.data['values'][0]}")
        await itx.followup.send(view=style.panel(None, None, text or "The colony is busy. Try again in a moment.",
                                                 thumbnail=False), ephemeral=True)

    async def close(self, itx: discord.Interaction) -> None:
        await itx.response.edit_message(view=style.panel(None, None, "`Shop closed`", thumbnail=False))
        self.stop()


class SkillsView(discord.ui.LayoutView):
    """Skill points: pick a skill, spend 1 / 5 / 10. Only the player who opened it can use it."""

    def __init__(self, cog: "Colony", uid: int, text: str, chosen: Optional[str] = None, note: str = ""):
        super().__init__(timeout=300)
        self.cog, self.uid, self.chosen = cog, uid, chosen
        container = discord.ui.Container(accent_colour=style.BLURPLE)
        container.add_item(discord.ui.TextDisplay(style.heading("Skills") + "\n" + style.code(text)[:3800]))
        if note:
            container.add_item(discord.ui.TextDisplay(f"> {note}"))
        sel = discord.ui.Select(placeholder="Choose a skill to train...", options=[
            discord.SelectOption(label=name, value=key, description=what[:100], default=key == chosen)
            for key, (name, what) in SKILLS.items()])
        sel.callback = self.pick
        container.add_item(discord.ui.ActionRow(sel))
        row = discord.ui.ActionRow()
        for n in (1, 5, 10):
            b = discord.ui.Button(label=f"+{n}", style=discord.ButtonStyle.green, disabled=chosen is None)
            b.callback = self.spend(n)
            row.add_item(b)
        container.add_item(row)
        self.add_item(container)

    async def interaction_check(self, itx: discord.Interaction) -> bool:
        if itx.user.id != self.uid:
            await itx.response.send_message("These are not your skills.", ephemeral=True)
            return False
        return True

    def _text(self, guild) -> str:
        me = self.cog.rt.session(guild).player(self.uid)
        return skills_text(me) if me else "You have no living character."

    async def pick(self, itx: discord.Interaction) -> None:
        await itx.response.edit_message(view=SkillsView(self.cog, self.uid, self._text(itx.guild),
                                                        itx.data["values"][0]))

    def spend(self, n: int):
        async def cb(itx: discord.Interaction) -> None:
            await itx.response.defer()
            note = await self.cog.rt.command(itx.guild, itx.channel, self.uid, f"upgrade {self.chosen} {n}")
            await itx.edit_original_response(view=SkillsView(self.cog, self.uid, self._text(itx.guild), self.chosen,
                                                             note or "The colony is busy - try again in a moment."))
        return cb


class Colony(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @property
    def rt(self):
        return self.bot.runtime

    async def do(self, ctx: commands.Context, line: str, title: Optional[str] = None) -> None:
        """Run one colony command and show what came of it."""
        word = line.split()[0].lower() if line.split() else ""
        private = word in INFO
        await ctx.defer(ephemeral=private)
        text = await self.rt.command(ctx.guild, ctx.channel, ctx.author.id, line)
        if text is None:
            await reply(ctx, style.panel(self.bot, "Colony busy",
                                         "Something is already happening in this colony (most likely a fight). "
                                         "Your command was not run - try again when it is over.",
                                         accent=style.DANGER, thumbnail=False), ephemeral=True)
            return
        game = self.rt.session(ctx.guild)
        me = game.player(ctx.author.id)
        where = (f"day {game.day()} · {me.name} @ {game.world.nodes[me.node].name} · {me.points} pts"
                 if me is not None else f"day {game.day()}")
        pieces = style.chunks(text.split("\n"), 3700)
        for i, piece in enumerate(pieces):
            await reply(ctx, style.panel(self.bot if i == 0 else None, (title or game.colony.name) if i == 0 else None,
                                         f"-# {where}" if i == 0 else "", style.code(piece.rstrip("\n")),
                                         thumbnail=i == 0), ephemeral=private)

    # ---- the generic one ---------------------------------------------------------------------
    @commands.hybrid_command(name="do", aliases=["c"], description="Any colony command, typed (see /learn colony)")
    @commands.guild_only()
    @app_commands.describe(command="e.g. `go 3`, `break 4`, `sell knife 20`, `order 2 auto`")
    async def do_cmd(self, ctx: commands.Context, *, command: str) -> None:
        await self.do(ctx, command)

    # ---- looking around ----------------------------------------------------------------------
    @commands.hybrid_command(name="look", description="What is here: exits, objects, players, curses nearby")
    @commands.guild_only()
    async def look(self, ctx):
        await self.do(ctx, "look")

    @commands.hybrid_command(name="map", description="The colony map (you are marked *)")
    @commands.guild_only()
    async def map_cmd(self, ctx):
        await self.do(ctx, "map")

    @commands.hybrid_command(name="me", description="Your full character sheet")
    @commands.guild_only()
    async def me(self, ctx):
        await self.do(ctx, "me", "Character sheet")

    @commands.hybrid_command(name="players", description="Who is playing in this colony")
    @commands.guild_only()
    async def players(self, ctx):
        await self.do(ctx, "players")

    # ---- moving and acting -----------------------------------------------------------------
    @commands.hybrid_command(name="go", description="Move to a connected node (entering a building is trespass)")
    @commands.guild_only()
    async def go(self, ctx, node: int):
        await self.do(ctx, f"go {node}")

    @commands.hybrid_command(name="wait", description="Let hours pass; curses keep moving toward you")
    @commands.guild_only()
    async def wait(self, ctx, hours: Optional[int] = 1):
        await self.do(ctx, f"wait {max(1, min(int(hours or 1), 24))}")

    @commands.hybrid_command(name="rest", description="Claim this hideout and lie low (does not heal)")
    @commands.guild_only()
    async def rest(self, ctx):
        await self.do(ctx, "rest")

    @commands.hybrid_command(name="search", description="Turn this node over for ordinary things")
    @commands.guild_only()
    async def search(self, ctx):
        await self.do(ctx, "search")

    @commands.hybrid_command(name="interact", description="Break or loot an object here (Judgeman takes note)")
    @commands.guild_only()
    @app_commands.choices(verb=[app_commands.Choice(name="break", value="break"),
                                app_commands.Choice(name="loot", value="loot")])
    async def interact(self, ctx, verb: str, obj: int):
        await self.do(ctx, f"{verb} {obj}")

    # ---- healing -----------------------------------------------------------------------------
    @commands.hybrid_command(name="heal", description="Reverse cursed technique on yourself or a player here")
    @commands.guild_only()
    async def heal(self, ctx, player: Optional[discord.Member] = None):
        name = self._name(ctx, player) if player else ""
        await self.do(ctx, f"heal {name}".strip())

    @commands.hybrid_command(name="medic", description="Where the colony's medic was last seen")
    @commands.guild_only()
    async def medic(self, ctx):
        await self.do(ctx, "medic")

    @commands.hybrid_command(name="treat", description="Be treated by the medic (same node)")
    @commands.guild_only()
    async def treat(self, ctx):
        await self.do(ctx, "treat")

    @commands.hybrid_command(name="use", description="Use a supply on yourself (a bandage...)")
    @commands.guild_only()
    async def use(self, ctx, item: str):
        await self.do(ctx, f"use {item}")

    # ---- gear and trade ----------------------------------------------------------------------
    @commands.hybrid_command(name="equip", description="Equip an item from your bag (cursed tools: in your hideout)")
    @commands.guild_only()
    async def equip(self, ctx, item: str):
        await self.do(ctx, f"equip {item}")

    @commands.hybrid_command(name="unequip", description="Put away your weapon or armor")
    @commands.guild_only()
    async def unequip(self, ctx, slot: str):
        await self.do(ctx, f"unequip {slot}")

    @commands.hybrid_command(name="shop", description="The colony's Cursed Tool Shop")
    @commands.guild_only()
    async def shop(self, ctx):
        game = self.rt.session(ctx.guild)
        me = game.player(ctx.author.id)
        here = me is not None and game.world.nodes[me.node].kind == "shop"
        note = (f"You are in the shop. You have **{me.points}** points." if here else
                f"The shop is at node **{game.world.shop}**: {game.world.nodes[game.world.shop].name}. "
                "You have to be there to buy.")
        await ctx.send(view=ShopView(self, ctx, note), ephemeral=True)

    @commands.hybrid_command(name="buy", description="Buy from the shop (item key), a player here (#n) or anywhere (g<n>)")
    @commands.guild_only()
    async def buy(self, ctx, item: str):
        await self.do(ctx, f"buy {item}")

    @commands.hybrid_command(name="sell", description="Sell to the shop (half price), or list it at your price")
    @commands.guild_only()
    @app_commands.describe(global_market="list it where every colony can buy it (needs a price)")
    async def sell(self, ctx, item: str, price: Optional[int] = None, global_market: bool = False):
        await self.do(ctx, f"sell {item}" + (f" {price}" if price else "") + (" global" if global_market and price else ""))

    @commands.hybrid_command(name="market", description="What players have up for sale (here, or in every colony)")
    @commands.guild_only()
    @app_commands.choices(scope=[app_commands.Choice(name="this colony", value="colony"),
                                 app_commands.Choice(name="global (every colony)", value="global")])
    async def market(self, ctx, scope: Optional[str] = "colony"):
        await self.do(ctx, "market global" if scope == "global" else "market")

    @commands.hybrid_command(name="leaderboard", description="Top players (needs the Open Score Board rule)")
    @commands.guild_only()
    @app_commands.choices(scope=[app_commands.Choice(name="this colony", value="colony"),
                                 app_commands.Choice(name="global (every colony)", value="global")])
    async def leaderboard(self, ctx, scope: Optional[str] = "colony"):
        await self.do(ctx, "leaderboard global" if scope == "global" else "leaderboard", "Leaderboard")

    # ---- Sukuna ----------------------------------------------------------------------------------
    @commands.hybrid_command(name="fingers", description="Sukuna's fingers: what you hold, where the bearers lurk")
    @commands.guild_only()
    async def fingers(self, ctx):
        await self.do(ctx, "fingers")

    @commands.hybrid_command(name="eat", description="Eat one of Sukuna's fingers. Your body may not cage it.")
    @commands.guild_only()
    async def eat(self, ctx):
        await self.do(ctx, "eat")

    # ---- rules, points, other players ----------------------------------------------------------
    @commands.hybrid_command(name="rules", description="Colony rules in force and for sale")
    @commands.guild_only()
    async def rules(self, ctx):
        await self.do(ctx, "rules")

    @commands.hybrid_command(name="addrule", description="Add a rule to this colony (100 points)")
    @commands.guild_only()
    @app_commands.choices(rule=[app_commands.Choice(name=r.name, value=r.key) for r in RULES.values()])
    async def addrule(self, ctx, rule: str):
        await self.do(ctx, f"addrule {rule}")

    @commands.hybrid_command(name="give", description="Give points to a player (needs the Point Transfer rule)")
    @commands.guild_only()
    async def give(self, ctx, player: discord.Member, points: int):
        await self.do(ctx, f"give {self._name(ctx, player)} {points}")

    @commands.hybrid_command(name="pvp", description="Attack another player at your node")
    @commands.guild_only()
    async def pvp(self, ctx, player: discord.Member):
        if player.id == ctx.author.id:
            await ctx.send("You cannot attack yourself.", ephemeral=True)
            return
        await self.do(ctx, f"pvp {self._name(ctx, player)}")

    @commands.hybrid_command(name="transfer", description="Move to another colony (both need the Free Passage rule)")
    @commands.guild_only()
    async def transfer(self, ctx, server_id: str):
        dst = self.bot.get_guild(int(server_id)) if server_id.isdigit() else None
        if dst is None:
            await ctx.send("I am not in a server with that id.", ephemeral=True)
            return

        def move(game):
            rec = game.player(ctx.author.id)
            if rec is None:
                return "You have no living character here."
            self.rt.session(dst)                          # make sure the destination colony exists
            err = game.store.move_player(rec, str(dst.id))
            if err:
                return err
            game.players[:] = [p for p in game.players if p is not rec]
            other = self.rt.sessions.get(str(dst.id))
            if other is not None:
                other.players[:] = [p for p in other.players if p.user_id != rec.user_id] + [rec]
            return f"{rec.name} leaves {game.colony.name} for {dst.name}."
        ok, text = await self.rt.run(ctx.guild, ctx.channel, move)
        await ctx.send(text if ok else "The colony is busy. Try again in a moment.", ephemeral=True)

    # ---- skill points --------------------------------------------------------------------------
    @commands.hybrid_command(name="skills", description="Spend skill points (+10 a level to 10, +5 after)")
    @commands.guild_only()
    async def skills_cmd(self, ctx):
        game = self.rt.session(ctx.guild)
        me = game.player(ctx.author.id)
        if me is None:
            await ctx.send("You have no living character in this colony. Use `/create` first.", ephemeral=True)
            return
        await ctx.send(view=SkillsView(self, ctx.author.id, skills_text(me)), ephemeral=True)

    @commands.hybrid_command(name="upgrade", description="Spend skill points on a skill")
    @commands.guild_only()
    @app_commands.choices(skill=[app_commands.Choice(name=n, value=k) for k, (n, _) in SKILLS.items()])
    async def upgrade(self, ctx, skill: str, points: Optional[int] = 1):
        await self.do(ctx, f"upgrade {skill} {max(1, int(points or 1))}", "Skills")

    # ---- spirits, shikigami, puppets -------------------------------------------------------------
    @commands.hybrid_command(name="scouts", description="Spirits and shikigami you have out in the colony")
    @commands.guild_only()
    async def scouts(self, ctx):
        await self.do(ctx, "scouts")

    @commands.hybrid_command(name="puppets", description="Puppeteers: your puppets and banked energy")
    @commands.guild_only()
    async def puppets(self, ctx):
        await self.do(ctx, "puppets")

    def _name(self, ctx, member: discord.abc.User) -> str:
        """The colony commands find a player by the start of their character's name."""
        rec = self.rt.session(ctx.guild).player(member.id)
        return (rec.name if rec else member.display_name).split()[0]


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Colony(bot))
