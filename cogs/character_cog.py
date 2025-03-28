import discord, os, random, techniques, db, game, techniques
from game import Player
from techniques import generate_tech
from db import create_player, update_player, update_colony
from discord.ext import commands
from discord import app_commands


log_channel = int(os.getenv('LOGCHANNEL'))

techlist=["techniques under construction", "test run"]


class Character_cog(commands.Cog):

    welcstr="# Welcome to Kogane Culling Games!"
    def __init__(self, bot):
        self.bot = bot
        self.playerdict={}
        self.channel = bot.get_channel(log_channel)

    @commands.hybrid_command(name="create", description="Create your player in the culling games! (only one player per colony)")
    async def create(self, ctx, name: str=None):
        self.playerdict={}
        if not name:
            name=ctx.author.display_name
        self.playerdict["name"] = name
        embed= discord.Embed(title="Create a character", description=self.welcstr +
        "\n## The first step in creating your character, here you can spin for your player Class, Technique, and Cursed Energy!"
        "\n* You may only spin once for each attribute!")
        embed.set_author(name=ctx.author.display_name, url=ctx.author.avatar, icon_url=ctx.author.avatar)
        embed.set_thumbnail(url=self.bot.user.avatar)
        msg = await ctx.send(embed=embed) 
        await msg.edit(view=CreateButtons(msg, embed, self.bot, playerdict))
        return


class CreateButtons(discord.ui.View):
    def __init__(self, embed, bot, playerdict: dict, timeout=30,):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.embed=embed
        self.playerdict=playerdict
        self.welcome = "## `Welcome to Kogane Culling Games!`"


    @discord.ui.button(label="Spin", style=discord.ButtonStyle.premium)
    async def spin(self, interaction: discord.Interaction, button: discord.Button):
        pclass= random.choice(1, 2, 3)
        tech_dict= generate_tech()
        ce = random.randrange(200, 2000)  
        async def on_timeout(self):
            for child in self.children:
                child.disabled = True
            self.embed.description = "### Embed timed out"
            await self.msg.edit(embed=self.embed, view=self)


async def setup(bot):
    await bot.add_cog(Character_cog(bot))