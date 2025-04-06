import discord, os, dotenv, traceback # Import general dependencies 
from dotenv import load_dotenv, find_dotenv
from discord.ext import commands

dotenv = find_dotenv()
load_dotenv(dotenv)
log_channel = os.getenv('LOGCHANNEL')
token = os.getenv('TOKEN')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix=',', intents=intents)



async def load():
    for filename in os.listdir('cogs'):
        if filename.endswith('.py'):
            cog = filename[:-3]
            await bot.load_extension(f'cogs.{cog}')
            print(f'Cog loaded: {cog}')
        
                
@bot.event
async def on_ready():
 print('Bot is ready')


async def main():
    await load()
    await bot.wait_until_ready()
    print('Bot is ready')
    channel = bot.get_channel(int(log_channel))
    await channel.send('Bot is ready')
    synced = await bot.tree.sync()
    print(f'Commands synced {synced}')
    commands = bot.all_commands
    for command in commands:
        print(command)
    print('Commands printed')
    
@bot.command()
async def sync(ctx):
      channel = bot.get_channel(int(log_channel))
      if await bot.is_owner(ctx.author):
        await main()
        await ctx.send("Commands synced")
      else:
        await ctx.send("You are not the owner of this bot")
        fstring = f'User {ctx.author.id} ({ctx.author}) tried to sync commands but is not the owner in {ctx.guild.id} ({ctx.guild.name}) - {ctx.channel.id} ({ctx.channel.name}) '
        await channel.send(fstring)
        print(fstring)

bot.run(token)


