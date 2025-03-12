import discord, os
from pagination import Pagination
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


    # CHANGED TO 'CHARACTER' INSTEAD OF 'CREATE' JUST SEEMED MORE FITTING LMK
    @learn.command(name='create', description='Learn how to create a character') 
    async def character(self, ctx):
        pages= [
            discord.Embed(title="Learn: How to Create a player! - Page 1", description="# Table of Contents\n* Learn how to spin for a class: Page 1\n* Learn how to spin for a technique: Page 2\n* Learn how to Spin for your CE amount: Page 3\n* Learn How to delete your player: Page 4\n# Player Class information:\n### `use (,spin class or /spin class) spin for your class`\n```You will get one of the following classes when creating your player```\n* Sorcerer: `Chance to inherit a technique. Chance to get the 6 eyes. May gain CE by consuming fingers, but if CE is too much it can be poisonous. Types: support or attack. `\n* Mutant: `enhanced physical abilities, can gain CE by consuming death wombs, abiliy to gain shrine through consuming fingers, immune to poison, advanced self-rct, enhanced black flash luck. Slow CT level up. Type: attack. `\n* Reincarnated: `Chance to get ancient sorcery techniques. Ability to consume fingers without the worry of poison. High base CT level due to prior experience in their past lives. Type: attack or support.`\n* Curse: `Best base healing of all the classes, fastest ct level ups, access to techniques known for curses. Take extra damage from RCT attacks. Type: attack or support`"),
            discord.Embed(title="Learn: How to Create a player! - Page 2", description ="# Technique Spins\n### `spin for a technique using the (,spin tech | /spin tech) commands or the spin button`\n```This phase will take you through spinning for a technique specific to your class type```\n* Only sorcerer's can get a 6 eyes technique.\n* Only 1 six eyes per colony is allowed.\n* Only reincarnated sorcerers can unlock Shrine\n* A sorcerer's blood manipulaton technique is capped much lower than a Mutant\n* There are two types of heavenley restrictions: `max` or `zero`\n* Max HR users gain the ability to flood the battle with mechabots and increase their CE with skillpoints\n* Techniques have levels to them, some technique levels go higher than others.\n* Some techniques have domains\n* Some techniques have maximum techniques\n* Distaster techniques are unique to curses\n* 6 eye techniques get special moves\n* Mutants can unlock Shrine by eating fingers"),
            discord.Embed(title="Learn: How to Create a player! - Page 3", description='# Spinning for your cursed energy\n### `Use the (,spin ce | /spin ce) commands to spin!`\n```This will determine the amount of CE reserves your character will have access to.```\n* This stat cannot be increased by skillpoints.\n* Mutants may increase CE by consuming death paintings.\n* Sorcerers may increase CE by being heavenly restricted, or consuming fingers. `warning: mutants are the only ones capable of controlling the demon inside the fingers`\n'),
            discord.Embed(title="Learn how to Delete a player! - Page 4", description = '```You my use the /remove or ,remove command to delete your character from its current colony.```\n* `Warning: once a character is deleted you will not get it back`\n* If you wish to delete another users player, defeat them in battle!')
        ]

        async def get_page(page: int):
            emb = pages[page - 1]
            emb.set_author(name=self.botname, icon_url=self.avatar, url=self.avatar)
            emb.set_thumbnail(url=self.avatar)
            return emb, len(pages)
        
        pagination = Pagination(ctx.interaction, get_page)
        await pagination.navegate()

        
    # @tree.command(name="show")
    # async def show(interaction: discord.Interaction):
    #     async def get_page(page: int):
    #         emb = discord.Embed(title="The Users", description="")
    #         offset = (page-1)
    #         emb.set_author(name=f"Requested by {interaction.user}")
    #         n = Pagination.compute_total_pages(
    #         emb.set_footer(text=f"Page {page} from {n}"))
    #         return emb, n

    # SHOULD THE LOBBY/BATTLE HELP COMMANDS BE TOGETHER OR SEPARATE ?
    @learn.command(name='lobby', description='Learn how to use the lobby functions') 
    async def lobby(self, ctx):
         pages = [
            discord.Embed(title='Learn: Lobby functions - Page 1', description='### Use the `,lobby` or `/lobby` command to create a lobby.\n### A lobby may also be created using the (`,pve` | `/pve`) or (`,pvp` | `/pvp`) commands')
            .add_field(name='Create a private lobby (invite only)', value='```To create an invite only lobby you must use the lock button```\n* `Must be owner to use this button`\n* Once you lock a lobby the button will turn into an unlock button to return to a public lobby\n* Can only create a lobby if in roaming mode', inline=False),
            discord.Embed(title='Learn: Lobby functions - Page 2')
            .add_field(name="Game Mode", value="```Use the embed's PvE or PvP buttons to change game mode of the lobby. Or use the (,pve | /pve) and (,pvp | /pvp) commands```\n* Gamemode locked after everyone is ready\n* Must be selected to start a match"),
            discord.Embed(title='Learn: Lobby functions - Page 3')
            .add_field(name='Start', value= "```Start a game to fight other culling game players!```\n* Everyone in the lobby must be ready'd up\n* A PvE or PvP game mode must be set before starting a match\n* Equipping items must happen before a match starts. `Will not be able to equip items from inventory in match`"),
            discord.Embed(title='Learn: Lobby functions - Page 4')
            .add_field(name='Invite or Kick players', value='```Invite or kick players to your lobby (Must be in the same colony) using the lobby buttons Invite and Kick or the commands (,lobinv | /lobinv) and (,lobkick | /lobkick)```\n* May only invite active colony players\n* `Only owner may kick players`', inline=False),
            discord.Embed(title='Learn: Lobby functions - Page 5')
            .add_field(name="Join lobby", value="```To join a lobby, enter the lobby code after using the ,lobby or /lobby commands, or use the join button on a lobby.```\n* If lobby is locked, only invited players may join"),
            discord.Embed(title='Learn: Lobby functions - Page 6')
            .add_field(name='Leave lobby', value='```Use the leave button to leave a lobby. Or use the ,leave or /leave commands```\n* Can leave during active battles but may be hit if defense check is failed', inline=False),
            discord.Embed(title='Learn: Lobby functions - Page 7')
            .add_field(name='Ready up', value='```All players must be ready before a match can begin, using the ready up lobby button or the /ready and ,ready commands```', inline=False)
        ]
         async def get_page(page: int):
            emb = pages[page - 1]
            emb.set_author(name=self.botname, icon_url=self.avatar, url=self.avatar)
            emb.set_thumbnail(url=self.avatar)
            return emb, len(pages)
      

         pagination = Pagination(ctx.interaction, get_page)
         await pagination.navegate()


        

        

        

    @learn.command(name='battle', description='Learn how to battle')
    async def battle(self, ctx):

        pages = [
            discord.Embed(title='Learn: Battle - Page 1', description='### Table of contents:\n* Learn PVP and PVE: Page 1\n* Learn Leaving a battle: Page 2\n* Learn Technique activation: Page 3\n* Learn Melee attacks: Page 3\n* Learn Cursed Tool usage: Page 4\n* Learn Summons and Rituals: Page 5\n* Learn Domains: Page 6\n* Learn Maximum Techniques: Page 7\n### `Before you can start a battle, you must have a lobby with every player ready. Once everyone in the lobby is ready, and the game mode is selected, use the start button or (/start | ,start) command`')
            .add_field(name='PvP', value='```PVP is the player vs player mode. Here you will face off against real players in turn based rounds.```\n* Enabled using the (,pvp | /pvp) commands or using the button.\n* Greater rewards than battling NPCs in PVE (usually)', inline=False)
            .add_field(name='PvE', value="```PVE is the player vs enviornment mode. Here you will face off against NPC culling game players.```\n* Enabled using the (,pve | /pvp) commands or button\n* Rewards grow as you fight higher level enemies.\n* Stronger enemies have respawn timers", inline=False),
            discord.Embed(title='Learn: Battle - Page 2')
            .add_field(name="Leave", value="```You can leave a lobby in queue mode at any time. But must pass defense checks to leave an active battle unharmed.```\n* Help from a support type character may aid your escape from an active battle\n* If available, you may surrender game points in exchange for escape.\n* Having a technique that increases your speed active may help your escape\n* The chances of escape vary depending on physical speed and active technique")
            .add_field(name="Tech Activation", value="```To activate your technique, you must be in an active battle. You can use the (,technique | /technique) commands or the battle buttons to activate a technique. You will get a private pop up prompting you to pick a technique. You may use a (,bindvow | /bindvow) command or the button to see the options of increasing the effectiveness of your technique.```\n* Each tecehnique will have statistics displayed\n* May reinforce strength, speed, or technique with CE at this stage.\n* Each technique will have a CE chargec.\n* May choose to take a defensive stance or heal at this stage.\n* Using a binding vow will prompt you the available vows for your technique"),
            discord.Embed(title='Learn: Battle - Page 3')
            .add_field(name="Melee Attacks", value="```Use physical attacks to land combos on your enemies. Activate using the (,melee | /melee) command or the melee button. You will get a private prompt of combos you can use.```\n* If you have a cursed tool equipped, using a melee attack will show you extra prompts for the cursed tool combos.\n* May infuse CE into melee attacks.")
            .add_field(name="Cursed Tools", value="```Must be equipped prior to battle activation. Use the (,equip | /equip) commands from lobby or the equip lobby button to equip from your inventory. You may also equip and unequip (,unequip | /unequip) items outside of a lobby.```\n* During battles, you may activate your cursed tool with a (,melee | /melee) attack.\n* Cursed tools may add aditional moves to a players melee options.\n* Cursed tools can be acquired at the (,shop | /shop)."),
            discord.Embed(title='Learn: Battle - Page 4')
            .add_field(name="Summons and Rituals", value="```Some techniques allow you to (,summon | /summon) Shikigami or Spirits. This will create an additional turn for you, allowing you to attack or support using the summon's abilities. Some cursed spirit players will have the option to be tamed if weak enough. Some techniques require (,ritual | /ritual)'s to tame Shikigami for summoning.```\n*  Ritual starts a private 1 on 1 match with a Shikigami.\n* If a Ritual is used in battle it will include everyone in the battle as the Shikigami's enemy.\n* Ritual Shikgami target the caster of the ritual first.\n* Summoning Shikigami or Spirits requires technique activation without a talisman or a tamed spirit in your inventory."),
            discord.Embed(title='Learn: Battle - Page 5')
            .add_field(name="Domains", value="```To open your Domain, you must select the players you want to contain in it as the targets. For conditions you can choose any of the three barrier types available to you: Internal, External, as well as selecting the sure hit available to you: Lethal, Non Lethal. The duration of the Domain will depend on your tech level. You may choose to create a binding vow to shorten the duration of your domain, in exchange for other benefits.```\n* If a player has any anti-domain abilities, they will be prompted with a domain defense check.\n* If a player has a domain, they can enter a Domain Clash.\n* In a Domain Clash, a number of variables will be calculated to determine the outcome.\n* Domain clashes have 3 outcomes: Win, Draw, or Lose.\n* Non lethal domains have a higher chance of winning domain clashes."),
            discord.Embed(title='Learn: Battle - Page 6')
            .add_field(name="Maximum Techniques", value="````These techniques are locked at higher tech levels than the base techniques. To unlock them, you will have to upgrade your threat grade. There are 5 tech levels, and 5 threat grade levels. Each threat grade level increases your tech level. ``` Maximum techniques require more CE than their lapse counterpart.\n* Reverse techniques do not have maximum variants.\n* Maximum techniques can be customized with binding vows")
        ]
        
        async def get_page(page: int):
            emb = pages[page - 1]
            emb.set_author(name=self.botname, icon_url=self.avatar, url=self.avatar)
            emb.set_thumbnail(url=self.avatar)
            return emb, len(pages)
        
        pagination = Pagination(ctx.interaction, get_page)
        await pagination.navegate()

    

 

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