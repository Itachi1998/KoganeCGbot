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
                 duration: int=None,
                 cooldown: int=None
                 ):
            self.name = name
            self.level=level
            self.act_speed = act_speed
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
            self.negates=negates
            self.duration=duration
            self.cooldown=cooldown ### NEW ###

# region ### ENEMY TECH DICT
# Decending order (special grade -> grade 4)
enemy_techs = {
    
    "Soul Manipulation" : # Femhito - special grade
        [
            {"Attack" :
                { "Callous Formation" : Techniques(
                    name="Soul Manipulation: Callous Formation",
                    level=1,
                    act_speed=2,
                    act_cost=50,
                    act_body=("hands", "legs"),
                    aoe=1,
                    strength=1000,
                    speed=600,
                    type="melee",
                    soul=200,
                    buff=(1, "strength", 200)
                    ),
                "Soul Transmute" : Techniques( # change the form or nature of the soul (self) - will need sub techniques for separate abilities
                    name="Soul Manipulation: Soul Transmute", 
                    level=1,
                    act_speed=1,
                    act_cost=50,
                    act_body=("full"),
                    aoe=1,
                    strength=600,
                    speed=800,
                    type="melee"
                    )
                }   
            },
            {"Defense" :
                {"Body Morph" : Techniques( # will need sub techniques for separate abilities
                    name="Soul Manipulation : Body Morph",
                    level=1,
                    act_speed=1,
                    act_cost=50,
                    act_body=("hands","legs", "torso", "head"),
                    aoe=1,
                    strength=600,
                    speed=800,
                    type="dodge" # wings/legs or smth
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
                    act_cost=100,
                    act_body=("hands", "torso"),
                    aoe=1,
                    strength=420,
                    speed=100,
                    type="projectile", # attack projectile, attack melee
                    sure_hit=True
                    )
                }
            },
            {"Defense" :         
                {"Foresight" : Techniques(
                    name="Orbmaster: Foresight",
                    level=1,
                    act_speed=10,
                    act_cost=100,
                    act_body=("head"),
                    aoe=1,
                    strength=400,
                    speed=200,
                    type="counter", #defense tank, defense dodge, defense counter
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
                    act_cost=40,
                    act_body=("right arm"),
                    aoe=1,
                    strength=500,
                    speed=300,
                    buff=(2, 'strength', 100),
                    type="melee"
                    ),
                "Electric Ground-pound" : Techniques(
                    name="Charger : Electric Ground-pound",
                    level=1,
                    act_speed=3,
                    act_cost=50,
                    act_body=("right arm", "left arm"),
                    aoe=5,
                    strength=400,
                    speed=300,
                    type="projectile" # add a 'wave' or 'spread' type of attack?
                    )
                }
            },
            {"Defense" : 
                {"Charged Field" : Techniques(
                    name="Charger : Charged Field",
                    level=1,
                    act_speed=2,
                    act_cost=40,
                    act_body=("right arm"),
                    aoe=5,
                    strength=400,
                    speed=500,
                    type="tank"
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
                    act_cost=20,
                    act_body=("Head", "Torso"),
                    aoe=5,
                    strength=50,
                    speed=100,
                    type="poison",
                    poison=(range(10, 20), 2)
                    ),
                "Carbon Monoxide Disperse" : Techniques( # colorless odorless gas that can be fatal in high enough quantities
                    name="Stinkaspore : Carbon Monoxide Disperse",
                    level=1,
                    act_speed=3,
                    act_cost=60,
                    act_body=("Head", "Torso"),
                    aoe=5,
                    strength=100,
                    speed=100,
                    type="poison"
                    #sure_hit=True - Maybe
                    )
                }
            },
            {"Defense" :
                {"Ammonia Cloud" : Techniques( # can cause skin burns, respitory damage and is highly flammable
                    name="Stinkaspore : Ammonia Cloud", 
                    level=1,
                    act_speed=3,
                    act_cost=60,
                    act_body=("Head", "Torso"),
                    aoe=5,
                    strength=80,
                    speed=150,
                    type="counter"
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
                    act_cost=30,
                    act_body=("Head", "Torso"),
                    aoe=1,
                    strength=200,
                    speed=500,
                    type="stun"
                    )
                }
            },
            {"Defense" :
                {"Thought Manipulation Defense" : Techniques(
                    name="MonkeyBrain : Thought Manipulation Defense",
                    level=1,
                    act_speed=2,
                    act_cost=50,
                    act_body=("Head"),
                    aoe=5,
                    strength=300,
                    speed=400,
                    type="counter"
                    )
                }
            }
        ]

}    

for k, v in enemy_techs.items():
    print(k,v)

# endregion

# region ### PLAYER TECH BIRD MANIP
bird_manip = {
     "Bird Manipulation" : [
          {"Attack" : 
           { "Talon Attack" :
            Techniques(name="Bird Manip: Talon Attack",
                       level=1,
                       act_speed=100,
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
                          =3,
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

# region ### PLAYER TECH BLOOD MANIP
blood_manip= {"Blood Manip" :[
        {
             "Attack" : {
                    "Piercing Blood" :
                    Techniques(name="Blood Manip: Piercing Blood", 
                             level=1,
                             act_speed=100,
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

# region ### PLAYER TECH BOOGIE WOOGIE
boogie_woogie = {

"Boogie Woogie" : 
     [
          {
               "Attack" :
                 {
                    "Rock Throw" : 
                         Techniques(
                              name="Boogie Woogie: Rock Throw",
                              level=1,
                              act_speed=10,
                              act_cost=20,
                              act_body=("Head", "Left Arm", "Right Arm", "Left Leg", "Right Leg"),
                              aoe=1,
                              strength=200,
                              speed=900,
                              type="Melee",
                              buff=("strength", "speed")
                              ),

                    "Double Switch Fake" : 
                         Techniques(
                              name="Boogie Woogie: Double Switch Fake",
                              level=2,
                              act_speed=0,
                              act_cost=0,
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
                         act_body=("Head", "Torso", "Right Arm", "Left Arm"),
                         aoe=5,
                         strength=800,
                         speed=2000,
                         type="Melee",
                         stun=1
                         ),
               }
          },
          {
               "Defense" : 
               {
                    "Clap Swap" : 
                         Techniques(
                              name="Boogie Woogie: Clap Swap",
                              level=1,
                              act_speed=10,
                              act_cost=50,
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
                              act_body=("Head", "Torso"),
                              aoe=5,
                              strength=10,
                              speed=5000,
                              type="dodge"
                         )
               }
          }
     ],

"Rarity" : 20 
}
# endregion

# region ### PLAYER TECH COMEDIAN

comedian={
"Comedian" : 
     [
          {
               "Attack" : 
               {
                    "Punchline" : 
                         Techniques(
                              name="Comedian: Punchline",
                              level=1,
                              act_speed=1,
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
                              act_cost=20,
                              act_body=("Head", "torso", "arms", "legs"),
                              aoe=4,
                              strength=2000,
                              speed=1000,
                              type="Projectile",
                              sure_hit=True
                              )
                }
                },
          {
               "Defense" :
                 {
                    "Red is Taboo" : 
                    Techniques(name="Comedian: Red is Taboo",
                              level=1,
                              act_speed=10,
                              act_cost=10,
                              act_body=("Head", "arms", "torso"),
                              aoe=4,
                              strength=200,
                              speed=1000,
                              type="counter",
                              negates=True
                              ),
                    "Fanta Sea":
                         Techniques(name="Comedian: Fanta Sea",
                                   level=2,
                                   act_speed=10,
                                   act_cost=10,
                                   act_body=("Head", "arm", "torso"),
                                   aoe=5,
                                   strength=1500,
                                   speed=1500,
                                   type="counter"
                                   ),
                    "Slimed" :
                         Techniques(name="Comedian: Slimed",
                                   level=1,
                                   act_speed=10,
                                   act_cost=10,
                                   act_body=("full"),
                                   aoe=2,
                                   strength=900,
                                   speed=900,
                                   type="dodge"
                                   ),
                    "Ya Trying To Kill Me?" :
                         Techniques(name="Comedian: Ya Trying To Kill Me?",
                                   level=3,
                                   act_speed=10,
                                   act_cost=10,
                                   act_body=("full"),
                                   aoe=1,
                                   strength=1000,
                                   speed=2000,
                                   type="tank",
                                   negate=True
                                   )
                    }
          }

     ], 

"Rarity" : 5

}

# endregion #### PLAYER TECH COMEDIAN

# region ### PLAYER TECH CONSTRUCTION

construction={
"Construction":
     [
          {
               "Attack" : 
                    {
                    "Blade" : 
                         Techniques(
                              name="Construction: Blade",
                              level=1,
                              act_speed=40,
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
                                   act_cost=20,
                                   act_body=("full"),
                                   aoe=4,
                                   strength=3500,
                                   speed=25000,
                                   type="Projectile") 
                    }
          },
          {
               "Defense" : 
                    {
                    "Bug Armor": 
                         Techniques(name="Construction: Blood Armor",
                                   level=3,
                                   act_speed=20,
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
                                   act_cost=300,
                                   act_body=("full"),
                                   aoe=3,
                                   strength=600,
                                   speed=600,
                                   type="tank"
                              ),
                    }
          }
],
"Rarity" : 15, 
"Six Eyes Rarity" : 5
}

# endregion

# region ### PLAYER COPY TECH

copy={
"Copy" : 
     [
          {
               "Attack" : 
               {
                    "Freeze"  : 
                         Techniques(
                         name="Copied Technique: Freeze",
                         level=1,
                         act_speed=30,
                         act_cost=50,
                         act_body=("Head"),
                         aoe=5,
                         strength=10,
                         speed=800,
                         type="Projectile",
                         stun=4),
                    "Die" : 
                         Techniques(
                              name="Copied Technique: Die",
                              level=2,
                              act_speed=30,
                              act_cost=500,
                              act_body=("full"),
                              aoe=4,
                              strength=400,
                              speed=1000,
                              type="Projectile"
                         ),
                    "Sword Blast" : 
                         Techniques(
                              name="Sword Reinforcement Discharge",
                              level=3,
                              act_speed=3,
                              act_cost=300,
                              act_body=("Full", "sword"),
                              aoe=5,
                              strength=1000,
                              speed=1000,
                              type="Melee"
                         ),
                    "Authentic Love Beam" : 
                         Techniques(
                              name="Authentic Love Beam",
                              level=1,
                              act_speed=20,
                              act_cost=500,
                              act_body=("Full", "Rika"),
                              aoe=5,
                              strength=2000,
                              speed=2000,
                              type="Projectile"
                         ),
                    "Rika Summon" : 
                         Techniques(
                              name="Come out, RIKA",
                              level=1,
                              act_speed=1,
                              act_cost=100,
                              act_body=("Head"),
                              aoe=1,
                              strength=4000,
                              speed=4000,
                              type="summon",
                              summon={"Rika" : {"Speed" : 4000, "Strength" : 4000, "Max CE" : 4000}}
                         )
          }
     },
     {
          "Defend" :
               {
               "Don't Move" : Techniques(
                    name="Copied technique: Don't Move",
                    level=1,
                    act_speed=20,
                    act_cost=50,
                    act_body=("Head"),
                    aoe=3,
                    strength=50,
                    speed=800,
                    type="counter",
                    stun=2,
                    
                    )
               }
          }
],
"Rarity" : 5,
"Six Eyes Rarity" : 2
}


# endregion



# region ### CURSED SPEECH TECH

cursed_speech={
     "Cursed Speech" :
       [
          {
               "Attack" : 
               {
               
                    "Blast Away" :
                         Techniques(
                              name="Blast Away!",
                              level=1,
                              act_speed=10,
                              act_cost=100,
                              act_body=("Head", "Torso"),
                              aoe=1,
                              strength=800,
                              speed=800,
                              type="Projectile",
                              stun=3
                         ),
                    "Plummet" : 
                         Techniques(
                              name="Plummet!",
                              level=3,
                              act_speed=10,
                              act_cost=100,
                              act_body=("Head", "torso"),
                              aoe=2,
                              strength=1000,
                              speed=1000,
                              type="Projectile",
                              stun=5
                         )
          }
          },
          {
               "Defend" :
               {
                         
                    "Freeze" : 
                         Techniques(
                              name="Freeze!", 
                              level=1, 
                              act_speed=10, 
                              act_cost=100,
                              act_body=("Head", "Torso"),
                              aoe=2,
                              Strength=600,
                              speed=900,
                              type="counter",
                              stun=3
                              )
                    
                }
          }
     ],
     "Rarity" : 50
}

#endregion



# region ### Cursed Spirit Manipulation
cursed_spirit_manip={
     "Cursed Spirit Manip" : [
          {
               "Attack" :
                    {
                         "Summon" : 
                              Techniques(
                                   name="Cursed Spirit Manipulation: Summoning",
                                   level=1,
                                   act_speed=20,
                                   act_cost=100,
                                   act_body=("Full"),
                                   aoe=5,
                                   strength=1000,
                                   speed=1000,
                                   type="summon",
                                   summon={}
                                   )
                    }
                 },
          {
               "Defend" :
               {
               "Summon" :
                    Techniques(
                         name="Cursed Spirit Manipulation: Summoning",
                         level=1,
                         act_speed=10,
                         act_cost=50,
                         act_body=("Full"),
                         aoe=5,
                         strength=1000,
                         speed=1000,
                         type="Summon",
                         summon={}
                    )
          }
     }
],
"Rarity" : 10
}




# endregion





# region ### HR: Zero

hr_zero={
     
"Heavenly Restriction: Zero" :
     [
          {
               "Attack" : 
               {
                    "3 Piece" : 
                         Techniques(
                              name="Three Piece Combo",
                              level=1,
                              act_speed=1,
                              act_cost=0,
                              act_body=("Left Arm", "Right Arm"),
                              aoe=3,
                              strength=1000,
                              speed=1000,
                              type="Melee"
                         ),
                    "Spinning Back Kick":
                         Techniques(
                              name="Spinning Back Kick",
                              level=1,
                              act_speed=3,
                              act_cost=0, 
                               =1,
                              act_body=("Left Leg", "Right Leg"),
                              aoe=1,
                              strength=1200,
                              speed=1200,
                              type="Melee"
                         ),
                    "Yeet Car" : 
                         Techniques(
                              name="Yeet Car",
                              act_speed=10,
                              act_cost=0,
                              act_body=("arms", "legs"),
                              aoe=1,
                              strength=800,
                              speed=800,
                              type="Projectile"
                         )
               }
          },

          {
               "Defend": 
           
               {
                    "Heavenly Body" : 
                         Techniques(
                              name="Heavenly Body",
                              level=1,
                              act_speed=0,
                              act_body=("Full"),
                              aoe=2,
                              strength=2000,
                              speed=2000,
                              type="tank"
                         ),
           
               }
          }
     ],
"Rarity" : 6
}

# endregion



# region ### Idle Transfiguration

soul_manipulation={
     
"Soul Manipulation" :
     [
          {
               "Attack" : 
               {
                    "Transmutate" : 
                         Techniques(
                              name="Soul Manipulation: Transmutate",
                              level=1,
                              act_speed=1,
                               =1,
                              act_cost=100,
                              act_body=("Left Arm", "Right Arm"),
                              aoe=1,
                              strength=1000,
                              speed=800,
                              type="Melee",
                              soul=True
                         ),
                    "Transmutated Souls":
                         Techniques(
                              name="Soul Manipulation: Transmutated Souls",
                              level=1,
                              act_speed=3,
                              act_cost=50,
                              act_body=("Left Arm", "Right Arm"),
                              aoe=4,
                              strength=300,
                              speed=400,
                              type="summon",
                              summon={"Transfigured Humans" : {"Speed" : 400, "Strength" : 300, "Max CE" : 100}} 
                         ),
                    "Polymorphic Soul Isomer" : 
                         Techniques(
                              name="Polymorphic Soul Isomer",
                              level=2,
                              act_speed=3,
                              act_cost=70,
                               =1,
                              act_body=("Left Arm", "Right Arm"),
                              aoe=2,
                              strength=700,
                              speed=600,
                              type="summon",
                              summon={"Polymorphic Soul Isomer" : {"Speed" : 600, "Strength" : 700, "Max CE" : 200}}
                         ),

                    "ISBODK Transform" : # make a general move like a domain?
                         Techniques(
                              name="ISBODK Transform",
                              level=3,
                              act_speed=2,
                              act_cost=150,
                               =1,
                              act_body=("Full"),
                              aoe=0,
                              strength=1200,
                              speed=1000,
                              type="transform" ###
                            )
               }
          },

          {
               "Defend": 
           
               {
                    "Soul Repel" : # always active
                        Techniques(
                            name="Soul Repel",
                            level=1,
                            act_speed=0,
                            act_cost=0,
                             =1, ###
                            act_body=("Full"),
                            aoe=1, ###
                            strength=500,
                            speed=1000, ###
                            type="tank",
                            soul=True
                            ),

                    "Soul Mulitiplicity" : 
                        Techniques(
                            name="Soul Mulitiplicity",
                            level=2,
                            act_speed=2,
                            act_cost=80,
                             =1,
                            act_body=("Left Arm", "Right Arm"),
                            aoe=1,
                            strength=200,
                            speed=800,
                            type="dodge"
                            )
           
               }
          }
     ],
"Rarity" : 8
}

# endregion


# region ### Limitless

limitless={
     
"Limitless" :
        [
            {
                "Attack" : 
                {
                    "Blue" : 
                        Techniques(
                            name="Blue",
                            level=1,
                            act_speed=1,
                             =1,
                            act_cost=50,
                            act_body=("Left Arm", "Right Arm"),
                            aoe=range(1, 5), ###
                            strength=800,
                            speed=1000,
                            type="projectile"
                         ),
                    
                    "Red": # RCT required
                        Techniques(
                            name="Red",
                            level=2,
                            act_speed=2,
                            act_cost=100, 
                             =1,
                            act_body=("Left Arm", "Right Arm"),
                            aoe=1,
                            strength=1600,
                            speed=1000,
                            type="projectile"
                         ),
                    
                    "Hollow Purple" : 
                        Techniques(
                            name="Hollow Purple",
                            level=3,
                            act_speed=3,
                            act_cost=150,
                             =1,
                            act_body=("Left Arm", "Right Arm"),
                            aoe=1,
                            strength=2500,
                            speed=1000,
                            type="projectile"
                         ),
                    
                    "Unlimited Hollow Purple" : # reduced dmg from own ce
                        Techniques(
                            name="Unlimited Hollow Purple",
                            level=3,
                            act_speed=3,
                            act_cost=150,
                             =1,
                            act_body=("Left Arm", "Right Arm"),
                            aoe=10,
                            strength=2500,
                            speed=1000,
                            type="projectile"
                         )
                }
            },

          {
               "Defend": 
           
               {
                    "Infinity" : # always active
                        Techniques(
                            name="Infinty",
                            level=1,
                            act_speed=0,
                            act_cost=1,
                             =1, ###
                            act_body=("Full"),
                            aoe=1, ###
                            strength=1000,
                            speed=1000, ###
                            type="tank"
                        ),

                    "Blue" : 
                        Techniques(
                            name="Blue",
                            level=1,
                            act_speed=1,
                             =1,
                            act_cost=50,
                            act_body=("Left Arm", "Right Arm"),
                            aoe=range(1, 5), ###
                            strength=800,
                            speed=1000,
                            type="dodge"
                        ),
                    
                    "Red": # RCT required
                        Techniques(
                            name="Red",
                            level=2,
                            act_speed=2,
                            act_cost=100, 
                             =1,
                            act_body=("Left Arm", "Right Arm"),
                            aoe=1,
                            strength=1600,
                            speed=1000,
                            type="counter"
                        ),
                }
            }
        ],
"Rarity" : 3,
"Six Eyes Rarity" : 100 # Lowkey useless without it
}

# endregion



# region ### MBA

mba={
     
"Mythic Beast Amber" : # add a constant hp decrease per turn and stat boost while activated?
        [
            {
                "Attack" : 
                {
                    "Lighting Rod" : # requires cursed tool?
                        Techniques(
                            name="Lightning Rod",
                            level=1,
                            act_speed=1,
                            act_cost=150,
                            act_body=("Left Arm", "Right Arm"),
                            aoe=1,
                            strength=1000,
                            speed=1200,
                            type="projectile",
                            cooldown=3 # 3 turns between being able to use it from start of the fight or after each use
                         ),
                    
                    "Lighting Dash" : # may or may not keep - enhanced melee attack
                        Techniques(
                            name="Lightning Dash",
                            level=1,
                            act_speed=1,
                            act_cost=10,
                            act_body=("Full"),
                            aoe=1,
                            strength=800,
                            speed=900,
                            type="melee"
                        ),

                    "Corona Blast" : 
                        Techniques(
                            name="Corona Blast",
                            level=2,
                            act_speed=2,
                            act_cost=80,
                            act_body=("Head"),
                            aoe=3,
                            strength=600,
                            speed=1200,
                            type="projectile"
                        )

                }
            },

          {
               "Defend": 
           
               {
                    "Lighting Dash" : 
                        Techniques(
                            name="Lightning Dash",
                            level=1,
                            act_speed=1,
                            act_cost=10,
                            act_body=("Full"),
                            aoe=1,
                            strength=800,
                            speed=900,
                            type="dodge"
                        ),

                    "Corona Discharge" : # localized electric discharge created by a strong electrical field ionizes the surrounding air
                        Techniques(
                            name="Corona Discharge",
                            level=2,
                            act_speed=2,
                            act_cost=80,
                            act_body=("Full"),
                            aoe=5,
                            strength=600,
                            speed=1200,
                            type="counter"
                        )
                }
            }
        ],
"Rarity" : 7
}

# endregion



# region ### Projection Sorcery

projection_sorcery={
     
"Projection Sorcery" :
        [
            {
                "Attack" : 
                {
                    "Projection" : 
                        Techniques(
                            name="Projection",
                            level=1,
                            act_speed=1,
                            act_cost=50,
                            act_body=("Left Arm", "Right Arm"),
                            aoe=1,
                            strength=400,
                            speed=1200,
                            type="melee",
                            stun=True
                         ),
                    
                    "Projection Stack" : # only if projection was used in the previous turn
                        Techniques(
                            name="Projection Stack",
                            level=2,
                            act_speed=1,
                            act_cost=50,
                            act_body=("Left Arm", "Right Arm"),
                            aoe=1,
                            strength=800,
                            speed=2400,
                            type="melee",
                            stun=True
                        )
                }
            },

          {
               "Defend": 
           
               {
                    "Projection Dodge" : 
                        Techniques(
                            name="Projection Dodge",
                            level=1,
                            act_speed=1,
                            act_cost=50,
                            act_body=("Left Arm", "Right Arm"),
                            aoe=1,
                            strength=400,
                            speed=1200,
                            type="dodge"
                        ),
                    
                    "Projection Stun" : 
                        Techniques(
                            name="Projection Stun",
                            level=1,
                            act_speed=1,
                            act_cost=50,
                            act_body=("Left Arm", "Right Arm"),
                            aoe=1,
                            strength=400,
                            speed=1200,
                            type="counter",
                            stun=True
                        )
                }
            }
        ],
"Rarity" : 15
}

# endregion