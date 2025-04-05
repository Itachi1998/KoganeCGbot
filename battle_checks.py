import game, random
from game import Player
from player_tech import technique_list
from cursed_tools import cursed_tools
# check if the player can use the attack before starting the checks



def get_move(player, attack=None, defense=None, tool=None): # Maybe this works?      
    tech = [tech for tech in technique_list if next(iter(tech)) == player.technique]
    if tool:
        new_tool = cursed_tools[tool]
        return new_tool

    if attack:
        new_attack = tech[0][player.technique][0]['Attack'][attack]
        return new_attack
    
    if defense:
        new_defense = tech[0][player.technique][1]["Defend"][defense]
        return new_defense
    


def attack_verify(player, attack):
    attack = get_move(player, attack=attack)

    if player.ce < attack.act_cost:
        print('not enough ce to use attack')
        return "no ce"
    
    if player.level < attack.level:
        print('not a high enough level to use attack')
        return "no lvl"
    
    else:
        player.ce -= attack.act_cost + player.imbue
        return attack
    

# check if the target can use the defense before starting the checks
def defense_verify(target, defense):
    defense = get_move(target, defense=defense)
    if target.ce < defense.act_cost:
        print('not enough ce to use defense')
        return "no ce"
    
    if target.level < defense.level:
        print('not a high enough level to use defense')
        return "no lvl"
    else:
        target.ce -= defense.act_cost + target.imbue
        return defense

def type_multiply(player, attack=None, defense=None):
    if attack:
        if attack.type == 'melee':
                if player.equipped:
                    items=[item for item in player.equipped ]
                    for item in items:
                        dmg = attack.strength + item.strength + player.strength + player.imbue
                        speed = attack.speed + item.speed + player.speed + player.imbue
                    return dmg, speed, items
                else:
                    dmg = attack.strength + player.imbue + player.strength
                    speed = attack.speed + player.imbue + player.speed
        else:
            dmg = attack.strength + player.imbue
            speed = attack.speed + player.imbue
        return dmg, speed 
    
    if defense:
        if defense.type == 'melee':
                defense_strength = defense.strength + player.imbue + player.strength
                speed = defense.speed + player.imbue + player.speed

                if player.equipped:
                    items=[item for item in player.equipped ]
                    for item in items:
                        defense_strength += item.strength
                        speed += item.speed
                    return defense_strength, speed, items

        else:
            defense_strength = defense.strength + player.imbue
            speed = defense.speed + player.imbue

        return defense_strength, speed

def negate_check(attack, target, dmg):
    if attack.negate:
            if attack.soul:
                target.max_hp -= attack.soul
            target.hp -= dmg
            return ("hit", dmg, target.hp<=0, target.max_hp <=0)
    
def joke_check(player, target, answer1, answer2, answer3, choice, dmg, defense=None, attack=None):
        if player.technique or target.technique == "Comedian":
             if defense:
                joke = defense.name
                correct = random.choice([answer1, answer2, answer3])
                if choice == correct:
                     total_dmg = max(dmg - defense.strength, 0)
                     target.hp -= total_dmg
                     return("tank", total_dmg, target.hp <=0, target.max_hp <=0)

def tank_check(target, attack, defense, dmg):
            defense.strength += target.imbue
            defense.speed += target.imbue
            if defense.act_speed > attack.act_speed:
                target.hp -= dmg
                if attack.soul:
                    target.max_hp -= attack.soul
                results = ("hit", dmg, target.hp <= 0, target.max_hp <=0)
                print(f"{defense.name} was not able to activate in time to tank {attack.name}")
                return results
            
            else:
                print(f"dmg {dmg} defense {defense.strength}")
                total_dmg = max(dmg - defense.strength, 0)
                target.hp -= total_dmg
                if attack.soul:
                    soul_dmg = max(attack.soul - defense.soul, 0)
                    target.max_hp -= soul_dmg
                results = ("tank", total_dmg, target.hp <=0, target.max_hp <=0)
                print(f"{defense.name} was able to activate in time to tank {attack.name}. {total_dmg} damage dealt, {dmg - total_dmg} damage tanked")
                return results
            

def counter_check(target, player, defense, attack, dmg):
            if defense.act_speed > attack.act_speed:
                target.hp -= dmg
                if attack.soul:
                    target.max_hp -= attack.soul
                print(f"{defense.name} was too slow to counter {attack.name}")
                return ("hit", dmg, target.hp <=0, target.max_hp <=0)
            
            else:
                
                if defense.soul:
                    player.max_hp -= defense.soul
               
                if defense.stun:
                    player.stun = defense.stun

                if defense.poison:
                    player.poison= defense.poison
                
                if defense.charge:
                    target.charge = target.charge
            
                counter_dmg = defense.strength # subtract player.imbue
                player.hp -= counter_dmg
                results = ("counter", counter_dmg, player.hp <=0, player.max_hp <=0)
                print(f"{defense.name} was able to counter {attack.name} for {counter_dmg}")
                return results

def dodge_check(target, defense, attack, dmg):
       # 8                  6
    if defense.act_speed > attack.act_speed:
                
                speed_diff = max(defense.speed - attack.speed, 0)
                                # 100 / 1 (grade 4) = 100 but 100 // 5 (special grade) = 20    
                attack_speed = attack.speed/target.grade            
                                    # 1200 / 20
                reduced_multiplier = speed_diff//attack_speed
                         # 50 - 24
                total_dmg = dmg - reduced_multiplier

                target.hp -= total_dmg
    
                target.max_hp -= attack.soul
    
                results = ("hit", total_dmg, target.hp<=0, target.max_hp <=0)
                print(f"{defense.name} was not able to dodge {attack.name}\n{total_dmg} damage taken\nspeed diff reduction {reduced_multiplier}")
                return results
    
    else: 
        print(f"Successfull defense dodge.\nCalculating speed diff between {attack.name} and {defense.name}")
                        #1000           500        
        speed_diff = max(attack.speed - defense.speed, 0)
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
            target.hp -= reduced_multiplier

            print(f"{defense.name} was able to dodge {attack.name}. There was a difference of {speed_diff} resulting in some damage of {total_dmg}")
            results = ("dodge", dmg, target.hp<=0, target.max_hp<=0)
            return

        else:
            print(f"There is no difference in speed or the defense speed was faster. {defense.name} was able to dodge {attack.name}.")
            results = ("dodge", dmg, target.hp<=0, target.max_hp<=0)
            return

def melee_checks(player, target, attack_str, defense_str):
    # check if the player can use the attack before starting the checks
    attack = attack_verify(player, attack_str)
    defense = defense_verify(target, defense_str)
    print(attack)
    print(defense)
    if not attack:
        return False
    if not defense:
        return False            
    print('Starting battle checks...')
    stack=player.stack
    charge=player.charge # this check should take place in the verify func right?
    inventory = player.inventory
    equipped = player.equipped
    dmg = 0
    speed = 0

# adds physical speed and strength to attack if it is melee


# the battle interaction is handled by this function
def battle_checks(player, target, attack_str, defense_str, aoe=None, targets=None):    
        attack = attack_verify(player, attack_str)
        defense = defense_verify(target, defense_str)
        print(attack)
        print(defense)
        if not attack:
            return False
        if not defense:
            return False            
        print('Starting battle checks...')
        stack=player.stack
        charge=player.charge # this check should take place in the verify func ?
        inventory = player.inventory
        equipped = player.equipped
        defense_negate=False
        attack_negate=False
        soul_dmg=0
        soul_defense=0
        dmg = 0
        speed = 0


        # check if the player can use the attack before starting the checks
        if player.equipped:
            dmg, speed, items = type_multiply(player, attack=attack)
            print(f"Attack {attack.name} has a base damage of {dmg} and speed of {speed}")
            if len(items) > 1:
                for item in items:
                    print(f"Attack {attack.name} has a base damage of {dmg} and speed of {speed} with item {item.name}")
                    if item.negates:

                        defense_negate=True
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
             dmg, speed = type_multiply(player, attack=attack)
             print(f"Attack {attack.name} has a base damage of {dmg} and speed of {speed}")
        

        if target.equipped:
            defense_strength, speed, items = type_multiply(target, defense=defense)
            print(f"Defense {defense.name} has a base damage of {defense_strength} and speed of {speed}")
            if len(items) > 1:
                for item in items:
                    print(f"Defense {defense.name} has a base damage of {defense_strength} and speed of {speed} with item {item.name}")
                    if item.negates:
                        attack_negate=True
                        print(f"{item.name} negates any attacks from {attack.name}")
                    if item.soul:
                        soul_defense += item.soul
                        print(f"{item.name} has a soul defense of {soul_defense}")
        else:

            defense_strength, speed = type_multiply(target, defense=defense)

            print(f"Defense {defense.name} has a base damage of {defense_strength} and speed of {speed}")
            if defense.negates:
                  attack_negate=True
                  print(f"{defense.name} negates any attacks from {attack.name}")
            if defense.soul:
                soul_defense += defense.soul
                print(f"{defense.name} has a soul damage of {soul_defense}")    
        
        
        if stack > 0:
            print(f"{attack.name} has a stack of {stack}")
            dmg = attack.strength + (speed * 2.4) 
            stack -= 1
            player.stack = stack

        if defense_negate:
            print(f"{attack.name} negates any defenses for {defense.name}")
            results= negate_check(attack, target, dmg)
            return results
        
     
    # negate check
        if attack_negate:
                print(f"{defense.name} negates any attacks from {attack.name}")
                return("negate", dmg, target.hp <= 0, target.max_hp <=0)

    # tank check
        if defense.type == 'tank':
            print(f"{defense.name} tank check against {attack.name}")
            results = tank_check(target, attack, defense, dmg)
            return results
        
    # counter check
        if defense.type == 'counter':
            results = counter_check(target, player, defense, attack, dmg)
            return results
                
    # dodge check
        if defense.type == 'dodge':
            results = dodge_check(target, defense, attack, dmg)
            return results            
        



test_player1 = Player(
     name="Uraume",
     level=10,
     max_hp=2000,
     max_ce=2000,
     strength=500,
     speed=500,
     technique="Ice Manipulation",
     playerclass="sorcerer",
     colony=1,
     xp=0,
     cgp=0,
     skp=0,
     user_id=0,
     grade=5,
     imbue=0,
)



test_player2= Player(
     name="Toji",
     level=10,
     max_hp=2000,
     max_ce=2000,
     strength=500,
     speed=500,
     technique="Heavenly Restriction: Zero",
     playerclass="sorcerer",
     colony=1,
     xp=0,
     cgp=0,
     skp=0,
     user_id=0,
     grade=5,
     imbue=0
)

results = battle_checks(test_player1, test_player2, "Frostbite", "Heavenly Body")

print(results)