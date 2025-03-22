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
                 target=None
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