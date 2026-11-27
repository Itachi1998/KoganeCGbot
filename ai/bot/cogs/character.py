"""/create, /profile, /delete, /mod - the original character cog on the ai engine.

Creation keeps the original bot's odds exactly (ai/rarity.py): the class roll (Sorcerer, Curse,
Reincarnate), the per-class technique rarities, and the Six Eyes chance for copy/construction.
"""
from __future__ import annotations

import time
from typing import Optional

import discord
import numpy as np
from discord import app_commands
from discord.ext import commands

from ...constants import CLASS_NAME, GRADE_NAME, DAY, PClass, Stat
from ...data import ITEMS
from ... import oldstats
from ...colony import NAME_MAX, NAME_MIN, clean_name
from ...effects import tame_all
from ...rarity import (class_odds, class_rarity_of, rarity_of, roll_class, roll_six_eyes, roll_technique,
                       technique_odds, technique_pool)
from ...records import PlayerRecord, grade_for, has_six_eyes, roll_vessel, xp_to_next
from ...skills import points_through
from ...techniques import TECHNIQUES
from .. import style
from ..runtime import is_dev

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
    left = min(inactivity_days, inactivity_days - (time.time() - rec.last_score_ts) / DAY)      # real days
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
        style.stat("Skill Points", f"{rec.skill_points} to spend (/skills)") + "  "
        + " · ".join(f"{k} {v}" for k, v in rec.skills.items() if v),
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


class NameModal(discord.ui.Modal, title="Name your character"):
    name = discord.ui.TextInput(label="Character name", min_length=NAME_MIN, max_length=NAME_MAX,
                                placeholder="2-24 letters, digits or spaces")

    def __init__(self, view: "CreateView"):
        super().__init__()
        self.view = view

    async def on_submit(self, itx: discord.Interaction) -> None:
        name, why = clean_name(str(self.name.value))
        if name is None:
            await itx.response.send_message(why, ephemeral=True)
            return
        await itx.response.edit_message(view=CreateView(self.view.cog, self.view.user, self.view.guild, name))


class CreateView(discord.ui.LayoutView):
    """The original CreatePromptLayout: welcome, odds, and a Spin button only the invoker can press -
    plus the character's name, which the player may change before spinning."""

    def __init__(self, cog: "Character", user: discord.abc.User, guild: discord.Guild, name: str, note: str = ""):
        super().__init__(timeout=300)
        self.cog, self.user, self.guild, self.name = cog, user, guild, name
        url = style.avatar_url(cog.bot)
        classes, legends = odds_text()
        container = discord.ui.Container(discord.ui.TextDisplay(style.heading("Welcome to the Culling Games")),
                                         accent_colour=style.BLURPLE)
        container.add_item(discord.ui.TextDisplay(f"{style.stat('Character name', name)}"
                                                  + (f"\n> {note}" if note else "")))
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
        rename = discord.ui.Button(label="Change name", style=discord.ButtonStyle.secondary)
        rename.callback = self.rename
        self.add_item(discord.ui.ActionRow(spin, rename))

    async def interaction_check(self, itx: discord.Interaction) -> bool:
        if itx.user.id != self.user.id:
            await itx.response.send_message("You did not invoke this prompt. Use `/create` yourself.", ephemeral=True)
            return False
        return True

    async def rename(self, itx: discord.Interaction) -> None:
        await itx.response.send_modal(NameModal(self))

    async def spin(self, itx: discord.Interaction) -> None:
        await itx.response.defer()
        result = await self.cog.create(self.guild, itx.channel, self.user, self.name)
        self.stop()
        await itx.edit_original_response(view=result)


class Character(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.rng = np.random.default_rng()

    @property
    def rt(self):
        return self.bot.runtime

    async def create(self, guild: discord.Guild, channel, user: discord.abc.User, name: Optional[str] = None, *,
                     technique: Optional[str] = None, pclass: Optional[PClass] = None, level: int = 1,
                     six_eyes: Optional[bool] = None, vessel: Optional[int] = None,
                     replace: bool = False) -> discord.ui.LayoutView:
        """Make a character and put it in the colony. With no ``technique`` everything is rolled at the
        original odds (what players get); the developer command passes what it wants instead."""
        rng = self.rng
        name, why = clean_name(name if name is not None else user.display_name)
        if name is None:
            name = f"Player {str(user.id)[-4:]}"                # an unusable display name: a plain default
        dev = technique is not None
        if pclass is None:
            pclass = roll_class(rng) if not dev else next(
                (pc for pc in (PClass.SORCERER, PClass.REINCARNATED, PClass.CURSED_SPIRIT, PClass.MUTANT)
                 if technique in technique_pool(pc)), PClass.SORCERER)
        tech = technique or roll_technique(pclass, rng)
        six = roll_six_eyes(pclass, tech, rng) if six_eyes is None else bool(six_eyes)
        rec = PlayerRecord(str(guild.id), str(user.id), name, int(pclass), techniques=[tech], six_eyes=six)
        rec.old_stats = oldstats.roll(pclass, tech, six, rng)              # the original stat spin
        rec.vessel = roll_vessel(rng) if vessel is None else int(vessel)
        rec.level = max(1, min(int(level), 60))
        rec.skill_points = points_through(rec.level)
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
            if replace:
                if str(user.id) in game.in_battle:        # (its fight would write the old character back)
                    return "busy", out
                game.remove_player(user.id)
            if game.name_taken(rec.name, rec.user_id):
                return "name", out
            return ("ok" if game.add_player(rec, lambda s: out.append(str(s))) else "exists"), out
        ran, res = await self.rt.run(guild, channel, join)
        if not ran:
            return style.panel(self.bot, "Create a character", "The colony is busy. Try again in a moment.",
                               accent=style.DANGER)
        status, out = res
        if status == "name":
            return CreateView(self, user, guild, name, f"Someone here is already called **{name}**. "
                                                       f"Press **Change name** and pick another.")
        if status == "busy":
            return style.panel(self.bot, "Create a character", "Not while your character is in a fight.",
                               accent=style.DANGER)
        if status == "exists":
            return style.panel(self.bot, "Create a character",
                               "You cannot create more than one player per colony. (`/delete` your current one first.)",
                               accent=style.DANGER)
        if replace or dev:
            self.rt.book.remove_user(guild.id, user.id)             # a new character: out of any old lobby
        t = TECHNIQUES[tech]
        in_pool = tech in technique_pool(pclass)
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
            f"* {style.stat('Technique Rarity', rarity_of(pclass, tech) if in_pool else 'developer pick')}",
            f"* {style.stat('Class Rarity', class_rarity_of(pclass) or 'developer pick')}",
        ])
        extra = "\n".join(notes + out + [f"*{t.desc}*" if t.desc else "", "Use `/profile` to see your character "
                                         "and `/learn colony` to start playing."])
        return style.panel(self.bot, "Welcome to the Culling Games", body, extra)

    @commands.hybrid_command(name="create", description="Create your player in the culling games! (one per colony)")
    @commands.guild_only()
    @app_commands.describe(name="your character's name (2-24 characters); you can also change it before you spin")
    async def create_cmd(self, ctx: commands.Context, *, name: Optional[str] = None) -> None:
        existing = self.rt.store.get_player(str(ctx.guild.id), str(ctx.author.id))
        if existing is not None and existing.alive:
            await ctx.send(view=style.panel(self.bot, "Create a character",
                                            f"You already have **{existing.name}** in this colony. One character "
                                            f"per colony.", accent=style.DANGER), ephemeral=True)
            return
        chosen, why = clean_name(name if name else ctx.author.display_name)
        if chosen is None and name:
            await ctx.send(why, ephemeral=True)
            return
        chosen = chosen or f"Player {str(ctx.author.id)[-4:]}"
        await ctx.send(view=CreateView(self, ctx.author, ctx.guild, chosen))

    # ---- developer option --------------------------------------------------------------------------
    @commands.hybrid_command(name="devcreate", description="(Developers) Create your character with any technique")
    @commands.guild_only()
    @app_commands.describe(technique="any innate technique in the engine", pclass="class (default: one that rolls it)",
                           name="character name", level="starting level (skill points come with it)",
                           six_eyes="born with the Six Eyes", strong_vessel="can cage all twenty fingers")
    @app_commands.choices(pclass=[app_commands.Choice(name=n, value=int(pc)) for pc, n in SHORT_CLASS.items()])
    async def devcreate(self, ctx: commands.Context, technique: str, pclass: Optional[int] = None,
                        name: Optional[str] = None, level: Optional[int] = 1, six_eyes: Optional[bool] = None,
                        strong_vessel: Optional[bool] = None) -> None:
        """Only for the ids in runtime.DEV_IDS. Replaces the developer's character in this colony."""
        if not is_dev(ctx.author.id):
            await ctx.send("This command is for the bot's developers.", ephemeral=True)
            return
        key = technique.strip().lower().replace(" ", "_")
        if key not in TECHNIQUES or not TECHNIQUES[key].innate:
            key = next((k for k, t in TECHNIQUES.items() if t.innate and t.name.lower() == technique.strip().lower()),
                       None)
        if key is None:
            await ctx.send("No such innate technique. Start typing and pick one from the list.", ephemeral=True)
            return
        if str(ctx.author.id) in self.rt.fighting(ctx.guild.id):
            await ctx.send("Not while your character is in a fight.", ephemeral=True)
            return
        await ctx.defer(ephemeral=True)
        view = await self.create(ctx.guild, ctx.channel, ctx.author, name, technique=key,
                                 pclass=PClass(pclass) if pclass is not None else None, level=level or 1,
                                 six_eyes=six_eyes, vessel=20 if strong_vessel else None, replace=True)
        await ctx.send(view=view, ephemeral=True)

    @devcreate.autocomplete("technique")
    async def _dev_techniques(self, itx: discord.Interaction, current: str):
        if not is_dev(itx.user.id):
            return []
        low = current.lower()
        hits = [(k, t) for k, t in TECHNIQUES.items() if t.innate and (low in k or low in t.name.lower())]
        hits.sort(key=lambda kt: (-int(kt[1].grade), kt[1].name))
        return [app_commands.Choice(name=f"{t.name} [{GRADE_NAME[t.grade]}]"[:100], value=k) for k, t in hits[:25]]

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
        uid = ctx.author.id
        ok, rec = await self.rt.run(ctx.guild, ctx.channel,
                                    lambda game: "busy" if str(uid) in game.in_battle else game.remove_player(uid))
        if ok and rec == "busy":
            await ctx.send("Not while your character is in a fight.", ephemeral=True)
        elif not ok:
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
        allowed = (is_dev(ctx.author.id) or await self.bot.is_owner(ctx.author)
                   or str(ctx.author.id) in colony.managers or ctx.author.guild_permissions.administrator)
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
