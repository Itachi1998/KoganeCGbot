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

    def __init__(self, name: str, level:int, hp: int, max_hp: int, ce: int, max_ce: int, strength: int, speed: int, xp: int, cgp: int, technique: str, colony:int, luck:int, antidomain: bool):
        self.name = name
        self.level= level
        self.hp = hp # be represented by a healthbar
        self.max_hp = max_hp
        self.ce = ce # be represented by a ce bar unless they are ZERO restricted
        self.max_ce = max_ce 
        self.strength = strength # enemy or player strength (physical)
        self.speed = speed # physical speed
        self.xp = xp  # experience points of current player of experience of enemy reward
        self.cgp = cgp # culling game points
        self.technique = technique # cursed technique: will be a cursed technique class name
        self.colony= colony
        self.luck = luck
        self.antidomain = antidomain
        
    def __repr__(self):
        return f"{self.name} - HP: {self.hp}, XP: {self.xp}, CGP: {self.cgp}, Technique: {self.technique}"


    # sukuna.physical_attack_checks(gojo, gojo.defense)
    def physical_attack_checks(self, target, attack, defense, **kwargs):
        try:
            print(f"{self.name} attacks {target.name}")
            speed = self.speed + attack.speed # 100
            strength = self.strength= + attack.strength
            bf = attack.bf
            def_speed = target.speed + defense.speed # 50
            def_strength = target.strenght + defense.strength
            speed_buff_percentage = (def_speed / speed) * 100 # 75+ to have a chance to dodge
            if speed_buff_percentage > 100:
                 return(0, "dodge")
            else:
                                            # 0-15
                result = random.randint(0, speed_buff_percentage)
                if result > 75:
                    return (0, "dodge")
        
            damage = strength - def_strength

            if damage > 0:
                 return (damage, "hit", target.hp <= 0, bf)

            elif damage <= 0:
                 return (damage, 'tank')
            
        except Exception as e:
            print(f"Error in physical_attack_checks: {e}")
    
            
            # if isinstance(other, Enemy):
            #           print(f"{other.name} is an ai, continuing player vs ai physical attack calculations")
            #           t = old_techniques.Techniques(**other.technique)
            #           defense = t.defense[other.defense]
            #           other_speed = t.defense[other.defense]['speed']
                
            # elif isinstance(self, Enemy):
            #     t_name = None
            #     t = old_techniques.get_cursed_technique(other.technique)
            #     if other.defense:
            #         t_name = other.defense.replace(" ","_")
            #     else:
            #         defense_names = list(t.defense.keys())
            #         if len(defense_names) > 1: 
            #             other.defense = random.choice(defense_names)
            #             t_name = other.defense.replace(" ", "_")
            #     physic_dic = self.technique['attack']['Physical']
            #     d_func = None
            #     if t_name:    
            #         d_func = getattr(t, t_name.lower())
            #     else:
            #         t_name = None
            #         if self.technique != 'Heavenly Restriction':
            #             self.defense = 'CE'
            #             t_name = self.defense
            #         else:
            #             self.defense = 'Heavenly Body'
            #             t_name = self.defense.replace(' ', '_')
                    
            #         d_func = getattr(t, t_name.lower())        
            #     results = d_func(self, other, physic_dic)
            #     other.imbued = 0
            #     other.save_to_db()
            #     return results
                
            # tool = None
            # negate = None
            # print(f"{self.name}'s  speed: {speed}, {other.name}'s  {other.defense} speed: {other_speed}")
            
            # if self.equipped is not None:
            #     tool = self.equipped
            # if speed >= other_speed:
            #     spd_calc = max(0, speed - other_speed)
            #     print(f"spd_calc: {spd_calc}")  # log the calculated speed
            #     if spd_calc < 20:
            #         chance_to_hit = random.randint(0, max(1, 200 - (defense['def'] + spd_calc)))
            #     else:
            #         chance_to_hit = random.randint(0, max(1, 200 - defense['def'])) 
            #     damage = self.attack + self.imbued

            #     if tool:
            #         if len(tool) > 1:
            #             tool1 =old_techniques.get_cursed_tool(tool[0])
            #             tool2 = old_techniques.get_cursed_tool(tool[1])
            #             damage += tool1.attack, tool2.attack
            #             if tool1.negate or tool2.negate:
            #                 defense=0
            #                 negate='negate'
            #         else:
            #             tool1 = old_techniques.get_cursed_tool(tool[0])
            #             damage += tool1.attack + tool1.pen  #add tool attack power and penetration to the damage
            #             if tool1.negate:
            #               defense = 0  #negate defense if tool has the ability
            #               negate = 'negate'  #set the negation variable to 'negate
                    
            #     print(f"Chance to Hit: {chance_to_hit}, Damage: {damage}")


            #     if self.technique == "HeavenlyRestriction":
            #         damage += speed  #add the players speed to damage

            #     if chance_to_hit:
            #         other.hp -= damage
            #         print(f"Hit! Damage: {damage}, Enemy HP: {other.hp}")
            #         return (
            #             damage, "hit", other.hp <= 0, tool)  #add negate variable to check if the hit negated defense
            #     else:
            #         print("Tanked! Enemy HP not reduced")
            #         return (0, "tank", other.hp <= 0, tool)
            # else:
            #     print("Missed! Speed too low")
            #     return (0, "miss", other.hp <= 0, tool)

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
                t= old_techniques.Techniques(**self.technique)
                atk = t.attack[technique]
                target_tech = old_techniques.get_cursed_technique(target.technique)
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
                t = old_techniques.get_cursed_technique(self.technique)
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
                t = old_techniques.get_cursed_technique(self.technique)
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
                
    
        def use_cursed_tool(self, tool: dict, **kwargs):
                pass
        
        def domain(self, **kwargs):
             pass
     




class Enemy(Actor):

    def __init__(self, name: str, level: int, hp: int, max_hp: int, strength: int, speed: int, xp: int, cgp: int, technique: dict,killed: bool, timer: int, colony: int, equipped: list, ce:int, max_ce: int, killed_by: str=None):
        super().__init__(name, level, hp, max_hp, strength, speed, xp, cgp,
                         technique, colony)
        self.name = name
        self.level = level
        self. hp = hp
        self.max_hp = max_hp
        self.killed = killed
        self.timer = timer
        self.strength = strength
        self.speed = speed
        self.equipped = equipped
        self.colony = colony
        self.technique = technique
        self.cgp = cgp
        self.xp = xp
        self.ce = ce
        self.max_ce= max_ce
        if killed_by:
             self.killed_by=killed_by
    
    
    
    def __repr__(self):
        return f"Enemy: {self.name} - HP: {self.hp}, XP: {self.xp}, CGP: {self.cgp}, Technique: {self.technique} - in colony: {self.colony}"

    


class Character(Actor):
    level_cap = 200
    def __init__(self, 
                 name: str, 
                 hp: int, 
                 max_hp: int,
                strength: int, 
                speed: int, 
                xp: int, 
                cgp: int, 
                technique: dict,  
                colony: int, 
                inventory: list, 
                equipped: list, 
                status: int, 
                user_id: int, 
                skp: int,
                charclass: int,
                HR: int=None,
                RCT: bool=False,
                domain: bool=False,
                maximum: bool=False
                ):
        super().__init__(name, hp, max_hp, strength, speed, xp, cgp, technique, colony)
        self.name = name
        self.hp = hp
        self.max_hp = max_hp
        self.strength = strength
        self.speed = speed
        self.xp = xp
        self.cgp = cgp
        self.technique = technique
        self.colony = colony
        self.inventory = inventory
        self.equipped = equipped
        self.status = status
        self.user_id = user_id
        self.skp = skp
        self.HR = HR,
        self.RCT= RCT,
        self.charclass=charclass
        self.domain = domain,
        self.maximum = maximum


    def __repr__(self):
        return f"Character: {self.name} - HP: {self.hp}, XP: {self.xp}, CGP: {self.cgp}, Technique: {self.technique} - belonging to user_id: {self.user_id} - in colony: {self.colony}"
    
        

    
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


    #spawn a shikigami, curse, mechabot, or ultimate mechabot
    def spawn(self, **kwargs):
        self.curse = []
        self.shikigami = []
        self.mechabot = []
        self.ultimateMechabot = []

        for k, v in kwargs.items():
            try:
                if k == 'Shikigami':
                    self.shikigami.append([{k:v}])
                    return True
                if k == 'Curse':
                    self.curse.append([{k:v}])
                    return True
                if k == 'Mechabot':
                    self.mechabot.append([{k:v}])
                    return True
                if k == 'UltimateMechabot':
                    self.ultimateMechabot.append([{k:v}])
                    return True
                if k == 'ShadowInventory':
                    self.inventory.append({k:v})
                    return True
                self.save_to_db()

            except Exception as e:
                print(f"Failed to spawn {k} {e} due to {e}")
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

                    self.save_to_db()
                    xp_needed = self.ready_level_up()[1]
                    if self.xp >= xp_needed:
                        continue
                    else:
                        break
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

    def save_to_db(self):
        save_player(self) #the imported save_player method from the database file

    def run(self, target: dict):
        self_speed = self.speed + self.imbued  #add the players imbued speed to their speed
        target_speed = target.speed + target.imbued #add the targets imbued speed to their speed
        if self_speed > target_speed:
            chance = random.randint(0, (200 - (self_speed - target_speed)))
            if chance < 5:
                return False
            else:
                return True

    def pve(self, colony_id: int) -> Union[List['Enemy'], 'Enemy']:
        pass
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
        
class Grade4_BugFly(Enemy):
    min_level = 1
    def __init__(self):
        super.init(
            name="BugFly", 
            hp=20, 
            max_hp=20, 
            strength=10, 
            speed=40, 
            xp=10, 
            cgp=5, 
            technique=Bugyfly,
            killed=False, 
            timer=1, 
            colony=None, 
            equipped=[], 
            avatar=None, 
            quantity=random.choice([1, 2, 3, 4, 5]) * 10, 
            ce=20, 
            max_ce=20)


class  Grade4_FloatJelly(Enemy):
    min_level = 1
    def __init__(self):
        super.init(
            name="FloatJelly", 
            hp=30, 
            max_hp=30, 
            strength=20, 
            speed=10, 
            xp=10, 
            cgp=5, 
            technique=FloatJelly,
            killed=False, 
            timer=1, 
            colony=None, 
            equipped=[], 
            avatar=None, 
            quantity=random.choice([1, 2, 3, 4, 5]) * 10, 
            poisonous=(True, 2), 
            ce=20, 
            max_ce=20)

    
class Grade4_FlyMouth(Enemy):
    min_level= 1
    def __init__(self):
        super.init(
                name="Flymouth curse"
                max_hp=40, 
                strength=30, 
                speed=30, 
                xp=10, 
                cgp=5, 
                technique=Flymouth,
                killed=False, 
                timer=1, 
                colony=1, 
                equipped=[], 
                avatar=None, 
                quantity=random.choice([0.5, 1, 2]) * 10,
                ce=20, 
                max_ce=20)


class Grade3_Backhand(Enemy):
    min_level = 1
    def __init__(self):
        super.init(
            name="Backhand Curse", 
            hp=150,
            max_hp=150, 
            strength=60, 
            speed=200, 
            xp=20, 
            cgp=5, 
            technique=Backhand, 
            killed=False, 
            timer=20, 
            colony=None, 
            equipped=[],
            avatar=None, 
            ce=50, 
            max_ce=50
            )

class Grade3_Furrpede(Enemy):
    min_level = 1
    def __init__(self):
      super.init(
        name="Furrpede curse", 
        hp=150, 
        max_hp=150, 
        strength=80, 
        speed=150, 
        xp=20, 
        cgp=5, 
        technique=Furrpede, 
        imbued=150, 
        killed=False, 
        timer=20, 
        colony=None, 
        equipped=[], 
        avatar=None, 
        ce=50, 
        max_ce=50
        )

class Grade3_AnxiousEars(Enemy):
    min_level = 1
    def __init__(self):
        super.init(
            ame="AnxiousEars Curse",
            hp=200, 
            max_hp=200, 
            strength=100, 
            speed=100, 
            xp=20, 
            cgp=5, 
            technique=AnxiousEars,
            imbued=150, 
            killed=False, 
            timer=20, 
            colony=None, 
            equipped=[], 
            avatar=None, 
            ce=50, 
            max_ce=50)

class Grade2_StingerSpore(Enemy):
    min_level = 1
    def __init__(self):
        super.init(
            name="Stinger-Spore", 
            hp=300, 
            max_hp=300, 
            strength=150, 
            speed=200, 
            xp=30, 
            cgp=5, 
            technique=StingerSpore, 
            imbued=200, 
            killed=False, 
            timer=60, 
            colony=1, 
            equipped=[], 
            avatar=None, 
            ce=100, 
            max_ce=100, 
            poisounous=(True, 10)
            )


class Grade2_Monkeybrain(Enemy):
    min_level = 1
    def __init__(self):
        super.init(
            name="MonkeyBrain", 
            hp=300, 
            max_hp=300, 
            strength=150, 
            speed=200, 
            xp=30, 
            cgp=5, 
            technique=Monkeybrain, 
            killed=False, 
            timer=60, 
            colony=None, 
            equipped=[], 
            avatar=None, 
            ce=100, 
            max_ce=100
            )


class Grade1_OrbMaster(Enemy):
    min_level = 1
    def __init__(self):
        super.init(
            name="OrbMaster", 
            hp=400, 
            max_hp=400, 
            strength=300, 
            speed=500, 
            xp=40, 
            cgp=5, 
            technique=Orbmaster,  
            killed=False, 
            timer=60, 
            colony=1, 
            equipped=[], 
            avatar=None, 
            ce=150, 
            max_ce=150
            )

class Grade1_Charger(Enemy):
    min_level = 1
    def __init__(self):
        super.init(
            name="Charger", 
            hp=400,
            max_hp=400, 
            strength=400, 
            speed=600, 
            xp=40, 
            cgp=5, 
            technique=ElectricCharge,
            killed=False, 
            timer=60, 
            colony=1, 
            equipped=[], 
            avatar=None, 
            ce=150, 
            max_ce=150
            )

class SpecialGrade_FingerBearer(Enemy):
    min_level = 1
    def __init__(self):
        super.init(
             name="Finger Bearer",
               hp=600, 
               max_hp=600, 
               strength=800, 
               speed=700, 
               xp=50, 
               cgp=5, 
               technique=Fingerbear,  
               killed=False, 
               timer=60, 
               colony=None, 
               equipped=[{'finger':1}], 
               avatar=None,
               ce=200, 
               max_ce=200
               )


class SpecialGrade_Obstacle(Enemy):
    min_level = 1
    def __init__(self):
        super.init(
             name="Obstacle",
               hp=900, 
               max_hp=900, 
               strength=300, 
               speed=600, 
               xp=50, 
               cgp=5, 
               technique=ObstacleRemoval,  
               killed=False, 
               timer=60, 
               colony=None, 
               avatar=None,
               ce=300, 
               max_ce=300
               )

class SpecialGrade_DisasterFlame(Enemy):
        min_level = 30
        def __init__(self):
            super().__init__(
            name="Distaster Flame Curse",
            hp=800,
            max_hp=800,
            strength=900,
            speed=900,
            xp=200,
            cgp=5,
            technique=DisasterFire,
            killed=False
            timer=200,
            equipped=[], 
            killcount=[], 
            avatar=None,
            colony=None,
            ce=600,
            max_ce=600,
            domain=True)


class SpecialGrade_NatureSpirit(Enemy):
        min_level = 30
        def __init__(self):
            super().__init__(
            name="Spirit of Nature",
            hp=1200,
            max_hp=1200,
            strength=700,
            speed=700,
            xp=200,
            cgp=5,
            technique=NatureManipulation,
            timer=200,
            killed=False,
            equipped=[], 
            killcount=[], 
            avatar=None,
            colony=None,
            ce=300,
            max_ce=300,
            domain=True)


class SpecialGrade_TideCurse(Enemy):
        min_level = 30
        def __init__(self):
            super().__init__(
            name="Disaster Tides Curse",
            hp=1500,
            max_hp=1500,
            strength=400,
            speed=400,
            xp=200,
            cgp=5,
            technique=DisasterTides,
            killed=False,
            timer=200,
            equipped=[], 
            killcount=[],
            shikigami=[], 
            avatar=None,
            colony=None,
            ce=500,
            max_ce=500,
            domain=True)




class SpecialGrade_DeathSpirit(Enemy):
        min_level = 30
        def __init__(self):
            super().__init__(
            name="Disaster Human Curse",
            hp=1500,
            max_hp=1500,
            strength=400,
            speed=400,
            xp=200,
            cgp=5,
            technique=SoulManipulation,
            killed=False,
            timer=200,
            equipped=[], 
            killcount=[],
            shikigami=[], 
            avatar=None,
            colony=None,
            ce=500,
            max_ce=8500,
            domain=True)






class SpecialGrade_ThreeFingerSukuna():
     min_level = 30
     def __init__(self):
            super().__init__(
            name="King of Curses: 3 Fingers",
            hp=1200,
            max_hp=1200,
            strength=1000,
            speed=1000,
            xp=500,
            cgp=5,
            technique=Shrine,
            killed=False,
            timer=300,
            equipped=[{'fingers': 3}], 
            killcount=[{'killed' : []}],
            shikigami=[], 
            avatar=None,
            colony=None,
            ce=1000,
            max_ce=1000,
            domain=True, 
            )


class Toji(Enemy):
            min_level = 80
            def __init__(self):
                super().__init__(
                    name="Toji",
                    hp=900,
                    max_hp=900,
                    strength=1500,
                    speed=2000,
                    xp=700,
                    cgp=5,
                    technique=PhysicalRestriction,
                    colony=None,
                    killed=False,
                    timer=300,
                    equipped=['Eternal Chain', 'ISOH'], 
                    timer=300,
                    antidomain=True
                    )



class Reggie(Enemy):
        min_level = 30
        def __init__(self):
            super().__init__(
                name="Reggie",
                hp=500,
                max_hp=500,
                strength=500,
                speed=800,
                xp=500,                
                cgp=5,
                technique=Receipts,
                killed=False,
                equipped=[{'receipts' : 5000}], 
                timer=300,
                ce=500,
                max_ce=500)


class Uro(Enemy):
                min_level = 40
                def __init__(self):
                    super().__init__(
                        name="Uro",
                        hp=450,
                        max_hp=450,
                        strength=650,
                        speed=700,
                        xp=100,
                        cgp=5,
                        technique=SkyManip,
                        killed=False,
                        equipped=[], 
                        timer=200,
                        ce=450,
                        ce_max=450)





class KingOfCurses(Enemy):                  
                        min_level = 150
                        def __init__(self):
                     
                            super().__init__(
                                name="King Of Curses",
                                hp=900,
                                max_hp=900,
                                strength=7000, # highest NPC strength in the game
                                speed=7000, # highest NPC speed in the game
                                xp=200,
                                cgp=5,
                                technique=Shrine,
                                killed=False,
                                equipped=[], 
                                timer=500
                                )


class Kenjaku(Enemy):
    min_level = 100
    
    def __init__(self):
     
        super().__init__(
            name="Kenjaku",
            hp= 700,
            max_hp=700,
            strength=3000,
            speed=5000,
            xp=150,
            cgp=5,
            technique=Kenjaku,
            imbued=150,
            killed=False,
            equipped=[], 
            timer=500
            )

class Uraume(Enemy):
    min_level = 100
    def __init__(self):
        super().__init__(
            name="Uraume", 
            hp=900, 
            max_hp=900, 
            strength=5000,
            speed = 5000, 
            xp=150, 
            cgp=5, 
            technique=Frozen, 
            imbued=150, 
            killed = False, 
            equipped = [], 
            timer=500
            )
    
class Kashimo(Enemy):
        min_level=120
        super().__init__(
            name="Kashimo",
            hp=900,
            max_hp=900,
            strength=4000,
            speed=5000,
            xp=150,
            cgp=5,
            technique=Kashimo,
            imbued=150,
            killed=False,
            timer=100,
            equipped=[]
            )
