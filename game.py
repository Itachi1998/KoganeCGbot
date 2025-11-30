import traceback, os, db
import datetime
from typing import Union, List, Optional
import enum, random, sys
from copy import deepcopy


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

#region Actor
class Actor:
    def __init__(self,
            name: str, 
            level: int,
            max_hp,
            max_ce: int,
            strength: int, 
            speed: int,
            technique: str, 
            playerclass: str, colony_id
            ):
        self.name = name
        self.level = level
        self.max_hp = max_hp
        self.max_ce = max_ce
        self.strength = strength
        self.speed = speed
        self.technique = technique
        self.playerclass = playerclass
        self.colony_id = colony_id
        self.hp = max_hp
        self.ce = max_ce


    def __repr__(self):
        return f"{self.name} - HP: {self.hp}, XP: {self.xp}, CGP: {self.cgp}, Technique: {self.technique}"

#endregion

# region Enemy
class Enemy(Actor):
    def __init__(self, name, level, max_hp, max_ce, strength, speed, technique, 
                 playerclass,  xp: int, cgp: int, 
                stack=0, colony_id:int = None, defense: dict=None,
                inventory: list = None, equipped: list = None,
                poison: tuple=None,charge: int=None, 
                stun: tuple=None,  hi: bool=None, hr: str=None,
                prescience: int=None, tamed: int=None,
                debuffed: list=None, buffed: list=None, summons: list=None, 
                healed: int=None, bodyparts: dict=None, quantity: int=None, 
                soul: int=None, status=None, timer=None, killed=None):
            super().__init__(
                name, 
                level, 
                max_hp, 
                max_ce, 
                strength, 
                speed, 
                technique, 
                playerclass, 
                colony_id)
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
            self.colony = colony_id
            self.inventory = inventory 
            self.equipped = equipped 
            self.xp = xp
            self.cgp = cgp
            self.stack = stack
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

    def __init__(self, 
                    name, entered, level, max_hp, max_ce, strength, 
                    speed, technique, playerclass, colony_id, 
                    xp: int, cgp: int, skp: int, user_id: int,
                    stack=0, imbue={'speed':0, 'strength':0},
                    defense: str="CE", 
                    inventory={"Technique Inv" : {}, "Tools" : {}, "Summon" : {}, "Binding Vows" : {}, "Rules" : {}},
                    equipped: list=None,
                    summons: list=None,
                    poisoned: tuple=None, stunned: tuple=None, 
                    hr: str=None, # heavenley restriction ("max", "zero")
                    hi: bool=None, # hidden inventory
                    heal: dict=None,
                    self_heal: int=None,
                    killcount: list=None, 
                    buffed: list=None, 
                    debuffed: list=None, status: str=None, grade=None, 
                    soul: dict=None, six_eyes: bool=None,
                    killed: str=None):
        try:          
          super().__init__(name, level, max_hp, max_ce, strength, speed, technique, playerclass, colony_id)

          self.entered=entered
          self.defense = defense
          self.xp = xp
          self.cgp = cgp
          self.skp = skp
          self.strength=strength
          self.speed=speed
          self.technique=technique
          self.colony=colony_id
          self.userd_id=user_id
          self.colony=colony_id
          self.user_id=user_id
          self.equipped=equipped
          self.inventory=inventory
          self.summons=summons
          self.stack=stack
          self.imbue=imbue
          self.poisoned=poisoned
          self.stunned=stunned
          self.hr=hr
          self.hi =hi
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

def save_to_db(self, value=None):
    if value == None:
          db.save_player(self)
    else:
         updated_player = db.update_player(value)

#endregion
def check_for_image(name):
    if not os.path.isdir('images'):
          print("No image found for: " + name)
          return None
    else:
         imagedir = os.listdir('images')
         for i in imagedir:
              if i == name + ".png":
                   path = "images/" + i
                   return path
#region Bugfly
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
             quantity=random.randrange(4, 8),
             bodyparts={
            "Head" : BodyPart(name="Head", max_hp=15, max_ce=20), 
        
            },
            timer=0,
            killed=False,
             )
        self.hp = self.max_hp
        self.ce = self.max_ce
image = check_for_image("bugfly_spirit")
if image is not None:
    Grade4_Bugfly.image_path = image

#endregion
Grade4_Bugfly.grade = 1
Grade4_Bugfly.min_level = 1
#region FloatJelly      
class  Grade4_Floatjelly(Enemy):
    def __init__(self):
          super().__init__(
             name="Floatjelly", 
             level=1, 
      
             max_hp=20, 
       
             max_ce=20, 
             strength=20, 
             speed=20, 
             xp=10, 
             cgp=1, 
             technique="Floatjelly", 
             playerclass="Curse", 
             quantity=random.randrange(2, 6), 
             stun=1,
             bodyparts={"Head": BodyPart(name="Head", max_hp=15, max_ce=20)},
             timer=0,
             killed=False)
          self.hp = self.max_hp
          self.ce = self.max_ce
image = check_for_image("flaotjelly_spirit")
if image:
     Grade4_Floatjelly.image_path = image
#endregion
Grade4_Floatjelly.grade = 1
Grade4_Floatjelly.min_level=1
#region Flymouth
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
#endregion
Grade4_Flymouth.grade = 1
Grade4_Flymouth.min_level=1

image = check_for_image("mouthbat_spirit")
if image:
     Grade4_Flymouth.image_path = image

#region Barehand
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
             technique="Barehand", 
             playerclass="Curse", 
             quantity=random.randrange(1, 3),
 bodyparts= {"Head" : BodyPart(name='Head', max_hp=150 * 20// 100, max_ce=100 * 20 // 100), "Torso" : BodyPart(name="Torso", max_hp=150 * 50 // 100, max_ce=100 * 50 // 100), "Hands" : BodyPart(name="Hands", max_hp=150 * 30 // 100, max_ce = 150 * 30 //100)},
 timer=60,
 killed=False)
          self.hp = self.max_hp
          self.ce = self.max_ce
# endregion
Grade3_Barehand.grade = 2
Grade3_Barehand.min_level=1

image = check_for_image("barehand_curse")
if image:
     Grade3_Barehand.image_path = image

#region  Furrpede
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
#endregion
Grade3_Furrpede.grade = 2
Grade3_Furrpede.min_level=1

image = check_for_image("furrpede_spirit")
if image:
     Grade3_Furrpede.image_path = image
#region AnxiousEars
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
#endregion
Grade3_AnxiousEars.grade = 2
Grade3_AnxiousEars.min_level=1
image = check_for_image("anxious_ears")
if image:
     Grade3_AnxiousEars.image_path = image

#region Stinkaspor
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
Grade2_Stinkaspor.grade = 3
Grade2_Stinkaspor.min_level=1
image = check_for_image("stinkaspore")
if image:
     Grade2_Stinkaspor.image_path = image
#endregion

#region Primate
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
             bodyparts={"Head" : BodyPart(name='Head', max_hp=300 * 20// 100, max_ce=350 * 20 // 100), "Torso" : BodyPart(name="Torso", max_hp=300 * 50 // 100, max_ce=350 * 50 // 100), "Arms" : BodyPart(name="Arms", max_hp=300 * 15 // 100, max_ce = 350 * 30 //100),
                         "Legs" : BodyPart(name="Legs", max_hp=300*15//100, max_ce =350 * 30 //100)})
Grade2_Primate.grade = 3
Grade2_Primate.min_level=1
image = check_for_image("primate")
if image:
     Grade2_Primate.image_path = image
#region Orbmaster
class Grade1_Orbmaster(Enemy):
    def __init__(self ):
        super().__init__(
             name="Orbmaster", 
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
#endregion
Grade1_Orbmaster.grade = 4
Grade1_Orbmaster.min_level=20
image = check_for_image("orbmaster")
if image:
     Grade1_Orbmaster.image_path = image

#region Charger
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
#endregion
Grade1_Charger.grade = 4
Grade1_Charger.min_level=30
image = check_for_image("charger_spirit")
if image:
     Grade1_Charger.image_path = image
#region FingerBearer
class SpecialGrade_FingerBearer(Enemy):
    def __init__(self):
        super().__init__(
             name="Finger Bearer", 
             level=80, 
             max_hp=600, 
             max_ce=600, 
             strength=700,
             speed=800,
             xp=600,
             cgp=1,
             technique="Finger Bearer",
             playerclass="Curse",
             bodyparts=human_body_parts,
             timer=300,
             killed=False)
        self.hp = self.max_hp
        self.ce = self.max_ce

#endregion
SpecialGrade_FingerBearer.grade = 5
SpecialGrade_FingerBearer.min_level=50
image = check_for_image("fingerer")
if image:
     SpecialGrade_FingerBearer.image_path = image
#region DisasterFlames
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
#endregion
SpecialGrade_DisasterFlames.grade = 5
SpecialGrade_DisasterFlames.min_level=50
image = check_for_image("joga")
if image:
     SpecialGrade_DisasterFlames.image_path = image
#region NatureSpirit
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
                       technique="Natures Wrath", 
                       playerclass="curse",
                       bodyparts=human_body_parts,
                       timer=300,
                       killed=False
                       )
            self.hp = self.max_hp
            self.ce = self.max_ce
#endregion
SpecialGrade_NatureSpirit.grade = 5
SpecialGrade_NatureSpirit.min_level=50
image = check_for_image("hanam")
if image:
     SpecialGrade_NatureSpirit.image_path = image
#region TideCurse
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
#endregion
SpecialGrade_TideCurse.grade = 5
SpecialGrade_TideCurse.min_level=50
image = check_for_image("dagon_womb")
if image:
     SpecialGrade_TideCurse.image_path = image

#region SoulCurse
class SpecialGrade_SoulCurse(Enemy):
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
SpecialGrade_SoulCurse.min_level=50
#endregion
SpecialGrade_SoulCurse.grade = 5
image = check_for_image("femhito")
if image:
     SpecialGrade_SoulCurse.image_path = image
#region Toji
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
                       technique="Heavenly Restriction: Zero", 
                       playerclass="Reincarnate",
                       bodyparts=human_body_parts,
                       timer=300,
                       killed=False
                       )
            self.hp = self.max_hp
            self.ce = self.max_ce
#endregion
Toji.grade = 5
Toji.min_level=100
#region Reggie
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
                           technique="Contractual Recreation",
                           playerclass="Reincarnate",
                           bodyparts=human_body_parts,
                           timer=300,
                           killed=False
                )
                self.hp = self.max_hp
                self.ce = self.max_ce
#endregion
Reggie.grade = 4
Reggie.min_level=100
#region Uro
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
                                   technique="Sky Manipulation",
                                   playerclass="Reincarnate",
                                   bodyparts=human_body_parts,
                                   timer=300,
                                   killed=False
                                   )
                        self.hp = self.max_hp
                        self.ce = self.max_ce
#endregion
Uro.grade = 4
Uro.min_level=100
image = check_for_image("uro")
if image:
     Uro.image_path = image
#region Ryu
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
#endregion
Ryu.grade=5
Ryu.min_level=100
image = check_for_image("ryu")
if image:
     Ryu.image_path = image
#region Kashimo
class Kashimo(Enemy):
     def __init__(self):
          super().__init__(
                    name="Kashima",
                    level=150,
                     max_hp=1500,
                     max_ce=1600,
                     strength=1800,
                     speed=1800,
                     xp=1500,
                     cgp=5,
                     technique="Mythical Beast",
                     playerclass="Reincarnate",
                     stun=2,
                     soul={"strength" : 100},
                     bodyparts=human_body_parts,
                     timer=500,
                     killed=False
                     )
          self.hp = self.max_hp
          self.ce = self.max_ce
Kashimo.min_level=150
#endregion
Kashimo.grade = 5
image = check_for_image("kashima")
if image:
     Kashimo.image_path = image
#region KingOfCurses
class KingOfCurses(Enemy):                  
        def __init__(self):
                super().__init__(name="King Of Curses", 
                           level=150,
                           max_hp=7000, 
                           max_ce=4000, 
                           strength=5000, 
                           speed=5000, 
                           xp=2000, 
                           cgp=5,
                           technique="Shrine",
                            playerclass="Reincarnate",
                           bodyparts=human_body_parts,
                           timer=500,
                           killed=False
                           )
                self.hp = self.max_hp
                self.ce = self.max_ce
KingOfCurses.grade = 5
KingOfCurses.min_level=150
#endregion
image = check_for_image("kingofcurses")
if image:
     KingOfCurses.image_path = image


#region Kenjaku
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
                     technique="Body Hop",
                     playerclass="Reincarnate",
                     bodyparts=human_body_parts,
                     timer=500,
                     killed=False
                     )                
                self.hp = self.max_hp
                self.ce = self.max_ce
                
Kenjaku.grade = 5
Kenjaku.min_level=150
image = check_for_image("kenny")
if image:
     Kenjaku.image_path = image

     
#endregion