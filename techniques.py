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
                 act_cost: int, # activation cost per turn of activating this technique: can be changed with binding vows
                 aoe: int, # amount of players targetable (can be changed with binding vows)
                 strength: int, # strength of attack or defense (will be used in attack vs defense checks, can be changed with binding vows)
                 speed: int, # speed of attack or defense (will be used in attack vs defense checks, can be changed with binding vows) 
                 **kwargs #Take in additional values as a dictionary {negs: bool=True)
                 ):
        try:
            self.name = name
            self.level=level
            self.act_speed = act_speed
            self.act_dur = act_dur
            self.act_cost = act_cost
            self.aoe = aoe
            self.strength = strength
            self.speed = speed

            for k, v in kwargs.items(): #Iterate through optional attributes (k=name(string), v=value(any type))
                try:
                    if k == "negs" and isinstance(v, bool): # make sure to check the type and name of the key before setting it as an attribute
                        self.negs = v # if negates
                    if k == "soul" and isinstance(v, int):
                        self.soul = v # soul strength of this move (damage or reinforcement)
                    if k == "stun" and isinstance(v, int):
                        self.stun=v # amount of turns this move stuns target
                    if k == "charge" and isinstance(v, tuple):
                        self.charge = v # amount of charges on a target (target: string, charges: int) 
                    if k == "sure_hit" and isinstance(v, bool):
                        self.sure_hit = v # if this is a sure hit capable technique
                    if k == "maximum" and isinstance(v, bool):
                        self.maximum= v # if this is a maximum technique
                    if k == "domain" and isinstance(v,  dict):
                        self.domain = v # a dictionary of the domain effects and name        
                    if k == "type" and isinstance(v, str):
                        self.type = v   # what type of move this is ("atk melee", "atk projectile", "def counter", "def dodge", "def tank")
                    if k == "debuff" and isinstance(v, dict):
                        self.debuff = v # debuff {"turns active ": integer, "debuff attribute": "<class.attribute>", "debuff number": integer)                
                    if k == "buff" and isinstance(v, tuple):
                        self.buff = v # debuff("turns active ": integer, "buff attribute": "<class.attribute>", "buff number": integer)                
                    if k == "antidomain" and isinstance(v, bool):
                        self.antidomain = v # if this active technique will prompt a defense check
                    if k == "bindvow" and isinstance(v, dict):
                        self.bindvow = v # dictionary binding vow {"trade" : (attribute, amount), "addto" : (attribute, amount), "forturns": (number of turns or False if permanent}
                    if k == "shikigami" and isinstance(v, list):
                        self.shiki = v # list of shikigami available to user
                    if k == "curses" and isinstance(v, list):
                        self.curses = v #list of curses tamed by user
                    if k == "souls" and isinstance(v, list):
                        self.souls = v # list of souls transfigured by users
                except Exception as e:
                    string= "Error loading optional attributes for Techniques class"
                    print(string)
                    print(e)

        except Exception as e:
            fstring=f"Failed to configure technique {name}\n Check console for error"
            print(fstring)
            print(e)
 


enemy_techs = {
        "Orbmaster" :
        [ # list of moves 
            {
                "Impending Doom" : Techniques(
                    name="Orbmaster: Impending Doom",
                    level=1,
                    act_speed=10,
                    act_dur=1,
                    act_cost=100,
                    aoe=1,
                    strength=420,
                    speed=100,
                    type="attack projectile", # attack projectile, attack melee
                    sure_hit=True,
                )
            },
            {
                "Foresight" : Techniques(
                    name="Orbmaster: Foresight",
                    level=1,
                    act_speed=10,
                    act_dur=1,
                    act_cost=100,
                    aoe=1,
                    strength=400,
                    speed=200,
                    type="defense dodge", #defense tank, defense dodge, defense counter
                    sure_hit=True
                    )
            }
        ],
        
}    

for k, v in enemy_techs.items():
    print(k,v)



    

