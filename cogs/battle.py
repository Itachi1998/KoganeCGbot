import discord, pagination, game, db, random, battle_checks
from battle_checks import battle_checks
from game import Player, Enemy
from player_tech import technique_list
from enemy_techs import enemy_tech
from db import read_player, read_colony, update_player,  update_colony, update_enemy, update_technique, read_technique, read_enemy
from discord.ext import commands
from discord import Subscription, app_commands

def healthbar(health, max_health):
    max_dashes = 4
    dash_ratio = max_health / max_dashes
    filled_dashes = 0 if health <= 0 else int(health / dash_ratio)
    remainder = (health / dash_ratio) - filled_dashes if health > 0 else 0
    dashes = "<:1000001328:1354469784724570172>" * filled_dashes
    if remainder > 0:
        dashes += "<:1000001329:1354469791724736745>"  # Add a half-heart emoji
    percent = f"`{round((health / max_health) * 100)}%`"
    if '-' in percent:
        percent = "`0%`"
    bar = f"{dashes} {percent}"
    return bar

def ce_bar(ce, max_ce):
    
    max_dashes = 4 # max 4
    dash_ratio = max_ce / max_dashes # maximum ce / 4 = 1000 ce = 250 ce per dash
    filled_dashes = 0 if ce <= 0 else int(ce / dash_ratio) # 853 / 250 = 3 dashes 
    remainder = max_dashes - filled_dashes if ce > 0 else 0 # 1000 / 250 = 4 dashes - 3 = 1 remainder 
    dashes = "<:1000001330:1354469798230102258>" * filled_dashes # emoji times number of dashes
    percent = f"`{0 if ce <= 0 else round((ce / max_ce) * 100)}%`" # 853 / 1000 = 0.853 * 100 = 85.3% rounded to 85%
    if remainder > 0: # if remainder is greater than 0, add a half dash
        dashes += "<:IMG_44021:1394503076223783043>" # Add a half-ce emoji
    bar = f"{dashes} {percent}" # return the bar with dashes and percent
    print(dashes)
    return bar

def verify_player(user_id, colony):
    player_dict = read_player(user_id, colony)
    if player_dict:
        tech = player_dict['techniques'][0]
        player_id = player_dict['id']
        del player_dict['techniques']
        del player_dict['id']
        player_dict['technique'] = tech['name'] if isinstance(tech, dict) else tech.name
        player = Player(**player_dict)
        if player:
          return player, player_id
        else:
            return False
    else:
        return False 
    
def verify_move(technique, name):
    try:
        barrier = technique[name][2]['Barrier']
        print(barrier)
    except IndexError:
         return False
    else:
         return True

def generate_round_embed(lobby):
    embed = discord.Embed(title="Round " + str(lobby.round), description="Round " + str(lobby.round) + " has started!")
    embed.add_field(name=lobby.teamA['name'], value="\n".join(p.name for p in lobby.teamA['players']))
    embed.add_field(name=lobby.teamB['name'], value="\n".join(p.name for p in lobby.teamB['players']))
    embed.add_field(name="Field", value="\n".join(p.name for p in lobby.field.values()))
    embed.set_author(name=lobby.name)
    return embed

def check_ready_players(lobby):
    players = []
    ready_players = 0
    for p in lobby.teamA['players']:
            players.append(p)
    for p in lobby.teamB['players']:
            players.append(p)
    for p in lobby.field.values():
        if hasattr(p, 'user_id'):
            players.append(p)
    
    for p in lobby.ready:
        ready_players += 1
    if len(players) == ready_players:
        return True
    else:
        return False
      

def get_player_team(player, lobby):
    if player.user_id in [p.user_id for p in lobby.teamA['players']]:
        return lobby.teamA
    elif player.user_id in [p.user_id for p in lobby.teamB['players']]:
        return lobby.teamB
    elif player.name in [p.name for p in lobby.field.values()]:
        return lobby.field
    else:
        return False

def get_player_feed(player, team, lobby, type):
    if "players" in team.keys():

        if player.user_id in [p.user_id for p in team['players']]:
                
                return lobby.feed[lobby.round][type][team['name']]
        
    elif player.name in [p.name for p in lobby.field.values()]:
        return lobby.feed[lobby.round][type]['Field']
    
    else:
        return False
    
def get_valid_targets(feed, team, player, lobby):
        chosen_enemies = feed[player.user_id]['targets'] if player.user_id in feed else []
        targets = []
        teamA = lobby.teamA
        teamB = lobby.teamB

        if 'name' in team.keys():
                
                if team['name'] == teamA['name']:
                        for p in teamB['players']:
                            if not chosen_enemies or p.name not in [p.name for p in chosen_enemies]:
                                    targets.append(p)

                elif team['name'] == teamB['name']:
                        for p in teamA['players']:
                            if not chosen_enemies or p.name not in [p.name for p in chosen_enemies]:
                                    targets.append(p)

                for p in lobby.field.values():
                    print("Checking target: " + str(p))
                    if hasattr(p, 'user_id') and p.user_id == player.user_id:
                        continue
                    elif not chosen_enemies or p.name not in [p.name for p in chosen_enemies]:
                        targets.append(p)
                return targets
        
        else:
            for p in lobby.field.values():
                    print("Checking target: " + str(p))
                    if hasattr(p, 'user_id') and p.user_id == player.user_id:
                        continue
                    elif not chosen_enemies or p.name not in [p.name for p in chosen_enemies]:
                        targets.append(p)

                    for tar in teamA['players'] :
                        if tar.user_id == player.user_id:
                            continue

                        elif not chosen_enemies or tar.name not in [p.name for p in chosen_enemies]:
                                targets.append(tar)

                    for tar in teamB['players']:
                        if tar.user_id == player.user_id:
                                continue
                        elif not chosen_enemies or tar.name not in [p.name for p in chosen_enemies]:
                            targets.append(tar)

                    return targets


def target_embed(player, lobby, type):
    embed = discord.Embed(title="Choose your target", description="Select a target")
    team = get_player_team(player, lobby)
    feed = get_player_feed(player, team, lobby, type)
    targets = []
    if feed:
        targets = get_valid_targets(feed, team, player, lobby)
    else:
        targets = [p for p in lobby.field.values()]
        if isinstance(team, dict):
            for t in lobby.teamA['players']:
                targets.append(t)
            for t in lobby.teamB['players']:
                targets.append(t)
        elif team.name == lobby.teamA['name']:
            targets.extend([p for p in lobby.teamB['players']] + [v for v in lobby.field.values()])
        elif team.name == lobby.teamB['name']:
            targets.extend(p for p in lobby.teamA['players'] + [v for v in lobby.field.values()])
    
    for t in targets:
        if hasattr(t, 'user_id') and t.user_id == player.user_id:
            targets.remove(t)
    
    if len(targets) == 0:
        return False
    else:
        value_string = ""
        for i, t in enumerate(targets):
            if hasattr(t, 'user_id'):
                health = t.hp
                max_health = t.max_hp
                ce = t.ce
                max_ce = t.max_ce
                name = t.name
            else:
                health = t.hp
                max_health = t.max_hp
                ce = t.ce
                max_ce = t.max_ce
                name = t.name

            value_string += f"`{i+1}: {name}`\n" + healthbar(health, max_health) + "\n" + ce_bar(ce, max_ce) + "\n"
            embed.add_field(name=name, value=value_string)
            return embed, targets
        
#region move embed

def move_embed(player, move):

    print("Showing options for " + move.name)
    name = move.name
    strength = move.strength
    speed = move.speed
    required_ce = move.act_cost
    aoe = move.aoe
    move_type = move.type
    required_bodyparts = move.act_body
    activation_speed = move.act_speed
    soul = move.soul if move.soul else None
    embed = discord.Embed(title=name, description="## " + name + " selected")
    embed.add_field(
        name="Required stats",
        value="- **Required CE:** " + str(required_ce) + "\n" + "- **Required Bodyparts:** " + ", ".join(part for part in required_bodyparts))
    embed.add_field(
        name="Move stats",
        value="- **Strength:** " + str(strength) + "\n" "- **Speed:** " + str(speed) + "\n" + "- **Targets:** " + str(aoe) + "\n" + 
        "- **Type:** " + move_type + "\n" + "- **Activation Speed:** " + str(activation_speed)
    )
    embed.set_author(name=player.name)
    if soul:
        embed.add_field(name="Soul strength",
        value="- **Strength:** " + str(move.soul))
    return embed

#endregion
def get_npc_random_defense(target):
    defenses = []
    if target.technique not in enemy_tech:
        for tech in technique_list:
            if target.technique in tech:
               if next(iter(tech.keys())) == target.technique:
                    defenses = list(tech[target.technique][1]['Defend'].keys())
                    defense_str = random.choice(defenses)
                    defense = tech[target.technique][1]['Defend'][defense_str]
                    break
    else:
        for defend in enemy_tech[target.technique][1]['Defend'].keys():
            defenses.append(defend)
        defense_str = random.choice(defenses)
        defense = enemy_tech[target.technique][1]['Defend'][defense_str]
    return defense_str, defense

def format_battle_result(attacker, target, attack_move, defense_move, results):
    # Format the battle result for display.
    result_str = "`" + attacker.name + ":` " + attack_move.name + "\n"
    result_str += "`" + target.name + ":` " + defense_move.name + "\n"
    # results structure : ("name", damage, killed, soul_damage)
    result = results[0]
    killed = results[2]
    damage = results[1]
    if result == 'hit':
        result_str += "`" + attacker.name +  "` hit `" + target.name + "`\n" + "Damage taken: " + str(damage) + "\n"
        if killed:
            result_str += "`" + target.name + "` has been defeated!\n"

    elif result == 'dodge':
        result_str += "`" + target.name + "` dodged the attack!\n"
        result_str += "Attack speed: " + str(attack_move.speed) + "\n"
        result_str += "Defense speed: " + str(defense_move.speed) + "\n"
        if damage > 0:
            if killed:
                 
                 result_str += "`" + target.name + "`" + " attempted to dodge, but took too much damage and was defeated!\n" + "Damage taken: " + str(damage) + "\n"

            result_str += "`" + target.name + "`" + " was able to dodge but still took  damage!\n" + "Damage taken: " + str(damage) + "\n"

    elif result == 'tank':
        result_str += "`" + target.name + "` tanked the attack!\n"
        result_str += "Damage tanked: " + str(damage) + "\n"

        
    elif result == 'counter':
        result_str += "`" + target.name + "`" + " countered the attack!\n"
        result_str += "Counter damage: " + str(damage) + "\n"
        result_str += "`" + target.name + "`" + " hits " + "`" + attacker.name + "` \n" + "Damage taken: " + str(damage) + "\n"

    return result_str

def set_player_defense(player, feed):
    defense = None
    default = None
    for tech in technique_list:
        if player.technique in tech:
            if next(iter(tech.keys())) == player.technique:
                default_defense_name = next(iter(tech[player.technique][1]['Defend'].keys()))
                default = tech[player.technique][1]['Defend'][default_defense_name]
                break

    for team_name, team_actions in feed['defenses'].items():
        if player.user_id in team_actions.keys():
            defense = team_actions[player.user_id]['move']

    if defense:
        player.defense = defense.name

        return defense.name, defense
    else:
        player.defense = default.name if default else "None"
        return default.name, default
         

#region sim embed
def simulation_embed(lobby, round_num):
    print(f"TeamA players: {[(p.user_id, p.name) for p in lobby.teamA['players']]}")
    print(f"TeamB players: {[(p.user_id, p.name) for p in lobby.teamB['players']]}")
    print(f"Field players: {[(p.user_id, p.name) for p in lobby.field.values() if hasattr(p, 'user_id')]}")
    """Generate simulation embed for all actions in the current round."""
    embed = discord.Embed(title=f"Round {round_num} Simulation", description="Battle Results") # initialize embed
    round_feed = lobby.feed[round_num] # get the feed for the current round
    
    # Get references to the feed sections
    # round feed dictionary structure:
    # { "round" : { "attacks" : {"team_a" : { "player_id" : {"move" : {}, "targets" : []}}, "team_b" : {}, "field" : {}}, "barriers" : {}, "defenses" : {}}}
    attacks = round_feed.get('attacks', {}) # get the value from round_feed or default it to empty
    barriers = round_feed.get('barriers', {}) 
    defenses = round_feed.get('defenses', {})
    if defenses:
        print("Defenses found in round feed.")
    # Track all simulations for this round
    simulations = []
    results = None
    # Process all attacks
    for team_name, team_actions in attacks.items():
        print(f"Feed team '{team_name}' has player IDs: {list(team_actions.keys())}")
        for player_id, action_data in team_actions.items():
            # Find the player object
            player = None
            # get current player
            if team_name == lobby.teamA['name']:
                for p in lobby.teamA['players']:
                    if p.user_id == player_id:
                        player = p
                        break
            elif team_name == lobby.teamB['name']:
                for p in lobby.teamB['players']:
                    if p.user_id == player_id:
                        player = p
                        break
            elif team_name == 'Field':
                for p in lobby.field.values():
                    if hasattr(p, 'user_id') and p.user_id == player_id:
                        player = p
                        break   

            if player:
                move = action_data.get('move')
                print(move)
                targets = action_data.get('targets', [])
                print(targets)
                for target in targets:
                    if hasattr(target, 'user_id'):
                        defense_name, defense_move = set_player_defense(target, round_feed)
                        results = battle_checks(player, target, move.name, defense_name)
                        print("Defense: " + str(defense_move))
                        print("Results: " + str(results))
                    else:
                        # NPC target - get random defense
                        defense_name, defense_move = get_npc_random_defense(target)
                        results = battle_checks(player, target, move.name, defense_name)
                    
                    # Format and store the result
                    result_str = format_battle_result(player, target, move, defense_move, results)
                    simulations.append(result_str)

    for team_name, team_actions in barriers.items():
        for player_id, action_data in team_actions.items():
            player = None
            results = None
            if team_name == lobby.teamA['name']:
                    for p in lobby.teamA['players']:
                        if p.user_id == player_id:
                            player = p
                            break
            elif team_name == lobby.teamB['name']:
                    for p in lobby.teamB['players']:
                        if p.user_id == player_id:
                            player = p
                            break
            elif team_name == 'Field':
                    for p in lobby.field.values():
                        if hasattr(p, 'user_id') and p.user_id == player_id:
                            player = p
                            break
        
            if player:
                    move = action_data.get('move')
                    targets = action_data.get('targets', [])

                    for target in targets:
                        if hasattr(target, 'user_id'):
                            defense_str, defense = set_player_defense(target, round_feed)
                            results = battle_checks(player, target, move.name, defense_str)

                        else:

                            defense_str, defense = get_npc_random_defense(target)
                            results = battle_checks(player, target, move.name, defense_str)
                            
                        result_str = format_battle_result(player, target, move, defense, results)

                        simulations.append(result_str)
                        action_data['results'] = results

    if simulations:
        embed.description = "\n".join(simulations)
    else:
        embed.description = "No actions taken this round."
    return embed



#region Battle Cog
class Battle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cog = bot.get_cog('Lobby_Cog')
        
    @commands.Cog.listener()
    async def on_ready(self):
        print("Battle cog is ready!")

    @commands.hybrid_command(name="vow", description="")
    async def vow(self, ctx):
        
        pass

    @commands.hybrid_command(name="summon")
    async def summon(self, ctx):
        player, id = verify_player(ctx.author.id, ctx.guild.id)
        lobby = self.cog.lobbies[ctx.channel.id]['Lobby']
        if player:
            if lobby and lobby.status > 1:           
                if player.user_id in lobby['players']:
                    embed = discord.Embed(title="Choose a  summon", description="")
                    await ctx.send(embed=embed)
                    return
                else:
                    await ctx.send("Not in a lobby.")
            pass
        await ctx.send("Command under construction")
        return
#endregion

#region BattleView
class BattleView(discord.ui.View):
    def __init__(self, lobby, bot):
        super().__init__()
        self.lobby = lobby
        self.bot = bot
        self.timeout = 30
        
    @discord.ui.button(label="Attack Options", style=discord.ButtonStyle.green)
    async def attack_options(self, itx:discord.Interaction, btn:discord.ui.Button):
        lobby = self.lobby
        if lobby:
                teama = lobby.teamA
                teamb = lobby.teamB
                field = lobby.field
                
                player, id = verify_player(itx.user.id, itx.guild.id)
                tech = read_technique(id)
                technique = None
                name = None
                if player:
                    for t in technique_list:
                        key = list(t.keys())[0]
                        if key == tech['name']:
                            technique = t
                            name = key
                            break
                if technique is None or name not in technique:
                    await itx.response.send_message(content="Technique not found.", ephemeral=True)
                    return
                if any(itx.user.id == p.user_id for p in teama['players']):
                    if player.user_id in lobby.feed[lobby.round]['attacks'][teama['name']]:
                                await itx.response.send_message("You have already selected an attack for this round.", ephemeral=True)
                                return
                if any(itx.user.id == p.user_id for p in teamb['players']):
                    if player.user_id in lobby.feed[lobby.round]['attacks'][teamb['name']]:
                                await itx.response.send_message("You have already selected an attack for this round.", ephemeral=True)
                                return
                if any(hasattr(thing, 'user_id') and itx.user.id == thing.user_id for thing in field):
                    if player.user_id in lobby.feed[lobby.round]['attacks']['Field']:
                                await itx.response.send_message("You have already selected an attack for this round.", ephemeral=True)
                                return
                        
                embed = discord.Embed(title="Attack", description="Choose from your offense")
                value_string = ""
                for key in technique[name][0]['Attack'].keys():
                    attack = technique[name][0]['Attack'][key]
                    fields = [
                        f"`Atk dmg:` **{attack.strength}**",
                        f"`Atk spd:` **{attack.speed}**",
                        f"`Bodyparts:` **{', '.join(attack.act_body)}**",
                        f"`Max targets:` **{attack.aoe}**",
                        f"`Type:` **{attack.type}**"
                    ]
                    if attack.soul:
                        fields.append(f"`Soul dmg:` **{attack.soul}**")
                    # Optionally include other properties if needed and if length allows
                    value_string = "\n".join(fields) + "\n"

                    embed.add_field(name=attack.name, value=value_string)
                
                embed.set_thumbnail(url=self.bot.user.avatar.url)
                select_view = MoveView(player, self.bot, technique, self.lobby, attack=True)
                # t_embed, targets = target_embed(player, lobby)
                # # await itx.channel.send(embed=t_embed)
                # # view = TargetSelectView(player, targets, lobby)
                # await itx.response.send_message(embed=embed, view=view, ephemeral=True)
                await itx.response.send_message(embed=embed, view=select_view, ephemeral=True)
                return
        else:
            await itx.response.send_message("Error not in lobby")
            return

    @discord.ui.button(label="Defend Options", style=discord.ButtonStyle.blurple)
    async def defend_options(self, itx:discord.Interaction, btn:discord.ui.Button):
        lobby = self.lobby
        if lobby:
            player, id = verify_player(itx.user.id, itx.guild.id)
            tech = read_technique(id)
            technique = None
            name = None
            if player:
                for t in technique_list:
                    key = list(t.keys())[0]
                    if key == tech['name']:
                        technique = t
                        name = key
                        break
            if technique is None or name not in technique:
                await itx.response.send_message("Technique not found.", ephemeral=True)
                return
            
            
            embed = discord.Embed(title="Defend", description="Choose from your defense")
            value_string = ""
            for key in technique[name][1]['Defend'].keys():
                defense = technique[name][1]['Defend'][key]
                fields = [
                    f"`Def dmg:` **{defense.strength}**",
                    f"`Def spd:` **{defense.speed}**",
                    f"`Bodyparts:` **{', '.join(defense.act_body)}**",
                    f"`Max targets:` **{defense.aoe}**",
                    f"`Type:` **{defense.type}**"
                ]

                if defense.soul:
                    fields.append(f"`Soul defense` **{defense.soul}**")

                # Optionally include other properties if needed and if length allows
                value_string = "\n".join(fields) + "\n"

                embed.add_field(name=defense.name, value=value_string)

            embed.set_thumbnail(url=self.bot.user.avatar.url)
            view = MoveView(player, self.bot, technique, self.lobby, defense=True)
            await itx.response.send_message(embed=embed, view=view, ephemeral=True)
            return
        
        else:
            await itx.response.send_message("Error not in a lobby")
            return
        
    @discord.ui.button(label="Item Options", disabled=True, style=discord.ButtonStyle.red)
    async def item_options(self, itx:discord.Interaction, btn:discord.ui.Button):
        pass

    @discord.ui.button(label="Barrier Options", style=discord.ButtonStyle.gray) #BROKEN
    async def summon_options(self, itx:discord.Interaction, btn:discord.ui.Button):
        lobby = self.lobby
        if lobby:
            player, id = verify_player(itx.user.id, itx.guild.id)
            tech = read_technique(id)
            teama = lobby.teamA
            teamb = lobby.teamB
            field = lobby.field
            technique = None
            name = None
            if player:
                for t in technique_list:
                    key = list(t.keys())[0]
                    if key == tech['name']:
                        technique = t
                        name = key
                        break
            if technique is None or name not in technique:
                await itx.response.send_message("Technique not found.", ephemeral=True)
                return
            
            if any(itx.user.id == p.user_id for p in teama['players']):
                    if player.user_id in lobby.feed[lobby.round]['attacks'][teama['name']]:
                                print("Player " + str(player.user_id) + " already selected an attack")
                                await itx.response.send_message("You have already selected a defense for this round.", ephemeral=True)
                                return
            if any(itx.user.id == p.user_id for p in teamb['players']):
                    if player.user_id in lobby.feed[lobby.round]['attacks'][teamb['name']]:
                                print("Player " + str(player.user_id) + " already selected an attack")
                                await itx.response.send_message("You have already selected a defense for this round.", ephemeral=True)
                                return
            if any(hasattr(thing, 'user_id') and itx.user.id == thing.user_id for thing in field):
                    if player.user_id in lobby.feed[lobby.round]['defenses']['Field']:
                                print("Player " + str(player.user_id) + " already selected an attack")
                                await itx.response.send_message("You have already selected a defense for this round.", ephemeral=True)
                                return

            if verify_move(technique, name):
                embed = discord.Embed(title="Barrier", description="Choose from your barrier")
                value_string = ""
                for key in technique[name][2]['Barrier'].keys():
                    barrier = technique[name][2]['Barrier'][key]
                    fields = [
                        f"`Barrier dmg:` **{barrier.strength}**",
                        f"`Barrier spd:` **{barrier.speed}**",
                        f"`Bodyparts:` **{', '.join(barrier.act_body)}**",
                        f"`Max targets:` **{barrier.aoe}**",
                        f"`Type:` **{barrier.type}**"
                    ]

                    if barrier.soul:
                        fields.append(f"`Soul barrier` **{barrier.soul}**")

                    # Optionally include other properties if needed and if length allows
                    value_string = "\n".join(fields) + "\n"

                    embed.add_field(name=barrier.name, value=value_string)

                embed.set_thumbnail(url=self.bot.user.avatar.url)
                view = MoveView(player, self.bot, technique, self.lobby, barrier=True)
                await itx.response.send_message(embed=embed, view=view, ephemeral=True)
                return
            
            else:
                 await itx.response.send_message("You do not have a barrier move in your technique")
                 return
        
        else:
            await itx.response.send_message("Error not in a lobby")
            return

    @discord.ui.button(label="Surrender", disabled=True, style=discord.ButtonStyle.red)
    async def surrender(self, itx:discord.Interaction, btn:discord.ui.Button):
        # Logic to surrender
        pass

    @discord.ui.button(label="Flee", disabled=True, style=discord.ButtonStyle.red)
    async def flee(self, itx:discord.Interaction, btn:discord.ui.Button):
        # Logic to flee
        pass

    @discord.ui.button(label="End Turn", disabled=True, style=discord.ButtonStyle.gray)
    async def end_turn(self, itx:discord.Interaction, btn:discord.ui.Button):
        # Logic to end the turn
        pass
# endregion
class MoveView(discord.ui.View):
    def __init__(self, player, bot, technique, lobby, attack=False, defense=False, barrier=False):
        super().__init__()
        if attack:
            self.add_item(MoveSelect(player, bot, technique, lobby, attack=True))
        if defense:
            self.add_item(MoveSelect(player, bot, technique, lobby, defense=True))
        if barrier:
            self.add_item(MoveSelect(player, bot, technique, lobby, barrier=True))
    
class MoveSelect(discord.ui.Select):
    def __init__(self, player, bot, technique, lobby, attack=False, defense=False, barrier=False):
        print(technique)
        moves = []
        self.bot = bot
        techname = next(iter(technique.keys()))
        if attack:
            moves = [technique[techname][0]['Attack'][move] for move in technique[techname][0]['Attack'].keys()]
        if defense:
            moves = [technique[techname][1]['Defend'][move] for move in technique[techname][1]['Defend'].keys()]
        if barrier:
            moves = [technique[techname][2]['Barrier'][move] for move in technique[techname][2]['Barrier'].keys()]  
       
        options = [discord.SelectOption(label=f"{i+1}: {m.name}", value=str(i)) for i, m in enumerate(moves)]
        super().__init__(placeholder='Choose your move', min_values=1, options=options)
        self.lobby = lobby
        self.player = player
        self.tech = technique
        self.attack = attack
        self.defense = defense
        self.barrier = barrier
        self.moves = moves
        self.field = lobby.field
        self.teama = lobby.teamA
        self.teamb = lobby.teamB

    async def callback(self, itx: discord.Interaction):
        if itx.user.id != self.player.user_id:
            await itx.response.send_message("You did not invoke this prompt", ephemeral=True)
        else:
            await itx.response.defer()
            if itx.user.id in self.lobby.ready:
                                await itx.followup.send("You have already selected an action for this round.", ephemeral=True)
                                return
            move = self.moves[int(self.values[0])]
            embed = move_embed(self.player, move)
            move_type = None
            if self.attack:
                move_type = 'attacks'
            elif self.defense:
                move_type = 'defenses'
            elif self.barrier:
                move_type = 'barriers'
            else:
                await itx.followup.send("Invalid move type.", ephemeral=True)
                return
            results = target_embed(self.player, self.lobby, move_type)
            t_embed = None
            targets = None
            if results:
                t_embed, targets = results
            else:
                t_embed = discord.Embed(title="No targets available", description="No targets available.")
                targets = False

            if targets == False:
                await itx.followup.send("No targets available.", ephemeral=True)
                return
            
            view = TargetSelectView(self.bot, self.player, targets, self.lobby, move, attack=self.attack, defense=self.defense, barrier=self.barrier)
            
            await itx.followup.send(embeds=[embed, t_embed], view=view, ephemeral=True)
            return
           
#region TargetSelect
class TargetSelectView(discord.ui.View):
    def __init__(self, bot, player, targets, lobby, move, attack=False, defense=False, barrier=False):
        super().__init__()
        self.add_item(TargetSelect(bot, player, targets, lobby, move, attack=attack, defense=defense, barrier=barrier))

class TargetSelect(discord.ui.Select):
    def __init__(self, bot, player, targets, lobby, move, attack=False, defense=False, barrier=False):
        options = [discord.SelectOption(label=f"{i+1}: {t.name}", value=str(i)) for i, t in enumerate(targets)]
        super().__init__(placeholder='Choose your target', min_values=1, options=options)
        self.lobby = lobby
        self.bot = bot
        self.player = player
        self.targets = targets
        self.move = move
        self.feed = lobby.feed
        self.field = lobby.field
        self.teama = lobby.teamA
        self.teamb = lobby.teamB
        self.attack = attack
        self.defense = defense
        self.barrier = barrier

    async def callback(self, itx: discord.Interaction):
        if itx.user.id != self.player.user_id:
            await itx.response.send_message("You did not invoke this prompt.", ephemeral=True)
        else:
            await itx.response.defer()
            round = self.lobby.round
            charges = getattr(self.move, 'charge', 0)
            attacks = self.lobby.feed[round]['attacks']
            defenses = self.lobby.feed[round]['defenses']
            barriers = self.lobby.feed[round]['barriers']
            channel = itx.channel
            # Determine which team the player is on
            team = None
            move_type = None
            if self.attack:
                move_type = 'attacks'
            elif self.defense:
                move_type = 'defenses'
            elif self.barrier:
                move_type = 'barriers'
            team_name = None
            if any(self.player.user_id == p.user_id for p in self.teama['players']):
                team = self.teama
                team_name = team['name']

            elif any(self.player.user_id == p.user_id for p in self.teamb['players']):
                team = self.teamb
                team_name = team['name']

            elif any(hasattr(thing, 'user_id') and self.player.user_id == thing.user_id for thing in self.field.values()):
                team = self.field
                team_name = 'Field'

            if not team:
                await itx.followup.send("Player is not on any team.", ephemeral=True)
                return
            
            if self.attack:
                if team_name not in attacks:
                    attacks[team_name] = {}
                team_feed = attacks[team_name]

            elif self.defense:
                if team_name not in defenses:
                    defenses[team_name] = {}
                team_feed = defenses[team_name]

            elif self.barrier:
                if team_name not in barriers:
                    barriers[team_name] = {}
                team_feed = barriers[team_name]
            else:
                await itx.followup.send("Invalid move type.", ephemeral=True)
                return
            
            # print("Team feed: " + str(team_feed) + " for team: " + team_name)
            selected_target = self.targets[int(self.values[0])]
            print("Selected target: " + selected_target.name)

            if self.player.user_id not in team_feed.keys():
                team_feed[self.player.user_id] = {
                    'move': self.move, # save technique to feed
                    'targets': [selected_target], # initialize targets
                    'charges': charges, # initialize charges
                    'results': None # initialize results
                }

            else:
                team_feed[self.player.user_id]['targets'].append(selected_target)

            print(f"Updated team feed for {self.player.user_id}: {team_feed[self.player.user_id]}")

            await itx.followup.send(self.player.name + " targets: " + selected_target.name + " with: " + self.move.name)
            
            selected_targets = len(team_feed[self.player.user_id]['targets'])

            if self.move.aoe > 1 and  selected_targets < self.move.aoe:
                results = target_embed(self.player, self.lobby, move_type)
                if results:
                    embed, targets = results
                    if self.defense:
                        msg_text = "defense targets"
                    elif self.attack:
                        msg_text = "attack targets"
                    elif self.barrier:
                        msg_text = "barrier targets"
                    view = TargetSelectView(self.bot, self.player, targets, self.lobby, self.move, attack=self.attack, defense=self.defense, barrier=self.barrier)
                    # Update the embed with the selected targets
                    aoe = self.move.aoe
                    await itx.followup.send(
                        content=f"Selected {selected_targets} out of {aoe} {msg_text}. You may choose more targets.",
                        embeds=[embed],
                        view=view,
                        ephemeral=True
                    )
                    return
                else:
                        await itx.followup.send("No more targets available.", ephemeral=True)
                        self.lobby.ready.append(self.player.user_id)
                        ready = check_ready_players(self.lobby)
                        if ready:
                            embed = simulation_embed(self.lobby, self.lobby.round)
                            await itx.followup.send(embed=embed, ephemeral=True)
                            self.lobby.round += 1
                            self.lobby.ready = []
                            self.lobby.feed.append({'round' : self.lobby.round,
                                'attacks': { self.lobby.teamA['name'] : {}, self.lobby.teamB['name'] : {}, 'Field': {}},
                                'defenses': { self.lobby.teamA['name'] : {}, self.lobby.teamB['name'] : {}, 'Field': {}},
                                'barriers': { self.lobby.teamA['name'] : {}, self.lobby.teamB['name'] : {}, 'Field': {}}
                            })
                            round_embed = generate_round_embed(self.lobby)
                            await channel.send(embed=round_embed, view=BattleView(self.lobby, self.bot))
                            return      
                        await itx.followup.send("Move selected for this round, wait for players to finish selecting moves.", ephemeral=True)
                        return
            else:
                self.lobby.ready.append(self.player.user_id)
                ready = check_ready_players(self.lobby)
                if ready:
                    embed = simulation_embed(self.lobby, self.lobby.round)
                    await itx.followup.send(embed=embed)
                    
                    self.lobby.round += 1
                    self.lobby.ready = []
                    self.lobby.feed.append({'round' : self.lobby.round,
                        'attacks': { self.lobby.teamA['name'] : {}, self.lobby.teamB['name'] : {}, 'Field': {}},
                        'defenses': { self.lobby.teamA['name'] : {}, self.lobby.teamB['name'] : {}, 'Field': {}},
                        'barriers': { self.lobby.teamA['name'] : {}, self.lobby.teamB['name'] : {}, 'Field': {}}
                    })
                    round_embed = generate_round_embed(self.lobby)
                    await channel.send(embed=round_embed, view=BattleView(self.lobby, self.bot))
                    return
                
                await itx.followup.send("You have selected your target. Wait for others to finish selecting", ephemeral=True)
                return
        
#endregion


async def setup(bot):
    battle_cog = Battle(bot)
    battle_cog.BattleView = BattleView
    await bot.add_cog(battle_cog)