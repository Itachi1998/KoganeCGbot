import game
from game import Player
from player_tech import technique_list

# check if the player can use the attack before starting the checks
def get_move(player, attack=None, defense=None):
    tech = [tech for tech in technique_list if next(iter(tech)) == player.technique]
    if attack:
        new_attack = tech[0][player.technique][0]['Attack'][attack]
        return new_attack
    if defense:
        new_defense= tech[0][player.technique][1]["Defend"][defense]
        return new_defense
    

def attack_verify(player,attack ):
    attack = get_move(player, attack=attack)

    if player.ce < attack.act_cost:
        print('not enough ce to use attack')
        return "no ce"
    
    if player.level < attack.level:
        print('not a high enough level to use attack')
        return "no lvl"
    
    else:
        player.ce -= attack.act_cost + attack.imbue
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
        target.ce -= defense.act_cost + defense.imbue
        return defense

def type_multiply(player, attack):
    if attack.type is 'melee':
            dmg = attack.strength + attack.imbue + player.strength
            speed = attack.speed + attack.imbue + player.speed
    else:
        dmg = attack.strength + attack.imbue
        speed = attack.speed + attack.imbue

    return dmg, speed

def negate_check(attack, target, dmg):
    if attack.negate:
            if attack.soul:
                target.max_hp -= attack.soul
            target.hp -= dmg
            return ("hit", dmg, target.hp<=0, target.max_hp <=0)
    
def tank_check(target, attack, defense, dmg):
            defense.strength += defense.imbue
            defense.speed += defense.imbue
            if defense.act_speed > attack.act_speed:
                target.hp -= dmg
                if attack.soul:
                    target.max_hp -= attack.soul
                results = ("hit", dmg, target.hp <= 0, target.max_hp <=0)
                print(f"{defense.name} was not able to activate in time to tank {attack.name}")
                return results
            
            else:
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
        print(f"Reduced multiplier calc: {attack.strength} - {defense.strength} // {attack_speed}")
        reduced_multiplier = (attack.strength - defense.strength) // attack_speed
                         # 50 - 24
        print(f"Multiplying reduced multiplier ({reduced_multiplier}) by attack level: {attack.level}")
        
        total_dmg = (reduced_multiplier * attack.level)
        target.hp -= reduced_multiplier

        print(f"{defense.name} was able to dodge {attack.name}. There was a difference of {speed_diff} resulting in some damage of {total_dmg}")
        results = ("dodge", dmg, target.hp<=0, target.max_hp<=0)
        return
     
          
                
# the battle interaction is handled by this function
def battle_checks(player, target, attack_str, defense_str):    
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
        dmg = type_multiply(player, attack)

        if stack > 0:
            dmg = attack.strength + (attack.speed * 2.4) 
            stack -= 1
            player.stack = stack

        if attack.negates:
            print(f"{attack.name} negates any defenses for {defense.name}")
            results= negate_check(attack, target, dmg)
            return results
        
    # if fast enough, reduces damage or completely nullifies it
        if defense.negates:
                print(f"{defense.name} negates any attacks from {attack.name}")
                return("negate", dmg, target.hp <= 0, target.max_hp <=0)
    
    # tank check
        if defense.type is 'tank':
            print(f"{defense.name} tank check against {attack.name}")
            results = tank_check(target, attack, defense, dmg)
            return results
    # counter check
        if defense.type is 'counter':
            results = counter_check(target, player, defense, attack, dmg)
            return results
                
    # takes less damage the closer you are to dodging and none if dodged. reduction percentage ranges from (>0 - <1)
        if defense.type is 'dodge':
            results = dodge_check(target, defense, attack, dmg)
            return results            


test_player1 = Player(
     name="Gojo",
     level=10,
     max_hp=2000,
     max_ce=2000,
     strength=500,
     speed=500,
     technique="Limitless",
     playerclass="sorcerer",
     colony=1,
     xp=0,
     cgp=0,
     skp=0,
     user_id=0,
     grade=5     
)
test_player2= Player(
     name="Sukuna",
     level=10,
     max_hp=2000,
     max_ce=2000,
     strength=500,
     speed=500,
     technique="Shrine",
     playerclass="reincarnate",
     colony=1,
     xp=0,
     cgp=0,
     skp=0,
     user_id=0,
     grade=5
)


results = battle_checks(test_player1, test_player2, "Hollow Purple", "Air Hop")

print(results)