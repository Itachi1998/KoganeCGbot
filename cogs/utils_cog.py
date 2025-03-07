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

    # Tutorial command group
    @app_commands.group(name='learn', description='Get help with the bot', invoke_without_command=True)
    async def tutorial(self, interaction: discord.Interaction):
        await interaction.response.send_message('Help command group', ephemeral=True)
        # list out subcommands using a forloop inside an embed
        return
    
    @tutorial.command(name='create', description='Learn how to create a character')
    async def create(self, interaction: discord.Interaction):
        await interaction.response.send_message('Create a character', ephemeral=True)
        # We will be creating characters with a /create command that will have buttons to spin for the class, technique, and CE amount
        # Create an embed using the bot's avatar as a thumbnail and a title of "Learn: Create a character"
        # Add a field that explains how to spin for a class
        # Add a field that explains how to spin for a technique
        # Add a field that explains how to spin for a CE amount
        return
        

    @tutorial.command(name='battle', description='Learn how to battle')
    async def battle(self, interaction: discord.Interaction):
        await interaction.response.send_message('Learn: Battle commandS!', ephemeral=True)
        # We will be using /lobby create to create lobby's to battle in, once in a lobby they can use /lobby pve to enable, or /lobby pvp to enable pvp mode, or they can use the lobby buttons
        
        # Create an embed using the bot's avatar as a thumbnail and a title of "Learn: Battle commands"
        # Add a field Explain that players will be able to create invite only lobby's.
        # Add a field that explains how to create a lobby
        # Add a field that explains how to enable pve mode
        # Add a field that explains how to enable pvp mode
        # Add a field that tells them to do /learn pve and /learn pvp to learn more about pve and pvp lobby's
        return

    

    



# class Help_buttons(discord.ui.View):
#     def __init__(self):
#         super().__init__(timeout=200)
#         self.add_item(tutorial_button())

#     @discord.ui.button(label='Tutorial', style=discord.ButtonStyle.primary)
#     async def tutorial_button(self, button: discord.ui.Button, interaction: discord.Interaction):
#         button.disabled=True
#         await Utils_cog.help(interaction)
#         description = """
# Use /create to create a character, choose a class, and spin 
# """ 
#         embed=discord.Embed(title='Tutorial', description='Learn how to play!', color=discord.Color.green())
#         await interaction.response.send_message(embed=embed, view=self)
        
    
async def setup(bot):
    await bot.add_cog(Utils_cog(bot))

            
           
        

            