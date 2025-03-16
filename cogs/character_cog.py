import discord, os, random
from discord.ext import commands
from discord import app_commands
log_channel = int(os.getenv('LOGCHANNEL'))

techlist=["techniques under construction", "test run"]

class Character_cog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.channel = bot.get_channel(log_channel)

    @commands.hybrid_command(name="create", description="Create your player in the culling games! (only one player per colony)")
    async def create(self, ctx):
        embed= discord.Embed(title="Create a character: Start", description="# Welcome to the Culling Games!"
        "\n## The first step in creating your character, here you can spin for your player Class, Technique, and Cursed Energy!"
        "\n* You may only spin once for each attribute!")
        pclass = None
        tech = None
        ce= None
        embed.set_author(name=ctx.author.display_name, url=ctx.author.avatar, icon_url=ctx.author.avatar)
        embed.set_thumbnail(url=self.bot.user.avatar)
        msg = await ctx.send(embed=embed) 
        await msg.edit(view=CreateButtons(msg, embed, self.bot, tech, pclass, ce))
        return






class CreateButtons(discord.ui.View):
    def __init__(self, msg, embed, bot, tech, pclass, ce):
        super().__init__()
        self.bot = bot
        self.msg = msg
        self.embed=embed
        self.tech = tech
        self.pclass = pclass
        self.ce = ce

    @discord.ui.button(label="Class Spin", style=discord.ButtonStyle.blurple)
    async def class_spin(self, interaction: discord.Interaction, button: discord.Button):
        if self.embed.fields:
            for f in self.embed.fields:
                if f.name == "Class":
                    button.disabled=True
                self.embed.description= F"### Error you've already spun for a class!\n* Spin for Technique next!"
                await self.msg.edit(embed=self.embed, view=self)
            else:
                button.disabled=True
                self.embed.description= F"### Error you've already spun for a class!\n* Spin for Technique amount next!"
                await self.msg.edit(embed=self.embed, view=self)
        else:
            if self.pclass == None:
                button.disabled=True
                p = random.choice(['sorcerer', 'reincarnated', 'curse'])
                self.pclass= p
                self.embed.description = f"### You have landed on {p} class!\n* Next spin for your technique"
                self.embed.add_field(name="Class", value=f"`{p}`")
                await self.msg.edit(embed=self.embed, view=self)

    @discord.ui.button(label="Tech spin", style=discord.ButtonStyle.blurple)
    async def tech_spin(self, interaction: discord.Interaction, button: discord.Button):
        if self.embed.fields:
            for f in self.embed.fields:
                if f.name == "Technique":
                    button.disabled=True
                    self.embed.description= F"### Error you've already spun for a technique!\n* Spin for CE next!"
                    await self.msg.edit(embed=self.embed, view=self)
                    
                

                if f.name == "Class":
                        button.disabled=True
                        t = random.choice(techlist)
                        self.embed.description= f"### You landed on {t}!"
                        self.embed.add_field(name="Technique", value=f"{t}")
                        await self.msg.edit(embed=self.embed, view=self)
                        
                
                else:
                    self.embed.description= "### Pleaase spin for a class before spinning for your technique!"
                    await self.msg.edit(embed=self.embed, view=self)
        else:

                self.embed.description= "### Pleaase spin for a class before spinning for your technique or CE!"
                await self.msg.edit(embed=self.embed, view=self)
    


    @discord.ui.button(label="CE spin", style=discord.ButtonStyle.blurple)
    async def ce_spin(self, interaction: discord.Interaction, button: discord.Button):
       if self.embed.fields:
        for f in self.embed.fields:
                if f.name == "Technique":
                    button.disabled=True
                    t = random.randrange(500, 2000)
                    self.embed.description= f"### You've got `{t}` CE reserves!!"
                    self.embed.add_field(name="Cursed Energy", value=f"`{t}`")
                    await self.msg.edit(embed=self.embed, view=self)    
                else:
                    self.embed.description= "### Pleaase spin for a technique before spinning for your CE reserves!"
                    await self.msg.edit(embed=self.embed, view=self)
        else:
            self.embed.description= "### Pleaase spin for a class before spinning for your technique or CE!"
            await self.msg.edit(embed=self.embed, view=self)

async def setup(bot):
    await bot.add_cog(Character_cog(bot))