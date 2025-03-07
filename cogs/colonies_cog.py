import os, dotenv
from dotenv import load_dotenv, find_dotenv
import discord, asyncio, json
from discord.ext import commands
#from old_techniques import get_cursed_technique
#import game, time, asyncio
# GLOBAL VARIABLES

dotenv = find_dotenv()
load_dotenv(dotenv)

log_channel = os.getenv("LOGCHANNEL")




class Colonies(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        @commands.Cog.listener()
        async def on_ready(self):
            print('Colonies cog is ready!')

        @commands.command(name="colony", description="Colony Command")
        async def colony(self, ctx):
            channel = await bot.fetch_channel(int(log_channel))
async def setup(bot):
    await bot.add_cog(Colonies(bot))


#client = Client()


# async def ai_respawn(ai, colony):
#     time_end = ai.timer
#     while time_end > 0:
#         if ai.name in colony['ai']:
#             colony['ai'].remove(ai.name)
#         print(f"Removing {ai.name} from {colony['name']}")
#         dynamo.save_colony(Colony(**colony))
#         await asyncio.sleep(time_end)
#         colony = dynamo.read_colony(colony['id'])
#         colony['ai'].append(ai.name)
#         print(f"Respawning {ai.name} in {colony['name']}")
#         colony = Colony(**colony)
#         dynamo.save_colony(colony)
#         await asyncio.sleep(time_end)
#         time_end = 0
        
#     if ai.name not in colony['ai']:
#         colony['ai'].append[ai.to_dict()]
        

# class Colonies(commands.Cog):
#     def __init__(self, bot):
#                 self.bot = bot

#     @commands.Cog.listener()
#     async def on_guild_join(self, guild):
#         ai_pool = []
#         for enemy in game.Enemy.__subclasses__():
#             ai_pool.append(enemy.name)
#         colony = Colony(id=guild.id, name=guild.name, owner=guild.owner.id, members=[], ai=[ai_pool], xp=0, colony_color='gray')
#         dynamo.update_colony(colony.id, "colony_color", colony.colony_color)
#         colony_data = dynamo.read_colony(colony.id)
#         colony_name = colony_data['name']
#         colony_owner = colony_data['owner']
#         colony_id = colony_data['id']
#         colony_color = colony_data['colony_color']
#         print(f"Colony added: {colony_name}\nColony id: {colony_id}\nColony owner: {colony_owner}")





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
    #                         return
            
    #         else:
    #                 await ctx.send(f"Player not found")

                
                
            


#____________VIEWS__________
        
# class UIEdit(discord.ui.View):
#     def __init__(self, bot, ctx, col):
#         super().__init__(timeout=None)
#         self.ctx = ctx
#         self.col = col
#         self.bot = bot
#         self.add_item(UISelect(self.bot, self.ctx, self.col))
        
        
        
    
# class UISelect(discord.ui.Select):
    
#     def __init__(self, bot, ctx, col):
#         super().__init__(
#             placeholder="Select a color",
#             options=[
#                 discord.SelectOption(label="Pink", value="pink"),
#                 discord.SelectOption(label="Blue", value="blue"),
#                 discord.SelectOption(label="Gray", value="gray"),
#                 discord.SelectOption(label="Black", value="black"),
#                 discord.SelectOption(label="Green", value="green")
#             ]
#         )
#         self.ctx = ctx
#         self.col = col
#         self.bot = bot
      

    # async def callback(self, interaction: discord.Interaction):
    #         if self.ctx.author.id != interaction.user.id:
    #             await interaction.response.send_message("You dont have permissions to choose an option", ephemeral=True)
    #             return
    #         colony_data = dynamo.read_colony(self.col.id)
    #         if colony_data:
    #             value = self.values[0]
    #             if value == "blue":
    #                 colony_data['colony_color'] = value
    #                 await interaction.response.edit_message(content="Blue", view=None)
    #             elif value == "pink":
    #                 colony_data['colony_color'] = value
    #                 await interaction.response.edit_message(content="Pink", view=None)
    #             elif value == "gray":
    #                 colony_data['colony_color'] = value
    #                 await interaction.response.edit_message(content="Gray", view=None)
    #             elif value == "black":
    #                 colony_data['colony_color'] = value
    #                 await interaction.response.edit_message(content="Black", view=None)
    #             elif value == "green":
    #                 colony_data['colony_color'] = value
    #                 await interaction.response.edit_message(content="Green", view=None)
    #             colony = Colony(**colony_data)
    #             dynamo.save_colony(colony)
    #             await interaction.response.edit_message(content="Color changed", view=None)
            

# async def setup(bot: commands.Bot):
#             await bot.add_cog(Colonies(bot))

# class Colony:
#     def __init__(self, id, name, owner, members: list, ai: list, xp, colony_color):
#         self.id = id
#         self.name = name
#         self.owner = owner
#         self.members = members
#         self.ai = ai
#         self.xp = xp
#         self.colony_color = colony_color