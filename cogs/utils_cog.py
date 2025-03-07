import discord
from discord.ext import commands
from discord import app_commands

import os




class Utils_cog(commands.Cog):


    def __init__(self, bot):
        self.bot = bot
        self.log_channel = int(os.getenv('LOGCHANNEL'))
        self.channel = bot.get_channel(self.log_channel)

    #@bot.events
    @commands.Cog.listener()
    async def on_ready(self):
        print('Utils cog is ready!')

    # learn command group
    @commands.hybrid_group(name='learn', desciption='Learn how to play the game')
    async def learn(self, ctx):
        await ctx.send('Help command group', ephemeral=True)

    
    @learn.command(name='create', description='Learn how to create a character')
    async def create(self, ctx):
        #create_embed = discord.Embed(title=''We will be creating characters with a /create command that will have buttons to spin for the class, technique, and CE amount')
        # Create an embed using the bot's avatar as a thumbnail and a title of "Learn: Create a character"
        # Add a field that explains how to spin for a class
        # Add a field that explains how to spin for a technique
        # Add a field that explains how to spin for a CE amount
        await ctx.send('Create a character', ephemeral=True)
        return
        

    @learn.command(name='battle', description='Learn how to battle')
    async def battle(self, ctx):
        await ctx.send('Learn: Battle commandS!', ephemeral=True)
        # We will be using /lobby create to create lobby's to battle in, once in a lobby they can use /lobby pve to enable, or /lobby pvp to enable pvp mode, or they can use the lobby buttons
        
        # Create an embed using the bot's avatar as a thumbnail and a title of "Learn: Battle commands"
        # Add a field Explain that players will be able to create invite only lobby's.
        # Add a field that explains how to create a lobby
        # Add a field that explains how to enable pve mode
        # Add a field that explains how to enable pvp mode
        # Add a field that tells them to do /learn pve and /learn pvp to learn more about pve and pvp lobby's
        return

    # lobby (invite, kick, leave, ready up, lock, start), pve (), pvp

    



# class Help_buttons(discord.ui.View):
#     def __init__(self):
#         super().__init__(timeout=200)
#         self.add_item(learn_button())

#     @discord.ui.button(label='learn', style=discord.ButtonStyle.primary)
#     async def learn_button(self, button: discord.ui.Button, ctx: discord.ctx):
#         button.disabled=True
#         await Utils_cog.help(ctx)
#         description = """
# Use /create to create a character, choose a class, and spin 
# """ 
#         embed=discord.Embed(title='learn', description='Learn how to play!', color=discord.Color.green())
#         await ctx.response.send_message(embed=embed, view=self)
        
    
async def setup(bot):
    await bot.add_cog(Utils_cog(bot))

            
           
        

            