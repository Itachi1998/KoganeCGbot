from player_tech import construction
from game import Player, Enemy

# Get the attack and defense dictionaries for the technique
attack_dict = construction['Construction'][0]['Attack'] # returns attack dictionary
defense_dict = construction['Construction'][1]['Defense'] # returns defense ditionary

def total_dmg(attack_strength, defense_strength)
     return (attack_strength - defense_strength)

def attack_checks(player, target, technique):
    attack = attack_dict[technique] 
    defense = target.defense
    if attack.level > player.grade:
        return (0, 'NA grade', attack)
    
    if attack.buffs:
        if 'strength' in attack.buffs:
            player.strength += attack.strength
        if 'speed' in attack.buffs:
             player.speed += attack.speed
        return (0, 'buff', attack)
    if target.ce >= target.defense.ce:
        defense = target.defense
    else:
         defense = None
    if player.imbued:
         attack.strength += player.imbued
         attack.speed += player.imbued
    if defense:
        speed_diff = defense.speed - attack.speed
            # 50               20
        if defense.speed > attack.speed:
            # 30            # 50 / 1 (grade 4)
            if speed_diff < defense.speed // target.grade:
                dmg = total_dmg(attack.strength, defense.strength)
                return (dmg, 'hit', attack)
            if defense.type == "dodge":
                return (0, 'dodge', attack)
            if defense.type == 'counter':
                return (defense.strength, 'counter', attack)
        else:
            dmg = total_dmg(attack.strength + speed_diff, defense.strength)
            return (dmg, 'hit', attack)
    else:
         return(attack.strength + attack.speed, 'hit', attack) 
    

def set_defense(player, defense):
     player.defense = defense
     return player.defense



def create_item(stats, name, player):
     

# Domain
# def threefold_affliction(player, target):
#       if player.ce < self.ce_cost:
#           results = (0, 'NA ce', False, [])
#           return results

#       if player.imbued < self.attack['Threefold Affliction']['imbue cost']:
#           results = (0, 'NA imbue', False, [])
#           return results

#       if player.ct_level < self.attack['Threefold Affliction']['ct lvl']:
#           results = (0, 'NA lvl', False,[])
#           return results
          
#       player.ce -= self.ce_cost
#       player.save_to_db()
#       sure_hit = self.attack['Threefold Affliction']['domain']
#       results = domain_check(self.attack[sure_hit], target, player)
#       return results

    
def perfect_sphere(player, target):
    attack = attack_dict['Perfect Sphere']
              
    if player.grade < attack.level:
         results = (0, 'NA level', attack)

    if player.ce < attack.ce_cost:
        results = (0, 'NA ce', attack)
        targets = targets
        return results, targets
        
    if player.ce < attack.ce_cost:
        results = (0, 'NA imbue', attack)
        targets = targets
        return results, targets

    player.ce -= attack.ce_cost

    if player.defense:
        if player.defense.negate:
             return (0, 'NA negated', attack)
        if player.defense.speed > attack.speed:
            if player.defense.type == "dodge":
                 return(0, 'miss', attack)
            if player.defense.type == 'counter':
                 dmg = player.defense.strength
                 return(dmg, 'counter', attack)
            else:
                 dmg = attack.strength // 2
                 total_dmg = player.defense.strength - dmg
                 return (total_dmg, 'hit slow', False)
        
        dmg = attack.strength + attack.speed
        def_num = player.defense.strength + player.defense.speed
        total_dmg = dmg - def_num
        if total_dmg <= 0:
                return (0, 'tank', attack)
        else:
            return (total_dmg, 'hit', attack)

    
def metal_shield(enemy, player, attack):
    defense = defense_dict["Metal shield"]
    if player.imbued < defense.ce_cost:
            results = (0, 'NA imbue', False, [])
            return results
    if player.ct_level < defense.level:
        results = (0, 'NA lvl', False, [])
        return results 
        
    player.ce -= defense.ce_cost
    player.save_to_db()
    results = defense_checks(defense, enemy, player, attack)
    return results

    
def butterfly_wings(enemy, player, attack):
      defense = defense_dict['Butterfly Wings']
      if player.imbued < defense.ce_cost:
              results = (0, 'NA imbue', False, [])
              return results

      player.ce -= defense.ce_cost
      player.save_to_db()
      results = defense_checks(defense, enemy, player, attack)
      return results


def bug_armor(enemy, player, attack):
    defense = defense_dict["Bug Armor"]

    if player.imbued < defense.ce_cost:
              return (False, "NA ce")

    player.ce -= defense.ce_cost
    player.save_to_db()
    results = defense_checks(defense, enemy, player, attack)
    return results
  
    
def ce( enemy, player, attack):         
    defense = 'CE'                    
    results = defense_checks(defense, enemy, player, attack, ce=player.ce)
    return results



def domain_check(sure_hit, target, player):
   try:
        print(f"{sure_hit} domain expansion check commencing")
        marks = {}
        dmg = sure_hit['dmg']
        if player.imbued > sure_hit['imbue cost']:
            dmg += player.imbued
        soul_dmg = 0
        drain = None
        stack = None
        stun = None
     
        if 'soul' in sure_hit.keys():
            soul_dmg = sure_hit['soul']
        if 'drain' in sure_hit.keys():
            drain = sure_hit['drain']
        if 'stack' in sure_hit.keys():
            stack = sure_hit['stack']
        if 'stun' in sure_hit.keys():
            stun = sure_hit['stun']
            
        if target.name in enemy_techniques:
                tech = Techniques(**target.technique)
                def_dict = tech.defense[target.defense]
                print(f"Defense Dictionary: {def_dict}")  # Debugging output to check def_dict content
                if 'negate' in def_dict.keys():
                    marks['def'] = def_dict
                    print(f"Negate found in defense, marks: {marks}")
                    return (dmg, 'negate', player.hp <= 0, marks)
                  
                def_numb = def_dict['def']
                def_soul = 0
                
                if 'soul' in def_dict.keys():
                    def_soul = def_dict['soul']
                    marks['def soul'] = def_soul
                    
                if 'aoe defense' in def_dict.keys():
                    def_numb = def_dict['aoe defense']['def']
                    marks['aoe defense']['def'] = def_numb
                    marks['aoe defense']['player'] = def_dict['aoe defense']['player']
                    if 'soul' in def_dict['aoe defense']:
                        def_soul = def_dict['aoe defense']['soul']
                        marks['aoe defense']['soul'] =  def_soul
                        
                marks['def'] = def_dict
                if soul_dmg >0:
                    dmg = max(0,(dmg + soul_dmg) - (def_numb + def_soul))
                else:
                    dmg = max(0, dmg-def_numb)
                
                target.hp -= dmg
                target.max_hp -= max(0, soul_dmg - def_soul)
                player.imbued = 0
                player.save_to_db()

                if dmg > 0:
                    if drain:
                        marks['drain'] = drain
                    if soul_dmg > 0:
                        marks['soul'] = soul_dmg - def_soul
                    if stack:
                        marks['stack'] = stack
                    if stun:
                        marks['stun'] = stun
                        
                    print(f"hit, {marks}")
                    print(f"Returning values: dmg={dmg}, hit status={'hit'}, target hp <= 0={target.hp <= 0}, marks={marks}")
                    return (dmg, 'hit', target.hp <= 0, marks)
                else:
                        print(f"domain tanked, {marks}")
                        return (dmg, 'tank', target.hp <=0, marks)
   except Exception as e:
       traceback.print_exc()
    

def attack_checks(attack, target, player, strength=None, stun=None, soul=None, stack=None, charge=None):
  try:
      print(f"Starting attack check")
      def_speed = None
      defense=None
      dmg = attack['dmg'] + player.imbued

      if strength:
          dmg += strength

      speed = player.imbued + attack['speed'] 

      soul_dmg = 0
      drain = None
      stack = None
      stun = None
      charge = None

      if soul:
          soul_dmg += soul + player.imbued

      if 'Physical' in attack.keys():
                dmg = attack['Physical']['dmg']
                if 'soul' in attack['Physical'].keys:
                    soul_dmg = attack['Physical']['soul']
                speed = attack['Physical']['speed']

      if target.name in enemy_techniques:
          def_name = target.defense
          defense = target.technique['defense'][def_name]

          def_num = defense['def'] 
          def_speed = defense['speed'] 

      else:
          attack['soul'] = soul_dmg
          attack['dmg'] = dmg
          t = None
          if isinstance(target, game.Enemy):
            t = Techniques(**target.technique) 
          else:
             t = get_cursed_technique(target.technique)
          if target.defense == None:
              target.defense = 'CE'
          defense = t.defense[target.defense]
          def_name = target.defense.replace(" ","_")
          defense_func = getattr(t, def_name.lower())
          results = defense_func(player, target, attack)
          return results

      if 'soul' in defense:
              soul_dmg -= defense['soul']

      dmg = max(0, dmg + soul_dmg) - defense['def']

      if def_speed > speed:

              defense_dict = {}
              if 'counter' in defense:
                  defense_dict['counter'] = defense['dmg']
              if 'soul' in defense:
                  defense_dict['soul'] = defense['soul']
                  soul_dmg -= defense['soul']
              if 'drain' in defense:
                  defense_dict['drain'] = defense['drain']
              if 'charge' in defense:
                  defense_dict['charge']  = defense['charge']

              if 'negate' in defense:
                  dmg = dmg + soul_dmg
                  player.hp -= dmg
                  player.max_hp -= soul_dmg
                  player.save_to_db()
                  return(dmg, 'negate', player.hp<=0, defense_dict)

              if 'counter' in defense:
                          dmg = defense['dmg']
                          soul_dmg = defense['soul']['dmg']
                          dmg += soul_dmg + target.imbued
                          if dmg > 0:
                              player.hp -= dmg 
                              player.max_hp -= soul_dmg
                              player.save_to_db()

                          return (dmg, 'counter' , player.hp <=0, defense_dict)
              else:
                      defense_dict = {'atk speed' : speed, 'def speed' : def_speed}
                      return (dmg, 'miss', player.hp<=0, defense_dict)

      else:

                  mark_dict = {}

                  if 'drain' in attack:
                      number = attack['drain']
                      mark_dict['drain'] = {'dmg' : number, 'turn' : number, 'target' : target.name}


                  if 'stack' in attack:

                      number = attack['stack']
                      mark_dict['stack'] = {'speed' : target.speed, 'turn' : number, 'target' : target.name}

                  if dmg > 0:
                      if 'negate' in attack:
                          dmg += soul_dmg
                          target.hp -= dmg
                          target.max_hp -= soul_dmg
                          return(dmg, 'negate', target.hp <=0, mark_dict)

                      if 'domain' in attack:
                          mark_dict = attack['domain']
                          return (dmg, 'domain', target.hp <=0, mark_dict)

                      target.hp -= dmg
                      target.max_hp -= soul_dmg

                      return(dmg, 'hit', target.hp<=0, mark_dict)

                  else:

                      return(dmg, 'tanked', target.hp<=0, mark_dict)

  except Exception as e:
      print(f"Exception in aoe check: {e}")
      traceback.print_exc()


def defense_checks(defense, enemy, player, attack, stack=None, charge=None, strength=None, stun=None, ce=None):
  try:  
              speed = None
              dmg = None
              atk_speed = None
              mark_dict = {}
              soul_dmg = 0
              if 'Physical' in attack:
                  attack= attack['Physical']

              dmg = attack['dmg']
              atk_speed = attack['speed']
              speed = defense['speed'] + player.imbued
              if atk_speed > speed:
                       if ce:               
                           defense_number = defense['def'] + ce // 5
                           player.ce -= (max(0, defense_number - 10))//player.ct_level
                           player.save_to_db()
                           defense['def'] = defense_number
                       if 'soul' in attack:
                           soul_dmg += attack['soul']
                       if 'soul' in defense:
                           soul_dmg -= defense['soul']
                       if 'drain' in attack:
                           mark_dict['drain'] = attack['drain']
                           dmg += mark_dict['drain']
                       if 'stack' in attack:
                           mark_dict['stack'] = {'turn':attack['stack']}
                       mark_dict['soul'] = soul_dmg
                       if 'charge' in attack:
                           charge = attack['charge']
                           sure_hit = attack['dmg']
                           mark_dict['charge'] = {'charge' : charge }
                       if 'negate' in attack:
                           player.hp -= dmg
                           player.max_hp -= dmg
                           player.imbued=0
                           player.save_to_db()
                           return (dmg, 'negate', player.hp<=0, mark_dict)

                       dmg = max(0, (dmg + soul_dmg) - defense['def'])
                       if dmg > 0:
                           player.hp -= dmg
                           player.max_hp -= soul_dmg
                           player.imbued=0
                           player.save_to_db()
                           return(dmg, "hit", player.hp<=0, mark_dict)
                       else:
                           return(dmg, 'tank', player.hp<=0, mark_dict)

              else:
                  mark_dict = {}
                  if 'counter' in defense:
                          if strength:
                              defense['dmg'] += strength
                          dmg = defense['dmg'] + player.imbued

                          mark_dict = {}
                          if stack:
                              mark_dict['stack'] = {'stack' : stack}
                          if charge:
                              mark_dict['charge'] = {'charge' : charge}
                          if stun:
                              mark_dict['stun'] = {'stun' : stun, "target" : enemy.name}
                          if 'soul' in defense.keys():
                              mark_dict['soul'] = {'soul' : defense['soul'], 'target' : enemy.name}
                          if 'drain' in defense.keys():
                             mark_dict['drain'] = {'drain' : defense['drain'], 'target' : enemy.name, 'turn' : defense['drain']}

                          return (dmg, 'counter', enemy.hp<=0, mark_dict)
                  if stack:
                      mark_dict['stack'] = {'stack' : stack}
                  if charge:
                      mark_dict['charge'] = {'charge' : charge}
                 
                  mark_dict = {'atk speed' : atk_speed, 'def speed' : defense['speed']}
                  print(f"Mark dictionary: {mark_dict}")

                  return(dmg, 'missed', player.hp<=0, mark_dict)
  except Exception as e:
      print(f"Exception in defense check: {e}")
      traceback.print_exc()
      

def aoe_check(targets, player, attack = None, def_aoe = None):
    try:
        result_list = []
        if def_aoe:
            print("AOE defense launched")
            def_numb = def_aoe['def'] // len(targets)
            def_speed = def_aoe['def'] // len(targets)
            for t in targets:
                if t.defense != def_aoe:
                    t.defense = def_aoe
                    t.speed = def_speed  
                    t.save_to_db()
                    result_list.append({'target': t.name, 'defense': t.defense})

        if attack:
            dmg = attack['dmg']
            speed = attack['speed']
            if strength:
                dmg += strength
            soul_dmg = 0
            atk_dict = {}
            if 'soul' in attack:
                atk_dict['soul'] = attack['soul']
                soul_dmg += attack['soul']
            if 'drain' in attack:
                atk_dict['drain'] = attack['drain']
            if 'charge' in attack:
                atk_dict['charge'] = attack['charge']
            if 'stack' in attack:
                atk_dict['stack'] = attack['stack']
            if 'stun' in attack:
                atk_dict['stun'] = attack['stun']
            
            length = len(targets)
            dmg = dmg // length
            speed = speed // length
            soul_dmg = soul_dmg // length
            print(f"AOE attack launched, targets: {length} dmg per target: {dmg}, soul dmg per target: {soul_dmg} - prior defense check")

            for t in targets:
                if t.name in enemy_techniques:
                    tech = Techniques(**t.technique)
                    defense_info = tech.defense[t.defense]
                    def_speed = defense_info['speed']
                    tank_amount = defense_info['def']
                    defense = defense_info
                else:
                    tech = get_cursed_technique(t.technique)
                    defense_func = getattr(tech, tech.defense.replace(" ", "_").lower())
                    defense = defense_func(player, t, attack)
                    result_list.append({'target': t.to_dict(), 'results': defense})
                if defense:
                    if def_speed > speed:
                        defensive_action = {'atk': atk_dict}
                        if 'counter' in defense:
                            defensive_action['counter'] = defense['counter']
                        if 'soul' in defense:
                            defensive_action['soul'] = defense['soul']
                        if 'drain' in defense:
                            defensive_action['drain'] = defense['drain']
                        if 'negate' in defense:
                            dmg=0
                            player.save_to_db()
                            result_list.append({'target': t.to_dict(), 'results': [dmg, 'negate', player.hp <= 0, defensive_action]})
                        if 'counter' in defense:
                            dmg = defense['dmg']
                            soul_dmg = defense['soul']
                            dmg += soul_dmg + t.imbued
                            player.hp -= dmg
                            player.save_to_db()
                            result_list.append({'target': t.to_dict(), 'results': [dmg, 'counter', player.hp <= 0, defensive_action]})
                        else:
                            defensive_action['tank'] = dmg
                            result_list.append({'target': t.to_dict(), 'results': [dmg, 'tank', t.hp <= 0, defensive_action]})
                    if defense['def'] > dmg:
                        soul_dmg -= defense.get('soul', 0)
                        t.hp -= soul_dmg
                        t.max_hp -= soul_dmg
                        atk_dict['soul'] = {'dmg': soul_dmg}
                        result_list.append({'target': t.to_dict(), 'results': [dmg, 'tank', t.hp <= 0, atk_dict]})
                    else:
                        t.hp -= dmg
                        result_list.append({'target': t.to_dict(), 'results': [dmg, 'hit', t.hp <= 0, atk_dict]})

        return (result_list, targets)
    except Exception as e:
        print(f"Exception in aoe check: {e}")
        traceback.print_exc()