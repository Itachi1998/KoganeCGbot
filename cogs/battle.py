import discord, pagination, game, db, random, battle_checks
from battle_checks import *
from game import Player, Enemy
from player_tech import technique_list
from enemy_techs import enemy_tech
from db import read_player, read_colony, update_player,  update_colony, update_enemy, update_technique, read_technique, read_enemy
from discord.ext import commands
from discord import Subscription, app_commands

def healthbar(health, max_health):
    max_dashes = 4
    dash_ratio = max_health / max_dashes
    filled_dashes = int(health / dash_ratio)
    dashes = "❤️" * filled_dashes
    if filled_dashes % 1 != 0:
        dashes += "💔"

    percent = f"`{round((health / max_health) * 100)}%`"
    if '-' in percent:
        percent = "`0%`"
    bar = f"{dashes}{percent}"
    return bar

def ce_bar(ce, max_ce):
    max_dashes = 4
    dash_ratio = max_ce / max_dashes
    filled_dashes = 0 if ce <= 0 else int(ce / dash_ratio)
    dashes = "" * filled_dashes
    if filled_dashes % 1 != 0:
        dashes += "<a:blueflames:1279971716382326804>"
    percent = f"`{0 if ce <= 0 else round((ce / max_ce) * 100)}%`"
    if '-' in percent:
        percent = "`0%`"
    bar = f"{dashes}{percent}"
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
    
#region target embed
def target_embed(player, lobby, move, defense=False, attack=False, barrier=False):
        print(f"Checking for {player} in {lobby.name}")
        print(lobby)
        embed = discord.Embed(title="Attack Targets", description="Choose a target.")
        targets = []
        # Get team lists (default to empty lists if missing)
        teamA = lobby.teamA.get('players', [])
        teamB = lobby.teamB.get('players', [])
        
        print(teamA)
        print(teamB)
        # For field, assume lobby.field is a dict; otherwise use it directly
        field = list(lobby.field.values()) if isinstance(lobby.field, dict) else lobby.field
        # If player is on Team A, then the enemy targets are Team B and the field.
        print(field)
        type_move = None
        if attack:
            type_move = 'attacks'
        elif defense:
            type_move = 'defenses'
        elif barrier:
            type_move = 'barriers'

        lobby_feed = lobby.feed[lobby.round][type_move]
        targets = []
        chosen = []
        if any(player.user_id == p.user_id for p in teamA):
            player_feed = lobby_feed[teamA.name].get(player.user_id, None)
            if player_feed:
                chosen = player_feed['targets']
            for t in teamB:
                if chosen:
                    if t.name not in [tar.name for tar in chosen]:
                        targets.append(t)
                    else:
                        continue
                else:
                    targets.append(t)
            for t in field:
                if chosen:
                    if t.name not in [tar.name for tar in chosen]:
                        targets.append(t)
                    else:
                        continue
                else:
                    targets.append(t)
        
        elif any(player.user_id == p.user_id for p in teamB):

            player_feed = lobby_feed[teamB.name].get(player.user_id, None)
            if player_feed:
                chosen = player_feed['targets']
            for t in teamA:
                if chosen:
                    if t.name not in [tar.name for tar in chosen]:
                        targets.append(t)
                    else:
                        continue
                else:
                    targets.append(t)
            for t in field:
                if chosen:
                    if t.name not in [tar.name for tar in chosen]:
                        targets.append(t)
                    else:
                        continue
                else:
                    targets.append(t)

        elif any(hasattr(thing, 'user_id') and player.user_id == thing.user_id for thing in field):
            field_feed = lobby_feed.get('Field', {})
            player_feed = field_feed.get(player.user_id, None)
            print("current player feed")
            print(player_feed)
            if player_feed:
               chosen = player_feed['targets']
    
            for t in teamA:
                if chosen:
                    if t.name not in [tar.name for tar in chosen]:
                        targets.append(t)
                    else:
                        continue
                else:
                    targets.append(t)

            for t in field:
                if hasattr(t, 'user_id') and t.user_id == player.user_id:
                    continue
                if chosen:
                    print("checking if target " + t.name + " is in targets")
                    print([tar.name for tar in chosen])
                    if t.name not in [tar.name for tar in chosen]:
                        targets.append(t)
                    else:
                        continue
                else:
                    targets.append(t)
            
            for t in teamB:
                if chosen:
                    if t.name not in [tar.name for tar in chosen]:
                        targets.append(t)
                else:
                    targets.append(t)
        else:
            return False
        if len(targets) == 0:
            return False
        else:        
            embed.add_field(name="Targets", value="\n".join(t.name for t in targets))
            return embed, targets
  


#endregion

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

#region sim embed
def simulation_embed(lobby, player, target, feed):
    user_id = player.user_id
    print(user_id)
    attacks = feed['attacks']
    defenses = feed['defenses']
    barriers = feed['barriers']
    teama = lobby.teamA
    teamb = lobby.teamB
    field = lobby.field
    attack_str = None
    defense_str = None
    print(f"Checking user_id: {user_id}")
    print(f"Team A players: {[p.user_id for p in teama['players']]}")
    print(f"Team B players: {[p.user_id for p in teamb['players']]}")
    print(f"Field players: " + ", ". join(field.keys()))
    print(f"Attacks: {attacks}")
    print(f"Barriers: {barriers}")
    p_feed = None
    if user_id in [p.user_id for p in teama['players']]:
        if user_id in attacks.get(teama.name, {}):
            attack_str = attacks[teama.name][user_id]['move'].name
        elif user_id in barriers.get(teama.name, {}):
            attack_str = barriers[teama.name][user_id]['move'].name
    elif user_id in [p.user_id for p in teamb['players']]:
        if user_id in attacks.get(teamb.name, {}):
            attack_str = attacks[teamb.name][user_id]['move'].name
        elif user_id in barriers.get(teamb.name, {}):
            attack_str = barriers[teamb.name][user_id]['move'].name
    elif player.name in field.keys():
        if user_id in attacks.get('Field', {}):
            attack = attacks['Field'][user_id]['move']
            p_feed = attacks['Field'][user_id]
            print(f"Attack move: {attack}")
            attack_str = attack.name
        elif user_id in barriers.get('Field', {}):
            barrier = barriers['Field'][user_id]['move']
            attack_str = barrier.name
    else:
        print("No matching condition found for user_id.")

    if hasattr(target, 'user_id'):
        if target.user_id in [p.user_id for p in teama['players']]:
            if target.user_id in defenses[teama.name]:
                defense_str = defenses[teama.name][target.user_id]['move'].name
            elif target.user_id in barriers[teama.name]:
                defense_str = barriers[teama.name][target.user_id]['move'].name
        if target.user_id in [p.user_id for p in teamb['players']]:
            if target.user_id in defenses[teamb.name]:
                defense_str = defenses[teamb.name][target.user_id]['move'].name
            elif target.user_id in barriers[teamb.name]:
                defense_str = barriers[teamb.name][target.user_id]['move'].name
        if target.user_id in [p.user_id for p in field]:
            if target.user_id in defenses['Field']:
                defense_str = defenses['Field'][target.user_id]['move'].name
            elif target.user_id in barriers['Field']:
                defense_str = barriers['Field'][target.user_id]['move'].name
    else:
        if target.tamed:
            if target.tamed in [p.user_id for p in teama['players']]:
                if target.tamed in defenses[teama.name]:
                    defense_str = defenses[teama.name][target.tamed].name
            if target.tamed in [p.user_id for p in teamb['players']]:
                if target.tamed in defenses[teamb.name]:
                    defense_str = defenses[teamb.name][target.tamed]['move'].name
            if target.tamed in [p.user_id for p in field]:
                if target.tamed in defenses['Field']:
                    defense_str = defenses['Field'][target.tamed]['move'].name
        else:
            target_tech = None
            npc_tech=None
            name = None
            for tech in enemy_tech:
                name = next(iter(tech))
                if name == target.technique:
                    npc_tech = tech
                    break

            if target_tech is None:
                for tech in technique_list:
                    name = next(iter(tech))
                    if name == target.technique:
                        target_tech = tech
                        break

            if target_tech:
                random_defense = [t for t in target_tech[name][1]['Defend'].keys()]
                defense_str = random.choice(random_defense)


            elif npc_tech:
                random_defense = [t for t in npc_tech[1]['Defend'].keys()]
                defense_choice = random.choice(random_defense)
                defense_str = defense_choice
    
    results = battle_checks(player, target, attack_str, defense_str)
    p_feed['results'] = results

    result_str = "`" + player.name + ":` " + player.technique + " technique activation: " + attack_str + "\n" + "`" + target.name + ":` " +  target.technique + " technique activation: " + defense_str
    if "dodge" in results:
        result_str += "\n" + target.name + " dodged " + player.name + "'s attack"
    elif "hit" in results:
        result_str += "\n" + player.name + " hit " + target.name + " with " + attack_str
    elif "tank" in results:
        result_str += "\n" + target.name + " tanked " + str(results[1]) + " dmg from " + attack_str + " using " + defense_str
    elif "counter" in results:
        result_str += "\n" + target.name + " countered " + player.name + "'s attack with " + defense_str
        if results[1] > 0:
            result_str += "\n" + target.name + " dealt " + str(results[1]) + " damage to " + player.name + " using " + defense_str
        else:
            result_str += "\n" + target.name + "'s counter dealt no damage to " + player.name


    embed = discord.Embed(title="Simulation", description=f"**{player.name}** vs **{target.name}**")
    print("Simulation results for " + player.name + " vs " + target.name)
    print(results)
    embed.add_field(name='Results', value=result_str)
    return embed
#endregion


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

class BattleView(discord.ui.View):
    def __init__(self, lobby, bot):
        super().__init__()
        self.lobby = lobby
        self.bot = bot
        self.timeout = 30
        
    @discord.ui.button(label="Attack Options", style=discord.ButtonStyle.green)
    async def attack_options(self, itx: discord.Interaction, btn: discord.ui.Button):
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
                    if player.user_id in lobby.feed[lobby.round]['attacks'][teama.name]:
                                await itx.response.send_message("You have already selected an attack for this round.", ephemeral=True)
                                return
                if any(itx.user.id == p.user_id for p in teamb['players']):
                    if player.user_id in lobby.feed[lobby.round]['attacks'][teamb.name]:
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
                select_view = MoveView(player, technique, self.lobby, attack=True)
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
    async def defend_options(self,  itx: discord.Interaction, btn:discord.ui.Button):
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
            view = MoveView(player, technique, self.lobby, defense=True)
            await itx.response.send_message(embed=embed, view=view, ephemeral=True)
            return
        
        else:
            await itx.response.send_message("Error not in a lobby")
            return
        
    @discord.ui.button(label="Item Options", style=discord.ButtonStyle.red)
    async def item_options(self, button: discord.ui.Button, interaction: discord.Interaction):
        pass

    @discord.ui.button(label="Barrier Options", style=discord.ButtonStyle.gray)
    async def summon_options(self, button: discord.ui.Button, itx: discord.Interaction):
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
                    if player.user_id in lobby.feed[lobby.round]['attacks'][teama.name]:
                                print("Player " + str(player.user_id) + " already selected an attack")
                                await itx.response.send_message("You have already selected a defense for this round.", ephemeral=True)
                                return
            if any(itx.user.id == p.user_id for p in teamb['players']):
                    if player.user_id in lobby.feed[lobby.round]['attacks'][teamb.name]:
                                print("Player " + str(player.user_id) + " already selected an attack")
                                await itx.response.send_message("You have already selected a defense for this round.", ephemeral=True)
                                return
            if any(hasattr(thing, 'user_id') and itx.user.id == thing.user_id for thing in field):
                    if player.user_id in lobby.feed[lobby.round]['defenses']['Field']:
                                print("Player " + str(player.user_id) + " already selected an attack")
                                await itx.response.send_message("You have already selected a defense for this round.", ephemeral=True)
                                return
                    
            embed = discord.Embed(title="Barrier", description="Choose from your barrier")
            value_string = ""
            for key in technique[name][3]['Barrier'].keys():
                barrier = technique[name][3]['Barrier'][key]
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
            view = MoveView(player, technique, self.lobby, barrier=True)
            await itx.response.send_message(embed=embed, view=view, ephemeral=True)
            return
        
        else:
            await itx.response.send_message("Error not in a lobby")
            return

    @discord.ui.button(label="Surrender", style=discord.ButtonStyle.red)
    async def surrender(self, button: discord.ui.Button, interaction: discord.Interaction):
        # Logic to surrender
        pass

    @discord.ui.button(label="Flee", style=discord.ButtonStyle.red)
    async def flee(self, button: discord.ui.Button, interaction: discord.Interaction):
        # Logic to flee
        pass

    @discord.ui.button(label="End Turn", style=discord.ButtonStyle.gray)
    async def end_turn(self, button: discord.ui.Button, interaction: discord.Interaction):
        # Logic to end the turn
        pass

class MoveView(discord.ui.View):
    def __init__(self, player, technique, lobby, attack=False, defense=False, barrier=False):
        super().__init__()
        if attack:
            self.add_item(MoveSelect(player, technique, lobby, attack=True))
        if defense:
            self.add_item(MoveSelect(player, technique, lobby, defense=True))
        if barrier:
            self.add_item(MoveSelect(player, technique, lobby, barrier=True))
    
class MoveSelect(discord.ui.Select):
    def __init__(self, player, technique, lobby, attack=False, defense=False, barrier=False):
        print(technique)
        moves = []
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
            print("Printing lobby feed")
            print(self.lobby.feed[self.lobby.round])
    
            if itx.user.id in self.lobby.ready:
                                await itx.followup.send("You have already selected an action for this round.", ephemeral=True)
                                return
            
            move = self.moves[int(self.values[0])]
            embed = move_embed(self.player, move)
            results = target_embed(self.player, self.lobby, move, defense=self.defense, attack=self.attack, barrier=self.barrier)
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
            
            view = TargetSelectView(self.player, targets, self.lobby, move, attack=self.attack, defense=self.defense, barrier=self.barrier)
            self.lobby.ready.append(itx.user.id)
            await itx.followup.send(embeds=[embed, t_embed], view=view, ephemeral=True)
            
            return
           

class TargetSelectView(discord.ui.View):
    def __init__(self, player, targets, lobby, move, attack=False, defense=False, barrier=False):
        super().__init__()
        self.add_item(TargetSelect(player, targets, lobby, move, attack=attack, defense=defense, barrier=barrier))

class TargetSelect(discord.ui.Select):
    def __init__(self, player, targets, lobby, move, attack=False, defense=False, barrier=False):
            options = [discord.SelectOption(label=f"{i+1}: {t.name}", value=str(i)) for i, t in enumerate(targets)]
            super().__init__(placeholder='Choose your target', min_values=1, options=options)
            self.lobby = lobby
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
           
            # Determine which team the player is on
            team = None

            if any(self.player.user_id == p.user_id for p in self.teama['players']):
                team = self.teama

            elif any(self.player.user_id == p.user_id for p in self.teamb['players']):
                team = self.teamb
            
            elif any(hasattr(thing, 'user_id') and self.player.user_id == thing.user_id for thing in self.field.values()):
                team = self.field

            if not team:
                await itx.followup.send("Player is not on any team.", ephemeral=True)
                return

            # Update the appropriate feed based on move type
            if self.attack:
                if isinstance(team, dict):
                    team = 'Field'
                    team_feed = attacks.get(team, {})

                else:
                    team_feed = attacks.get(team['name'], {})

            elif self.defense:
                if isinstance(team, dict):
                    team = 'Field'
                    team_feed = defenses.get(team, {})

                else:
                    team_feed = defenses.get(team['name'], {})

            elif self.barrier:
                if isinstance(team, dict):
                    team = 'Field'
                    team_feed = barriers.get(team, {})

                else:
                    team_feed = barriers.get(team['name'], {})

            else:
                await itx.followup.send("Invalid move type.", ephemeral=True)
                return
            
            print("Team feed \n" + str(team_feed))
            if self.player.user_id not in team_feed.keys():
                team_feed[self.player.user_id] = {
                    'move' : self.move,
                    'targets' : [self.targets[int(self.values[0])]],
                    'charges': charges, 'results' : None}
            else:
                # Save the move for the player and update targets
                team_feed[self.player.user_id]['move'] = self.move
                target_list = team_feed[self.player.user_id].get('targets', [])
                target_list.append(self.targets[int(self.values[0])])
                team_feed[self.player.user_id]['targets'] = target_list
                if charges > 0:
                    team_feed[self.player.user_id]['charges'] = charges - 1

            await itx.followup.send(self.player.name + " targets: " + self.targets[int(self.values[0])].name + " with: " + self.move.name)
            # Check if the move is a charge move
            # Check if more targets need to be selected for multi-target moves
            if self.move.aoe > 1 and len(team_feed[self.player.user_id]['targets']) < self.move.aoe:
              
                results = target_embed(self.player, self.lobby, self.move, defense=self.defense, attack=self.attack, barrier=self.barrier)
                if results:
                    embed, targets = results
                    if self.defense:
                        msg_text = "defense targets"
                    elif self.attack:
                        msg_text = "attack targets"
                    elif self.barrier:
                        msg_text = "barrier targets"
                    
                    view = TargetSelectView(self.player, targets, self.lobby, self.move, attack=self.attack, defense=self.defense, barrier=self.barrier)
                    # Update the embed with the selected targets
                    selected_targets = len(team_feed[self.player.user_id]['targets'])
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
                    await itx.followup.send("Running simulation", ephemeral=True)
                    simbed = simulation_embed(self.lobby, self.player, self.targets[int(self.values[0])], self.lobby.feed[self.lobby.round])
                    await itx.followup.send(embed=simbed, ephemeral=True)
                    return
            else:
                await itx.followup.send("Running simulation", ephemeral=True)
                simbed = simulation_embed(self.lobby, self.player, self.targets[int(self.values[0])], self.lobby.feed[self.lobby.round])
                await itx.followup.send(embed=simbed, ephemeral=True)
                return



async def setup(bot):
    battle_cog = Battle(bot)
    battle_cog.BattleView = BattleView
    await bot.add_cog(battle_cog)