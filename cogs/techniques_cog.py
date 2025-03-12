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
    def __init__(self, name: str, level: int, offense: dict, defense: dict, emote: str, techclass :str,activation_speed: int, activation_duration: int, activation_cost: int, poison: tuple, stun: tuple, negates: bool):
        try:
            self.name = name
            self.level = level
            self.emote = emote
            self.techclass= techclass # (is it for awakened sorcerers, curses, reincarnated, or mutants)
            self.act_spd = activation_speed
            self.act_dur = activation_duration
            self.act_cost = activation_cost 

        except Exception as e:
            fstring=f"Failed to configure technique {name}\n Check console for error"
            print(fstring)
            print(e)



class Offense(Technique):
     def __init__(self, name, level emote, techclass, activation_speed: int, activation_cost: int,activation_dur: int, strength: int, speed: int, aoe: int,imbued: int, poison: tuple, stun: int, sure_hit: bool, maximum: bool, negates: bool, soul: bool):
          super.__init__(name, level, emote, techclass)
          self.name = name
          self.level = level
          self.emoji = emote
          self.class = techclass
          self.act_spd = self.activation_speed
          self.act_cost = self.activation_cost
          self.act_dur = self.activation_duration
          self.strength = strength
          self.speed = speed
          self.aoe = aoe
          self.imbued=imbued
          self.poison = poison
          self.stun = stun
          self.sure_hit = sure_hit
          self.maximum = maximum
          self.negates = negates
          self.soul = soul

class Defense(Technique)
       def __init__(self, name, level, technique, emote, techclass, activation_speed, activation_cost, activation_dur, debuffs, buffs, aoe, imbued, poison, stun, sure_hit, maximum, negates, soul):
           super.__init__(name, level, technique, emote, techclass, activation_speed, activation_cost, activation_dur)
           self.name = name
           self.level = level
           self.tech = technique
           self.emoji = emote
           self.class =techclass
           self.act_speed = activation_speed
           self.act_cost = activation_cost
           self.act_dur = activation_duration
           self.debuffs = debuffs
           self.buffs = buffs
           self.aoe = aoe
           self.imbued = imbued
           self.poison = poison
           self.stun = stun
           self.sure_hit = sure_hit
           self.maximum = maximum
           self.soul = soul

          


   
      
    

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
    




