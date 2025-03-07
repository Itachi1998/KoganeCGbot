import discord, os
from discord.ext import commands
from discord import app_commands
bot = commands.Bot(command_prefix=',', intents=discord.Intents.all())
log_channel = int(os.getenv('LOGCHANNEL'))
channel = bot.get_channel(log_channel)

class Character_cog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        @commands.Cog.listener()
        async def on_ready(self):
            print('Character cog is ready!')



async def setup(bot):
    await bot.add_cog(Character_cog(bot))