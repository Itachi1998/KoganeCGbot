import discord
from discord.ext import commands
from discord import app_commands

import os


bot = commands.Bot(command_prefix=',', intents=discord.Intents.all())
log_channel = int(os.getenv('LOGCHANNEL'))
channel = bot.get_channel(log_channel)


class Utils_cog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Utils cog is ready!')



    @bot.group(name='command_help', description='Learn about a specific command', with_app_command=True, fallback='get')
    async def command_help(self, ctx):
            if ctx.invoked_subcommand is None:
                commands = bot.tree.get_commands()
                embed = discord.Embed(title='Commands', description='List of all commands', color=0x00ff00)
                for c in commands:
                    name = c.name
                    description = c.description
                    embed.add_field(name=name, value=description, inline=False)
                await ctx.send(embed=embed)

    @command_help.command(name='create', description='Learn about the create command')
    async def create(self, ctx):
            command = bot.tree.get_command('create')
            if command is None:
                await ctx.send('Command not found')
            else:
                embed = discord.Embed(title='Create Command', description='Will display the character creation screen', color=0x00ff00)
                await ctx.send(embed=embed)
        
    @command_help.command(name='pve', description='Learn about the pve command')
    async def pve(self, ctx):
            command = bot.tree.get_command('pve')
            if command is None:
                await ctx.send('Command not found')
            else:
                embed = discord.Embed(title='PVE Command', description="""Will display the PVE lobby along with its buttons: 
                                    - Start `will start the game if all players are ready!`
                                    - Lock `will lock the lobby!`
                                    - Invite `will prompt the invite screen`
                                    - Disband `will disband the lobby if you are the lobby owner`
                                    - Leave `will leave the lobby if you are not the owner. If the owner leaves as the last person the lobby will disband. If the owner leaves with others still in the lobby it will remain open, and a new owner will be chosen.`""", color=0x00ff00)
                await ctx.send(embed=embed)



async def setup(bot):
    await bot.add_cog(Utils_cog(bot))

            
           
        

            