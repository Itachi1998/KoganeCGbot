import json, traceback
import datetime
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
    ROAM = 1 #Roam status for when player does nothing
    PVE = 2 #Pve status for when player begins a PvE fight
    PVP = 3 #Pvp status for when player begins a PvP fight earn more xp from killing players, team up against stronger players, team battles, earn higher points
    Q = 4 # for when the player is in a queue

class BodyPart:
    def __init__(self, name, max_hp, max_ce):
        self.max_ce=max_ce
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0
        print(f"{self.name} took {damage} damage. Remaining hp: {self.hp}")

    def is_stunned(self):
         if self.hp <= self.max_hp//2:
              return True
         
    def is_destroyed(self):
        return self.hp <= 0

# class Character:
   # def __init__(self, name):
       # self.name = name
       # self.body_parts = {}

   # def add_body_part(self, body_part):
#         self.body_parts[body_part.name] = body_part

#    # def take_damage(self, body_part_name, damage):
#         if body_part_name in self.body_parts:
           #  self.body_parts[body_part_name].take_damage(damage)
           # if self.body_parts[body_part_name].is_destroyed():
               # print(f"{self.body_parts[body_part_name].name} is destroyed!")
       #  else:
           # print(f"{body_part_name} not found on {self.name}.")

# Example usage
# player = Character("Hero")
# head = BodyPart("Head", 50)
# arm_left = BodyPart("Left Arm", 30)
# arm_right = BodyPart("Right Arm", 30)
# torso = BodyPart("Torso", 100)

# player.add_body_part(head)
# player.add_body_part(arm_left)
# player.add_body_part(arm_right)
# player.add_body_part(torso)

# player.take_damage("Head", 20)
# player.take_damage("Left Arm", 30)
# player.take_damage("Torso", 110)
# player.take_damage("Legs", 40) # Body part not found
# Parent class for the Player and Enemy Subclasses

class Actor:
    def __init__(self,
 name: str, 
level:int,
max_hp,
 max_ce: int,
 strength: int, 
speed: int,
 xp: int, 
cgp: int,
 technique: str, 
playerclass: str):
        self.name=name
        self.level=level
        self.max_hp = max_hp
        self.max_ce = max_ce
        self.strength = strength
        self.speed = speed,
        self.xp = xp,
        self.cgp=cgp,
        self.technique = technique
        self.playerclass= playerclass
        self.hp = max_hp
        self.ce = max_ce

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

    def __init__(self, name, level, max_hp, max_ce, strength, speed, xp, cgp, technique, playerclass, **kwargs):
        super().__init__(name, level, max_hp, max_ce, strength, speed, xp, cgp, technique, playerclass)
        self.ce=max_ce
        self.hp = max_hp
        for k,v in kwargs:
             if k == "colony" and isinstance(v, int):
                  self.colony = v
             if k == "grade" and isinstance(v, str):
                  self.grade = v 
             if k == "killed" and isinstance(v, bool):
                  self.killed = v # if this enemy is dead
             if k == "timer" and isinstance(v, tuple) and  all(isinstance(i, int) for i in v):
                  self.timer = v # (date_killed, timer)
             if k == "tamed" and isinstance(v, tuple) and all(isinstance(i, int) for i in v):
                   self.tamed = v # (owner_player_id, colony_id, date_tamed)
             if k == "equipped" and isinstance(v, list) and all(isinstance(i, dict) for i in v):
                   self.equipped = v # list of equipped items
             if k == "shikigami" and isinstance(v, list) and all(isinstance(i, dict) for i in v):
                   self.shikigami = v # list of shikigami
             if k == "killby" and isinstance(v, tuple) and all(isinstance(i, int) for i in v):
                    self.killby = v # who it was killed by (player_id, colony_id)
             if k == "poison" and isinstance(v, tuple) and all(isinstance(i, int) for i in v):
                  self.poison = v # poison damage and duration
             if k == "stun" and isinstance(v, int):
                  self.stun=v
             if k == "charged" and isinstance(v, int):
                  self.charged=v
             if k == "quantity" and isinstance(v, int):
                  self.quantity=v
             if k == "transfigured souls" and isinstance(v, list):
                  self.tranf_souls = v
             if k == "stacks" and isinstance(v, int):
                  self.stacks = v # number of stacks needed to duplicate speed if Proj Sorcery
             if k == "hr" and isinstance(v, str):
                  self.hr = v
     

    def __repr__(self):
        return f"Enemy: {self.name} - HP: {self.hp}, XP: {self.xp}, CGP: {self.cgp}, Technique: {self.technique} - in colony: {self.colony}"

class Player(Actor):
    level_cap = 200
    def __init__(self, name, level, max_hp, max_ce, strength, speed, xp, cgp, technique, playerclass, **kwargs):
          super().__init__(name, level, max_hp, max_ce, strength, speed, xp, cgp, technique, playerclass)
   
          if 'luck' in kwargs.keys() and isinstance(kwargs['luck'], int):
                        self.luck = kwargs['luck']

          if "clan" in kwargs.keys() and isinstance(kwargs['clan'], str):
                     self.clan = kwargs['clan']

          if "awakened" in kwargs.keys() and isinstance(kwargs['awakened'], bool):
                    self.awakened= kwargs['awakened']
                    self.luck = 0
          if "rct" in kwargs.keys() and isinstance(kwargs['rct'], bool):
                   self.rct = kwargs['rct']
                   self.max_hp += 100
                   self.hp = self.max_hp
          if 'hr' in kwargs.keys() and isinstance(kwargs['hr'], str):
                   self.hr = kwargs['hr']

          if 'six eyes' in kwargs.keys() and isinstance(kwargs['six eyes'], bool):
                   self.six_eyes = True
               
          if 'bodyparts' in kwargs.keys() and isinstance(kwargs['bodyparts'], list):
                   self.bodyparts = kwargs['bodyparts'] 
          if 'colony' in kwargs.keys() and isinstance(kwargs['colony'], int):
                   self.colony = kwargs['colony']

          self.buffs = []
          self.debuffs = []
          self.shikigami = []
          self.inventory = []
          self.equipped = []
          self.curses = []
          self.copied_techs = []
          self.bindvows = []
          self.rules = []
          self.souls = []
          self.killcount = []
          self.selling = []
          self.bought = []
          self.shadowstore = []
          self.rikastore = []
          self.status = GameMode.ROAM
          self.head = BodyPart(name='Head', max_hp=self.max_hp//4, max_ce=self.max_ce//4)
          self.torso = BodyPart(name='Torso', max_hp= self.max_hp//4)
          self.legs = BodyPart(name="Legs", max_hp = self.max_hp//4, max_ce = self.max_ce//4)
          self.arms = BodyPart(name="Arms", max_hp=self.max_hp//4, max_ce = self.max_ce//4)
          

    def __repr__(self):
        return f"Character: {self.name} - HP: {self.hp}, XP: {self.xp}, CGP: {self.cgp}, Technique: {self.technique} - belonging to user_id: {self.user_id} - in colony: {self.colony}"


    def sell(self, item, price):
         if item in self.inventory:
              forsale = self.inventory.pop(item)
              self.selling.append((forsale, price))
              self.save_to_db()
              return True
         else:
              return False
         
    def bought(self, item, price, colony):
         if isinstance(item, dict):
              self.inventory.append(item)
              date = datetime.datetime.now()
              printable = f"{date.strftime("%c")}"
              self.bought.append(item['name'], item['price'], printable, colony)

     
                    
    def get_grade(self):
         level = self.level
         if self.level >= 1 and self.level < 10:
             return "Grade 4"
         elif self.level >= 10 and self.level < 20:
             return "Grade 3"
         elif self.level >= 20 and self.level < 40:
             return "Grade 2"
         elif self.level >= 40 and self.level < 60:
             return "Grade 1"
         else:
             return "Special Grade"

    def store(self, item):
        if item in self.equipment:
            self.inventory.append(item)
            self.equipment.remove(item)
            self.save_to_db()
            return True
        else:
            print("You don't have that item!")
            return False

    def equip(self, item):
            if item in self.inventory:
                self.inventory.remove(item)
                self.equipment.append(item)
                self.save_to_db()
                return True
            else:
                print("Item not owned")
                return False
            
            

    def level_up(self, xp_needed):

        if self.level >= self.level_cap:
            self.level = self.level_cap
            self.save_to_db()
            return (False, self.level, self.xp) #if the player has reached the level cap, they will no longer level up, and will no longer gain skill points

        if self.xp >= xp_needed:
            while self.xp >= xp_needed:
                    
                    self.level += 1 # If the players xp is greater than or equal to the xp needed to level up, they will level up

                    if self.level < 10: # If the players level is under 10, they will gain 2 skill points 
                        self.skp += 2
                    if self.level > 10: # If the players level is over 10, they will gain 4 skill points
                        self.skp += 4
                    if self.level > 50: # If the players level is over 50, they will gain 6 skill points
                        self.skp += 6
                    if self.level > 100: # If the players level is over 100, they will gain 8 skill points
                        self.skp += 8
                    if self.level > 180: # If the players level is over 180, they will gain 10 skill points per level
                        self.skp += 10
                    
                    

                    self.save_to_db()
                    xp_needed = self.ready_level_up()[1]
                
            grade = self.get_grade() # Use the calss method get_grade to determine the players grade

                    # Set player CT level per grade

            if 'Grade 4' in grade:
                                self.ct_level = 1
            if 'Grade 3' in grade:
                                self.ct_level = 2
            if 'Grade 2' in grade:
                                self.ct_level = 3
            if 'Grade 1' in grade:
                                self.ct_level = 4
            if 'Special Grade' in grade:
                                self.ct_level = 5

            return (True, self.level, self.skp)
        return (False, self.level, self.xp)
        
    def ready_level_up(self): # Method that returns xp needed for next level up
        level_cap = self.level_cap
        if self.level == level_cap:
            return (False, self.level)
        xp_needed = self.level * 5 # Start with the base XP needed being the players level multiplied by 5
        if self.level > 10: 
            xp_needed = self.level * 10 
        if self.level > 20:
            xp_needed = (self.level) * 12 
        if self.level > 30:
            xp_needed = (self.level) * 14 
        if self.level > 40:
            xp_needed = (self.level) * 16 
        if self.level > 50:
            xp_needed = (self.level) * 18 
        if self.level > 60:
            xp_needed = (self.level) * 20
        if self.level > 80:
            xp_needed = (self.level) * 22
        if self.level > 100:
            xp_needed = (self.level) * 24
        if self.level > 120:
            xp_needed = (self.level) * 26
        if self.level > 140:
            xp_needed = (self.level) * 28
        if self.level > 160:
            xp_needed = (self.level) * 30
        if self.level > 180:
            xp_needed = (self.level) * 32
        return (self.xp >= xp_needed, xp_needed)

#     def save_to_db(self):
#      save_player(self) #the imported save_player method from the database file

        
## ENEMY CLASSES 
## SUBCLASS OF ENEMY CLASS
        
class Grade4_Bugfly(Enemy):
    def __init__(self):
        super.init(
             name="Bugfly", 
             level=1,
             hp=15, 
             max_hp=15, 
             max_ce=20, 
             strength=20, 
             speed=40, 
             xp=10, 
             cgp=1, 
             technique="Bugfly", 
             playerclass="curse4", 
             quantity=random.randrange(1, 8)
             )
        self.head = BodyPart(name='Head', max_hp=self.max_hp * 10// 100, max_ce=self.max_ce * 10 // 100)
        self.torso = BodyPart(name='Torso', max_hp=self.max_hp * 50 // 100, max_ce=self.max_ce * 50// 100)
        self.legs = BodyPart(name='Legs', max_hp = self.max_hp * 20 // 100, max_ce = self.max_ce * 20 // 100)
        self.arms = BodyPart(name='Arms', max_hp= self.max_hp * 20 // 100, max_ce = self.max_ce * 20 // 100)
        self.hp = self.max_hp
        self.ce = self.max_ce


            
class  Grade4_Floatjelly(Enemy):
    def __init__(self):
          super.init(
             name="FloatJelly", 
             level=1, 
      
             max_hp=20, 
       
             max_ce=20, 
             strength=20, 
             speed=20, 
             xp=10, 
             cgp=1, 
             technique="Floatjelly", 
             playerclass="curse4", 
             quantity=random.randrange(1, 6), 
             stun=1
             )
          self.head = BodyPart(name='Head', max_hp=self.max_hp * 10// 100, max_ce=self.max_ce * 10 // 100)
          self.torso = BodyPart(name='Torso', max_hp=self.max_hp * 50 // 100, max_ce=self.max_ce * 50// 100)
          self.legs = BodyPart(name='Legs', max_hp = self.max_hp * 20 // 100, max_ce = self.max_ce * 20 // 100)
          self.arms = BodyPart(name='Arms', max_hp= self.max_hp * 20 // 100, max_ce = self.max_ce * 20 // 100)
          self.hp = self.max_hp
          self.ce = self.max_ce


class Grade4_Flymouth(Enemy):
    min_level= 1
    def __init__(self):
          super.init(
             name="Flymouth", 
             level="1", 
             max_hp=30, 
             max_ce=20, 
             strength=10, 
             speed=20,
             xp=10, 
             cgp=1, 
             technique="Flymouth", 
             playerclass="curse4", 
             quantity=random.randrange(1, 4),
             poison=(3, 1) 
             )
        
          self.head = BodyPart(name='Head', max_hp=self.max_hp * 10// 100, max_ce=self.max_ce * 10 // 100)
          self.torso = BodyPart(name='Torso', max_hp=self.max_hp * 50 // 100, max_ce=self.max_ce * 50// 100)
          self.legs = BodyPart(name='Legs', max_hp = self.max_hp * 20 // 100, max_ce = self.max_ce * 20 // 100)
          self.arms = BodyPart(name='Arms', max_hp= self.max_hp * 20 // 100, max_ce = self.max_ce * 20 // 100)
          self.hp = self.max_hp
          self.ce = self.max_ce
          


class Grade3_Backhand(Enemy):

    def __init__(self):
          super.init(
              name="Backhand", 
             level=1, 
             hp=150, 
             max_hp=150, 
             ce=100, 
             max_ce=100, 
             strength=80, 
             speed=120, 
             xp=50, 
             cgp=1, 
             technique="Backhand", 
             playerclass="curse3", 
             quantity=random.randrange(1, 3)
             )
          self.head = BodyPart(name='Head', max_hp=self.max_hp * 10// 100, max_ce=self.max_ce * 10 // 100)
          self.torso = BodyPart(name='Torso', max_hp=self.max_hp * 50 // 100, max_ce=self.max_ce * 50// 100)
          self.legs = BodyPart(name='Legs', max_hp = self.max_hp * 20 // 100, max_ce = self.max_ce * 20 // 100)
          self.arms = BodyPart(name='Arms', max_hp= self.max_hp * 20 // 100, max_ce = self.max_ce * 20 // 100)
          self.hp = self.max_hp
          self.ce = self.max_ce

class Grade3_Furrpede(Enemy):
    def __init__(self):
        super.init(
             name="Furrpede", 
             level=1,  
             max_hp=200, 
             max_ce=50, 
             strength=100, 
             speed=50, 
             xp=50, 
             cgp=1, 
             technique="Furrpede", 
             playerclass="curse3", 
             quantity=random.randrange(1,3)
             )
        self.head = BodyPart(name='Head', max_hp=self.max_hp * 10// 100, max_ce=self.max_ce * 10 // 100)
        self.torso = BodyPart(name='Torso', max_hp=self.max_hp * 50 // 100, max_ce=self.max_ce * 50// 100)
        self.legs = BodyPart(name='Legs', max_hp = self.max_hp * 20 // 100, max_ce = self.max_ce * 20 // 100)
        self.arms = BodyPart(name='Arms', max_hp= self.max_hp * 20 // 100, max_ce = self.max_ce * 20 // 100)
        self.hp = self.max_hp
        self.ce = self.max_ce

class Grade3_AnxiousEars(Enemy):
    def __init__(self):
        super.init(
             name="Anxious Ears", 
             level=15, 
             max_hp=250, 
             max_ce=200, 
             strength=50, 
             speed=50, 
             xp=100, 
             cgp=1, 
             technique="AnxiousEars", 
             playerclass="curse3", 
             quantity=random.randrange(1,3)
             )
        self.head = BodyPart(name='Head', max_hp=self.max_hp * 10// 100, max_ce=self.max_ce * 10 // 100)
        self.torso = BodyPart(name='Torso', max_hp=self.max_hp * 50 // 100, max_ce=self.max_ce * 50// 100)
        self.legs = BodyPart(name='Legs', max_hp = self.max_hp * 20 // 100, max_ce = self.max_ce * 20 // 100)
        self.arms = BodyPart(name='Arms', max_hp= self.max_hp * 20 // 100, max_ce = self.max_ce * 20 // 100)
        self.hp = self.max_hp
        self.ce = self.max_ce


class Grade2_Stinkaspor(Enemy):
    def __init__(self):
        super.init(
             name="Stinkaspor", 
             level=30,
             max_hp=350, 
             max_ce=350, 
             strength=150, 
             speed=150, 
             xp=200, 
             cgp=1, 
             technique="Stinkaspor", 
             playerclass="curse2",
             quantity=random.randrange(1, 2)
             )
        self.head = BodyPart(name='Head', max_hp=self.max_hp * 10// 100, max_ce=self.max_ce * 10 // 100)
        self.torso = BodyPart(name='Torso', max_hp=self.max_hp * 50 // 100, max_ce=self.max_ce * 50// 100)
        self.legs = BodyPart(name='Legs', max_hp = self.max_hp * 20 // 100, max_ce = self.max_ce * 20 // 100)
        self.arms = BodyPart(name='Arms', max_hp= self.max_hp * 20 // 100, max_ce = self.max_ce * 20 // 100)
        self.hp = self.max_hp
        self.ce = self.max_ce

             


class Grade2_Monkeybrain(Enemy):
    def __init__(self):
        super.init(
             name="Monkeybrain", 
             level=30, 
             max_hp=300,
             max_ce=350, 
             strength=150, 
             speed=150, 
             xp=200,
             cgp=1, 
             technique="Monkeybrain",
             playerclass="curse2",
             quantity=random.randrange(1,2)
              )
        self.head = BodyPart(name='Head', max_hp=self.max_hp * 10// 100, max_ce=self.max_ce * 10 // 100)
        self.torso = BodyPart(name='Torso', max_hp=self.max_hp * 50 // 100, max_ce=self.max_ce * 50// 100)
        self.legs = BodyPart(name='Legs', max_hp = self.max_hp * 20 // 100, max_ce = self.max_ce * 20 // 100)
        self.arms = BodyPart(name='Arms', max_hp= self.max_hp * 20 // 100, max_ce = self.max_ce * 20 // 100)
        self.hp = self.max_hp
        self.ce = self.max_ce
        




class Grade1_Orbmaster(Enemy):
    def __init__(self ):
        super.init(
             name="OrbMaster", 
             level=40, 
    
             max_hp=400, 
 
             max_ce=500, 
             strength=200, 
             speed=300, 
             xp=400, 
             cgp=1, 
             technique="Orbmaster", 
             playerclass="curse1")
        self.head = BodyPart(name='Head', max_hp=self.max_hp * 10// 100, max_ce=self.max_ce * 10 // 100)
        self.torso = BodyPart(name='Torso', max_hp=self.max_hp * 50 // 100, max_ce=self.max_ce * 50// 100)
        self.legs = BodyPart(name='Legs', max_hp = self.max_hp * 20 // 100, max_ce = self.max_ce * 20 // 100)
        self.arms = BodyPart(name='Arms', max_hp= self.max_hp * 20 // 100, max_ce = self.max_ce * 20 // 100)
        self.hp = self.max_hp
        self.ce = self.max_ce


class Grade1_Charger(Enemy):
    def __init__(self):
            super.init(
                 name="Charger", 
                 level=40, 
         
                 max_hp=400, 
  
                 max_ce=400, 
                 strength=400, 
                 speed=400, 
                 xp=400, 
                 cgp=1, 
                 technique="Charger", 
                 playerclass="curse1"
                 )
            self.head = BodyPart(name='Head', max_hp=self.max_hp * 10// 100, max_ce=self.max_ce * 10 // 100)
            self.torso = BodyPart(name='Torso', max_hp=self.max_hp * 50 // 100, max_ce=self.max_ce * 50// 100)
            self.legs = BodyPart(name='Legs', max_hp = self.max_hp * 20 // 100, max_ce = self.max_ce * 20 // 100)
            self.arms = BodyPart(name='Arms', max_hp= self.max_hp * 20 // 100, max_ce = self.max_ce * 20 // 100)
            self.hp = self.max_hp
            self.ce = self.max_ce


class SpecialGrade_FingerBearer(Enemy):
    def __init__(self):
          super.init(
             name="Fingerbearer", 
             level=80, 
     
             max_hp=600, 
   
             max_ce=600, 
             strength=700,
             speed=800,
             xp=600,
             cgp=1,
             technique="Fingerbearer",
             playerclass="curse0")
          self.head = BodyPart(name='Head', max_hp=self.max_hp * 10// 100, max_ce=self.max_ce * 10 // 100)
          self.torso = BodyPart(name='Torso', max_hp=self.max_hp * 50 // 100, max_ce=self.max_ce * 50// 100)
          self.legs = BodyPart(name='Legs', max_hp = self.max_hp * 20 // 100, max_ce = self.max_ce * 20 // 100)
          self.arms = BodyPart(name='Arms', max_hp= self.max_hp * 20 // 100, max_ce = self.max_ce * 20 // 100)
          self.hp = self.max_hp
          self.ce = self.max_ce


class SpecialGrade_DisasterFlames(Enemy):
        def __init__(self):
            super.init(
                        name="Disaster Flames",
                        level=80, 
                   
                        max_hp=800, 
                 
                        max_ce=1200, 
                        strength=800, 
                        speed=1500, 
                        xp=1000, 
                        cgp=1, 
                        technique="Disaster Flames", 
                        playerclass="curse0"
                        )
            self.head = BodyPart(name='Head', max_hp=self.max_hp * 10// 100, max_ce=self.max_ce * 10 // 100)
            self.torso = BodyPart(name='Torso', max_hp=self.max_hp * 50 // 100, max_ce=self.max_ce * 50// 100)
            self.legs = BodyPart(name='Legs', max_hp = self.max_hp * 20 // 100, max_ce = self.max_ce * 20 // 100)
            self.arms = BodyPart(name='Arms', max_hp= self.max_hp * 20 // 100, max_ce = self.max_ce * 20 // 100)
            self.hp = self.max_hp
            self.ce = self.max_ce
                
                




class SpecialGrade_NatureSpirit(Enemy):
        def __init__(self):
            super.init(name="Nature Spirit",
                       level=80, 
                
                       max_hp=1200, 
               
                       max_ce=1000, 
                       strength=900, 
                       speed=900, 
                       xp=1000, 
                       cgp=1, 
                       technique="Nature Spirit", 
                       playerclass="curse"
                       )
            self.head = BodyPart(name='Head', max_hp=self.max_hp * 10// 100, max_ce=self.max_ce * 10 // 100)
            self.torso = BodyPart(name='Torso', max_hp=self.max_hp * 50 // 100, max_ce=self.max_ce * 50// 100)
            self.legs = BodyPart(name='Legs', max_hp = self.max_hp * 20 // 100, max_ce = self.max_ce * 20 // 100)
            self.arms = BodyPart(name='Arms', max_hp= self.max_hp * 20 // 100, max_ce = self.max_ce * 20 // 100)
            self.hp = self.max_hp
            self.ce = self.max_ce


class SpecialGrade_TideCurse(Enemy):
       def __init__(self):
        super.init(name="Tide Curse",
                   level=60,
                
                   max_hp=800, 
               
                   max_ce=1000, 
                   strength=800, 
                   speed=800, 
                   xp=1000, 
                   cgp=1, 
                   technique="Tide Curse", 
                   playerclass="curses"
                   )
        self.head = BodyPart(name='Head', max_hp=self.max_hp * 10// 100, max_ce=self.max_ce * 10 // 100)
        self.torso = BodyPart(name='Torso', max_hp=self.max_hp * 50 // 100, max_ce=self.max_ce * 50// 100)
        self.legs = BodyPart(name='Legs', max_hp = self.max_hp * 20 // 100, max_ce = self.max_ce * 20 // 100)
        self.arms = BodyPart(name='Arms', max_hp= self.max_hp * 20 // 100, max_ce = self.max_ce * 20 // 100)
        self.hp = self.max_hp
        self.ce = self.max_ce
        


class SpecialGrade_Satasha(Enemy):
       def __init__(self):
        super.init(name="Satasha",
                   level=80, 
            
                   max_hp=1000,
            
                   max_ce=1000,
                   strength=600,
                   speed=800,
                   xp=1000,
                   cgp=1,
                   technique="Satasha",
                   playerclass="curses"
                   )
        self.head = BodyPart(name='Head', max_hp=self.max_hp * 10// 100, max_ce=self.max_ce * 10 // 100)
        self.torso = BodyPart(name='Torso', max_hp=self.max_hp * 50 // 100, max_ce=self.max_ce * 50// 100)
        self.legs = BodyPart(name='Legs', max_hp = self.max_hp * 20 // 100, max_ce = self.max_ce * 20 // 100)
        self.arms = BodyPart(name='Arms', max_hp= self.max_hp * 20 // 100, max_ce = self.max_ce * 20 // 100)
        self.hp = self.max_hp
        self.ce = self.max_ce



class Toji(Enemy):
           def __init__(self):
            super.init(name="Toji",
                       level=100,
                  
                       max_hp=1200,
                   
                       max_ce=0,
                       strength=1200,
                       speed=1200,
                       xp=1200,
                       cgp=5,
                       technique="Toji", 
                       playerclass="reincarnated"
                       )
            self.head = BodyPart(name='Head', max_hp=self.max_hp * 10// 100, max_ce=self.max_ce * 10 // 100)
            self.torso = BodyPart(name='Torso', max_hp=self.max_hp * 50 // 100, max_ce=self.max_ce * 50// 100)
            self.legs = BodyPart(name='Legs', max_hp = self.max_hp * 20 // 100, max_ce = self.max_ce * 20 // 100)
            self.arms = BodyPart(name='Arms', max_hp= self.max_hp * 20 // 100, max_ce = self.max_ce * 20 // 100)
            self.hp = self.max_hp
            self.ce = self.max_ce



class Reggie(Enemy):
        def __init__(self):
                super.init(name="Reggie", 
                           level=60,
                         
                           max_hp=600,
                      
                           max_ce=700,
                           strength=800,
                           speed=800,
                           xp=1000,
                           cgp=5,
                           technique="Reggie",
                           playerclass="reincarnated"
                )

                self.head = BodyPart(name='Head', max_hp=self.max_hp * 10// 100, max_ce=self.max_ce * 10 // 100)
                self.torso = BodyPart(name='Torso', max_hp=self.max_hp * 50 // 100, max_ce=self.max_ce * 50// 100)
                self.legs = BodyPart(name='Legs', max_hp = self.max_hp * 20 // 100, max_ce = self.max_ce * 20 // 100)
                self.arms = BodyPart(name='Arms', max_hp= self.max_hp * 20 // 100, max_ce = self.max_ce * 20 // 100)
                self.hp = self.max_hp
                self.ce = self.max_ce
class Uro(Enemy):
        def __init__(self):
                        super.init(name="Uro",
                                   level=80,
                             
                                   max_hp=800,
                                 
                                   max_ce=1000,
                                   strength=600,
                                   speed=1200,
                                   xp=1000,
                                   cgp=5,
                                   technique="Uro",
                                   playerclass="reincarnated"
                                   )

                        self.head = BodyPart(name='Head', max_hp=self.max_hp * 10// 100, max_ce=self.max_ce * 10 // 100)
                        self.torso = BodyPart(name='Torso', max_hp=self.max_hp * 50 // 100, max_ce=self.max_ce * 50// 100)
                        self.legs = BodyPart(name='Legs', max_hp = self.max_hp * 20 // 100, max_ce = self.max_ce * 20 // 100)
                        self.arms = BodyPart(name='Arms', max_hp= self.max_hp * 20 // 100, max_ce = self.max_ce * 20 // 100)
                        self.hp = self.max_hp
                        self.ce = self.max_ce
class Ryu(Enemy): 
     def __init__(self):
          super.init(name="Ryu",
                  
                     max_hp=1000,
               
                     max_ce=1200,
                     strength=1000,
                     speed=1000,
                     xp=1000,
                     cgp=5,
                     technique="Ryu",
                     playerclass="reincarnated"
                     )
          self.head = BodyPart(name='Head', max_hp=self.max_hp * 10// 100, max_ce=self.max_ce * 10 // 100)
          self.torso = BodyPart(name='Torso', max_hp=self.max_hp * 50 // 100, max_ce=self.max_ce * 50// 100)
          self.legs = BodyPart(name='Legs', max_hp = self.max_hp * 20 // 100, max_ce = self.max_ce * 20 // 100)
          self.arms = BodyPart(name='Arms', max_hp= self.max_hp * 20 // 100, max_ce = self.max_ce * 20 // 100)
          self.hp = self.max_hp
          self.ce = self.max_ce
          


class Kashimo(Enemy):
     def __init__(self):
          super.init(name="Kashimo",
                
                     max_hp=1500,
           
                     max_ce=1600,
                     strength=1800,
                     speed=1800,
                     xp=1500,
                     cgp=5,
                     technique="Kashimo",
                     playerclass="reincarnated",
                     stun=2,
                     soul={"strength" : 100}
                     )
          self.head = BodyPart(name='Head', max_hp=self.max_hp * 10// 100, max_ce=self.max_ce * 10 // 100)
          self.torso = BodyPart(name='Torso', max_hp=self.max_hp * 50 // 100, max_ce=self.max_ce * 50// 100)
          self.legs = BodyPart(name='Legs', max_hp = self.max_hp * 20 // 100, max_ce = self.max_ce * 20 // 100)
          self.arms = BodyPart(name='Arms', max_hp= self.max_hp * 20 // 100, max_ce = self.max_ce * 20 // 100)
          self.hp = self.max_hp
          self.ce = self.max_ce

class KungOfCurses(Enemy):                  
        def __init__(self, **kwargs):
                super.init(name="King of Curses", 
                           level=100, 
                      
                           max_hp=7000, 
                   
                           max_ce=4000, 
                           strength=5000, 
                           speed=5000, 
                           xp=2000, 
                           cgp=5, 
                           technique="King of Curses", 
                           playerclass="reincarnated"
                           )
                self.head = BodyPart(name='Head', max_hp=self.max_hp * 10// 100, max_ce=self.max_ce * 10 // 100)
                self.torso = BodyPart(name='Torso', max_hp=self.max_hp * 50 // 100, max_ce=self.max_ce * 50// 100)
                self.legs = BodyPart(name='Legs', max_hp = self.max_hp * 20 // 100, max_ce = self.max_ce * 20 // 100)
                self.arms = BodyPart(name='Arms', max_hp= self.max_hp * 20 // 100, max_ce = self.max_ce * 20 // 100)
                self.hp = self.max_hp
                self.ce = self.max_ce


class Kenjaku(Enemy):
        def __init__(self, ):
                super.init(
                     name="Kenjaku", 
                     level=100, 

                     max_hp=3000, 
               
                     max_ce=2000, 
                     strength=2000, 
                     speed=2000, 
                     xp=2000, 
                     cgp=1, 
                     technique="Kenjaku",
                     playerclass="reincarnated"
                     )
                self.head = BodyPart(name='Head', max_hp=self.max_hp * 10// 100, max_ce=self.max_ce * 10 // 100)
                self.torso = BodyPart(name='Torso', max_hp=self.max_hp * 50 // 100, max_ce=self.max_ce * 50// 100)
                self.legs = BodyPart(name='Legs', max_hp = self.max_hp * 20 // 100, max_ce = self.max_ce * 20 // 100)
                self.arms = BodyPart(name='Arms', max_hp= self.max_hp * 20 // 100, max_ce = self.max_ce * 20 // 100)
                
                if sum(self.head.hp, self.torsohp.hp, self.legs.hp, self.arms.hp) == self.max_hp:
                    self.hp = self.max_hp
                    self.ce = self.max_ce
