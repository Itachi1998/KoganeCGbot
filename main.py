import discord, os# Import general dependencies 
from os import environ
from discord.ext import commands
import old_techniques
from old_techniques import enemy_techniques, BVs, cursed_tools, rules, get_cursed_technique
from technique_list import * # Import all techniques

log_channel = os.getenv('LOGCHANNEL')
token = os.getenv('TOKEN')
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


@bot.event
async def on_ready():
    print(f'{bot.user.name} is ready')
    
    for cog in bot.cogs:
        print(f"Cog loaded: {cog}")
    print(f"Loaded cogs: {len(bot.cogs)}")



bot.setup_hook = setup_hook
bot.run(token)


