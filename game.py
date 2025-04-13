import json, traceback
import datetime
from typing import Union, List, Optional
import enum, random, sys
from copy import deepcopy
import old_techniques


#currencies:
# CGP = CULLING GAME POINTS - Points used to buy items from the shop
# SKP = SKILL POINTS - Points used to level up Skillsets
# XP = EXPERIENCE POINTS - Points that level you up and level up your cursed technique 


#this is where we will create most of the functionaliy for our characters and enemies
class GameMode(enum.IntEnum):
    ROAM = 1 #Roam status for when player does nothing
    PVE = 2 #Pve status for when player begins a PvE fight
    PVP = 3 #Pvp status for when player begins a PvP fight earn more xp from killing players, team up against stronger players, team battles, earn higher points # for when the player is in a queue
# to be used for all human characters/enemies


# region BodyParts
class BodyPart:
    def __init__(self, name, max_hp, max_ce=None):
        self.name = name
        self.max_ce = max_ce
        self.ce=max_ce
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
    
human_body_parts = {"Head" : BodyPart('Head', 0, 0),
    "Left Arm" : BodyPart('Left Arm', 0,0),
    "Right Arm" : BodyPart('Right Arm', 0, 0),
    "Torso" : BodyPart('Torso', 0, 0)}


#endregion

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

#region Actor class
class Actor:
    def __init__(self,
            name: str, 
            level:int,
            max_hp,
            max_ce: int,
            strength: int, 
            speed: int,
            technique: str, 
            playerclass: str, colony
            ):
        self.name=name
        self.level=level
        self.max_hp=max_hp
        self.max_ce=max_ce
        self.strength=strength
        self.speed=speed
        self.technique=technique
        self.playerclass=playerclass
        self.colony=colony
        self.hp=max_hp
        self.ce=max_ce


    def __repr__(self):
        return f"{self.name} - HP: {self.hp}, XP: {self.xp}, CGP: {self.cgp}, Technique: {self.technique}"

#endregion

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
     
# region Enemy
class Enemy(Actor):
    def __init__(self, name, level, max_hp, max_ce, strength, speed, technique, playerclass,  xp: int, cgp: int, 
                stack=0, colony:int = None, defense: dict=None,
                inventory: list = None, equipped: list = None,
                poison: tuple=None,charge: int=None, 
                stun: tuple=None,  hi: bool=None, hr: str=None,
                prescience: int=None, tamed: bool=None,
                debuffed: list=None, buffed: list=None, summons: list=None, 
                healed: int=None, bodyparts: dict=None, quantity: int=None, soul: int=None, status=None, timer=None, killed=None):
            
            super().__init__(
                name, 
                level, 
                max_hp, 
                max_ce, 
                strength, 
                speed, 
                technique, 
                playerclass, 
                colony)
            inventory = {"Tools" : {}, "Technique Inv" : {}, "Summon" : {}}
            self.name = name
            self.ce = max_ce
            self.hp = max_hp
            self.max_hp = max_hp
            self.max_ce = max_ce
            self.level = level
            self.strength = strength
            self.speed = speed
            self.technique = technique
            self.playerclass = playerclass
            self.colony = colony
            self.inventory = inventory 
            self.equipped = equipped 
            self.xp = xp
            self.cgp = cgp
            self.stacked = stack
            self.charged = charge
            self.stun = stun
            self.hi = hi
            self.hr = hr
            self.prescience = prescience
            self.debuffed = debuffed 
            self.buffed = buffed
            self.summons = summons
            self.poison= poison
            self.healed=healed
            self.bodyparts=bodyparts
            self.tamed=tamed
            self.quantity=quantity
            self.soul = soul
            self.status=status
            self.killed=killed
            self.timer=timer
            self.imbue=0
            self.defense = defense

    def __repr__(self):
        return f"Enemy: {self.name} - {self.level} - HP: {self.hp}, XP: {self.xp}, CGP: {self.cgp}, Technique: {self.technique} - in colony: {self.colony}"
# endregion 



# region Player
class Player(Actor):
    level_cap = 200
    def __init__(self, name, level, max_hp, max_ce, strength, speed, technique, playerclass, colony, 
                    xp: int, cgp: int, skp: int, user_id: int,
                    stack=0, imbue=0,defense: dict={"Default" : "ce"}, inventory={"Technique Inv" : {}, "Tools" : {}, "Summon" : {}, "Binding Vows" : {}, "Rules" : {}},
                    equipped: list=None,
                    summons: list=None,
                    poisoned: tuple=None, stunned: tuple=None, 
                    hr: str=None, # heavenley restriction ("max", "zero")
                    hi: bool=None, # hidden inventory
                    rct: tuple=None, #(1, 2, 3) 
                    heal: dict=None,
                    self_heal: int=None,
                    killcount: list=None, 
                    buffed: list=None, 
                    debuffed: list=None, status: str=None, grade=None, 
                    soul: dict=None, six_eyes: bool=None,
                    killed: str=None):
        try:          
          super().__init__(name, level, max_hp, max_ce, strength, speed, technique, playerclass, colony)
          self.defense = defense
          self.xp = xp
          self.cgp = cgp
          self.skp = skp
          self.strength=strength
          self.speed=speed
          self.technique=technique
          self.colony=colony
          self.userd_id=user_id
          self.equipped=equipped
          self.inventory=inventory
          self.summons=summons
          self.stack=stack
          self.imbue=imbue
          self.poisoned=poisoned
          self.stunned=stunned
          self.hr=hr
          self.hi =hi
          self.rct = rct
          self.heal = heal
          self.self_heal = self_heal
          self.killcount=killcount
          self.buffed=buffed
          self.debuffed=debuffed
          self.status=status
          self.grade=grade
          self.soul=soul
          self.heal = heal
          self.six_eyes=six_eyes
          self.killed=killed
          humanoid_body = {
              "Head": BodyPart(name='Head', max_hp=self.max_hp * 10 // 100),
              "Torso": BodyPart(name='Torso', max_hp=self.max_hp * 50 // 100, max_ce=self.max_ce),
              "Left Arm": BodyPart(name='Left Arm', max_hp=self.max_hp * 10 // 100),
              "Right Arm": BodyPart(name='Right Arm', max_hp=self.max_hp * 10 // 100),
              "Left Leg": BodyPart(name='Left Leg', max_hp=self.max_hp * 10 // 100),
              "Right Leg": BodyPart(name='Right Leg', max_hp=self.max_hp * 10 // 100)
          }
          self.bodyparts = humanoid_body

          
          
        except:
             traceback.print_exc()
     
    def __repr__(self):
        return f"Character: {self.name} - HP: {self.hp}, XP: {self.xp}, CGP: {self.cgp}, Technique: {self.technique} - belonging to user_id: {self.user_id} - in colony: {self.colony}"


    def sell(self, item, price, shop):
        try:
         if item in self.inventory:
              forsale = self.inventory.pop(item)
              shop.append[{
                   "forsale" : 
                    [
                    {"name": forsale.name}, 
                    {"price" : price},
                     {"owner" : self.user_id}
                    ]
                    }]
              self.save_player()
              return True
         else:
              return False
        except:
            print("Erorr selling " + item + "\n#" * 50 + "\n# Error in def sell(self, item, price, shop) function of the  Player Class\n") #############################################
            traceback.print_exc()


     
    def add_body_part(self, bodypart):
        try:
            parts = self.body_parts
            self.body_parts[bodypart.name] = bodypart
            self.saveplayer()
        except:
             print("#" * 50 + "\n# Error in add_body_parts(self, bodypart) function of the  Player Class\n")
             traceback.print_exc()
    
                            
    def get_grade(self):
        try:
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
        except:
             print("#" * 50 + "\n# Error in get_grade(self) function of the  Player Class\n\n")
             traceback.print_exc()
             

    def store(self, item):
     try:
        if item in self.equipment:
            self.inventory.append(item)
            self.equipment.remove(item)
            self.saveplayer()
            return True
        else:
            print("You don't have that item!")
            return False
           
     except:
          print("#" * 50 + "\n# Error in get_grade(self) function of the  Player Class\n\n")
          traceback.print_exc()
             
    def equip(self, item):
            if item in self.inventory:
                self.inventory.remove(item)
                self.equipment.append(item)
                self.saveplayer()
                return True
            else:
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

#endregion
#         
#region ENEMY CLASSES 
## SUBCLASS OF ENEMY CLASS





class Grade4_Bugfly(Enemy):
    def __init__(self):
        
        super().__init__(
             name="Bugfly", 
             level=1,
             max_hp=15, 
             max_ce=20, 
             strength=20, 
             speed=40, 
             xp=10, 
             cgp=1, 
             technique="Bugfly", 
             playerclass="Curse", 
             quantity=random.randrange(1, 8),
             bodyparts={
            "Head" : BodyPart(name="Head", max_hp=15, max_ce=20), 
        
            },
            timer=0,
            killed=False
             )
        self.hp = self.max_hp
        self.ce = self.max_ce


            
class  Grade4_Floatjelly(Enemy):
    def __init__(self):
          super().__init__(
             name="FloatJelly", 
             level=1, 
      
             max_hp=20, 
       
             max_ce=20, 
             strength=20, 
             speed=20, 
             xp=10, 
             cgp=1, 
             technique="Floatjelly", 
             playerclass="Curse", 
             quantity=random.randrange(1, 6), 
             stun=1,
             bodyparts={"Head": BodyPart(name="Head", max_hp=15, max_ce=20)},
             timer=0,
             killed=False)
          self.hp = self.max_hp
          self.ce = self.max_ce


class Grade4_Flymouth(Enemy):
    min_level= 1
    def __init__(self):
          super().__init__(
             name="Flymouth", 
             level="1", 
             max_hp=30, 
             max_ce=20, 
             strength=10, 
             speed=20,
             xp=10, 
             cgp=1, 
             technique="Flymouth", 
             playerclass="Curse", 
             quantity=random.randrange(1, 4),
             poison=(3, 1),
             bodyparts={"Head": BodyPart(name="Head", max_hp=15, max_ce=20)},
             timer=0,
             killed=False)
    
          self.hp = self.max_hp
          self.ce = self.max_ce
          
class Grade3_Barehand(Enemy):

    def __init__(self):
          super().__init__(
              name="Barehand Curse", 
             level=1, 
        
             max_hp=150, 
   
             max_ce=100, 
             strength=80, 
             speed=120, 
             xp=50, 
             cgp=1, 
             technique="Backhand", 
             playerclass="Curse", 
             quantity=random.randrange(1, 3),
 bodyparts= {"Head" : BodyPart(name='Head', max_hp=150 * 20// 100, max_ce=100 * 20 // 100), "Torso" : BodyPart(name="Torso", max_hp=150 * 50 // 100, max_ce=100 * 50 // 100), "Hands" : BodyPart(name="Hands", max_hp=150 * 30 // 100, max_ce = 150 * 30 //100)}
 ,
 timer=60,
 killed=False)
  

class Grade3_Furrpede(Enemy):
    def __init__(self):
        super().__init__(
             name="Furrpede", 
             level=1,  
             max_hp=200, 
             max_ce=50, 
             strength=100, 
             speed=50, 
             xp=50, 
             cgp=1, 
             technique="Furrpede", 
             playerclass="Curse", 
             quantity=random.randrange(1,3),
             bodyparts={"Head": BodyPart(name="Head", max_hp=200 * 20 // 100, max_ce=50 * 20 // 100), 
                        "Torso": BodyPart(name="Torso", max_hp=200 * 50 // 100, max_ce=50 * 50 // 100), 
                        "Legs": BodyPart(name="Legs", max_hp=200 * 30 // 100, max_ce=50 * 30 // 100)},
            timer=60,
            killed=False
             )
        self.hp = self.max_hp
        self.ce = self.max_ce

class Grade3_AnxiousEars(Enemy):
    def __init__(self):
        super().__init__(
             name="Anxious Ears", 
             level=15, 
             max_hp=250, 
             max_ce=200, 
             strength=50, 
             speed=50, 
             xp=100, 
             cgp=1, 
             technique="AnxiousEars", 
             playerclass="Curse", 
             quantity=random.randrange(1,3),
             bodyparts={"Head" : BodyPart(name='Head', max_hp=250 * 20// 100, max_ce=200 * 20 // 100), "Torso" : BodyPart(name="Torso", max_hp=250 * 50 // 100, max_ce=200 * 50 // 100), "Hands" : BodyPart(name="Hands", max_hp=250 * 30 // 100, max_ce = 200 * 30 //100)}
             , timer=60,
             killed=False)

        self.hp = self.max_hp
        self.ce = self.max_ce


class Grade2_Stinkaspor(Enemy):
    def __init__(self):
        super().__init__(
             name="Stinkaspor", 
             level=30,
             max_hp=350, 
             max_ce=350, 
             strength=150, 
             speed=150, 
             xp=200, 
             cgp=1, 
             technique="Stinkaspor", 
             playerclass="Curse",
             quantity=random.randrange(1, 2),
             bodyparts={"Head" : BodyPart(name='Head', max_hp=350 * 20// 100, max_ce=350 * 20 // 100), "Torso" : BodyPart(name="Torso", max_hp=350 * 50 // 100, max_ce=350 * 50 // 100), "Stingers" : BodyPart(name="Stingers", max_hp=350 * 30 // 100, max_ce = 350 * 30 //100)}
             ,
             timer=60,
             killed=False)
 
        self.hp = self.max_hp
        self.ce = self.max_ce

             


class Grade2_Primate(Enemy):
    def __init__(self):
        super().__init__(
             name="Primate", 
             level=30, 
             max_hp=300,
             max_ce=350, 
             strength=150, 
             speed=150, 
             xp=200,
             cgp=1, 
             technique="Primate",
             playerclass="Curse",
             quantity=random.randrange(1,2),
             bodyparts={"Head" : BodyPart(name='Head', max_hp=300 * 20// 100, max_ce=350 * 20 // 100), "Torso" : BodyPart(name="Torso", max_hp=300 * 50 // 100, max_ce=350 * 50 // 100), "Arms" : BodyPart(name="Arms", max_hp=300 * 15 // 100, max_ce = 350 * 30 //100), "Legs" : BodyPart(name="Legs", max_hp=300*15//100, max_ce = 350 * 30 // 100)}
              ,
              timer=60,
              killed=False)
        self.hp = self.max_hp
        self.ce = self.max_ce
        




class Grade1_Orbmaster(Enemy):
    def __init__(self ):
        super().__init__(
             name="OrbMaster", 
             level=40, 
             max_hp=400, 
             max_ce=500, 
             strength=200, 
             speed=300, 
             xp=400, 
             cgp=1, 
             technique="Orbmaster", 
             playerclass="Curse",
             bodyparts=human_body_parts,
             timer=300,
             killed=False)
        self.hp = self.max_hp
        self.ce = self.max_ce


class Grade1_Charger(Enemy):
    def __init__(self):
            super().__init__(
                 name="Charger", 
                 level=40, 
         
                 max_hp=400, 
  
                 max_ce=400, 
                 strength=400, 
                 speed=400, 
                 xp=400, 
                 cgp=1, 
                 technique="Charger", 
                 playerclass="Curse",
                 bodyparts=human_body_parts,
                 timer=300,
                 killed=False
                 )
            self.hp = self.max_hp
            self.ce = self.max_ce


class SpecialGrade_FingerBearer(Enemy):
    def __init__(self):
          super().__init__(
             name="Fingerbearer", 
             level=80, 
     
             max_hp=600, 
   
             max_ce=600, 
             strength=700,
             speed=800,
             xp=600,
             cgp=1,
             technique="Fingerbearer",
             playerclass="Curse",
             bodyparts=human_body_parts,
             timer=300,
             killed=False)
          self.hp = self.max_hp
          self.ce = self.max_ce


class SpecialGrade_DisasterFlames(Enemy):
        def __init__(self):
            super().__init__(
                        name="Disaster Flames",
                        level=80, 
                   
                        max_hp=800, 
                 
                        max_ce=1200, 
                        strength=800, 
                        speed=1500, 
                        xp=1000, 
                        cgp=1, 
                        technique="Disaster Flames", 
                        playerclass="Curse",
                        bodyparts=human_body_parts,
                        timer=300,
                        killed=False
                        )
            self.hp = self.max_hp
            self.ce = self.max_ce
                
                




class SpecialGrade_NatureSpirit(Enemy):
        def __init__(self):
            super().__init__(name="Nature Spirit",
                       level=80, 
                
                       max_hp=1200, 
               
                       max_ce=1000, 
                       strength=900, 
                       speed=900, 
                       xp=1000, 
                       cgp=1, 
                       technique="Nature Spirit", 
                       playerclass="curse",
                       bodyparts=human_body_parts,
                       timer=300,
                       killed=False
                       )
   
            self.hp = self.max_hp
            self.ce = self.max_ce


class SpecialGrade_TideCurse(Enemy):
       def __init__(self):
        super().__init__(name="Tide Curse",
                   level=60,
                
                   max_hp=800, 
               
                   max_ce=1000, 
                   strength=800, 
                   speed=800, 
                   xp=1000, 
                   cgp=1, 
                   technique="Disaster Tides", 
                   playerclass="Curse",
                   bodyparts=human_body_parts,
                   timer=300,
                   killed=False
        )
        self.hp = self.max_hp
        self.ce = self.max_ce
        
class SpecialGrade_Soul_Curse(Enemy):
       def __init__(self):
        super().__init__(
                    name="Soul Curse",
                   level=80, 
            
                   max_hp=1000,
            
                   max_ce=1000,
                   strength=600,
                   speed=800,
                   xp=1000,
                   cgp=1,
                   technique="Idle Transfiguration",
                   playerclass="Curse",
                   bodyparts=human_body_parts,
                   soul=500,
                   timer=300,
                   killed=False
                   )
     
        self.hp = self.max_hp
        self.ce = self.max_ce



class Toji(Enemy):
           def __init__(self):
            super().__init__(name="Toji",
                       level=100,
                       max_hp=1200,
                       max_ce=0,
                       strength=1200,
                       speed=1200,
                       xp=1200,
                       cgp=5,
                       technique="Toji", 
                       playerclass="Reincarnate",
                       bodyparts=human_body_parts,
                       timer=300,
                       killed=False
                       )
            self.hp = self.max_hp
            self.ce = self.max_ce



class Reggie(Enemy):
        def __init__(self):
                super().__init__(name="Reggie", 
                           level=60,
                         
                           max_hp=600,
                      
                           max_ce=700,
                           strength=800,
                           speed=800,
                           xp=1000,
                           cgp=5,
                           technique="Reggie",
                           playerclass="Reincarnate",
                           bodyparts=human_body_parts,
                           timer=300,
                           killed=False
                )

                self.hp = self.max_hp
                self.ce = self.max_ce
class Uro(Enemy):
        def __init__(self):
                        super().__init__(name="Uro",
                                   level=80,
                             
                                   max_hp=800,
                                 
                                   max_ce=1000,
                                   strength=600,
                                   speed=1200,
                                   xp=1000,
                                   cgp=5,
                                   technique="Uro",
                                   playerclass="Reincarnate",
                                   bodyparts=human_body_parts,
                                   timer=300,
                                   killed=False
                                   )
                        self.hp = self.max_hp
                        self.ce = self.max_ce
class Ryu(Enemy): 
     def __init__(self):
          super().__init__(
                    name="Ryu",
                    level=100,
                     max_hp=1000,
                     max_ce=1200,
                     strength=1000,
                     speed=1000,
                     xp=1000,
                     cgp=5,
                     technique="Cursed Energy Discharge",
                     playerclass="Reincarnate",
                     bodyparts=human_body_parts,
                     timer=300,
                     killed=False,
                     )
          self.hp = self.max_hp
          self.ce = self.max_ce
          


class Kashimo(Enemy):
     def __init__(self):
          super().__init__(
                    name="Kashimo",
                    level=150,
                     max_hp=1500,
                     max_ce=1600,
                     strength=1800,
                     speed=1800,
                     xp=1500,
                     cgp=5,
                     technique="Kashimo",
                     playerclass="Reincarnate",
                     stun=2,
                     soul={"strength" : 100},
                     bodyparts=human_body_parts,
                     timer=500,
                     killed=False
                     )
          self.hp = self.max_hp
          self.ce = self.max_ce

class KingOfCurses(Enemy):                  
        def __init__(self, **kwargs):
                super().__init__(name="King Of Curses", 
                           level=150, 
                      
                           max_hp=7000, 
                   
                           max_ce=4000, 
                           strength=5000, 
                           speed=5000, 
                           xp=2000, 
                           cgp=5,
                           technique="King Of Curses",
                            playerclass="Reincarnate",
                           bodyparts=human_body_parts,
                           timer=500,
                           killed=False
                           )
                self.hp = self.max_hp
                self.ce = self.max_ce
                


class Kenjaku(Enemy):
        def __init__(self, ):
                super().__init__(
                     name="Kenjaku", 
                     level=150, 
                     max_hp=3000, 
                     max_ce=2000, 
                     strength=2000, 
                     speed=2000, 
                     xp=2000, 
                     cgp=5, 
                     technique="Body Hop: Anti Gravity Manipulation",
                     playerclass="Reincarnate",
                     bodyparts=human_body_parts,
                     timer=500,
                     killed=False
                     )                
                self.hp = self.max_hp
                self.ce = self.max_ce
             
#endregion