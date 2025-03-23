import os
import discord 
from discord.ext import commands
class Techniques_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Techniques cog is ready!')


async def setup(bot):
    await bot.add_cog(Techniques_cog(bot))

class Techniques():
    def __init__(self, 
                 name: str,  # "Blood Manipulation: Piercing Blood"
                 level: int, # 1-5
                 act_speed: int, # activation speed of technique: 1-5 (can be changed with binding vows)
                 act_dur: int, #activation duration in turn counts: can very in numbers and be changed with binding vows
                 act_cost: int,
                 act_body: tuple, # activation cost per turn of activating this technique: can be changed with binding vows
                 aoe: int, # amount of players targetable (can be changed with binding vows)
                 strength: int, # strength of attack or defense (will be used in attack vs defense checks, can be changed with binding vows)
                 speed: int, # speed of attack or defense (will be used in attack vs defense checks, can be changed with binding vows) 
                 type: str,
                 soul: int=None,
                 buff: tuple=None,
                 debuff: tuple=None,
                 poison: tuple = None,
                 stun: int = None,
                 stack: int = None,
                 charge: list=None,
                 summon: dict=None,
                 sure_hit=None,
                 target=None,
                 negates: bool =None,
                 ):
            self.name = name
            self.level=level
            self.act_speed = act_speed
            self.act_dur = act_dur
            self.act_cost = act_cost
            self.act_body= act_body
            self.aoe = aoe
            self.strength = strength
            self.speed = speed
            self.type=type
            self.soul=soul
            self.buff=buff
            self.debuff=debuff
            self.poison=poison
            self.stun=stun
            self.stack=stack
            self.charge=charge
            self.summon=summon
            self.sure_hit=sure_hit
            self.target=target

# region ##### ENEMY TECH DICT
# Decending order (special grade -> grade 4)
enemy_techs = {
    
    "Soul Manipulation" : # Femhito - special grade
        [
            {"Attack" :
                { "Callous Formation" : Techniques(
                    name="Soul Manipulation: Callous Formation",
                    level=1,
                    act_speed=2,
                    act_dur=1, # possibly perminant - use 0 as a way to check for permanent?
                    act_cost=50,
                    act_body=("hands", "legs"),
                    aoe=1,
                    strength=800,
                    speed=600,
                    type="melee",
                    soul=200,
                    buff=(1, "strength", 200)
                    ),
                "Soul Transmute" : Techniques( # change the form or nature of the soul (self) - will need sub techniques for separate abilities
                    name="Soul Manipulation: Soul Transmute", 
                    level=1,
                    act_speed=1,
                    act_dur=1,
                    act_cost=50,
                    act_body=("right arm", "right leg", "head", "left arm", "left leg"),
                    aoe=1,
                    strength=600,
                    speed=800,
                    type="melee" # change body into weapons
                    )
                }   
            },
            {"Defense" :
                {"Soul Transmute Escape" : Techniques( # will need sub techniques for separate abilities
                    name="Soul Manipulation : Soul Transmute",
                    level=1,
                    act_speed=1,
                    act_dur=1,
                    act_cost=50,
                    act_body=("hands","legs", "torso", "head"),
                    aoe=1,
                    strength=600,
                    speed=800,
                    type="defense dodge" # wings/legs or smth
                    )
                }
            }
        ],
        
    "Orbmaster" : # grade 1
        [    
            {"Attack" : 
                {"Impending Doom" : Techniques(
                    name="Orbmaster: Impending Doom",
                    level=1,
                    act_speed=10,
                    act_dur=1,
                    act_cost=100,
                    act_body=("hands", "torso"),
                    aoe=1,
                    strength=420,
                    speed=100,
                    type="attack projectile", # attack projectile, attack melee
                    sure_hit=True
                    )
                }
            },
            {"Defense" :         
                {"Foresight" : Techniques(
                    name="Orbmaster: Foresight",
                    level=1,
                    act_speed=10,
                    act_dur=1,
                    act_cost=100,
                    act_body=("head"),
                    aoe=1,
                    strength=400,
                    speed=200,
                    type="defense counter", #defense tank, defense dodge, defense counter
                    sure_hit=True
                    )
                }
            }
        ],

    "Charger" : 
        [ 
            {"Attack" :
                {"Charged Punch" : Techniques(
                    name="Charger : Charged Punch",
                    level=1,
                    act_speed=3,
                    act_dur=1,
                    act_cost=40,
                    act_body=("right arm"),
                    aoe=1,
                    strength=500,
                    speed=300,
                    buff=(2, 'strength', 100),
                    type="attack melee"
                    ),
                "Electric Ground-pound" : Techniques(
                    name="Charger : Electric Ground-pound",
                    level=1,
                    act_speed=3,
                    act_dur=1,
                    act_cost=50,
                    act_body=("right arm", "left arm"),
                    aoe=5,
                    strength=400,
                    speed=300,
                    type="attack projectile" # add a 'wave' or 'spread' type of attack?
                    )
                }
            },
            {"Defense" : 
                {"Charged Field" : Techniques(
                    name="Charger : Charged Field",
                    level=1,
                    act_speed=2,
                    act_dur=1,
                    act_cost=40,
                    act_body=("right arm"),
                    aoe=5,
                    strength=400,
                    speed=500,
                    type="defense tank"
                    )
                }
            }
        ],

    "Stinkaspore" : # grade 2
        [
            {"Attack" : 
                {"Hydrogen Sulfide Bomb" : Techniques( # rotten egg smelling gas that can cause; unconsciousness, memory loss, death
                    name="Stinkaspore: Hydrogen Sulfide Bomb",
                    level=1,
                    act_speed=3,
                    act_dur=2,
                    act_cost=20,
                    act_body=("Head", "Torso"),
                    aoe=5,
                    strength=50,
                    speed=100,
                    type="attack poison",
                    poison=(range(10, 20), 2)
                    ),
                "Carbon Monoxide Disperse" : Techniques( # colorless odorless gas that can be fatal in high enough quantities
                    name="Stinkaspore : Carbon Monoxide Disperse",
                    level=1,
                    act_speed=3,
                    act_dur=3,
                    act_cost=60,
                    act_body=("Head", "Torso"),
                    aoe=5,
                    strength=100,
                    speed=100,
                    type="attack poison"
                    #sure_hit=True - Maybe
                    )
                }
            },
            {"Defense" :
                {"Ammonia Cloud" : Techniques( # can cause skin burns, respitory damage and is highly flammable
                    name="Stinkaspore : Ammonia Cloud", 
                    level=1,
                    act_speed=3,
                    act_dur=1,
                    act_cost=60,
                    act_body=("Head", "Torso"),
                    aoe=5,
                    strength=80,
                    speed=150,
                    type="defense counter"
                    )
                }
            }
        ],

    "Primal Curse" : 
        [ 
            {"Attack" :
                {"Thought Manipulation Attack" : Techniques(
                    name="MonkeyBrain : Thought Manipulation Attack",
                    level=1,
                    act_speed=2,
                    act_dur=1,
                    act_cost=30,
                    act_body=("Head", "Torso"),
                    aoe=1,
                    strength=200,
                    speed=500,
                    type="attack stun" # new types for targeting the mind etc.
                    )
                }
            },
            {"Defense" :
                {"Thought Manipulation Defense" : Techniques(
                    name="MonkeyBrain : Thought Manipulation Defense",
                    level=1,
                    act_speed=2,
                    act_dur=1,
                    act_cost=50,
                    act_body=("Head"),
                    aoe=5,
                    strength=300,
                    speed=400,
                    type="defense counter"
                    )
                }
            }
        ]

}    

for k, v in enemy_techs.items():
    print(k,v)

# endregion

# region #### PLAYER TECH BIRD MANIP
bird_manip = {
     "Bird Manipulation" : [
          {"Attack" : 
           { "Talon Attack" :
            Techniques(name="Bird Manip: Talon Attack",
                       level=1,
                       act_speed=100,
                       act_dur=1,
                       act_cost=100,
                       act_body=("Head", "Right Arm", "Left Arm"),
                       aoe=3,
                       strength=50,
                       speed=250,
                       type="projectile"
                       ),
            "Bird Flock" :
            Techniques(name="Bird Manip: Bird Flock",
                       level=2,
                       act_speed=50,
                       act_dur=3,
                       act_cost=300,
                       act_body=("head", "left arm", "right arm"),
                       aoe=3,
                       strength=200,
                       speed=400,
                       type="projectile"
                       )
                    ,
                "Bird Sacrifice" : Techniques(
                     name="Bird Manip: Bird Sacrifice",
                     level=3,
                     act_speed=20,
                     act_dur=1,
                     act_cost=400,
                     act_body=("Head", "left arm", "right arm"),
                     aoe=2,
                     strength=1500,
                     speed=500,
                     stun=3,
                     type="Projectile"
                )
                       

           }
           },

           {"Defense": 
               {
                    "Feather Screen" : Techniques(
                         name="Bird Manip: Feathered Screen",
                         level=1,
                         act_speed=40,
                         act_dur=3,
                         act_cost=50,
                         act_body=("Head", "left arm", "right arm"),
                         aoe=3,
                         strength=50,
                         speed=100,
                         type="dodge"),
                    "Birds Eye" : Techniques(
                         name="Bird Manip: Birds Eye",
                         level=2,
                         act_speed=20,
                         act_dur=5,
                         act_cost=10,
                         act_body=("head"),
                         aoe=5,
                         strength=150,
                         speed=500,
                         buff=("speed", 550),
                         type="dodge"
                    )

               }}],
                "Rarity" : 60}

# endregion

# region #### PLAYER TECH BLOOD MANIP
blood_manip= {"Blood Manip" :[
        {
             "Attack" : {
                    "Piercing Blood" :
                    Techniques(name="Blood Manip: Piercing Blood", 
                             level=1,
                             act_speed=100,
                             act_dur=2,
                             act_cost=100,
                             act_body=("Head", "left arm", "right arm"),
                             aoe=1,
                             strength=400,
                             speed=1200,
                             type="projectile",
                             poison=(10, 4),
                             stun=1
                             ),
                    "Blood Edge" : 
                    Techniques(name="Blood Manip: Blood Edge",
                                        level=2,
                                        act_speed=50,
                                        act_dur=4,
                                        act_cost=300,
                                        act_body=("Head", "left arm", "right arm"),
                                        aoe=5,
                                        strength=800,
                                        speed=500,
                                        type="Projectile",
                                        poison=(5, 8)

                                        ),
                    "Red Scale" : 
                    Techniques(name="Blood Manip: Red Scale",
                               level=1,
                               act_speed=10,
                               act_cost=500,
                               act_dur=5,
                               act_body=("Head", "right arm", "left arm", "left leg", "right leg"),
                               aoe=1,
                               strength=500,
                               speed=500,
                               type="melee",
                               buff=("strength", "speed"),


                    ) 
                            
             }
                  
        }, 
        {
                "Defense" : {
                "Blood Meteor" : 
                Techniques(name="Blood Manip: Blood Meteor",
                                                        level=1,
                                                        act_speed=100,
                                                        act_cost=300,
                                                        act_dur=1,
                                                        act_body=("Head", "left arm", "right arm"),
                                                        aoe=1,
                                                        strength=400,
                                                        speed=100,
                                                        type="Counter",
                                                        stun=3
                                                        ),
                "Blood Armor":
                Techniques(name="Blood Manip: Blood Armor",
                                           level=3,
                                           act_speed=20,
                                           act_cost=500,
                                           act_dur=5,
                                           act_body=("Head", "Torso", "Right Arm", "Left Arm", "Right Leg", "Left Leg"),
                                           aoe=1,
                                           strength=1000,
                                           speed=1000,
                                           type="Block"
                                )
                                                        
        }
        }
        ], 
        "Rarity" : 30
        }

# endregion

# region #### PLAYER TECH BOOGIE WOOGIE
boogie_woogie = {
     "Boogie Woogie" : [
          "Attack" : {
          "Rock Throw" : 
          Techniques(
               name="Boogie Woogie: Rock Throw",
               level=1
               act_speed=10,
               act_cost=20,
               act_dur=1,
               act_body=("Head", "Left Arm", "Right Arm", "Left Leg", "Right Leg"),
               aoe=1,
               strength=200,
               speed=900,
               type="Melee",
               buff=("strength", "speed"),
            "Double Switch Fake" : 
            Techniques(
                 name="Boogie Woogie: Double Switch Fake",
                 level=2,
                 act_speed=0,
                 act_cost=0,
                 act_dur=1,
                 act_body=("Head", "Torso", "Left Leg", "Right Leg", "Right Arm", "Left Arm"),
                 strength=400,
                 speed=400,
                 type="Melee",
                 stun=2),
            "Over Here" : 
            Techniques(
                 name="Boogie Woogie: Over Here",
                 level=2,
                 act_speed=10,
                 act_cost=50,
                 act_dur=5,
                 act_body=("Head", "Torso", "Right Arm", "Left Arm"),
                 aoe=5,
                 strength=800,
                 speed=2000,
                 type="Melee",
                 stun=1
            ),
          )},
          {"Defense" : {
               "Clap Swap" : 
               Techniques(
                    name="Boogie Woogie: Clap Swap",
                    level=1,
                    act_speed=10,
                    act_cost=50,
                    act_dur=5,
                    act_body=("Head", "Torso", "Left Arm", "Right Arm"),
                    aoe=5,
                    strength=10,
                    speed=2000,
                    type="Dodge"
               ),
               "Reverse Swap" : 
               Techniques(
                    name="Boogie Woogie: Reverse Swap",
                    level=3,
                    act_speed=10,
                    act_cost=50,
                    act_dur=4,
                    act_body=("Head", "Torso", "Left Arm", "Right Arm"),
                    aoe=1,
                    strength=10,
                    speed=2000,
                    type="counter"
               ),
               "Vibra Swap" : 
               Techniques(
                    name="Boogie Woogie: Vibra Swap",
                    level=4,
                    act_speed=1,
                    act_cost=100,
                    act_dur=5,
                    act_body=("Head", "Torso"),
                    aoe=5,
                    strength=10,
                    speed=5000,
                    type="dodge"
               )
          }}
          ],
        "Rarity" : 20 
     }
# endregion

# region ### PLAYER TECH COMEDIAN

comedian={
     "Comedian" : [
          {"Attack" : {
               "Punchline" : 
               Techniques(
                    name="Comedian: Punchline",
                    level=1,
                    act_speed=1,
                    act_dur=5,
                    act_cost=10,
                    act_body={"head", "torso", "arms", "legs"},
                    aoe=1,
                    strength=500,
                    speed=900,
                    type="Melee",
                    buff=("strength", "speed")
                    ),
                "One Liner" :
                Techniques(
                     name="Comedian: One Liner",
                     level=1,
                     act_speed=1,
                     act_dur=5,
                     act_cost=10,
                     act_body={"Head", "torso", "arms", "legs"},
                     aoe=4,
                     strength=700,
                     speed=900,
                     type="Melee",
                     buff=("Strength", "speed")),
                "Skit" : 
                Techniques(
                     name="Comedian: Skit",
                     level=2,
                     act_speed=1,
                     act_dur=5,
                     act_cost=10,
                     act_body=("Head", "Torso", "Arms", "Legs"),
                     strength=900,
                     speed=1500,
                     type="Melee",
                     buff=("Strength", "Speed")
                     ),
                "Truck Kun" :
                Techniques(
                     name="Comedian: Truck Kun",
                     level=3,
                     act_speed=10,
                     act_dur=1,
                     act_cost=10,
                     act_body=("Head", "Torso", "Arms", "Legs"),
                     aoe=1,
                     strength=1500,
                     speed=2000,
                     type="Projectile",
                     stun=1,
                     sure_hit=True
                ),
                "Wouldn't It Be Funny" :
                Techniques(
                     name="Comedian: Wouldn't it be funny",
                     level=5,
                     act_speed=1,
                     act_dur=5,
                     act_cost=20,
                     act_body=("Head", "torso", "arms", "legs"),
                     aoe=4,
                     strength=2000,
                     speed=1000,
                     type="Projectile",
                     sure_hit=True
                )}},
          {"Defense" : {
               "Red is Taboo" : 
            Techniques(name="Comedian: Red is Taboo",
                       level=1,
                       act_speed=10,
                       act_dur=5,
                       act_cost=10,
                       act_body=("Head", "arms", "torso"),
                       aoe=4,
                       strength=200,
                       speed=1000,
                       type="counter",
                       negates=True),
                "Fanta Sea":
                Techniques(name="Comedian: Fanta Sea",
                           level=2,
                           act_speed=10,
                           act_dur=5,
                           act_cost=10,
                           act_body=("Head", "arm", "torso"),
                           aoe=5,
                           strength=1500,
                           speed=1500,
                           type="counter"),
                "Slimed" :
                Techniques(name="Comedian: Slimed",
                           level=1,
                           act_speed=10,
                           act_dur=2,
                           act_cost=10,
                           act_body=("full"),
                           aoe=2,
                           strength=900,
                           speed=900,
                           type="dodge"),
                "Ya Trying To Kill Me?" :
                Techniques(name="Comedian: Ya Trying To Kill Me?",
                           level=3,
                           act_speed=10,
                           act_dur=5,
                           act_cost=10,
                           act_body=("full"),
                           aoe=1,
                           strength=1000,
                           speed=2000,
                           type="tank",
                           negate=True)
          }}
     ], "Rarity" : 5
}

# endregion #### PLAYER TECH COMEDIAN

# region ### PLAYER TECH CONSTRUCTION

construction={
     "Construction":[
          {"Attack" : {
               "Blade" : 
               Techniques(
                    name="Construction: Blade",
                    level=1,
                    act_speed=40,
                    act_dur=1,
                    act_cost=400,
                    act_body=("Full"),
                    aoe=1,
                    strength=850,
                    speed=500,
                    type="Melee",
               ),

               "Ammo" : 
               Techniques(
                    name="Construction: Ammo",
                    level=1,
                    act_speed=30,
                    act_dur=1,
                    act_cost=400,
                    act_body=("Full"),
                    aoe=1,
                    strength=700,
                    speed=600,
                    type="Projectile"
               ),
               "Liquid Metal" : 
               Techniques(
                    name="Construction: Liquid Metal",
                    level=3,
                    act_speed=20,
                    act_dur=5,
                    act_cost=150,
                    act_body=("Full"),
                    aoe=5,
                    strength=1000,
                    speed=1000,
                    type="Projectile",
                    debuffs=("speed")),
                "Air to Surface Missile" : 
                Techniques(name="Six Eyes Construction: Air to Surface Missiles",
                           level=3,
                           act_speed=1,
                           act_dur=5,
                           act_cost=5,
                           act_body=("Full"),
                           aoe=5,
                           strength=1500,
                           speed=1500,
                           type="Projectile"
               ),
               "Nuclear Warhead" : 
               Techniques(name="Six Eyes Construction: Nuclear Warhead",
                          level=5,
                          act_speed=20,
                          act_dur=1,
                          act_cost=200,
                          act_body=("full"),
                          aoe=5,
                          strength=5500,
                          speed=2000,
                          type="Projectile"),
                "True Sphere Orbs" : 
                Techniques(name="Six Eyes Construction: True Sphere Orbs",
                           level=3,
                           act_speed=10,
                           act_dur=1,
                           act_cost=20,
                           act_body=("full"),
                           aoe=4,
                           strength=3500,
                           speed=25000,
                           type="Projectile") 
          }},
          {"Defense" : 
           {
                "Bug Armor": 
                Techniques(name="Construction: Blood Armor",
                           level=3,
                           act_speed=20,
                           act_dur=5,
                           act_cost=150,
                           act_body=("Full"),
                           aoe=1,
                           strength=2000,
                           speed=2000,
                           type="Counter",
                           buffs=("strength", "speed")
                           ),
                "Armored Sentinels":
                Techniques(name="Six Eyes Construction: Armored Sentinels",
                           level=1,
                           act_speed=1,
                           act_dur=5,
                           act_cost=50,
                           act_body=("Full"),
                           aoe=1,
                           strength=10000,
                           speed=1000,
                           type="Summon",
                           summon={"Sentinel" : {'dmg' : 1000, 'speed' : 1000, "max_hp" : 900, "tamed" : True}}
                           ),
                "Liquid Metal Shield" : 
                Techniques(
                     name="Construction: Liquid Metal Shield",
                     act_speed=20,
                     act_dur=2,
                     act_cost=300,
                     act_body=("full"),
                     aoe=3,
                     strength=600,
                     speed=600,
                     type="tank"
                ),
           }}
     ],
     "Rarity" : 15, "Six Eyes Rarity" : 5}

# endregion




