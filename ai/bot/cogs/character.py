"""/create, /profile, /delete, /mod - the original character cog on the ai engine.

Creation keeps the original bot's odds exactly (ai/rarity.py): the class roll (Sorcerer, Curse,
Reincarnate), the per-class technique rarities, and the Six Eyes chance for copy/construction.
"""
from __future__ import annotations

import time

import discord
import numpy as np
from discord.ext import commands

from ...constants import CLASS_NAME, GRADE_NAME, DAY, PClass, Stat
from ...data import ITEMS
from ... import oldstats
from ...effects import tame_all
from ...rarity import (class_odds, class_rarity_of, rarity_of, roll_class, roll_six_eyes, roll_technique,
                       technique_odds)
from ...records import PlayerRecord, grade_for, has_six_eyes, roll_vessel, xp_to_next
from ...techniques import TECHNIQUES
from .. import style

SHORT_CLASS = {PClass.SORCERER: "Sorcerer", PClass.CURSED_SPIRIT: "Curse", PClass.REINCARNATED: "Reincarnate",
               PClass.MUTANT: "Mutant"}


def odds_text() -> tuple:
    classes = "\n".join(f"* {SHORT_CLASS[k]}: {p:.1%} ({class_rarity_of(k)})"
                        for k, p in sorted(class_odds().items(), key=lambda x: -x[1]))
    legends = []
    for pclass in class_odds():
        rare = sorted(technique_odds(pclass).items(), key=lambda x: x[1])[:3]
        legends.append(f"- **{SHORT_CLASS[pclass]}:**\n```py\n" + "\n".join(
            f"* {TECHNIQUES[k].name}: {p:.2%}" for k, p in rare) + "```")
    return classes, "\n".join(legends)


def sheet(rec: PlayerRecord, colony_name: str, now: float, inactivity_days: int, in_lobby: bool = False) -> str:
    """The profile, in the original `Label:` **value** style."""
    spec = rec.to_spec()
    st = spec.stats
    cond = rec.condition or {"hp": 1.0, "scar": 0.0}
    mx_hp = st[Stat.MAX_HP] * (1 - cond["scar"])
    hp = mx_hp * cond["hp"]
    ce = rec.rested_ce(now) * st[Stat.MAX_CE]
    left = inactivity_days - (now - rec.last_score_ts) / DAY
    techs = ", ".join(TECHNIQUES[t].name for t in rec.techniques) or "none"
    lines = [
        style.heading(rec.name, 2),
        style.stat("Colony", colony_name),
        style.stat("Level", f"{rec.level} ({rec.xp}/{xp_to_next(rec.level)} XP)"),
        style.stat("Grade", GRADE_NAME[grade_for(rec.level, spec.techniques)]),
        style.stat("Class", CLASS_NAME[rec.pclass]),
        style.stat("Technique", techs),
        style.stat("Six Eyes", has_six_eyes(rec.techniques, rec.six_eyes)),
        f"{style.stat('Health', f'{hp:.0f}/{mx_hp:.0f}')} {style.bar(hp, mx_hp)}",
        f"{style.stat('Energy', f'{ce:.0f}/{st[Stat.MAX_CE]:.0f}')} {style.bar(ce, st[Stat.MAX_CE], style.CE, style.HALF_CE)}",
        (style.stat("Rolled", f"HP {o['hp']} · CE {o['ce']} · Strength {o['str']} · Speed {o['spd']}")
         if (o := rec.old_stats) else ""),
        style.stat("In battle", f"Strength {st[Stat.STR]:.0f} · Speed {st[Stat.SPD]:.0f} · "
                                f"Durability {st[Stat.DUR]:.0f} · Perception {st[Stat.PER]:.0f}"),
        style.stat("Game Points", rec.points),
        style.stat("Condition", rec.condition_text()),
        style.stat("Gear", ", ".join(f"{k}: {ITEMS[v].name if v in ITEMS else v}" for k, v in rec.equipment.items() if v)
                   or "none"),
        style.stat("Bag", ", ".join(ITEMS[k].name if k in ITEMS else k for k in rec.inventory) or "empty"),
        style.stat("Kills", f"{rec.kills['players']} players, {rec.kills['spirits']} curses"),
        style.stat("Record", rec.crimes.summary()),
        style.stat("Lobby", "in a lobby: curses and players can fight you" if in_lobby else
                   "not in a lobby: nothing can attack you, and you can't fight") if rec.alive else "",
        style.stat("Status", "Active" if rec.alive else "Dead")
        + (f"  ({left:.1f} days until technique removal)" if rec.alive else ""),
    ]
    return "\n".join(x for x in lines if x)


class CreateView(discord.ui.LayoutView):
    """The original CreatePromptLayout: welcome, odds, and a Spin button only the invoker can press."""

    def __init__(self, cog: "Character", user: discord.abc.User, guild: discord.Guild):
        super().__init__(timeout=300)
        self.cog, self.user, self.guild = cog, user, guild
        url = style.avatar_url(cog.bot)
        classes, legends = odds_text()
        container = discord.ui.Container(discord.ui.TextDisplay(style.heading("Welcome to the Culling Games")),
                                         accent_colour=style.BLURPLE)
        text2 = discord.ui.TextDisplay(f"{style.heading('Class Odds', 3)}\n```py\n{classes}```\n"
                                       "Your class decides which techniques you can awaken.")
        text3 = discord.ui.TextDisplay(f"{style.heading('Rarest Techniques', 3)}\n{legends}\n"
                                       "Limitless always comes with the **Six Eyes**; a sorcerer who rolls Copy or "
                                       "Construction has a 1 in 2 chance of them.")
        for t in (text2, text3):
            container.add_item(discord.ui.Section(t, accessory=discord.ui.Thumbnail(url)) if url else t)
        self.add_item(container)
        spin = discord.ui.Button(label="Spin", style=discord.ButtonStyle.blurple, emoji=style.SLOTS)
        spin.callback = self.spin
        self.add_item(discord.ui.ActionRow(spin))

    async def spin(self, itx: discord.Interaction) -> None:
        if itx.user.id != self.user.id:
            await itx.response.send_message("You did not invoke this prompt. Use `/create` yourself.", ephemeral=True)
            return
        await itx.response.defer()
        result = await self.cog.create(self.guild, itx.channel, self.user)
        self.stop()
        await itx.edit_original_response(view=result)


class Character(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.rng = np.random.default_rng()

    @property
    def rt(self):
        return self.bot.runtime

    async def create(self, guild: discord.Guild, channel, user: discord.abc.User) -> discord.ui.LayoutView:
        rng = self.rng
        pclass = roll_class(rng)
        tech = roll_technique(pclass, rng)
        six = roll_six_eyes(pclass, tech, rng)
        rec = PlayerRecord(str(guild.id), str(user.id), user.display_name, int(pclass), techniques=[tech],
                           six_eyes=six)
        rec.old_stats = oldstats.roll(pclass, tech, six, rng)              # the original stat spin
        rec.vessel = roll_vessel(rng)
        notes = []
        if tech == "ten_shadows" and rec.unlock_level >= 6:
            tame_all(rec.tech_state)
        if TECHNIQUES[tech].tool:
            rec.equipment["weapon"] = TECHNIQUES[tech].tool
            notes.append(f"Your technique comes with a cursed tool: **{ITEMS[TECHNIQUES[tech].tool].name}**.")
        if rec.vessel >= 20:
            notes.append("You are one in twenty: a **strong vessel**. Your body could cage all of Sukuna's fingers.")

        def join(game):
            out: list = []
            ok = game.add_player(rec, lambda s: out.append(str(s)))
            return ok, out
        ran, res = await self.rt.run(guild, channel, join, wait=True)
        ok, out = res
        if not ok:
            return style.panel(self.bot, "Create a character",
                               "You cannot create more than one player per colony. (`/delete` your current one first.)",
                               accent=style.DANGER)
        t = TECHNIQUES[tech]
        body = "\n".join([
            f"* {style.stat('Name', rec.name)}",
            f"* {style.stat('Level', rec.level)}",
            f"* {style.stat('Technique', t.name)}",
            f"* {style.stat('Technique Grade', GRADE_NAME[t.grade])}",
            f"* {style.stat('HP', rec.old_stats['hp'])}",
            f"* {style.stat('CE', rec.old_stats['ce'])}",
            f"* {style.stat('Class', SHORT_CLASS[pclass])}",
            f"* {style.stat('Six Eyes', has_six_eyes(rec.techniques, rec.six_eyes))}",
            f"* {style.stat('Speed', rec.old_stats['spd'])}",
            f"* {style.stat('Strength', rec.old_stats['str'])}",
            f"* {style.stat('Technique Rarity', rarity_of(pclass, tech))}",
            f"* {style.stat('Class Rarity', class_rarity_of(pclass))}",
        ])
        extra = "\n".join(notes + out + [f"*{t.desc}*" if t.desc else "", "Use `/profile` to see your character "
                                         "and `/learn colony` to start playing."])
        return style.panel(self.bot, "Welcome to the Culling Games", body, extra)

    @commands.hybrid_command(name="create", description="Create your player in the culling games! (one per colony)")
    @commands.guild_only()
    async def create_cmd(self, ctx: commands.Context) -> None:
        existing = self.rt.store.get_player(str(ctx.guild.id), str(ctx.author.id))
        if existing is not None and existing.alive:
            await ctx.send(view=style.panel(self.bot, "Create a character",
                                            f"You already have **{existing.name}** in this colony.",
                                            accent=style.DANGER), ephemeral=True)
            return
        await ctx.send(view=CreateView(self, ctx.author, ctx.guild))

    @commands.hybrid_command(name="profile", description="View your player profile, or someone else's!")
    @commands.guild_only()
    async def profile(self, ctx: commands.Context, user: discord.User = None) -> None:
        user = user or ctx.author
        rec = self.rt.store.get_player(str(ctx.guild.id), str(user.id))
        if rec is None:
            await ctx.send("Player does not exist in this colony.", ephemeral=True)
            return
        game = self.rt.sessions.get(str(ctx.guild.id))
        if game is not None:                                    # the live copy, if the colony is loaded
            rec = next((p for p in game.players if p.user_id == str(user.id)), rec)
        now = game.now if game is not None else time.time()
        colony = game.colony if game is not None else self.rt.store.get_colony(str(ctx.guild.id))
        name = colony.name if colony else ctx.guild.name
        days = colony.inactivity_days if colony else 19
        in_lobby = self.rt.lobby_of(ctx.guild.id, user.id) is not None
        await ctx.send(view=style.panel(self.bot, "Player Profile", sheet(rec, name, now, days, in_lobby)),
                       ephemeral=True)

    @commands.hybrid_command(name="delete", description="Delete your player in the culling games!")
    @commands.guild_only()
    async def delete(self, ctx: commands.Context) -> None:
        await ctx.defer(ephemeral=True)
        ok, rec = await self.rt.run(ctx.guild, ctx.channel, lambda game: game.remove_player(ctx.author.id))
        if not ok:
            await ctx.send("The colony is busy (a fight is on). Try again when it is over.", ephemeral=True)
        elif rec is None:
            await ctx.send("You do not have a player in this colony.", ephemeral=True)
        else:
            await ctx.send(view=style.panel(self.bot, "Deleted player",
                                            f"Deleted **{rec.name}** from {ctx.guild.name}."), ephemeral=True)

    @commands.hybrid_command(name="mod", description="(Managers) Modify a player's points, xp or level")
    @commands.guild_only()
    async def mod(self, ctx: commands.Context, stat: str, amount: int, user: discord.User = None) -> None:
        user = user or ctx.author
        colony = self.rt.session(ctx.guild).colony
        allowed = (await self.bot.is_owner(ctx.author) or str(ctx.author.id) in colony.managers
                   or ctx.author.guild_permissions.administrator)
        if not allowed:
            await ctx.send("Only the bot owner, a colony manager or a server admin can do that.", ephemeral=True)
            return
        stat = stat.lower()
        if stat not in ("points", "xp", "level"):
            await ctx.send("Stat must be one of: points, xp, level.", ephemeral=True)
            return

        def apply(game):
            rec = game.player(user.id)
            if rec is None:
                return None
            if stat == "points":
                rec.points = max(0, rec.points + amount)
            elif stat == "xp":
                rec.gain_xp(max(0, amount))
            else:
                rec.level = max(1, rec.level + amount)
            game.save()
            return rec
        ok, rec = await self.rt.run(ctx.guild, ctx.channel, apply)
        if not ok:
            await ctx.send("The colony is busy. Try again in a moment.", ephemeral=True)
        elif rec is None:
            await ctx.send("That user has no living player here.", ephemeral=True)
        else:
            await ctx.send(view=style.panel(self.bot, "Player Profile",
                                            sheet(rec, colony.name, self.rt.session(ctx.guild).now,
                                                  colony.inactivity_days)), ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Character(bot))
