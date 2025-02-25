from old_techniques import Techniques, enemy_techniques, get_cursed_technique, get_enemy_cursed_technique

import random, traceback, game



class StarRage(Techniques):

  rarity = 5

  def __init__(self):
    super().__init__(
      "StarRage",
      1,
      {"Virtual mAss": {'dmg': 500, 'speed': 200, 'soul' :100, 'ct lvl': 1, 'imbue cost': 25},
       "Garuda Canon": {'dmg': 400, 'speed': 250, 'soul' : 50, 'aoe' : 3, 'ct lvl': 2, 'imbue cost': 25}, 
       "Black Hole" : {'dmg' : 999, 'speed': 500, 'ct lvl': 5, "imbue cost": 100, 'aoe': 5}}, #suicide
      {"Garuda": {'def': 500, 'speed': 375, 'ct lvl': 1, 'imbue cost': 30},
       "Density": {'def': 900, 'speed': 700, 'ct lvl': 3, 'imbue cost': 50}, 
       'CE' : {'def' : 100, 'speed' : 100, 'ct lvl' : 1, 'imbue cost' : 0}},
      0,
      20,
      "<:starrage:1278555247740190720>")


  def virtual_mass(self, player, target):
    if player.ce < self.ce_cost:
      results = (0, 'NA ce', False, [])
      return results


    if player.imbued < self.attack['Virtual mAss']['imbue cost']:
      results = (0, 'NA imbue', False, [])
      return results

    if player.ct_level < self.attack['Virtual mAss']['ct lvl']:
        results = (0, 'NA lvl', False,[])
        return results
    self.attack['Virtual mAss']['dmg'] += player.attack
    self.attack['Virtual mAss']['speed'] += player.speed
    player.ce -= self.ce_cost
    player.save_to_db()
    results = attack_checks(self.attack['Virtual mAss'], target, player, soul=self.attack['Virtual mAss']['soul'])
    return results


  def garuda_canon(self, player, targets):
    if player.ce < self.ce_cost:
      results = (0, 'NA ce', False, [])
      targets = targets
      return results, targets


    if player.imbued < self.attack['Garuda Canon']['imbue cost']:
      results = (0, 'NA imbue', False, [])
      targets = targets
      return results, targets


    player.ce -= self.ce_cost
    player.save_to_db()
    results, targets = aoe_check(targets, player, attack=self.attack['Garuda Canon'])
    print(f"results and targets for Garuda Canon \n{results} {targets}")
    return results, targets
  

  def black_hole(self, player, targets):
    if player.ce < self.ce_cost:
      results = (0, 'NA ce', False, [])
      targets = targets
      return results, targets


    if player.imbued < self.attack['Black Hole']['imbue cost']:
      results = (0, 'NA imbue', False, [])
      targets = targets
      return results, targets


    player.ce -= self.ce_cost
    player.save_to_db()
    results, targets = aoe_check(targets, player, attack=self.attack['Black Hole'])
    print(f"results and targets for Black Hole \n{results} {targets}")
    return results, targets

  def garuda(self, enemy, player, attack):
    if player.ce < self.ce_cost:
      results = (0, 'NA ce', False, [])
      return results

    if player.imbued < self.defense['Garuda']['imbue cost']:
      results = (0, 'NA imbue', False, [])
      return results

    player.ce -= self.ce_cost
    player.save_to_db()
    results = defense_checks(self.defense['Garuda'], enemy, player, attack)
    return results

  def density(self, enemy, player, attack):
    if player.ce < self.ce_cost:
      results = (0, 'NA ce', False, [])
      return results

    if player.imbued < self.defense['Density']['imbue cost']:
      results = (0, 'NA imbue', False, [])
      return results

    player.ce -= self.ce_cost
    player.save_to_db()
    results = defense_checks(self.defense['Density'], enemy, player, attack)
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