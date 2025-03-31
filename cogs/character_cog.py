import discord, os, random, techniques, db, game, player_tech
from random import randint
from game import Player
from db import create_player, update_player, update_colony
from discord.ext import commands
from discord import app_commands

sorcerer_techs = [
                  player_tech.hr_zero,
                  player_tech.auspicious_beasts_summon,
                  player_tech.bird_manip,
                  player_tech.blood_manip,
                  player_tech.comedian,
                  player_tech.cursed_spirit_manip,
                  player_tech.construction,
                  player_tech.projection_sorcery,
                  player_tech.ten_shadows,
                  player_tech.straw_doll,
                  player_tech.limitless,
                  player_tech.copy,
                  player_tech.star_rage
                  ]

reincarnated_techs = [
    player_tech.shrine, player_tech.mba, player_tech.construction, player_tech.blood_manip
                      ]

cursed_techs = [
    player_tech.soul_manipulation, player_tech.projection_sorcery
    ]

def get_random_sorcerer_tech(techlist=sorcerer_techs):
    rarity = {"legend" : 5, "rare" : 15, "uncommon" : 30, "common" : 50}
    sum = 0
    value=0
    for r in rarity:
        sum += rarity[r]
    choice = randint(1, sum)
    while value==0:
        choice = randint(1, sum)
        for r in rarity:
            if choice <= rarity[r]:
                value = choice
                break
            choice -= rarity[r]
    print(f"Getting technique value: {value}")
    ct_list = [t for t in techlist if t.get("Rarity", 0) >= value]
    tech = random.choice(ct_list)
    tech_name = next(iter(tech))
    print(f"Getting technique: {tech_name}, rarity level: {tech["Rarity"]}")
    if "Six Eyes" in tech.keys():
        six_values = randint(0, 10)
        if six_values <= 5:
            tech['Six Eyes'] = True
    return tech

def get_random_reincarnate_tech(techlist=reincarnated_techs):
    rarity = {"legend" : 5, "rare" : 15, "uncommon" : 30, "common" : 50}
    sum = 0
    value=0
    for r in rarity:
        sum += rarity[r]

    while value==0:
        choice = randint(1, sum)
        for r in rarity:
            if choice <= rarity[r]:
                value = choice
                break
            choice -= rarity[r]
        
        print(f"Getting technique value: {value}")
        ct_list = [t for t in techlist if t.get("Rarity", 0) >= value]
        if ct_list:  # Ensure the list is not empty
            break
        print("No techniques found for the selected rarity, retrying...")
    
    tech = random.choice(ct_list)
    tech_name = next(iter(tech))
    print(f"Getting technique: {tech_name}, rarity level: {tech["Rarity"]}")
    if "Six Eyes" in tech.keys():
        six_values = randint(0, 10)
        if six_values < 5:
            tech['Six Eyes'] = True
    return tech

def get_random_curse_tech(techlist=cursed_techs):
    rarity = {"legend" : 5, "rare" : 15, "uncommon" : 30, "common" : 50}
    sum = 0
    value=0
    for r in rarity:
        sum += rarity[r]
    choice = randint(0, sum)
    #50
    while value==0:
        for r in rarity:
            if choice <= rarity[r]:
                value=choice
            else:
                choice -= rarity[r]
    print(f"Getting technique value: {value}")
    ct_list = [t for t in techlist if t.get("Rarity", 0) >= value]
    tech = random.choice(ct_list)
    tech_name = next(iter(tech))
    print(f"Getting technique: {tech_name}, rarity level: {tech["Rarity"]}")
    return tech


class Character_cog(commands.Cog):

    welcstr="# Welcome to Kogane Culling Games!"

    def __init__(self, bot):
        self.bot = bot
        self.playerdict={}


    @commands.hybrid_command(name="create", description="Create your player in the culling games! (only one player per colony)")
    async def create(self, ctx, name: str=None):
        if not name:
            name=ctx.author.display_name
        self.playerdict["name"] = name
        embed= discord.Embed(title="Create a character", description=self.welcstr +
        "\n## The first step in creating your character, here you can spin for your player Class, Technique, and Cursed Energy!"
        "\n* You may only spin once for each attribute!")
        embed.set_author(name=ctx.author.display_name, url=ctx.author.avatar, icon_url=ctx.author.avatar)
        embed.set_thumbnail(url=self.bot.user.avatar)
        await ctx.send(embed= embed, view=CreateButtons(embed, self.bot, self.playerdict))
        return


class CreateButtons(discord.ui.View):
    def __init__(self, embed, bot, playerdict: dict, timeout=30,):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.embed=embed
        self.playerdict=playerdict
        self.welcome = "## `Welcome to Kogane Culling Games!`"


    @discord.ui.button(label="Spin", style=discord.ButtonStyle.primary)
    async def spin(self, interaction: discord.Interaction, button: discord.Button):
        pclass= randint(1,3)
        if pclass== 1:
           tech= get_random_sorcerer_tech()
        if pclass == 2:
           tech =  get_random_reincarnate_tech()
        if pclass == 3:
            tech = get_random_curse_tech()
        ce = random.randrange(200, 2000)  
        six_eyes="None"
        print(tech)
        if 'Six Eyes' in tech.keys() and tech['Six Eyes'] == True:
            ce += 1000
            six_eyes="True"

        if 'copy' or 'shrine' or 'limitless' or 'star rage' or 'cursed spirit manip' in next(iter(tech)).lowered():
            ce += 1000

        if 'zero' in next(iter(tech)).lower():
            ce = 0
        if pclass==1:
            pclass = "Sorcerer"
        elif pclass ==2:
            pclass = "Reincarnate"
        elif pclass == 3:
            pclass = "Curse"
        else:
            return await interaction.response.send_message("Error setting player class")
        self.embed.description=f"* Name: {self.playerdict['name']}\n* Level: 0\n* Technique: {next(iter(tech))}\n* CE: {ce}\n* Class: {pclass}\n* Six Eyes: {six_eyes}"
        await interaction.response.edit_message(embed=self.embed, view=None)
        return



async def setup(bot):
    await bot.add_cog(Character_cog(bot))