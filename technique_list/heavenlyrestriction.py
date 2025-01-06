from techniques import Techniques, enemy_techniques, get_cursed_technique, get_enemy_cursed_technique

import random, traceback, game

##Technique attack results format -------- (damage, (tank, miss, hit), killed
##Technique defense results format ------- (defense, (block, dodge, counter), killed)

class HeavenlyRestriction(Techniques):
    
    rarity = 5

    def __init__(self):
        super().__init__(
            "Heavenly Restriction",
            1,
            {"Heavenly Fist": {"dmg": 100, "speed": 300, 'ct lvl' : 1, 'soul' : 5, 'imbue cost' : 0},
            "Heavenly Kick": {"dmg": 100, "speed": 300, 'soul' : 5, 'ct lvl' : 1, 'imbue cost' : 0},
            "Yeet Car": {"dmg": 100, "speed": 500, 'ct lvl' : 1, 'imbue cost' : 0}, 
            "Sneak Attack": {"dmg":650, "speed": 600, 'ct lvl' : 4, 'soul' : 50, 'stun' : 1, 'imbue cost' : 0},
            "Flash Step": {"dmg" : 100, "speed" : 850, 'ct lvl' : 3, 'stun' : 2, 'imbue cost' : 0}, 
             'Pebble Impact' : {'dmg' : 100, 'stun' : 1, 'speed' : 300, 'aoe' : 5, 'ct lvl' : 1, 'imbue cost' : 0}},
            {"Heavenly Body": {"def": 200, "speed": 10, "dmg" : 50, 'ct lvl' : 1, 'imbue cost' : 0},
            "Precognition": {"def": 50, "speed": 800, "dmg" : 200, 'ct lvl' : 5, 'imbue cost' : 0},
            "Disappear": { "def":50, "speed" : 400, 'dmg' : 150, 'ct lvl' : 3, 'counter' : True, 'imbue cost' : 0, 'negate' : True},
             "Air Hop" : {'def' : 50, 'speed' : 900, 'ct lvl' : 5, 'imbue cost' : 0}}, 
            0, 
            0, 
            "<:toji_heavenlyrestriction:1275288686497370173>")

    def flash_step(self, player, target):
        if player.ct_level < self.attack['Flash Step']['ct lvl']:
            return (0, 'NA lvl', target.hp<=0)
        self.attack['Flash Step']['dmg'] += player.attack
        self.attack['Flash Step']['speed'] += player.speed
        results = attack_checks(self.attack['Flash Step'], target, player)
        return results

    def sneak_attack(self, player, target):
        self.attack['Sneak Attack']['dmg'] += player.attack
        self.attack['Sneak Attack']['speed'] += player.speed
        results = attack_checks(self.attack['Sneak Attack'], target, player, soul=self.attack['Sneak Attack']['soul'])
        return results
    
    def heavenly_fist(self, player, target):
        if player.ct_level < self.attack['Heavenly Fist']['ct lvl']:
            return (0, 'NA lvl', target.hp<=0)
        self.attack['Heavenly Fist']['dmg'] += player.attack
        self.attack['Heavenly Fist']['speed'] += player.speed
        results = attack_checks(self.attack['Heavenly Fist'], target, player, soul=self.attack['Heavenly Fist']['soul'])
        return results

    def pebble_impact(self, player, targets):
        if player.ct_level < self.attack['Pebble Impact']['ct lvl']:
            return (0, 'NA lvl', False)
        self.attack['Pebble Impact']['dmg'] += player.attack
        results, targets = aoe_check(targets, player, attack=self.attack['Pebble Impact'])
        print(f"results and targets for liquid metal \n{results}\n{targets}")
        return results, targets
    


    def heavenly_kick(self, player, target):
        if player.ct_level < self.attack['Heavenly Kick']['ct lvl']:
            return (0, 'NA lvl', target.hp<=0)
        self.attack['Heavenly Kick']['dmg'] += player.attack
        self.attack['Heavenly Kick']['speed'] += player.speed
        results = attack_checks(self.attack['Heavenly Kick'], target, player, soul=self.attack['Heavenly Kick']['soul'])
        return results


    def heavenly_body(self, enemy, player, attack):
        if player.ct_level < self.defense['Heavenly Body']['ct lvl']:
            return (0, 'NA lvl', False)
        self.defense['Heavenly Body']['def'] += player.attack
        self.defense['Heavenly Body']['speed'] += player.speed
        results = defense_checks(self.defense['Heavenly Body'], enemy, player, attack)
        return results

    def yeet_car(self, player, target):
        if player.ct_level < self.attack['Yeet Car']['ct lvl']:
            return (0, 'NA lvl', target.hp<=0)
        self.attack['Yeet Car']['dmg'] += player.attack
        self.attack['Yeet Car']['speed'] += player.speed
        results = attack_checks(self.attack['Yeet Car'], target, player)
        return results
        

    def air_hop(self, enemy, player, attack):
          if player.ct_level < self.defense['Air Hop']['ct lvl']:
              return (0, 'NA lvl', False)
          self.defense['Air Hop']['speed'] += player.speed
          results = defense_checks(self.defense["Air Hop"], enemy, player, attack)
          return results

    
    def precognition(self, enemy, player, attack):
          if player.ct_level < self.defense['Precognition']['ct lvl']:
              return (0, 'NA lvl', False)
          self.defense['Precognition']['dmg'] += player.attack
          self.defense['Precognition']['speed'] += player.speed
          results = defense_checks(self.defense["Precognition"], enemy, player, attack)
          return results


    def disappear(self, enemy, player, attack):
          if player.ct_level < self.defense['Disappear']['ct lvl']:
              return (0, 'NA lvl', False)
          self.defense['Disappear']['speed'] += player.speed
          results = defense_checks(self.defense["Disappear"], enemy, player, attack)
          return results


    def ce(self, enemy, player, attack):
        self.defense['Heavenly Body']['def'] += player.attack
        self.defense['Heavenly Body']['speed'] += player.speed
        results = defense_checks(self.defense['Heavenly Body'], enemy, player, attack, ce=0)
        return results


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
          t = get_cursed_technique(target.technique)
          if target.defense == None:
              if target.technique == "Heavenly Restriction":
                  target.defense = 'Heavenly Body'
              else:
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


def aoe_check(targets, player, attack = None, def_aoe = None, strength=None):
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