import discord
from discord.ext import commands
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
        group_embed = discord.Embed(title="Tutorial", description="Choose one of the following commands to learn about!\nYou can use either `/learn <command_name>` or the prefix `,learn <command_name>`")
        for subc in learn.commands:
           name=subc.name
           description=sync.description
        await ctx.send('Tutorial command group', embed=group_embed)


    # CHANGED TO 'CHARACTER' INSTEAD OF 'CREATE' JUST SEEMED MORE FITTING LMK
    @learn.command(name='character', description='Learn how to create a character') 
    async def character(self, ctx):
        create_embed = discord.Embed(title='Learn: Create a character', description='You will learn how to create a character')
        create_embed.add_field(name='Create', value='Use the /create command to bring up the create menu... ', inline=False)
        create_embed.add_field(name='Spinning for a class', value='...', inline=False)
        create_embed.add_field(name='Spinning for a technique', value='...', inline=False)
        create_embed.add_field(name='Spinning for a CE amount', value='...', inline=False)
        create_embed.add_field(name='Deleting you\'re character', value='...', inline=False)
        create_embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar)
        await ctx.send(embed=create_embed, ephemeral=True)
        return
        

    # SHOULD THE LOBBY/BATTLE HELP COMMANDS BE TOGETHER OR SEPARATE ?
    @learn.command(name='lobby', description='Learn how to use the lobby functions') 
    async def lobby(self, ctx):
        lobby_embed = discord.Embed(title='Learn: Lobby functions', description='...')
        lobby_embed.add_field(name='Create invite only lobby', value='...', inline=False)
        lobby_embed.add_field(name='Create an open lobby', value='...', inline=False)
        lobby_embed.add_field(name='Invite players', value='...', inline=False)
        lobby_embed.add_field(name='Kick players', value='...', inline=False)
        lobby_embed.add_field(name='Leave lobby', value='...', inline=False)
        lobby_embed.add_field(name='Lock lobby', value='...', inline=False)
        lobby_embed.add_field(name='Ready up', value='...', inline=False)
        lobby_embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar)
        await ctx.send(embed=lobby_embed, ephemeral=True)
        return


    @learn.command(name='battle', description='Learn how to battle')
    async def battle(self, ctx):
        battle_embed = discord.Embed(title='Learn: Battle commands', description='You will learn how to use battle commands...')
        battle_embed.add_field(name='Enable PVE', value='To enable PVE...', inline=False)
        battle_embed.add_field(name='Enable PVP', value='To enable PVP...', inline=False)
        battle_embed.add_field(name='More about PVE & PVP', value='To learn more about PVE lobbies, enter "/learn pve". '
        'To learn more about PVP lobbies, enter "/learn pvp."', inline=False)
        battle_embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar)
        await ctx.send(embed=battle_embed, ephemeral=True)
        return
 

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