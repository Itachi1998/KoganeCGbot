# import os, sys
# from discord.ext.commands.core import has_permissions
# from enum import Enum
# from random import randint
# import random



# ##New results - aoe, stun, domain, stack, charge
# ##Technique attack results format -------- (damage, (tank, miss, hit), killed)
# ##Technique defense results format ------- (defense, (block, dodge, counter), killed)
# class Techniques():

#     def __init__(self, name: str, level: int, attack, defense, imbued, ce_cost,
#                  emote):
#         self.name = name
#         self.level = level
#         self.attack = attack
#         self.defense = defense
#         self.imbued = imbued
#         self.ce_cost = ce_cost
#         self.emote = emote

#     def to_dict(self):
#         return {
#             "name": self.name,
#             "level": self.level,
#             "attack": self.attack,
#             "defense": self.defense,
#             "imbued": self.imbued,
#             "ce_cost": self.ce_cost,
#             "emote": self.emote
#         }


# #class Star_Rage:

# #class Copy:

# #class Anti-Gravity:

# #class Sky_Manipulation:

# enemy_techniques = {
#     "Uraume":
#     Techniques(
#         "Uraume", 1, {
#             'Physical': {
#                 'dmg': 100,
#                 'speed': 100,
#                 'soul': 20
#             },
#             "Snow Calm": {
#                 'dmg': 300,
#                 'speed': 400,
#                 'stun': 3,
#                 'aoe': 4
#             },
#             'Ice Shard': {
#                 'dmg': 250,
#                 'speed': 300,
#                 'aoe': 2
#             }
#         }, {
#             'CE': {
#                 'def': 100,
#                 'speed': 200
#             },
#             'Ice Wall': {
#                 'def': 300,
#                 'speed': 500
#             }
#         }, 350, 15, None),
#     "Kechi":
#     Techniques(
#         "Kechi", 1, {
#             "Physical": {
#                 'dmg': 20,
#                 'speed': 20,
#                 'drain': 1
#             },
#             "Poison Blood": {
#                 "dmg": 50,
#                 'speed': 150,
#                 "drain": 2
#             }
#         }, {'CE': {
#             "def": 50,
#             "speed": 100
#         }}, 100, 20, None),
#     "Eso":
#     Techniques(
#         "Eso", 1, {
#             "Physical": {
#                 'dmg': 40,
#                 'speed': 40,
#                 'drain': 1
#             },
#             "Poison Blood": {
#                 "dmg": 150,
#                 "drain": 1,
#                 'speed' : 700
#             }
#         }, {
#             "Physical": {
#                 "def": 50,
#                 "speed": 150
#             },
#             'CE': {
#                 "def": 50,
#                 "speed": 100
#             }
#         }, 100, 20, None),
#     "Choso":
#     Techniques(
#         "Choso", 1, {
#             "Physical": {
#                 'dmg': 100,
#                 'speed': 120,
#                 'drain': 1
#             },
#             "Piercing Blood": {
#                 "dmg": 140,
#                 "speed": 250
#             },
#             'Super Nova': {
#                 'dmg': 300,
#                 'speed': 400,
#                 'stun': 1,
#                 'aoe': 2,
#                 'drain': 2
#             }
#         }, {
#             "Blood Armor": {
#                 "def": 200,
#                 "speed": 300
#             },
#             'Blood Meteor': {
#                 'def': 10,
#                 'speed': 100,
#                 'dmg': 300
#             }
#         }, 100, 10, None),
#     "Dagon":
#     Techniques(
#         "Dagon", 1, {
#             "Physical": {
#                 'dmg': 100,
#                 'speed': 200
#             },
#             "Disaster Tides": {
#                 "dmg": 50,
#                 "speed": 400,
#                 'stun': 1,
#                 'aoe': 3
#             },
#             "Captivating Skhanda": {
#                 'dmg': 300,
#                 'speed': 300,
#                 'domain': 'Fish Shikigami'
#             }
#         }, {"Fish Shikigami": {
#             "def": 150,
#             "speed": 200
#         }}, 250, 10, None),
#     "Jogo":
#     Techniques(
#         "Jogo", 1, {
#             "Physical": {
#                 'dmg': 200,
#                 'speed': 200
#             },
#             "Volcano Head": {
#                 'dmg': 240,
#                 'speed': 150
#             },
#             "Maximum Meteor": {
#                 "dmg": 300,
#                 'speed': 10
#             },
#             "Iron Coffin": {
#                 'dmg': 400,
#                 'speed': 400,
#                 'domain': 'Maximum Meteor'
#             }
#         }, {
#             "Afterburn": {
#                 'def': 10,
#                 'speed': 600
#             },
#             "Soundwave Bugs": {
#                 'def': 30,
#                 'speed': 150,
#                 'stun': 1
#             }
#         }, 150, 5, None),
#     "Hanami":
#     Techniques(
#         "Hanami", 1, {
#             "Physical": {
#                 'dmg': 200,
#                 'speed': 150
#             },
#             "Root Sprouts": {
#                 'dmg': 100,
#                 'speed': 200,
#                 'drain': 3
#             },
#             "Garden of the Everlasting": {
#                 'dmg': 50,
#                 'speed': 150,
#                 'domain': 'Blisfful Essence'
#             }
#         }, {
#             "Wood Wall": {
#                 'def': 100,
#                 'speed': 250
#             },
#             "Blissful Essence": {
#                 'def': 300,
#                 'speed': 500,
#                 'stun': 3
#             }
#         }, 250, 5, None),
#     "Mahito":
#     Techniques(
#         "Mahito", 1, {
#             "Physical": {
#                 'dmg': 100,
#                 'speed': 300,
#                 'soul': 50
#             },
#             "Idle Transfig": {
#                 'dmg': 200,
#                 'speed': 350,
#                 'soul': 300
#             },
#             "Transfigured Human": {
#                 'dmg': 250,
#                 'speed': 250
#             },
#             "Soul Repel": {
#                 'dmg': 300,
#                 'speed': 500,
#                 'aoe': 4
#             },
#             "Perfect Body Of Killing": {
#                 'dmg': 500,
#                 'speed': 900,
#                 'soul': 150
#             }
#         }, {"Soul Reinforcement": {
#             'def': 200,
#             'speed': 800,
#             'soul': 100
#         }}, 450, 5, None),
#     "Toji":
#     Techniques(
#         "Toji", 1, {
#             "Physical": {
#                 'dmg': 400,
#                 'speed': 400
#             },
#             "Heavenly Kicks": {
#                 'dmg': 200,
#                 "speed": 500,
#                 'soul': 100
#             },
#             "Heavenly Punches": {
#                 "dmg": 200,
#                 "speed": 500,
#                 'soul': 50
#             },
#             "Split Soul": {
#                 "dmg": 400,
#                 "speed": 600,
#                 'soul': 500
#             },
#             "ISOH": {
#                 "dmg": 300,
#                 "speed": 800,
#                 "negate": True
#             },
#             'Blicky': {
#                 'dmg': 500,
#                 'speed': 800
#             }
#         }, {
#             "Air Hop": {
#                 "def": 200,
#                 "speed": 500
#             },
#             'ISOH': {
#                 'def': 400,
#                 'speed': 500,
#                 'negate': True
#             },
#             'Precognition': {
#                 'def': 500,
#                 'speed': 500
#             },
#             'Sneak Attack': {
#                 'dmg': 500,
#                 'speed': 400,
#                 'def': 400
#             }
#         }, 200, 100, None),
#     "Reggie":
#     Techniques(
#         "Reggie", 1, {
#             "Physical": {
#                 'dmg': 50,
#                 'speed': 150
#             },
#             'Grenades': {
#                 'dmg': 500,
#                 'speed': 50,
#                 'aoe': 2
#             },
#             "Semi Truck": {
#                 "dmg": 250,
#                 "speed": 250
#             },
#             "Kitchen Knives": {
#                 "dmg": 50,
#                 "speed": 150
#             }
#         }, {
#             'Bear Trap': {
#                 'def': 10,
#                 'speed': 250,
#                 'dmg': 50,
#                 'stun': 2
#             },
#             "Moped": {
#                 "def": 10,
#                 "speed": 400
#             },
#             "Spa": {
#                 "def": 500,
#                 "speed": 100,
#                 "rct": 20
#             },
#             }, 
#             200, 
#             10, 
#             None),
#     "Uro":
#     Techniques(
#         "Uro", 1, {
#             "Physical": {
#                 'dmg': 150,
#                 'speed': 250
#             },
#             "Ice Breaker": {
#                 "dmg": 450,
#                 "speed": 400
#             }
#         }, {
#             "Sky Deflect": {
#                 "def": 300,
#                 "speed": 300
#             },
#             'Sky Reversal': {
#                 'def': 250,
#                 'speed': 500,
#                 'dmg': 50
#             }
#         }, 300, 10, None),
#     "Kenjaku":
#     Techniques(
#         "Kenjaku", 1, {
#             "Physical": {
#                 'dmg': 250,
#                 'speed': 350
#             },
#             "Gravity": {
#                 "dmg": 150,
#                 "speed": 900,
#                 'stun': 2
#             },
#             "Uzumaki": {
#                 "dmg": 600,
#                 "speed": 200
#             },
#             "Special Grade Curse": {
#                 'dmg': 200,
#                 "speed": 250
#             },
#             "Smallpox": {
#                 'dmg': 200,
#                 'speed': 300,
#                 'domain': {
#                     'Smallpox Curse': {
#                         'dmg': 200,
#                         'speed': 900,
#                         'drain': 2
#                     }
#                 }
#             }
#         }, {
#             'Anti Gravity': {
#                 'def': 400,
#                 'speed': 900,
#                 'stun': 1
#             },
#             "Illusion Curse": {
#                 'def': 10,
#                 'speed': 300,
#                 'stun': 1
#             },
#             'Cursed Womb': {
#                 'def': 400,
#                 'speed': 900,
#                 'dmg': 200,
#                 'domain': 'Gravity'
#             }
#         }, 500, 15, None),
#     "King Of Curses":
#     Techniques(
#         "King Of Curses", 1, {
#             "Cleave": {
#                 "dmg": 600,
#                 "speed": 30,
#                 'soul': 200
#             },
#             "Dismantle": {
#                 "dmg": 500,
#                 "speed": 800,
#                 'soul': 200
#             },
#             "Malevolent Shrine": {
#                 "dmg": 500,
#                 "speed": 800,
#                 'domain': 'Dismantle',
#                 'soul': 200
#             }
#         }, {
#             "Binding Vow": {
#                 "def": 1000,
#                 "speed": 1000
#             },
#             'Domain Amplification': {
#                 'def': 500,
#                 "speed": 500,
#                 'negate': True,
#                 'dmg': 500,
#                 'dmg': 300
#             },
#             'Black Flash': {
#                 'def': 10,
#                 'speed': 200,
#                 'dmg': 500,
#                 'soul': 200
#             }
#         }, 900, 5, None),
#     "Kashimo":
#     Techniques(
#         "Kashimo",  #name
#         1,  #ct_level
#         {
#             "Physical": {
#                 'dmg': 250,
#                 'speed': 450
#             },
#             "Rod": {
#                 "dmg": 400,
#                 "speed": 400,
#                 'stun': 1,
#                 'charge': 1,
#                 'soul': 10
#             },
#             "Positive Charge Punch": {
#                 "dmg": 400,
#                 "speed": 600
#             },
#             "Charged Rod": {
#                 "dmg": 200,
#                 "speed": 500,
#                 'negate': True
#             },
#             'MBA : Railgun Fist': {
#                 'dmg': 400,
#                 'speed': 900,
#                 'soul': 100
#             },
#             'MBA : Oral Discharge': {
#                 'dmg': 300,
#                 'speed': 900,
#                 'soul': 100
#             }
#         },
#         {
#             "X Ray": {
#                 "def": 300,
#                 "speed": 300
#             },
#             "Frequency Phase": {
#                 "def": 600,
#                 "speed": 400
#             }
#         },  #defense options 
#         500,  #imbued
#         10,  #ce_cost
#         None),
#     "Finger Bearer":
#     Techniques(
#         "Finger Bearer", 1, {
#             "Physical": {
#                 'dmg': 150,
#                 'speed': 150
#             },
#             "Energy Blast": {
#                 "dmg": 100,
#                 "speed": 100
#             }
#         }, {"Energy shield": {
#             "def": 100,
#             "speed": 100
#         }}, 100, 5, None),
#     "Grade 4":
#     Techniques("Grade 4", 1, {
#         "Physical": {
#             'dmg': 20,
#             'speed': 20
#         },
#         "Bite": {
#             "dmg": 10,
#             "speed": 10
#         }
#     }, {"CE": {
#         "def": 10,
#         "speed": 10
#     }}, 40, 2, None),
#     "Grade 3":
#     Techniques(
#         "Grade 3", 1, {
#             "Physical": {
#                 'dmg': 20,
#                 'speed': 50
#             },
#             "Punch": {
#                 "dmg": 15,
#                 "speed": 25
#             },
#             "kick": {
#                 "dmg": 20,
#                 "speed": 20
#             }
#         }, {"CE": {
#             "def": 20,
#             "speed": 20
#         }}, 40, 2, None),
#     "Grade 2":
#     Techniques("Grade 2", 1, {
#         "Physical": {
#             'dmg': 50,
#             'speed': 50
#         },
#         "Slash": {
#             "dmg": 40,
#             "speed": 50
#         }
#     }, {"CE": {
#         "def": 10,
#         "speed": 50
#     }}, 40, 2, None),
#     "Grade 1":
#     Techniques(
#         "Grade 1", 1, {
#             "Physical": {
#                 'dmg': 100,
#                 'speed': 100
#             },
#             "Combo Strikes": {
#                 "dmg": 80,
#                 "speed": 60
#             },
#             "Flying Kicks": {
#                 "dmg": 100,
#                 "speed": 100
#             }
#         }, {"CE": {
#             "def": 50,
#             "speed": 100
#         }}, 100, 2, None)
# }


# class CursedTools():

#     def __init__(self, name: str, attack: int, pen: int, cost: int, emote,
#                  negate, broke, hp, max_hp):
#         self.name = name
#         self.attack = attack
#         self.pen = pen
#         self.cost = cost
#         self.emote = emote
#         self.broke = broke
#         self.negate = negate
#         self.hp = hp
#         self.max_hp = max_hp


# class BindingVows():

#     def __init__(self, name: str, description: str, cost: int, emote, used):
#         self.description = description
#         self.cost = cost
#         self.emote = emote
#         self.used = False
#         self.name = name

#     def use_vow():
#         pass


# class KoganeRules():

#     def __init__(self, name: str, description: str, cost: int, emote, used):
#         self.name = name
#         self.description = description
#         self.cost = cost
#         self.emote = emote
#         self.used = False

#     def use_rule():
#         pass


# BVs = {
#     "Sukuna Vow":
#     BindingVows(name="Sukuna Vow",
#                 description="Sacrifice a cursed tool for no damage",
#                 cost=100,
#                 emote=None,
#                 used=False),
#     "Mahito Vow":
#     BindingVows(name="Mahito Vow",
#                 description="Let Mahito re-awaken your cursed technique",
#                 cost=100,
#                 emote=None,
#                 used=False),
#     "Life Vow" : BindingVows(name="Life Vow",
#                             description = 'Sacrifice life for a kamikaze attack',
#                             cost=100,
#                             emote=None,
#                             used=False),
    
# }

# cursed_tools = {
#     "ISOH":
#     CursedTools(name="ISOH",
#                 attack=20,
#                 pen=100,
#                 cost=300,
#                 emote="<:ISOH:1275114916201894025>",
#                 negate=True,
#                 broke=False,
#                 hp=300,
#                 max_hp=300),
#     "Dragon Bone":
#     CursedTools(name="Dragon Bone",
#                 attack=20,
#                 pen=5,
#                 cost=50,
#                 emote="<:dragonbone:1277632814367506567>",
#                 negate=False,
#                 broke=False,
#                 hp=100,
#                 max_hp=100),
#     "Maichan":
#     CursedTools(name="Maichan",
#                 attack=50,
#                 pen=100,
#                 cost=250,
#                 emote="<:soulsplit:1277632881640083456>",
#                 negate=False,
#                 broke=False,
#                 hp=150,
#                 max_hp=150),
#     "Playful Cloud":
#     CursedTools(name="Playful Cloud",
#                 attack=70,
#                 pen=0,
#                 cost=300,
#                 emote="<:playfulcloud:1277632921720586362>",
#                 negate=False,
#                 broke=False,
#                 hp=100,
#                 max_hp=100),
#     "Black Rope":
#     CursedTools(name="Black Rope",
#                 attack=50,
#                 pen=100,
#                 cost=250,
#                 emote="<:blackrope:1277632984928882769>",
#                 negate=True,
#                 broke=False,
#                 hp=150,
#                 max_hp=150),
#     "Cow Blade":
#     CursedTools(name="Cow Blade",
#                 attack=100,
#                 pen=100,
#                 cost=300,
#                 emote="<:cow_blade:1277632737683046431>",
#                 negate=False,
#                 broke=False,
#                 hp=200,
#                 max_hp=200),
#     "Soul Blicky":
#     CursedTools(name="Soul Blicky",
#                 attack=100,
#                 pen=100,
#                 cost=300,
#                 emote="<:soulblicky:1277633038251196497>",
#                 negate=True,
#                 broke=False,
#                 hp=13,
#                 max_hp=13),
#     "Tsumikichan":
#     CursedTools(name="Tsumikichan",
#                 attack=300,
#                 pen=50,
#                 cost=200,
#                 emote="<:dababy:1277638084426727565>",
#                 negate=False,
#                 broke=False,
#                 hp=50,
#                 max_hp=50)
# }

# rules = {
#     "Transfer Points":
#     KoganeRules(name="Transfer Points",
#                 description="Give a player a certain amount of points",
#                 cost=100,
#                 emote=None,
#                 used=False),
#     "Transfer Colonies":
#     KoganeRules(name="Transfer Colonies",
#                 description="Transfer your player to another colony",
#                 cost=100,
#                 emote=None,
#                 used=False),
#     "View Players":
#     KoganeRules(name="View Players",
#                 description="View player profiles in your colony",
#                 cost=100,
#                 emote=None,
#                 used=False),
#     "Hunt Players":
#     KoganeRules(name="Hunt Players", 
#                 description="Hunt down other culling game players",
#                 cost=200,
#                 emote=None,
#                 used=False)
# }


def set_technique(techniques: list):
    rarity = {"epic": 5, "rare": 15, "uncommon": 30, "common": 50}
    sum = 0
    value = 0
    for r in rarity:
        sum += rarity[r]
    choice = randint(1, sum)
    for r in rarity:
        if choice > rarity[r]:
            value = rarity[r]

#     print(f"Getting technique value : {value}")

#     ct_list = [t for t in techniques if t.rarity >= value]
#     technique = random.choice(ct_list)
#     print(
#         f"Got technique: {technique.name}, rarity level : {technique.rarity}")
#     return technique


# def get_enemy_cursed_technique(enemy_name):
#     for t in enemy_techniques.keys():
#         if t == enemy_name:
#             return enemy_techniques[t]


# def get_cursed_technique(name, techniques: list):
#     for t in techniques:
#         if t.name == name:
#             technique = t
#             return technique  # Instantiate the class before returning


# def get_BV(name):
#     return BVs.get(name)


# def get_cursed_tool(name):
#     return cursed_tools.get(name)


# def get_rule(name):
#     return rules.get(name)
