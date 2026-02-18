import traceback, os, db
import enum, random
from copy import deepcopy
from dataclasses import dataclass, field

class Status(enum.Enum):
    """Class for showing which game mode player is in"""
    ROAM, PVP, PVE = range(3)



@dataclass
class BodyPart:
    """Class for body parts of entities"""
    name: str
    hp: int
    ce: int
    max_hp: int
    max_ce: int
    soul_ce: int = 0
        
    def poison_damage(self, hp_damage=0):
        self.hp = max(self.hp - hp_damage, 0)

    def take_damage(self, damage_type, amount):
        total_damage = amount
        if damage_type == "hp":
            total_damage = max(amount - self.ce, 0)
            self.hp = max(self.hp - total_damage, 0)
            return total_damage
        
        elif damage_type == "soul":
            total_damage = max(amount - self.soul_ce, 0)
            self.hp = max(self.hp - total_damage, 0)
            self.max_hp = self.hp
            return total_damage
 
    def is_destroyed(self):
        return self.hp <= 0
    
    def hp_percentage(self):
        return (self.hp / self.max_hp) * 100 if self.max_hp > 0 else 0
    
    def ce_percentage(self):
        return (self.ce / self.max_ce) * 100 if self.max_ce > 0 else 0
    
    def restore(self, hp_amount=0, ce_amount=0, soul_amount=0):
        self.hp = min(self.hp + hp_amount, self.max_hp)
        self.ce = min(self.ce + ce_amount, self.max_ce)
        self.soul_ce = min(self.soul_ce + soul_amount, self.max_hp)

    def buff(self, hp_buff=0, ce_buff=0, soul_ce_buff=0):
        self.hp = min(self.hp + hp_buff, self.max_hp)
        self.max_ce += ce_buff
        self.hp = min(self.hp + hp_buff, self.max_hp)
        self.ce = min(self.ce + ce_buff, self.max_ce)
        self.soul_ce = min(self.soul_ce + soul_ce_buff, self.max_hp)


@dataclass
class Entity:
    """Entity class for players and npcs to inherit from"""
    name: str
    level: int
    hp: int
    max_hp: int
    ce: int
    max_ce: int
    speed: int
    strength: int
    grade: int 
    player_type: str
    playerclass: str
    is_reincarnate: bool = False
    is_alive: bool = True
    is_flying: bool = False
    is_stunned: bool = False
    is_poisoned: bool = False
    six_eyes: bool = False
    cgp_reward: int = 0
    charges: int = 0
    colony_id: int = 0
    body_parts: dict = field(default_factory=dict)
    techniques: list = field(default_factory=list)
    buffs: dict = field(default_factory=dict)



    
@dataclass
class Player(Entity):
    """Player class for player entitites"""
    status: int = Status.ROAM
    user_id: int = None
    skillpoints: int = 0
    rules_added: dict = field(default_factory=dict)
    inventory: dict = field(default_factory=dict)
    tech_inventory: dict = field(default_factory=dict)
    equipped: dict = field(default_factory=dict)
    techs_activated: dict = field(default_factory=dict)


    def get_grade(self) -> str:
        if self.grade == 1:
            return "Grade 4"
        elif self.grade == 2:
            return "Grade 3"
        elif self.grade == 3:
            return "Grade 2"
        elif self.grade == 4:
            return "Grade 1"
        elif self.grade == 5:
            return "Special Grade"
    
    def get_status(self) -> str:
        if self.status == Status.ROAM:
            return "Roaming"
        elif self.status == Status.PVP:
            return "In PvP"
        elif self.status == Status.PVE:
            return "In PvE"
        
    def level_up(self, xp) -> tuple[bool, int]:
        max_level = 100
        required_xp = self.level * 100
        if xp >= required_xp and self.level < max_level:
            self.level += 1
            if self.level <= 20:
                self.skillpoints += self.level
            if self.level > 20 and self.level <= 50:
                self.skillpoints += 20 + self.level
            if self.level > 50:
                self.skillpoints += 50 + self.level
            return True, self.level
        else:
            return False, required_xp - xp
    
    def add_to_inventory(self, item: dict) -> bool:
        if item['equipped'] == True:
            item['equipped'] = False
        else:
            return False
        item_name = item['name']
        for k, v in self.inventory.items():
            if k == item_name:
                if self.inventory[k]['quantity'] + item['quantity'] < self.inventory[k]['max_stack']:
                    self.inventory[k]['quantity'] += item['quantity']
                    return True
                else:
                    return False
        self.inventory[item_name] = item
        return True
    
    def equip_item(self, item: dict) -> bool:
        item_name = item['name']
        for k in self.equipped.keys():
            if k == item['type']:
                if self.equipped[k]:
                    if self.equipped[k]['dual_wield'] and item['dual_wield']:
                        self.equipped[k] = item
                        return True
                    else:
                        return False
                else:
                    self.equipped[k] = item
                    return True

    

    def upgrade_attr(self, points, attr_name) -> int:
        if self.skillpoints >= points:
            if attr_name == "hp":
                self.max_hp += points * 10
                self.hp += points * 10
            elif attr_name == "ce":
                self.max_ce += points * 5
                self.ce += points * 5
            elif attr_name == "speed":
                self.speed += points * 2
            elif attr_name == "strength":
                self.strength += points * 2
            self.skillpoints -= points
            return True
        else:
            return False
    
    def ready_level_up(self) -> tuple[bool, int]:
        max_level = 100
        required_xp = self.level * 100
        return self.level < max_level and self.xp >= required_xp, required_xp - self.xp
    

@dataclass
class NPC(Entity):
    """NPC class for non player entities"""
    tamed: bool = False
    owner_id: int = None
    xp_reward: int = 0
    quantity: int = 1
    is_tamed: bool = False
    tamed_by: int = None

floatjelly_hp = 30
floatjelly_ce = 40
FloatJelly = NPC(
    name="Float Jelly",
    level=1,
    hp=floatjelly_hp,
    max_hp=floatjelly_hp,
    ce=floatjelly_ce,
    max_ce=floatjelly_ce,
    speed=10,
    strength=40,
    grade=1,
    player_type="NPC",
    playerclass="Curse",
    xp_reward=2,
    cgp_reward=2,
    techniques=["FloatJelly"],
    quantity=random.randrange(3,8),
    body_parts={"head" : BodyPart(name="head", hp=floatjelly_hp, ce=0, max_hp=floatjelly_hp, max_ce=0)}
)

bugfly_hp = 20
bugfly_ce =50
BugFly = NPC(
    name="Bug Fly",
    level=1,
    hp=bugfly_hp,
    max_hp=bugfly_hp,
    ce=bugfly_ce,
    max_ce=bugfly_ce,
    speed=50,
    strength=20,
    grade=1,
    player_type="NPC",
    playerclass="Curse",
    xp_reward=2,
    cgp_reward=2,
    is_flying=True,
    techniques=["BugFly"],
    quantity=random.randrange(2,8),
    body_parts={"head" : BodyPart(name="head", hp=bugfly_hp, ce=0, max_hp=bugfly_hp, max_ce=0)}

)

batmouth_hp = 40
batmouth_ce = 60
BatMouth = NPC(
    name="Bat Mouth",
    level=1,
    hp=batmouth_hp,
    max_hp=batmouth_hp,
    ce=batmouth_ce,
    max_ce=batmouth_ce,
    speed=20,
    strength=30,
    grade=1,
    player_type="NPC",
    playerclass="Curse",
    xp_reward=2,
    cgp_reward=2,
    techniques=["FlyMouth"],
    quantity=random.randrange(2,5),
    body_parts={"head" : BodyPart(name="head", hp=batmouth_hp, ce=0, max_hp=batmouth_hp, max_ce=0)}
)



barehand_hp = 150
barehand_ce = 200
BareHand = NPC(
    name="Bare Hand",
    level=10,
    hp=barehand_hp,
    max_hp=barehand_hp,
    ce=barehand_ce,
    max_ce=barehand_ce,
    speed=100,
    strength=100,
    grade=2,
    player_type="NPC",
    playerclass="Curse",
    xp_reward=10,
    cgp_reward=2,
    techniques=['BareHand'],
    quantity=1,
    body_parts= {"head" : BodyPart(name="head", hp=barehand_hp * 50 // 100, ce=0, max_hp=barehand_hp * 50 // 100, max_ce=0),
                  "hand_1" : BodyPart(name="hand", hp=barehand_hp * 17 // 100, ce=0, max_hp=barehand_hp * 17 // 100, max_ce=0), 
                  "hand_2" : BodyPart(name="hand", hp=barehand_hp * 17 // 100, ce=0, max_hp=barehand_hp * 17 // 100, max_ce=0), 
                  "hand_3" : BodyPart(name="hand", hp=barehand_hp * 16 // 100, ce=0, max_hp=barehand_hp * 16 // 100, max_ce=0)}
)


furrpede_hp = 200
furrpede_ce = 200
Furrpede = NPC(
    name="Furrpede",
    level=10,
    hp=furrpede_hp,
    max_hp=furrpede_hp,
    ce=furrpede_ce,
    max_ce=furrpede_ce,
    speed=50,
    strength=150,
    grade=2,
    player_type="NPC",
    playerclass="Curse",
    xp_reward=10,
    cgp_reward=2,
    techniques=['Furrpede'],
    quantity=1,
    body_parts= {
        "head" : BodyPart(name="head", hp=furrpede_hp * 20 // 100, ce=0, max_hp=furrpede_hp * 20 // 100, max_ce=0),
         "body" : BodyPart(name="body", hp=furrpede_hp * 50 // 100, ce=0, max_hp=furrpede_hp * 50 // 100, max_ce=0),
         "hands" : BodyPart(name="hands", hp=furrpede_ce * 30 // 100, ce=0, max_hp= furrpede_ce * 30 // 100, max_ce=0)
         }
)


onewisemonkey_hp = 250
onewisemonkey_ce = 200
OneWiseMonkey = NPC(
    name="One Wise Monkey",
    level=10,
    hp=onewisemonkey_hp,
    max_hp=onewisemonkey_hp,
    ce=onewisemonkey_ce,
    max_ce=onewisemonkey_ce,
    speed=60,
    strength=150,
    grade=2,
    player_type="NPC",
    playerclass="Curse",
    xp_reward=10,
    cgp_reward=2,
    techniques=['OneWiseMonkey'],
    quantity=1,
    body_parts= {
        "head" : BodyPart(name="head", hp=onewisemonkey_hp * 50 // 100, ce=0, max_hp=onewisemonkey_hp * 30 // 100, max_ce=0),
        "arms" : BodyPart(name="arms", hp=onewisemonkey_hp * 25 // 100, ce=0, max_hp=onewisemonkey_hp * 25 // 100, max_ce=0),
        "legs" : BodyPart(name="legs", hp=onewisemonkey_hp * 25 // 100, ce=0, max_hp=onewisemonkey_hp * 25 // 100, max_ce=0)        
         }
)

stinkaspore_hp = 350
stinkaspore_ce = 350
Stinkaspore = NPC(
    name="Stinkaspore",
    level=20,
    hp=stinkaspore_hp,
    max_hp=stinkaspore_hp,
    ce=stinkaspore_ce,
    max_ce=stinkaspore_ce,
    speed=150,
    strength=250,
    grade=3,
    player_type="NPC",
    playerclass="Curse",
    xp_reward=20,
    cgp_reward=2,
    techniques=['Stinkaspore'],
    quantity=1,
    body_parts = {
        "head" : BodyPart(name="head", hp=stinkaspore_hp * 20 // 100, ce=0, max_hp=stinkaspore_hp * 20 // 100, max_ce=0),
        "body" : BodyPart(name="body", hp=stinkaspore_hp * 50 // 100, ce=0, max_hp=stinkaspore_hp * 50 // 100, max_ce=0),
        "stingers" : BodyPart(name="stingers", hp=stinkaspore_hp * 30 // 100, ce=0, max_hp=stinkaspore_hp * 30 // 100, max_ce=0)
    }
)


primate_hp = 400
primate_ce = 300
Primate = NPC(
    name="Primate",
    level=20,
    hp=primate_hp,
    max_hp=primate_hp,
    ce=primate_ce,
    max_ce=primate_ce,
    speed=250,
    strength=300,
    grade=3,
    player_type="NPC",
    playerclass="Curse",
    xp_reward=20,
    cgp_reward=2,
    techniques=['Primate'],
    quantity=1,
    body_parts= {
        "head" : BodyPart(name="head", hp=primate_hp * 10 // 100, ce=0, max_hp=primate_hp * 20 // 100, max_ce = 0),
        "body" : BodyPart(name="body", hp=primate_hp * 50 // 100, ce=0, max_hp=primate_hp * 50 // 100, max_ce=0),
        "arm_1" : BodyPart(name="left arm", hp=primate_hp * 10 // 100, ce=0, max_hp=primate_hp * 10 // 100, max_ce=0),
        "arm_2" : BodyPart(name="right arm", hp=primate_hp * 10 // 100, ce=0, max_hp=primate_hp * 10 // 100, max_ce=0),
        "leg_1" : BodyPart(name="left leg", hp=primate_hp * 10 // 100, ce=0, max_hp=primate_hp * 10 // 100, max_ce=0),
        "leg_2" : BodyPart(name="right leg", hp=primate_hp * 10 // 100, ce=0, max_hp=primate_hp * 10 // 100, max_ce=0)
    }
)


orbmaster_hp = 400
orbmaster_ce = 500
Orbmaster = NPC(
    name="Orbmaster",
    level=40,
    hp=orbmaster_hp,
    max_hp=orbmaster_hp,
    ce=orbmaster_ce,
    max_ce=orbmaster_ce,
    speed=300,
    strength=200,
    grade=4,
    player_type="NPC",
    playerclass="Curse",
    xp_reward=40,
    cgp_reward=2,
    techniques=['Orbmaster'],
    quantity=1,
    body_parts = {
        "head" : BodyPart(name="head", hp=orbmaster_hp * 10 // 100, ce=0, max_hp=orbmaster_hp * 10 // 100, max_ce=0),
        "body" : BodyPart(name="body", hp=orbmaster_hp * 50 // 100, ce=0, max_hp=orbmaster_hp * 50 // 100, max_ce= 0),
        "arm_1" : BodyPart(name="left arm", hp=orbmaster_hp * 10 // 100, ce=0, max_hp=orbmaster_hp * 10 // 100, max_ce=0),
        "arm_2" : BodyPart(name="right arm", hp=orbmaster_hp * 10 // 100, ce=0, max_hp=orbmaster_hp * 10 // 100, max_ce=0),
        "leg_1" : BodyPart(name="left leg", hp=orbmaster_hp * 10 // 100, ce=0, max_hp=orbmaster_hp * 10 // 100, max_ce=0),
        "leg_2" : BodyPart(name="right leg", hp=orbmaster_hp * 10 // 100, ce=0, max_hp=orbmaster_hp * 10 // 100, max_ce=0)
    }
)


electrocharge_hp = 500
electrocharge_ce = 700
Electrocharge = NPC(
    name="Electrocharge",
    level=40,
    hp=electrocharge_hp,
    max_hp=electrocharge_hp,
    ce=electrocharge_ce,
    max_ce=electrocharge_ce,
    speed=400,
    strength=300,
    grade=4,
    player_type="NPC",
    playerclass="Curse",
    xp_reward=40,
    cgp_reward=2,
    techniques=['Electrocharge'],
    quantity=1,
    body_parts= {
        "head" : BodyPart(name="head", hp=electrocharge_hp * 10 // 100, ce=0, max_hp=electrocharge_hp * 10 // 100, max_ce=0),
        "body" : BodyPart(name="body", hp=electrocharge_hp * 50 // 100, ce=0, max_hp=electrocharge_hp * 50 // 100, max_ce=0),
        "arm_1" : BodyPart(name="left arm", hp=electrocharge_hp * 10 // 100, ce=0, max_hp=electrocharge_hp * 10 // 100, max_ce=0),
        "arm_2" : BodyPart(name="right arm", hp=electrocharge_hp * 10 // 100, ce=0, max_hp=electrocharge_hp * 10 // 100, max_ce=0),
        "leg_1" : BodyPart(name="left leg", hp=electrocharge_hp * 10 // 100, ce=0, max_hp=electrocharge_hp * 10 // 100, max_ce=0),
        "leg_2" : BodyPart(name="right leg", hp=electrocharge_hp * 10 // 100, ce=0, max_hp=electrocharge_hp * 10 // 100, max_ce=0)  
    }
)

fingerbearer_hp = 1000
fingerbearer_ce= 1000
Fingerbearer= NPC(
    name="Fingerbearer",
    level=40,
    hp=fingerbearer_hp,
    max_hp=fingerbearer_hp,
    ce=fingerbearer_ce,
    max_ce=fingerbearer_ce,
    speed=650,
    strength=650,
    grade=5,
    player_type="NPC",
    playerclass="Curse",
    xp_reward=60,
    cgp_reward=2,
    techniques=['Fingerbearer'],
    quantity=1,
    body_parts= {
        "head" : BodyPart(name="head", hp=fingerbearer_hp * 10 // 100, ce=0, max_hp=fingerbearer_hp * 10 // 100, max_ce=0),
        "body" : BodyPart(name="body", hp=fingerbearer_hp * 50 // 100, ce=0, max_hp=fingerbearer_hp * 50 // 100, max_ce=0),
        "arm_1" : BodyPart(name="left arm", hp=fingerbearer_hp * 10 // 100, ce=0, max_hp=fingerbearer_hp * 10 // 100, max_ce=0),
        "arm_2" : BodyPart(name="right arm", hp=fingerbearer_hp * 10 // 100, ce=0, max_hp=fingerbearer_hp * 10 // 100, max_ce=0),
        "leg_1" : BodyPart(name="left leg", hp=fingerbearer_hp * 10 // 100, ce=0, max_hp=fingerbearer_hp * 10 // 100, max_ce=0),
        "leg_2" : BodyPart(name="right leg", hp=fingerbearer_hp * 10 // 100, ce=0, max_hp=fingerbearer_hp * 10 // 100, max_ce=0)  
    }
)


dis_flame_hp = 1500
dis_flame_ce = 1500
DisasterFlame = NPC(
    name="Disaster Flame",
    level=50,
    hp=dis_flame_hp,
    max_hp=dis_flame_hp,
    ce=dis_flame_ce,
    max_ce=dis_flame_ce,
    speed=1500,
    strength=1500,
    grade=5,
    player_type="NPC",
    playerclass="Curse",
    xp_reward=80,
    cgp_reward=2,
    techniques=['DisasterFlame'],
    quantity=1,
    body_parts= {
"head" : BodyPart(name="head", hp=dis_flame_hp * 10 // 100, ce=0, max_hp=dis_flame_hp * 10 // 100, max_ce=0),
"body" : BodyPart(name="body", hp=dis_flame_hp * 50 // 100, ce=0, max_hp=dis_flame_hp * 50 // 100, max_ce=0),
"arm_1" : BodyPart(name="left arm", hp=dis_flame_hp * 10 // 100, ce=0, max_hp=dis_flame_hp * 10 // 100, max_ce=0),
"arm_2" : BodyPart(name="right arm", hp=dis_flame_hp * 10 // 100, ce=0, max_hp=dis_flame_hp * 10 // 100, max_ce=0),
"leg_1" : BodyPart(name="left leg", hp=dis_flame_hp * 10 // 100, ce=0, max_hp=dis_flame_hp * 10 // 100, max_ce=0),
"leg_2" : BodyPart(name="right leg", hp=dis_flame_hp * 10 // 100, ce=0, max_hp=dis_flame_hp * 10 // 100, max_ce=0)
    }
)




nature_hp = 2000
nature_ce = 1200
Nature = NPC(
    name="Nature Spirit",
    level=50,
    hp=nature_hp,
    max_hp=nature_hp,
    ce=nature_ce,
    max_ce=nature_ce,
    speed=1000,
    strength=1000,
    grade=5,
    player_type="NPC",
    playerclass="Curse",
    xp_reward=80,
    cgp_reward=2,
    techniques=['Nature'],
    quantity=1,
    body_parts= {
"head" : BodyPart(name="head", hp=nature_hp * 10 // 100, ce=0, max_hp=nature_hp * 10 // 100, max_ce=0),
"body" : BodyPart(name="body", hp=nature_hp * 50 // 100, ce=0, max_hp=nature_hp * 50 // 100, max_ce=0),
"arm_1" : BodyPart(name="left arm", hp=nature_hp * 10 // 100, ce=0, max_hp=nature_hp * 10 // 100, max_ce=0),
"arm_2" : BodyPart(name="right arm", hp=nature_hp * 10 // 100, ce=0, max_hp=nature_hp * 10 // 100, max_ce=0),
"leg_1" : BodyPart(name="left leg", hp=nature_hp * 10 // 100, ce=0, max_hp=nature_hp * 10 // 100, max_ce=0),
"leg_2" : BodyPart(name="right leg", hp=nature_hp * 10 // 100, ce=0, max_hp=nature_hp * 10 // 100, max_ce=0),
    }
)


tide_hp = 1200
tide_ce = 1000
TideCurse = NPC(
name="Disaster Tides",
level=50,
hp=tide_hp,
max_hp=tide_hp,
ce=tide_ce,
max_ce=tide_ce,
speed=800,
strength=800,
grade=5,
player_type="NPC",
playerclass="Curse",
xp_reward=80,
cgp_reward=2,
techniques=['TideCurse'],
quantity=1,
body_parts= {
    "head" : BodyPart(name="head", hp=tide_hp * 17 // 100, ce=0, max_hp=tide_hp * 10 // 100, max_ce=0),
    "body" : BodyPart(name="body", hp=tide_hp * 50 // 100, ce=0, max_hp=tide_hp * 50 // 100, max_ce=0),
    "arm_1" : BodyPart(name="left arm", hp=tide_hp * 16 // 100, ce=0, max_hp=tide_hp * 16 // 100, max_ce=0),
    "arm_2" : BodyPart(name="right arm", hp=tide_hp * 16 // 100, ce=0, max_hp=tide_hp * 17 // 100, max_ce=0)
    }
)



femhito_hp = 2000
femhito_ce = 1500
Femhito = NPC(
    name="Femhito",
    level=50,
    hp=femhito_hp,
    max_hp=femhito_hp,
    ce=femhito_ce,
    max_ce=femhito_ce,
    speed=1000,
    strength=1000,
    grade=5,
    player_type="NPC",
    playerclass="Curse",
    xp_reward=100,
    cgp_reward=2,
    techniques=['Femhito'],
    quantity=1,
    body_parts= {
        "head" : BodyPart(name="head", hp=femhito_hp * 17 // 100, ce=0, max_hp=femhito_hp * 17 // 100, max_ce=0),
        "body" : BodyPart(name="body", hp=femhito_hp * 50 // 100, ce=0, max_hp=femhito_hp * 50 // 100, max_ce=0),
        "arm_1" : BodyPart(name="left arm", hp=femhito_hp * 16 // 100, ce=0, max_hp=femhito_hp * 16 // 100, max_ce=0),
        "arm_2" : BodyPart(name="right arm", hp=femhito_hp * 17 // 100, ce=0, max_hp=femhito_hp * 17 // 100, max_ce=0)
        }
)


brute_hp = 1000
brute_ce= 500
Brute = NPC(
    name="Brute Curse",
    level=30,
    hp=brute_hp,
    max_hp=brute_hp,
    ce=brute_ce,
    max_ce=brute_ce,
    speed=600,
    strength=900,
    grade=5,
    player_type="NPC",
    playerclass="Curse",
    xp_reward=50,
    cgp_reward=2,
    techniques=['Fist of Destruction'],
    quantity=1,
    body_parts= {
        "head" : BodyPart(name="head", hp=brute_hp * 10 // 100, ce=0, max_hp=brute_hp * 10 // 100, max_ce=0),
        "body" : BodyPart(name="body", hp=brute_hp * 50 // 100, ce=0, max_hp=brute_hp * 50 // 100, max_ce=0),
        "arm_1" : BodyPart(name="left arm", hp=brute_hp * 10 // 100, ce=0, max_hp=brute_hp * 10 // 100, max_ce=0),
        "arm_2" : BodyPart(name="right arm", hp=brute_hp * 10 // 100, ce=0, max_hp=brute_hp * 10 // 100, max_ce=0),
        "leg_1" : BodyPart(name="left leg", hp=brute_hp * 10 // 100, ce=0, max_hp=brute_hp * 10 // 100, max_ce=0),
        "leg_2" : BodyPart(name="right leg", hp=brute_hp * 10 // 100, ce=0, max_hp=brute_hp * 10 // 100, max_ce=0)
        }
)

witch_hp = 900
witch_ce = 600
Witch = NPC(
    name="Witch Curse",
    level=20,
    hp=witch_hp,
    max_hp=witch_hp,
    ce=witch_ce,
    max_ce=witch_ce,
    speed=500,
    strength=400,
    grade=5,
    player_type="NPC",
    playerclass="Curse",
    xp_reward=30,
    cgp_reward=2,
    techniques=['Curse Magic'],
    quantity=1,
    body_parts= {
        "head" : BodyPart(name="head", hp=witch_hp * 10 // 100, ce=0, max_hp=witch_hp * 10 // 100, max_ce=0),
        "body" : BodyPart(name="body", hp=witch_hp * 50 // 100, ce=0, max_hp=witch_hp * 50 // 100, max_ce=0),
        "arm_1" : BodyPart(name="left arm", hp=witch_hp * 10 // 100, ce=0, max_hp=witch_hp * 10 // 100, max_ce=0),
        "arm_2" : BodyPart(name="right arm", hp=witch_hp * 10 // 100, ce=0, max_hp=witch_hp * 10 // 100, max_ce=0),
        "leg_1" : BodyPart(name="left leg", hp=witch_hp * 10 // 100, ce=0, max_hp=witch_hp * 10 // 100, max_ce=0),
        "leg_2" : BodyPart(name="right leg", hp=witch_hp * 10 // 100, ce=0, max_hp=witch_hp * 10 // 100, max_ce=0)
    }
)


cultist_hp = 1000
cultist_ce = 500

Cultist = NPC(
    name="Cultist Curse",
    level=30,
    hp=cultist_hp,
    max_hp=cultist_hp,
    ce=cultist_ce,
    max_ce=cultist_ce,
    speed=600,
    strength=600,
    grade=5,
    player_type="NPC",
    playerclass="Curse",
    xp_reward=40,
    cgp_reward=2,
    techniques=['Binding Chains'],
    quantity=1,
    body_parts= {
        "head" : BodyPart(name="head", hp=cultist_hp * 10 // 100, ce=0, max_hp=cultist_hp * 10 // 100, max_ce=0),
        "body" : BodyPart(name="body", hp=cultist_hp * 50 // 100, ce=0, max_hp=cultist_hp * 50 // 100, max_ce=0),
        "arm_1" : BodyPart(name="left arm", hp=cultist_hp * 10 // 100, ce=0, max_hp=cultist_hp * 10 // 100, max_ce=0),
        "arm_2" : BodyPart(name="right arm", hp=cultist_hp * 10 // 100, ce=0, max_hp=cultist_hp * 10 // 100, max_ce=0),
        "leg_1" : BodyPart(name="left leg", hp=cultist_hp * 10 // 100, ce=0, max_hp=cultist_hp * 10 // 100, max_ce=0),
        "leg_2" : BodyPart(name="right leg", hp=cultist_hp * 10 // 100, ce=0, max_hp=cultist_hp * 10 // 100, max_ce=0)
    }
)


merfolk_hp = 1000
merfolk_ce = 800
Merfolk = NPC(
    name="Merfolk Curse",
    level=30,
    hp=merfolk_hp,
    max_hp=merfolk_hp,
    ce=merfolk_ce,
    max_ce=merfolk_ce,
    speed=600,
    strength=500,
    grade=5,
    player_type="NPC",
    playerclass="Curse",
    xp_reward=40,
    cgp_reward=2,
    techniques=['Depths Call'],
    quantity=1,
    body_parts= {
        "head" : BodyPart(name="head", hp=merfolk_hp * 10 // 100, ce=0, max_hp=merfolk_hp * 10 // 100, max_ce=0),
        "body" : BodyPart(name="body", hp=merfolk_hp * 50 // 100, ce=0, max_hp=merfolk_hp * 50 // 100, max_ce=0),
        "arm_1" : BodyPart(name="left arm", hp=merfolk_hp * 10 // 100, ce=0, max_hp=merfolk_hp * 10 // 100, max_ce=0),
        "arm_2" : BodyPart(name="right arm", hp=merfolk_hp * 10 // 100, ce=0, max_hp=merfolk_hp * 10 // 100, max_ce=0),
        "leg_1" : BodyPart(name="left leg", hp=merfolk_hp * 10 // 100, ce=0, max_hp=merfolk_hp * 10 // 100, max_ce=0),
        "leg_2" : BodyPart(name="right leg", hp=merfolk_hp * 10 // 100, ce=0, max_hp=merfolk_hp * 10 // 100, max_ce=0)
    }
)

toji_hp = 3000
toji_ce = 0
Toji = NPC(
    name="Toji",
    level=50,
    hp=toji_hp,
    max_hp = toji_hp,
    ce=toji_ce,
    max_ce=toji_ce,
    speed=2000,
    strength=2000,
    grade=5,
    player_type="NPC",
    playerclass="Sorcerer",
    xp_reward=100,
    cgp_reward=5,
    techniques=['Heavenly Restriction: 0'],
    quantity=1,
body_parts= {
    "head" : BodyPart(name="head", hp=toji_hp * 10 // 100, ce=0, max_hp=toji_hp * 10 // 100, max_ce=0),
    "body" : BodyPart(name="body", hp=toji_hp * 50 // 100, ce=0, max_hp=toji_hp * 50 // 100, max_ce=0),
    "arm_1" : BodyPart(name="left arm", hp=toji_hp * 10 // 100, ce=0, max_hp=toji_hp * 10 // 100, max_ce=0),
    "arm_2" : BodyPart(name="right arm", hp=toji_hp * 10 // 100, ce=0, max_hp=toji_hp * 10 // 100, max_ce=0),
    "leg_1" : BodyPart(name="left leg", hp=toji_hp * 10 // 100, ce=0, max_hp=toji_hp * 10 // 100, max_ce=0),
    "leg_2" : BodyPart(name="right leg", hp=toji_hp * 10 // 100, ce=0, max_hp=toji_hp * 10 // 100, max_ce=0)
    }
)


reggie_hp = 800
reggie_ce = 500
Reggie = NPC(
    name="Reggie",
    level=30,
    hp=reggie_hp,
    max_hp=reggie_hp,
    ce=reggie_ce,
    max_ce=reggie_ce,
    speed=400,
    strength=600,
    grade=4,
    player_type="NPC",
    playerclass="Sorcerer",
    xp_reward=60,
    cgp_reward=5,
    techniques=['Contract Recreation'],
    quantity=1,
body_parts= {
    "head" : BodyPart(name="head", hp=reggie_hp * 10 // 100, ce=0, max_hp=reggie_hp * 10 // 100, max_ce=0),
    "body" : BodyPart(name="body", hp=reggie_hp * 50 // 100, ce=0, max_hp=reggie_hp * 50 // 100, max_ce=0),
    "arm_1" : BodyPart(name="left arm", hp=reggie_hp * 10 // 100, ce=0, max_hp=reggie_hp * 10 // 100, max_ce=0),
    "arm_2" : BodyPart(name="right arm", hp=reggie_hp * 10 // 100, ce=0, max_hp=reggie_hp * 10 // 100, max_ce=0),
    "leg_1" : BodyPart(name="left leg", hp=reggie_hp    * 10 // 100, ce=0, max_hp=reggie_hp * 10 // 100, max_ce=0),
    "leg_2" : BodyPart(name="right leg", hp=reggie_hp * 10 // 100, ce=0, max_hp=reggie_hp * 10 // 100, max_ce=0)
    }
)

uro_hp = 1000
uro_ce = 800
Uro = NPC(
    name="Uro",
    level=40,
    hp=uro_hp,
    max_hp=uro_hp,
    ce=uro_ce,
    max_ce=uro_ce,
    speed=500,
    strength=300,
    grade=4,
    player_type="NPC",
    playerclass="Sorcerer",
    xp_reward=80,
    cgp_reward=5,
    techniques=['Sky Manipulation'],
    quantity=1,
    body_parts= {
        "head" : BodyPart(name="head", hp=uro_hp * 10 // 100, ce=0, max_hp=uro_hp * 10 // 100, max_ce=0),
        "body" : BodyPart(name="body", hp=uro_hp * 50 // 100, ce=0, max_hp=uro_hp * 50 // 100, max_ce=0),
        "arm_1" : BodyPart(name="left arm", hp=uro_hp * 10 // 100, ce=0, max_hp=uro_hp * 10 // 100, max_ce=0),
        "arm_2" : BodyPart(name="right arm", hp=uro_hp * 10 // 100, ce=0, max_hp=uro_hp * 10 // 100, max_ce=0),
        "leg_1" : BodyPart(name="left leg", hp=uro_hp * 10 // 100, ce=0, max_hp=uro_hp * 10 // 100, max_ce=0),
        "leg_2" : BodyPart(name="right leg", hp=uro_hp *  10 // 100, ce=0, max_hp=uro_hp * 10 // 100, max_ce=0)
    })

takaba_hp = 900
takaba_ce = 700
Takaba = NPC(
    name="Takaba",
    level=40,
    hp=takaba_hp,
    max_hp=takaba_hp,
    ce=takaba_ce,
    max_ce=takaba_ce,
    speed=400,
    strength=400,
grade=5,
player_type="NPC",
playerclass="Sorcerer",
xp_reward=80,
cgp_reward=5,
techniques=['Comedian'],
quantity=1,
body_parts= {
    "head" : BodyPart(name="head", hp=takaba_hp * 10 // 100, ce=0, max_hp=takaba_hp * 10 // 100, max_ce=0),
    "body" : BodyPart(name="body", hp=takaba_hp * 50 // 100, ce=0, max_hp=takaba_hp * 50 // 100, max_ce=0),
    "arm_1" : BodyPart(name="left arm", hp=takaba_hp * 10 // 100, ce=0, max_hp=takaba_hp * 10 // 100, max_ce=0),
    "arm_2" : BodyPart(name="right arm", hp=takaba_hp * 10 // 100, ce=0, max_hp=takaba_hp * 10 // 100, max_ce=0),
    "leg_1" : BodyPart(name="left leg", hp=takaba_hp * 10 // 100, ce=0, max_hp=takaba_hp * 10 // 100, max_ce=0),
    "leg_2" : BodyPart(name="right leg", hp=takaba_hp * 10 // 100, ce=0, max_hp=takaba_hp * 10 // 100, max_ce=0)
}
)

ryu_hp = 1000
ryu_ce = 800
Ryu = NPC(
name="Ryu",
level=40,
hp=ryu_hp,
max_hp=ryu_hp,
ce=ryu_ce,
max_ce=ryu_ce,
speed=700,
strength=700,
grade=4,
player_type="NPC",
playerclass="Sorcerer",
xp_reward=80,
cgp_reward=5,
techniques=['Energy Discharge'],
quantity=1,
body_parts= {
    "head" : BodyPart(name="head", hp=ryu_hp * 10 // 100, ce=0, max_hp=ryu_hp * 10 // 100, max_ce=0),
    "body" : BodyPart(name="body", hp=ryu_hp * 50 // 100, ce=0, max_hp=ryu_hp * 50 // 100, max_ce=0),
    "arm_1" : BodyPart(name="left arm", hp=ryu_hp * 10 // 100, ce=0, max_hp=ryu_hp * 10 // 100, max_ce=0),
    "arm_2" : BodyPart(name="right arm", hp=ryu_hp * 10 // 100, ce=0, max_hp=ryu_hp * 10 // 100, max_ce=0),
    "leg_1" : BodyPart(name="left leg", hp=ryu_hp * 10 // 100, ce=0, max_hp=ryu_hp * 10 // 100, max_ce=0),
    "leg_2" : BodyPart(name="right leg", hp=ryu_hp * 10 // 100, ce=0, max_hp=ryu_hp * 10 // 100, max_ce=0)
}
)


kashima_hp = 2000
kashima_ce = 1500
Kashima = NPC(
    name="Kashima",
    level=80,
    hp=kashima_hp,
    max_hp=kashima_hp,
    ce=kashima_ce,
    max_ce=kashima_ce,
    speed=1000,
    strength=1000,
    grade=5,
    player_type="NPC",
    playerclass="Reincarnate",
    xp_reward=80,
    cgp_reward=5,
    techniques=['Mythic Beast Amber'],
    quantity=1,
    body_parts= {
    "head" : BodyPart(name="head", hp=kashima_hp * 10 // 100, ce=0, max_hp = kashima_hp * 10 // 100, max_ce=0),
    "body" : BodyPart(name="body", hp=kashima_hp * 50 // 100, ce=0, max_hp=kashima_hp * 50 // 100, max_ce=0),
    "arm_1" : BodyPart(name="left arm", hp=kashima_hp * 10 // 100, ce=0, max_hp=kashima_hp * 10 // 100, max_ce=0),
    "arm_2" : BodyPart(name="right arm", hp=kashima_hp *  10 // 100, ce=0, max_hp=kashima_hp * 10 // 100, max_ce=0),
    "leg_1" : BodyPart(name="left leg", hp=kashima_hp * 10 // 100, ce=0, max_hp=kashima_hp * 10 // 100, max_ce=0),
    "leg_2" : BodyPart(name="right leg", hp=kashima_hp * 10 // 100, ce=0, max_hp=kashima_hp * 10 // 100, max_ce=0)
}
)
    

higgy_hp = 600
higgy_ce = 600
Higuruma = NPC(
    name="Higuruma",
    level=40,
    hp=higgy_hp,
    max_hp=higgy_hp,
    ce=higgy_ce,
    max_ce=higgy_ce,
    speed=300,
    strength=300,
    grade=4,
    player_type="NPC",
    playerclass="Sorcerer",
    xp_reward=60,
    cgp_reward=5,
    techniques=['Deadly Sentence'],
    quantity=1,
    body_parts= { 
    "head" : BodyPart(name="head", hp=higgy_hp * 10 // 100, ce=0, max_hp=higgy_hp * 10 // 100, max_ce=0),
    "body" : BodyPart(name="body", hp=higgy_hp * 50 // 100, ce=0, max_hp=higgy_hp * 50 // 100, max_ce=0),
    "arm_1" : BodyPart(name="left arm", hp=higgy_hp * 10 // 100, ce=0, max_hp=higgy_hp * 10 // 100, max_ce=0),
    "arm_2" : BodyPart(name="right arm", hp=higgy_hp * 10 // 100, ce=0, max_hp=higgy_hp * 10 // 100, max_ce=0),
    "leg_1" : BodyPart(name="left leg", hp=higgy_hp * 10 // 100, ce=0, max_hp=higgy_hp * 10 // 100, max_ce=0),
    "leg_2" : BodyPart(name="right leg", hp=higgy_hp * 10 // 100, ce=0, max_hp=higgy_hp * 10 // 100, max_ce=0)
}
)

three_finger_hp = 1500
three_finger_ce = 1500
ThreeFinger = NPC(
    name="Three Finger King",
    level=30,
    hp=three_finger_hp,
    max_hp=three_finger_hp,
    ce=three_finger_ce,
    max_ce=three_finger_ce,
    speed=1500,
    strength=1500,
    grade=5,
    player_type="NPC",
    playerclass="Reincarnate",
    xp_reward=100,
    cgp_reward=5,
    techniques=['Shrine'],
    quantity=1,
    body_parts= {
        "head" : BodyPart(name="head", hp=three_finger_hp * 10 // 100, ce=0, max_hp=three_finger_hp * 10 // 100, max_ce=0),
        "body" : BodyPart(name="body", hp=three_finger_hp * 50 // 100, ce=0, max_hp=three_finger_hp * 50 // 100, max_ce=0),
        "arm_1" : BodyPart(name="left arm", hp=three_finger_hp * 10 // 100, ce=0, max_hp=three_finger_hp * 10 // 100, max_ce=0),
        "arm_2" : BodyPart(name="right arm", hp=three_finger_hp * 10 // 100, ce=0, max_hp=three_finger_hp * 10 // 100, max_ce=0),
        "leg_1" : BodyPart(name="left leg", hp=three_finger_hp * 10 // 100, ce=0, max_hp=three_finger_hp * 10 // 100, max_ce=0),
        "leg_2" : BodyPart(name="right leg", hp=three_finger_hp * 10 // 100, ce=0, max_hp=three_finger_hp * 10 // 100, max_ce=0)
    }
)



fifteen_finger_hp = 3000
fifteen_finger_ce = 3000

FifteenFinger = NPC(
    name="Fifteen Finger King",
    level=50,
    hp=fifteen_finger_hp,
    max_hp=fifteen_finger_hp,
    ce=fifteen_finger_ce,
    max_ce=fifteen_finger_ce,
    speed=2000,
    strength=2000,
    grade=5,
    player_type="NPC",
    playerclass="Reincarnate",
    xp_reward=100,
    cgp_reward=5,
    techniques=['Shrine', "Ten Shadows"],
    quantity=1,
    body_parts= {
        "head" : BodyPart(name="head", hp=fifteen_finger_hp * 10 // 100, ce=0, max_hp=fifteen_finger_hp * 10 // 100, max_ce=0),
        "body" : BodyPart(name="body", hp=fifteen_finger_hp * 50 // 100, ce=0, max_hp=fifteen_finger_hp * 50 // 100, max_ce=0),
        "arm_1" : BodyPart(name="left arm", hp=fifteen_finger_hp * 10 // 100, ce=0, max_hp=fifteen_finger_hp * 10 // 100, max_ce=0),
        "arm_2" : BodyPart(name="right arm", hp=fifteen_finger_hp * 10 // 100, ce=0, max_hp=fifteen_finger_hp * 10 // 100, max_ce=0),
        "leg_1" : BodyPart(name="left leg", hp=fifteen_finger_hp * 10 // 100, ce=0, max_hp=fifteen_finger_hp * 10 // 100, max_ce=0),
        "leg_2" : BodyPart(name="right leg", hp=fifteen_finger_hp * 10 // 100, ce=0, max_hp=fifteen_finger_hp * 10 // 100, max_ce=0)
    }
)

twenty_finger_hp = 4000
twenty_finger_ce = 4000

TwentyFinger = NPC(
    name="King Of Curses",
    level=100,
    hp=twenty_finger_hp,
    max_hp=twenty_finger_hp,
    ce=twenty_finger_ce,
    max_ce=twenty_finger_ce,
    speed=4500,
    strength=4500,
    grade=5,
    player_type="NPC",
    playerclass="Reincarnate",
    xp_reward=200,
    cgp_reward=5,
    techniques=['Shrine', "Ten Shadows"],
    quantity=1,
    body_parts= {
        "head" : BodyPart(name="head", hp=twenty_finger_hp * 10 // 100, ce=0, max_hp=twenty_finger_hp * 10 // 100, max_ce=0),
        "body" : BodyPart(name="body", hp=twenty_finger_hp * 50 // 100, ce=0, max_hp=twenty_finger_hp * 50 // 100, max_ce=0),
        "arm_1" : BodyPart(name="left arm", hp=twenty_finger_hp * 10 // 100, ce=0, max_hp=twenty_finger_hp * 10 // 100, max_ce=0),
        "arm_2" : BodyPart(name="right arm", hp=twenty_finger_hp * 10 // 100, ce=0, max_hp=twenty_finger_hp * 10 // 100, max_ce=0),
        "leg_1" : BodyPart(name="left leg", hp=twenty_finger_hp * 10 // 100, ce=0, max_hp=twenty_finger_hp * 10 // 100, max_ce=0),
        "leg_2" : BodyPart(name="right leg", hp=twenty_finger_hp * 10 // 100, ce=0, max_hp=twenty_finger_hp * 10 // 100, max_ce=0)
    }
)

kenny_hp = 2500
kenny_ce = 2500

Kenny = NPC(
    name="Kenny",
    level=60,
    hp=kenny_hp,
    max_hp=kenny_hp,
    ce=kenny_ce,
    max_ce=kenny_ce,
    strength=2000,
    speed=2000,
    grade=5,
    player_type="NPC",
    playerclass="Reincarnate",
    xp_reward=100,
    cgp_reward=5,
    techniques=['Cursed Spirit Manipulation', 'Anti-Gravity System', 'Body Hop'],
    quantity=1,
    body_parts= {
        "head" : BodyPart(name="head", hp=kenny_hp * 10 // 100, ce=0, max_hp=kenny_hp * 10 // 100, max_ce=0),
        "body" : BodyPart(name="body", hp=kenny_hp * 50 // 100, ce=0, max_hp=kenny_hp * 50 // 100, max_ce=0),
        "arm_1" : BodyPart(name="left arm", hp=kenny_hp * 10 // 100, ce=0, max_hp=kenny_hp * 10 // 100, max_ce=0),
        "arm_2" : BodyPart(name="right arm", hp=kenny_hp * 10 // 100, ce=0, max_hp=kenny_hp * 10 // 100, max_ce=0),
        "leg_1" : BodyPart(name="left leg", hp=kenny_hp * 10 // 100, ce=0, max_hp=kenny_hp * 10 // 100, max_ce=0),
        "leg_2" : BodyPart(name="right leg", hp=kenny_hp * 10 // 100, ce=0, max_hp=kenny_hp * 10 // 100, max_ce=0)
    }
)

uraume_hp = 2000
uraume_ce = 2000
Uraume = NPC(
    name="Uraume",
    level=60,
    hp=uraume_hp,
    max_hp=uraume_hp,
    ce=uraume_ce,
    max_ce=uraume_ce,
    speed=1000,
    strength=1000,
    grade=5,
    player_type="NPC",
    playerclass="Reincarnate",
    xp_reward=80,
    cgp_reward=5,
    techniques=['Freeze'],
    quantity=1,
    body_parts= {
        "head" : BodyPart(name="head", hp=uraume_hp * 10 // 100, ce=0, max_hp=uraume_hp * 10 // 100, max_ce=0),
        "body" : BodyPart(name="body", hp=uraume_hp * 50 // 100, ce=0, max_hp=uraume_hp * 50 // 100, max_ce=0),
        "arm_1" : BodyPart(name="left arm", hp=uraume_hp * 10 // 100, ce=0, max_hp=uraume_hp * 10 // 100, max_ce=0),
        "arm_2" : BodyPart(name="right arm", hp=uraume_hp * 10 // 100, ce=0, max_hp=uraume_hp * 10 // 100, max_ce=0),
        "leg_1" : BodyPart(name="left leg", hp=uraume_hp * 10 // 100, ce=0, max_hp=uraume_hp * 10 // 100, max_ce=0),
        "leg_2" : BodyPart(name="right leg", hp=uraume_hp * 10 // 100, ce=0, max_hp=uraume_hp * 10 // 100, max_ce=0)
    }
)


NPC_enemy_list = [
    FloatJelly,
    BatMouth,
    BugFly,
    Furrpede,
    OneWiseMonkey,
    BareHand,
    Stinkaspore,
    Primate,
    Orbmaster,
    Electrocharge,
    Fingerbearer,
    DisasterFlame,
    Nature,
    TideCurse,
    Femhito,
    Brute,
    Witch,
    Cultist,
    Merfolk,
    Toji,
    Reggie,
    Uro,
    Ryu,
    Kashima,
    Higuruma,
    ThreeFinger,
    FifteenFinger,
    TwentyFinger,
    Kenny,
    Uraume
    
]

for npc in NPC_enemy_list:
    print(f"{npc.name} - HP: {npc.hp}, CE: {npc.ce}, Speed: {npc.speed}, Strength: {npc.strength}, Grade: {npc.grade}, Techniques: {', '.join(npc.techniques)}")


@dataclass
class Technique():
    name: str
    cost: int
    description: str
    technique_type: str
    strength: int
    activation_speed: int
    aoe: int
    grade: int
    travel_speed: int = 0
    requirements: dict = field(default_factory=dict)
    binding_vows: dict = field(default_factory=dict)
    effects: dict = field(default_factory=dict)
    summons: list = field(default_factory=list)


@dataclass
class Domain():
    name: str
    cost: int
    grade: int
    activation_speed: int
    open: bool
    sure_hit: str
    lethal: bool
    aoe: int
    duration: int
    requirements: dict = field(default_factory=dict)
    vows: dict = field(default_factory=dict)

@dataclass
class Barrier():
    name: str
    cost: int
    activation_speed: int
    strength: int
    duration: int
    cooldown: int
    aoe: int
    requirements: dict = field(default_factory=dict)
    effects: dict = field(default_factory=dict)


@dataclass
class CurseItem():
    name: str
    durability: int
    cost: int
    requirements: dict = field(default_factory=dict)
    effects: dict = field(default_factory=dict)
    

