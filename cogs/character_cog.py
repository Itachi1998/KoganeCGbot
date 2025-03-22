import discord, os, random, techniques, db
from discord.ext import commands
from discord import app_commands


log_channel = int(os.getenv('LOGCHANNEL'))

techlist=["techniques under construction", "test run"]

class Character_cog(commands.Cog):

    welcstr="# Welcome to Kogane Culling Games!"
    def __init__(self, bot):
        self.bot = bot
        self.channel = bot.get_channel(log_channel)

    @commands.hybrid_command(name="create", description="Create your player in the culling games! (only one player per colony)")
    async def create(self, ctx, name=str):
        embed= discord.Embed(title="Create a character", description=self.welcstr +
        "\n## The first step in creating your character, here you can spin for your player Class, Technique, and Cursed Energy!"
        "\n* You may only spin once for each attribute!")
        embed.set_author(name=ctx.author.display_name, url=ctx.author.avatar, icon_url=ctx.author.avatar)
        embed.set_thumbnail(url=self.bot.user.avatar)
        msg = await ctx.send(embed=embed) 
        await msg.edit(view=CreateButtons(msg, embed, self.bot, name))
        return






class CreateButtons(discord.ui.View):
   
    def __init__(self,  msg, embed, bot, name: str, timeout=30):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.msg = msg
        self.embed=embed
        self.name = name
        self.welcome = "## `Welcome to Kogane Culling Games!`"


    @discord.ui.button(label="Spin", style=discord.ButtonStyle.premium)
    async def spin(self, interaction: discord.Interaction, button: discord.Button):
        emb = self.embed
        col = db.read_colony(interaction.guild.id)
        user_id = self.interaction.user.id
        pclass = random.chocie(['sorcerer', 'reincarnated', 'curses'])
        if pclass == 'sorcerer':
            tech = technqiues.get_tech(col, pclass)
            if 'six eyes' in tech:
                ce = random.randrage(500, 2000)
                ce += 1000
                col.six_eyes = True
                ct_level = 3
                create_player(user_id, col.colony_id, playername=self.name, playerclass=pclass, technique=tech, max_ce=ce, max_hp=1000, six_eyes=True)
                update_colony(interaction.guild.id, {"six_eyes": True})

        
            
            

                
            
            

            



        async def on_timeout(self):
            for child in self.children:
                child.disabled = True
            self.embed.description = "### Embed timed out"
            await self.msg.edit(embed=self.embed, view=self)


async def setup(bot):
    await bot.add_cog(Character_cog(bot))