import discord, datetime, re, random
from game import Enemy, Player
from db import read_player, read_enemy, read_colony
from datetime import datetime
from discord.ext import commands
import time, asyncio

# MAIN CLASS FOR LOBBIES
# Use this to instantiate lobby instances


def healthbar(health, max_health):
    max_dashes = 4
    dash_ratio = max_health / max_dashes
    filled_dashes = 0 if health <= 0 else int(health / dash_ratio)
    
    # Full heart emoji
    dashes = "<:1000001328:1354469784724570172>" * filled_dashes
    
    # Add half heart if there's a decimal portion
    if health > 0 and health % dash_ratio > 0:
        dashes += "<:1000001329:1354469791724736745>"
    
    percent = f"`{0 if health <= 0 else round((health / max_health) * 100)}%`"
    if '-' in percent:
        percent = "`0%`"
    bar = f"{dashes}{percent}"
    return bar

def ce_bar(ce, max_ce):
    max_dashes = 4
    dash_ratio = max_ce / max_dashes
    filled_dashes = 0 if ce <= 0 else int(ce / dash_ratio)
     # Full heart emoji
    dashes = "<:1000001330:1354469798230102258>" * filled_dashes
    # Add half heart if there's a decimal portion
    if ce > 0 and ce % dash_ratio > 0:
        dashes += "<:1000001331:1354469803112403078>"
    percent = f"`{0 if ce <= 0 else round((ce / max_ce) * 100)}%`"
    if '-' in percent:
        percent = "`0%`"
    bar = f"{dashes}{percent}"
    return bar


def remove_name(text, name):
    pattern = re.escape(name)
    return re.sub(pattern, '', text)


def start_pve_embed(lobby):
            #create pve embed
            embed = discord.Embed(title=lobby.name, description="# `ROUND " + str(lobby.round) +"`")
            colony = read_colony(lobby.colony_id)
            max_level=0
            #populate the teamA and teamB list with players
            for p in lobby.players:
                
                player_from_db = read_player(p)
                real_player = Player(**player_from_db.__dict__)

                if p in lobby.ready:
                    if real_player:
                        if real_player.user_id in lobby.teamA['players']:
                            lobby.teamA['players'].remove(real_player.user_id)
                            lobby.add_teamA(real_player)

                        elif real_player.user_id in lobby.teamB:
                            lobby.teamB['players'].remove(real_player.user_id)
                            lobby.add_teamB(real_player)

                    else:
                        lobby.add_spectator(p)
                else:
                    lobby.add_spectator(p)
                        
            enemies = [e for e in colony.enemies if e.level <= max_level]
            e_choice = random.choice(enemies)
            enemy = Enemy(**e_choice.__dict__)
            enemy_list = []
           
            # Handle multiple enemy spawns if quantity is set
            if hasattr(enemy, "quantity") and enemy.quantity > 1:
                for i in range(enemy.quantity):
                    enemy_clone = Enemy(**e_choice.__dict__)
                    enemy_clone.name = f"{enemy_clone.name} {i+1}"
                    enemy_list.append(f"{enemy_clone.name}: {healthbar(enemy_clone.hp, enemy_clone.max_hp)}")
            else:
                enemy_list.append(f"{enemy.name}: {healthbar(enemy.hp, enemy.max_hp)}")
            if lobby.field:
                lobby.field.append(e for e in enemy_list)
            else:
                lobby.field = enemy_list
            
            if  lobby.teamA:
                teamname = lobby.teamA['name'] if lobby.teamA['name'] else  "Team A"
                teamAlist = [p.name for p in lobby.teamA['players']]
                embed.add_field(name=teamname, value="\n".join(teamAlist))
            if  lobby.teamB:
                teamname = lobby.teamB['name'] if lobby.teamB['name'] else  "Team B"
                teamBlist = [p.name for p in lobby.teamB['players']]
                embed.add_field(name=teamname, value="\n".join(teamBlist))

            return embed, lobby

class Lobby():
    def __init__(self, 
                name: str, 
                owner: int, 
                colony_id: int,
                private: bool, 
                players: list, 
                invited: list, 
                teamA: dict,
                teamB:  dict, 
                ready: list, 
                Round: int,
                start_time=time.time(),
                field: dict=None, 
                graveyard: dict=None,
                feed: list=None, 
                spectators: list=None, 
                status: int=None):
        
        self.name = name # name of lobby default to "<player name>'s Lobby"
        self.owner = owner # user_id of the owner of the lobby
        self.colony_id = colony_id # id of colony lobby is created in
        self.private = private # if lobby is private = True
        self.players=players # list of total players in the lobby
        self.invited=invited # list of invited players 
        self.teamA=teamA # list of players who joined team1
        self.teamB=teamB # list of players who joined team2
        self.ready = ready # list of players ready 
        self.round = Round # int of the current turn
        self.start = start_time # date of creation EST
        self.field = field # players and items on the field 
        self.graveyard = graveyard # players killed in this battle
        self.feed = feed # battle feed 
        self.spectators=spectators
        self.status=status
       
    def add_player(self, player):
        if player in self.players:
              return False
        self.players.append(player)
        return True
        
    def remove_player(self, player):
        if player in self.players:
            self.players.remove(player)
            if player in self.teamA:
                self.teamA.remove(player)
            if player in self.teamB:
                self.teamB.remove(player)
            if player in self.spectators:
             self.spectators.remove(player)
            if player in self.field:
                self.field.remove(player)
            if player in self.invited:
                self.invited.remove(player)
            if player in self.ready:
                self.ready.remove(player)
            if player in self.field:
                self.field.remove(player)
            # Check if the player is the owner
            if player == self.owner:
                if self.players:  # If there are more players left
                    self.owner = random.choice(self.players)  # Set a new owner
                else:  # If no players are left
                    return False  # Indicate that the lobby should be deleted
            return True
                
        else:
            return False
         
    def add_spectator(self, player):
        if player in self.spectators:
              return False
        self.spectators.append(player)
        return True

    def set_teamA_name(self, name):
        self.teamA['name'] = name
        return True
    
    def add_teamA(self, player):
        if player in self.teamA['players']:
           return False
        if player in self.teamB['players']:
              self.teamB.remove(player)
        player_list = [p for p in self.teamA['players']]
        player_list.append(player)
        self.teamA['players'] = player_list 
        return True
    

    def set_teamB_name(self, name):
        self.teamB['name'] = name
        return True
    
    def add_teamB(self, player):
         if player in self.teamA['players']:
              self.teamA['players'].remove(player)
         if player in self.teamB['players']:
              return False
         player_list = [p for p in self.teamB['players']]
         player_list.append(player)
         self.teamB['players'] = player_list 
         return True
    
    def player_killed(self, player):
        if player in self.teamB or self.teamA or self.field:

            self.remove_player(player)

            self.graveyard.append({"player" : player.__dict__, "killed by" : player.killed})
            return True
        else:
             return False
        
    def ready_up(self, player):
        if player in self.players:
            if player in self.ready:
                self.ready.remove(player)
                return False
            else:
                 self.ready.append(player)
                 return True
        else:
             return False
        

def generate_lobby_embed(lobby: Lobby, bot) -> discord.Embed:
    embed = discord.Embed(
        title=f"{lobby.name}",
        description=f"Owner: <@{lobby.owner}>\nStatus: {'Active PvE' if lobby.status == 2 else 'Active PvP' if lobby.status == 3 else 'In Queue'}",
        color=discord.Color.from_rgb(255, 251,  86)
    )
    owner_user = bot.get_user(lobby.owner)
    embed.set_author(name="Lobby", icon_url=owner_user.avatar.url if owner_user else None)
    embed.set_thumbnail(url=bot.user.avatar.url)
    embed.add_field(name="Players", value="\n".join(f"<@{player}>" for player in lobby.players) or "No players", inline=False)
    embed.add_field(name="Team A", value="\n".join(f"<@{player}>" for player in lobby.teamA) or "No players", inline=True)
    embed.add_field(name="Team B", value="\n".join(f"<@{player}>" for player in lobby.teamB) or "No players", inline=True)
    embed.add_field(name="Ready Players", value="\n".join(f"<@{player}>" for player in lobby.ready) or "No players", inline=False)
    embed.add_field(name="Spectators", value="\n".join(f"<@{player}>" for player in lobby.spectators) or "No spectators", inline=False)
    if lobby.private:
        embed.add_field(name="Invited Players", value="\n".join(f"<@{player}>" for player in lobby.invited) or "No invited players", inline=False)
    embed.set_footer(
        text=f"Lobby created at {lobby.start.astimezone().strftime('%c')}",
        icon_url=None  # Optionally, you can add an icon URL here
    )
    return embed


class Lobby_Cog(commands.Cog):
    def __init__(self, bot): 
        self.bot = bot
        self.lobbies = {}  # Dictionary to store active lobbies
        # Reference to the battle cog for starting battles
        self.battle_cog = bot.get_cog('battle')
    @commands.Cog.listener()
    async def on_thread_member_join(self, member):
        thread = member.thread
        user= self.bot.get_user(member.id)
        if thread.id in self.lobbies:
            lobby = self.lobbies[thread.id]["Lobby"]
        else:
            return
    
        if user.id not in lobby.players and user.id not in lobby.invited:
            lobby.add_player(user.id)
            embed = generate_lobby_embed(lobby, self.bot)
            self.lobbies[thread.id]["embed"] = embed
            embed.description = "New player joined " + user.mention
            await thread.send(embed=embed)
            
        elif user.id in lobby.invited:
            lobby.add_player(user.id)
            embed = generate_lobby_embed(lobby, self.bot)
            self.lobbies[thread.id]["embed"] = embed
            await thread.send("Invited player joined " + user.mention)

        elif user.id in lobby.players:
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
            
    @lobby.command(name="invite")
    async def invite(self, ctx, member: discord.Member):
        # Check if the command is used in a thread context
        if not isinstance(ctx.channel, discord.Thread):
            await ctx.send("This command can only be used in a thread.", ephemeral=True)
            return
        # Check if the thread is a private thread
        thread_type = self.thread_check(ctx)
        if thread_type != "private":
            await ctx.send("This command can only be used in private threads.", ephemeral=True)
            return
        # Check if the current channel is a private thread and if it exists in the lobbies
        if ctx.channel.id in self.lobbies.keys():
            lobby = self.lobbies[ctx.channel.id]["Lobby"]
            thread = ctx.channel
            # Ensure the lobby is private
            if not lobby.private:
                await ctx.send("This command can only be used in private lobbies.", ephemeral=True)
                return
            # Check if the user issuing the command is the lobby owner
            if ctx.author.id != lobby.owner:
                await ctx.send("Only the lobby owner can invite players.", ephemeral=True)
                return
            # Check if the member is already in the lobby
            if member.id in lobby.invited:
                await ctx.send(f"{member.mention} is already in invited.", ephemeral=True)
                return
            # Add the member to the invited list and the thread
            lobby.invited.append(member.id)
            lobby.add_player(member.id)
            await thread.add_user(member)
            await ctx.send(f"{member.mention} has been invited to the lobby.")
            # Update the embed
            embed = generate_lobby_embed(lobby, self.bot)
            self.lobbies[ctx.channel.id]["embed"] = embed
            await ctx.send(embed=embed)
            return
        else:
            await ctx.send("This channel is not associated with a lobby.", ephemeral=True)
            return


    @lobby.command(name='create')
    async def create(self, ctx, name: str=None, private: bool=False):
        if name is None:
            name = f"{ctx.author.name}'s Lobby"
        player_data = read_player(ctx.author.id, ctx.guild.id)
        if player_data:
             print(player_data)
        else:
             embed= discord.Embed(title="Error reading player", description="Player not found. Use /create or ,create to create a player in a colony!")
             await ctx.send(embed=embed, ephemeral=True)
             return False
        if private:
            invited = [ctx.author.id]
            thread = await ctx.channel.create_thread(name=name, type=discord.ChannelType.private_thread,
                                                      auto_archive_duration=1440, reason="## Lobby created " + name)
            await thread.add_user(ctx.author)
            await thread.edit(invitable=False)
            await thread.send("Private lobby created, only invited players can join.")
            self.lobbies[thread.id] ={ "Lobby" :  Lobby(name=name, owner=ctx.author.id, colony_id=0, private=True,
                                                     players=[ctx.author.id], invited=invited, teamA=[], teamB=[],
                                                    status=1,  ready=[], Round=0, start_time=datetime.now(),
                                                    field=[], graveyard=[], feed=[], spectators = []), "embed" : ""}
        else:
            thread = await ctx.channel.create_thread(name=name, type=discord.ChannelType.public_thread, auto_archive_duration=1440, 
                                                     reason="## Lobby created " + name)
            self.lobbies[thread.id] ={ "Lobby" :  Lobby(name=name, owner=ctx.author.id, colony_id=0, private=False,
                                                        players=[ctx.author.id], invited=[], teamA=[], teamB=[],
                                                        status=1,  ready=[], Round=0, start_time=datetime.now(),
                                                        field=[], graveyard=[], feed=[], spectators = []), "embed" : ""}
        lobby = self.lobbies[thread.id]["Lobby"]
        embed = generate_lobby_embed(lobby, self.bot)
        self.lobbies[thread.id]["embed"] = embed
        embed.description = "Lobby created: " + thread.mention
        embed.set_footer(text="Lobby owner " + ctx.author.name + " created at " +  datetime.now().astimezone().strftime("%c"), icon_url=ctx.author.avatar.url)
        await thread.send(embed=embed)
        await ctx.send(f"Lobby created: {thread.mention}")

    @lobby.command(name="kick")
    async def kick(self, ctx, member: discord.Member):
        if ctx.channel.id in self.lobbies.keys():
            lobby = self.lobbies[ctx.channel.id]["Lobby"]
            embed = self.lobbies[ctx.channel.id]["embed"]
            thread = ctx.channel
            user = self.bot.get_user(member.id)        
            lobby.remove_player(member.id)
            embed = generate_lobby_embed(lobby, self.bot)
            embed.description = "Player removed from lobby: " + user.mention
            self.lobbies[ctx.channel.id]["embed"] = embed
            await thread.remove_user(member)
            await thread.send(f"{member.id} removed from lobby")
            await ctx.send(embed=embed)

        else:
                await ctx.send("You are not the owner of any lobby or the member is not in the lobby.")
                
    @lobby.command(name='disband')
    async def disband(self, ctx):
        if ctx.channel.id in self.lobbies.keys():
            lobby = self.lobbies[ctx.channel.id]["Lobby"]
            if ctx.author.id == lobby.owner:
                del(lobby)
                embed = self.lobbies[ctx.channel.id]["embed"]
                del(embed)
                del(self.lobbies[ctx.channel.id])
                thread = ctx.channel
                await ctx.send("`Lobby Disbanded`")
                await thread.send("`Channel Archived` at " + "`"  + datetime.now().astimezone().strftime('%c') + "`")
                await thread.edit(locked=True)
                await thread.edit(archived=True)
                return
      
            else:
                await thread.send("You are not the owner")


    @lobby.command(name='leave')
    async def kick(self, ctx):
        lobby = self.lobbies[ctx.channel.id]["Lobby"]
        thread= ctx.channel
        if ctx.channel.id in self.lobbies.keys():
            if ctx.author.id == lobby.owner:
                await thread.send("`Owner Leaving Lobby, New Owner Will Be Selected`")
            player_removed = lobby.remove_player(ctx.author.id)
            if player_removed == "delete_lobby":
                await thread.send("`No New Owner Found Lobby Will Be Deleted`")
                del self.lobbies[ctx.channel.id]
              
                await thread.send("`Channel Archived` at " + "`"  + datetime.now().astimezone().strftime('%c') + "`")
                await thread.edit(locked=True)
                await thread.edit(archived=True)
                return
            await thread.send(f"{ctx.author.mention} has left the lobby.")
            embed = generate_lobby_embed(lobby, self.bot)
            self.lobbies[ctx.channel.id]["embed"] = embed
            embed.description = "Player left lobby: " + ctx.author.mention
            await ctx.send("`Lobby updated`")
            await thread.send(embed=embed)
        else:
             await thread.send("`Error: lobby doesn't exist`")


    @lobby.command(name="start")
    async def start(self, ctx, pve: bool=False, pvp: bool=False):
        if pve:
            lobby = self.lobbies[ctx.channel.id]['Lobby']
            if lobby:
                if len(lobby.teamA) and len(lobby.teamB) == 0:
                    if lobby.players:
                        lobby.teamA = lobby.players
                    else:
                        return 
        if pvp:
            pass


async def setup(bot):
    await bot.add_cog(Lobby_Cog(bot))