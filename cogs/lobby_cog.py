import discord, datetime
from datetime import datetime
from discord.ext import commands
from discord import app_commands

# MAIN CLASS FOR LOBBIES
# Use this to instantiate lobby instances

class Lobby():
    def __init__(self, name: str, owner: int, colony_id: int, private: bool, players: list, 
                 invited: list, 
                 team1: list,
                  team2: list, ready: list, turn: int,
                 created_at=datetime.now(), field: list=None, graveyard: list=None,
                   feed: list=None, spectators: list=None):
        self.name = name # name of lobby default to "<player name>'s Lobby"
        self.owner = owner # user_id of the owner of the lobby
        self.colony_id = colony_id # id of colony lobby is created in
        self.private = private # if lobby is private = True
        self.players=players # list of total players in the lobby
        self.invited=invited # list of invited players 
        self.team1=team1 # list of players who joined team1
        self.team2=team2 # list of players who joined team2
        self.read = ready # list of payers ready 
        self.turn = turn # int of the current turn
        self.create_at = created_at # date of creation EST
        self.field = field # players and items on the field 
        self.graveyard = graveyard # players killed in this battle
        self.feed = feed # battle feed 
        self.spectators=spectators
        self.time_active=datetime.now()




def create_lobby(player, colony, name=None, private: bool=None):
    lob = Lobby(name=name, owner=player, colony_id=colony, private=False, players=[player], invited=[], team1=[], team2=[], ready=[], turn=0)
    return lob 

class Lobby_Cog(commands.Cog):
    def __init__(self, bot): 
         self.bot = bot
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
        tclass= self.thread_check(ctx)
        if tclass== "private" or tclass == "public":
            if not name:
                name = ctx.author.name + "'s Lobby"
            private = False if tclass=="public" else True
            lob =create_lobby(ctx.author.id, ctx.guild.id, name=name, private=private)
            newbed=discord.Embed(title="", description="Lobby created")
            newbed.set_author(name=ctx.author.name, url=ctx.author.avatar, icon_url=ctx.author.avatar)
            newbed.set_thumbnail(url=self.bot.user.avatar)
            newbed.title=name
            newbed.add_field(name="Players", value=ctx.author.name, inline=False)
            newbed.add_field(name="Team 1", value=lob.team1, inline=True)
            newbed.add_field(name="Team 2", value=lob.team2, inline=True)
            newbed.add_field(name="Ready", value="", inline=False)
            newbed.add_field(name="Spectators", value="", inline=False)
            newbed.set_footer(text="Privacy: " + tclass + " || Created at: " + lob.create_at, icon_url=self.bot.user.avatar)
            print(lob.time_active)
            if ctx.interaction:
                await ctx.interaction.response.send_message(embed=newbed)
            else:
                await ctx.send(embed=newbed)
            return
        else:
            if ctx.interaction:
                await ctx.interaction.response.send_message("You are not in a thread, Create a thread to start a lobby."
                "\n* All players must be in a thread to start a lobby to prevent spam."
                "\n* If you start the lobby in a private thread, it will start a private lobby\n* If you are in a private lobby and invite members to the thread, you must still invite them to the lobby")
            else:
                await ctx.send("You are not in a thread, Create a thread to start a lobby."
                "\n* All players must be in a thread to start a lobby to prevent spam."
                "\n* If you start the lobby in a private thread, it will start a private lobby")
            return

       


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