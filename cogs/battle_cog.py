import discord, db, random, battle_checks
from game import Enemy, Player
from player_tech import technique_list
from battle_checks import battle_checks
from game import Player, Enemy
from player_tech import technique_list
from enemy_techs import enemy_tech
from db import read_player, read_colony
from discord.ext import commands
from discord import app_commands


#region help funcs


def healthbar(health, max_health):

    max_dashes = 4
    dash_ratio = max_health / max_dashes
    filled_dashes = 0 if health <= 0 else int(health / dash_ratio)
    remainder = (health / dash_ratio) - filled_dashes if health > 0 else 0
    dashes = "<:fullheart:1401327640018944070>" * filled_dashes
    if remainder > 0:
        dashes += "<:halfheart:1401327657060270160>"  # Add a half-heart emoji
    percent = f"`{max(round((health / max_health) * 100), 0)}%`"
    # if '-' in percent:
    #     percent = "`0%`"
    bar = f"{dashes} {percent}"

    return bar


def ce_bar(ce, max_ce):

    max_dashes = 4 # max 4
    dash_ratio = max_ce / max_dashes # maximum ce / 4 = 1000 ce = 250 ce per dash
    filled_dashes = 0 if ce <= 0 else int(ce / dash_ratio) # 853 / 250 = 3 dashes 
    remainder = max_dashes - filled_dashes if ce > 0 else 0 # 1000 / 250 = 4 dashes - 3 = 1 remainder 
    dashes = "<:fullce:1401327669328740405>" * filled_dashes # emoji times number of dashes
    percent = f"`{0 if ce <= 0 else round((ce / max_ce) * 100)}%`" # 853 / 1000 = 0.853 * 100 = 85.3% rounded to 85%
    if remainder > 0: # if remainder is greater than 0, add a half dash
        dashes += "<:halfce:1401327682540666951>" # Add a half-ce emoji
    bar = f"{dashes} {percent}" # return the bar with dashes and percent
    print(dashes)
    
    return bar


async def get_player(user_id, colony_id, value=None):

    if value:

        val = read_player(user_id, colony_id, value=value)

    else:

        dict, techlist = read_player(user_id, colony_id)

        return Player(**dict)    
    

async def get_colony(colony_id, value=None):

    if value:
    
        val = read_colony(colony_id)

        return val
    
    else:
    
        dict = read_colony(colony_id)

        return Colonies(**dict)
    

async def gen_round_cont(lobby, bot):
    container= discord.ui.Container()
    header = "# Round " + str(lobby.round)
    teama_title=f"## {lobby.teamA['name']}"
    teama_body="\n".join([f"> {p.name}" for p in lobby.teamA['players']])
    teamb_title=f"## {lobby.teamB['name']}"
    teamb_body="\n".join([f"> {p.name}" for p in lobby.teamB['players']])
    field_title=f"## Field"
    field_body="\n".join([f"> {t.name}" for t in lobby.field.values()])
    display = discord.ui.TextDisplay(content=header + "\n" + teama_title + "\n" + teama_body + "\n" + teamb_title + "\n" + teamb_body + "\n" + field_title + "\n" + field_body)
    container.add_item(discord.ui.Section(display), accessory=bot.user.avatar.url)
    return container


async def ready_check(players):
    for p in players:
        if p.ready == True:
            continue
        else:
            return False
    return True


async def get_player_team(player, lobby):
    if player.user_id in [p.user_id for p in lobby.teamA['players']]:
        return lobby.teamA
    elif player.user_id in [p.user_id for p in lobby.teamB['players']]:
        return lobby.teamB
    elif player.name in [p.name for p in lobby.field.values()]:
        return lobby.field
    else:
        return False


async def get_player_feed(player, team, lobby, type):
    feed = None
    for k, v in lobby.feed.items():
            if k == type:
                feed = [k[team][player.user_id]]
                break
            else:
               continue
    return feed


async def get_valid_targets(feed, team, player, lobby):
    is_npc = False
    is_player = False
    chosen_enemies=None
    if hasattr(player, "user_id"):
        is_player = True
    else:
        is_npc = True
    if is_player:
        chosen_enemies= feed[player.user_id]['targets'] if player.user_id in feed else []
    if is_npc:
        chosen_enemies = feed[player.name]['targets'] if player.name in feed else []
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
                    if is_player:
                        if hasattr(p, 'user_id') and p.user_id == player.user_id:
                            continue
                        elif not chosen_enemies or p.name not in [p.name for p in chosen_enemies]:
                            targets.append(p)

                    elif is_npc:
                        if p.name == player.name:
                              continue
                        elif not chosen_enemies or p.name not in [p.name for p in chosen_enemies]:
                             targets.append(p) 
        return targets
    
    else:
        for p in lobby.field.values():
            if is_player:
                if hasattr(p, 'user_id') and p.user_id == player.user_id:
                    continue
            if is_npc:
                if p.name == player.name:
                    continue
                else:
                    if not chosen_enemies or p.name not in [p.name for p in chosen_enemies]:
                        targets.append(p)
            
            for tar in teamA['players']:
                if is_player:
                    if tar.user_id == player.user_id:
                        continue
                    elif not chosen_enemies or tar.name not in [p.name for p in chosen_enemies]:
                        targets.append(tar)
                if is_npc:
                    if not chosen_enemies or tar.name not in [p.name for p in chosen_enemies] and tar.name != player.name:
                        targets.append(tar)
                return targets


def target_container(player, lobby, type):
    team = get_player_team(player, lobby)
    feed = get_player_feed(player, team, lobby, type)
    targets = None
    if feed:
        targets = get_valid_targets(feed, team, player, lobby)
    else:
        return None
    
    for t in targets:
        if hasattr(t, 'user_id') and t.user_id == player.user_id:
            targets.remove(t)

    value_string = ""
    for i, t in enumerate(targets):
        hp = t.hp
        max_hp = t.max_hp
        ce = t.ce
        max_ce = t.max_ce
        name = t.name
        value_string += f"\n`{i + 1}: {name}`\n" + healthbar(hp, max_hp) + "\n" + ce_bar(ce, max_ce)
    final_str = "# Select target(s)" + "\n" + value_string

    return final_str
        

def move_container(player, move, bot):
    container = discord.ui.Container(accent_color=discord.Color.blue)
    name = move.name
    strength = move.strength
    speed = move.speed
    required_ce = move.act_cost
    aoe = move.aoe
    soul = move.soul if move.soul else None
    move_type = move.type
    required_bodyparts = move.act_req
    activation_speed = move.act_speed
    soul = move.soul if move.soul else None
    title = f"## `{player.name} selected {name}`"
    req_string = "# `Requirements:`\n"
    req_string += f"> **CE required:**`{required_ce}` **Required parts:** " + ", ".join(part for part in required_bodyparts) + "\n"
    move_stats = "# `Stats:`\n"
    move_stats += f"> **Strength:** `{strength}` **Speed:** `{speed}` **AOE:** {aoe} **Activation:** `{activation_speed}s` **Type:** `{move_type}`"
    if soul:
        move_stats += f" **Soul:** `{soul}`"
    container.add_item(discord.ui.Section(discord.ui.TextDisplay(title)), accessory=discord.ui.Thumbnail(bot.user.avatar.url))
    container.add_item(discord.ui.Separator())
    container.add_item(discord.ui.TextDisplay(req_string, move_stats))
    return container


def get_npc_random_attack(lobby):
    attack_field_feed = lobby.feed[lobby.round]['attacks']['Field']
    attack_ready = False
    for enemy_name, enemy_player in lobby.field.items():
        if hasattr(enemy_player, "user_id"):
              continue
        else:
            targets = get_valid_targets(attack_field_feed, lobby.field, enemy_player, lobby)
            rand_targ = random.choice(targets)
            attack_field_feed[enemy_name] = {'target' : rand_targ}
            technique=None
            for tech in enemy_tech:
                if tech.name == enemy_player.technique:
                      technique = tech
            for ptec in technique_list:
                if ptec.name == enemy_player.technique:
                     technique=ptec
            # think about summons and joining all the techniques in one file
            # different summon techniques should have different abilities
            # partial summons for higher levels
            attack_field_feed[enemy_name]['move'] = technique 
            attack_ready = True
    return attack_ready


def get_npc_random_defense(target):

    defenses = []
    defense_str = None
    defense = None
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
     

def format_results(attacker, target, attack_move, defense_move, results):
    result_str = f"**{attacker.name}:** `{attack_move.name}`\n> **Attack strength:** `{attack_move.strength}` **Attack speed:** `{attack_move.speed}` **Activation speed:** `{attack_move.act_speed}s`\n"
    result_str += f"**{target.name}:** `{defense_move.name}`\n> **Defense strength:** `{defense_move.strength}` **Defense speed:** `{defense_move.speed}` **Defense speed:** `{defense_move.act_speed}s`\n"
    result = results[0]
    killed = results[2]
    damage = results[1]
    buffs = results [3]
    atk_speed_buffs = None
    atk_strength_buffs = None
    def_speed_buffs = None
    def_strength_buffs = None
    if buffs:
        if 'speed' in buffs['attack'].keys():
            atk_speed_buffs = buffs['attack']['speed']
        if 'strength' in buffs['attack'].keys():
            atk_strength_buffs = buffs['attack']['strength']
        if 'speed' in buffs['defense'].keys():
            def_speed_buffs= buffs['defense']['speed']
        if 'strength' in buffs['defense'].keys():
            def_speed_buffs=buffs['defense']['strength']
    if atk_strength_buffs:
        result_str += f"**{attack_move.name} Strength buffs:**\n"
        result_str+=">"
        for k, v in atk_strength_buffs.items():
            result_str += f"**{k}:** `{v}` "
        result_str+="\n"
    if atk_speed_buffs:
        result_str += f"**{attack_move.name} Speed buffs:**\n"
        result_str += ">"
        for k, v in atk_speed_buffs.items():
            result_str += f"**{k}:** `{v}`"
        result_str += "\n"

    if def_strength_buffs:
        result_str += f"**{defense_move.name} Strength buffs:**\n"
        result_str += ">"
        for k, v in def_strength_buffs.items():
            result_str += f"**{k}:** `{v}`"
        result_str += "\n"
    if def_speed_buffs:
        result_str += f"**{defense_move.name} Speed buffs:**\n"
        result_str += ">"
        for k, v in def_speed_buffs.items():
            result_str += f"**{k}:** `{v}`"
        result_str += "\n"
    if result == 'hit':
        result_str += f"`{attacker.name} hit {target.name}`\n> **Damage:** `{damage} dmg`"
        if killed:
            result_str += f"`{target.name} has been defeated!`"
    
    elif result == 'tank':
        result_str += f"`{target.name} tanked attack`\n> **Tanked:** `{damage} dmg`"

    elif result == 'dodge':
        if damage>0:
            if killed:
                result_str += f"`{target.name} died attempting to dodge`\n> **Damage:** `{damage} dmg`"
            else:
                result_str += f"`{target.name} took damage dodging`\n> **Damage:** `{damage} dmg`"
        else:
            result_str += f"`{target.name} was able to dodge the attack`\n> **No damage taken**"

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


def sim_container(lobby, round_num, bot):
    get_npc_random_attack(lobby)
    container = discord.ui.Container(accent_color=discord.Color.blue)
    title = f"# `Round {round_num} Simulation`\n> Battle Results"
    container.add_item(discord.ui.Section(discord.ui.TextDisplay(title), accessory=discord.ui.Thumbnail(bot.user.avatar.url)))
    container.add_item(discord.ui.MediaGallery())
    container.add_item(discord.ui.Separator())

    round_feed = lobby.feed[round_num]
    npc_attacks_ready = get_npc_random_attack(lobby)
    attacks = round_feed.get('attacks', {})
    barriers = round_feed.get('barriers', {})
    defenses = round_feed.get("defenses", {})
    simulations = []
    results = None
    for team_name, team_actions in attacks.items():
        for player_id, action_data in team_actions.items():
            player = None
            if team_name == lobby.teamA['name']:
                for p in lobby.teamA['players']:
                    if p.user_id == player_id:
                        player = p
            
            elif team_name == lobby.teamB['name']:
                for p in lobby.teamB['players']:
                    if p.user_id == player_id:
                        player = p
            
            elif team_name == 'Field':
                for p in lobby.field_values():
                    if hasattr(p, 'user_id') and p.user_id == player_id:
                        player = p
                        break
                        
            if player:
                move = action_data.get('move')
                targets = action_data.get('targets', [])
                for target in targets:
                    if hasattr(target, 'user_id'):
                        defense_name, defense_move = set_player_defense(target, round_feed)
                        results = battle_checks(player, target, move.name, defense_name)

                    else:
                        defense_name, defense_move = get_npc_random_defense(target)
                        results = battle_checks(player, target, move.name, defense_name)
                    result_str = format_results(player, target, move, defense_move, results)
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
                            
                        result_str = format_results(player, target, move, defense, results)

                        simulations.append(result_str)
        result_strings = None
        if simulations:
            result_strings = "\n".join(simulations)
        else:
            result_strings = "No actions taken this round"
        return result_strings

def player_cleanup(player):
    pass


def target_container(player, lobby, move_type, bot, move):
    container = discord.ui.Container()
    title = "# `Choose your target`\n"
    team = get_player_team(player, lobby)
    feed = get_player_feed(player, team, lobby, move_type)
    targets = []
    if feed:
        targets = get_valid_targets(feed, team, player, lobby)
    else:
        return False

    for t in targets:
        if hasattr(t, 'user_id') and t.user_id == player.user_id:
            targets.remove(t)
    valuestrings = []
    for i, t in enumerate(targets):
        hp = t.hp
        max_hp = t.max_hp
        ce = t.ce
        max_ce = t.max_ce
        name = t.name
        bp = t.bodyparts
        valuestrings.append(f"### `{i+1}: {name}`\n" + healthbar(hp, max_hp) + "\n" + ce_bar(ce, max_ce) + "\n")
    container.accent_color = discord.Color.blue
    title_section = discord.ui.Section(discord.ui.TextDisplay(title), accessory=bot.user.avatar.url)
    container.add_item(title_section)
    container.add_item(discord.ui.Separator())
    for string in valuestrings:
        container.add_item(discord.ui.TextDisplay(string))
        container.add_item(discord.ui.Separator())
    if move_type == "attack":
        container.add_item(discord.ui.ActionRow(AttackSelect(bot, player, targets, lobby, move, team)))
    if move_type == "defense":
        container.add_item(discord.ui.ActionRow(DefenseTargets()))
    if move_type == "barrier":
        container.add_item(discord.ui.ActionRow(BarrierTargets()))
    return container

# endregion

#region BattleCog
class Battle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cog = bot.get_cog('Lobby_Cog')

    @commands.Cog.listener()
    async def on_ready(self):
        print("Battle cog ready")


    @commands.hybrid_command(name='vow', description="Choose a binding vow")
    async def vow(self, ctx):
        player = get_player(ctx.author.id, ctx.guild.id)
        await ctx.send("command under construction")
    
    @commands.hybrid_command(name="summon")
    async def summon(self, ctx):
        player = get_player(ctx.author.id, ctx.guild.id)
        await ctx.send("command under construction")
        lobby = self.cog.lobbies[ctx.channel.id]['Lobby']
        if player:
            if lobby and lobby.status > 1:
                if player.user_id in lobby['players']:
                    title="# Choose a summon"
                
#endregion
class BattleView(discord.ui.LayoutView):
    def __init__(self, lobby, bot):
        super().__init__()
        self.team1 = lobby.teamA
        self.team2 = lobby.teamB
        self.field = lobby.field
        self.lobby = lobby
        self.bot = bot
        container = discord.ui.Container(accent_color=discord.Color.blurple())
        title_section = discord.ui.Section(discord.ui.TextDisplay(f"# `Battle Started`\n## Round {lobby.round}"), accessory=discord.ui.Thumbnail(bot.user.avatar.url))
        container.add_item(title_section)
        container.add_item(discord.ui.Separator())
        container.add_item(discord.ui.TextDisplay(f"### `{self.team1['name']}`\n" + "\n".join([f"> {p.name}" for p in self.team1['players']])))
        container.add_item(discord.ui.Separator())
        container.add_item(discord.ui.TextDisplay(f"### `{self.team2['name']}`\n" + "\n".join([f"> {p.name}" for p in self.team2['players']])))
        container.add_item(discord.ui.Separator())
        container.add_item(discord.ui.TextDisplay(f"### `Field`\n" + "\n".join([f"> {t.name}" for t in self.field.values()])))
        self.add_item(container)



#region Attack Select View

# class AttackSelect(discord.ui.Select):
    
#     def __init__(self, player, attack_moves):
#         self.player = player
#         self.attack_moves = attack_moves
#         options = [ discord.SelectOption(label=f"{i+1}: {m.name}", description=f"AOE: {m.aoe}", value=str(i)) for i, m in enumerate(attack_moves)]
#         super().__init__(placeholder="Select an attack", options=options)

#     async def callback(self, itx: discord.Interaction):
#         channel = itx.channel
#         if itx.user.id != self.player.user_id:
#             await itx.response.send_message("This is not your prompt.", ephemeral=True)
#         else:
#             await itx.response.defer()
#             if itx.user.id in self.lobby.ready:
#                 await itx.response.send_message("You've already chosen an attack this round.", ephemeral=True)
#             move = self.attack_moves[int(self.values[0])]
#             string = move_string(self.player, move)
#             await itx.response.send_message(string, ephemeral=True)

class AttackSelect(discord.ui.Select):
    def __init__(self, bot, player, targets, lobby, move, team):
        options = [discord.SelectOption(label=f"{i+1}: {t.name}", value=str(i)) for i, t in enumerate(targets)]
        super().__init__(placeholder="Choose attack target")
        self.lobby = lobby
        self.player = player
        self.move = move
        self.bot = bot
        self.team = team
        self.targets = targets

    async def callabck(self, itx: discord.Interaction):
        channel = itx.channel
        if itx.user_id != self.player.user_id:
            await itx.response.send_message("This is not your prompt.", ephemeral=True)
        else:
            await itx.response.defer()
            round = self.lobby.round
            charges= getattr(self.move, 'charge', 0)
            atk_feed = self.lobby.feed[round]['attacks'][self.team['name']]
            selected_target = self.targets[int(self.values[0])]
            if self.player.user_id not in atk_feed.keys():
                atk_feed[self.player.user_id] = {
                    'move' : self.move,
                    'targets' : [selected_target],
                    'charges' : charges,
                    'results' : None
                }

            else:
                if self.move.aoe > 1:
                    if len(atk_feed[self.player.user_id]['targets']) >= self.move.aoe:
                        await itx.followup.send("Maximum targets selected.", ephemeral=True)
                    else:
                        atk_feed[self.player.user_id]['targets'].append(selected_target)
            await itx.followup.send('You target: ' + selected_target.name + " with: " + self.move.name, ephemeral=True)

            selected_targets = len(atk_feed[self.player.user_id]['targets'])

            if self.move.aoe > 1 and selected_targets < self.move.aoe:
                target_container = target_container(self.player, self.targets, 'attack', self.bot)
                target_view = discord.ui.LayoutView()
                target_view.add_item(target_container)
                target_view.add_item(discord.ui.ActionRow(FinishAOE()))
                aoe = self.move.aoe
                await itx.followup.send(view=target_view)
                return
            else:
                await itx.followup.send("Finished selecting targets.", ephemeral=True)
                if self.lobby.feed['Defend'][self.team['name']][self.player.user_id]:
                    self.lobby.ready.append(self.player.user_id)
                    ready = ready_check(self.lobby.players)
                    if ready:
                        container=sim_container(self.lobby, self.lobby.round, self.bot)
                        layout = discord.ui.LayoutView()
                        layout.add_item(container)
                        view=layout
                        await itx.followup.send(view=view)
                        self.lobby.round += 1
                        self.lobby.ready = []
                        self.lobby.feed.append({
                                                "round" : self.lobby.round,
                                                 
                                               'attacks' : {self.lobby.teamA['name'] : {}, 
                                                            self.lobby.teamB['name'] : {}, 
                                                            'Field' : {}},
                                                'defenses' : {self.lobby.teamA['name'] : {},
                                                              self.lobby.teamB['name'] : {},
                                                              'Field' : {}},
                                                'barrriers' : {self.lobby.teamA['name'] : {},
                                                               self.lobby.teamB['name'] : {},
                                                               'Field' : {}}})
                        round_container = gen_round_cont(self.lobby, self.bot)
                        round_view = discord.ui.LayoutView()
                        round_view.add_item(round_container)
                        await channel.send(view=round_view)
                        return
                    else:
                        await itx.followup.send(f"{self.player.name} is ready.\nWaiting for all players to finish selecting moves.")
                        return
                else:
                    await itx.followup.send("No defense selected yet", ephemeral=True)
                    return

class DefenseSelect(discord.ui.Select):
    def __init__(self, bot, player, lobby, move, team):
        targets=[]
        for t in team.players:
            targets.append(t)
        options = [discord.SelectOption(label=f"{i+1}: {t.name}", value=str(i)) for i, t in enumerate(targets)]
        super().__init__(placeholder="Choose defense target")

        self.lobby = lobby
        self.player = player
        self.move = move
        self.bot = bot
        self.team = team
        self.targets = targets

    async def callabck(self, itx: discord.Interaction):
        channel = itx.channel
        if itx.user_id != self.player.user_id:
            await itx.response.send_message("This is not your prompt.", ephemeral=True)
        else:
            await itx.response.defer()
            round = self.lobby.round
            charges= getattr(self.move, 'charge', 0)
            def_feed = self.lobby.feed[round]['defenses'][self.team['name']]
            selected_target = self.targets[int(self.values[0])]
            if self.player.user_id not in def_feed.keys():
                def_feed[self.player.user_id] = {
                    'move' : self.move,
                    'targets' : [selected_target],
                    'charges' : charges,
                    'results' : None
                }
            else:
                
                if len(def_feed[self.player.user_id]['targets']) >= self.move.aoe:
                        await itx.followup.send("Maximum targets selected.", ephemeral=True)
                else:
                        def_feed[self.player.user_id]['targets'].append(selected_target)

            await itx.followup.send('You target: ' + selected_target.name + " with: " + self.move.name, ephemeral=True)

            selected_targets = len(def_feed[self.player.user_id]['targets'])

            if self.move.aoe > 1 and selected_targets < self.move.aoe:
                self.targets.remove(selected_target)
                result_container = target_container(self.player, self.targets, 'attack', self.bot)
                targ_view = discord.ui.Container(accent_color=discord.Color.blue)
                await itx.edit_original_response(view=targ_view)
                aoe = self.move.aoe
                await itx.followup.send(f"Selected {selected_targets} out of {aoe} attack targets, choose more targets or press done", view=FinishAOE())
                return
            
            else:
                await itx.followup.send("Finished selecting targets.", ephemeral=True)
                if self.lobby.feed['Defend'][self.team['name']][self.player.user_id]:
                    self.lobby.ready.append(self.player.user_id)
                    ready = ready_check(self.lobby.players)
                    if ready:
                        container=sim_container(self.lobby, self.lobby.round)
                        view = SimulationLayout(container)
                        await itx.followup.send(view=SimulationLayout())
                        self.lobby.round += 1
                        self.lobby.ready = []
                        self.lobby.feed.append({"round" : self.lobby.round, 
                                               'attacks' : {self.lobby.teamA['name'] : {}, 
                                                            self.lobby.teamB['name'] : {}, 
                                                            'Field' : {}},
                                                'defenses' : {self.lobby.teamA['name'] : {},
                                                              self.lobby.teamB['name'] : {},
                                                              'Field' : {}},
                                                'barrriers' : {self.lobby.teamA['name'] : {},
                                                               self.lobby.teamB['name'] : {},
                                                               'Field' : {}}})
                        round_container = gen_round_cont(self.lobby, self.bot)
                        await channel.send(view=RoundLayout(round_container))
                        return
                else:
                    await itx.followup.send("No defense selected, do you wish to finish the round?", ephemeral=True)
                    return

class BarrierSelect(discord.ui.Select):
    pass
#             channel = itx.channel
#             # Determine which team the player is on
#             team = None
#             move_type = None
#             if self.attack:
#                 move_type = 'attacks'
#             elif self.defense:
#                 move_type = 'defenses'
#             elif self.barrier:
#                 move_type = 'barriers'
#             team_name = None
#             if any(self.player.user_id == p.user_id for p in self.teama['players']):
#                 team = self.teama
#                 team_name = team['name']

#             elif any(self.player.user_id == p.user_id for p in self.teamb['players']):
#                 team = self.teamb
#                 team_name = team['name']

#             elif any(hasattr(thing, 'user_id') and self.player.user_id == thing.user_id for thing in self.field.values()):
#                 team = self.field
#                 team_name = 'Field'

#             if not team:
#                 await itx.followup.send("Player is not on any team.", ephemeral=True)
#                 return
            
#             if self.attack:
#                 if team_name not in attacks:
#                     attacks[team_name] = {}
#                 team_feed = attacks[team_name]

#             elif self.defense:
#                 if team_name not in defenses:
#                     defenses[team_name] = {}
#                 team_feed = defenses[team_name]

#             elif self.barrier:
#                 if team_name not in barriers:
#                     barriers[team_name] = {}
#                 team_feed = barriers[team_name]
#             else:
#                 await itx.followup.send("Invalid move type.", ephemeral=True)
#                 return
            
#             # print("Team feed: " + str(team_feed) + " for team: " + team_name)
#             selected_target = self.targets[int(self.values[0])]
#             print("Selected target: " + selected_target.name)

#             if self.player.user_id not in team_feed.keys():
#                 team_feed[self.player.user_id] = {
#                     'move': self.move, # save technique to feed
#                     'targets': [selected_target], # initialize targets
#                     'charges': charges, # initialize charges
#                     'results': None # initialize results
#                 }

#             else:
#                 team_feed[self.player.user_id]['targets'].append(selected_target)

#             print(f"Updated team feed for {self.player.user_id}: {team_feed[self.player.user_id]}")

#             await itx.followup.send(self.player.name + " targets: " + selected_target.name + " with: " + self.move.name)
            
#             selected_targets = len(team_feed[self.player.user_id]['targets'])

#             if self.move.aoe > 1 and  selected_targets < self.move.aoe:
#                 results = TargetLayout(self.player, self.targets, self.lobby)
#                 if results:
#                     embed, targets, file = results
#                     if self.defense:
#                         msg_text = "defense targets"
#                     elif self.attack:
#                         msg_text = "attack targets"
#                     elif self.barrier:
#                         msg_text = "barrier targets"
#                     view = TargetSelectView(self.bot, self.player, targets, self.lobby, self.move, attack=self.attack, defense=self.defense, barrier=self.barrier)
#                     # Update the embed with the selected targets
#                     aoe = self.move.aoe
#                     if not file:
#                         await itx.followup.send(
#                             content=f"Selected {selected_targets} out of {aoe} {msg_text}. You may choose more targets.",
#                             embeds=[embed],
#                             view=view,
#                             ephemeral=True
#                         )
#                     else:
#                          await itx.followup.send(
#                             content=f"Selected {selected_targets} out of {aoe} {msg_text}. You may choose more targets.",
#                             embeds=[embed],
#                             view=view,
#                             ephemeral=True, file=file
#                         )
                         
#                     return
#                 else:
#                         await itx.followup.send("No more targets available.", ephemeral=True)
#                         self.lobby.ready.append(self.player.user_id)
#                         ready = check_ready_players(self.lobby)
#                         if ready:
#                             embed = simulation_embed(self.lobby, self.lobby.round)
#                             await itx.followup.send(embed=embed, ephemeral=True)
#                             self.lobby.round += 1
#                             self.lobby.ready = []
#                             self.lobby.feed.append({'round' : self.lobby.round,
#                                 'attacks': { self.lobby.teamA['name'] : {}, self.lobby.teamB['name'] : {}, 'Field': {}},
#                                 'defenses': { self.lobby.teamA['name'] : {}, self.lobby.teamB['name'] : {}, 'Field': {}},
#                                 'barriers': { self.lobby.teamA['name'] : {}, self.lobby.teamB['name'] : {}, 'Field': {}}
#                             })
#                             round_embed = generate_round_embed(self.lobby)
#                             await channel.send(embed=round_embed, view=BattleView(self.lobby, self.bot))
#                             return      
#                         await itx.followup.send("Move selected for this round, wait for players to finish selecting moves.", ephemeral=True)
#                         return
#             else:
#                 self.lobby.ready.append(self.player.user_id)
#                 ready = check_ready_players(self.lobby)
#                 if ready:
#                     embed = simulation_embed(self.lobby, self.lobby.round)
#                     print("Final round feed: " + str(self.lobby.feed))
#                     await itx.followup.send(embed=embed)
                    
#                     self.lobby.round += 1
#                     self.lobby.ready = []
#                     self.lobby.feed.append({'round' : self.lobby.round,
#                         'attacks': { self.lobby.teamA['name'] : {}, self.lobby.teamB['name'] : {}, 'Field': {}},
#                         'defenses': { self.lobby.teamA['name'] : {}, self.lobby.teamB['name'] : {}, 'Field': {}},
#                         'barriers': { self.lobby.teamA['name'] : {}, self.lobby.teamB['name'] : {}, 'Field': {}}
#                     })
#                     round_embed = generate_round_embed(self.lobby)
#                     await channel.send(embed=round_embed, view=BattleView(self.lobby, self.bot))
#                     return
                
#                 await itx.followup.send("You have selected your target. Wait for others to finish selecting", ephemeral=True)
#                 return


class SimulationLayout(discord.ui.LayoutView):
    def __init__(self, container):
        super().__init__()
        self.add_item(container)

class FinishAOE(discord.ui.Button):
    def __init__(self, msg):
        super().__init__(label="Finish AOE selection")
        self.msg = msg
    async def callback(self, itx: discord.Interaction, btn: discord.Button):
        await itx.followup.send("Finished selecting targets.", ephemeral=True)
        if self.lobby.feed['Defend'][self.team['name']][self.player.user_id]:
                    self.lobby.ready.append(self.player.user_id)
                    ready = ready_check(self.lobby.players)
                    if ready:
                        container=sim_container(self.lobby, self.lobby.round, self.bot)
                        layout = discord.ui.LayoutView()
                        layout.add_item(container)
                        view=layout
                        await itx.followup.send(view=view)
                        self.lobby.round += 1
                        self.lobby.ready = []
                        self.lobby.feed.append({"round" : self.lobby.round, 
                                               'attacks' : {self.lobby.teamA['name'] : {}, 
                                                            self.lobby.teamB['name'] : {}, 
                                                            'Field' : {}},
                                                'defenses' : {self.lobby.teamA['name'] : {},
                                                              self.lobby.teamB['name'] : {},
                                                              'Field' : {}},
                                                'barrriers' : {self.lobby.teamA['name'] : {},
                                                               self.lobby.teamB['name'] : {},
                                                               'Field' : {}}})
                        # round_container = gen_round_cont()
                        # await channel.send(view=RoundLayout(round_container))
                        return
                    else:
                            await itx.edit_original_response(f"{self.player.name} is ready.\nWaiting for all players to finish selecting moves.")
                            return
                    
        else:
                        await itx.followup.send("No defense selected, do you wish to finish the round?", ephemeral=True)
                        return
              

async def setup(bot):
    Battle.BattleView=BattleView
    await bot.add_cog(Battle(bot))


# #endregion

