import game, random
from summons import Mahoraga
from game import Player, Enemy, KingOfCurses
from player_tech import technique_list
from enemy_techs import enemy_techs
from cursed_tools import cursed_tools


# region get move
def get_move(player, attack=None, defense=None, tools=None):
    tech=None 
    is_player=False
    is_enemy=False

    if isinstance(player, Enemy):
        if player.name in enemy_techs:
            tech = enemy_techs[player.technique]
            is_enemy=True

    elif isinstance(player, Player):
            tech = [t for t in technique_list if next(iter(t)) == player.technique]
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

        if is_player:
            new_attack = tech[0][player.technique][0]['Attack'][attack]
            return new_attack
        
        if is_enemy:
            new_attack = tech[0]['Attack'][attack]
            return new_attack
    
    if defense:
        print(f"Setting defense '{defense}' for {player.name}")

        if is_player:
            new_defense= tech[0][player.technique][1]['Defend'][defense]
            return new_defense
        if is_enemy:
            new_defense = tech[1]['Defend'][defense]
            return new_defense


# region verify checks
def attack_verify(player, attack):
    attack = get_move(player, attack=attack)

    if player.ce < attack.act_cost:
        print('not enough ce to use attack')
        return "no ce"
    
    if player.level < attack.level:
        print('not a high enough level to use attack')
        return "no lvl"
    
    else:
        print("Attack verified!")
        player.ce -= attack.act_cost + player.imbue
        return attack
    

def defense_verify(target, defense):
    defense = get_move(target, defense=defense)
    if target.ce < defense.act_cost:
        print('not enough ce to use defense')
        return "no ce"
    
    if target.level < defense.level:
        print('not a high enough level to use defense')
        return "no lvl"
    else:
        print("Defense verified!")
        target.ce -= defense.act_cost + target.imbue
        return defense


# region type increment
def type_increment(player, attack=None, defense=None, tools=None):

    if attack:
        print(f"Incrementing {attack.name} stats...")

        if attack.type == 'melee':
            if tools:
                for item in tools:
                    dmg = attack.strength + item.strength + player.strength + player.imbue
                    speed = attack.speed + item.speed + player.speed + player.imbue
                    return dmg, speed, tools
            else:
                dmg = attack.strength + player.imbue + player.strength
                speed = attack.speed + player.imbue + player.speed
                
        else:
            dmg = attack.strength + player.imbue
            speed = attack.speed + player.imbue

        return dmg, speed
    
    if defense:
        print(f"Incrementing {defense.name} stats...")
        if defense.type == 'tank' or 'counter':
                defense_strength = defense.strength + player.imbue + player.strength
                defense_speed = defense.speed + player.imbue + player.speed
                if tools:
                    for item in tools:
                        defense_strength += item.strength
                        defense_speed += item.speed
                    return defense_strength, defense_speed, tools

        else:
            defense_strength = player.imbue + player.strength
            defense_speed = player.imbue + player.speed

        return defense_strength, defense_speed

      
# region visability checks
def attack_visability(target, attack):

    if attack:
        print(f"Accessing {target.name}'s visibility of incoming attack...")
        if target.technique == "Heavenly Restriction: Zero":        
                print(f"{target.name} can see {attack.name}")
                return False
        else:
            print(f"{target.name} can't see but could sense the activation of {attack.name}")
            return True       
        

def defense_visability(player, target, attack, defense):          
    if defense:
        print(f"Accessing {player.name}'s visablity of target...")
        if player.technique == "Heavenly Restriction: Zero":
            print(f"{player.name} can see {target.name}")
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
            

# region negate checks
def negate_check(target, dmg, defense_strength, attack=None, defense=None):
    print("Checking for negation...")

    if attack: 
        if attack.soul:
            target.max_hp -= attack.soul
        target.hp -= dmg
        print(f"{attack.name} negates {defense_strength} defense from {target.name}")
        return ("hit", dmg, target.hp<=0, target.max_hp <=0)
    
    if defense:
        print(f"{target.name} negates {dmg} damage from {attack.name}") 
        return ("negate", dmg, target.hp<=0, target.max_hp <=0)


# region joke check
def joke_check(player, target, answer1, answer2, answer3, choice, dmg, defense=None, attack=None):
    if player.technique or target.technique == "Comedian":
        if defense:
            joke = defense.name
            correct = random.choice([answer1, answer2, answer3])
            if choice == correct:
                    total_dmg = max(dmg - defense.strength, 0)
                    target.hp -= total_dmg
                    return("tank", total_dmg, target.hp <=0, target.max_hp <=0)


# region tank check
def tank_check(target, attack, defense, dmg, speed, defense_strength, defense_speed, targ_invis, attack_negated, defense_negated, soul_defense=0):
    if targ_invis:
        dmg = 0
        print(f"{defense.name} negated {attack.name} dealing {dmg} dmg")
        return ("hit", dmg, target.hp<=0, target.max_hp<=0)
    
    if defense_negated:
        defense_strength = 0
        print(f"Attack negated {defense.name} dealing {dmg} dmg")
        return ("hit", dmg, target.hp <= 0, target.max_hp <=0)
    
    if attack_negated:
        dmg = 0
        print(f"{defense.name} negates {attack.name}")

    if defense.act_speed > attack.act_speed:
        speed_diff = max(defense_speed - speed, 0)
                        # 100 / 1 (grade 4) = 100 but 100 // 5 (special grade) = 20    
        attack_speed = speed/target.grade            
                            # 1200 / 20
        reduction_multiplier = speed_diff//attack_speed
                    # 50 - 24
        total_dmg = dmg - reduction_multiplier
        target.hp -= total_dmg
        if attack.soul:
            target.max_hp -= attack.soul - soul_defense
        print(f"{defense.name} was not able to activate in time to tank {attack.name}")
        return ("hit", dmg, target.hp <= 0, target.max_hp <=0)
    
    else:
        print(f"dmg {dmg} defense {defense_strength}")
        total_dmg = max(dmg - defense_strength, 0)

        target.hp -= total_dmg
        if attack.soul:
            soul_dmg = max(attack.soul - soul_defense, 0)
            
            target.max_hp -= soul_dmg
        print(f"{defense.name} was able to activate in time to tank {attack.name}. {total_dmg} damage dealt, {dmg - total_dmg} damage tanked")
        return ("tank", total_dmg, target.hp <=0, target.max_hp <=0)
    

# region counter check
def counter_check(target, player, defense, attack, dmg, speed, defense_strength, defense_speed, targ_invis, atk_invis, attack_negated, defense_negated):
    if atk_invis:
        target.hp -= dmg
        print(f"{defense.name} couldn't counter because {attack.name} was invisable")
        return ("hit", dmg, target.hp<=0, target.max_hp<=0)
    
    if targ_invis:
        dmg = 0
        print(f"{defense.name} (invisable) was able to dodge {attack.name}")
        return ("counter", dmg, target.hp<=0, target.max_hp<=0)

    if attack_negated:
            dmg = 0
            print(f"{defense.name} negates {attack.name}")

    if defense.act_speed > attack.act_speed and dmg !=0:
        speed_diff = max(defense_speed - speed, 0)
                # 100 / 1 (grade 4) = 100 but 100 // 5 (special grade) = 20    
        attack_speed = speed/target.grade            
                        # 1200 / 20
        reduction_multiplier = speed_diff//attack_speed
                    # 50 - 24
        total_dmg = dmg - reduction_multiplier
        target.hp -= total_dmg
        if attack.soul:
            target.max_hp -= attack.soul
        
        print(f"{defense.name} was too slow to counter {attack.name}")
        return ("hit", dmg, target.hp <=0, target.max_hp <=0)
    
    if defense_negated:
        defense_strength = 0
        print(f"Attack negated {defense.name} dealing {dmg} dmg")
        return ("hit", dmg, target.hp <= 0, target.max_hp <=0)
    
    else:
        if defense.soul:
            player.max_hp -= defense.soul
        
        if defense.stun:
            player.stun = defense.stun

        if defense.poison:
            player.poison= defense.poison
        
        if defense.charge:
            target.charge = target.charge
            
        counter_dmg = defense_strength
            # subtract player.imbue ?
        if target.equipped:
            items=[item for item in target.equipped ]
            for item in items:
                counter_dmg += item.strength
                print(f"{item.name} adds {item.strength} to counter damage")        
        player.hp -= counter_dmg
        print(f"{defense.name} was able to counter {attack.name} for {counter_dmg} damage")
        return ("counter", counter_dmg, player.hp <=0, player.max_hp <=0)
        

# region dodge check
def dodge_check(target, defense, attack, dmg, speed, defense_speed, targ_invis, attack_negated, defense_negated):

    if targ_invis:
        dmg = 0
        print(f"{defense.name} (invisable) was able to dodge {attack.name}")
        return ("dodge", dmg, target.hp<=0, target.max_hp<=0)

    if attack_negated:  
        dmg = 0
        print(f"{defense.name} negated {attack.name}")

    if defense_negated:
        target.strength=0
        print(f"{attack.name} negated {defense.name}")

    if defense.act_speed >= attack.act_speed:

        print(f"Unsuccessful defense activation calculating speed diff of {defense.name} and {attack.name}\nDefense speed: {defense.speed}\nAttack speed: {attack.speed}")
        speed_diff = max(defense_speed - speed, 0)
                        # 100 / 1 (grade 4) = 100 but 100 // 5 (special grade) = 20    
        print(f"Speed diff: {speed_diff}\nDividing by target grade")
        act_diff = defense.act_speed - attack.act_speed
        divider = act_diff + target.grade
        attack_speed = speed/divider     
                            # 1200 / 20
        print(f"Total attack speed divided by target grade: {attack_speed}")
        print(f"Dividing speed diff: {speed_diff} by attack speed: {attack_speed}")
        reduced_multiplier = speed_diff/attack_speed
                 # 50 - 24
        print(f"Reduced multiplier: {reduced_multiplier}")
        total_dmg = dmg - reduced_multiplier 
        target.hp -= total_dmg
        if attack.soul:
            target.max_hp -= attack.soul
        results = ("hit", total_dmg, target.hp<=0, target.max_hp <=0)
        print(f"{defense.name} was not able to dodge {attack.name}\n{total_dmg} damage taken\nspeed diff reduction {reduced_multiplier}")
        return results


    else: 
        print(f"Successfull defense dodge.\nCalculating speed diff between {attack.name} and {defense.name}")
                        #1000           500        
        speed_diff = max(speed - defense_speed, 0)

        print(f"Speed difference of {attack.name} - {defense.name} is {speed_diff}")
                        #500//5
        attack_speed = speed_diff/target.grade         

        print(f"Final attack speed difference is {attack_speed}")
                                    # 2600 - 400 // 100
        if attack_speed != 0:
            
            print(f"Reduced multiplier calc: {attack.strength} - {defense.strength} // {attack_speed}")

            reduced_multiplier = (attack.strength - defense.strength) // attack_speed
                            # 50 - 24
            print(f"Multiplying reduced multiplier ({reduced_multiplier}) by attack level: {attack.level}")

            total_dmg = (reduced_multiplier * attack.level)

            target.hp -= total_dmg

            print(f"{defense.name} was able to dodge {attack.name}. There was a difference of {speed_diff} resulting in some damage of {total_dmg}")
            results = ("dodge", dmg, target.hp<=0, target.max_hp<=0)
            return

        else:
            print(f"There is no difference in speed or the defense speed was faster. {defense.name} was able to dodge {attack.name}.")
            results = ("dodge", dmg, target.hp<=0, target.max_hp<=0)
            return


# region battle_checks
def battle_checks(player, target, attack_str, defense_str, aoe=None, targets=None):    
        tools=None
        target_tools=None
        attack = attack_verify(player, attack_str)
        defense = defense_verify(target, defense_str)
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
        charge=player.charge # this check should take place in the verify func ?
        defense_negated=False
        attack_negated=False
        soul_dmg=0
        soul_defense=0
        dmg = 0
        speed = 0
    
    # tool checks
        if tools:
            dmg, speed, items = type_increment(player, attack=attack, tools=tools)  
            for item in items:
                print(f"Attack {attack.name} has a base damage of {dmg} and speed of {speed} with item {item.name}")
                if item.negates:
                    defense_negated=True
                    print(f"{item.name} negates any defenses for {defense.name}")

                if item.soul:                         
                    soul_dmg += item.soul
                    print(f"{item.name} has a soul damage of {soul_dmg}")

                if item.charge:
                    charge += item.charge
                    print(f"{item.name} has a charge of {item.charge}")

                if item.poison:
                    player.poison = item.poison
                    print(f"{item.name} has a poison of {item.poison}")

        else:
            dmg, speed = type_increment(player, attack=attack)
            print(f"Attack {attack.name} has a base damage of {dmg} and speed of {speed}")
        
        if target_tools:
            defense_strength, defense_speed, items = type_increment(defense=defense, tools=target_tools)
         
            for item in items:
                print(f"Defense {defense.name} has a base damage of {defense_strength} and speed of {defense_speed} with item {item.name}")
                if item.negates:
                    attack_negated=True
                    print(f"{item.name} negates any attacks from {attack.name}")
                if item.soul:
                    soul_defense += item.soul
                    print(f"{item.name} has a soul defense of {soul_defense}")

        else:
            defense_strength, defense_speed = type_increment(target, defense=defense)
            print(f"Defense {defense.name} has a base defense of {defense_strength} and speed of {defense_speed}") 
    
    # visability checks
        atk_invis=None
        targ_invis=None

        if attack.invisable:
            atk_invis = attack_visability(target, attack)

        if defense.invisable:
            targ_invis = defense_visability(target, attack)

    # negate checks
        if defense.negates:
            attack_negated=True
        
            if attack_negated:
                results = negate_check(target, dmg, defense_strength, defense=defense)
                return results
        
        if attack.negates:
            defense_negated=True
        
            if defense_negated:
                results= negate_check(target, dmg, defense_strength, attack=attack)
                return results

    # soul/stack checks
        if defense.soul:
            soul_defense += defense.soul
            print(f"{defense.name} has a soul strength of {soul_defense}") 
    
        if stack > 0:
            print(f"{attack.name} has a stack of {stack}")
            dmg = dmg + (speed * 2.4) 
            stack -= 1
            player.stack = stack


    # tank check
        if defense.type == 'tank':
            print(f"{defense.name} 'tank check' against {attack.name}...")
            results = tank_check(target, attack, defense, dmg, speed, defense_strength, defense_speed, targ_invis, attack_negated, defense_negated, soul_defense=soul_defense)
            return results
        
        
    # counter check
        if defense.type == 'counter':
            print(f"{defense.name} 'counter check' against {attack.name}...")
            results = counter_check(target, player, defense, attack, dmg, speed, defense_strength, defense_speed, targ_invis, atk_invis, attack_negated, defense_negated)
            return results
                

    # dodge check
        if defense.type == 'dodge':
            print(f"{defense.name} 'dodge check' against {attack.name}...")
            results = dodge_check(target, defense, attack, dmg, speed, defense_speed, targ_invis, attack_negated, defense_negated)
            return results            
        

# region test players
test_player1 = Player(
    name="Toji",
    level=10,
    max_hp=4000,
    max_ce=4000,
    strength=300,
    speed=300,
    technique="Straw Doll",
    playerclass="sorcerer",
    colony=1,
    xp=0,
    cgp=0,
    skp=0,
    user_id=0,
    grade=5,
    imbue=0
)

test_player2= Player(
    name="Gojo",
    level=10,
    max_hp=4000,
    max_ce=4000,
    strength=100,
    speed=100,
    technique="Limitless",
    playerclass="sorcerer",
    colony=1,
    xp=0,
    cgp=0,
    skp=0,
    user_id=0,
    grade=5,
    imbue=200
)


sukuna=KingOfCurses()     #player1       player2        attack        defense
results = battle_checks(test_player1, test_player2, "Resonance", "Blue")
print(results)