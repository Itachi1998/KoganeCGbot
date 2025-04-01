import game, player_tech # doesn't work
from player_tech import limitless


# pull the currect attack/defense from the player/target and save its attributes to the attack/defense variable
attack = limitless["Attack"]["Blue"]  #'current player (technique)[attack][move]'
defense = limitless["Defense"]["Infinity"]  #'current target (technique)[defense][move]'
print(attack, defense)


# check if the player can use the attack before starting the checks
def attack_verify(player, attack):
    
    if player.ce < attack.act_cost:
        print('not enough ce to use attack')
        return
    
    if player.imbue < attack.act_cost:
        print('not enough ce imbued to use attack')
        return
    
    if player.level < attack.level:
        print('not a high enough level to use attack')
        return
    
    else:
        print('attack verified')
        defense_verify()


# check if the target can use the defense before starting the checks
def defense_verify(target, defense):
    
    if target.ce < defense.act_cost:
        print('not enough ce to use defense')
        return
    
    if target.imbue < defense.act_cost:
        print('not enough ce imbued to use defense')
        return
    
    if target.level < defense.level:
        print('not a high enough level to use defense')
        return
    
    else:
        print('defense verified')
        battle_checks()


# the battle interaction is handled by this function
def battle_checks(attack, target, player, strength=None, stun=None, soul=None, stack=None, charge=None):
    try:
        print('Starting battle checks...')

        speed=None
        dmg=None
        soul_dmg=None
        stack=1
        drain=0
        stun=0
        charge=None # this check should take place in the verify func right?
        def_strength=defense.strength
        def_speed=defense.speed

    # adds physical speed and strength to attack if it is melee
        if attack.type is 'melee':
            dmg = attack.strength + player.imbue + player.strength
            speed = attack.speed + player.imbue + player.speed
    
        if attack.type is 'projectile':
            dmg = attack.strength + player.imbue
            speed = attack.speed + player.imbue
    # multiplies the speed and dmg by the stack multiplier (projection sorcery) - default is 1 (no multiplier for any non-stack moves)
        if stack in attack:
            stack = player.stack
            dmg = dmg*stack
            speed = speed*stack

        if soul in attack:
            soul_dmg = attack.strength + player.imbue

        if stun in attack: # no need?
            stun = attack.stun

        if charge in attack: # no need?
            charge = player.charge 

    # if fast enough, reduces damage or completely nullifies it
        if target.type is 'tank':
            
            if def_speed < speed:
                target.hp -= dmg
                target.max_hp -= soul_dmg
                target.max_ce -= drain
                target.stunned = stun

            elif def_speed > speed:
                target.hp -= max(0,(dmg - def_strength))
                target.max_hp -= soul_dmg
                target.max_ce -= drain
                target.stunned = stun

            else:
                target.hp = target.hp

    # either takes full damage or takes none and does counter damage instead
        if target.type is 'counter':
            
            if def_speed < speed:
                target.hp -= dmg
                target.max_hp -= soul_dmg
                target.max_ce -= drain
                target.stunned = stun

            elif def_speed > speed:
                player.hp -= def_strength

            else:
                target.hp = target.hp

    # takes less damage the closer you are to dodging and none if dodged. reduction percentage ranges from (>0 - <1)
        if target.type is 'dodge':
     
            if def_speed < speed:
                reduction_multiplier = (def_speed/speed)
                reduction_amount = (dmg*reduction_multiplier)
                dmg = (-1)*(reduction_amount - dmg)
                target.hp -= dmg
                target.max_hp -= soul_dmg
                target.max_ce -= drain
                target.stunned = stun

            else:
                target.hp = target.hp

        
    except Exception as e:
        print(f'Battle checks failed because of the following exception: {e}')