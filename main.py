import discord, os, dotenv# Import general dependencies 
from dotenv import load_dotenv, find_dotenv
from discord.ext import commands
import old_techniques
from old_techniques import enemy_techniques, BVs, cursed_tools, rules, get_cursed_technique
from technique_list import * # Import all techniques
dotenv = find_dotenv()
load_dotenv(dotenv)

log_channel = os.getenv('LOGCHANNEL')
token = os.getenv('TOKEN')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix=',', intents=intents)

async def load():
    for filename in os.listdir('cogs'):
        if filename.endswith('.py'):
            cog = filename[:-3]
            try:
                await bot.load_extension(f'cogs.{cog}')
                print(f'Cog loaded: {cog}')
            except Exception as e:
                print(f'Failed to load cog {cog}: {e}')


@bot.command()
async def sync(ctx):
    if ctx.author.id == bot.owner_id:
        await bot.tree.sync()
        await ctx.send("Commands synced! ")


@bot.event
async def on_ready():
    print(f'{bot.user.name} is ready')
    await main()

async def main():
    await load()
    await bot.wait_until_ready()
    await bot.change_presence(activity=discord.Game(name='Culling Games Commence! | /help'))
    print('Bot is ready')
    channel = bot.get_channel(int(log_channel))
    await channel.send('Bot is ready')

bot.run(token)


