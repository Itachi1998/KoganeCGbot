import discord, os
from discord.ext import commands


class Utils_cog(commands.Cog):

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


    # CHANGED TO 'CHARACTER' INSTEAD OF 'CREATE' JUST SEEMED MORE FITTING LMK
    @learn.command(name='create', description='Learn how to create a character') 
    async def character(self, ctx):
        create_embed = discord.Embed(title='Learn: Create a character', description='Create a character by using the ,create or /create commands!\nThis will send you to an embed where you can spin for your stats!')
        create_embed.add_field(name='Spinning for a class', value='```You will get one of the following classes when creating your character```\n* Sorcerer: `Chance to inherit a technique. Chance to get the 6 eyes. Most techniques of any classes, most variety. May gain CE by consuming fingers, but if CE is too much it can be poisonous. Types: support or attack`\n* Mutant: `enhanced physical abilities, can gain CE by consuming death wombs, abiliy to gain shrine through consuming fingers, immune to poison, advanced blood manipulation techniques, advanced self-rct, enhanced black flash luck. Slow CT level up. Type: attack`\n* Reincarnated: `Chance to get ancient sorcery techniques. Ability to consume fingers without the worry of poison. High base CT level due to prior experience in their past lives. Type: attack or support`\n* Curse: `Best base healing of all the classes, fastest ct level ups, access to techniques known for curses. Take extra damage from RCT attacks. Type: attack or support`', inline=False)
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
        battle_embed = discord.Embed(title='Learn: Battle commands', description='### Before you can start a battle, you must have a lobby with every player ready. Once everyone in the lobby is ready, and the game mode is selected, use the start button or /start | ,start command')
        battle_embed.add_field(name='PvP', value='```PVP is the player vs player mode. Here you will face off against real players in turn based rounds.```\n* Enabled using the (,pvp | /pvp) commands or using the button.\n* Greater rewards than battling NPCs in PVE (usually)', inline=False)
        battle_embed.add_field(name='PvE', value="```PVE is the player vs enviornment mode. Here you will face off against NPC culling game players.```\n* Enabled using the (,pve | /pvp) commands or button\n* Rewards grow as you fight higher level enemies.\n* Stronger enemies have respawn timers", inline=False)
        battle_embed.add_field(name="Leave", value="```You can leave a lobby in queue mode at any time. But must pass defense checks to leave an active battle unharmed.```\n* Help from a support type character may aid your escape from an active battle\n* If available, you may surrender game points in exchange for escape.\n* Having a technique that increases your speed active may help your escape\n* The chances of escape vary depending on physical speed and active technique")
        battle_embed.add_field(name="Tech Activation", value="```To activate your technique, you must be in an active battle. You can use the (,technique | /technique) commands or the battle buttons to activate a technique. You will get a private pop up prompting you to pick a technique.```\n* Each tecehnique will have statistics displayed\n* May reinforce strength, speed, or technique with CE at this stage.\n* Each technique will have a CE chargec.\n* May choose to take a defensive stance or heal at this stage.")
        battle_embed.add_field(name="Melee Attacks", value="```Use physical attacks to land combos on your enemies. Activate using the (,melee | /melee) command or the melee button. You will get a private prompt of combos you can use.```\n* If you have a cursed tool equipped, using a melee attack will show you extra prompts for the cursed tool combos.\n* May infuse CE into melee attacks.")
        battle_embed.add_field(name="Cursed Tools", value="```Must be equipped prior to battle activation. Use the (,equip | /equip) commands from lobby or the equip lobby button to equip from your inventory. You may also equip and unequip (,unequip | /unequip) items outside of a lobby.```\n* During battles, you may activate your cursed tool with a (,melee | /melee) attack.\n* Cursed tools may add aditional moves to a players melee options.\n* Cursed tools can be acquired at the (,shop | /shop).")
        battle_embed.add_field(name="Summons and Rituals", value="```Some techniques allow you to (,summon | /summon) Shikigami or Spirits. This will create an additional turn for you, allowing you to attack or support using the summon's abilities. Some cursed spirit players will have the option to be tamed if weak enough. Some techniques require (,ritual | /ritual)'s to tame Shikigami for summoning.```\n*  Ritual starts a private 1 on 1 match with a Shikigami.\n* If a Ritual is used in battle it will include everyone in the battle as the Shikigami's enemy.\n* Ritual Shikgami target the caster of the ritual first.\n* Summoning Shikigami or Spirits requires technique activation without a talisman or a tamed spirit in your inventory.")
        # TODO add field for leaving battles, add fields for technique usages, add field for physical attacks, add field for cursed tool usage, add field for summons
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