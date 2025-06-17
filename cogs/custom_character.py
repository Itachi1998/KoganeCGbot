import PIL.Image
import discord
import io
from discord.ext import commands
from db import read_player
import PIL 
import random
female_hair = {
    'Hair 1' :
      {'hair' : {
          'default' :'images/Characters/Humans/Female/Hair/hair1/hair1_default.png',
       'pink hair' : 'images/Characters/Humans/Female/Hair/hair1/hair1_pink.png',
       'black hair' : 'images/Characters/Humans/Female/Hair/hair1/hair1_black.png',
       'brunette hair' : 'images/Characters/Humans/Female/Hair/hair1/hair1_brunette.png'},
       'beanies' : {
       'default beanie' : 'images/Characters/Humans/Female/Hair/hair1/beanie_colors/black_beanie.png',

       'gray_beanie' : 'images/Characters/Humans/Female/Hair/hair1/beanie_colors/gray_beanie.png',
       'white beanie' : 'images/Characters/Humans/Female/Hair/hair1/beanie_colors/white_beanie.png',
       'orange beanie' : 'images/Characters/Humans/Female/Hair/hair1/beanie_colors/orange_beanie.png',
       'sky blue beanie' : 'images/Characters/Humans/Female/Hair/hair1/beanie_colors/sky_blue_beanie.png',
       'red beanie' : 'images/Characters/Humans/Female/Hair/hair1/beanie_colors/red_beanie.png',
        'green beanie' : 'images/Characters/Humans/Female/Hair/hair1/beanie_colors/green_beanie.png'
       }}, 
       'Hair 2' : 
       {'Front Hair' : {
              'default' :'images/Characters/Humans/Female/Hair/hair2/hair2_brunette_front.png',
              'blonde' : 'images/Characters/Humans/Female/Hair/hair2/hair2_blonde_front.png',
              'green' : 'images/Characters/Humans/Female/Hair/hair2/green_hair_front.png',
              'black' : 'images/Characters/Humans/Female/Hair/hair2/hair2_black_front.png',
              'sky blue' : 'images/Characters/Humans/Female/Hair/hair2/hair2_sky_blue_front.png',
              'white' : 'images/Characters/Humans/Female/Hair/hair2/hair2_white_front.png',
       },
       'Back Hair' : {
                'default' :'images/Characters/Humans/Female/Hair/hair2/hair2_brunette_back.png',
                'green' : 'images/Characters/Humans/Female/Hair/hair2/green_hair2_back.png',
                'black' : 'images/Characters/Humans/Female/Hair/hair2/hari2_black_back.png',
                'white' : 'images/Characters/Humans/Female/Hair/hair2/hair2_white_back.png',
                'sky blue' : 'images/Characters/Humans/Female/Hair/hair2/hair2_sky_blue_back.png',
                'blonde' : 'images/Characters/Humans/Female/Hair/hair2/hair2_blonde_back.png',


       }},
       'Hair 3' :
       {'Hair' : {
                'default' :'images/Characters/Humans/Female/Hair/hair3/hair3_default.png',
                'green' : 'images/Characters/Humans/Female/Hair/hair3/hair3_green.png',
                'black' : 'images/Characters/Humans/Female/Hair/hair3/hair3_black.png',
                'white' : 'images/Characters/Humans/Female/Hair/hair3/hair3_white.png',
       }},
       'Hair 4' : 
       {
                'default' :'images/Characters/Humans/Female/Hair/hair4/hair4_default.png',
                'brunette' : 'images/Characters/Humans/Female/Hair/hair4/hair4_brunette.png',
                'blonde' : 'images/Characters/Humans/Female/Hair/hair4/hair4_blonde.png',
                'green' : 'images/Characters/Humans/Female/Hair/hair4/hair4_green.png',
                'white' : 'images/Characters/Humans/Female/Hair/hair4/hair4_white.png',
                'pink' : 'images/Characters/Humans/Female/Hair/hair4/hair4_pink.png'
       },
       'Hair 5' :
       {
               'default' :'images/Characters/Humans/Female/Hair/hair5/default_short_hair.png',
               'blonde' : 'images/Characters/Humans/Female/Hair/hair5/blonde.png',
               'white' : 'images/Characters/Humans/Female/Hair/hair5/white.png',
               'black' : 'images/Characters/Humans/Female/Hair/hair5/black.png',         
       },
       'Hair 6' :{
           'Front' : 
            {
               'default' :'images/Characters/Humans/Female/Hair/hair6/maki_hair_front_default.png',
               'black'  : 'images/Characters/Humans/Female/Hair/hair6/hair6_front.png',
               'white' : 'images/Characters/Humans/Female/Hair/hair6/hair6_white.png',
            

            },
            'Back' : 
            {
                'default' :'images/Characters/Humans/Female/Hair/hair6/mak_hair_back_default.png',
                'black' : 'images/Characters/Humans/Female/Hair/hair6/hair6_black_back.png',
                'white' : 'images/Characters/Humans/Female/Hair/hair6/hair6_black.png',

            }
            },
            'Eyebrows' : 
            {
                'default' : 'images/Characters/Humans/Female/Hair/brunette_eye_brows.png',
                'blonde' : 'images/Characters/Humans/Female/Hair/blonde_eye_brows.png',
                'green' : 'images/Characters/Humans/Female/Hair/green_eye_brows.png',
                'white' : 'images/Characters/Humans/Female/Hair/white_eye_brows.png',
            }}
female_lips = {
        'default' : 'images/Characters/Humans/Female/Lips/default_lip.png',
        'black' : 'images/Characters/Humans/Female/Lips/black_lips.png',
        'purple' : 'images/Characters/Humans/Female/Lips/purple_lips.png',
        'red' : 'images/Characters/Humans/Female/Lips/red_lips.png',
        'white' : 'images/Characters/Humans/Female/Lips/white_lips.png',
        'saturated' : 'images/Characters/Humans/Female/Lips/saturated_lip.png',

}
female_eyes = {
        'blue' : 'images/Characters/Humans/Female/Eyes/blue_eyes.png',
        'brown' : 'images/Characters/Humans/Female/Eyes/brown_eyes.png',
        'green' : 'images/Characters/Humans/Female/Eyes/green_eyes.png',
        'hazel' : 'images/Characters/Humans/Female/Eyes/hazel_eyes.png',
        'six' : 'images/Characters/Humans/Female/Eyes/six_eyes.png',
        'red' : 'images/Characters/Humans/Female/Eyes/red_eyes.png',
}

female_school_fits = {
    'default' : 'images/Characters/Humans/Female/Clothes/school_fit/default_school_fit.png',
    'black' : 'images/Characters/Humans/Female/Clothes/school_fit/black_school_fit.png',
    'gray' : 'images/Characters/Humans/Female/Clothes/school_fit/gray_school_fit.png',
    'red' : 'images/Characters/Humans/Female/Clothes/school_fit/red_school_fit.png',
    'white' : 'images/Characters/Humans/Female/Clothes/school_fit/white_school_fit.png'
}

female_fighter_fits = {
    'blue' : 'images/Characters/Humans/Female/Clothes/fighter_fit/blue_fighter.png',
    'default' : 'images/Characters/Humans/Female/Clothes/fighter_fit/default_fighter.png',
    'pink' : 'images/Characters/Humans/Female/Clothes/fighter_fit/pink_fghter.png',
    'white' : 'images/Characters/Humans/Female/Clothes/fighter_fit/white_fighter.png',
    'teal' : 'images/Characters/Humans/Female/Clothes/fighter_fit/teal_fighter.png',
}
female_casual_fits = {
    'front' : {
    'default' : 'images/Characters/Humans/Female/Clothes/Casual/default_casual.png',
    'blue' : 'images/Characters/Humans/Female/Clothes/Casual/blue_casual.png',
    'white' : 'images/Characters/Humans/Female/Clothes/Casual/white_hoodie.png',
    'red' : 'images/Characters/Humans/Female/Clothes/Casual/red_casual.png',
},
'back' : 
{
    'default' : 'images/Characters/Humans/Female/Clothes/Casual/default_casual_back.png',
    'white' : 'images/Characters/Humans/Female/Clothes/Casual/white_casual_back.png',
}}

female_suits = {
    'default' : 'images/Characters/Humans/Female/Clothes/Suit/suit_default.png',
    'gray' : 'images/Characters/Humans/Female/Clothes/Suit/official_gray_suit.png',
    'brown' : 'images/Characters/Humans/Female/Clothes/Suit/official_brown_suit.png',
    'pink'  : 'images/Characters/Humans/Female/Clothes/Suit/pink_suit.png',
}

female_body_skins = {
'default' : 'images/Characters/Humans/Female/body_light_skin.png',
'dark' : 'images/Characters/Humans/Female/body_dark_skin.png',
'medium light' : 'images/Characters/Humans/Female/medium_light_skin.png',
'medium skin' : 'images/Characters/Humans/Female/medium_skin.png',
}


male_hair = {
    '1' :
    {
        'default' : 'images/Characters/Humans/Male/Hair/hair1/hair1_default.png',
        'black' : 'images/Characters/Humans/Male/Hair/hair1/hair1_black.png',
        'brown' : 'images/Characters/Humans/Male/Hair/hair1/hair1_brown.png',
        'white' : 'images/Characters/Humans/Male/Hair/hair1/hiar1_white.png',
},
'2' : {
    'black' : 'images/Characters/Humans/Male/Hair/hair2/hair2_black.png',
    'brown' : 'images/Characters/Humans/Male/Hair/hair2/hair2_brown.png',
    'default' : 'images/Characters/Humans/Male/Hair/hair2/hair2_default.png',
    'white' : 'images/Characters/Humans/Male/Hair/hair2/hair2_white.png',
},
'3' : {
    'default' : 'images/Characters/Humans/Male/Hair/hair3/hair3_default.png',
    'black' : 'images/Characters/Humans/Male/Hair/hair3/hair3_black.png',
    'brown' : 'images/Characters/Humans/Male/Hair/hair3/hair3_brown.png',
    'white' : 'images/Characters/Humans/Male/Hair/hair3/hair3_white.png',
},
'4' : {
'default' : 'images/Characters/Humans/Male/Hair/hair4/hair4_default.png',
'black' : 'images/Characters/Humans/Male/Hair/hair4/hair4_black.png',
'brown' : 'images/Characters/Humans/Male/Hair/hair4/hair4_brown.png',
'white' : 'images/Characters/Humans/Male/Hair/hair4/hair4_white.png',
},
'5' : {
    'default' : 'images/Characters/Humans/Male/hair/hair5/hair5_default.png',
    'black' : 'images/Characters/Humans/Male/Hair/hair5/hair5_black.png',
    'brown' : 'images/Characters/Humans/Male/Hair/hair5/hair5_brown.png',
    'white' : 'images/Characters/Humans/Male/Hair/hair5/hair5_white.png',
},
'6' : {
    'default' : 'images/Characters/Humans/Male/Hair/hair6/hair6_default.png',
    'black' : 'images/Characters/Humans/Male/Hair/hair6/hair6_black.png',
    'brown' : 'images/Characters/Humans/Male/Hair/hair6/hair6_brown.png',
    'white' : 'images/Characters/Humans/Male/Hair/hair6/hair6_white.png'

}}
male_skins = {
'default' : 'images/Characters/Humans/Male/medium_light_skin.png',
'light skin' : 'images/Characters/Humans/Male/light_skin.png',
'dark skin' : 'images/Characters/Humans/Male/dark_skin.png'}

male_casual_fits = {
    "Front" : {
    'default' : 'images/Characters/Humans/Male/clothes/casual/default_casual.png',
},
'Back' : {
    'default' : 'images/Characters/Humans/Male/clothes/casual/default_back_casual.png',
}
}
male_fighter_fits = {
    'black' : 'images/Characters/Humans/Male/Clothes/fighter/black_fighter.png',
    'blue' : 'images/Characters/Humans/Male/Clothes/fighter/blue_fighter.png',
    'default' : 'images/Characters/Humans/Male/Clothes/fighter/default_fighter.png',
    'red' : 'images/Characters/Humans/Male/Clothes/fighter/red_fighter.png',
    'white' : 'images/Characters/Humans/Male/Clothes/fighter/white_fighter.png',

}

male_school = {
    "front" : {
    'default' : 'images/Characters/Humans/Male/Clothes/school/front_school_fit.png',
    'black' : 'images/Characters/Humans/Male/Clothes/school/black_front_school_fit.png',
    'gray' : 'images/Characters/Humans/Male/Clothes/school/gray_front_school_fit.png',
    'red' : 'images/Characters/Humans/Male/Clothes/school/red_front_school_fit.png',
    'white' : 'images/Characters/Humans/Male/Clothes/school/white_front_school_fit.png',
}, "back" : {
    'default' : 'images/Characters/Humans/Male/Clothes/school/school_back_default.png',
}
}

male_suit = {
    'default' : 'images/Characters/Humans/Male/Clothes/suit/default_suit.png',
    'gray' : 'images/Characters/Humans/Male/Clothes/suit/gray_suit.png',
    'red' : 'images/Characters/Humans/Male/Clothes/suit/red_suit.png',
    'blue' : 'images/Characters/Humans/Male/Clothes/suit/blue_suit.png',
    'white' : 'images/Characters/Humans/Male/Clothes/suit/white_suit.png',
    'teal' : 'images/Characters/Humans/Male/Clothes/suit/teal_suit.png'
}

male_eyes = {
    'blue' : 'images/Characters/Humans/Male/Eyes/blue_eyes.png',
    'brown' : 'images/Characters/Humans/Male/Eyes/brown_eyes.png',
    'hazel' : 'images/Characters/Humans/Male/Eyes/hazel_eyes.png',
    'six' : 'images/Characters/Humans/Male/Eyes/six_eyes.png'
}

male_eyebrows = {
    'default' : 'images/Characters/Humans/Male/Hair/eyebrows/blonde.png',
    'black' : 'images/Characters/Humans/Male/Hair/eyebrows/black.png',
    'brown' : 'images/Characters/Humans/Male/Hair/eyebrows/brown.png',
    'white' : 'images/Characters/Humans/Male/Hair/eyebrows/white.png',
}

curse1 = {
    'default head' : 'images/Characters/Curses/DiabloCurseParts/Heads/default_head.png',
    'default torso' : 'images/Characters/Curses/DiabloCurseParts/Torso/default_torso.png',
    'default front arm' : 'images/Characters/Curses/DiabloCurseParts/FrontArm/default_arm.png',
    'default back arm' : 'images/Characters/Curses/DiabloCurseParts/BackArm/default_arm.png'}
curse2 = {
'default head' : 'images/Characters/Curses/FishCurseParts/Heads/default_head.png',
'default torso' : 'images/Characters/Curses/FishCurseParts/Torso/default_torso.png',
'default front arm' : 'images/Characters/Curses/FishCurseParts/FrontArm/default_arm.png',
'default back arm' : 'images/Characters/Curses/FishCurseParts/BackArm/default_arm.png',
# 'cyan head' : 'images/Characters/Curses/FishCurseParts/Heads/cyan.png',
# 'cyan torso' : 'images/Characters/Curses/FishCurseParts/Torso/cyan_torso.png',
# 'cyan front arm' : 'images/Characters/Curses/FishCurseParts/FrontArm/cyan_arm.png',
# 'cyan back arm' : 'images/Characters/Curses/FishCurseParts/BackArm/cyan.png',
# 'red head' : 'images/Characters/Curses/FishCurseParts/Heads/red.png',
# 'red torso' : 'images/Characters/Curses/FishCurseParts/Torso/red.png',
# 'red front arm' : 'images/Characters/Curses/FishCurseParts/FrontArm/red.png',
# 'red back arm' : 'images/Characters/Curses/FishCurseParts/BackArm/red.png',
# 'black head' : 'images/Characters/Curses/FishCurseParts/Heads/black.png',
# 'black torso' : 'images/Characters/Curses/FishCurseParts/Torso/black.png',
# 'black front arm' : 'images/Characters/Curses/FishCurseParts/FrontArm/black.png',
# 'black back arm' : 'images/Characters/Curses/FishCurseParts/BackArm/black.png'
}

curse3 = {
'default head' : 'images/Characters/Curses/WitchCurseParts/Heads/default_head.png',
'default torso' : 'images/Characters/Curses/WitchCurseParts/Torso/default_torso.png',
'default front arm' : 'images/Characters/Curses/WitchCurseParts/FrontArm/default_arm.png',
'default back arm' : 'images/Characters/Curses/WitchCurseParts/BackArm/default_arm.png'}
curse4 = {
    'default head' : 'images/Characters/Curses/BruteCurseParts/Heads/default_head.png',
    'red head' : 'images/Characters/Curses/BruteCurseParts/Heads/red.png',
    'black head' : 'images/Characters/Curses/BruteCurseParts/Heads/black.png',
    'cyan head' : 'images/Characters/Curses/BruteCurseParts/Heads/cyan.png',

    'default torso' : 'images/Characters/Curses/BruteCurseParts/Torso/default_torso.png',
    'red torso' : 'images/Characters/Curses/BruteCurseParts/Torso/red.png',
    'black torso' : 'images/Characters/Curses/BruteCurseParts/Torso/black.png',
    'cyan torso' : 'images/Characters/Curses/BruteCurseParts/Torso/cyan_torso.png',
    'default front arm' : 'images/Characters/Curses/BruteCurseParts/FrontArm/default_arm.png',
    'red front arm' : 'images/Characters/Curses/BruteCurseParts/FrontArm/red.png',
    'black front arm' : 'images/Characters/Curses/BruteCurseParts/FrontArm/black.png',
    'cyan front arm' : 'images/Characters/Curses/BruteCurseParts/FrontArm/cyan_arm.png',

    'default back arm' : 'images/Characters/Curses/BruteCurseParts/BackArm/default_arm.png',
    'red back arm' : 'images/Characters/Curses/BruteCurseParts/BackArm/red.png',
    'black back arm' : 'images/Characters/Curses/BruteCurseParts/BackArm/black.png',
    'cyan back arm' : 'images/Characters/Curses/BruteCurseParts/BackArm/cyan.png',
    }

class CustomCharacter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.custom_character = {'hair' : None, 'eyes' : None, 'clothes' : None, 'eyebrows' : None, 'gender' : 'Female'}
    
    @commands.hybrid_command(name="randomchar", description="Create a custom character")
    async def randomchar(self, ctx):
        # Fetch player data from the database
        female = False
        male=False
        curse=False
        random_gender = random.choice(['male', 'female', 'curse'])
        if random_gender == 'female':
            female= True
        if random_gender=='male':
            male=True
        if random_gender == 'curse':
            curse=True
        hair=None
        skintone=None
        clothes = None
        eyebrows = None
        eyes = None
        lips = None
        clothes=None
        back_hair = None
        pupils = PIL.Image.open('images/Characters/Humans/Female/Eyes/pupils.png').convert("RGBA")
        whites = PIL.Image.open('images/Characters/Humans/Female/Eyes/whites.png').convert("RGBA")
        back_clothes=  None
        skintone=None
        male_whites = PIL.Image.open('images/Characters/Humans/Male/Eyes/whites.png').convert("RGBA")
        if curse:
            random_head = random.choice(['diablo', 'fish', 'witch', 'brute'])
            random_torso = random.choice(['diablo', 'fish', 'witch', 'brute'])
            random_front_arm = random.choice(['diablo', 'fish', 'witch', 'brute'])
            random_back_arm = random.choice(['diablo', 'fish', 'witch', 'brute'])
            if random_head == 'diablo':
                head = PIL.Image.open(curse1['default head']).convert("RGBA")
            if random_head == 'fish':
                head = PIL.Image.open(curse2['default head']).convert("RGBA")
            if random_head == 'witch':
                head = PIL.Image.open(curse3['default head']).convert("RGBA")
            if random_head == 'brute':
                color = random.choice(['default', 'red', 'black', 'cyan'])
                if color == 'default':
                    head = PIL.Image.open(curse4['default head']).convert("RGBA")
                elif color == 'red':
                    head = PIL.Image.open(curse4['red head']).convert("RGBA")
                elif color == 'black':
                    head = PIL.Image.open(curse4['black head']).convert("RGBA")
                elif color == 'cyan':
                    head = PIL.Image.open(curse4['cyan head']).convert("RGBA")
            if random_torso == 'diablo':
                torso = PIL.Image.open(curse1['default torso']).convert("RGBA")
            if random_torso == 'fish':
                torso = PIL.Image.open(curse2['default torso']).convert("RGBA")
            if random_torso == 'witch':
                torso = PIL.Image.open(curse3['default torso']).convert("RGBA")
            if random_torso == 'brute':
                color = random.choice(['default', 'red', 'black', 'cyan'])
                if color == 'default':
                    torso = PIL.Image.open(curse4['default torso']).convert("RGBA")
                elif color == 'red':
                    torso = PIL.Image.open(curse4['red torso']).convert("RGBA")
                elif color == 'black':
                    torso = PIL.Image.open(curse4['black torso']).convert("RGBA")
                elif color == 'cyan':
                    torso = PIL.Image.open(curse4['cyan torso']).convert("RGBA")
            if random_front_arm == 'diablo':
                front_arm = PIL.Image.open(curse1['default front arm']).convert("RGBA")
            if random_front_arm == 'fish':
                front_arm = PIL.Image.open(curse2['default front arm']).convert("RGBA")
            if random_front_arm == 'witch':
                front_arm = PIL.Image.open(curse3['default front arm']).convert("RGBA")
            if random_front_arm == 'brute':
                color = random.choice(['default', 'red', 'black', 'cyan'])
                if color == 'default':
                    front_arm = PIL.Image.open(curse4['default front arm']).convert("RGBA")
                elif color == 'red':
                    front_arm = PIL.Image.open(curse4['red front arm']).convert("RGBA")
                elif color == 'black':
                    front_arm = PIL.Image.open(curse4['black front arm']).convert("RGBA")
                elif color == 'cyan':
                    front_arm = PIL.Image.open(curse4['cyan front arm']).convert("RGBA")
            if random_back_arm == 'brute':
                color = random.choice(['default', 'red', 'black', 'cyan'])
                if color == 'default':
                    back_arm = PIL.Image.open(curse4['default back arm']).convert("RGBA")
                elif color == 'red':
                    back_arm = PIL.Image.open(curse4['red back arm']).convert("RGBA")
                elif color == 'black':
                    back_arm = PIL.Image.open(curse4['black back arm']).convert("RGBA")
                elif color == 'cyan':
                    back_arm = PIL.Image.open(curse4['cyan back arm']).convert("RGBA")
            if random_back_arm == 'diablo':
                back_arm = PIL.Image.open(curse1['default back arm']).convert("RGBA")
            if random_back_arm == 'fish':
                back_arm = PIL.Image.open(curse2['default back arm']).convert("RGBA")
            if random_back_arm == 'witch':
                back_arm = PIL.Image.open(curse3['default back arm']).convert("RGBA")
            if random_back_arm == 'brute':
                color = random.choice(['default', 'red', 'black', 'cyan'])
                if color == 'default':
                    back_arm = PIL.Image.open(curse4['default back arm']).convert("RGBA")
                elif color == 'red':
                    back_arm = PIL.Image.open(curse4['red back arm']).convert("RGBA")
                elif color == 'black':
                    back_arm = PIL.Image.open(curse4['black back arm']).convert("RGBA")
                elif color == 'cyan':
                    back_arm = PIL.Image.open(curse4['cyan back arm']).convert("RGBA")
          
                
            base = head.copy()
            with base as base:
                base.paste(back_arm, (0, 0), back_arm)
                base.paste(torso, (0, 0), torso)
                base.paste(front_arm, (0, 0), front_arm)
                base.paste(head, (0, 0), head)
                body = base.convert("RGBA")
                buf = io.BytesIO()
                body.save(buf, format="PNG")
                buf.seek(0)
                await ctx.send(file=discord.File(buf, "custom_character.png"))
                return
            
            # Composite the overlays on top of the base body paint
            return

        if female:
            
            random_skintone = random.choice(list(female_body_skins.keys()))
            skintone = PIL.Image.open(female_body_skins[random_skintone]).convert("RGBA")
            hair_select = random.choice(['hair1', 'hair2', 'hair3', 'hair4', 'hair5', 'hair6'])
            if hair_select == 'hair1':
                random_beanie = random.choice([beanie for beanie in female_hair['Hair 1']['beanies'].keys()])
                beanie = PIL.Image.open(female_hair['Hair 1']['beanies'][random_beanie]).convert("RGBA")
                random_color = random.choice([color for color in female_hair['Hair 1']['hair'].keys()])
                hair_color = PIL.Image.open(female_hair['Hair 1']['hair'][random_color]).convert("RGBA")
                hair_overlay = PIL.Image.open('images/Characters/Humans/Female/Hair/hair1/hiar1_outline.png').convert("RGBA")
                with hair_color as base:
                    base.paste(beanie, (0, 0), beanie)
                    hair = PIL.Image.alpha_composite(base, hair_overlay).convert("RGBA")
            elif hair_select == 'hair2':
                random_front_hair = random.choice([front for front in female_hair['Hair 2']['Front Hair'].keys()])
                hair = PIL.Image.open(female_hair['Hair 2']['Front Hair'][random_front_hair]).convert("RGBA")
                back_hair = PIL.Image.open(female_hair['Hair 2']['Back Hair'][random_front_hair]).convert("RGBA")
            elif hair_select == 'hair3':
                random_hair_color = random.choice([color for color in female_hair['Hair 3']['Hair'].keys()])
                hair = PIL.Image.open(female_hair['Hair 3']['Hair'][random_hair_color]).convert("RGBA")
                random_hair_color = random.choice([color for color in female_hair['Hair 4'].keys()])
                hair = PIL.Image.open(female_hair['Hair 4'][random_hair_color]).convert("RGBA")
            elif hair_select == 'hair4':
                random_hair_color = random.choice([color for color in female_hair['Hair 4'].keys()])
                hair = PIL.Image.open(female_hair['Hair 4'][random_hair_color]).convert("RGBA")

            elif hair_select == 'hair5':
                random_hair_color = random.choice([color for color in female_hair['Hair 5'].keys()])
                hair = PIL.Image.open(female_hair['Hair 5'][random_hair_color]).convert("RGBA")
            elif hair_select == 'hair6':
                random_front_hair = random.choice([front for front in female_hair['Hair 6']['Front'].keys()])
                hair = PIL.Image.open(female_hair['Hair 6']['Front'][random_front_hair]).convert("RGBA")
                back_hair = PIL.Image.open(female_hair['Hair 6']['Back'][random_front_hair]).convert("RGBA")

            random_eyebrows = random.choice([eyebrow for eyebrow in female_hair['Eyebrows'].keys()])
            eyebrows = PIL.Image.open(female_hair['Eyebrows'][random_eyebrows]).convert("RGBA")
            random_eyes = random.choice([eye for eye in female_eyes.keys()])
            eyes = PIL.Image.open(female_eyes[random_eyes]).convert("RGBA")
            random_lips = random.choice([lip for lip in female_lips.keys()])
            lips = PIL.Image.open(female_lips[random_lips]).convert("RGBA")

            random_clothes = random.choice(['school', 'fighter', 'casual', 'suit'])
            if random_clothes == 'school':
                random_clothes_color = random.choice([color for color in female_school_fits.keys()])
                clothes = PIL.Image.open(female_school_fits[random_clothes_color]).convert("RGBA")
            elif random_clothes == 'fighter':
                random_clothes_color = random.choice([color for color in female_fighter_fits.keys()])
                clothes = PIL.Image.open(female_fighter_fits[random_clothes_color]).convert("RGBA")
            elif random_clothes == 'casual':
                random_clothes_color = random.choice([color for color in female_casual_fits['front'].keys()])
                if random_clothes_color == 'default' or random_clothes_color == 'blue' or random_clothes_color == 'red':
                    clothes = PIL.Image.open(female_casual_fits['front'][random_clothes_color]).convert("RGBA")
                    back_clothes = PIL.Image.open(female_casual_fits['back']['default']).convert("RGBA")
                elif random_clothes_color == 'white':
                    clothes = PIL.Image.open(female_casual_fits['front'][random_clothes_color]).convert("RGBA")
                    back_clothes = PIL.Image.open(female_casual_fits['back']['white']).convert("RGBA")
                    
            elif random_clothes == 'suit':
                random_clothes_color = random.choice([color for color in female_suits.keys()])
                clothes = PIL.Image.open(female_suits[random_clothes_color]).convert("RGBA")
            # Composite the overlays on top of the base body paint
        if male:
            skintone_select= random.choice(list(male_skins.keys()))
            skintone = PIL.Image.open(male_skins[skintone_select]).convert("RGBA")
            hair_select = random.choice(['1', '2', '3', '4', '5', '6'])
            if hair_select == '1':
                random_hair_color = random.choice([color for color in male_hair['1'].keys()])
                hair = PIL.Image.open(male_hair['1'][random_hair_color]).convert("RGBA")
            elif hair_select == '2':
                random_hair_color = random.choice([color for color in male_hair['2'].keys()])
                hair = PIL.Image.open(male_hair['2'][random_hair_color]).convert("RGBA")
            elif hair_select == '3':
                random_hair_color = random.choice([color for color in male_hair['3'].keys()])
                hair = PIL.Image.open(male_hair['3'][random_hair_color]).convert("RGBA")
            elif hair_select == '4':
                random_hair_color = random.choice([color for color in  male_hair['4'].keys()])
                hair = PIL.Image.open(male_hair['4'][random_hair_color]).convert("RGBA")
            elif hair_select == '5':
                random_hair_color = random.choice([color for color in male_hair['5'].keys()])
                hair = PIL.Image.open(male_hair['5'][random_hair_color]).convert("RGBA")
            elif hair_select == '6':
                random_hair_color = random.choice([color for color in male_hair['6'].keys()])
                hair = PIL.Image.open(male_hair['6'][random_hair_color]).convert("RGBA")
            clothes_select = random.choice(['school', 'fighter', 'casual', 'suit'])
            if clothes_select == 'school':
                random_clothes_color = random.choice([color for color in male_school['front'].keys()])
                back_clothes = PIL.Image.open(male_school['back']['default']).convert("RGBA")
                clothes = PIL.Image.open(male_school['front'][random_clothes_color]).convert("RGBA")

            elif clothes_select == 'fighter':
                random_clothes_color = random.choice([color for color in male_fighter_fits.keys()])
                clothes = PIL.Image.open(male_fighter_fits[random_clothes_color]).convert("RGBA")
            elif clothes_select == 'casual':
                random_clothes_color = random.choice([color for color in male_casual_fits['Front'].keys()])
                back_clothes = PIL.Image.open(male_casual_fits['Back'][random_clothes_color]).convert("RGBA")
                clothes = PIL.Image.open(male_casual_fits['Front'][random_clothes_color]).convert("RGBA")
            elif clothes_select == 'suit':
                random_clothes_color = random.choice([color for color in male_suit.keys()])
                clothes = PIL.Image.open(male_suit[random_clothes_color]).convert("RGBA")
            random_eyes = random.choice([eye for eye in male_eyes.keys()])
            eyes = PIL.Image.open(male_eyes[random_eyes]).convert("RGBA")
            random_eyebrows = random.choice([eyebrow for eyebrow in male_eyebrows.keys()])
            eyebrows = PIL.Image.open(male_eyebrows[random_eyebrows]).convert("RGBA")
            male_pupils = PIL.Image.open('images/Characters/Humans/Male/Eyes/male_pupils.png').convert("RGBA")
        

        female_base_outline = PIL.Image.open('images/Characters/Humans/Female/OVERLAY.png').convert("RGBA")
        male_base_outline = PIL.Image.open('images/Characters/Humans/Male/male_body_outline.png').convert("RGBA")
        base=skintone.copy()
        if back_clothes:
                base.paste(back_clothes, (0, 0), back_clothes)
        if back_hair:
                base.paste(back_hair, (0, 0), back_hair)

        base.paste(skintone.copy(), (0, 0), skintone.copy())
        if female:
            base.paste(whites, (0, 0), whites)
        if male:
            base.paste(male_whites, (0, 0), male_whites)
        base.paste(eyes, (0, 0), eyes)
        if female:
            base.paste(pupils, (0, 0), pupils)  
            base.paste(lips, (0, 0), lips)  
        if male:
            base.paste(male_pupils, (0,0) , male_pupils)


        base.paste(eyebrows, (0, 0), eyebrows)
       
        if female:
            base.paste(female_base_outline, (0,0), female_base_outline)
        elif male:
            base.paste(male_base_outline, (0,0), male_base_outline)
        base.paste(clothes, (0, 0), clothes)            
        base.paste(hair, (0, 0), hair)

        buf = io.BytesIO()
        base.save(buf, format="PNG")
        buf.seek(0)
        # Send the generated image as a Discord file from the buffer
        await ctx.send(file=discord.File(buf, "custom_character.png"))

async def setup(bot):
    await bot.add_cog(CustomCharacter(bot))

