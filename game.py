import json, traceback
from typing import Union, List, Optional
import enum, random, sys
from copy import deepcopy
from cogs.battle import Target
import old_techniques

#currencies:
# CGP = CULLING GAME POINTS - Points used to buy items from the shop
# SKP = SKILL POINTS - Points used to level up Skillsets
# XP = EXPERIENCE POINTS - Points that level you up and level up your cursed technique 


#this is where we will create most of the functionaliy for our characters and enemies
class GameMode(enum.IntEnum):
    Roam = 1 #Roam status for when player does nothing
    Pve = 2 #Pve status for when player begins a PvE fight
    Pvp = 3 #Pvp status for when player begins a PvP fight earn more xp from killing players, team up against stronger players, team battles, earn higher points
    Q = 4 # for when the player is in a queue


# Parent class for the Player and Enemy Subclasses
class Actor:
    def __init__(self, name: str, level:int, hp: int, max_hp: int, ce: int, max_ce: int, strength: int, speed: int, xp: int, cgp: int, technique: str, playerclass: str):
        self.name=name
        self.level=level
        self.hp=hp
        self.max_hp = max_hp
        self.ce = ce
        self.max_ce = max_ce
        self.strength = strength
        self.speed = speed,
        self.xp = xp,
        self.cgp=cgp,
        self.technique = technique
        self.playerclass= playerclass
    def __repr__(self):
        return f"{self.name} - HP: {self.hp}, XP: {self.xp}, CGP: {self.cgp}, Technique: {self.technique}"


    # sukuna.physical_attack_checks(gojo, gojo.defense)
    # def physical_attack_checks(self, target, attack, defense, **kwargs):
    #     try:
    #         print(f"{self.name} attacks {target.name}")
    #         speed = self.speed + attack.speed # 100
    #         strength = self.strength= + attack.strength
    #         bf = attack.bf
    #         def_speed = target.speed + defense.speed # 50
    #         def_strength = target.strenght + defense.strength
    #         speed_buff_percentage = (def_speed / speed) * 100 # 75+ to have a chance to dodge
    #         if speed_buff_percentage > 100:
    #              return(0, "dodge")
    #         else:
    #                                         # 0-15
    #             result = random.randint(0, speed_buff_percentage)
    #             if result > 75:
    #                 return (0, "dodge")
        
    #         damage = strength - def_strength

    #         if damage > 0:
    #              if attack.stun:
    #                  target.stun = attack.stun
    #                  target.save_to_db()
    #              return (damage, "hit", target.hp <= 0, bf)

    #         elif damage <= 0:
    #              return (damage, 'tank')
            
    #     except Exception as e:
    #         print(f"Error in physical_attack_checks: {e}")
     
   
    # def use_technique(self, technique, move, target, defense):
    #     name = technique.name
    #     domain = technique.domain
    #     maximum = technique.maximum
    #     rct = technique.rct
    #     attack_type = technique.type
    #     defense_type = defense.type
        
    #     if attack_type == "melee":
    #          pass
    #     if attack_type == "ranged":
    #         pass
    #     if attack_type == "curse":
    #         pass
    #     if attack_type == "domain":
    #         pass
    #     if attack_type == "maximum":
    #         pass
    #     if attack_type == "shikigami":
    #         pass
    #     if attack_type = 'mechabot':
    #         pass
    #     elif attack_type == None:
    #         print("No attack type")
    #         return False
        
    #     # if move == "attack":
    #     #     atr = None
    #     #     atk = None
    #     #     t=None
    #     #     if isinstance(self, Enemy):
    #     #         t= old_techniques.Techniques(**self.technique)
    #     #         atk = t.attack[technique]
    #     #         target_tech = old_techniques.get_cursed_technique(target.technique)
    #     #         if target.defense is not None:
    #     #             def_name = technique.replace(" ", "_")
    #     #             def_func = getattr(target_tech, def_name.lower())
    #     #             results = def_func(self, target, atk)
    #     #             return results
                    
    #     #         else:
    #     #             def_name = 'ce'
    #     #             def_func = getattr(target_tech, def_name.lower())
    #     #             results = def_func(self, target, atk)
                    
    #     #     else:
    #     #         t = old_techniques.get_cursed_technique(self.technique)
    #     #     print(f"{self.name} launching attack {technique}")
    #     #     atr = technique.lower()
    #     #     atr = atr.replace(" ","_")
    #     #     atk = getattr(t, atr)
    #     #     results=None
            
    #     #     if target:
    #     #         results = atk(self, target)
                
    #     #     if targets:
    #     #         results, targets =atk(self, targets)
    #     #         if targets:
    #     #          return results, targets
    #     #         else:
    #     #             return results
   
    #     #     return results
            
    #     # if move == "defense":
    #     #         lobdat = dynamo.read_lobby(host, colony_id = self.colony)
    #     #         t = old_techniques.get_cursed_technique(self.technique)
    #     #         self.defense=technique
    #     #         technique = technique.replace(" ", "_")
    #     #         if targets:
    #     #             defense_func = getattr(t, technique.lower())
    #     #             results, targets = defense_func(self, targets)
    #     #             return results, targets
    #     #         else:
    #     #             defense_func = getattr(t, technique.lower())
    #     #             results = defense_func(target, self, attack)
    #     #             return results
                
    
    #     def use_cursed_tool(self, tool: dict, **kwargs):
    #         if tool[type] == 'melee':
                 
        
    #     def domain(self, **kwargs):
    #          pass
     




class Enemy(Actor):

    def __init__(self, name, level, hp, max_hp, ce, max_ce, strength, speed, xp, cgp, technique, playerclass, **kwargs):
        super.__init__(self, name, level, hp, max_hp, ce, max_ce, strength, speed, xp, cgp, technique,  playerclass)
        for k,v in kwargs:
             if k == "colony" and isinstance(v, int):
                  self.colony = v
             if k == "grade" and isinstance(v, str):
                  self.grade = v
             if k == "killed" and isinstance(v, bool):
                  self.killed = v
             if k == "timer" and isinstance(v, int):
                  self.timer = v
             if k == "tamed" and isinstance(v, tuple):
                   self.tamed= v
             if k == "equipped" and isinstance(v, list):
                   self.equipped = v
             if k == "shikigami" and isinstance(v, list):
                   self.shikigami = v
             if k == "killby" and isinstance(v, dict):
                    self.killby = v
            
    def __repr__(self):
        return f"Enemy: {self.name} - HP: {self.hp}, XP: {self.xp}, CGP: {self.cgp}, Technique: {self.technique} - in colony: {self.colony}"

class Player(Actor):
    level_cap = 200
    def __init__(self, name, level, hp, max_hp, ce, max_ce, strength, speed, xp, cgp, technique, playerclass, **kwargs):
         super.__init__(self, name, level, hp, max_hp, ce, max_ce, strength, speed, xp, cgp, technique, playerclass)
         for k,v  in kwargs:
              if k == "colony" and isinstance(v, int):
                   self.colony = v
              if k == "skp" and isinstance(v, int): # skill points
                   self.skp = v
              if k == "ct_level" and isinstance(v, int): # ct level
                   self.ct_level = v
              if k == "hr" and isinstance(v, str): # type of heavenly restriction
                   self.hr = v
              if k == "shikigami" and isinstance(v, list): # list of shikigami 
                   self.shikigami = v
              if k == "curses" and isinstance(v, list): # list of tamed curses
                   self.curses= v
              if k == "bots" and isinstance(v, list): # list of remote bots 
                   self.bots = v
              if k == "souls" and isinstance(v, list): # list of souls
                    self.souls = v
              if k == "killed" and isinstance(v, bool): # if dead or not
                   self.killed = v
              if k == "equipped" and isinstance(v, list): # equipped items that can be used in battle
                   self.equipped = v
              if k == "inventory" and isinstance(v, list): # stored items 
                   self.inventory= v
              if k == "bindvows" and isinstance(v , dict): # binding vows
                    self.bindvows = v
              if k == "addedrules" and isinstance(v, dict): # rules
                    self.addedrules = v
              if k == "six_eyes" and isinstance(v, bool): # 6 eyes
                   self.six_eyes = v
              if k == "clan" and isinstance(v, str): # clan if they're part of one
                   self.clan = v
              

    def __repr__(self):
        return f"Character: {self.name} - HP: {self.hp}, XP: {self.xp}, CGP: {self.cgp}, Technique: {self.technique} - belonging to user_id: {self.user_id} - in colony: {self.colony}"

    
    # def get_grade(self):
    #     level = self.level
    #     if self.level >= 1 and self.level < 10:
    #         return "Grade 4"
    #     elif self.level >= 10 and self.level < 20:
    #         return "Grade 3"
    #     elif self.level >= 20 and self.level < 40:
    #         return "Grade 2"
    #     elif self.level >= 40 and self.level < 60:
    #         return "Grade 1"
    #     else:
    #         return "Special Grade"

    # def store(self, item):
    #     if item in self.equipment:
    #         self.inventory.append(item)
    #         self.equipment.remove(item)
    #         self.save_to_db()
    #         return True
    #     else:
    #         print("You don't have that item!")
    #         return False

    # def equip(self, item):
    #         if item in self.inventory:
    #             self.inventory.remove(item)
    #             self.equipment.append(item)
    #             self.save_to_db()
    #             return True
    #         else:
    #             print("Item not owned")
    #             return False


    # #spawn a shikigami, curse, mechabot, or ultimate mechabot
    # def spawn(self, **kwargs):
    #     self.curse = []
    #     self.shikigami = []
    #     self.mechabot = []
    #     self.ultimateMechabot = []

    #     for k, v in kwargs.items():
    #         try:
    #             if k == 'Shikigami':
    #                 self.shikigami.append([{k:v}])
    #                 return True
    #             if k == 'Curse':
    #                 self.curse.append([{k:v}])
    #                 return True
    #             if k == 'Mechabot':
    #                 self.mechabot.append([{k:v}])
    #                 return True
    #             if k == 'UltimateMechabot':
    #                 self.ultimateMechabot.append([{k:v}])
    #                 return True
    #             if k == 'ShadowInventory':
    #                 self.inventory.append({k:v})
    #                 return True
    #             self.save_to_db()

    #         except Exception as e:
    #             print(f"Failed to spawn {k} {e} due to {e}")
    #             return False
        
            
            

    # def level_up(self, xp_needed):

    #     if self.level >= self.level_cap:
    #         self.level = self.level_cap
    #         self.save_to_db()
    #         return (False, self.level, self.xp) #if the player has reached the level cap, they will no longer level up, and will no longer gain skill points

    #     if self.xp >= xp_needed:
    #         while self.xp >= xp_needed:
                    
    #                 self.level += 1 # If the players xp is greater than or equal to the xp needed to level up, they will level up

    #                 if self.level < 10: # If the players level is under 10, they will gain 2 skill points 
    #                     self.skp += 2
    #                 if self.level > 10: # If the players level is over 10, they will gain 4 skill points
    #                     self.skp += 4
    #                 if self.level > 50: # If the players level is over 50, they will gain 6 skill points
    #                     self.skp += 6
    #                 if self.level > 100: # If the players level is over 100, they will gain 8 skill points
    #                     self.skp += 8
    #                 if self.level > 180: # If the players level is over 180, they will gain 10 skill points per level
    #                     self.skp += 10
                    
    #                 grade = self.get_grade() # Use the calss method get_grade to determine the players grade

    #                 # Set player CT level per grade

    #                 if 'Grade 4' in grade:
    #                             self.ct_level = 1
    #                 if 'Grade 3' in grade:
    #                             self.ct_level = 2
    #                 if 'Grade 2' in grade:
    #                             self.ct_level = 3
    #                 if 'Grade 1' in grade:
    #                             self.ct_level = 4
    #                 if 'Special Grade' in grade:
    #                             self.ct_level = 5

    #                 self.save_to_db()
    #                 xp_needed = self.ready_level_up()[1]
    #                 if self.xp >= xp_needed:
    #                     continue
    #                 else:
    #                     break
    #         return (True, self.level, self.skp)
    #     return (False, self.level, self.xp)
        
    # def ready_level_up(self): # Method that returns xp needed for next level up
    #     level_cap = self.level_cap
    #     if self.level == level_cap:
    #         return (False, self.level)
    #     xp_needed = self.level * 5 # Start with the base XP needed being the players level multiplied by 5
    #     if self.level > 10: 
    #         xp_needed = self.level * 10 
    #     if self.level > 20:
    #         xp_needed = (self.level) * 12 
    #     if self.level > 30:
    #         xp_needed = (self.level) * 14 
    #     if self.level > 40:
    #         xp_needed = (self.level) * 16 
    #     if self.level > 50:
    #         xp_needed = (self.level) * 18 
    #     if self.level > 60:
    #         xp_needed = (self.level) * 20
    #     if self.level > 80:
    #         xp_needed = (self.level) * 22
    #     if self.level > 100:
    #         xp_needed = (self.level) * 24
    #     if self.level > 120:
    #         xp_needed = (self.level) * 26
    #     if self.level > 140:
    #         xp_needed = (self.level) * 28
    #     if self.level > 160:
    #         xp_needed = (self.level) * 30
    #     if self.level > 180:
    #         xp_needed = (self.level) * 32
    #     return (self.xp >= xp_needed, xp_needed)

    # def save_to_db(self):
    #     save_player(self) #the imported save_player method from the database file

    # def run(self, target: dict):
    #     self_speed = self.speed + self.imbued  #add the players imbued speed to their speed
    #     target_speed = target.speed + target.imbued #add the targets imbued speed to their speed
    #     if self_speed > target_speed:
    #         chance = random.randint(0, (200 - (self_speed - target_speed)))
    #         if chance < 5:
    #             return False
    #         else:
    #             return True

    # def pve(self, colony_id: int) -> Union[List['Enemy'], 'Enemy']:
    #     pass
    #TODO implement the pve method to return a list of enemies or a single enemy based on the players level and colony_id and colony events
        # colony = dynamo.read_colony(colony_id)
        # enemies = colony['ai'][0]
        # enemy = None
        # enemy_list = []
        # for e in enemies:
        #     name = e.replace(" ", "")
        #     for i in Enemy.__subclasses__():
        #         if i.__name__.lower() == name.lower(): # Corrected a match condition
        #             if i.min_level <= self.level and i.min_level >= self.level-100:
        #                 enemy_list.append(i())
        # enemies = []
        # enemy = random.choice(enemy_list)           
        # if enemy.name == "Grade 4":
        #     enemies = [deepcopy(enemy), deepcopy(enemy), deepcopy(enemy), deepcopy(enemy), deepcopy(enemy)]
        # elif enemy.name == "Grade 3":
        #     enemies = [deepcopy(enemy), deepcopy(enemy), deepcopy(enemy), deepcopy(enemy)]
        # elif enemy.name == "Grade 2":
        #     enemies = [deepcopy(enemy), deepcopy(enemy), deepcopy(enemy)]
        # elif enemy.name == "Grade 1":
        #     enemies = [deepcopy(enemy), deepcopy(enemy)]
        # elif enemy.name == "Kechi":
        #     eso = Eso()
        #     enemies = [deepcopy(enemy),deepcopy(eso)]
        # elif enemy.name == "Eso":
        #     kechi = Kechi()
        #     enemies = [deepcopy(enemy), deepcopy(kechi)]
        # elif enemy.name == "Mahito" or "Jogo" or "Dagon" or "Hanami":
        #     list = [1, 2, 3, 4]
        #     choice = random.choice(list)
        #     if choice == 1:
        #          enemies = [deepcopy(enemy)]
        #     if choice == 2:
        #         if enemy.name == 'Mahito':
        #             enemies = [deepcopy(enemy), deepcopy(Jogo())]
        #         if enemies == 'Hanami':
        #             enemies = [deepcopy(enemy), deepcopy(Jogo())]
        #         if enemy.name == 'Jogo':
        #                 enemies = [deepcopy(enemy), deepcopy(Hanami())]
        #         if enemy.name == "Dagon":
        #             enemies = [deepcopy(enemy), deepcopy(Jogo())]
        #     if choice == 3:
        #         if enemy.name == 'Mahito':
        #             enemies = [deepcopy(enemy), deepcopy(Jogo()), deepcopy(Hanami())]
        #         if enemy.name == 'Hanami':
        #             enemies = [deepcopy(enemy), deepcopy(Jogo()), deepcopy(Dagon())]
        #         if enemy.name == 'Jogo':
        #                 enemies = [deepcopy(enemy), deepcopy(Hanami()), deepcopy(Mahito())]
        #         if enemy.name == "Dagon":
        #             enemy_list = [deepcopy(enemy), deepcopy(Jogo()), deepcopy(Hanami())]
        #     if choice == 4:
        #         if enemy.name == 'Mahito':
        #             enemies = [deepcopy(enemy), deepcopy(Jogo()), deepcopy(Hanami()), deepcopy(Dagon())]
        #         if enemy.name == 'Hanami':
        #             enemies = [deepcopy(enemy), deepcopy(Jogo()), deepcopy(Dagon()), deepcopy(Mahito())]
        #         if enemy.name == 'Jogo':
        #                 enemies = [deepcopy(enemy), deepcopy(Hanami()), deepcopy(Mahito()), deepcopy(Dagon())]
        #         if enemy.name == "Dagon":
        #             enemies = [deepcopy(enemy), deepcopy(Jogo()), deepcopy(Hanami()), deepcopy(Mahito())]

        # elif enemy.name == "King Of Curses":
        #     uraume = Uraume()
        #     list = [1, 2]
        #     choice = random.choice(list)
        #     if choice == 1:
        #         enemies = [deepcopy(enemy), deepcopy(uraume)]
                
        # else:
            
        #     enemies = [enemy]
            
        # return enemies
        
        
## ENEMY CLASSES 
## SUBCLASS OF ENEMY CLASS
        
class Grade4_Bugfly(Enemy):
    def __init__(self, **kwargs):
        super.init(name="Bugfly", level=1, hp=15, max_hp=15, ce=20, max_ce=20, strength=20, speed=40, xp=10, cgp=1, technique="Bugfly", playerclass="curse")
        for k, v in kwargs:
             if k == "qunatity" and isinstance(v, int):
                  self.quantity = v
             if k == "killed" and isinstance(v, dict):
                  self.killed=v
             if k == "killcount" and isinstance(v, dict):
                  self.killcount=v
             if k == "colony" and isinstance(v, int):
                  self.colony = v

            
class  Grade4_Floatjelly(Enemy):
    def __init__(self, **kwargs):
        super.init(name="FloatJelly", level=1, hp=20, max_hp=20, ce=20, max_ce=20, strength=20, speed=20, xp=10, cgp=1, technique="Floatjelly", playerclass="curse")
        for k, v in kwargs:
             if k == "qunatity" and isinstance(v, int):
                  self.quantity = v
             if k == "killed" and isinstance(v, dict):
                  self.killed=v
             if k == "killcount" and isinstance(v, dict):
                  self.killcount=v
             if k == "stun" and isinstance(v, int):
                    self.stun = v
             if k == "colony" and isinstance(v, int):
                  self.colony = v

class Grade4_Flymouth(Enemy):
    min_level= 1
    def __init__(self, **kwargs):
        super.init(name="Flymouth", level="1", hp=30, max_hp=30, ce=20, max_ce=20, strength=10, speed=20, xp=10, cgp=1, technique="Flymouth", playerclass="curse")
        for k, v in kwargs:
             if k == "qunatity" and isinstance(v, int):
                  self.quantity = v
             if k == "killed" and isinstance(v, dict):
                  self.killed=v
             if k == "killcount" and isinstance(v, dict):
                    self.killcount=v
             if k == "poison" and isinstance(v, tuple):
                    self.poison = v 
             if k == "colony" and isinstance(v, int):
                  self.colony = v
               
            


class Grade3_Backhand(Enemy):

    def __init__(self, **kwargs):
        super.init(name=:"Backhand", level=1, hp=150, max_hp=150, ce=100, max_ce=100, strength=80, speed=120, xp=50, cgp=1, technique="Backhand", playerclass="curse")
        for k, v in kwargs:
             if k == "qunatity" and isinstance(v, int):
                  self.quantity = v
             if k == "killed" and isinstance(v, dict):
                  self.killed=v
             if k == "killcount" and isinstance(v, dict):
                    self.killcount=v
             if k == "colony" and isinstance(v, int):
                  self.colony = v

class Grade3_Furrpede(Enemy):
    def __init__(self, **kwargs):
        super.init(name="Furrpede", level=1, hp=200, max_hp=200, ce=50, max_ce=50, strength=100, speed=50, xp=50, cgp=1, technique="Furrpede", playerclass="curse")
        for k, v in kwargs:
             if k == "qunatity" and isinstance(v, int):
                  self.quantity = v
             if k == "killed" and isinstance(v, dict):
                  self.killed=v
             if k == "killcount" and isinstance(v, dict):
                    self.killcount=v
             if k == "poison" and isinstance(v, tuple):
                    self.poison = v 
             if k == "colony" and isinstance(v, int):
                  self.colony = v


class Grade3_AnxiousEars(Enemy):
    def __init__(self, **kwargs):
        super.init(name="Anxious Ears", level=1, hp=250, max_hp=250, ce=200, max_ce=200, strength=50, speed=50, xp=100, cgp=1, technique="AnxiousEars", playerclass="curse")
        for k, v in kwargs:
             if k == "qunatity" and isinstance(v, int):
                  self.quantity = v
             if k == "killed" and isinstance(v, dict):
                  self.killed=v
             if k == "killcount" and isinstance(v, dict):
                    self.killcount=v
             if k == "stun" and isinstance(v, int):
                  self.stun = v 
             if k == "colony" and isinstance(v, int):
                  self.colony = v


class Grade2_Stinkaspor(Enemy):
    def __init__(self, **kwargs):
        super.init(name="Stinkaspor", level=10, hp=350, max_hp=350, ce=350, max_ce=350, strength=150, speed=150, xp=200, cgp=1, technique="Stinkaspor", playerclass="curse")
        for k, v in kwargs:
             if k == "qunatity" and isinstance(v, int):
                  self.quantity = v
             if k == "killed" and isinstance(v, dict):
                  self.killed=v
             if k == "killcount" and isinstance(v, dict):
                    self.killcount=v
             if k == "poison" and isinstance(v, tuple):
                    self.poison = v 
             if k == "colony" and isinstance(v, int):
                  self.colony = v
             


class Grade2_Monkeybrain(Enemy):
    def __init__(self, **kwargs):
        super.init(name="Monkeybrain", level=10, hp=300, max_hp=300, ce=350, max_ce=350, strength=150, speed=150, xp=200, cgp=1, technique="Monkeybrain", playerclass="curse")
        for k, v in kwargs:
             if k == "qunatity" and isinstance(v, int):
                  self.quantity = v
             if k == "killed" and isinstance(v, dict):
                  self.killed=v
             if k == "killcount" and isinstance(v, dict):
                    self.killcount=v
             if k == "stun" and isinstance(v, dict):
                  self.stun=v
             if k == "colony" and isinstance(v, int):
                  self.colony = v



class Grade1_Orbmaster(Enemy):
    def __init__(self, **kwargs):
        super.init(name="OrbMaster", level=10, hp=400, max_hp=400, ce=500, max_ce=500, strength=200, speed=300, xp=400, cgp=1, technique="Orbmaster", playerclass="curse")
        for k, v in kwargs:
             if k == "killed" and isinstance(v, dict):
                  self.killed=v
             if k == "killcount" and isinstance(v, dict):
                    self.killcount=v
             if k == "stun" and isinstance(v, dict):
                  self.stun = v
             if k == "colony" and isinstance(v, int):
                  self.colony = v

class Grade1_Charger(Enemy):
    def __init__(self, **kwargs):
            super.init(name="Charger", level=10, hp=400, max_hp=400, ce=400, max_ce=400, strength=400, speed=400, xp=400, cgp=1, technique="Triplebackhand", playerclass="curse")
            for k, v in kwargs:
                if k == "qunatity" and isinstance(v, int):
                    self.quantity = v
                if k == "killed" and isinstance(v, dict):
                    self.killed=v
                if k == "killcount" and isinstance(v, dict):
                        self.killcount=v
                if k == "poison" and isinstance(v, tuple):
                        self.poison = v 
                if k == "colony" and isinstance(v, int):
                    self.colony = v


class SpecialGrade_FingerBearer(Enemy):
    def __init__(self, **kwargs):
        super.init(name="Flymouth", level=1, hp=30, max_hp=30, ce=20, max_ce=20, strength=10, speed=20, xp=10, cgp=1, technique="Triplebackhand", playerclass="curse")
        for k, v in kwargs:
             if k == "qunatity" and isinstance(v, int):
                  self.quantity = v
             if k == "killed" and isinstance(v, dict):
                  self.killed=v
             if k == "killcount" and isinstance(v, dict):
                    self.killcount=v
             if k == "poison" and isinstance(v, tuple):
                    self.poison = v 
             if k == "colony" and isinstance(v, int):
                  self.colony = v


class SpecialGrade_Obstacle(Enemy):
    def __init__(self, **kwargs):
        super.init(name="Flymouth", level=1, hp=30, max_hp=30, ce=20, max_ce=20, strength=10, speed=20, xp=10, cgp=1, technique="Triplebackhand", playerclass="curse")
        for k, v in kwargs:
             if k == "qunatity" and isinstance(v, int):
                  self.quantity = v
             if k == "killed" and isinstance(v, dict):
                  self.killed=v
             if k == "killcount" and isinstance(v, dict):
                    self.killcount=v
             if k == "poison" and isinstance(v, tuple):
                    self.poison = v 
             if k == "colony" and isinstance(v, int):
                  self.colony = v


class SpecialGrade_DisasterFlame(Enemy):
        def __init__(self, **kwargs):
        super.init(name="Flymouth", level=1, hp=30, max_hp=30, ce=20, max_ce=20, strength=10, speed=20, xp=10, cgp=1, technique="Triplebackhand", playerclass="curse")
        for k, v in kwargs:
             if k == "qunatity" and isinstance(v, int):
                  self.quantity = v
             if k == "killed" and isinstance(v, dict):
                  self.killed=v
             if k == "killcount" and isinstance(v, dict):
                    self.killcount=v
             if k == "poison" and isinstance(v, tuple):
                    self.poison = v 
             if k == "colony" and isinstance(v, int):
                  self.colony = v



class SpecialGrade_NatureSpirit(Enemy):
        def __init__(self, **kwargs):
        super.init(name="Flymouth", level=1, hp=30, max_hp=30, ce=20, max_ce=20, strength=10, speed=20, xp=10, cgp=1, technique="Triplebackhand", playerclass="curse")
        for k, v in kwargs:
             if k == "qunatity" and isinstance(v, int):
                  self.quantity = v
             if k == "killed" and isinstance(v, dict):
                  self.killed=v
             if k == "killcount" and isinstance(v, dict):
                    self.killcount=v
             if k == "poison" and isinstance(v, tuple):
                    self.poison = v 
             if k == "colony" and isinstance(v, int):
                  self.colony = v



class SpecialGrade_TideCurse(Enemy):
       def __init__(self, **kwargs):
        super.init(name="Flymouth", level=1, hp=30, max_hp=30, ce=20, max_ce=20, strength=10, speed=20, xp=10, cgp=1, technique="Triplebackhand", playerclass="curse")
        for k, v in kwargs:
             if k == "qunatity" and isinstance(v, int):
                  self.quantity = v
             if k == "killed" and isinstance(v, dict):
                  self.killed=v
             if k == "killcount" and isinstance(v, dict):
                    self.killcount=v
             if k == "poison" and isinstance(v, tuple):
                    self.poison = v 
             if k == "colony" and isinstance(v, int):
                  self.colony = v




class SpecialGrade_DeathSpirit(Enemy):
       def __init__(self, **kwargs):
        super.init(name="Flymouth", level=1, hp=30, max_hp=30, ce=20, max_ce=20, strength=10, speed=20, xp=10, cgp=1, technique="Triplebackhand", playerclass="curse")
        for k, v in kwargs:
             if k == "qunatity" and isinstance(v, int):
                  self.quantity = v
             if k == "killed" and isinstance(v, dict):
                  self.killed=v
             if k == "killcount" and isinstance(v, dict):
                    self.killcount=v
             if k == "poison" and isinstance(v, tuple):
                    self.poison = v 
             if k == "colony" and isinstance(v, int):
                  self.colony = v

class Toji(Enemy):
           def __init__(self, **kwargs):
            super.init(name="Flymouth", level=1, hp=30, max_hp=30, ce=20, max_ce=20, strength=10, speed=20, xp=10, cgp=1, technique="Triplebackhand", playerclass="curse")
            for k, v in kwargs:
                if k == "qunatity" and isinstance(v, int):
                    self.quantity = v
                if k == "killed" and isinstance(v, dict):
                    self.killed=v
                if k == "killcount" and isinstance(v, dict):
                        self.killcount=v
                if k == "poison" and isinstance(v, tuple):
                        self.poison = v 
                if k == "colony" and isinstance(v, int):
                    self.colony = v




class Reggie(Enemy):
        def __init__(self, **kwargs):
                super.init(name="Flymouth", level=1, hp=30, max_hp=30, ce=20, max_ce=20, strength=10, speed=20, xp=10, cgp=1, technique="Triplebackhand", playerclass="curse")
                for k, v in kwargs:
                    if k == "qunatity" and isinstance(v, int):
                        self.quantity = v
                    if k == "killed" and isinstance(v, dict):
                        self.killed=v
                    if k == "killcount" and isinstance(v, dict):
                            self.killcount=v
                    if k == "poison" and isinstance(v, tuple):
                            self.poison = v 
                    if k == "colony" and isinstance(v, int):
                        self.colony = v



class Uro(Enemy):
        def __init__(self, **kwargs):
                        super.init(name="Flymouth", level=1, hp=30, max_hp=30, ce=20, max_ce=20, strength=10, speed=20, xp=10, cgp=1, technique="Triplebackhand", playerclass="curse")
                        for k, v in kwargs:
                            if k == "qunatity" and isinstance(v, int):
                                self.quantity = v
                            if k == "killed" and isinstance(v, dict):
                                self.killed=v
                            if k == "killcount" and isinstance(v, dict):
                                    self.killcount=v
                            if k == "poison" and isinstance(v, tuple):
                                    self.poison = v 
                            if k == "colony" and isinstance(v, int):
                                self.colony = v





class KingOfCurses(Enemy):                  
        def __init__(self, **kwargs):
                super.init(name="Flymouth", level=1, hp=30, max_hp=30, ce=20, max_ce=20, strength=10, speed=20, xp=10, cgp=1, technique="Triplebackhand", playerclass="curse")
                for k, v in kwargs:
                    if k == "qunatity" and isinstance(v, int):
                        self.quantity = v
                    if k == "killed" and isinstance(v, dict):
                        self.killed=v
                    if k == "killcount" and isinstance(v, dict):
                            self.killcount=v
                    if k == "poison" and isinstance(v, tuple):
                            self.poison = v 
                    if k == "colony" and isinstance(v, int):
                        self.colony = v


class Kenjaku(Enemy):
        def __init__(self, **kwargs):
                super.init(name="Flymouth", level=1, hp=30, max_hp=30, ce=20, max_ce=20, strength=10, speed=20, xp=10, cgp=1, technique="Triplebackhand", playerclass="curse")
                for k, v in kwargs:
                    if k == "qunatity" and isinstance(v, int):
                        self.quantity = v
                    if k == "killed" and isinstance(v, dict):
                        self.killed=v
                    if k == "killcount" and isinstance(v, dict):
                            self.killcount=v
                    if k == "poison" and isinstance(v, tuple):
                            self.poison = v 
                    if k == "colony" and isinstance(v, int):
                        self.colony = v


class Uraume(Enemy):
        def __init__(self, **kwargs):
                super.init(name="Flymouth", level=1, hp=30, max_hp=30, ce=20, max_ce=20, strength=10, speed=20, xp=10, cgp=1, technique="Triplebackhand", playerclass="curse")
                for k, v in kwargs:
                    if k == "qunatity" and isinstance(v, int):
                        self.quantity = v
                    if k == "killed" and isinstance(v, dict):
                        self.killed=v
                    if k == "killcount" and isinstance(v, dict):
                            self.killcount=v
                    if k == "poison" and isinstance(v, tuple):
                            self.poison = v 
                    if k == "colony" and isinstance(v, int):
                        self.colony = v

    
class Kashimo(Enemy):
        def __init__(self, **kwargs):
                super.init(name="Flymouth", level=1, hp=30, max_hp=30, ce=20, max_ce=20, strength=10, speed=20, xp=10, cgp=1, technique="Triplebackhand", playerclass="curse")
                for k, v in kwargs:
                    if k == "qunatity" and isinstance(v, int):
                        self.quantity = v
                    if k == "killed" and isinstance(v, dict):
                        self.killed=v
                    if k == "killcount" and isinstance(v, dict):
                            self.killcount=v
                    if k == "poison" and isinstance(v, tuple):
                            self.poison = v 
                    if k == "colony" and isinstance(v, int):
                        self.colony = v
