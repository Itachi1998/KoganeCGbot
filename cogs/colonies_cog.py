import os, dotenv, datetime
from datetime import datetime
from db import create_colony,read_colony, update_colony, check_relationship
from dotenv import load_dotenv, find_dotenv
import discord, asyncio, json
from discord.ext import commands
import game
#from old_techniques import get_cursed_technique
#import game, time, asyncio
# GLOBAL VARIABLES

dotenv = find_dotenv()
load_dotenv(dotenv)

log_channel = os.getenv("LOGCHANNEL")

# Update after postgres database is set up

class Colonies(commands.Cog):
    def __init__(self, bot):
                self.bot = bot

    @commands.Cog.listener()
    async def on_join(self, guild):
        colony_data = {
            'name': guild.name,
            'colony id': guild.id,
            'create date': datetime.now().astimezone().strftime("%c"),
            'colony color': 'gray',
            'players': [],
            'enemies': [],
            'items': [],
            'ce': 0,
            'xp': 0,
            'leaderboard': [],
            'color': "black",
            'six eyes': False,
         }
        
        colony = create_colony(colony_data)
        channel = self.bot.get_channel(int(log_channel))
        if channel:
            await channel.send(f"Bot joined new server. New colony created: {guild.name}")
        print("Colony added: " + guild.name)
        print(colony)
        return     

    @commands.command(name="colony", description="Sync colonies")
    async def colony(self, ctx):

        if ctx.author.id != self.bot.owner_id:
            await ctx.send("You are not the owner of this bot.")
            return

        for guild in self.bot.guilds:
            enemies = [enemy_class() for enemy_class in game.Enemy.__subclasses__()]
            colony_data = {
                'name': guild.name,
                'colony id': guild.id,
                'creation date': datetime.now().astimezone().strftime("%c"),
                'colony color': 'gray',
                'players': [],
                'enemies': [],
                'items': [],
                'ce': 0,
                'xp': 0,
                'leaderboard': [],
                'color': "black",
                'six eyes': False,
            }

            existing_col = read_colony(guild.id)

            if existing_col:
                await ctx.send("Colony already exists: " + guild.name)
                continue

            colony = create_colony(colony_data, enemies)
            check_relationship()
            
            await ctx.send("Colony added: " + guild.name)
            print("Colony added: " + guild.name)
            print(colony)
       

async def setup(bot):
    await bot.add_cog(Colonies(bot))




#     @commands.command(name="colony", description="Update colony")
#     async def colony(self, ctx):
#         await ctx.defer()
#         ai_pool = []
#         for enemy_class in game.Enemy.__subclasses__():
#                         enemy = enemy_class()
#                         ai_pool.append(enemy.name)
#         if ctx.author.id != 677718946270543882:
#                         await ctx.send("You are not allowed to use this command.")
#                         return
#         else:
#                     for guild in self.bot.guilds:
#                         colony_data = dynamo.read_colony(guild.id)
                            
                            
#                         if colony_data is None:
#                                 colony = Colony(id=guild.id, name=guild.name, owner=guild.owner.id, members=[], ai=[ai_pool], xp=0, colony_color='gray')
#                                 dynamo.save_colony(colony)
#                                 colony_data = dynamo.read_colony(colony.id)
#                                 await ctx.send(f"Saved colony {colony.name}")
                                
        
#                         if colony_data:
#                                 colony = Colony(**colony_data)
#                                 colony_data['ai'] = ai_pool
#                                 dynamo.save_colony(colony)
#                                 colony_data = dynamo.read_colony(colony.id)
#                                 await ctx.send(f"Saved colony {colony.name}")
                                
                                
                                          

    # @commands.hybrid_command(name='ui', description='Edit UI of your Colony')
    # async def ui(self, ctx):
    #     await ctx.defer()
    #     colony_data = dynamo.read_colony(ctx.guild.id)
    #     if colony_data:
    #         if ctx.author.id == ctx.guild.owner.id or ctx.author.id == 677718946270543882:
    #             embed = discord.Embed(title="Colony UI", description="Select an option to edit")
    #             embed.add_field(name="1) Colony Name", value="Change the name of your colony", inline=False)
    #             embed.add_field(name="2) UI Color", value="Change the color of your colonies UI", inline=False)
    #             colony = ctx.guild 
    #             await ctx.send(embed=embed, view=UIEdit(self.bot, ctx, colony))
    #         else:
    #             ctx.send("You are not the GameMaster of this colony")
    #     else:
    #         dynamo.save_colony(Colony(id=ctx.guild.id, name=ctx.guild.name, owner=ctx.guild.owner.id, members=[], ai=[], xp=0, colony_color='gray'))
    #         embed = discord.Embed(title="Colony UI", description="New colony created!\nSelect an option to edit")
    #         embed.add_field(name="1) Colony Name", value="Change the name of your colony")
    #         embed.add_field(name="2) UI Color", value="Change the color of your colonies UI")
    #         colony = ctx.guild
    #         await ctx.send(embed=embed, view=UIEdit(self.bot, ctx, colony))
        

    # @commands.hybrid_command(name='remove', description='Remove a character from colony')
    # async def remove(self, ctx, member: discord.Member=None):
    #         player = None
    #         if member:
    #              if ctx.author.id == ctx.guild.owner.id or ctx.author.id==677718946270543882:
    #                 player = dynamo.read_player(member.id, ctx.guild.id)
    #              else:
    #                 await ctx.send(f"Access denied. You dont have permission.")
    #                 return
    #         else:
    #             member = await self.bot.fetch_user(ctx.author.id)
    #             player = dynamo.read_player(member.id, ctx.guild.id)
    #         if player:
    #                         dynamo.delete_from_colony(ctx.guild.id, "members", ctx.author.id)
    #                         await ctx.send(f"{ctx.author.mention} has been removed from the colony.")
#     #                         return
            
#     #         else:
#     #                 await ctx.send(f"Player not found")

                
                
            


# #____________VIEWS__________
        
# # class UIEdit(discord.ui.View):
# #     def __init__(self, bot, ctx, col):
# #         super().__init__(timeout=None)
# #         self.ctx = ctx
# #         self.col = col
# #         self.bot = bot
# #         self.add_item(UISelect(self.bot, self.ctx, self.col))
        
        
        
    
# # class UISelect(discord.ui.Select):
    
# #     def __init__(self, bot, ctx, col):
# #         super().__init__(
# #             placeholder="Select a color",
# #             options=[
# #                 discord.SelectOption(label="Pink", value="pink"),
# #                 discord.SelectOption(label="Blue", value="blue"),
# #                 discord.SelectOption(label="Gray", value="gray"),
# #                 discord.SelectOption(label="Black", value="black"),
# #                 discord.SelectOption(label="Green", value="green")
# #             ]
# #         )
# #         self.ctx = ctx
# #         self.col = col
# #         self.bot = bot
      

#     # async def callback(self, interaction: discord.Interaction):
#     #         if self.ctx.author.id != interaction.user.id:
#     #             await interaction.response.send_message("You dont have permissions to choose an option", ephemeral=True)
#     #             return
#     #         colony_data = dynamo.read_colony(self.col.id)
#     #         if colony_data:
#     #             value = self.values[0]
#     #             if value == "blue":
#     #                 colony_data['colony_color'] = value
#     #                 await interaction.response.edit_message(content="Blue", view=None)
#     #             elif value == "pink":
#     #                 colony_data['colony_color'] = value
#     #                 await interaction.response.edit_message(content="Pink", view=None)
#     #             elif value == "gray":
#     #                 colony_data['colony_color'] = value
#     #                 await interaction.response.edit_message(content="Gray", view=None)
#     #             elif value == "black":
#     #                 colony_data['colony_color'] = value
#     #                 await interaction.response.edit_message(content="Black", view=None)
#     #             elif value == "green":
#     #                 colony_data['colony_color'] = value
#     #                 await interaction.response.edit_message(content="Green", view=None)
#     #             colony = Colony(**colony_data)
#     #             dynamo.save_colony(colony)
#     #             await interaction.response.edit_message(content="Color changed", view=None)
            

# # async def setup(bot: commands.Bot):
# #             await bot.add_cog(Colonies(bot))


# class Colony:
#     def __init__(self, colony_name: str, colony_id: int, owner_id: int, creation_date: str, color: str, 
#                  players: list, enemies: list, items: list, ce: int, xp: int, shop: list, rules: list, graveyard: list, leaderboard: list, events: list):
#         # 'colony_name': guild.name,
#         #     'colony_id': guild.id,
#         #     'owner_id': guild.owner_id,
#         #     'creation_date': datetime.now().astimezone().strftime("%c"),
#         #     'colony_color': 'gray',
#         #     'districts': [],
#         #     'players': [],
#         #     'enemies': enemies,
#         #     'items': [],
#         #     'ce': 0,
#         #     'xp': 0,
#         #     'shop': [],
#         #     'rules': [],
#         #     'graveyard': [],
#         # #     'leaderboard': []
#         # self.colony_name = colony_name
#         # self.colony_id = colony_id
#         # self.owner_id = owner_id
#         # self.creation_date = creation_date
#         # self.color = color
#         # self.players = players
#         # self.enemies=enemies
#         # self.items=items
#         # self.ce=ce
#         # self.xp=xp
#         # self.shop=shop
        # self.rules