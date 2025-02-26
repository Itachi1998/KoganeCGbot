import discord, os, dotenv# Import general dependencies 
from dotenv import load_dotenv, find_dotenv
from discord.ext import commands

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



@bot.event
async def on_ready():
    print(f'{bot.user.name} is ready')
    await main()

async def main():
    await load()
    await bot.wait_until_ready()
    print('Bot is ready')
    channel = bot.get_channel(int(log_channel))
    await channel.send('Bot is ready')

@bot.command()
async def sync(ctx):
      channel = bot.get_channel(int(log_channel))
      if ctx.author.id == bot.owner_id:
            await bot.change_presence(activity=discord.Game(name="the Kogane's Culling Games"))
            await bot.tree.sync()
            await ctx.send("Commands synced")
    
      else:
        await ctx.send("You are not the bot owner")
        fstring = f"User ({ctx.author.id}) tried to sync commands but is not the bot owner in {ctx.guild.name} id {ctx.guild.id}"
        await channel.send(fstring)
        print(fstring)


@bot.tree.command(name='help', description='Learn how to play!')
async def help(interaction: discord.Interaction):
    embed = discord.Embed(title='Help', description="""/create a character, choose a class, and spin for your techniques, cursed energy reserves, and special traits!""", color=0x00ff00)
    embed.add_field(name='##/command <command>', 
                    value="""To learn about a specific command.
                    Or see the subcommands for any command""", inline=False)
    embed.add_field(name='##/help', value="""See this message again""", inline=False)
    embed.add_field(name='##/pve', value="""Start a PvE lobby to fight against AI Culling Game players!""", inline=False)
    embed.add_field(name='##/pvp', value="""Start a PvP lobby to fight against other Discord Culling Game players!""", inline=False)
    embed.add_field(name='##/rules', value="""See the colony rules. 
                    Use /commands rules to see more rule commands""", inline=False)
    
    embed.add_field(name='##/leaderboard', value="""See the leaderboard.
                    Use /commands leaderboard to see more leaderboard commands""", inline=False)

    embed.add_field(name='##/techniques', value="""See all the different techniques and classes available in the colony!""", inline=False)

    embed.add_field(name='##/market,', value="""See the market. 
                    Use /commands market to see more market commands""", inline=False)

    embed.add_field(name='##/colony', value="""See your colony information. 
                    Use /commands colony to see more colony commands""", inline=False)


    embed.add_field(name='##/character', value="""See your character information. 
                    Use /commands character to see more character commands""", inline=False)

    await interaction.response.send_message(embed=embed)

bot.run(token)


