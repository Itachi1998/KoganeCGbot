import json, dynamo, traceback
from typing import Union, List
import enum, random, sys
from copy import deepcopy
from cogs.battle import Target
import techniques
from dynamo import save_player











#currencies:
# CGP = CULLING GAME POINTS - Points used to buy items from the shop
# SKP = SKILL POINTS - Points used to level up Skillsets
# XP = EXPERIENCE POINTS - Points that level you up and level up your cursed technique 











#this is where we will create most of the functionaliy for our characters and enemies

def str_to_class(classname):
    for e in Enemy.__subclasses__():
        if e.__name__.lower() == classname.lower():
            return e
    raise ValueError(f"Unknown Enemy class name: {classname}")


class GameMode(enum.IntEnum):
    ROAM = 1
    PVE = 2 #learn game and farm
    PVP = 3 #earn more xp from killing players, team up against stronger players, team battles, earn higher points
    Q = 4


class Actor:

    def __init__(self, name, hp, max_hp, attack, defense, speed, xp, cgp,
                 technique, imbued, equipped):
        self.name = name
        self.hp = hp
        self.max_hp = max_hp
        self.attack = attack
        self.defense = defense
        self.xp = xp
        self.speed = speed
        self.cgp = cgp
        self.technique = technique
        self.imbued = imbued
        self.equipped = equipped
        

    def fight(self, other):
        try:
            print(f"{self.name} attacks {other.name}"
                  )
            
            speed = self.imbued + self.speed
            
            other_speed = other.imbued + other.speed
            
            defense = None
            
            if isinstance(other, Enemy):
                      print(f"{other.name} is an ai, continuing player vs ai physical attack calculations")
                      t = techniques.Techniques(**other.technique)
                      defense = t.defense[other.defense]
                      other_speed = t.defense[other.defense]['speed']
                
            elif isinstance(self, Enemy):
                t_name = None
                t = techniques.get_cursed_technique(other.technique)
                if other.defense:
                    t_name = other.defense.replace(" ","_")
                else:
                    defense_names = list(t.defense.keys())
                    if len(defense_names) > 1: 
                        other.defense = random.choice(defense_names)
                        t_name = other.defense.replace(" ", "_")
                physic_dic = self.technique['attack']['Physical']
                d_func = None
                if t_name:    
                    d_func = getattr(t, t_name.lower())
                else:
                    t_name = None
                    if self.technique != 'Heavenly Restriction':
                        self.defense = 'CE'
                        t_name = self.defense
                    else:
                        self.defense = 'Heavenly Body'
                        t_name = self.defense.replace(' ', '_')
                    
                    d_func = getattr(t, t_name.lower())        
                results = d_func(self, other, physic_dic)
                other.imbued = 0
                other.save_to_db()
                return results
                
            tool = None
            negate = None
            print(f"{self.name}'s  speed: {speed}, {other.name}'s  {other.defense} speed: {other_speed}")
            
            if self.equipped is not None:
                tool = self.equipped
            if speed >= other_speed:
                spd_calc = max(0, speed - other_speed)
                print(f"spd_calc: {spd_calc}")  # log the calculated speed
                if spd_calc < 20:
                    chance_to_hit = random.randint(0, max(1, 200 - (defense['def'] + spd_calc)))
                else:
                    chance_to_hit = random.randint(0, max(1, 200 - defense['def'])) 
                damage = self.attack + self.imbued

                if tool:
                    if len(tool) > 1:
                        tool1 =techniques.get_cursed_tool(tool[0])
                        tool2 = techniques.get_cursed_tool(tool[1])
                        damage += tool1.attack, tool2.attack
                        if tool1.negate or tool2.negate:
                            defense=0
                            negate='negate'
                    else:
                        tool1 = techniques.get_cursed_tool(tool[0])
                        damage += tool1.attack + tool1.pen  #add tool attack power and penetration to the damage
                        if tool1.negate:
                          defense = 0  #negate defense if tool has the ability
                          negate = 'negate'  #set the negation variable to 'negate
                    
                print(f"Chance to Hit: {chance_to_hit}, Damage: {damage}")


                if self.technique == "HeavenlyRestriction":
                    damage += speed  #add the players speed to damage

                if chance_to_hit:
                    other.hp -= damage
                    print(f"Hit! Damage: {damage}, Enemy HP: {other.hp}")
                    return (
                        damage, "hit", other.hp <= 0, tool)  #add negate variable to check if the hit negated defense
                else:
                    print("Tanked! Enemy HP not reduced")
                    return (0, "tank", other.hp <= 0, tool)
            else:
                print("Missed! Speed too low")
                return (0, "miss", other.hp <= 0, tool)

        except Exception as e:
            print(f"Error in fight method: {e}")
            traceback.print_exc()
            return (0, "error", False)

   
    def use_technique(self, technique, move, target=None, attack=None, host=None, targets=None):
        if move == "attack":
            atr = None
            atk = None
            t=None
            if isinstance(self, Enemy):
                t= techniques.Techniques(**self.technique)
                atk = t.attack[technique]
                target_tech = techniques.get_cursed_technique(target.technique)
                if target.defense is not None:
                    def_name = technique.replace(" ", "_")
                    def_func = getattr(target_tech, def_name.lower())
                    results = def_func(self, target, atk)
                    return results
                    
                else:
                    def_name = 'ce'
                    def_func = getattr(target_tech, def_name.lower())
                    results = def_func(self, target, atk)
                    
            else:
                t = techniques.get_cursed_technique(self.technique)
            print(f"{self.name} launching attack {technique}")
            atr = technique.lower()
            atr = atr.replace(" ","_")
            atk = getattr(t, atr)
            results=None
            
            if target:
                results = atk(self, target)
                
            if targets:
                results, targets =atk(self, targets)
                if targets:
                 return results, targets
                else:
                    return results
   
            return results
            
        if move == "defense":
                lobdat = dynamo.read_lobby(host, colony_id = self.colony)
                t = techniques.get_cursed_technique(self.technique)
                self.defense=technique
                technique = technique.replace(" ", "_")
                if targets:
                    defense_func = getattr(t, technique.lower())
                    results, targets = defense_func(self, targets)
                    return results, targets
                else:
                    defense_func = getattr(t, technique.lower())
                    results = defense_func(target, self, attack)
                    return results
        
class Enemy(Actor):

    def __init__(self, name, hp, max_hp, attack, defense, speed, xp, cgp,
                 technique, imbued, killed, equipped, timer):
        super().__init__(name, hp, max_hp, attack, defense, speed, xp, cgp,
                         technique, imbued, equipped)
        self.enemy = self.__class__.__name__
        self.name = name
        self.killed = killed
        self.timer = timer
        
    def to_dict(self):
        diction = {
            'name': self.name,
            'hp': self.hp,
            'max_hp': self.max_hp,
            'attack': self.attack,
            'defense': self.defense,
            'speed': self.speed,
            'xp': self.xp,
            'cgp': self.cgp,
            'technique': self.technique,
            'imbued': self.imbued,
            'killed': self.killed,
            'equipped': self.equipped,
            'timer': self.timer
        }
        return diction


class Character(Actor):
    level_cap = 200
    def __init__(self, name, hp, max_hp, attack, defense, speed, xp, cgp,
                 technique, imbued, ce, max_ce, level, ct_level, inventory, equipment, mode, user_id, skp, enemy, HR, RCT, colony, victory_msg, shiki, spirits, souls, rules, vows, tools, luck):
        super().__init__(name,
                         hp,
                         max_hp,
                         attack,
                         defense,
                         speed,
                         xp,
                         cgp,
                         technique,
                         imbued, equipped=equipment)
        self.max_ce = max_ce
        self.ct_level = ct_level
        self.ce = ce
        self.level = level
        self.inventory = inventory
        self.equipment = equipment
        self.mode = mode
        self.user_id = user_id
        self.skp = skp
        self.enemy = enemy
        self.HR = HR
        self.RCT = RCT
        self.enemy = enemy
        self.colony = colony
        self.victory_msg = victory_msg
        self.shiki = shiki
        self.spirits = spirits
        self.souls = souls
        self.rules = rules
        self.vows = vows
        self.luck = luck
        self.tools = tools


    def to_dict(self):
        diction = {
            'name': self.name,
            'hp': self.hp,
            'max_hp': self.max_hp,
            'attack': self.attack,
            'defense': self.defense,
            'speed': self.speed,
            'xp': self.xp,
            'cgp': self.cgp,
            'technique': self.technique,
            'imbued': self.imbued,
            'ce': self.ce,
            'max_ce': self.max_ce,
            'level': self.level,
            'ct_level': self.ct_level,
            'inventory': self.inventory,
            'equipment': self.equipment,
            'mode': self.mode,
            'user_id': self.user_id,
            'skp': self.skp,
            'enemy': self.enemy,
            'HR': self.HR,
            'RCT': self.RCT,
            'colony': self.colony,
            'victory_msg': self.victory_msg, 'shiki':self.shiki, 'spirits': self.spirits, 'souls':self.souls, 'stacks': self.stacks, 'charges': self.charges, 'luck': self.luck, 'tools': self.tools
        }
        return diction
    
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
        else:
            print("You don't have that item!")

    def equip(self, item):
            if item in self.inventory:
                self.inventory.remove(item)
                self.equipment.append(item)
                self.save_to_db()
            else:
                print("Item not owned")

    def level_up(self, xp_needed):
        if self.level >= self.level_cap:
            self.level = self.level_cap
            self.save_to_db()
            return (True, self.level)
        
        if self.xp >= xp_needed:
            while self.xp >= xp_needed:
                    self.level += 1
                    if self.level < 10:
                        self.skp += 2
                    if self.level > 10: 
                        self.skp += 4
                    if self.level > 50: # 200 skill points
                        self.skp += 6
                    if self.level > 100: # 500 skill points
                        self.skp += 8
                    if self.level > 180: # 1940
                        self.skp += 10
                    grade = self.get_grade()
                    if self.user_id !=  677718946270543882 or 1164740316738355313:
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
                    else:
                        self.ct_level = 5
                    
                    ready, next_xp = self.ready_level_up()
                    xp_needed = next_xp
                    self.save_to_db()
            return (True, self.level, self.skp)
        return (False, self.level, self.skp)
        
    def ready_level_up(self):
        level_cap = self.level_cap
        if self.level == level_cap:
            return (False, 0)
        xp_needed = (self.level) * 5
        if self.level > 10:
            xp_needed = self.level * 10
        if self.level > 20:
            xp_needed = (self.level) * 15
        if self.level > 30:
            xp_needed = (self.level) * 20
        if self.level > 40:
            xp_needed = (self.level) * 25
        if self.level > 50:
            xp_needed = (self.level) * 30
        if self.level > 60:
            xp_needed = (self.level) * 40
        if self.level > 80:
            xp_needed = (self.level) * 50           
        return (self.xp >= xp_needed, xp_needed)

    def save_to_db(self):
        save_player(self)

    def run(self, target):
        if self.speed > target.speed:
            chance = random.randint(0, (200 - (self.speed + self.imbued - target.speed + target.imbued)))
            if chance < 5:
                return False
            else:
                return True

    def pve(self, colony_id: int) -> Union[List['Enemy'], 'Enemy']:
        colony = dynamo.read_colony(colony_id)
        enemies = colony['ai'][0]
        enemy = None
        enemy_list = []
        for e in enemies:
            name = e.replace(" ", "")
            for i in Enemy.__subclasses__():
                if i.__name__.lower() == name.lower(): # Corrected a match condition
                    if i.min_level <= self.level and i.min_level >= self.level-100:
                        enemy_list.append(i())
        enemies = []
        enemy = random.choice(enemy_list)           
        if enemy.name == "Grade 4":
            enemies = [deepcopy(enemy), deepcopy(enemy), deepcopy(enemy), deepcopy(enemy), deepcopy(enemy)]
        elif enemy.name == "Grade 3":
            enemies = [deepcopy(enemy), deepcopy(enemy), deepcopy(enemy), deepcopy(enemy)]
        elif enemy.name == "Grade 2":
            enemies = [deepcopy(enemy), deepcopy(enemy), deepcopy(enemy)]
        elif enemy.name == "Grade 1":
            enemies = [deepcopy(enemy), deepcopy(enemy)]
        elif enemy.name == "Kechi":
            eso = Eso()
            enemies = [deepcopy(enemy),deepcopy(eso)]
        elif enemy.name == "Eso":
            kechi = Kechi()
            enemies = [deepcopy(enemy), deepcopy(kechi)]
        elif enemy.name == "Mahito" or "Jogo" or "Dagon" or "Hanami":
            list = [1, 2, 3, 4]
            choice = random.choice(list)
            if choice == 1:
                 enemies = [deepcopy(enemy)]
            if choice == 2:
                if enemy.name == 'Mahito':
                    enemies = [deepcopy(enemy), deepcopy(Jogo())]
                if enemies == 'Hanami':
                    enemies = [deepcopy(enemy), deepcopy(Jogo())]
                if enemy.name == 'Jogo':
                        enemies = [deepcopy(enemy), deepcopy(Hanami())]
                if enemy.name == "Dagon":
                    enemies = [deepcopy(enemy), deepcopy(Jogo())]
            if choice == 3:
                if enemy.name == 'Mahito':
                    enemies = [deepcopy(enemy), deepcopy(Jogo()), deepcopy(Hanami())]
                if enemy.name == 'Hanami':
                    enemies = [deepcopy(enemy), deepcopy(Jogo()), deepcopy(Dagon())]
                if enemy.name == 'Jogo':
                        enemies = [deepcopy(enemy), deepcopy(Hanami()), deepcopy(Mahito())]
                if enemy.name == "Dagon":
                    enemy_list = [deepcopy(enemy), deepcopy(Jogo()), deepcopy(Hanami())]
            if choice == 4:
                if enemy.name == 'Mahito':
                    enemies = [deepcopy(enemy), deepcopy(Jogo()), deepcopy(Hanami()), deepcopy(Dagon())]
                if enemy.name == 'Hanami':
                    enemies = [deepcopy(enemy), deepcopy(Jogo()), deepcopy(Dagon()), deepcopy(Mahito())]
                if enemy.name == 'Jogo':
                        enemies = [deepcopy(enemy), deepcopy(Hanami()), deepcopy(Mahito()), deepcopy(Dagon())]
                if enemy.name == "Dagon":
                    enemies = [deepcopy(enemy), deepcopy(Jogo()), deepcopy(Hanami()), deepcopy(Mahito())]

        elif enemy.name == "King Of Curses":
            uraume = Uraume()
            list = [1, 2]
            choice = random.choice(list)
            if choice == 1:
                enemies = [deepcopy(enemy), deepcopy(uraume)]
                
        else:
            
            enemies = [enemy]
            
        return enemies
        
        
        

class Grade4(Enemy):
    min_level = 1
    
    def __init__(self):
        self.t = techniques.get_enemy_cursed_technique("Grade 4")
        self.defense=list(self.t.defense.keys())
        if len(self.defense) > 1:
            self.defense = random.choice(self.defense)
        else:
            self.defense = self.defense[0]
        super().__init__(
            name="Grade 4",
            hp=25,
            max_hp=25,
            attack=20,
            defense=self.defense,
            speed=20,
            xp=5,
            cgp=2,
            technique=self.t.to_dict(),
            imbued=20,
            killed=False,
            equipped=[], timer=0)


class Grade3(Enemy):
    min_level = 1
    def __init__(self):
        self.t = techniques.get_enemy_cursed_technique("Grade 3")
        self.defense = list(self.t.defense.keys())
        if len(self.defense) > 1:
            self.defense = random.choice(self.defense)
        else:
            self.defense = self.defense[0]
        super().__init__(
            name="Grade 3",
            hp=30,
            max_hp=30,
            attack=34,
            defense=self.defense,
            speed=32,
            xp=5,
            cgp=2,
            technique=self.t.to_dict(),
            imbued=40,
            killed=False,
            equipped=[], timer=0)


class Grade2(Enemy):
            min_level = 5
            
            def __init__(self):
                self.t = techniques.get_enemy_cursed_technique("Grade 2")
                self.defense = list(self.t.defense.keys())
                if len(self.defense) > 1:
                    self.defense = random.choice(self.defense)
                else:
                    self.defense = self.defense[0]
                super().__init__(
                    name="Grade 2",
                    hp=50,
                    max_hp=50,
                    attack=40,
                    defense=self.defense,
                    speed=40,
                    xp=10,
                    cgp=2,
                    technique=self.t.to_dict(),
                    imbued=4,
                    killed=False,
                    equipped=[], timer=0)

class Grade1(Enemy):
    min_level = 5
    
    def __init__(self):
        self.t = techniques.get_enemy_cursed_technique("Grade 1")
        self.defense = list(self.t.defense.keys())
        if len(self.defense) > 1:
            self.defense = random.choice(self.defense)
        else:
            self.defense = self.defense[0]
        super().__init__(
            name="Grade 1",
            hp=100,
            max_hp=100,
            attack=60,
            defense=self.defense,
            speed=100,
            xp=10,
            cgp=2,
            technique=self.t.to_dict(),
            imbued=4,
            killed=False,
            equipped=[], timer=3)


class FingerBearer(Enemy):
            min_level = 10
            
            def __init__(self):
                self.t = techniques.get_enemy_cursed_technique("Finger Bearer")
                self.defense = list(self.t.defense.keys())
                if len(self.defense) > 1:
                    self.defense = random.choice(self.defense)
                else:
                    self.defense = self.defense[0]
                super().__init__(
                    name="Finger Bearer",
                    hp=100,
                    max_hp=100,
                    attack=20,
                    defense=self.defense,
                    speed=50,
                    xp=10,
                    cgp=2,
                    technique=self.t.to_dict(),
                    imbued=10,
                    killed=False,
                    equipped=[], timer=3)
                


class Kechi(Enemy):
    min_level = 15
    
    def __init__(self):
        self.t = techniques.get_enemy_cursed_technique("Kechi")
        self.defense = list(self.t.defense.keys())
        if len(self.defense) > 1:
            self.defense = random.choice(self.defense)
        else:
            self.defense = self.defense[0]
        super().__init__(
            name="Kechi",
            hp=120,
            max_hp=120,
            attack=80,
            defense=self.defense,
            speed=130,
            xp=20,
            cgp=5,
            technique=self.t.to_dict(),
            imbued=120,
            killed=False,
            equipped=[], timer=20)


class Eso(Enemy):
    min_level = 15
    
    def __init__(self):
        self.t = techniques.get_enemy_cursed_technique("Eso")
        self.defense = list(self.t.defense.keys())
        if len(self.defense) > 1:
            self.defense = random.choice(self.defense)
        else:
            self.defense = self.defense[0]
        super().__init__(
            name="Eso",
            hp=120,
            max_hp=120,
            attack=80,
            defense=self.defense,
            speed=80,
            xp=20,
            cgp=5,
            technique=self.t.to_dict(),
            imbued=120,
            killed=False,
            equipped=[], timer=20)


class Choso(Enemy):
            min_level = 20
            
            def __init__(self):
                self.t = techniques.get_enemy_cursed_technique("Choso")
                self.defense = list(self.t.defense.keys())
                if len(self.defense) > 1:
                    self.defense = random.choice(self.defense)
                else:
                    self.defense = self.defense[0]
                super().__init__(
                    name="Choso",
                    hp=200,
                    max_hp=200,
                    attack=150,
                    defense=self.defense,
                    speed=150,
                    xp=30,
                    cgp=5,
                    technique=self.t.to_dict(),
                    imbued=200,
                    killed=False,
                    equipped=[], timer=60)


class Jogo(Enemy):
        min_level = 30
       
        def __init__(self):
            self.t = techniques.get_enemy_cursed_technique("Jogo")
            self.defense = list(self.t.defense.keys())
            if len(self.defense) > 1:
                self.defense = random.choice(self.defense)
            else:
                self.defense = self.defense[0]
            super().__init__(
            name="Jogo",
            hp=200,
            max_hp=200,
            attack=350,
            defense=self.defense,
            speed=300,
            xp=50,
            cgp=2,
            technique=self.t.to_dict(),
            imbued=300,
            killed=False,
            equipped=[], timer=60)


class Hanami(Enemy):
    min_level = 20
    
    def __init__(self):
        self.t = techniques.get_enemy_cursed_technique("Hanami")
        self.defense = list(self.t.defense.keys())
        if len(self.defense) > 1:
            self.defense = random.choice(self.defense)
        else:
            self.defense = self.defense[0]
        super().__init__(
        name="Hanami",
        hp=300,
        max_hp=300,
        attack=200,
        defense=self.defense,
        speed=200,
        xp=50,
        cgp=2,
        technique=self.t.to_dict(),
        imbued=300,
        killed=False,
        equipped=[], timer=60)

class Dagon(Enemy):
    min_level = 20
    
    def __init__(self):
        self.t = techniques.get_enemy_cursed_technique("Dagon")
        self.defense = list(self.t.defense.keys())
        if len(self.defense) > 1:
            self.defense = random.choice(self.defense)
        else:
            self.defense = self.defense[0]
        super().__init__(
                        name="Dagon",
                        hp=400,
                        max_hp=400,
                        attack=150,
                        defense=self.defense,
                        speed=150,
                        xp=50,
                        cgp=2,
                        technique=self.t.to_dict(),
                        imbued=300,
                        killed=False,
                        equipped=[], timer=60)

class Toji(Enemy):
            min_level = 80
            
            def __init__(self):
                self.t = techniques.get_enemy_cursed_technique("Toji")
                self.defense = list(self.t.defense.keys())
                if len(self.defense) > 1:
                    self.defense = random.choice(self.defense)
                else:
                    self.defense = self.defense[0]
                super().__init__(
                    name="Toji",
                    hp=400,
                    max_hp=400,
                    attack=350,
                    defense=self.defense,
                    speed=350,
                    xp=150,
                    cgp=5,
                    technique=self.t.to_dict(),
                    imbued=0,
                    killed=False,
                    equipped=['Eternal Chain'], timer=90)


class Reggie(Enemy):
        min_level = 40
        def __init__(self):
            self.t = techniques.get_enemy_cursed_technique("Reggie")
            self.defense = list(self.t.defense.keys())
            if len(self.defense) > 1:
                self.defense = random.choice(self.defense)
            else:
                self.defense = self.defense[0]
            super().__init__(
                name="Reggie",
                hp=150,
                max_hp=150,
                attack=150,
                defense=self.defense,
                speed=250,
                xp=50,
                cgp=5,
                technique=self.t.to_dict(),
                imbued=150,
                killed=False,
                equipped=[], timer=90)


class Uro(Enemy):
                min_level = 40
                
                def __init__(self):
                    self.t = techniques.get_enemy_cursed_technique("Uro")
                    self.defense = list(self.t.defense.keys())
                    if len(self.defense) > 1:
                        self.defense = random.choice(self.defense)
                    else:
                        self.defense = self.defense[0]
                    super().__init__(
                        name="Uro",
                        hp=250,
                        max_hp=250,
                        attack=250,
                        defense=self.defense,
                        speed=300,
                        xp=100,
                        cgp=5,
                        technique=self.t.to_dict(),
                        imbued=30,
                        killed=False,
                        equipped=[], timer=80)

class Mahito(Enemy):
                        min_level = 50
                       
                        def __init__(self):
                            self.t = techniques.get_enemy_cursed_technique("Mahito")
                            self.defense = list(self.t.defense.keys())
                            if len(self.defense) > 1:
                                self.defense = random.choice(self.defense)
                            else:
                                self.defense = self.defense[0]
                            super().__init__(
                                name="Mahito",
                                hp=300,
                                max_hp=300,
                                attack=150,
                                defense=self.defense,
                                speed=250,
                                xp=150,
                                cgp=2,
                                technique=self.t.to_dict(),
                                imbued=80,
                                killed=False,
                                equipped=[], timer=100)


class KingOfCurses(Enemy):
                        min_level = 150
                        
                        def __init__(self):
                            self.t = techniques.get_enemy_cursed_technique("King Of Curses")
                            self.defense = list(self.t.defense.keys())
                            if len(self.defense) > 1:
                                self.defense = random.choice(self.defense)
                            else:
                                self.defense = self.defense[0]
                            super().__init__(
                                name="King Of Curses",
                                hp=900,
                                max_hp=900,
                                attack=1000,
                                defense=self.defense,
                                speed=900,
                                xp=200,
                                cgp=5,
                                technique=self.t.to_dict(),
                                imbued=20,
                                killed=False,
                                equipped=[], timer=100)


class Kenjaku(Enemy):
    min_level = 100
    
    def __init__(self):
        self.t = techniques.get_enemy_cursed_technique("Kenjaku")
        self.defense = random.choice(list(self.t.defense.keys()))
        if len(self.defense) > 1:
            self.defense = random.choice(self.defense)
        else:
            self.defense = self.defense[0]
        super().__init__(
            name="Kenjaku",
            hp= 700,
            max_hp=700,
            attack=300,
            defense=self.defense,
            speed=500,
            xp=150,
            cgp=5,
            technique=self.t.to_dict(),
            imbued=150,
            killed=False,
            equipped=[], timer=100)

class Uraume(Enemy):
    min_level = 100
    def __init__(self):
        self.t = techniques.get_enemy_cursed_technique('Uraume')
        self.defense = list(self.t.defense.keys())
        if len(self.defense) > 1:
            self.defense = random.choice(self.defense)
        else:
            self.defense = self.defense[0]
        super().__init__(name="Uraume", hp=900, max_hp=900, attack=200, defense=self.defense, speed = 500, xp=150, cgp=5, technique=self.t, imbued=150, killed = False, equipped = [], timer=100)
    
class Kashimo(Enemy):
    min_level = 100
    def __init__(self):
        self.t = techniques.get_enemy_cursed_technique("Kashimo")
        self.defense = list(self.t.defense.keys())
        if len(self.defense) > 1:
            self.defense = random.choice(self.defense)
        else:
            self.defense = self.defense[0]
        super().__init__(
            name="Kashimo",
            hp=900,
            max_hp=900,
            attack=400,
            defense=self.defense,
            speed=500,
            xp=150,
            cgp=5,
            technique=self.t.to_dict(),
            imbued=150,
            killed=False,
            equipped=[], timer=100)
