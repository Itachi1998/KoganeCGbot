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
    def __init__(self, name: str, level: int, offense: dict, defense: dict, emote: str, discription: str, rarity: int, hr: bool):
        try:
            self.name = name
            self.level = level
            self.offense = offense
            self.defense = defense
            self.emote = emote
            self.discription = discription
            self.rarity = rarity
            self.hr = hr


        except Exception as e:
            fstring=f"Failed to configure technique {name}\n Check console for error"
            print(fstring)
            print(e)




        
    
    