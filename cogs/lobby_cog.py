import discord, datetime
from datetime import datetime
from discord.ext import commands
import time, asyncio

# MAIN CLASS FOR LOBBIES
# Use this to instantiate lobby instances

class Lobby():
    def __init__(self, name: str, owner: int, colony_id: int, private: bool, players: list, 
                invited: list, 
                team1: list,
                team2: list, 
                ready: list, 
                Round: int,
                start_time=time.time(), 
                timer=time.time() + 500, 
                field: list=None, 
                graveyard: list=None,
                feed: list=None, 
                spectators: list=None,):
        self.name = name # name of lobby default to "<player name>'s Lobby"
        self.owner = owner # user_id of the owner of the lobby
        self.colony_id = colony_id # id of colony lobby is created in
        self.private = private # if lobby is private = True
        self.players=players # list of total players in the lobby
        self.invited=invited # list of invited players 
        self.team1=team1 # list of players who joined team1
        self.team2=team2 # list of players who joined team2
        self.ready = ready # list of players ready 
        self.round = Round # int of the current turn
        self.start = start_time # date of creation EST
        self.field = field # players and items on the field 
        self.graveyard = graveyard # players killed in this battle
        self.feed = feed # battle feed 
        self.spectators=spectators
        self.timer=timer
       
class Lobby_Cog(commands.Cog):
    def __init__(self, bot): 
         self.bot = bot
         self.lobbies = {}  # Dictionary to store active lobbies

    async def expire(self, lob):
        async def lobby_expiration_task():
            while True:
                await asyncio.sleep(1)
                # Check every second
                if lob.timer < time.time():
                    # Logic to delete the lobby
                    print(f"Lobby {lob.name} has expired and will be deleted.")
                    # Remove the lobby from the active lobbies dictionary
                    self.lobbies.pop(lob.name, None)
                    # Notify the lobby owner or players if needed
                    break
                else:
                    lob.timer += 500
                    print(f"Lobby {lob.name} timer extended by 500 seconds.")

        # Add the task to the bot's task queue
        self.bot.loop.create_task(lobby_expiration_task())

    async def interaction_check(self, ctx, data="", ephemeral=None, embed=None):
        if ctx.interaction:
            await ctx.interaction.response.send_message(data, embed=embed, ephemeral=ephemeral)
        else:
            await ctx.send(data, embed=embed)


    @commands.hybrid_group(name="lobby", description="Use /lobby <option>")
    async def lobby(self, ctx):

        if ctx.invoked_subcommand is None:

            embed = discord.Embed(title="Lobby commands", description="## Use /lobby `<command>`\n"
            "### /lobby create\n"
            "* Creates a public lobby\n### /lobby private\n* Creates a private lobby"
            "\n### /lobby lock\n* Use to lock a public lobby"
            "\n### /lobby invite\n* Allow players into lobby"
            "\n### /lobby leave\n"
            "* Any player can leave the lobby\n* If the owner leaves a new owner will be selected."
            "\n* If the last person leaves the lobby it will be disbanded\n* Lobby must not be in active battle"
            "\n### /lobby kick"
            "\n* Kick a player from lobby "
            "\n### /lobby disband\n* Disband a lobby in queue status if owner")
            await ctx.send(embed=embed, ephemeral=True)
    

    def thread_check(self, ctx):
        if isinstance(ctx.channel, discord.Thread):
                        if ctx.channel.type == discord.ChannelType.private_thread:
                            return "private"
                        elif ctx.channel.type == discord.ChannelType.public_thread:
                            return "public"
                        else:
                            return False
    
                        
    @lobby.command(name='create')
    async def create(self, ctx, name: str=None):
        tclass = self.thread_check(ctx)
        if tclass == "private" or tclass == "public":
            if not name:
                name = ctx.author.name + "'s Lobby"
            private = False if tclass == "public" else True
            lob = Lobby(
                name=name, 
                owner=ctx.author.id, 
                colony_id=ctx.guild.id, 
                private=private, 
                players=[],
                invited=[],
                team1=[],
                team2=[],
                ready=[],
                Round=0,
                field=[],
                graveyard=[],
                feed=[]
            )
            # Start the lobby expiration task
            newbed = discord.Embed(title="", description="Lobby created")
            newbed.set_author(name=ctx.author.name, url=ctx.author.avatar, icon_url=ctx.author.avatar)
            newbed.set_thumbnail(url=self.bot.user.avatar)
            newbed.title = name
            newbed.add_field(name="Players", value=ctx.author.name, inline=False)
            newbed.add_field(name="Team 1", value=lob.team1, inline=True)
            newbed.add_field(name="Team 2", value=lob.team2, inline=True)
            newbed.add_field(name="Ready", value="", inline=False)
            newbed.add_field(name="Spectators", value="", inline=False)
            embed=newbed
            if ctx.interaction:
                await self.interaction_check(interaction=ctx.interaction, embed=newbed)
                return
            else:
                await self.interaction_check(ctx=ctx, embed=newbed)
        else:
            data="You are not in a thread, Create a thread to start a lobby.""\n* All players must be in a thread to start a lobby to prevent spam.""\n* If you start the lobby in a private thread, it will start a private lobby""\n* If you are in a private lobby and invite members to the thread, you must still invite them to the lobby"
            if ctx.interacton:
                await self.interaction_check(interaction=ctx.interaction, data=data, ephemeral=True)
            else:
                await self.interaction_check(ctx=ctx, data=data, ephemeral=True)       
    
    
    @lobby.command(name='private')
    async def private(self, ctx, name: str = None):
        if self.thread_check(ctx):
            await ctx.send("Already in a lobby", ephemeral=True)
        else:
            channel = ctx.channel
            if name:
                thread = await channel.create_thread(name=name, type=discord.ChannelType.private_thread)
            else:
                thread = await channel.create_thread(name=ctx.author.name + "'s Private Culling Game Lobby", type=discord.ChannelType.private_thread)
            
            await thread.edit(owner=ctx.author)
            await ctx.send(f"`Created a private lobby:` {thread.mention}")


    @lobby.command(name='lock')
    async def lock(self, ctx):
        thread= self.thread_check(ctx)
        if thread:
            if thread == "not owner":
                if ctx.interaction:
                    await ctx.interaction.response.send_message("You are not the owner of this lobby", ephemeral=True)
                    return
                else:
                    await ctx.send("You are not the owner of this lobby", ephemeral=True)
                    return
            if thread == "private":
                if ctx.interaction:
                    await ctx.interaction.response.send_message("Already in a private lobby", ephemeral=True)
                    return
                else:
                    await ctx.send("Already in a private lobby", ephemeral=True)
                    return
            if thread == "public":
                realt = await ctx.channel
                await realt.edit(type=discord.ChannelType.private_thread, invitable=False)
                if ctx.interaction:
                    await ctx.interaction.response.send_message("Private lobby enabled", ephemeral=True)
                    return
                else:
                    await ctx.send("Private lobby enabled", ephemeral=True)
                    return
        else:
            if ctx.interaction:
                await ctx.interaction.response.send_message("You are not in a lobby", ephemeral=True)
            await ctx.send("You are not in a lobby", ephemeral=True)
   

    @lobby.command(name='invite')
    async def invite(self, ctx, member: discord.Member):
        thread = self.thread_check(ctx)
        if thread:
            if thread == "not owner":
                if ctx.interaction:
                  await ctx.interaction.response.send_message("Only the lobby owner may invite people", ephemeral=True)
                  return
                else:
                    ctx.send("Only the lobby owner may invite people", ephemeral=True)
                    return
            if thread == "private":
                    realt = await ctx.channel
                    await realt.add_user(member)
                    if ctx.interaction:
                     await ctx.interaction.response.send_message(member.mention + " has been invited to the private lobby", ephemeral=True)
                     return
                    else:
                        await ctx.send(member.mention +  " has been invited to the private lobby", ephemeral=True)
                        return

            else:
                if ctx.interaction:
                    await ctx.interaction.response.send_message("You can only invite people to a private lobby ( if you are owner )", ephemeral=True)
                    return
                else:
                  await ctx.send("You can only invite people to a private lobby ( if you are owner )", ephemeral=True)
                  return
        else:
            if ctx.interaction:
                await ctx.interaction.response.send_message("You are not in a lobby", ephemeral=True)
                return
            else:
              await ctx.send("You are not in a lobby", ephemeral=True)
              return


    @lobby.command(name='leave')
    async def leave(self, ctx):
        thread = self.thread_check(ctx)
        if thread:
            if thread == "not owner":
                await ctx.channel.remove_user(ctx.author)
                if ctx.interaction:
                 await ctx.interaction.response.send_message("You have left the lobby", ephemeral=True)
                 return
                else:
                    await ctx.send("You have left the lobby", ephemeral=True)
            else:
                if ctx.interaction:
                 await ctx.interaction.response.send_message("Lobby owner cannot leave the lobby. Use /lobby disband to disband the lobby.", ephemeral=True)
                 return
                else:
                    await ctx.send("Lobby owner cannot leave the lobby. Use /lobby disband to disband the lobby.", ephemeral=True)
                    return
        else:
            if ctx.interaction:
             await ctx.interaction.response.send_message("You are not in a lobby", ephemeral=True)
            else:
                await ctx.send("You are not in a lobby", ephemeral=True)

    @lobby.command(name='kick')
    async def kick(self, ctx, user: discord.Member):
        thread = self.thread_check(ctx)
        if thread:
            if thread == "not owner":
                await ctx.send("you are not the owner of this lobby " + ctx.author.mention)
            if thread == "private":
                await ctx.channel.remove_user(user)
                await ctx.interaction.response.send_message(user.mention + " `has been kicked by`" + ctx.author.mention)
                
    @lobby.command(name='disband')
    async def disband(self, ctx):
        await ctx.send("Disbanding the lobby...")

async def setup(bot):
    await bot.add_cog(Lobby_Cog(bot))