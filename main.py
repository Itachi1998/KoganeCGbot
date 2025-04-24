import discord, os, traceback, db, enemy_techs
from db import read_player, read_enemy, read_colony # Import general dependencies 
from game import Player, Enemy
from discord.ext import commands

log_channel = os.getenv('LOGCHANNEL')
token = os.getenv('TOKEN')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix=',', intents=intents)



def get_player(colony_id, user_id):
    player_data = read_player(user_id=user_id, colony_id=colony_id)
    if player_data:
        player = Player(
            name=player_data.name,
            level=player_data.level,
            max_hp=player_data.max_hp,
            max_ce=player_data.max_ce,
            strength=player_data.strength,
            speed=player_data.speed,
            technique=player_data.technique,
            playerclass=player_data.playerclass,
            colony=player_data.colony_id,
            xp=player_data.xp,
            cgp=player_data.cgp,
            skp=player_data.skp,
            user_id=player_data.user_id,
            six_eyes=player_data.six_eyes
        )
        
        return player
    else:
        return False
    
def random_pve_enemy(colony_id, lobby):
    colony = read_colony(colony_id)
    



bot.get_player = get_player

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


