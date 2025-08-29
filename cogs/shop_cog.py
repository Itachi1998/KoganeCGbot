import discord
from game import Player
from db import read_colony, read_player
from cursed_tools import cursed_tools
#from .colonies_cog import Colonies
from discord.ext import commands
#from io import BytesIO


class Shop_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        @commands.Cog.listener()
        async def on_ready(self):
            print('Shop cog is ready!')


async def setup(bot):
    await bot.add_cog(Shop_cog(bot))


# png_dict = {
#     'gray': 'images/grayshop.png',
#     'blue': 'images/blueshop.png',
#     'green': 'images/greenshop.png',
#     'pink': 'images/pinkshop.png',
#     'black': 'images/blackshop.png'
# }

# font_file = "Digital_tech.otf"


# def check_id(id1, id2):
#     if id1 == id2:
#         return True


# def shop_color(color):
#     for i in png_dict:
#         if color == i:
#             png = png_dict[i]
#             return png  #'images/greenshop.png'


# def get_image(image, name: list, price, title):
#     img = Image.open(image)
#     draw = ImageDraw.Draw(img)  #canvas
#     title_font = ImageFont.truetype(font_file, size=70)
#     header_font = ImageFont.truetype(font_file, size=60)
#     name_font = ImageFont.truetype(font_file, size=58)

#     draw.text((35, 200),
#               "NAME",
#               font=header_font,
#               fill=(255, 255, 255),
#               stroke_width=2,
#               stroke_fill=1)

#     draw.text((490, 200),
#               "PRICE",
#               font=header_font,
#               fill=(255, 255, 255),
#               stroke_width=2,
#               stroke_fill=1)

#     draw.text((120, 60),
#               title,
#               font=title_font,
#               fill=(255, 255, 255),
#               stroke_width=2,
#               stroke_fill=1)

#     if 'transfer' in name.lower():
#         draw.text((35, 300),
#                   name, (0, 255, 255),
#                   font=name_font,
#                   stroke_width=2,
#                   stroke_fill=1)
#         draw.text((580, 300),
#                   price,
#                   font=name_font,
#                   fill=(255, 0, 255),
#                   stroke_width=2,
#                   stroke_fill=1)

#     else:
#         draw.text((45, 300),
#                   name,
#                   font=name_font,
#                   fill=(0, 255, 255),
#                   stroke_width=2,
#                   stroke_fill=1)
#         draw.text((480, 300),
#                   price,
#                   font=name_font,
#                   fill=(255, 0, 250),
#                   stroke_width=2,
#                   stroke_fill=1)

#     buf = BytesIO()  # Create an instance of BytesIO
#     img.save(buf, 'PNG')
#     buf.seek(0)  # Set the stream position to the start
#     image_file = discord.File(fp=buf, filename="status.png")
#     del img
#     return image_file


def cursed_tool_shop():

    cursed_tool_items = list(cursed_tools.items())

    name = ""

    price = ""

    for key, value in cursed_tool_items:
        price += f"{value.cost}\n\n"
        name += f"{value.name}\n\n"

    return name, price


class CursedToolLayout(discord.ui.LayoutView):
    def __init__(self, bot, msg):
        container = discord.ui.Container(discord.ui.TextDisplay("# `Cursed Tool Shop`"))
        container.add_item(discord.ui.Separator(spacing=discord.SeparatorSpacing.large))
        
        self.select = CursedToolSelect(msg, bot)
        section = discord.ui.Section(accessory=self.select)
        katana_title = discord.ui.TextDisplay("## `Katana <:soulsplit:1277632881640083456>`")
        katana = cursed_tools["Katana"]
        katana_info = discord.ui.TextDisplay(f"{katana.name}\n"
                                                f"'Cost:' {katana.cost}\n"
                                                f"'HP:' {katana.hp}\n"
                                                f"'Max HP:' {katana.max_hp}\n"
                                                f"'AOE:' {katana.aoe}\n",
                                                f"'Strength:' {katana.strength}\n"
                                                f"'Speed:' {katana.speed}\n"
                                                f"'Type:' {katana.type}"
                                                )
        
        section.add_item(katana_title)
        section.add_item(katana_info)
        container.add_item(section)
        
    

class Shop(commands.Cog):

     def __init__(self, bot):
         self.bot = bot

     @commands.hybrid_command(name="shop", description="Shows the shop")
     async def shop(self, ctx):
        await ctx.defer()
        colony_Data = read_colony(ctx.guild.id)
        if colony_Data is None:
            await ctx.send("You are not in a colony")
            return

        #colony = Colonies(**colony_Data)  #instantiate colony

        #color = colony.colony_color  #set color variable depending on the colony the shop command was used in

        #image = shop_color(color)

        msg = await ctx.send(
            "Welcome to the shop! Buy cursed tools, vows, and rules here to help you achieve your goals!"
        )

        # name, price = cursed_tool_shop()

        # title = 'Cursed Tool Shop'
        
        await ctx.send(view=CursedToolLayout(self.bot, msg))

        #await msg.edit(view=CursedToolView(msg, self.bot))
        
        # img = get_image(image, name, price, title)

        # msg = await ctx.send(file=img)

        # await msg.edit(view=CursedToolView(msg, ctx.author.id, self.bot, color)
        #       )


class CursedToolView(discord.ui.View):

    def __init__(self, msg, bot):
        super().__init__(timeout=None)
        # self.add_item(Vow(msg, id, bot, color))
        # self.add_item(Rule(msg, id, bot, color))
        self.add_item(CursedToolSelect(msg, bot))


# class BvView(discord.ui.View):

#     def __init__(self, msg, id, bot, color):
#         super().__init__(timeout=None)
#         self.add_item(Cursedtool(msg, id, bot, color))
#         self.add_item(Rule(msg, id, bot, color))
#         self.add_item(VowSelect(msg, id, bot, color))


# class RuleView(discord.ui.View):

#     def __init__(self, msg, id, bot, color):
#         super().__init__(timeout=None)
#         self.add_item(Cursedtool(msg, id, bot, color))
#         self.add_item(Vow(msg, id, bot, color))
#         self.add_item(RuleSelect(msg, id, bot, color))


# class Cursedtool(discord.ui.Button):

#     def __init__(self, msg, id, bot):
#         super().__init__(label="Cursed Tool Shop",
#                          style=discord.ButtonStyle.blurple)
#         self.bot = bot
#         self.msg = msg
#         self.id = id
#         #self.color = color

#     async def callback(self, itx: discord.Interaction):
#         await itx.response.defer()
#         self.disabled = True

        # id = check_id(itx.user.id, self.id)
        # if not id:
        #     await itx.response.send_message(
        #         content="It is not your turn yet", ephemeral=True)

        #     return

        # name, price = cursed_tool_shop()

        # title = 'Cursed Tool Shop'

        # image = shop_color(self.color)

        # img = get_image(image, name, price, title)

        # msg = await self.msg.edit(attachments=[img])

        # await msg.edit(view=CursedToolView(msg, self.id, self.bot, self.color))


class CursedToolSelect(discord.ui.ActionRow['CursedToolLayout']):

    def __init__(self, msg, bot):
        self.msg = msg
        self.bot = bot
        #self.color = color
        cursed_tool_items = list(cursed_tools.values())

        options = [
            discord.SelectOption(
                label=f"{tool_obj.name}",
                value=tool_obj.name,
                description=
                f"Price: {tool_obj.cost}, Strength: {tool_obj.strength}, Negates: {tool_obj.negates}, Durability: {tool_obj.max_hp}"
                ) for tool_obj in cursed_tool_items
        ]

        super().__init__()
        self.placeholder = 

    async def callback(self, itx: discord.Interaction):
        await itx.response.defer()

        # id = check_id(itx.user.id, self.id)
        # if not id:
        #     await itx.response.send_message(
        #         content="It is not your turn yet", ephemeral=True)

        #     return

        name = self.values[0]

        tool = cursed_tools[name]

        price = tool.cost
        
        player_dict, techlist = read_player(itx.user.id, itx.user.guild.id, value=None)

        player = Player(**player_dict)

        if player is None:

            await itx.followup.send(content="Player not found", ephemeral=True)

            return

        if player.cgp >= price:
            player.cgp -= price
            player.inventory["Tools"][name]=tool 
            player.save_to_db()
            print(player.inventory)

            await itx.followup.send(
                content=f"You bought {name} for {price} points")
            await self.msg.edit(
                view=CursedToolView(self.msg, self.bot))
            return
        else:
            await itx.followup.send(
                content=f"You don't have enough points to buy {name}.",
                ephemeral=True)
            return


# class Vow(discord.ui.Button):

#     def __init__(self, msg, id, bot, color):
#         self.msg = msg
#         self.id = id
#         self.bot = bot
#         self.color = color
#         super().__init__(label="Vow Shop", style=discord.ButtonStyle.blurple)

#     async def vow_shop(self):
#         binding_vows = old_techniques.BVs
#         name = ""
#         price = ""
#         for key, vow_obj in binding_vows.items():
#             price += f"   {vow_obj.cost}\n\n"
#             name += f"{vow_obj.name}\n\n"
#         return name, price

#     async def callback(self, interaction: discord.Interaction):
#         await itx.response.defer()

#         id = check_id(itx.user.id, self.id)
#         if not id:
#             await itx.response.send_message(
#                 content="It is not your turn yet", ephemeral=True)

#         title = '  Binding Vow Shop'

#         name, price = await self.vow_shop()

#         image = shop_color(self.color)

#         img = get_image(image, name, price, title)

#         msg = await self.msg.edit(attachments=[img])

#         await msg.edit(view=BvView(msg, self.id, self.bot, self.color))


# class VowSelect(discord.ui.Select):

#     def __init__(self, msg, id, bot, color):
#         options = [
#             discord.SelectOption(
#                 label=f"{vow_obj.name}    Price: {vow_obj.cost}",
#                 description=vow_obj.description,
#                 value=vow_obj.name) for vow_obj in old_techniques.BVs.values()
#         ]
#         super().__init__(placeholder="Select a vow", options=options)
#         self.msg = msg
#         self.id = id
#         self.bot = bot
#         self.color = color

#     async def callback(self, interaction: discord.Interaction):
#         await itx.response.defer()
#         if itx.user.id != self.id:
#             await itx.followup.send(
#                 content="You did not use this command", ephemeral=True)
#             return
#         name = self.values[0]
#         vow = old_techniques.BVs[name]
#         price = vow.cost
#         player = self.bot.load_character(self.id, itx.guild.id)
#         if player.cgp >= price:
#             player.cgp -= price
#             player.inventory.append(name)
#             player.save_to_db()
#             await itx.followup.send(
#                 content=f"You bought {name} for {price} points.")
#             await self.msg.edit(
#                 view=BvView(self.msg, self.id, self.bot, self.color))
#             return

#         else:
#             await itx.followup.send(
#                 content=f"You don't have enough points to buy {name}.",
#                 ephemeral=True)
#             await self.msg.edit(
#                 view=BvView(self.msg, self.id, self.bot, self.color))
#             return


# class Rule(discord.ui.Button):

#     def __init__(self, msg, id, bot, color):
#         self.msg = msg
#         self.id = id
#         self.bot = bot
#         self.color = color
#         super().__init__(label="Rule Shop", style=discord.ButtonStyle.blurple)

#     async def rule_shop(self):
#         rules = old_techniques.rules
#         name = ""
#         price = ""
#         for key, rule_obj in rules.items():
#             price += f"   {rule_obj.cost}\n\n"
#             name += f"{rule_obj.name}\n\n"
#         return name, price

#     async def callback(self, interaction: discord.Interaction):
#         await itx.response.defer()
#         if itx.user.id != self.id:
#             await itx.response.send_message(
#                 content="You did not use this command", ephemeral=True)
#             return
#         title = "        Rule Shop"
#         name, price = await self.rule_shop()

#         image = shop_color(self.color)

#         img = get_image(image, name, price, title)

#         msg = await self.msg.edit(attachments=[img])

#         await msg.edit(view=RuleView(msg, self.id, self.bot, self.color))


# class RuleSelect(discord.ui.Select):

#     def __init__(self, msg, id, bot, color):
#         self.msg = msg
#         self.id = id
#         self.bot = bot
#         self.color = color
#         options = [
#             discord.SelectOption(
#                 label=f"{rule_obj.name}    Price: {rule_obj.cost}",
#                 description=rule_obj.description,
#                 value=rule_obj.name) for rule_obj in old_techniques.rules.values()
#         ]
#         super().__init__(placeholder="Select a rule", options=options)

#     async def callback(self, interaction: discord.Interaction):
#         await itx.response.defer()
#         if itx.user.id != self.id:
#             await itx.followup.send(
#                 content="You did not use this command", ephemeral=True)
#             return
#         player = self.bot.load_character(self.id, itx.guild.id)
#         name = self.values[0]
#         rule = old_techniques.rules[name]
#         price = rule.cost
#         if player.cgp >= price:
#             player.cgp -= price
#             player.inventory.append(name)
#             player.save_to_db()
#             await itx.followup.send(
#                 content=f"You bought {name} for {price} points.",
#                 view=RuleView(self.msg, self.id, self.bot, self.color))
#             await self.msg.edit(
#                 view=RuleView(self.msg, self.id, self.bot, self.color))
#             return
#         else:
#             await itx.followup.send(
#                 content=f"You don't have enough points to buy {name}.",
#                 ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Shop(bot))
