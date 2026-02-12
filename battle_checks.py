import game, random
from summons import shikigami_list
from game import Player, Enemy
from player_tech import technique_list
from enemy_techs import enemy_tech
from cursed_tools import cursed_tools

#region Battle Checks
def battle_checks(player, target, attack_str, defense_str, tech_vow=None, aoe=False):      
        tools=None
        target_tools=None
        buffs = None
        if aoe:
            attack, player = attack_verify(player, target, attack_str, aoe=True)
            defense, target = defense_verify(target, player, defense_str, aoe=True)
        else:
            attack, player = attack_verify(player, target, attack_str)
            defense, target = defense_verify(target, player, defense_str)

        if player.equipped:
            tools = get_move(player, tools=player.equipped)
        elif target.equipped:
            target_tools = get_move(target, tools=target.equipped)
        if not attack:
            return False
        if not defense:
            return False
        print('Starting battle checks...')
        stack=player.stack
        defense_negated=False
        attack_negated=False
        soul_dmg=0
        soul_defense=0
        dmg = 0
        speed = 0
    
    # region conditional increments
        if attack.type == "summon":
            print("summon")
            
        # player increment
        if tools:
            print("Tool detected... incrementing attack stats with tools")
            dmg, speed, buffs, items = type_increment(player, attack=attack, tools=tools)  
            for item in items:
                print(f"Attack {attack.name} has a base damage of {dmg} and speed of {speed} with item {item.name}")
                if item.negates:
                    defense_negated=True
                    print(f"{item.name} negates any defenses for {defense.name}")

                if item.soul:                         
                    soul_dmg += item.soul
                    print(f"{item.name} has a soul damage of {soul_dmg}")

                # if item.charge:
                #     charge += item.charge
                #     print(f"{item.name} has a charge of {item.charge}")

                if item.poison:
                    player.poison = item.poison
                    print(f"{item.name} has a poison of {item.poison}")

        if attack.type == 'amp':
            player, dmg, speed, buffs = type_increment(player, attack=attack)
            print(f"Attack {attack.name} has a base damage of {dmg} and speed of {speed}")
            results = barrier_checks(player, target, defense, attack, dmg)
        
        else:
            print(f"Attack {attack.name} has a base damage of {attack.strength} and base speed of {attack.speed}")
            player, dmg, speed, buffs = type_increment(player, attack=attack)
            print(f"Attack {attack.name} has a incremented damage of {dmg} and incremented speed of {speed}")

        # target increment
        if target_tools:
            defense_strength, defense_speed, buffs, items = type_increment(defense=defense, tools=target_tools)
         
            for item in items:
                print(f"Defense {defense.name} has a base damage of {defense.strength} and speed of {defense.speed} with item {item.name}")
                if item.negates:
                    attack_negated=True
                    print(f"{item.name} negates any attacks from {attack.name}")
                if item.soul:
                    soul_defense += item.soul
                    print(f"{item.name} has a soul defense of {soul_defense}")

        if defense.type == 'amp':
            target, defense_strength, defense_speed, buffs, target = type_increment(target, defense=defense)
            print(f"Defense {defense.name} has an incremented defense of {defense_strength} and incremented speed of {defense_speed}")
            results = barrier_checks(player, target, attack, dmg, speed, defense, defense_strength)
        
        else:
            print(f"Defense {defense.name} has a base defense of {defense.strength} and base speed of {defense.speed}")
            target, defense_strength, defense_speed, buffs = type_increment(target, defense=defense)
            print(f"Defense {defense.name} has a incremented defense of {defense_strength} and incremented speed of {defense_speed} defense owner is: {target} with the following buffs: \n{buffs} ") 

    #endregion

    # region conditional checks
        # sure hit checks
        if attack.sure_hit:
            print(f"{attack.name} is a sure hit")

        if defense.sure_hit:
            print(f"{defense.name} is a sure hit")

        # visability checks
        atk_invis=None
        targ_invis=None
        if attack.invisible:
            atk_invis = attack_visibility(target, attack)
        if defense.invisible:
            targ_invis = defense_visibility(player, target, attack, defense)

        # negate checks - needs to be improved
        if defense.negates:
            attack_negated=True
            if attack_negated:
                results = negate_check(target, dmg, defense_strength, defense=defense)
            #     return results
        if attack.negates:
            defense_negated=True
            if defense_negated:
                results = negate_check(target, dmg, defense_strength, attack=attack)
            #     return results

        # soul/stack checks
        if defense.soul:
            soul_defense += defense.soul
            print(f"{defense.name} has a soul strength of {soul_defense}") 
        if stack > 0:
            print(f"{attack.name} has a stack of {stack}")
            dmg = dmg + (speed * 2.4) 
            stack -= 1
            player.stack = stack
        
        # print other move stats
        print(f"Defense activaton speed: {defense.act_speed}\nAttack activation speed: {attack.act_speed}")
        print(f"{attack.name}'s type is {attack.type}\n{defense.name}'s type is {defense.type}")
    
        # barrier clash/attack check
        if attack.type == 'open' or attack.type == 'closed':
            if defense.type == 'open' or defense.type == 'closed':
                print(f"{defense.name} 'domain clash' against {attack.name}...")    
                results = domain_clash(target, player, defense, attack, dmg, speed, defense_strength, defense_speed, targ_invis, atk_invis, attack_negated, defense_negated)
                return results, buffs
            else:
                print(f"{attack.name} 'barrier check' with defense {defense.name}...")    
                results = barrier_checks(player, target, attack, dmg, speed, defense, defense_strength)
                return results, buffs
        
        # tank check
        if defense.type == 'tank' or defense.type == 'heal':
            print(f"{defense.name} 'tank check' against {attack.name}...")
            print(defense_strength)
            results = tank_check(target, attack, defense, dmg, speed, defense_strength, defense_speed, targ_invis, attack_negated, defense_negated, soul_defense=soul_defense)
            return results, buffs
        
        # counter check
        if 'counter' in defense.type:
            print(f"{defense.name} 'counter check' against {attack.name}...")
            results = counter_check(target, player, defense, attack, dmg, speed, defense_strength, defense_speed, targ_invis, atk_invis, attack_negated, defense_negated)
            return results, buffs
        
        # dodge check
        if defense.type == 'dodge':
            print(f"{defense.name} 'dodge check' against {attack.name}...")
            results = dodge_check(target, defense, attack, dmg, speed, defense_strength, defense_speed, targ_invis, attack_negated, defense_negated)
            return results, buffs   
        
        # barrier defense check
        else:
            print(f"{defense.name} 'barrier check' with attack {attack.name}...")    
            results = barrier_checks(player, target, attack, dmg, speed, defense, defense_strength)
            return results, buffs
        #endregion
#endregion


def damage_target(target, dmg, soul, defense, def_vow=None, atk_vow=None):
#region defense vow distribution
    initial_hp = target.hp
    if def_vow:
        #check if total defense vow ce is greater than target ce
        total_def_ce = sum(def_vow.values())
        if total_def_ce > target.ce:
            pass
        else:
            vow = def_vow
            for k in vow.keys():
                imbued = vow[k]
                if k in target.bodyparts and target.ce >= imbued:
                    bodypart = target.bodyparts[k]
                    if bodypart.ce:
                        bodypart.ce += imbued
                        bodypart.max_ce += imbued
                        target.ce -= imbued
                    else:
                        bodypart.ce = imbued
                        bodypart.max_ce = imbued
                        target.ce -= imbued
#endregion
#region attack vow distribution
    # Calculate base damage distribution
    base_10_percent = 10  # Base percent for limbs and head (10%)
    base_50_percent = 50  # Base percent for torso (50%)
    # Create a dictionary to track damage distribution percentages
    damage_distribution = {
        "Head": base_10_percent,
        "Left Arm": base_10_percent,
        "Right Arm": base_10_percent, 
        "Torso": base_50_percent,
        "Left Leg": base_10_percent,
        "Right Leg": base_10_percent
    }
    # Handle attack vows (redistribute damage to specific parts)
    if atk_vow:
        # Calculate how much percentage to redistribute
        total_redistribution = sum(atk_vow.values())
        if total_redistribution > 100:
            pass
        else:
            # First reduce percentages from non-targeted parts proportionally
            non_targeted_parts = [part for part in damage_distribution if part not in atk_vow]
            if non_targeted_parts:
                total_non_targeted_percent = sum(damage_distribution[part] for part in non_targeted_parts)
                for part in non_targeted_parts:
                    # Calculate how much this part should contribute to redistribution
                    if total_non_targeted_percent > 0:
                        reduction_factor = damage_distribution[part] / total_non_targeted_percent 

                        reduction = total_redistribution * reduction_factor

                        damage_distribution[part] = max(damage_distribution[part] - reduction, 0)

                    else:
                        damage_distribution[part] = 0
            
            # Then add the redistributed percentages to targeted parts
            for part, additional_percent in atk_vow.items():
                    old_damage = damage_distribution[part]
                    damage_distribution[part] += additional_percent
                    damage_distribution[part] -= old_damage # subtract the old damage to not go higher than 100%
                    print(f"Attack vow redistributes {additional_percent}% more damage to {part}")
    

    # Calculate actual damage amounts based on percentages
    damage_amounts = {part: (dmg * percent // 100) for part, percent in damage_distribution.items()}
    
    # Debug output
    for part, dmg_amount in damage_amounts.items():
        print(f"{part} will take {dmg_amount} damage ({damage_distribution[part]}% of total)")
    #endregion

#region soul
    # Calculate soul damage
    soul_damage = {}
    defense_soul = {}
    if soul:
        for part, percent in damage_distribution.items():
            soul_damage[part] = soul * percent // 100
    if defense:
        if defense.soul:
            for part, percent in damage_distribution.items():
                defense_soul[part] = defense.soul * percent // 100
        
    #endregion
    
    total_hp = 0
    total_maxhp = 0   

    for bodypart in target.bodyparts.keys():
        print("Pre damage check body: " + str(target.bodyparts[bodypart].__dict__))
        bp = target.bodyparts[bodypart]
        # Get the damage amount for this part
        part_damage = damage_amounts.get(bp.name, 0)
        #region dead bodypart
        if bp.hp <= 0:
            # If part is already disabled, redistribute its damage among other parts
            still_active = [p for p in target.bodyparts.values() if p.hp > 0 and p.name != bp.name]
            if len(still_active) > 0:
                extra_per_part = part_damage // len(still_active)
                for active_part in still_active:
                     damage_amounts[active_part.name] += extra_per_part
                # print(f"{bp.name} is disabled, its {part_damage} damage redistributed")
            continue
        #endregion

        #region ce checks    
        elif bp.ce and bp.ce > 0:
            print(f"Bodypart ce enforcement reducing damage by {bp.ce}")
            print(f"Pre damage ce check for {bp.name}: dmg={part_damage} - bp.ce={bp.ce}")

            # Apply the damage with CE protection
            reduced_dmg = max(part_damage - bp.ce, 0)
            reduced_ce = max(bp.ce - part_damage, 0)

            print(f"Post ce check damage {reduced_dmg}")
            bp.ce = reduced_ce
            bp.hp -= reduced_dmg
            
            if soul:
                part_soul_dmg = soul_damage.get(bp.name, 0)
                part_def_soul = defense_soul.get(bp.name, 0) if defense_soul else 0
                bp.max_hp -= max(part_soul_dmg - part_def_soul, 0)
                print(f"{bp.name} took {max(part_soul_dmg - part_def_soul, 0)} soul damage reducing their max hp to {bp.max_hp}")
                if bp.max_hp < bp.hp:
                    bp.hp = bp.max_hp
            print(f"{bp.name} taking {reduced_dmg} damage")
            print(f"Remaining ce {bp.ce}")
        #endregion

        #region full damage
        else:
            # # If bodypart has no CE, apply damage directly
            # print(f"No CE on bodypart to absorb damage")
            bp.hp -= part_damage
    
            if soul:
                part_soul_dmg = soul_damage.get(bp.name, 0)
                part_def_soul = defense_soul.get(bp.name, 0) if defense_soul else 0
                bp.max_hp -= max(part_soul_dmg - part_def_soul, 0)
                # print(f"{bp.name} took {max(part_soul_dmg - part_def_soul, 0)} soul damage reducing their max hp to {bp.max_hp}")
                if bp.max_hp < bp.hp:
                    bp.hp = bp.max_hp
            
            # print(f"{bp.name} took {part_damage} damage")
       
        total_hp += bp.hp
        total_maxhp += bp.max_hp
        # print("Post damage check body: " + str(target.bodyparts[bodypart].__dict__))
        #endregion
    target.hp = total_hp
    target.max_hp = total_maxhp
    body_dmg = initial_hp - total_hp # part of returning body_dmg
    print("Total hp left: " + str(total_hp))
    print("Total maxhp left: " + str(total_maxhp))    
    return target, target.hp, target.max_hp, body_dmg
    #endregion
    
# region get move
def get_move(player, attack=None, defense=None, tools=None, aoe=False, target=False):
    tech=None 
    is_player=False
    is_enemy=False

    if isinstance(player, Enemy):
        if player.playerclass == "summon":
            list_tech = [v for k, v in enemy_tech.items() if k == player.name]
            tech = list_tech[0]
            print(f"Enemy {player.name} has {player.technique} technique")
            is_enemy=True
        else:
            list_tech =[t for t in technique_list if next(iter(t)) == player.technique]
            tech = list_tech[0]
            print(f"Enemy {player.name} has {player.technique} technique")
            print(tech)
            is_enemy=True

    elif isinstance(player, Player):
            if aoe:
                list_tech = [t for t in technique_list if next(iter(t)) == target.technique]
                tech = list_tech[0]
                is_player=True
            else:
                list_tech = [t for t in technique_list if next(iter(t)) == player.technique]
                tech = list_tech[0]
                print(f"Player {player.name} has {player.technique} technique")
                print(tech[player.technique])
                is_player=True

    if tools:
        new_tools_dict = [(k, v) for k, v in cursed_tools.items() if k in tools]
        new_tools = []
        for name, item in new_tools_dict:
            new_tools.append(item)
            print(f"{player.name} has {name} equipped with a strength of {item.strength} and speed of {item.speed}")
        return new_tools
    
    if attack:
        print(f"Setting attack '{attack}' for {player.name}")

        if "Domain" in attack or "Falling Blossom" in attack or "Hollow Wicker" in attack:
            new_barrier = get_barrier(player, is_player, is_enemy, tech, attack=attack)
            return new_barrier
        
        if "Heal" in attack:
            print("You can't heal on an attack move")
            return None

        else:
            #print(f"Player {player.name} is using {attack}")
            #print(tech)
            new_attack = tech[player.technique][0]['Attack'][attack]
            return new_attack
        
        # if is_enemy:
        #     #print(f"Enemy {player.name} is using {attack}")
        #     #print(tech)
        #     new_attack = tech[0]['Attack'][attack]
        #     return new_attack
    
    if defense:
        print(f"Setting defense '{defense}' for {player.name}")

        if "Domain" in defense or "Falling Blossom" in defense or "Hollow Wicker" in defense:
            new_barrier = get_barrier(player, is_player, is_enemy, tech, defense=defense)
            return new_barrier
        
        if "Heal" in defense:
            if is_player:
                new_defense = tech[player.technique][3]['RCT'][defense]
            elif is_enemy:
                new_defense=tech[3]['RCT'][defense]
            player.defense = new_defense
            return new_defense

        if is_player:
            #print(f"Player {player.name} is using {defense}")
            if aoe:
                new_defense = tech[target.technique][1]['Defend'][defense]
                player.defense = new_defense
                return new_defense
            else:
                new_defense = None
                if defense in tech[player.technique][1]['Defend']:
                    new_defense= tech[player.technique][1]['Defend'][defense]
                    return new_defense
                else:
                    for tech in technique_list:
                        name = next(iter(tech))
                        print("Checking if  " + defense + " is in " + name)
                        technique = tech[name]
                        print(technique[1]['Defend'].keys())
                        if defense in technique[1]['Defend'].keys():
                            print(f"Found {defense} in {name}")
                            new_defense = tech[name][1]['Defend'][player.defense]
                            print(new_defense.name)
                            break
                        else:
                            continue
                return new_defense
                        
        
        if is_enemy:
            if isinstance(tech, list):
                new_defense = tech[1]['Defend'][defense]
                print(f"Enemy {player.name} is using {defense}")
                return new_defense
            else:
                new_defense = tech[player.technique][1]['Defend'][defense]
                print(f"Enemy {player.name} is using {defense}")
                return new_defense
#endregion

#region get_barrier
def get_barrier(player, is_player, is_enemy, tech, attack=None, defense=None):

    if attack:
        if is_player:
            new_attack = tech[player.technique][2]['Barrier'][attack]
            return new_attack
        
        if is_enemy:
            new_attack = tech[0]['Barrier'][attack]
            return new_attack

    if defense:
        if is_player:
            new_defense= tech[player.technique][2]['Barrier'][defense]
            return new_defense
        if is_enemy:
            new_defense = tech[1]['Barrier'][defense]
            return new_defense
#endregion
        
# region verify checks
def attack_verify(player, target, attack, aoe=False):
    print(f"Verifying attack '{attack}' for {player.name}")
    if aoe:
        attack = get_move(player, attack=attack, aoe=True)
    else:
        attack = get_move(player, attack=attack)
    
    # if player.ce < attack.act_cost:
    #     print('not enough ce to use attack')
    #     return "no ce"
    
    # if player.level < attack.level:
    #     print('not a high enough level to use attack')
    #     return "no lvl"
    
    if attack.charge:
        if target.name in player.inventory['Technique Inv']['Charges'].keys():
                print("checking charges")
                charge = player.inventory['Technique Inv']['Charges'][target.name]
                if charge > 0:
                    print("reducing charge by 1")
                    charge -= 1
                if charge <= 0:
                   print("insufficient charge")
                   del player.inventory['Technique Inv']['Charges'][target.name]
                print("Attack verified!")
                return attack, player
        else:
            print("No charge for attack")
            return False

    else:
        print("Attack verified!")

        if player.imbue:
            if isinstance(player.imbue, int):
                amount = player.imbue
                player.imbue = {'strength': amount, 'speed': amount}

            player.ce -= attack.act_cost + player.imbue['strength']
        else:
            player.ce -= attack.act_cost
        
        
        return attack, player
    

def defense_verify(target, player, defense, aoe=False):
    if defense == None:
        print("No defense selected")
        print(f"Selecting random defense for {target.name}")
        if target.technique in technique_list:
            list_tech = [t for t in technique_list if next(iter(t)) == target.technique]
            defense = random.choice(list_tech['Defend'].values())
        else:
            list_tech = [v for k, v in enemy_tech.items() if k == target.technique]
           
            
            if len(list_tech) == 0:
                list_tech = [t for t in technique_list if next(iter(t)) == target.technique]
                print("Choosing random enemy defense from: ")
                print(list_tech)
                defense = random.choice(list_tech['Defend'].values())
            else:
                print("Choosing random enemy defense from: ")
                print(list_tech)
                defense = random.choice(list_tech[1].values())
        
    defense = get_move(target, defense=defense)

    # if target.ce < defense.act_cost:
    #     print('not enough ce to use defense')
    #     return "no ce"
    
    # if target.level < defense.level:
    #     print('not a high enough level to use defense')
    #     return "no lvl"
    
    if defense.charge:
        if target.name in defense.inventory['Technique Inv']['Charges'].keys():
                charge = defense.inventory['Technique Inv']['Charges'][player.name]
                if charge > 0:
                    charge -= 1
                if charge <= 0:
                   del target.inventory['Technique Inv']['Charges'][player.name]
                print("Defense verified!")
                return defense, target
        else:
            print("No charge for defense")
            return False

    else:
        print("Defense verified!")
        if target.imbue:
            target.ce -= defense.act_cost + target.imbue['strength'] + target.imbue['speed']
        else:
            target.ce -= defense.act_cost
        return defense, target
    
# endregion

# region type increment
def type_increment(player, attack=None, defense=None, tools=None):
    buffs = {'attack': {'strength' : {}, 'speed' : {}}, 'defense': {'strength' : {}, 'speed': {}}}
    str_imbued = 0
    spd_imbued = 0
    if isinstance(player.imbue, int):
                str_imbued = player.imbue
                spd_imbued = player.imbue
    else:
                str_imbued = player.imbue['strength']
                spd_imbued = player.imbue['speed']
    if attack:
        print(f"Incrementing {attack.name} stats...")
        if attack.type == 'melee':
            if tools:
                for item in tools:
                    dmg = attack.strength + item.strength + player.strength + str_imbued
                    buffs['attack']['strength']['tool'] = item.strength
                    buffs['attack']['strength']['imbue'] = str_imbued
                    buffs['attack']['strength']['physical'] = player.strength
                    # playful cloud gets strength buffed based on both player strength and speed
                    # dragonbone gets strength buffed based on player speed 
                    speed = attack.speed + item.speed + player.speed + spd_imbued
                    buffs['attack']['speed']['physical'] = player.speed
                    buffs['attack']['speed']['imbue'] = spd_imbued
                player.imbue['strength'] = 0
                player.imbue['speed'] = 0
                return dmg, speed, buffs, tools
            else:
                dmg = attack.strength + str_imbued + player.strength
                speed = attack.speed + spd_imbued + player.speed
        
                # bf = black_flash_check(player) 
                # implement black flash counter to lobby feed and player
                # if bf:
                #     buffs['attack']['black flash'] = bf
                buffs['attack']['strength']['physical']= player.strength
                buffs['attack']['strength']['imbue'] = str_imbued
                buffs['attack']['speed']['imbue'] = spd_imbued
                buffs['attack']['speed']['physical'] = player.speed

        elif attack.type == 'projectile':
            dmg = attack.strength + str_imbued
            speed = attack.speed + spd_imbued
            buffs['attack']['strength']['imbue'] = str_imbued
            buffs['attack']['speed']['imbue'] = spd_imbued
        if isinstance(player.imbue, int):
            player.imbue=0
        else:
            player.imbue['strength'] = 0
            player.imbue['speed'] = 0
        return player, dmg, speed, buffs

    if defense:
        print(f"Incrementing {defense.name} stats...")
        if defense.type == 'tank' or defense.type == 'counter' or defense.type == 'dodge':
            
            defense_strength = defense.strength + str_imbued + player.strength
            buffs['defense']['strength']['physical'] = defense_strength
            # think about implementing different counter types i.e: 'counter melee' 'counter projectile' 'counter barrier'
            buffs['defense']['strength']['imbue'] = str_imbued
            defense_speed = defense.speed + spd_imbued + player.speed
            buffs['defense']['speed']['physical'] = defense_speed
            buffs['defense']['speed']['imbue'] = spd_imbued

            if tools:
                for item in tools:
                    defense_strength += item.strength
                    buffs['defense']['strength']['tool'] = item.strength
                    defense_speed += item.speed
                    buffs['defense']['speed']['tool'] = item.speed
                return player, defense_strength, defense_speed, buffs, tools
            
    
            return player, defense_strength, defense_speed, buffs
        if defense.type == 'heal':
            defense_strength = defense.strength + str_imbued + player.strength
            buffs['defense']['strength']['physical'] = player.strength
            buffs['defense']['strength']['imbue'] = str_imbued
            defense_speed = defense.speed + spd_imbued + player.speed
            buffs['defense']['speed']['physical'] = player.speed
            buffs['defense']['speed']['imbue'] = spd_imbued
                # else:
                #     defense_strength = defense.strength
                #     defense_speed = defense.speed

        else:
            defense_strength = defense.strength
            defense_speed = defense.speed

        return player, defense_strength, defense_speed, buffs
#endregion
      
# region visibility checks
def attack_visibility(target, attack):
    if attack:
        print(f"Accessing {target.name}'s visibility of incoming attack...")
        if target.technique == "Heavenly Restriction: Zero":        
                print(f"{target.name} can see {attack.name}")
                return False
        else:
            print(f"{target.name} can't see but could sense the activation of {attack.name}")
            return True       
        
        
def defense_visibility(player, target, attack, defense):          
    if defense:
        print(f"Accessing {player.name}'s visablity of target...")
        if player.technique == "Heavenly Restriction: Zero":
            print(f"{player.name} can see {target.name}")
            return False
        
        if attack.sure_hit:
            print(f"{player.name} can't see but will still hit {target.name}")
            return False
        
        if defense.invisible:
            aoe = attack.aoe
            if aoe > 10:
                aoe = 10
            rand = random.randint(aoe, 10)

            if rand == 10:
                print(f"{player.name} can't see but will still hit {target.name}")
                return False
            else:
                print(f"{player.name} can't see {target.name}")
                return True
#endregion

# region negate checks
def negate_check(target, dmg, defense_strength, attack=None, defense=None):
    print("Checking for negation...")
    # needs rework
    if attack: 
        print(f"{attack.name} negates {defense_strength} defense from {target.name}")
        return ("hit", dmg, target.hp<=0, target.max_hp <=0, target)
    
    if defense:
        print(f"{target.name} negates {dmg} damage from {attack.name}") 
        return ("negate", dmg, target.hp<=0, target.max_hp <=0, target)
# endregion

# region joke check
# def joke_check(player, target, answer1, answer2, answer3, choice, dmg, defense=None, attack=None):
#     if player.technique or target.technique == "Comedian":
#         if defense:
#             joke = defense.name
#             correct = random.choice([answer1, answer2, answer3])
#             if choice == correct:
#                 total_dmg = max(dmg - defense.strength, 0)
#                 target.hp -= total_dmg
#                 return("tank", total_dmg, target.hp <=0, target.max_hp <=0)
#endregion

# region tank check
def tank_check(target, attack, defense, dmg, speed, defense_strength, defense_speed, targ_invis, attack_negated, defense_negated, soul_defense=0):
    if targ_invis:
        dmg = 0
        print(f"{attack.name} missed {target.name} because they were invisable")
        return ("hit", dmg, target.hp<=0, target.max_hp<=0, target)
    
    if defense_negated:
        defense.strength = 0
        target_hp = target.hp
        target_maxhp = target.max_hp
        target, target_hp, target_maxhp, body_dmg = damage_target(target=target, defense=defense, dmg=dmg, soul=attack.soul)
        print(f"Attack negated {defense.name} dealing {body_dmg} dmg")
        return ("hit", body_dmg, target_hp <= 0, target_maxhp <=0, target)
    
    if attack_negated:
        dmg = 0
        print(f"{defense.name} negates {attack.name}")
        return ("hit", dmg, target.hp <= 0, target.max_hp <=0, target)

    if defense.type == 'heal' and defense_strength > dmg: #integrate healing into damage_target for bodyparts
            total_heal = (defense_strength - dmg)
            target.hp += total_heal
            if target.hp > target.max_hp:
                target.hp = target.max_hp
            print(f"{defense.name} was able to activate in time to tank {attack.name}. '{defense.name}' healed through {dmg} damage and healed {total_heal} hp to the defender")
            return ("rct", total_heal, target.hp <=0, target.max_hp <=0, target)
    
    
    if defense.act_speed >= attack.act_speed:
        # speed_diff = max(defense_speed - speed, 0)
        #                 # 100 / 1 (grade 4) = 100 but 100 // 5 (special grade) = 20    
        # attack_speed = speed/target.grade            
        #                     # 1200 / 20
        # reduction_multiplier = speed_diff//attack_speed
                    # 50 - 24
        total_dmg = max(dmg - defense_strength, 0)

        if total_dmg > 0:
            target_hp, target_maxhp, body_dmg = damage_target(target=target, defense=defense, dmg=total_dmg, soul=attack.soul)
            return ("hit", body_dmg, target_hp <= 0, target_maxhp <=0, target)
        else:
            return("tank", dmg, target.hp<=0, target.max_hp <=0, target)
    
    else:
            activation_difference = attack.act_speed - defense.act_speed
            total_dmg = max(dmg - defense_strength, 0)
            total_dmg = total_dmg * (activation_difference//target.grade)
            if total_dmg > 0:
                target_hp, target_maxhp, body_dmg = damage_target(target=target, defense=defense, dmg=total_dmg, soul=attack.soul)
            else:
                target_hp = target.hp
                target_maxhp = target.max_hp
                body_dmg = 0
            print(f"{defense.name} was able to activate in time to tank {attack.name}. {body_dmg} damage dealt, {dmg - total_dmg} damage tanked")
            return ("tank", body_dmg, target_hp <=0, target_maxhp <=0, target)
#endregion

# region counter check
def counter_check(target, player, defense, attack, dmg, speed, defense_strength, defense_speed, targ_invis, atk_invis, attack_negated, defense_negated):
    
    if defense.type == 'counter reflect':
        defense_strength = dmg

    if attack.sure_hit:
        if attack_negated:
            dmg = 0
            print(f"{defense.name} negated {attack.name}")
            return ("hit", dmg, target_hp<=0, target_maxhp<=0, target)
        else:
            target_hp, target_maxhp, body_dmg = damage_target(target=target, defense=defense, dmg=dmg, soul=attack.soul)
            print(f"{defense.name} was hit by sure hit {attack.name}")
            return ("hit", body_dmg, target_hp<=0, target_maxhp<=0, target)
    
    if atk_invis:
        target_hp, target_maxhp, body_dmg = damage_target(target=target, defense=defense, dmg=dmg, soul=attack.soul)
        print(f"{defense.name} couldn't counter because {attack.name} was invisible")
        return ("hit", body_dmg, target_hp<=0, target_maxhp<=0, target)
    
    if targ_invis:
        dmg = 0
        target_hp, max_hp, body_dmg = damage_target(target=target, defense=defense, dmg=defense_strength, soul=counter_soul)
        return ("counter", dmg, target.hp<=0, target.max_hp<=0, target)

    if attack_negated:
        dmg = 0
        print(f"{defense.name} negates {attack.name}. Effectively countered")
        return ("negate", dmg, target.hp<=0, target.max_hp<=0, target)

    if defense.act_speed > attack.act_speed and dmg !=0:
        speed_diff = max(defense_speed - speed, 0)
                # 100 / 1 (grade 4) = 100 but 100 // 5 (special grade) = 20    
        attack_speed = speed/target.grade            
                        # 1200 / 20
        reduction_multiplier = speed_diff//attack_speed
                    # 50 - 24
        total_dmg = dmg - reduction_multiplier
        
        target, target_hp, target_maxhp, body_dmg = damage_target(target=target, defense=defense, dmg=total_dmg, soul=attack.soul)
        print(f"{defense.name} was too slow to counter {attack.name}")
        return ("hit", body_dmg, target_hp <=0, target_maxhp <=0, target)
    
    if defense_negated:
        defense_strength = 0
        print(f"Attack negated {defense.name} dealing {dmg} dmg")
        return ("hit", dmg, target.hp <= 0, target.max_hp <=0, target)
    
    counter_dmg = defense_strength
    counter_soul = 0

    if target.equipped:
            items=[item for item in target.equipped]
            for item in items:
                counter_dmg += item.strength
                counter_soul = item.soul + defense.soul
                print(f"{item.name} adds {item.strength} to counter damage")
    player, target_hp, target_maxhp, body_dmg = damage_target(target=player, defense=defense, dmg=counter_dmg, soul=counter_soul)
    print(f"{defense.name} was able to counter {attack.name} for {counter_dmg} damage")
    return ("counter", body_dmg, player.hp <=0, player.max_hp <=0, player)
# endregion


# region dodge check
def dodge_check(target, defense, attack, dmg, speed, defense_strength, defense_speed, targ_invis, attack_negated, defense_negated):
    
    if attack_negated:  
        dmg = 0
        print(f"{defense.name} negated {attack.name}")
        return ("negated", dmg , target.hp<=0, target.max_hp<=0)

    if attack.sure_hit:
            print(f"{defense.name} was hit by sure hit {attack.name}")
            target_hp, target_maxhp, body_dmg = damage_target(target=target, defense=defense, dmg=reduced_dmg, soul=attack.soul)
            return ("hit", body_dmg, target_hp<=0, target_maxhp <=0)
    
    if targ_invis:
        dmg = 0
        print(f"{attack.name} could not target {target.name}")
        return ("dodge", dmg, target.hp<=0, target.max_hp<=0)

    if defense_negated:
        defense_strength=0
        print(f"{attack.name} negated {defense.name}. Target can still dodge")

    if defense_speed == 0:
        print(f"{defense.name} is 0 and was not able to dodge {attack.name}\n{dmg} damage taken")
        return ("hit", dmg, target.hp<=0, target.max_hp <=0)
    
    else:
        dmg = max(dmg - defense_strength, 0)

    if dmg == 0:
        print(f"{attack.name}'s damage is 0. Attack effectively dodged")
        return ("dodge", dmg, target.hp<=0, target.max_hp<=0, target)
    
    if defense.act_speed > attack.act_speed:
        print(f"Attack activated before defense\nCalculating speed diff of {defense.name} and {attack.name}\nDefense speed: {defense_speed}\nAttack speed: {dmg}")
        speed_gap = max(defense_speed - speed, 0)
                        # 100 / 1 (grade 4) = 100 but 100 // 5 (special grade) = 20    
        # print(f"Speed diff: {speed_diff}\nDividing by target grade")
        act_gap = defense.act_speed - attack.act_speed
        divider = act_gap + target.grade
        attack_speed = speed/divider     
                            # 1200 / 20
        # print(f"Total attack speed divided by target grade: {attack_speed}")
        # print(f"Dividing speed diff: {speed_diff} by attack speed: {attack_speed}")
        reduced_multiplier = speed_gap/attack_speed
                 # 50 - 24
        # print(f"Reduced multiplier: {reduced_multiplier}")
        total_dmg = dmg - reduced_multiplier
        target, target_hp, target_maxhp, body_dmg = damage_target(target=target, defense=defense, dmg=total_dmg, soul=attack.soul)
        return ("dodge", body_dmg, target_hp<=0, target_maxhp<=0, target)

    else: 
        print(f"Defense activated before attack\nCalculating speed diff between {attack.name} and {defense.name}")
                        #100        #1200     
        speed_gap = max(defense_speed - speed, 0)
                        #0//5
        attack_speed = speed_gap/target.grade

        if attack_speed != 0:
            
            reduced_dmg = max(dmg - defense_strength, 0) // attack_speed
                            # 50 - 24
            total_dmg = (reduced_dmg * attack.level)
            target_hp, target_maxhp, body_dmg = damage_target(target=target, defense=defense, dmg=total_dmg, soul=attack.soul)
            print(f"{defense.name} was able to dodge {attack.name}. There was a difference of {speed_gap} resulting in some damage of {total_dmg}")
            return ("dodge", body_dmg, target_hp<=0, target_maxhp<=0, target)
        
        else:
            reduced_dmg = max(dmg - defense_strength, 0)
            target_hp, target_maxhp, body_dmg = damage_target(target=target, defense=defense, dmg=reduced_dmg, soul=attack.soul)
            print(f"{defense.name} was able to dodge {attack.name}. There was a difference of {speed_gap} resulting in some damage of {reduced_dmg}")
            return ("dodge", body_dmg, target_hp<=0, target_maxhp<=0, target)
#endregion

# region summon check
def summon_check(name, type, tamed=False):
    print("Summoning " + name)
    if type == "shikigami":
        shikigami = [s for s in shikigami_list if s.name == name]
        shiki = shikigami[0]
        shiki.tamed = tamed
        if shikigami:
            print(f"Summoned: {type} {name}\nStrength: {shiki.strength}\nSpeed: {shiki.speed}\nTechnique: {shiki.technique}")
            return shiki
        return None
#endregion

# region domain clash
def domain_clash(target, player, defense, attack, dmg, speed, defense_strength, defense_speed, targ_invis, atk_invis, attack_negated, defense_negated):

    domain_type = attack.type
    targ_domain_type = defense.type
    
    if domain_type or targ_domain_type == 'open':
        print(f"{domain_type} vs {targ_domain_type} domain battle!")
        results = barrier_checks(target, player, defense, attack, dmg, speed, defense_strength, defense_speed, targ_invis, atk_invis, attack_negated, defense_negated)
        return results
    
    if attack.act_speed < defense.act_speed:
        print(f"{attack.name} broke {target.name}'s domain!")
        return 'defense broke'
    
    if attack.act_speed > defense.act_speed:
        print(f"{defense.name} broke {player.name}'s domain!")
        return 'attack broke'
    
    else:
        print(f"{player.name} vs {target.name} closed domain battle!") # is this possible? 
        results = barrier_checks(target, player, defense, attack, dmg, speed, defense_strength, defense_speed, targ_invis, atk_invis, attack_negated, defense_negated)
        return results
   #endregion 

# region barrier checks
def barrier_checks(player, target, attack, dmg, speed, defense, defense_strength):
        
        t_amp = False
        t_simple = False
        t_blossom = False
        t_basket = False
        t_domain = False

        print("Setting defense barrier type...")
        if defense.type == "amp":
            t_amp = True
        if defense.type == "simple":
            t_simple = True
        if defense.type == "blossom":
            t_blossom = True
        if defense.type == "basket":
            t_basket = True
        if defense.type == "open" or defense.type == "close":
            t_domain = True
        
        print("Calculating dmg...")
        if attack.type == "amp":
            dmg -= defense_strength
            target_hp, target_maxhp, body_dmg = damage_target(target=target, defense=defense, dmg=dmg, soul=attack.soul)
            return ("hit", body_dmg, target_hp <=0, target_maxhp <=0)
        
        if attack.type == "closed" or attack.type == "open":
            if t_domain:
                print("Domain clash (NOP)")
                # results = domain_clash()
                # return results
            
            elif t_basket:
                return("negate", body_dmg, target.hp<=0, target.max_hp <=0)
            
            elif t_amp:
                return ("negate", body_dmg, target.hp <=0, target.max_hp <=0)
            
            elif t_blossom:
                dmg-= defense_strength + defense.speed
                target_hp, target_maxhp, body_dmg = damage_target(target=target, defense=defense, dmg=dmg, soul=attack.soul)
                return ("negate", body_dmg, target_hp<=0, target_maxhp <=0)
            
            elif t_simple:
                return ("negate", dmg==0, target.hp<=0, target.max_hp <=0)

            else:  
                target_hp, target_maxhp, body_dmg = damage_target(target=target, defense=defense, dmg=dmg, soul=attack.soul)
                return ("hit", body_dmg, target_hp <=0, target_maxhp <=0)
        
        # if attack.type == "simple":
        #     target_hp, target_maxhp, body_dmg = damage_target(target=target, defense=defense, dmg=dmg, soul=attack.soul)
        #     return ("hit", body_dmg, target_hp <=0, target_maxhp <=0)
#endregion

#region Battle AOE
def battle_aoe_check(player, targets, attack_str=None, defense=None):
    target_amount = len(targets)
    results = []
    if attack_str:
        for target in targets:
            if target.hp > 0:
                result = battle_checks(player, target, attack_str, defense_str=target.defense)
                if result:
                    results.append(result)
            
            else:
                print(f"{target.name} is not within range of the AOE attack")
                return False
            
    if defense:
        for target in targets:
            defense = defense_verify(target, player, defense=defense,aoe=True)
            print(f"{target.name}'s defense set to {target.defense}")
            return defense
            
    return results
    
#endregion


# region test players
test_player1 = Player(
    name="Sukuna",
    entered="2023-10-01",
    level=10,
    max_hp=4000,
    max_ce=4000,
    strength=100,
    speed=100,
    technique="Sky Manipulation",
    playerclass="sorcerer",
    colony_id=1,
    xp=0,
    cgp=0,
    skp=0,
    user_id=0,
    grade=5,
    imbue={'strength': 50, 'speed': 50}
)

#test_player1.inventory['Technique Inv']['Charges'] = {"" : 1}

test_player2= Player(
    name="Gojo",
    entered="2023-10-01",
    level=10,
    max_hp=4000,
    max_ce=4000,
    strength=100,
    speed=100,
    technique="Limitless",
    playerclass="sorcerer",
    colony_id=1,
    xp=0,
    cgp=0,
    skp=0,
    user_id=0,
    grade=5,
    imbue={'strength': 50, 'speed': 50}
)

test_player3 = Player(
    name="Nobara",
    entered="2023-10-01",
    level=10,
    max_hp=1500,
    max_ce=1500,
    strength=10,
    speed=10,
    technique="Straw Doll",
    playerclass="sorcerer",
    colony_id=1,
    xp=0,
    cgp=0,
    skp=0,
    user_id=0,
    grade=3,
    imbue={'strength': 50, 'speed': 50}
)

#test_player3.inventory['Technique Inv']['Charges'] = {"Gojo" : 1}

test_player2.defense = "Infinity"
test_player3.defense = "Squeaky Hammer"

enemy = game.Reggie()
enemy.imbue = {'strength': 0, 'speed': 0}
#shiki = summon_check("Nue", "shikigami")

results = battle_checks(enemy, test_player3, "Knife Receipt", "Squeaky Hammer")
print(results)
print(results[0][4])
#endregion
