"""Launch the bot: ``python -m ai.bot`` (token in the DISCORD_TOKEN or TOKEN environment variable).

Same setup as the original main.py - prefix ``,``, the same intents, ``,sync`` for the owner - but
the cogs load at start-up (setup_hook), so slash commands work before anyone runs ``,sync``.
"""
from __future__ import annotations

import os
import pkgutil

import discord
from discord.ext import commands

from . import cogs
from .runtime import Runtime


class CullingBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        super().__init__(command_prefix=",", intents=intents)
        self.runtime = Runtime(self)

    async def setup_hook(self) -> None:
        for mod in pkgutil.iter_modules(cogs.__path__):
            await self.load_extension(f"{cogs.__name__}.{mod.name}")
            print(f"Cog loaded: {mod.name}")
        print(f"Storage: {self.runtime.store.backend}, battle cache: {self.runtime.cache.backend}")

    async def on_ready(self) -> None:
        print(f"Bot is ready as {self.user}")


bot = CullingBot()


@bot.command()
async def sync(ctx: commands.Context) -> None:
    """Owner only: push the slash commands to Discord (here at once, everywhere within the hour)."""
    if not await bot.is_owner(ctx.author):
        await ctx.send("You are not the owner of this bot")
        print(f"User {ctx.author.id} ({ctx.author}) tried to sync commands but is not the owner")
        return
    if ctx.guild is not None:
        bot.tree.copy_global_to(guild=ctx.guild)
        here = await bot.tree.sync(guild=ctx.guild)
    else:
        here = []
    synced = await bot.tree.sync()
    await ctx.send(f"Commands synced: {len(synced)} global" + (f", {len(here)} in this server" if here else ""))


def main() -> None:
    token = os.environ.get("DISCORD_TOKEN") or os.environ.get("TOKEN")
    if not token:
        raise SystemExit("Set DISCORD_TOKEN (or TOKEN) to the bot's token.")
    bot.run(token)


if __name__ == "__main__":
    main()
