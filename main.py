import discord, os, traceback, db, enemy_techs
from db import read_player, read_enemy, read_colony # Import general dependencies 
from game import Player, Enemy
from discord.ext import commands


# log_channel = os.getenv('LOGCHANNEL')
# token = os.getenv('TOKEN')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix=',', intents=intents)


def random_pve_enemy(colony_id, lobby):
    colony = read_colony(colony_id)
    

async def load():
#     await bot.load_extension('cogs.battle')
    for filename in os.listdir('cogs'):
        if filename.endswith('.py'):
            
            cog = filename[:-3]
            if cog == 'battle':
                continue
            await bot.load_extension(f'cogs.{cog}')
            print(f'Cog loaded: {cog}')
        
                
@bot.event
async def on_ready():
 print('Bot is ready')


async def main():
    await load()
    await bot.wait_until_ready()
    # print('Bot is ready')
    # # channel = bot.get_channel(int(log_channel))
    # await channel.send('Bot is ready')
    synced = await bot.tree.sync()
    print(f'Commands synced {synced}')
    commands = bot.all_commands
    for command in commands:
        print(command)
    print('Commands printed')
    

@bot.command()
async def sync(ctx):
#       channel = bot.get_channel(int(log_channel))
      if await bot.is_owner(ctx.author):
        await main()
        await ctx.send("Commands synced")
      else:
        await ctx.send("You are not the owner of this bot")
        fstring = f'User {ctx.author.id} ({ctx.author}) tried to sync commands but is not the owner in {ctx.guild.id} ({ctx.guild.name}) - {ctx.channel.id} ({ctx.channel.name}) '
        # await channel.send(fstring)
        print(fstring)
 


class Layout(discord.ui.LayoutView):
    actionrow = discord.ui.ActionRow()
    @actionrow.button(label='Click Me!')
    async def action_row_button(self, itx: discord.Interaction, btn: discord.ui.Button):
        await itx.response.send_message("Hi!", ephemeral=True)

    container = discord.ui.Container(
        discord.ui.TextDisplay(
            content="Click button for a very special message!"
        ),
        accent_color=discord.Colour.blurple()
    )

@bot.command()
async def layout(ctx: commands.Context):
    await ctx.send(view=Layout())

 
bot.run()
