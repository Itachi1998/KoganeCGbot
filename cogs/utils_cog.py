import discord, os
from discord.ext import commands


class Utils_cog(commands.Cog):
<<<<<<< HEAD

=======
    
>>>>>>> 633bd848223991f88277710626f700338eb54a5b
    def __init__(self, bot):
        self.bot = bot
        self.log_channel = int(os.getenv('LOGCHANNEL'))
        self.channel = bot.get_channel(self.log_channel)
        self.avatar = bot.user.avatar
        self.botname = bot.user.name
    #@bot.events
    @commands.Cog.listener()
    async def on_ready(self):
        print('Utils cog is ready!')

    # learn command group
    @commands.hybrid_group(name='learn', desciption='Learn how to play the game', invoke_without_command=True)
    async def learn(self, ctx):
<<<<<<< HEAD
        group_embed = discord.Embed(title="Tutorial", description="# Welcome to the culling games!\n### Use one of the following learn commands to learn how to play!\n`Make sure to use ,learn <command> or /learn command to learn about each part!" )
        for subc in self.learn.walk_commands():
           name=subc.name
           description=subc.description
           group_embed.add_field(name=name, value=description)
        group_embed.set_author(name=self.botname, icon_url=self.avatar, url=self.avatar)
        group_embed.set_thumbnail(url=self.avatar)
        await ctx.send('Tutorial command group', embed=group_embed)
=======
        group_embed = discord.Embed(title="Tutorial", 
                                    description="Choose one of the following commands to learn about!\nYou can use either" 
                                    " `/learn <command_name>` or the prefix `,learn <command_name>`")
        try:
            for subc in learn.commands: #this doesn't access the learn command properly
                name=subc.name
                description=sync.description #sync isn't correctly done
                group_embed.add_field(name=name, description=description)
            await ctx.send('Tutorial command group', embed=group_embed)

        except Exception as e:
            error = (f'<learn command> from file <{__name__}> ERROR:\n{e}') #no clue how to get the name the method
            print(error)
            await ctx.send(error)
>>>>>>> 633bd848223991f88277710626f700338eb54a5b


    # CHANGED TO 'CHARACTER' INSTEAD OF 'CREATE' JUST SEEMED MORE FITTING LMK
    @learn.command(name='create', description='Learn how to create a character') 
    async def character(self, ctx):
        create_embed = discord.Embed(title='Learn: Create a character', description='Create a character by using the ,create or /create commands!\nThis will send you to an embed where you can spin for your stats!')
        create_embed.add_field(name='Spinning for a class', value='```You will get one of the following classes when creating your character```\n* Sorcerer: `Chance to get one of the elite clan techniques. Chance to get the 6 eyes. Most techniques of any classes, most variety. May gain CE by consuming fingers, but if CE is too much it can be poisonous. Types: support or attack`\n* Mutant: `enhanced physical abilities, can gain CE by consuming death wombs, abiliy to gain shrine through consuming fingers, immune to poison, advanced blood manipulation techniques, advanced self-rct, enhanced black flash luck, Type: attack`\n* HeavenlyRestricted: `Either maximized physical stats with no cursed energy, or minimized physical stats with the ability to increase cursed energy and create remote attack bots. Type: attack`\n* Curse: `Best base healing of all the classes, fastest ct level ups, access to techniques known for curses. Extra damage from RCT attacks. Type: attack or support`', inline=False)
        create_embed.add_field(name='Spinning for a technique', value='```This phase will take you through spinning for a technique specific to your class type```\n* Techniques are chosen depending on the class landed for your character.\n* Only one limitless technique available per colony.', inline=False)
        create_embed.add_field(name='Spinning for a CE amount', value='```This will determine the amount of CE reserves your character will have access to.```\n* This stat cannot be increased by skillpoints.\n* Mutants may increase CE by consuming death paintings.\n* Sorcerers may increase CE by being heavenly restricted, or consuming fingers. `warning: consuming too many fingers may lead to the reincarnation of the king of the cursed spirits`', inline=False)
        create_embed.add_field(name="Deleting your character", value='```You my use the /remove or ,remove command to delete your character from its current colony.```\n* `Warning: once a character is deleted you will not get it back` ', inline=False)
        create_embed.set_author(name=self.botname, icon_url=self.avatar, url=self.avatar)
        create_embed.set_thumbnail(url=self.avatar)
        await ctx.send(embed=create_embed, ephemeral=True)
        return
        

    # SHOULD THE LOBBY/BATTLE HELP COMMANDS BE TOGETHER OR SEPARATE ?
    @learn.command(name='lobby', description='Learn how to use the lobby functions') 
    async def lobby(self, ctx):
        lobby_embed = discord.Embed(title='Learn: Lobby functions', description='### Use the `,lobby` or `/lobby` command to create a lobby.\n### A lobby may also be created using the (`,pve` | `/pve`) or (`,pvp` | `/pvp`) commands')
        lobby_embed.add_field(name='Create a private lobby (invite only)', value='```To create an invite only lobby you must use the lock button```\n* `Must be owner to use this button`\n* Once you lock a lobby the button will turn into an unlock button to return to a public lobby\n* Can only create a lobby if in roaming mode', inline=False)
        lobby_embed.add_field(name="Game Mode", value="```Use the embed's PvE or PvP buttons to change game mode of the lobby. Or use the (,pve | /pve) and (,pvp | /pvp) commands```\n* Gamemode locked after everyone is ready\n* Must be selected to start a match")
        lobby_embed.add_field(name='Start', value= "```Start a game to fight other culling game players!```\n* Everyone in the lobby must be ready'd up\n* A PvE or PvP game mode must be set before starting a match\n* Equipping items must happen before a match starts. `Will not be able to equip items from inventory in match`")
        lobby_embed.add_field(name='Invite or Kick players', value='```Invite or kick players to your lobby (Must be in the same colony) using the lobby buttons Invite and Kick or the commands (,lobinv | /lobinv) and (,lobkick | /lobkick)```\n* May only invite active colony players\n* `Only owner may kick players`', inline=False)
        lobby_embed.add_field(name="Join lobby", value="```To join a lobby, enter the lobby code after using the ,lobby or /lobby commands, or use the join button on a lobby.```\n* If lobby is locked, only invited players may join")
        lobby_embed.add_field(name='Leave lobby', value='```Use the leave button to leave a lobby. Or use the ,leave or /leave commands```\n* Can leave during active battles but may be hit if defense check is failed', inline=False)
        lobby_embed.add_field(name='Ready up', value='```All players must be ready before a match can begin, using the ready up lobby button or the /ready and ,ready commands```', inline=False)
        lobby_embed.set_author(name=self.botname, icon_url=self.avatar, url=self.avatar)
        lobby_embed.set_thumbnail(url=self.avatar)
        await ctx.send(embed=lobby_embed, ephemeral=True)
        return


    @learn.command(name='battle', description='Learn how to battle')
    async def battle(self, ctx):
        battle_embed = discord.Embed(title='Learn: Battle commands', description='You will learn how to use battle commands...')
        battle_embed.add_field(name='Enable PVE', value='To enable PVE...', inline=False)
        battle_embed.add_field(name='Enable PVP', value='To enable PVP...', inline=False)
        battle_embed.add_field(name='More about PVE & PVP', value='To learn more about PVE lobbies, enter "/learn pve". '
        'To learn more about PVP lobbies, enter "/learn pvp."', inline=False)
        battle_embed.set_author(name=self.botname, icon_url=self.bot.user.avatar, url=self.avatar)
        battle_embed.set_thumbnail(url=self.avatar)
        await ctx.send(embed=battle_embed, ephemeral=True)
        return
    

 

# class Help_buttons(discord.ui.View):
#     def __init__(self):
#         super().__init__(timeout=200)
#         self.add_item(learn_button())

#     @discord.ui.button(label='learn', style=discord.ButtonStyle.primary)
#     async def learn_button(self, button: discord.ui.Button, ctx: discord.ctx):
#         button.disabled=True
#         await Utils_cog.help(ctx)
#         description = """
# Use /create to create a character, choose a class, and spin 
# """ 
#         embed=discord.Embed(title='learn', description='Learn how to play!', color=discord.Color.green())
#         await ctx.response.send_message(embed=embed, view=self)
        
    
async def setup(bot):
    await bot.add_cog(Utils_cog(bot))  