import discord, datetime, re, random, copy
from game import Enemy, Player
from db import read_player, read_enemy, read_colony
from datetime import datetime
from discord.ext import commands
import time, asyncio

# MAIN CLASS FOR LOBBIES
# Use this to instantiate lobby instances

#region Healthbar 
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
#endregion

#region CE Bar
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
#endregion

#region Remove Characters
def remove_name(text, name):
    pattern = re.escape(name)
    return re.sub(pattern, '', text)
#endregion

#region Round embed
def start_round_embed(lobby, bot):
    # Create pve embed
    embed = discord.Embed(title=lobby.name, description="# `ROUND " + str(lobby.round) +"`")
    colony = read_colony(lobby.colony_id)
    if not colony:
        return False
    # Populate the teamA and teamB list with players
    playerlist = []
    for p in lobby.players:
        player = read_player(p, lobby.colony_id)
        # Initialize real_player as None for safety
        real_player = None
        if player:
            tech = player['techniques'][0] if player['techniques'] else None
            player['technique'] = tech['name']
            del player['techniques']
            del player['id']
            real_player = Player(**player)
            playerlist.append(real_player)
            if all(real_player.user_id != p.user_id for p in lobby.teamB['players']) and all(real_player.user_id != p.user_id for p in lobby.teamA['players']):
                lobby.add_field(real_player)
        else:
            # If player data couldn't be retrieved, remove from lobby
            lobby.remove_player(p)
            
        enemies = []

        for e in colony.enemies:
            highest_level = max(p.level for p in playerlist)
            if not e.killed:
                e.level <= highest_level
                enemies.append(e)

        if enemies:  # Make sure there are enemies to choose from
            e_choice = random.choice(enemies)
            enemy = None
            for e  in Enemy.__subclasses__():
                current_enemy = e()
                if current_enemy.name == e_choice.name:
                    enemy = current_enemy
                    break

            enemy_list = [enemy]
            # Handle multiple enemy spawns if quantity is set
            if enemy.quantity and enemy.quantity > 1:
                    for e in range(enemy.quantity):
                        enemy_clone = copy.deepcopy(enemy)
                        print(enemy.name + " was cloned")
                        enemy_list.append(enemy_clone)

            for e in enemy_list:
                    lobby.add_field(e) 
    
    # Team display section
    if lobby.teamA and lobby.teamA['players']:
        teamname = lobby.teamA['name'] if lobby.teamA['name'] else "Team A"
        teamAlist = [p.name for p in lobby.teamA['players']]
        embed.add_field(name=teamname, value="\n".join(teamAlist) if teamAlist else "Empty")
    
    if lobby.teamB and lobby.teamB['players']:
        teamname = lobby.teamB['name'] if lobby.teamB['name'] else "Team B"
        teamBlist = [p.name for p in lobby.teamB['players']]
        embed.add_field(name=teamname, value="\n".join(teamBlist) if teamBlist else "Empty")

    if lobby.field:
        field_values = [thing.name for thing in lobby.field.values()]
        if field_values:
            embed.add_field(name="Field", value="\n".join(field_values) if field_values else "Empty")
        else:
            embed.add_field(name="Field", value="Empty")
    
    if lobby.spectators:
        spectators = [p.name for p in lobby.spectators]
        if spectators:
            embed.add_field(name="Spectators", value="\n".join(spectators) if spectators else "None")
        else:
            embed.add_field(name="Spectators", value="Empty")
    embed.set_thumbnail(url=bot.user.avatar.url)
    return embed, lobby
#endregion


#region team embed
def team_option_embed(lobby, bot, player):
    lobby.teamA['name'] = lobby.teamA['name'] if lobby.teamA['name'] else "Team A"
    lobby.teamB['name'] = lobby.teamB['name'] if lobby.teamB['name'] else "Team B"
    embed = discord.Embed(title=lobby.name, description="Team Select")
    current_team = None
    if player in lobby.teamA['players']:
        leader = lobby.teamA['leader'] if lobby.teamA['leader'] else None
        if leader and player.user_id == leader.user_id:
            current_team = "Leader of " + lobby.teamA['name']
        else:
            current_team = lobby.teamB['name']

    elif player in lobby.teamB['players']:
        leader = lobby.teamB['leader'] if lobby.teamB['leader'] else None
        if leader and player.user_id == leader.user_id:
            current_team = "Leader of " + lobby.teamB['name']
        
        else:
            current_team = lobby.teamB['name']
            
    elif player.name in lobby.field.keys():
        current_team = "Field"

    elif player in lobby.spectators:
        current_team = "Spectator"

    embed.add_field(name="Current Team", 
                    value=current_team, 
                    inline=True)
    embed.set_thumbnail(url=bot.user.avatar.url)
    embed.set_footer(text="Select a team to join")
    return embed
#endregion

#region Lobby class
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
                feed: dict=None, 
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
        uid = player.user_id if isinstance(player, Player) else player
        if uid in self.players:
            self.players.remove(uid)
            if player in self.teamA['players']:
                if player == self.teamA['leader']:
                    self.teamA['leader'] = None
                self.teamA['players'].remove(player)
            if player in self.teamB['players']:
                if player == self.teamB['leader']:
                    self.teamB['leader'] = None
                self.teamB['players'].remove(player)
            if player in self.spectators:
             self.spectators.remove(player)
            if player in self.invited:
                self.invited.remove(player)
            if player in self.ready:
                self.ready.remove(player)
            if player in self.field.values():
                del self.field[player.name]
            # Check if the player is the owner
            if player == self.owner:
                if self.players:  # If there are more players left
                    self.owner = random.choice(self.players)  # Set a new owner
                else:  # If no players are left
                    return False  # Indicate that the lobby should be deleted
            return True
        elif player in self.field.values():
            del self.field[player.name]
        
        elif player in self.teamB['players']:
            self.teamB['players'].remove(player)
        
        elif player in self.teamA['players']:
            self.teamA['players'].remove(player)
        elif player in self.spectators:
            self.spectators.remove(player)
        else:
            return False
         
    def add_spectator(self, player):
        if player in self.spectators:
              return False
        if player in self.teamA['players']:
            self.remove_teamA(player)
        if player in self.teamB['players']:
            self.remove_teamB(player)
        if player.name in self.field.keys():
                del self.field[player.name]
        self.spectators.append(player)
        return True
    def remove_spectator(self, player):
        if player in self.spectators:
            self.spectators.remove(player)
            return True
        else:
            return False
    def set_teamA_name(self, name):
        self.teamA['name'] = name
        return True
    
    def add_teamA(self, player):
        if self.teamA['leader'] == '' or self.teamA['leader'] == None:
            self.teamA['leader'] = player
        if player in self.teamA['players']:
           return False
        if player in self.teamB['players']:
              self.remove_teamB(player)
        if player.name in self.field.keys():
                del self.field[player.name]
        if player in self.spectators:
                self.spectators.remove(player)
        player_list = [p for p in self.teamA['players']]
        player_list.append(player)
        self.teamA['players'] = player_list 
        return True
    
    def remove_teamA(self, player):
        if player in self.teamA['players']:
            if player == self.teamA['leader']:
                self.teamA['leader'] = None
            teama = self.teamA['players']
            teama.remove(player)  
            self.teamA['players'] = teama
            return True
        else:
            return False
        
    def add_teamB(self, player):
         if self.teamB['leader'] == None or self.teamA['leader'] == '':
            self.teamB['leader'] = player
         if player in self.teamA['players']:
              self.remove_teamA(player)
         if player.name in self.field.keys():
                del self.field[player.name]
         if player in self.spectators:
                self.spectators.remove(player)  
         if player in self.teamB['players']:
              return False
         player_list = [p for p in self.teamB['players']]
         player_list.append(player)
         self.teamB['players'] = player_list 
         return True
    
    def remove_teamB(self, player):
        if player in self.teamB['players']:
            if player == self.teamB['leader']:
                self.teamB['leader'] = None
            teamb = self.teamA['players']
            teamb.remove(player)  
            self.teamB['players'] = teamb
            return True
        else:
            return False
        
    def add_field(self, thing):
        if not isinstance(thing, Player):
            if thing.name in self.field.keys():
                total_things = [k for k in self.field.keys() if k.startswith(thing.name)]
                name = thing.name + " " + str(len(total_things) + 1)
                thing.name = name
            else:
                name = thing.name
        else:
            if thing.name in self.field.keys():
                return False
            if thing in self.teamA['players']:
                self.remove_teamA(thing)
            if thing in self.teamB['players']:
                self.remove_teamB(thing)
            if thing in self.spectators:
                self.spectators.remove(thing)
            name = thing.name
             
        self.field[name] = thing
        return True
    
    def remove_field(self, thing):
        if self.thing in self.field.values():
            del self.field[thing.name]
            return True
        else:
            return False

    def set_teamB_name(self, name):
        self.teamB['name'] = name
        return True
    

    
    def remove_teamB(self, player):
        if player in self.teamB['players']:
            self.teamB['players'].remove(player)
            return True
        else:
            return False
    
    def add_feed(self, text):
        self.feed.append(text)
        return True

    def player_killed(self, player):
        if player in self.teamB or self.teamA or self.field:
            self.remove_player(player)
            self.graveyard.append({"player" : player.__dict__, "killed by" : player.killed})
            return 
        else:
             return False
        
    def ready_up(self, player):
        if player in self.players:
            if player in self.ready:
                self.ready.remove(player)
                return
            else:
                 self.ready.append(player)
                 return 
        else:
             return False
#endregion

#region Generate lobby
def generate_lobby_embed(lobby: Lobby, bot) -> discord.Embed:
    embed = discord.Embed(
        title=f"{lobby.name}",
        description=f"Owner: <@{lobby.owner}>\nStatus: {'Active PvE' if lobby.status == 2 else 'Active PvP' if lobby.status == 3 else 'In Queue'}",
        color=discord.Color.from_rgb(255, 251,  86)
    )
    owner_user = bot.get_user(lobby.owner)
    teama_name = lobby.teamA['name'] if lobby.teamA['name'] else "Team A"
    teamb_name = lobby.teamB['name'] if lobby.teamB['name'] else "Team B"
    embed.set_author(name="Lobby", icon_url=owner_user.avatar.url if owner_user else None)
    embed.set_thumbnail(url=bot.user.avatar.url)
    embed.add_field(name="Players", value="\n".join(f"<@{player}>" for player in lobby.players) or "No players", inline=False)
    embed.add_field(name=teama_name, value="\n".join(f"{player.name}" for player in lobby.teamA['players']) or "No players", inline=True)
    embed.add_field(name=teamb_name, value="\n".join(f"{player.name}" for player in lobby.teamB['players']) or "No players", inline=True)
    embed.add_field(name="Ready Players", value="\n".join(f"<@{player}>" for player in lobby.ready) or "No players", inline=False)
    embed.add_field(name="Spectators", value="\n".join(f"<@{player}>" for player in lobby.spectators) or "No spectators", inline=False)
    
    if lobby.private:
        embed.add_field(name="Invited Players", value="\n".join(f"<@{player}>" for player in lobby.invited) or "No invited players", inline=False)
    
    embed.set_footer(
        text=f"Lobby created at {lobby.start.astimezone().strftime('%c')}",
        icon_url=None  
    )
    return embed
#endregion

#region Lobby Cog
class Lobby_Cog(commands.Cog):
    def __init__(self, bot): 
        self.bot = bot
        self.lobbies = {}  # Dictionary to store active lobbies
        # Reference to the battle cog for starting battles
        self.battle_cog = bot.get_cog("Battle")
        if self.battle_cog is None:
            raise ValueError("Battle_Cog not found. Ensure it is loaded before Lobby_Cog.")
        
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
            return
      
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

            
    @lobby.command(name="ready")
    async def ready(self, ctx):
        lobby = self.lobbies[ctx.channel.id]["Lobby"]
        if lobby:
            user_id = ctx.author.id
            if user_id in lobby.players:
                if user_id in lobby.ready:
                    lobby.ready.remove(user_id)
                    embed = generate_lobby_embed(lobby, self.bot)
                    self.lobbies[ctx.channel.id]["embed"] = embed
                    await ctx.send(f"{ctx.author.mention} is no longer ready.")
                else:
                    lobby.ready.append(user_id)
                    embed = generate_lobby_embed(lobby, self.bot)
                    self.lobbies[ctx.channel.id]["embed"] = embed
                    await ctx.send(f"{ctx.author.mention} is now ready.")

            
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
    async def create(self, ctx, name: str=None):
        if name is None:
            name = f"{ctx.author.name}'s Lobby"
        player_data = read_player(ctx.author.id, ctx.guild.id)
        if player_data:
             print(player_data)
        else:
             embed= discord.Embed(title="Error reading player", description="Player not found. Use /create or ,create to create a player in a colony!")
             await ctx.send(embed=embed, ephemeral=True)
             return False
        invited = [ctx.author.id]
        thread = await ctx.channel.create_thread(name=name, type=discord.ChannelType.private_thread,
                                                      auto_archive_duration=1440, reason="## Lobby created " + name)
        await thread.add_user(ctx.author)
        await thread.edit(invitable=False)
        await thread.send("Private lobby created, only invited players can join.")
        self.lobbies[thread.id] ={ "Lobby" :  Lobby(name=name, owner=ctx.author.id, colony_id=ctx.guild.id, private=True,
                                                     players=[ctx.author.id], invited=invited, teamA={"name" : "Team A", "players" : [], "leader" : ""}, 
                                                     teamB={"name" : "Team B", "players" : [], "leader" : ""},
                                                    status=0,  ready=[], Round=0, start_time=datetime.now(),
                                                    field={}, graveyard=[], feed=[], spectators = []), "embed" : ""}
        
        lobby = self.lobbies[thread.id]["Lobby"]
        embed = generate_lobby_embed(lobby, self.bot)
        self.lobbies[thread.id]["embed"] = embed
        embed.description = "Lobby created: " + thread.mention
        embed.set_footer(text="Lobby owner " + ctx.author.name + " created at " +  datetime.now().astimezone().strftime("%c"), icon_url=ctx.author.avatar.url)
        await thread.send(embed=embed)
        await ctx.send(f"Lobby created: {thread.mention}")
        lobby_view = LobbyView(lobby, self.bot, self.lobbies)
        await thread.send(view=lobby_view)

    @lobby.command(name="team")
    async def team(self, ctx):
        lobby = self.lobbies[ctx.channel.id]["Lobby"]
        if lobby:
            if ctx.author.id in lobby.players:
                player_dict = read_player(ctx.author.id, ctx.guild.id)
                tech = player_dict['techniques'][0] if player_dict['techniques'] else None
                player_dict['technique'] = tech['name'] if tech else None
                del player_dict['techniques'] 
                del player_dict['id']
                player = Player(**player_dict)
                embed = team_option_embed(lobby, self.bot, player)
                msg = await ctx.send(embed=embed)
                view = TeamSelectView(lobby, self, player)
                await msg.edit(view=view)
                return
            else:
                await ctx.send("You are not in the lobby.")
                return
        else:
            await ctx.send("You are not in the lobby.")
            return
    
    @lobby.command(name="name")
    async def name(self, ctx, name: str):
        thread = ctx.channel.id
        user = ctx.author.id
        embed = discord.Embed(title='Change Team Name', description='')
        if thread in self.lobbies:
            lobby = self.lobbies[thread]['Lobby']
            if lobby:
                if user == lobby.owner:
                    embed.title = "Change Name"
                    embed.description = "Choose to change your team name or your lobby's name to: " + name
                    await ctx.send(embed=embed, view=OwnerLobbyView(lobby, self.bot, name))
                    return
                teama = lobby.teamA['name'] if lobby.teamA['name'] else "Team A"
                teamb = lobby.teamB['name'] if lobby.teamB['name'] else "Team B"
                leader_a = lobby.teamA['leader'] if lobby.teamA['leader'] else None
                leader_b = lobby.teamB['leader'] if lobby.teamB['leader'] else None
                if leader_a:
                    if user == leader_a.user_id:
                        if name == teamb:
                            embed.description = ("Cannot set " + name + "to " + teamb)
                            await ctx.send(embed=embed, ephemeral=True)
                            return
                        if lobby.set_teamA_name(name):
                            embed.description = ("Change team name to: " + name)
                            await ctx.send(embed=embed, ephemeral=True)
                            return
                        else: 
                            embed.description = ("Error setting name to: " + name)
                            await ctx.send(embed=embed, ephemeral=True)
                            return
                  
                elif leader_b:
                    if user == leader_b.user_id:
                        if name == teama:
                            embed.description = ("Cannot set " + name + "to " + teama)
                            await ctx.send(embed=embed, ephemeral=True)
                            return
                        if lobby.set_teamB_name(name):
                            embed.description = ("Change team name to:" + name)
                            await ctx.send(embed=embed, ephemeral=True)
                            return
                        else: 
                            embed.description = ("Error setting name to:" + name)
                            await ctx.send(embed=embed, ephemeral=True)
                            return


                else:
                    embed.description = ("You are not in a team")
                    await ctx.send(embed=embed, ephemeral=True)
                    return

            else:
                embed.description = ("You are not in a lobby")
                await ctx.send(embed=embed, ephemeral=True)
                return
        else:
            embed.description = ("There is no lobby")
            await ctx.send(embed=embed, ephemeral=True)
            return
        


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
                await ctx.send("You are not the owner")

    @lobby.command(name='leave')
    async def leave(self, ctx):
        lobby = self.lobbies[ctx.channel.id]["Lobby"]
        thread= ctx.channel
        if ctx.channel.id in self.lobbies.keys():
            if ctx.author.id == lobby.owner:
                await thread.send("`Owner Leaving Lobby, New Owner Will Be Selected`")
            player_removed = lobby.remove_player(ctx.author.id)
            if player_removed == "delete_lobby":
                await thread.send("`No New Owner Found Lobby Will Be Deleted`")
                del self.lobbies[ctx.channel.id]
                await ctx.send("`Channel Archived` at " + "`"  + datetime.now().astimezone().strftime('%c') + "`")
                await thread.edit(locked=True)
                await thread.edit(archived=True)
                return
            await ctx.send(f"{ctx.author.mention} has left the lobby.")
            embed = generate_lobby_embed(lobby, self.bot)
            self.lobbies[ctx.channel.id]["embed"] = embed
            embed.description = "Player left lobby: " + ctx.author.mention
            await ctx.send("`Lobby updated`")
            await thread.send(embed=embed)
            return
        else:
             await ctx.send("`Error: lobby doesn't exist`")
             return

    @lobby.command(name="start")
    async def start(self, ctx):
        lobby = self.lobbies[ctx.channel.id]["Lobby"]
        lobby.status = 1
        lobby.ready = []
        if ctx.channel.id in self.lobbies.keys():
            if ctx.author.id == lobby.owner:
                if lobby.status == 1:
                    lobby.round = 0
                    embed, lobby = start_round_embed(lobby, self.bot)
                    battle_cog = self.bot.get_cog("Battle")
                    if battle_cog is None:
                        await ctx.send("Battle cog not found.")
                        await ctx.channel.send(embed=embed)
                        return
                    view = battle_cog.BattleView(lobby, self.bot)
                    lobby.feed = [{
                          'attacks' : {lobby.teamA['name'] : {}, lobby.teamB['name'] : {}, 'Field' : {}}, 
                          'defenses':{lobby.teamA['name'] : {}, lobby.teamB['name'] : {}, 'Field' : {}}, 
                          'barriers' : {lobby.teamA['name'] : {}, lobby.teamB['name'] : {}, 'Field' : {}}
                          }]
                    await ctx.send(embed=embed, view=view)
                    return
                else:
                    await ctx.send("`Lobby is already in battle`")
                    return
            else:
                await ctx.send("You are not the owner of this lobby")
                return
        
        else:
            await ctx.send("You are not in a lobby")
            return

#endregion

# region OwnerLobbyView
class OwnerLobbyView(discord.ui.View):
    def __init__(self, lobby, bot, name):
        super().__init__()
        self.lobby = lobby
        self.name = name
        self.bot = bot

    @discord.ui.button(label="Team", style=discord.ButtonStyle.primary)
    async def team_button(self,itx: discord.Interaction, btn: discord.ui.Button):
        btn.disabled=True
        user_id = itx.user.id
        leader_a = self.lobby.teamA['leader'] if self.lobby.teamA['leader'] else None
        leader_b = self.lobby.teamB['leader'] if self.lobby.teamB['leader'] else None

        if leader_a:
            if user_id == leader_a.user_id :
                self.lobby.teamA['name'] = self.name
                await itx.response.edit_message(content="Team name changed to: " + self.name)
                embed = generate_lobby_embed(self.lobby, self.bot)
                channel = itx.channel
                await channel.send(embed=embed)
                return
            
        if leader_b:
            if user_id == leader_b.user_id:
                self.lobby.teamB['name'] = self.name
                await itx.response.send_message(content="Team name changed to: " + self.name)
                embed = generate_lobby_embed(self.lobby, self.bot)
                channel = itx.channel
                await channel.send(embed=embed, view=LobbyView())
                return
        else:
            await itx.response.send_message("You are not a leader of any team")
            return
            
    @discord.ui.button(label="Lobby", style=discord.ButtonStyle.primary)
    async def lobby_button(self, itx: discord.Interaction, btn: discord.ui.Button):
        btn.disabled=True
        user_id = itx.user.id
        if user_id == self.lobby.owner:
            self.lobby.name = self.name
            embed = generate_lobby_embed(self.lobby, self.bot)
            self.lobby.embed = embed
            embed.description = "Lobby name changed to: " + self.name
            await itx.response.send_message(embed=embed)
            return
    
        else:
            await itx.response.send_message("You are not the owner of this lobby", view=self)
            return
          

#endregion


#region TeamSelect View
class TeamSelect(discord.ui.Select):
    def __init__(self, lobby, cog, player):
        options= [
discord.SelectOption(label=lobby.teamA['name'], value="teama", description=", ".join(p.name for p in lobby.teamA['players'])),
discord.SelectOption(label=lobby.teamB['name'], value="teamb", description=", ".join(p.name for p in lobby.teamB['players'])),
discord.SelectOption(label="Field", value="field", description=", ".join(v.name for v in lobby.field.values())),
discord.SelectOption(label="Spectator", value="spectator", description=", ".join(p.name for p in lobby.spectators)),
        ]
        super().__init__(placeholder='Choose your team', min_values=1, options=options)

        self.lobby = lobby
        self.cog = cog
        self.player = player
        self.teama = lobby.teamA
        self.teamb = lobby.teamB
        
class TeamSelect(discord.ui.Select):
    def __init__(self, lobby, cog, player):
        options = [
            discord.SelectOption(
                label=lobby.teamA['name'],
                value="teama",
                description=", ".join(p.name for p in lobby.teamA['players'])
            ),
            discord.SelectOption(
                label=lobby.teamB['name'],
                value="teamb",
                description=", ".join(p.name for p in lobby.teamB['players'])
            ),
            discord.SelectOption(
                label="Field",
                value="field",
                description=", ".join(v.name for v in lobby.field.values())
            ),
            discord.SelectOption(
                label="Spectator",
                value="spectator",
                description=", ".join(p.name for p in lobby.spectators)
            ),
        ]
        super().__init__(placeholder='Choose your team', min_values=1, options=options)

        self.lobby = lobby
        self.cog = cog
        self.player = player  # This is a Player instance.
    
    async def callback(self, itx: discord.Interaction):
        selected_value = self.values[0]
        author = itx.user
        channel = itx.channel

        # Verify player is actually in the lobby.
        if self.player.user_id not in self.lobby.players:
            await itx.response.send_message("You are not in this lobby", ephemeral=True)
            return

        # Now add the player to the chosen group.
        if selected_value == "teama":
            self.lobby.add_teamA(self.player)
            teamA_name = self.lobby.teamA['name'] or "Team A"
            if any(self.player.user_id == p.user_id for p in self.lobby.teamB['players']):
                self.lobby.remove_teamB(self.player)
            if any(hasattr(p, 'user_id') and self.player.user_id == p.user_id for p in self.lobby.field.values()):
                self.lobby.remove_field(self.player)
            if self.player.user_id in self.lobby.spectators:
                self.lobby.remove_spectator(self.player)
            await channel.send(f"{self.player.name} has joined {teamA_name}")
      
        elif selected_value == "teamb":
            self.lobby.add_teamB(self.player)
            teamB_name = self.lobby.teamB['name'] or "Team B"
            if any(self.player.user_id == p.user_id for p in self.lobby.teamA['players']):
                self.lobby.remove_teamA(self.player)
            if any(hasattr(p, 'user_id') and self.player.user_id == p.user_id for p in self.lobby.field.values()):
                self.lobby.remove_field(self.player)
            if any(hasattr(p, 'user_id') and self.player.user_id == p.user_id for p in self.lobby.spectators):
                self.lobby.remove_spectator(self.player)
            await channel.send(f"{self.player.name} has joined {teamB_name}")

        elif selected_value == "field":
            self.lobby.add_field(self.player)
            if self.player in self.lobby.teamA['players']:
                self.lobby.remove_teamA(self.player)
            if self.player in self.lobby.teamB['players']:
                self.lobby.remove_teamB(self.player)
            if self.player.user_id in self.lobby.spectators:
                self.lobby.remove_spectator(self.player)
            await channel.send(f"{self.player.name} has joined the field")

        elif selected_value == "spectator":
            if self.player in self.lobby.teamA['players']:
                self.lobby.remove_teamA(self.player)
            if self.player in self.lobby.teamB['players']:
                self.lobby.remove_teamB(self.player)
            if self.player in self.lobby.field.values():
                del self.lobby.field[self.player.name]

            self.lobby.add_spectator(self.player)
            await channel.send(f"{self.player.name} has joined as a spectator")
        else:
            await channel.send("Invalid selection")
            return
        
        # Update the lobby embed after selection and edit the message.
        embed = team_option_embed(self.lobby, self.cog.bot, self.player)
        embed.set_author(name="Lobby", icon_url=author.avatar.url if author else None)
        await itx.response.edit_message(embed=embed, view=self.view)


class TeamSelectView(discord.ui.View):
    def __init__(self, lobby, cog, player):
        super().__init__() 
        self.add_item(TeamSelect(lobby, cog, player))
#endregion


#region LobbyView
class LobbyView(discord.ui.View):
    def __init__(self, lobby, bot, lobbies):
        super().__init__()
        self.lobby = lobby
        self.lobbies = lobbies
        self.bot = bot
        

    @discord.ui.button(label="Join Team", style=discord.ButtonStyle.green)
    async def join_team(self, itx: discord.Interaction, btn: discord.ui.Button):
        lobby = self.lobby
        if lobby:
            if itx.user.id in lobby.players:
                player_dict = read_player(itx.user.id, itx.guild.id)
                tech = player_dict['techniques'][0] if player_dict['techniques'] else None
                player_dict['technique'] = tech['name'] if tech else None
                del player_dict['techniques'] 
                del player_dict['id']
                player = Player(**player_dict)
                view = TeamSelectView(lobby, Lobby_Cog(self.bot), player)
                embed = team_option_embed(lobby, self.bot, player)
                await itx.response.send_message(embed=embed, view=view, ephemeral=True)
                return
            else:
                await itx.response.send_message("You are not in a lobby", ephemeral=True)
        else:
            await itx.response.send_message("Lobby doesn't exist", ephemeral=True)


    @discord.ui.button(label="Ready Up", style=discord.ButtonStyle.green)
    async def ready_up(self, itx: discord.Interaction, btn: discord.ui.Button): 
        lobby = self.lobby
        if lobby:
            user_id = itx.user.id
            if user_id in lobby.players:
                if user_id in lobby.ready:
                    lobby.ready.remove(user_id)
                    embed = generate_lobby_embed(lobby, self.bot)
                    await itx.response.send_message(f"{itx.user.mention} is no longer ready.")
                else:
                    lobby.ready.append(user_id)
                    embed = generate_lobby_embed(lobby, self.bot)
                    await itx.response.send_message(f"{itx.user.mention} is now ready.")
            else:
                await itx.response.send_message("You are not in a lobby", ephemeral=True)
        else:
            await itx.response.send_message("You are not in a lobby", ephemeral=True)


    @discord.ui.button(label="Start Round", style=discord.ButtonStyle.green)
    async def start_round(self, itx: discord.Interaction, btn: discord.ui.Button):
        lobby = self.lobby
        thread = itx.channel
        lobby.status = 1
        lobby.ready = []
        if itx.channel.id == thread.id:
            if itx.user.id == lobby.owner:
                if lobby.status == 1:
                    lobby.round = 0
                    embed, lobby = start_round_embed(lobby, self.bot)
                    battle_cog = self.bot.get_cog("Battle")
                    if battle_cog is None:
                        await itx.response.send_message("Battle cog not found.")
                        return
                    view = battle_cog.BattleView(lobby, self.bot)
                    lobby.feed = [{
                          'attacks' : {lobby.teamA['name'] : {}, lobby.teamB['name'] : {}, 'Field' : {}}, 
                          'defenses':{lobby.teamA['name'] : {}, lobby.teamB['name'] : {}, 'Field' : {}}, 
                          'barriers' : {lobby.teamA['name'] : {}, lobby.teamB['name'] : {}, 'Field' : {}}
                          }]
                    await itx.response.send_message(embed=embed, view=view)
                    return
                else:
                    await itx.response.send_message("`Lobby is already in battle`", ephemeral=True)
                    return
            else:
                await itx.response.send_message("You are not the owner of this lobby", ephemeral=True)
                return
        
        else:
            await itx.response.send_message("You are not in a lobby", ephemeral=True)
            return
    

    @discord.ui.button(label="Change Name", style=discord.ButtonStyle.blurple)
    async def change_name(self, itx: discord.Interaction, btn: discord.ui.Button):   
        lobby = self.lobby
        user = itx.user.id
        await itx.response.send_modal(NameModal(lobby, user, self.bot))
        

    #kick player



    #leave lobby



    #disband lobby
    @discord.ui.button(label="Disband Lobby", style=discord.ButtonStyle.red)
    async def disband(self, itx: discord.Interaction, btn: discord.ui.Button):
        lobby = self.lobby
        thread = itx.channel
        if itx.user.id == lobby.owner:
            del(lobby)
            del(self.lobbies[itx.channel.id])
            await itx.response.send_message("`Lobby Disbanded`")
            await thread.send("`Channel Archived` at " + "`"  + datetime.now().astimezone().strftime('%c') + "`")
            await thread.edit(locked=True)
            await thread.edit(archived=True)
            return
    
        else:
            await itx.response.send_message("You are not the owner")
    


    # #invite player - can't pass discord.Member through the button interaction
    # @discord.ui.button(label="Invite Players")
    # async def invite_players(self, itx: discord.Interaction, btn: discord.ui.Button):
    #     lobby = self.lobby
    #     thread = itx.channel
    #     # Check if the command is used in a thread context
    #     if not isinstance(itx.channel, discord.Thread):
    #         await itx.send("This command can only be used in a thread.", ephemeral=True)
    #         return
    #     # Check if the thread is a private thread
    #     thread_type = self.thread_check(itx)
    #     if thread_type != "private":
    #         await itx.response.send_message("This command can only be used in private threads.", ephemeral=True)
    #         return
    #     # Check if the current channel is a private thread and if it exists in the lobbies
    #     if itx.channel.id in thread.id:
    #         # Ensure the lobby is private
    #         if not lobby.private:
    #             await itx.response.send_message("This command can only be used in private lobbies.", ephemeral=True)
    #             return
    #         # Check if the user issuing the command is the lobby owner
    #         if itx.user.id != lobby.owner:
    #             await itx.response.send_message("Only the lobby owner can invite players.", ephemeral=True)
    #             return
    #         # Check if the member is already in the lobby
    #         if member.id in lobby.invited:
    #             await itx.response.send_message(f"{member.mention} is already in invited.", ephemeral=True)
    #             return
    #         # Add the member to the invited list and the thread
    #         lobby.invited.append(member.id)
    #         lobby.add_player(member.id)
    #         await thread.add_user(member)
    #         await itx.response.send_message(f"{member.mention} has been invited to the lobby.")
    #         # Update the embed
    #         embed = generate_lobby_embed(lobby, self.bot)
    #         await itx.response.send_message(embed=embed)
    #         return
    #     else:
    #         await itx.response.send_message("This channel is not associated with a lobby.", ephemeral=True)
    #         return
    
#endregion


#region Modal
class NameModal(discord.ui.Modal):
    def __init__(self, lobby, user, bot):
        super().__init__(title="Change Name")
        self.lobby = lobby
        self.user = user
        self.bot = bot
        self.name = discord.ui.TextInput(label="Name", style=discord.TextStyle.short, placeholder="Enter New Name")
        self.add_item(self.name)

    async def on_submit(self, itx: discord.Interaction):
        name = self.name.value
        embed = discord.Embed(title='Change Team Name', description='')
        await itx.response.defer()

        user = self.user
        lobby = self.lobby

        if user == lobby.owner:
            embed.title = "Change Name"
            embed.description = "Choose to change your team name or your lobby's name to: " + name
            await itx.followup.send(embed=embed, view=OwnerLobbyView(lobby, self.bot, name))
            return
        teama = lobby.teamA['name'] if lobby.teamA['name'] else "Team A"
        teamb = lobby.teamB['name'] if lobby.teamB['name'] else "Team B"
        leader_a = lobby.teamA['leader'] if lobby.teamA['leader'] else None
        leader_b = lobby.teamB['leader'] if lobby.teamB['leader'] else None
        if leader_a:
            if user == leader_a.user_id:
                if name == teamb:
                    embed.description = ("Cannot set " + name + "to " + teamb)
                    await itx.followup.send(embed=embed, ephemeral=True)
                    return
                if lobby.set_teamA_name(name):
                    embed.description = ("Change team name to: " + name)
                    await itx.followup.send(embed=embed, ephemeral=True)
                    return
                else: 
                    embed.description = ("Error setting name to: " + name)
                    await itx.followup.send(embed=embed, ephemeral=True)
                    return
            
        elif leader_b:
            if user == leader_b.user_id:
                if name == teama:
                    embed.description = ("Cannot set " + name + "to " + teama)
                    await itx.followup.send(embed=embed, ephemeral=True)
                    return
                if lobby.set_teamB_name(name):
                    embed.description = ("Change team name to:" + name)
                    await itx.followup.send(embed=embed, ephemeral=True)
                    return
                else: 
                    embed.description = ("Error setting name to:" + name)
                    await itx.followup.send(embed=embed, ephemeral=True)
                    return

        else:
            embed.description = ("You are not in a team")
            await itx.followup.send(embed=embed, ephemeral=True)
            return


async def setup(bot):
    await bot.add_cog(Lobby_Cog(bot))