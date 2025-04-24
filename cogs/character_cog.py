import discord, os, random, techniques, db, game, player_tech, datetime
from random import randint
from game import Player
from db import create_player, update_player, update_colony, create_technique
from models import Technique
from discord.ext import commands
from discord import app_commands

sorcerer_techs = [
    player_tech.anti_gravity, 
    player_tech.auspicious_beasts_summon, 
    player_tech.bird_manip, 
    player_tech.blood_manip, 
    player_tech.boogie_woogie,
    player_tech.comedian, 
    player_tech.construction, 
    player_tech.copy, 
    player_tech.cursed_speech, 
    player_tech.cursed_spirit_manip,
    player_tech.hr_max, 
    player_tech.hr_zero,
    player_tech.limitless,
    player_tech.projection_sorcery,
    player_tech.star_rage, 
    player_tech.straw_doll, 
    player_tech.ten_shadows
    ]

reincarnated_techs = [
    player_tech.blood_manip, 
    player_tech.body_hop, 
    player_tech.ce_discharge, 
    player_tech.construction, 
    player_tech.cursed_speech, 
    player_tech.explosive_flesh,
    player_tech.ice_manip,
    player_tech.mba, 
    player_tech.shrine, 
    player_tech.sky_manip, 
    player_tech.ten_shadows
    ]

cursed_techs = [
    player_tech.disaster_flames, 
    player_tech.disaster_plants, 
    player_tech.disaster_tides,
    player_tech.idle_transfig, 
    player_tech.projection_sorcery
    ]

classes = {"Sorcerer" : 50, "Curse" : 30, "Reincarnate" : 15}

def get_random_class(classlist=classes):
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
    class_list = []
    for c in classes:
        if classes[c] >= choice:
            class_list.append(c)

    class_pick = random.choice(class_list)
    return class_pick
    



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
    ct_list = []
    for t in techlist: 
        if t['Rarity'] >= value:
            ct_list.append(t)
    tech = random.choice(ct_list)
    tech_name = next(iter(tech))
    print(f"Getting technique: {tech_name}, rarity level: {tech['Rarity']}")

    if "Six Eyes" in tech.keys():
        if tech['Six Eyes'] != True:
            six_values = random.randint(1, 2)
            if six_values == 1:
                tech['Six Eyes'] = True
                #cuz he not number 2

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
    ct_list=[]
    for t in techlist: 
        if t['Rarity'] >= value:
            ct_list.append(t)
    tech = random.choice(ct_list)
    print(f"value: {value} technique list with greater rarity values: {ct_list}")
    tech_name = next(iter(tech))
    print(f"Getting technique: {tech_name}, rarity level: {tech['Rarity']}")
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
    ct_list = []
    for t in techlist: 
        if t['Rarity'] >= value:
            ct_list.append(t)
        else:
            value -= t['Rarity']

    if len(ct_list) == 0:
        ct_list = [t for t in techlist if t['Rarity'] >= rarity['uncommon']]
    tech = random.choice(ct_list)
    tech_name = next(iter(tech))
    print(f"Getting technique: {tech_name}, rarity level: {tech['Rarity']}")
    return tech


class Character_cog(commands.Cog):

    welcstr="# Welcome to the Discord Culling Game "
    def __init__(self, bot):
        self.bot = bot
        self.playerdict={}


    @commands.hybrid_command(name="create", description="Create your player in the culling games! (only one player per colony)")
    async def create(self, ctx, name: str=None):
        if not name:
            name=ctx.author.display_name
        self.playerdict["colony"] = ctx.guild.id
        self.playerdict["name"] = name
        embed= discord.Embed(title="Create a character", description= self.welcstr + name +
        "\n## The first step in creating your character, here you can spin for your player Class, Technique, and Cursed Energy!"
        "\n* You may only spin once for each attribute!")
        embed.set_author(name=ctx.author.display_name, url=ctx.author.avatar, icon_url=ctx.author.avatar)
        embed.set_thumbnail(url=self.bot.user.avatar)
        embed.set_footer(text="Click the button to spin for your stats!", icon_url=self.bot.user.avatar)
        embed.color=discord.Color.from_rgb(255, 0, 0)
        await ctx.send(embed= embed, view=CreateButtons(embed, self.bot, self.playerdict, user=ctx.author.id))
        return
    
    @commands.hybrid_command(name="delete", description="Delete your player in the culling games!")
    async def delete(self, ctx):
        existing_player = db.read_player(user_id=ctx.author.id, colony_id=ctx.guild.id)
        if existing_player:
            playername = existing_player['name']
            db.delete_player(user_id=ctx.author.id, colony_id=ctx.guild.id)
            db.delete_technique(user_id=ctx.author.id, colony_id=ctx.guild.id)
            embed = discord.Embed(title="Deleted player", description=f"Deleted {playername} player from {ctx.guild.name}")
            await ctx.send(embed=embed, ephemeral=True)


    @commands.hybrid_command(name="profile", description="View your player profile, or someone else's!")
    async def profile(self, ctx, user: discord.User=None):

        if not user:
            user = ctx.author

        player_dict = db.read_player(user_id=user.id, colony_id=ctx.guild.id)
        technique = player_dict['techniques'][0]
        techname = technique['name']
        del player_dict['techniques']
        player_dict['technique'] = techname
        player = Player(**player_dict)

        if not player:
            await ctx.send("Player does not exist")
            return
    
        colony = db.read_colony(colony_id=ctx.guild.id)
        
        if not colony:
            await ctx.send("You are not in a colony")
            return
        
        if player.colony != colony.colony_id:
            await ctx.send("You are not in this colony")
            return
        
        if player:
            embed = discord.Embed(title=f"Player Profile", description="## Colony: `" + colony.colony_name + "`\n## " + player.name)
            embed.add_field(name="Level", value="`" + str(player.level) + "`", inline=True)
            embed.add_field(name="Health", value="`" + str(player.hp) + "`", inline=True)
            embed.add_field(name="Energy", value="`" + str(player.ce) + "`", inline=True)
            embed.add_field(name="Strength", value=f"`{player.strength}`", inline=True)
            embed.add_field(name="Speed", value=f"`{player.speed}`", inline=True)
            embed.add_field(name="Game Points", value=f"`{player.cgp}`")
            embed.add_field(name="Exp", value="`" + str(player.xp) + "`", inline=True)
            embed.add_field(name="Skillpoints", value="`" + str(player.skp) + "`", inline=True)
            embed.add_field(name="Class", value="`" + player.playerclass + "`", inline=True)
            embed.add_field(name="Technique", value="`" + techname + "`", inline=True)
            embed.add_field(name="Status", value="`Active`", inline=True)
            embed.set_author(name=user.display_name, url=user.avatar, icon_url=user.avatar)
            embed.set_thumbnail(url=self.bot.user.avatar)
            await ctx.send(embed=embed)
            return
        else:
            await ctx.send("Player does not exist in this colony")
            return



class CreateButtons(discord.ui.View):
    def __init__(self, embed, bot, playerdict: dict, user: int, timeout=30):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.embed=embed
        self.playerdict=playerdict
        self.welcome = "## `Welcome to Kogane Culling Games!`"
        self.user = user


    @discord.ui.button(label="Spin", style=discord.ButtonStyle.primary)
    async def spin(self, interaction: discord.Interaction, button: discord.Button):
        ce = random.randint(200, 2000)
        strength=random.randint(50, 200)
        speed=random.randint(50, 200)
        hp = random.randint(100, 300)
        pclass= get_random_class()
        tech = None

        if pclass== "Sorcerer":
            strength += 100
            speed += 100
            hp += 100
            ce += 50
            tech= get_random_sorcerer_tech()
        if pclass == "Reincarnate":
            ce += 100
            tech =  get_random_reincarnate_tech()      
            strength+= 120
            speed += 120
            hp += 150
        if pclass == "Curse":
            ce += 200
            strength += 150
            speed += 150
            hp += 150
            tech = get_random_curse_tech()
        six_eyes=False
        techname= next(iter(tech))
        print(f"rolled {techname}")

        if 'Six Eyes' in tech.keys() and tech['Six Eyes'] == True:
            print("Added 6 eyes ce: 1000 to " +  str(ce))
            ce += 1000
            hp += 300
            six_eyes=True

        if any(keyword in techname.lower() for keyword in ['copy', 'shrine', 'limitless']):
            print("Added copy, shrine, limitless, star rage, or cursed spirit manip ce boost of 1000 to: \n"+ next(iter(tech)) )
            ce += 1000
            hp += 100

        if techname == "Shrine":
            ce += 2000
            hp += 200

        if 'zero' in techname.lower():
            strength += 200
            speed += 200
            hp += 300
            ce = 0
        entered = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        player = Player(
            name=self.playerdict['name'],
            level=1,
            max_hp=hp,
            max_ce=ce,
            speed=speed,
            strength=strength,
            technique=techname,
            playerclass=pclass,
            colony_id=self.playerdict['colony'],
            xp=0,
            cgp=0,
            skp=0,
            user_id=interaction.user.id,
            six_eyes=six_eyes,
            entered=entered
        )
        created = create_player(player)
        rarity = {"legend": 5, "rare": 15, "uncommon": 30, "common": 50}
        tech_rarity = next((k for k in rarity.keys() if rarity[k] == tech['Rarity']), None)
        class_rarity = next((k for k in rarity.keys() if rarity[k] == classes[pclass]), None)
        if created:
            print ("Created technique: " + techname)
            self.embed.description=f"* Name: {player.name}\n* Level: {player.level}\n* Technique: {techname}\n* HP: {hp}\n* CE: {ce}\n* Class: {pclass}\n* Six Eyes: {six_eyes}\n* Speed: {player.speed}\n* Strength: {player.strength}\n* Technique Rarity: {tech_rarity}\n* Class Rarity: {class_rarity}"
            self.embed.set_footer(text="Use /profile to view your character!", icon_url=self.bot.user.avatar)
            await interaction.response.edit_message(embed=self.embed, view=None)
            return
        else:
            await interaction.response.send_message("You cannot create more than one player per colony")

async def setup(bot):
    await bot.add_cog(Character_cog(bot))
