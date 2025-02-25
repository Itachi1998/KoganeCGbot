import discord, os # Import general dependencies 
from discord.ext import commands
import techniques
from techniques import enemy_techniques, BVs, cursed_tools, rules, get_cursed_technique
from technique_list import * # Import all techniques

token = os.environ['TOKEN']
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix=',', intents=intents)

async def setup_hook():
    for filename in os.listdir('cogs'):
        if filename.endswith('.py'):
            cog = filename[:-3]
            try:
                await bot.load_extension(f'cogs.{cog}')
                print(f'Cog loaded: {cog}')
            except Exception as e:
                print(f'Failed to load cog {cog}: {e}')


