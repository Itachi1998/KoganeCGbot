import discord, asyncio, os, traceback, game, requests, textwrap, PIL, aiohttp, io, Postgresql, time
import math
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont, ImageSequence
import techniques
from game import Character, GameMode
from cogs import colonies
from techniques import enemy_techniques, BVs, cursed_tools, rules
from technique_list import bloodmanip, boogiewoogie,cursedspiritmanip, heavenlyrestriction, idletranfig, limitless, mythicbeastamber, projectionsorcery, shrine, strawdoll, tenshadows, birdmanip, comedian, construction, copy, cursed_speech
from io import BytesIO
from Postgresql import save_player


techs = [bloodmanip.Blood_Manipulation(), boogiewoogie.Boogie_Woogie(), cursedspiritmanip.Cursed_Spirit_Manip(), idletranfig.Idle_Transfiguration(), limitless.Limitless(), heavenlyrestriction.HeavenlyRestriction(), mythicbeastamber.Mythic_Beast_Amber(), projectionsorcery.Projection_Sorcery(), shrine.Shrine(), strawdoll.Straw_Doll(), tenshadows.Ten_Shadows(), birdmanip.Bird_Manipulation(), comedian.Comedian(), construction.Construction(), copy.Copy(), cursed_speech.Cursed_Speech()]

token = os.environ['TOKEN']
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix=',', intents=intents)
bot.remove_command('help')

#the status embed background
status_bg = {'gray' : 'images/graystats.png', 'blue' : 'images/bluestats.png', 'green' : 'images/greenstats.png', 'black' : 'images/blackstats.png', 'pink' : 'images/pinkstats.png'}
#the bots banner
cg_banner = 'images/cg_banner.png'

# Helper functions
def load_character(user_id, guild_id):
    print(f"user {user_id} guild {guild_id}")
    map_dict = Postgresql.read_player(user_id, guild_id)
    if map_dict is None:
        return None
    return game.Character(**map_dict)
    
#setting the function as an attribute of bot
bot.load_character = load_character
    
#setup hook requires for cog usage
async def setup_hook():
    
    for filename in os.listdir('cogs'):
        if filename.endswith('.py'):
            cog = filename[:-3]
            try:
                await bot.load_extension(f'cogs.{cog}')
                print(f'Cog loaded: {cog}')
            except Exception as e:
                print(f'Failed to load cog {cog}: {e}')



#returns the profile image
def status_embed(user, character, banner=None):
    try:
        img = Image.new("RGBA", (700, 900), (0, 0, 0, 0))  # Base image with transparency
        banner_frames = None
        banner_dur = 0
        print(banner)
        if banner:
            banner = Image.open(BytesIO(requests.get(banner).content))
            if 'duration' in banner.info.keys():
                banner_frames = [frame.copy().convert('RGBA') for frame in ImageSequence.Iterator(banner)]
                
        else:
            banner = Image.open(cg_banner)
            
        ui = None
        
        colony = Postgresql.read_colony(character.colony)
        
        if colony:
            colony_color = colony['colony_color']
            
            if colony_color in status_bg:
                ui = Image.open(status_bg[colony_color]).convert('RGBA')
        else:
            ui = Image.open(status_bg['gray']).convert('RGBA')
            
        ui = ui.resize((img.width, img.height))
        img.paste(ui)
        resp = requests.get(user.display_avatar)
       
        avatar = Image.open(BytesIO(resp.content))
        av_frames = None
        av_dur = 0
        
        if 'duration' in avatar.info.keys():
            av_frames = [frame.copy().convert('RGBA') for frame in ImageSequence.Iterator(avatar)]
            masked_frames = []
            for frame in av_frames:
                frame.thumbnail((226, 226))  # Ensure same size
                mask = Image.new('L', frame.size, 0)
                av_dur = frame.info['duration']
                mdraw = ImageDraw.Draw(mask)
                mdraw.ellipse((0, 0, frame.size[0], frame.size[1]), fill=255)
                frame.putalpha(mask)
                masked_frames.append(frame)
            avatar = masked_frames[0]
            av_frames = masked_frames
        
        else:
            avatar = avatar.resize((226, 226))
            mask = Image.new('L', avatar.size, 0)
            mdraw = ImageDraw.Draw(mask)
            mdraw.ellipse((0, 0, avatar.size[0], avatar.size[1]), fill=255)
            avatar.putalpha(mask)
            
        print(avatar)
 
        if colony and colony_color == 'black' and not av_frames:
            avatar.resize((220, 220))
            img.paste(avatar, (50, 165), avatar)
        

        namefont = ImageFont.truetype("Digital_tech.otf", size=40)
        font = ImageFont.truetype("Digital_tech.otf", size=25)
    
        # Drawing text (example code remains the same for this part)
        textwrapper = textwrap.TextWrapper(
            width=15, placeholder="...", break_long_words=True)
        text = f"{character.name}"
        text_list = textwrapper.wrap(text)
        charname = "\n".join(text_list)
    
        draw = ImageDraw.Draw(img)
        draw.text((285, 270), charname, font=namefont,
                  stroke_fill=1, stroke_width=2, fill=(255, 255, 255))
    
        technique_name = character.technique
        colony = Postgresql.read_colony(character.colony)
        draw.text((65, 450), f"TECHNIQUE", font=namefont,
                  stroke_fill=1, stroke_width=2, fill=(255, 255, 255))
        draw.text((65, 510), f"{technique_name}", font=font,
                  fill=(255, 255, 255), stroke_width=2, stroke_fill=1)
        draw.text((388, 450), f"COLONY", font=namefont,
                  stroke_fill=1, stroke_width=2, fill=(255, 255, 255))
        draw.text((388, 510), f"{colony['name']}", font=font,
                  fill=(255, 255, 255), stroke_width=2, stroke_fill=1)
        draw.text((65, 585), f"STATUS", font=namefont,
                  stroke_fill=1, stroke_width=2, fill=(255, 255, 255))
        draw.text((388, 585), f"CG POINTS", font=namefont,
                  stroke_fill=1, stroke_width=2, fill=(255, 255, 255))
        draw.text((388, 652), f"{character.cgp}", font=font,
                  fill=(255, 255, 255), stroke_width=2, stroke_fill=1)
        draw.text((65, 710), f"LEVEL", font=namefont,
                  stroke_fill=1, stroke_width=2, fill=(255, 255, 255))
        draw.text((65, 770), f"{character.get_grade()}\nLvl: {character.level}\nCT Lvl: {character.ct_level}",
                  font=font, fill=(255, 255, 255), stroke_width=2, stroke_fill=1)
        draw.text((388, 710), f"STATS", font=namefont,
                  stroke_fill=1, stroke_width=2, fill=(255, 255, 255))
        draw.text((388, 770), f"SKILL POINTS: {character.skp}\nSTRENGTH: {character.attack}\nSPEED: {character.speed}",font=font, fill=(255, 255, 255), stroke_width=2, stroke_fill=1)
    
        roam_text = ""
        if character.mode == GameMode.PVE:
            roam_text = "in pve"
        if character.mode == GameMode.ROAM:
            roam_text = "roaming"
        if character.mode == GameMode.PVP:
            roam_text = "in pvp"
        if character.mode == GameMode.Q:
            roam_text = "in lobby"
    
        roam_list = textwrapper.wrap(roam_text)
        roam_text = "\n".join(roam_list)
        draw.text((65, 650), f"{roam_text}", font=font, fill=(255, 255, 255), stroke_width=2, stroke_fill=1)
        print(f"Banner duration: {banner_dur}")
        print(f"Avatar duration: {av_dur}")
        print(f"Number of banner frames: {len(banner_frames) if banner_frames else 0}")
        print(f"Number of avatar frames: {len(av_frames) if av_frames else 0}")
        # Save the image to a BytesIO stream
        if banner_frames:
            resized_frames = []
            for frame in banner_frames:
                new_rect = Image.new("RGBA", (700, 900), (0, 0, 0, 0))
                frame_resized = frame.resize((new_rect.width, 300))
                banner_dur = frame.info['duration']
                mask = frame_resized.split()[3]  # Get the alpha channel for mask
                new_rect.paste(frame_resized, (0, 0), mask=mask)
                new_rect.paste(ui, (0,0), ui)
                img_with_banner = Image.alpha_composite(new_rect, img)
                resized_frames.append(img_with_banner)
            banner_frames = resized_frames
        else:
            banner = banner.resize((img.width, 300))
            new_rect = Image.new("RGBA", (700, 900), (0, 0, 0, 0))
            new_rect.paste(banner, (0, 0))
            img = Image.alpha_composite(new_rect, img)
            
        with BytesIO() as image_binary:
            if banner_frames or av_frames:
                dur = max(banner_dur, av_dur)
                frames = []
                for i in range(max(len(banner_frames or []), len(av_frames or []))):
                    bg = img.copy()
                    bfr = None
                    afr = None
                    
                    if banner_frames:
                        bfr = banner_frames[i % len(banner_frames)]
                    
                    if av_frames:
                        afr = av_frames[i % len(av_frames)]
                    
                    if bfr:
                        bg.paste(bfr, (0, 0), mask=bfr)
                    
                    if afr:
                        bg.paste(afr, (42, 162), mask=afr.split()[3])
                    else:
                        bg.paste(avatar, (42, 162), avatar)
                    frames.append(bg)
                frames[0].save(image_binary, format='GIF', save_all=True, append_images=frames[1:], duration=dur, loop=0)
                image_binary.seek(0)  # Ensure the stream is at start
                discord_file = discord.File(fp=image_binary, filename="status.gif")
                return discord_file
    
            else:
                img.paste(avatar, (42, 162), avatar)
                
                
                img.save(image_binary, 'PNG')
            image_binary.seek(0)  # Go to the beginning of the BytesIO stream
            return discord.File(fp=image_binary, filename="status.png")

    
    except Exception as e:
        print(f"Error in status_embed: {e}")
        traceback.print_exc()


bot.status_embed = status_embed
    



def make_embed(title, description, footer=None, thumbnail=None, color=None):
    embed = discord.Embed(title=title, description=description, color=discord.Color.yellow())
    if footer is not None:
        embed.set_footer(text=footer)
    if thumbnail is not None:
        embed.set_thumbnail(url=thumbnail)
    return embed


def new_field(embed, name, value, inline):
    if embed is None:
        print("invalid embed")
        return
    else:
        embed.add_field(name=name, value=value, inline=inline)
        return embed





@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    
   


@bot.hybrid_command(name='skillpoints', with_app_command=True, description='Level up your skills!')
async def skpl(ctx):
    character = bot.load_character(ctx.author.id, ctx.guild.id)
    if character:
        embed = make_embed(title='Skill Point Menu', description='```Choose a stat to level up```', color=discord.Color.yellow())
        new_field(embed, name='**Current Stats**', value=f'\n**CT Level**: `{character.ct_level}`\n**STRENGTH**: `{character.attack}`\n**SPEED**: `{character.speed}`\n**CE**: `{character.ce}`\n**HP**: `{character.max_hp}`', inline=True)
        new_field(embed, name='**Skill Points**', value=f'`{character.skp}`', inline=True)
        msg = await ctx.send(embed=embed)
        await msg.edit(view=LevelMenu(character, msg))
        return
        
    
    
class LevelMenu(discord.ui.View):
    def __init__(self, character, msg):
        super().__init__(timeout=None)
        self.add_item(LevelSelect(character, msg))

        


class LevelSelect(discord.ui.Select):
    def __init__(self, character, msg):
        options = [discord.SelectOption(label='Strength', value='strength'), discord.SelectOption(label='Speed', value='speed'), discord.SelectOption(label='CE', value='ce'), discord.SelectOption(label='HP',value='hp')]
        super().__init__(placeholder='Choose a stat to level up', options=options)
        self.character = character
        self.msg = msg

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.character.user_id:
            await interaction.response.send_message('This is not your character!', ephemeral=True)
            return
        character = self.character
        stat = self.values[0]
        skillpointmodal = SkillPointModal()
        skillpointmodal.stat = stat
        skillpointmodal.player = self.character
        skillpointmodal.skp = self.character.skp
        skillpointmodal.msg = self.msg
        await interaction.response.send_modal(skillpointmodal)
        
        



class SkillPointModal(discord.ui.Modal, title="Skill Points"):
    amount = discord.ui.TextInput(
        label="Amount of skill points",
        style=discord.TextStyle.short,
        max_length=5)


    async def on_submit(self, interaction: discord.Interaction):
        amount = int(self.amount.value)
        stat = self.stat
        if amount <= self.skp:
            sk_msg = None
            if stat == 'strength':
                self.player.attack += amount
                sk_msg = f'Your strength has been increased by {amount}!'

            elif stat == 'speed':
                self.player.speed += amount
                sk_msg = f'Your speed has been increased by {amount}!'

            elif stat == 'ce':
                if self.player.technique != 'Heavenly Restriction':
                    self.player.max_ce += amount
                    self.player.ce = self.player.max_ce
                    sk_msg = f'Your CE effeciency has been increased by {amount}!'
                else:
                    sk_msg = f"Cannot inrease CE effeciency because of Heavenly Restriction"
                    self.player.skp += amount
                    self.player.save_to_db()
            elif stat == 'hp':
                self.player.max_hp += amount
                self.player.hp = self.player.max_hp
                sk_msg = f'Your HP has been increased by {amount}!'
            
            self.player.skp -= amount
            player = self.player
            embed = make_embed(title='Skill Point Menu', description=f"`{sk_msg}`\n**Choose a stat to level up**", color=discord.Color.yellow())
            new_field(embed, name='**Current Stats**', value=f'\n**CT Level**: `{player.ct_level}`\n**STRENGTH**: `{player.attack}` \n**SPEED**: `{player.speed}` \n**CE**: `{player.ce}/{player.max_ce}`\n**HP**: `{player.max_hp}`\n**Skill Points**: `{player.skp}`', inline=True)
            
            self.player.save_to_db()
            await self.msg.edit(embed=embed, view=LevelMenu(self.player, self.msg))
            return
        else:
            await interaction.response.send_message('Not Enough Skill Points!', ephemeral=True)
            return
            
    async def error(self, interaction: discord.Interaction, error):
        print(error)
        return



@bot.hybrid_command(name='help', description='Shows all commands')
async def help(ctx, command: str = None):

    embed = make_embed('**COMMANDS**', "**Help**\n Show all commands" , "- OWNER @HXSTILE - CODE HELP @CODES46 - ART HELP @TI6ERIUS & @NESCRUZ76 -", thumbnail=bot.user.avatar.url)
    if command:
        command_obj = bot.get_command(command)
        if command_obj:
            new_field(embed, command, command_obj.description, True)
            await ctx.send(embed=embed)
            return
        else:
            embed.add_field(name="Invalid command", value="Command not found")
            await ctx.send(embed=embed)
            return
    else:
        new_field(embed, 'create', 'Creates a new player', True)
        new_field(embed, 'delete', 'Deletes your player', True)
        new_field(embed, 'profile', 'Shows your players profile', True)
        new_field(embed, 'equip', 'Equip an item from your inventory', True)
        new_field(embed, 'unequip', 'Store an item in your inventory', True)
        new_field(embed, 'inventory', 'Shows your inventory', True)
        new_field(embed, 'shop', 'Opens the shop', True)
        new_field(embed, 'lobby', 'Start a lobby', True)
        new_field(embed, 'vow', 'Use a binding vow(`not ready yet`)', True)
        new_field(embed, 'skp', 'Use your skill points', True)
        new_field(embed, 'rule', 'Use a Kogane rule (`not ready yet`)', True)
        new_field(embed, 'ui', 'Edit your colony UI (`must be owner of the server`)', True)
        await ctx.send(embed=embed)



@bot.hybrid_command(name='create', description='Creates a new player')
async def create(ctx, name: str=None):
    try:
        
        if name is None:
            name = ctx.author.name
            
        t = None

        author = ctx.author.id


        match author:
        
            case int(elo):
                #loop through techniques subclasses
                for tech in techniques.Techniques.__subclasses__():
                    if tech().name == "Shrine":
                        t = tech()
                        break
        
            case int(nate):
                for tech in techniques.Techniques.__subclasses__():
                    if tech().name == "Limitless":
                        t = tech()
                        break

        
            case int(loud):
                #loop through techniques subclasses
                for tech in techniques.Techniques.__subclasses__():
                    if tech().name == "Shrine":
                        t = tech()
                    break

        
        
            case int(dxrr):
            #loop through techniques subclasses
                for tech in techniques.Techniques.__subclasses__():
                    if tech().name == "Blood Manipulation":
                        t = tech()
                        break
        
            case int(tiberius):
                #loop through techniques subclasses
                for tech in techniques.Techniques.__subclasses__():
                    if tech().name == "Ten Shadows":
                        t = tech()
                        break

            case int(mikael):
                #loop through techniques subclasses
                    for tech in techniques.Techniques.__subclasses__():
                        if tech().name == "Blood Manipulation":
                            t = tech()
                            break

        
            case int(cats):
                #loop through techniques subclasses
                for tech in techniques.Techniques.__subclasses__():
                    if tech().name == "Comedian":
                        t = tech()
                        break
            case int(gam):
                    for tech in techniques.Techniques.__subclasses__():
                        if tech().name == "Limitless":
                            t = tech()
                            break
            case int(chyna):
                for tech in techniques.Techniques.__subclasses__():
                    if tech().name == "Limitless":
                        t = tech()
                        break           
            
            case int(chris):
                #loop through techniques subclasses
                for tech in techniques.Techniques.__subclasses__():
                    if tech().name == "Ten Shadows":
                        t = tech()
                        break
    
            
            case int(greg):
                for tech in techniques.Techniques.__subclasses__():
                    if tech().name == 'Shrine':
                        t = tech()
                        break
            
            case int(legend):
                #loop through techniques subclasses
                for tech in techniques.Techniques.__subclasses__():
                    if tech().name == "Heavenly Restriction":
                        t = tech()
                        break
            
    
            case int(myers):
                #loop through techniques subclasses
                for tech in techniques.Techniques.__subclasses__():
                    if tech().name == "Limitless":
                        t = tech()
                        break
                        
            case int(codes_id):
                #loop through techniques subclasses
                for tech in techniques.Techniques.__subclasses__():
                    if tech().name == "Bird Manipulation":
                        t = tech()
                        break
                        
            case int(snot):
                #loop through techniques subclasses
                for tech in techniques.Techniques.__subclasses__():
                    if tech().name == "Cursed Spirit Manip":
                        t = tech()
                        break
                        
            case int(owner_id):
                #loop through techniques subclasses
                for tech in techniques.Techniques.__subclasses__():
                    if tech().name == "Star Rage":
                        t = tech()
                        break
                        
            case _:  # Use underscore for the default case instead of 'default'
                t = techniques.set_technique(techs)
                t = t

        if not t:
            await ctx.send("Failed to set technique. Please try again.")
            return
        
        hr = False
        strength = 20
        speed = 20
        max_hp = 100
        ce = 30
        ct_lvl = 1
        rct = False
        defense = 'CE'
        cgp = 200
        lvl =1
        
       
            
        if ctx.author.id == loud_id:
            ct_lvl += 4
            ce += 50
            lvl = 100
            
        if t.name == "Heavenly Restriction":
            hr=True
            strength += 80
            speed += 80
            max_hp += 100
            ce = 0
            defense = 'Heavenly Body'

        if t.name == 'Star Rage':
            strength += 60
            speed += 60
            ce += 20
            rct = True

        if t.name == 'Ten Shadows':
            ce += 30
            strength += 20
            speed += 20
            
        if t.name == 'Construction':
            ce += 10
    
        if t.name == 'Mythic Beast Amber':
            ce += 20
            strength += 30
            speed += 30
        
        if t.name == 'Projection Sorcery':
            ce += 20
            strength += 10
            speed += 50
            
        if t.name == 'Blood Manipulation':
            ce += 20
            strength += 30
            speed += 30
            max_hp += 20
            
        if t.name == 'Limitless':
            ce += 90
            strength += 50
            speed += 50
            max_hp += 50
            rct = True
            
        if t.name == 'Copy':
            ce += 120
            strength += 30
            speed += 30
            max_hp += 50
            rct = True
            
        if t.name == 'Shrine' :
            ce += 240
            strength += 50
            speed += 50
            max_hp += 50
            rct = True

        await ctx.send("Creating your character...")
        
        colony = ctx.guild.id
        player_exists = Postgresql.read_player(ctx.author.id, ctx.guild.id)
        
        if player_exists:
            
                colony_data = Postgresql.read_colony(ctx.guild.id)
            
                if colony_data == None:
                    colony = colonies.Colony(id = ctx.guild.id, name = ctx.guild.name, owner = ctx.author.id, members = [], ai=[game.Enemy.__subclasses__()], xp = 0, colony_color = 'gray') 
                    
                if player_exists['user_id'] in colony_data['members']:
                    await ctx.send("You already have a character in this colony")
                    return
    
            
                else:
                    char = Character(
                        name=name,
                        hp=max_hp,
                        max_hp=max_hp,
                        attack=strength,
                        defense=defense,
                        speed=speed,
                        xp=0,
                        cgp=cgp,
                        technique=t.name,
                        imbued=0,
                        ce=ce,
                        max_ce = ce,
                        level=lvl,
                        ct_level = ct_lvl,
                        inventory=[],
                        equipment=[],
                        user_id=ctx.author.id,
                        skp=10,
                        enemy=None,
                        HR=hr,
                        RCT=rct,
                        mode=GameMode.ROAM,
                        colony=colony, victory_msg="Stand proud, you were strong", rules = [], vows = [], spirits = [], shiki = [], tools = [], luck = 0, souls = [])
                    char.save_to_db()  # Save to database
                    await ctx.send(f"Character created: {name}")
                    profile = await bot.fetch_user(ctx.author.id)
                    banner = profile.banner.url if profile.banner else None
                    member = ctx.guild.get_member(ctx.author.id)
                    embed = status_embed(member, char, banner)
                    msg = await ctx.send(file=embed)
                    view = ProfileView(msg, char)
                    await msg.edit(view=view)
                    
        else:
            member = ctx.guild.get_member(ctx.author.id)
            char = Character(
                name=name,
                hp=max_hp,
                max_hp=max_hp,
                attack=strength,
                defense=defense,
                speed=speed,
                xp=0,
                cgp=0,
                technique=t.name,
                imbued=0,
                ce=ce,
                max_ce = ce,
                level=1,
                ct_level = ct_lvl,
                inventory=[],
                equipment=[],
                user_id=ctx.author.id,
                skp=10,
                enemy=None,
                HR=hr,
                RCT=rct,
                mode=GameMode.ROAM,
                colony=colony, victory_msg='Stand proud, you were strong', shiki = [], spirits = [], vows = [], rules = [], tools = [], souls = [], luck=0)
            char.save_to_db()  # Save to database
            await ctx.send(f"Character created: {name}")
            profile = await bot.fetch_user(ctx.author.id)
            banner = profile.banner.url if profile.banner else None
            embed = status_embed(member, char, banner)
            await ctx.send(file=embed)
    except Exception as e:
        print(f"Error in create command: {e}")
        traceback.print_exc()



@help.error
async def help_error(ctx, error) -> None:
    ctx.send(traceback.print_exc())


@bot.hybrid_command(name='sync', description='sync commands')
async def sync(ctx):
    if ctx.author.id == owner_id or ctx.author.id == loud_id:
        await ctx.send('syncing commands')
        try:
            synced = await bot.tree.sync()
            await ctx.send(f'Synced {len(synced)} commands')
            return
        except Exception as e:
            await ctx.send(e)
    else:
        await ctx.send('You are not the owner of this bot')


bot.setup_hook = setup_hook
bot.run(token)
