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
                spectators: list=None, status: int=None,):
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
        self.status=status
       
class Lobby_Cog(commands.Cog):
    def __init__(self, bot): 
         self.bot = bot
         self.lobbies = {}  # Dictionary to store active lobbies

    @commands.Cog.listener()
    async def on_thread_member_join(self, member):
        thread = member.thread
        user= self.bot.get_user(member.id)
        if thread.id in self.lobbies:
            lobby = self.lobbies[thread.id]["Lobby"]
            embed = self.lobbies[thread.id]["embed"]
        else:
            await thread.send("Error adding new player")
        if user.id not in lobby.players:
            if lobby.status == 2:
                lobby.spectators.append(user.id)
                embed.description = "New spectator Joined " + user.mention
                for index, field in enumerate(embed.fields):
                    if field.name == "Spectators":
                        value = field.value
                        new_value = value + "\n" + user.mention
                        embed.set_field_at(index, name=field.name, value=new_value, inline=field.inline)
                        break
            else:
                lobby.players.append(user.id)
                embed.description += "\n New player joined"
                for index, field in enumerate(embed.fields):
                    if field.name == "Players":
                        value = field.value
                        new_value = value + "\n" + user.mention
                        embed.set_field_at(index, name=field.name, value=new_value, inline=field.inline)
                        break
            await thread.send(embed=embed)
        else:
            await thread.send("Player already in lobby " + user.mention)
      
    @commands.hybrid_group(name="lobby", description="Use /lobby <option>")
    async def lobby(self, ctx):

        if ctx.invoked_subcommand is None:

            embed = discord.Embed(title="Lobby commands", description="## Use /lobby `<command>`\n"
            "### /lobby create\n"
            "* Creates a public lobby (public thread)\n### /lobby private\n* Creates a private lobby (private thread)"
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

    def get_thread_description(self, ctx):
        if isinstance(ctx.channel, discord.Thread):
            return ctx.channel.topic  # Returns the thread's description (topic)
        return None
                        
    @lobby.command(name='create')
    async def create(self, ctx, name: str=None, private: bool=False):
        
        if name is None:
            name = f"{ctx.author.name}'s Lobby"
        thread_embed = discord.Embed(title="Lobby created", description=f"Lobby name: {name}\nOwner: {ctx.author.mention}\nPrivate: {private}", color=0x00ff00)
        lob_embed = discord.Embed(title=name, description=name + " lobby created", color=0x00ff00)
        lob_embed.add_field(name="Players", value=f"{ctx.author.mention}", inline=False)
        lob_embed.add_field(name="Status", value="Lobby in queue mode", inline=False)
        lob_embed.add_field(name="Ready", value="List of players ready", inline=False)
        lob_embed.add_field(name="Team 1", value="List of players in team 1", inline=False)
        lob_embed.add_field(name="Team 2", value="List of players in team 2", inline=False)
        lob_embed.add_field(name="Round", value="Round 0", inline=False)
        lob_embed.set_footer(text="Lobby owner " + ctx.author.name + " created at " + datetime.now().astimezone().strftime("%c"), icon_url=ctx.author.avatar.url)
        if private:
            invited = [ctx.author.id]
            thread = await ctx.channel.create_thread(name=name, type=discord.ChannelType.private_thread, auto_archive_duration=60, reason="## Lobby created " + name)
            await thread.add_user(ctx.author)
        else:
            invited = []
            thread = await ctx.channel.create_thread(name=name, type=discord.ChannelType.public_thread, auto_archive_duration=60, reason="## Lobby created " + name)
        self.lobbies[thread.id] ={ "Lobby" :  Lobby(name=name, owner=ctx.author.id, colony_id=0, private=False, players=[ctx.author.id], invited=[invited], team1=[], team2=[],status=1,  ready=[], Round=0, start_time=datetime.now(), timer=300, field=[], graveyard=[], feed=[], spectators = []), "embed" : lob_embed}

        await thread.send(embed=thread_embed)
        await thread.send(embed=lob_embed)
        await ctx.send(f"Lobby created: {thread.mention}")

    @lobby.command(name="kick")
    async def kick(self, ctx, member: discord.Member):
        if ctx.channel.id in self.lobbies.keys():
            lobby = self.lobbies[ctx.channel.id]["Lobby"]
            thread = ctx.channel
            if member.id in lobby.players:
                    lobby.players.remove(member.id)
            if member.id in lobby.spectators:
                    lobby.spectators.remove(member.id)
            if member.id in lobby.invited:
                lobby.invited.remove(member.id)
            await thread.remove_user(member)
            await thread.send(f"{member.id} removed from lobby")
        else:
                await ctx.send("You are not the owner of any lobby or the member is not in the lobby.")
                
    @lobby.command(name='disband')
    async def disband(self, ctx):
        if ctx.channel in self.lobbies.keys():
            lobby = self.lobbies[ctx.channel]
            if ctx.author.id == lobby.owner:
                thread = ctx.channel
                thread.archive = True
                await thread.send("Channel archived")
                thread.lock=True
            else:
                await thread.send("You are not the owner")



async def setup(bot):
    await bot.add_cog(Lobby_Cog(bot))