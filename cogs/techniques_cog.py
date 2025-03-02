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
    def __init__(self, name: str, level: int, offense: dict, defense: dict, emote: str, discription: str, rarity: int, techclass :str, **kwargs):
        try:
            self.name = name
            self.level = level
            self.offense = offense
            self.defense = defense
            self.emote = emote
            self.discription = discription
            self.rarity = rarity
            self.techclass= techclass


        except Exception as e:
            fstring=f"Failed to configure technique {name}\n Check console for error"
            print(fstring)
            print(e)






class Offense():
    def __init__(self, name: str, level: int, damage: int, reforce: reforce, accuracy: int, crit: int, speed: int, cost: int, neg: bool, pen: int, aoe: int):
        try:
            self.reforce = reforce #ce reinforcement cost per use
            self.damage = damage #damage of technique
            self.accuracy = accuracy #hit chance
            self.crit = crit #black flash chance
            self.speed = speed #speed of technique
            self.cost = cost # ce cost per use
            self.neg = neg  #negate's defense
            self.pen = pen #penetration
            self.aoe = aoe #area of effect
   
            self.name = name
            self.level = level #level required
        except Exception as e:
            fstring=f"Failed to configure offense {damage}\n Check console for error"
            print(fstring)
            print(e)
    
    def to_dict(self):
        return self.__dict__
    
    

class Defense():
    def __init__(self, name: str, level: int, block: int, dodge: int, reforce: int, speed: int, cost: int, neg: bool, debuff: int):
        try:
            self.name = name 
            self.block = block #block chance
            self.dodge = dodge #dodge chance
            self.reforce = reforce #ce reinforcement cost per use
            self.speed = speed #speed of defense
            self.cost = cost # ce cost per use
            self.neg = neg  #negate's attack
            self.level = level #level required
            self.debuff = debuff #debuff like simple domain or falling blossom emotion
        

        except Exception as e:
            fstring=f"Failed to configure defense {block}\n Check console for error"
            print(fstring)
            print(e)

    def to_dict(self):
        return self.__dict__
    

class Domain():
    def __init__(self, name: str, level: int, offense: dict, defense: dict, emote: str, turns: int):
        try:
            self.name = name
            self.level = level
            self.offense = offense
            self.defense = defense
            self.emote = emote
            self.turns = turns #amount of turns active

        except Exception as e:
            fstring=f"Failed to configure domain {name}\n Check console for error"
            print(fstring)
            print(e)

    def to_dict(self):
        return self.__dict__
    
class MaximumTech():
    def __init__(self, level: int, name: str, reforce: int, damage: int, accuracy: int, speed: int, cost: int, aoe: int, pen: int, neg: bool):
        try:
            self.level = level
            self.reforce = reforce #ce reinforcement cost per use
            self.damage = damage #damage of technique
            self.accuracy = accuracy #hit chance
            self.speed = speed #speed of technique
            self.cost = cost # ce cost per use
            self.neg = neg  #negate's defense
            self.pen = pen #penetration
            self.aoe = aoe #area of effect

        except Exception as e:
            fstring=f"Failed to configure maximum technique {name}\n Check console for error"
            print(fstring)
            print(e)

    def to_dict(self):
        return self.__dict__
    

class Shikigami():
    def __init__(self, name: str, level: int, offense: dict, defense: dict, emote: str, discription: str, rarity: int, shikiclass :str, **kwargs):
        try:
            self.name = name
            self.level = level
            self.offense = offense
            self.defense = defense
            self.emote = emote
            self.discription = discription
            self.rarity = rarity
            self.shikiclass= shikiclass

        except Exception as e:
            fstring=f"Failed to configure shikigami {name}\n Check console for error"
            print(fstring)
            print(e)

    def to_dict(self):
        return self.__dict__
    




