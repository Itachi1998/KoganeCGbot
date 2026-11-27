"""Launch the bot: ``python -m ai.bot``. The token comes from DISCORD_TOKEN, or from AWS (``fetch_token``).

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
        # Nothing the bot posts can ping @everyone or a role, whatever a player names their character.
        super().__init__(command_prefix=",", intents=intents,
                         allowed_mentions=discord.AllowedMentions(everyone=False, roles=False, users=True))
        self.runtime = None                      # opened at start-up, not on import (it opens the database)

    async def setup_hook(self) -> None:
        self.runtime = Runtime(self)
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


def fetch_token() -> str:
    """The bot token: DISCORD_TOKEN (or TOKEN) if set, else fetched from AWS with your local AWS login
    (``aws configure`` / ``aws sso login``; AWS_PROFILE and AWS_REGION are honoured):

      DISCORD_TOKEN_SSM=/kogane/discord-token     an SSM Parameter Store SecureString (free tier)
      DISCORD_TOKEN_SECRET=kogane/discord         a Secrets Manager secret: the token itself, or JSON
                                                  with a "DISCORD_TOKEN" (or DISCORD_TOKEN_SECRET_KEY) key
    The token is never printed or logged.
    """
    token = os.environ.get("DISCORD_TOKEN") or os.environ.get("TOKEN")
    if token:
        return token
    ssm_name, secret_id = os.environ.get("DISCORD_TOKEN_SSM"), os.environ.get("DISCORD_TOKEN_SECRET")
    if not (ssm_name or secret_id):
        raise SystemExit("No token: set DISCORD_TOKEN, or DISCORD_TOKEN_SSM / DISCORD_TOKEN_SECRET to fetch it "
                         "from AWS (see deploy/LOCAL.md).")
    try:
        import boto3
        if ssm_name:
            resp = boto3.client("ssm").get_parameter(Name=ssm_name, WithDecryption=True)
            print(f"Token: from SSM parameter {ssm_name}")
            return resp["Parameter"]["Value"].strip()
        raw = boto3.client("secretsmanager").get_secret_value(SecretId=secret_id)["SecretString"].strip()
        print(f"Token: from Secrets Manager secret {secret_id}")
        if raw.startswith("{"):
            import json
            data = json.loads(raw)
            key = os.environ.get("DISCORD_TOKEN_SECRET_KEY", "DISCORD_TOKEN")
            if key not in data:
                raise SystemExit(f"The secret is JSON but has no {key!r} key.")
            return str(data[key]).strip()
        return raw
    except SystemExit:
        raise
    except Exception as e:                       # say what failed, never what the token is
        raise SystemExit(f"Could not fetch the token from AWS: {type(e).__name__}: {e}")


def main() -> None:
    bot.run(fetch_token())


if __name__ == "__main__":
    main()
