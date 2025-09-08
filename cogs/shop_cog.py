import discord
from discord import ui
from game import Player
from db import read_colony, read_player
from cursed_tools import cursed_tools
from discord.ext import commands


#region Shop_cog setup
class Shop_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        @commands.Cog.listener()
        async def on_ready(self):
            print('Shop cog is ready!')


async def setup(bot):
    await bot.add_cog(Shop_cog(bot))
#endregion


#region Shop command
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
        
        msg = await ctx.send(
            "Welcome to the shop! Buy cursed tools, vows, and rules here to help you achieve your goals!"
        )

        await ctx.send(view=CursedToolView(msg, self.bot))
#endregion


#region PurchaseButton *unfinished
class PurchaseButton(ui.Button):
    def __init__(self):
        super().__init__(label='Purchase', disabled=True, style=discord.ButtonStyle.green)

    async def callback(self, itx: discord.Interaction):
        await itx.response.send_message("You purchased a tool - test")
#endregion


#region CursedToolSelect
class CursedToolSelect(ui.ActionRow['CursedToolView']):
    cursed_tool_values = list(cursed_tools.values())
    options = [
                discord.SelectOption(
                label=f"{tool_obj.name}",
                value=tool_obj.name,
                description=
                f"Price: {tool_obj.cost}, Strength: {tool_obj.strength}, Negates: {tool_obj.negates}, Durability: {tool_obj.max_hp}",
                emoji=tool_obj.emoji
                ) for tool_obj in cursed_tool_values
            ]
    
    def __init__(self, msg):
        super().__init__()
        self.msg = msg

    @ui.select(placeholder='Select a tool to purchase', options=options)
    async def select_tool(self, itx: discord.Interaction, select: ui.Select):
        await itx.response.defer()

        name = select.values[0]
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
            # player.save_to_db()
            # print(player.inventory)

            await itx.followup.send(content=f"You bought {name} for {price} points")
            #await self.msg.edit(view=CursedToolView(self.msg))
            return
        
        else:
            await itx.followup.send(content=f"You don't have enough points to buy {name}.", ephemeral=True)
            return
#endregion


#region cursed_tool_display
def cursed_tool_display():
    display_list = []
    for k, v in cursed_tools.items():
        display = ui.TextDisplay(f"# `{k}` {v.emoji}\n"
                                    f"> **Cost:** `{v.cost}` "
                                    f"**HP:** `{v.hp}` "
                                    f"**Max HP:** `{v.max_hp}` "
                                    f"**AOE:** `{v.aoe}` "
                                    f"**Strength:** `{v.strength}` "
                                    f"**Speed:** `{v.speed}` "
                                    f"**Type:** `{v.type}`"
                                    )
        display_list.append(display)
    
    return display_list
#endregion


#region CursedToolView
class CursedToolView(ui.LayoutView):
    row = ui.ActionRow()
    
    def __init__(self, msg, bot):
        super().__init__()
        self.msg = msg

        container = ui.Container()
        header = ui.Section(ui.TextDisplay('# `Cursed Tool Shop`'), accessory=ui.Thumbnail(bot.user.avatar.url))
        container.add_item(header)
        container.add_item(ui.Separator(spacing=discord.SeparatorSpacing.large))

        displays = cursed_tool_display()
        for d in displays:
            container.add_item(d)
        
        self.add_item(container)
        container.add_item(ui.Separator(spacing=discord.SeparatorSpacing.large))
        container.add_item(CursedToolSelect(msg))

        self.remove_item(self.row)
        self.add_item(self.row)
    
    @row.button(label='Close', style=discord.ButtonStyle.blurple)
    async def close_button(self, itx: discord.Interaction, btn: ui.Button):
        await itx.response.edit_message(view=self)
        await itx.followup.send('Shop closed', ephemeral=True)
        self.stop()
        await itx.delete_original_response()
#endregion


#region cursed_tool_shop
# def cursed_tool_shop():

#     cursed_tool_items = list(cursed_tools.items())

#     name = ""

#     price = ""

#     for key, value in cursed_tool_items:
#         price += f"{value.cost}\n\n"
#         name += f"{value.name}\n\n"

#     return name, price
#endregion


#region CursedToolView old
# class CursedToolView(ui.LayoutView):
#     row = ui.ActionRow()

#     def __init__(self, bot, msg):
#         super().__init__()
#         self.bot = bot
#         self.msg = msg
        
#         container = ui.Container(ui.TextDisplay("# `Cursed Tool Shop`"))
#         container.add_item(ui.Separator(spacing=discord.SeparatorSpacing.large))
        
#         # self.select = CursedToolSelect(msg, bot)
#         # section = ui.Section(accessory=self.select)
#         katana_title = ui.TextDisplay("## `Katana <:soulsplit:1277632881640083456>`")
#         katana = cursed_tools["Katana"]
#         katana_info = ui.TextDisplay(f"'Cost:' {katana.cost}\n"
#                                             f"'HP:' {katana.hp}\n"
#                                             f"'Max HP:' {katana.max_hp}\n"
#                                             f"'AOE:' {katana.aoe}\n"
#                                             f"'Strength:' {katana.strength}\n"
#                                             f"'Speed:' {katana.speed}\n"
#                                             f"'Type:' {katana.type}"
#                                             )
#         container.add_item(katana_title)
#         container.add_item(katana_info)
#         # section.add_item(katana_title)
#         # section.add_item(katana_info)
#         # container.add_item(section)
#endregion 


#region CursedToolSelect old
# class CursedToolSelect(ui.Select):

    # def __init__(self, msg, id, bot):
    #     self.msg = msg
    #     self.id = id
    #     self.bot = bot
    #     #self.color = color
    #     cursed_tool_items = list(cursed_tools.values())

    #     options = [
    #         discord.SelectOption(
    #             label=f"{tool_obj.name}",
    #             value=tool_obj.name,
    #             description=
    #             f"Price: {tool_obj.cost}, Strength: {tool_obj.strength}, Negates: {tool_obj.negates}, Durability: {tool_obj.max_hp}"
    #             ) for tool_obj in cursed_tool_items
    #     ]

    #     super().__init__(placeholder="Choose a cursed tool...",
    #                      options=options)

    # async def callback(self, itx: discord.Interaction):
    #     await itx.response.defer()

    #     # id = check_id(itx.user.id, self.id)
    #     # if not id:
    #     #     await itx.response.send_message(
    #     #         content="It is not your turn yet", ephemeral=True)

    #     #     return

    #     name = self.values[0]

    #     tool = cursed_tools[name]

    #     price = tool.cost
        
    #     player_dict, techlist = read_player(itx.user.id, itx.user.guild.id, value=None)

    #     player = Player(**player_dict)

    #     if player is None:

    #         await itx.followup.send(content="Player not found", ephemeral=True)

    #         return

    #     if player.cgp >= price:
    #         player.cgp -= price
    #         player.inventory["Tools"][name]=tool 
    #         player.save_to_db()
    #         print(player.inventory)

    #         await itx.followup.send(
    #             content=f"You bought {name} for {price} points")
    #         await self.msg.edit(
    #             view=CursedToolView(self.msg, self.id, self.bot))
    #         return
    #     else:
    #         await itx.followup.send(
    #             content=f"You don't have enough points to buy {name}.",
    #             ephemeral=True)
    #         return
#endregion


#region image
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
#endregion


#region old views
# class CursedToolView(ui.View):

#     def __init__(self, msg, id, bot):
#         super().__init__(timeout=None)
#         # self.add_item(Vow(msg, id, bot, color))
#         # self.add_item(Rule(msg, id, bot, color))
#         self.add_item(CursedToolSelect(msg, id, bot))


# class BvView(ui.View):

#     def __init__(self, msg, id, bot, color):
#         super().__init__(timeout=None)
#         self.add_item(Cursedtool(msg, id, bot, color))
#         self.add_item(Rule(msg, id, bot, color))
#         self.add_item(VowSelect(msg, id, bot, color))


# class RuleView(ui.View):

#     def __init__(self, msg, id, bot, color):
#         super().__init__(timeout=None)
#         self.add_item(Cursedtool(msg, id, bot, color))
#         self.add_item(Vow(msg, id, bot, color))
#         self.add_item(RuleSelect(msg, id, bot, color))
#endregion


# class Cursedtool(ui.Button):

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


# class Vow(ui.Button):

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


# class VowSelect(ui.Select):

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


# class Rule(ui.Button):

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


# class RuleSelect(ui.Select):

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
