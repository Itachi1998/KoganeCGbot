import game
from player_tech import technique_list
# check if the player can use the attack before starting the checks

enemy_list=[e() for e in game.Enemy.__subclasses__()]

def get_move(player, attack=None, defense=None):
    tech = [tech for tech in technique_list if next(iter(tech)) == player.technique]
    if attack:
        attack = tech[0]["Attack"][attack]
        return attack
    if defense:
        defense= tech[0]["Defense"][defense]
        return defense
    


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
            if defense.act_speed < attack.act_speed:
                target.hp -= dmg
                if attack.soul:
                    target.max_hp -= attack.soul
                results = ("hit", dmg, target.hp <= 0, target.max_hp <=0)
                return results
            
            else:
                total_dmg = max(dmg - defense.strength, 0)
                target.hp -= total_dmg
                if attack.soul:
                    soul_dmg = max(attack.soul - defense.soul, 0)
                    target.max_hp -= soul_dmg
                results = ("tank", total_dmg, target.hp <=0, target.max_hp <=0)
                return results
            

def counter_check(target, player, defense, attack, dmg):
            if defense.act_speed < attack.act_speed:
                target.hp -= dmg
                if attack.soul:
                    target.max_hp -= attack.soul
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
            
                counter_dmg = defense.strength - player.imbue
                player.hp -= counter_dmg
                results = ("counter", counter_dmg, player.hp <=0, player.max_hp <=0)
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
    
                return results
    
    else:

        results = ("dodge", dmg, target.hp<=0, target.max_hp<=0)
        return
     
          
                
# the battle interaction is handled by this function
def battle_checks(player, attack, target, defense):    
        attack = attack_verify(player,  attack)
        attack.imbue += player.imbue
        defense = defense_verify(target, defense)
        defense.imbue += target.imbue
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
        dmg, speed = type_multiply(player, attack)
        if stack > 0:
            dmg = attack.strength + (attack.speed * 2.4) 
            stack -= 1
            player.stack = stack

        if attack.negate:
            results= negate_check(attack, target, dmg)
            return results
        
    # if fast enough, reduces damage or completely nullifies it
        if defense.negate:
                return("negate", dmg, target.hp <= 0, target.max_hp <=0)
    
    # tank check
        if defense.type is 'tank':
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

    