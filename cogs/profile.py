import discord, old_techniques, game, traceback
from discord import player
from discord.flags import MessageFlags
from discord.enums import ButtonStyle, TextStyle
from discord import file
from discord.ext import commands
from discord import app_commands



def skills_embed(player, msg):
    _, xp_needed = player.ready_level_up()
    
    embed = discord.Embed(title="Use Skillpoints", description='```Distribute your skill points and build up your character!```')
    embed.add_field(name="**Available Skill Points**", value=player.skp)
    
    embed.add_field(name="**Existing Stats**", value=f"**Strength:** {player.attack}\n**Speed:** {player.speed}\n**CE:** {player.ce}/{player.max_ce}\n**HP**: {player.hp}/{player.max_hp}\n**CT level**: {player.ct_level}\n**Player level**: {player.level}\n**XP**: {player.xp}/{xp_needed}")
    return embed
    

class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

   
    @commands.hybrid_command(name="level", description = "Check your current level stats")
    async def level(self, ctx, member: discord.Member=None):
        if member is None:
            member = ctx.author.id
        player_stats = dynamo.read_player(member, ctx.guild.id)
        if player_stats is None:
            await ctx.send("Player not found.")
        colony = player_stats['colony']
        
        if colony is None:
            await ctx.send("Error, no colony found, deleting player from colony")
            dynamo.delete_from_colony(ctx.guild.id, 'members', player_stats['user_id'])
            await ctx.send("player deleted")

        if ctx.guild.id == colony:
            char = self.bot.load_character(player_stats['user_id'], ctx.guild.id)
            ready, xp_needed = char.ready_level_up()
            embed = discord.Embed(title=f"{char.name}'s Levels", description=f"**PLAYER LEVEL:** `{char.level}`\n**CT LEVEL:** `{char.ct_level}`\n{char.get_grade()}\n**XP:** `{char.xp}/{xp_needed}`")
            msg = await ctx.send(embed=embed)
            if ready:
                embed = msg.embeds[0]
                char.level_up(xp_needed)
                embed.add_field(name="**LEVEL UP**", value=f"**You leveld up!**\n**New Level:** `{char.level}`")
                await msg.edit(embed=embed)
            
            
            
            
            
    
    
    @commands.hybrid_command(name="profile", description="View your profile")
    async def profile(self, ctx, member: discord.Member = None):
        try:
            await ctx.defer()
            id= None
            if member is None:
                id = ctx.author.id
            else:
                id = member.id
            player_stats = dynamo.read_player(id, ctx.guild.id)
            if player_stats is None:
                await ctx.send("Player not found.")
                return
        
            colony = player_stats['colony']
        
            if colony is None:
                await ctx.send("Error player has no colony, deleting player")
                dynamo.delete_from_colony(ctx.guild.id, 'members', player_stats['user_id'])
                await ctx.send("player deleted")
        
            if ctx.guild.id == colony:
                member_obj = await self.bot.fetch_user(id)
                user_profile = await ctx.guild.fetch_member(id)
                banner = None
                if hasattr(member_obj, 'banner') and member_obj.banner:
                    banner = member_obj.banner
                char = game.Character(**player_stats)
                stat =  self.bot.status_embed(user_profile, char, banner)
                inv = [e for e in player_stats['inventory']]
                for e in inv:
                    if e in old_techniques.cursed_tools:
                        inv.remove(e)
                        e = old_techniques.get_cursed_tool(e)
                        inv.append("`" + e.name + "`" + e.emote )
                string = "`Inventory:` " + ",".join(inv)
                
                await ctx.send(string)
                
                equip = [e for e in player_stats['equipment']]
                for e in equip:
                    if e in old_techniques.cursed_tools:
                        equip.remove(e)
                        e = old_techniques.get_cursed_tool(e)
                        equip.append("`" + e.name + "`" +e.emote)
                        
                
                await ctx.send("`Equipped:` " + ",".join(equip))
                msg = await ctx.send(file=stat)
                await msg.edit(view=ProfileView(msg, char))
                return
        except Exception as e:
            print(f"Error in profile command: {e}")
            traceback.print_exc()
            return
                
            

class ProfileView(discord.ui.View):
    def __init__(self, msg, player):
        super().__init__(timeout=False)
        self.add_item(Equip(msg, player))
        self.add_item(Store(msg, player))
        self.add_item(Skills(msg, player))
        self.add_item(Victory(msg, player))


class Equip(discord.ui.Button):
    def __init__(self, msg, player):
        super().__init__(label='Equip', style=discord.ButtonStyle.blurple)
        self.msg = msg
        self.player = player

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if interaction.user.id != self.player.user_id:
            await interaction.followup.send("You can't equip items for this player", ephemeral=True)
            return            
        ct_list = [item for item in self.player.inventory if item in old_techniques.cursed_tools]
        bv_list = [vow for vow in self.player.inventory if vow in old_techniques.BVs]
        rule_list = [rule for rule in self.player.inventory if rule in old_techniques.rules]
        ct_str = ''
        bv_str = ''
        rule_str = ''
        tool = None
        for ct in ct_list:
            tool = old_techniques.get_cursed_tool(ct)
            ct_str += f'**{tool.name}** {tool.emote}\n**Dmg:** `{tool.attack}` **Pen:** `{tool.pen}`'
            if tool.negate:
                ct_str += ' **Negs:** `Yes`'
            else:
                ct_str += ' **Negs:** `No`'
    

        for bv in bv_list:
            vow = old_techniques.get_BV(bv)
            bv_str += f'{vow.name}\n**Description:** `{vow.description}`'

        for rule in rule_list:
            cgrule = old_techniques.get_rule(rule)
            rule_str += f'{cgrule.name}\n**Description:** `{cgrule.description}`'

        print('tools: ' + ct_str)
        print('rules: ' + rule_str)
        print('vows: ' + bv_str)

        embed = discord.Embed(title='Equip Menu', description='```Choose an item to equip```')
        embed.add_field(name='**Cursed Tools**', value=ct_str if ct_str else 'None') 
        embed.add_field(name='**Binding Vows**', value=bv_str if bv_str else 'None')  
        embed.add_field(name='**Rules**', value=rule_str if rule_str else 'None')
        await self.msg.edit(embed=embed, view=EquipView(self.msg, self.player.user_id, self.player))
 
class Victory(discord.ui.Button):
    def __init__(self, msg, player):
        self.msg = msg
        self.player = player
        super().__init__(label='Victory', style=discord.ButtonStyle.gray)

    async def callback(self, interaction: discord.Interaction):
        victory_modal = VictoryModal()
        victory_modal.player = self.player
        victory_modal.msg = self.msg
        await interaction.response.send_modal(victory_modal)



class VictoryModal(discord.ui.Modal, title="Victory Message Form"):
        message=discord.ui.TextInput(label="Enter a Message", placeholder="Cant be more than 100 chars", max_length=100, style=TextStyle.long, required=True,)

    
        async def on_submit(self, interaction: discord.Interaction):
                title="Victory Message Changed"
                description = f"### Victory message set to:\n  `{self.message.value}`"
                embed = discord.Embed(title=title, description=description)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                self.player.victory_msg = self.message.value
                self.player.save_to_db()

    
        
class Store(discord.ui.Button):
    def __init__(self, msg, player):
        super().__init__(label='Store', style=discord.ButtonStyle.blurple)
        self.msg = msg
        self.player = player

    async def callback(self, interaction: discord.Interaction):
        
        if interaction.user.id != self.player.user_id:
            await interaction.response.send_message(content="You can't store this players items", ephemeral=True)
            return
        if len(self.player.inventory) <= 0:
            await interaction.response.send_message("`Equipment empty`")
            await self.msg.edit(view=ProfileView(self.msg, self.player))
            
            return
        
        embed = discord.Embed(title='```Choose an equipped item to store in your inventroy```', description='\n>'.join(self.player.equipment))
        
        await self.msg.edit(embed=embed, view=StoreView(self.msg, self.player.user_id, self.player))


class StoreView(discord.ui.View):
    def __init__(self, msg, id, player):
        super().__init__(timeout=None)
        self.add_item(StoreSelect(msg, id, player))
    


class EquipView(discord.ui.View):
            def __init__(self, msg, id, player):
                super().__init__(timeout=180)
                self.add_item(ToolSelect(msg, id, player))
        
        
class ToolSelect(discord.ui.Select):
        def __init__(self, msg, id, player):
            self.id = id
            self.player = player
            self.msg = msg
            options=[]
            for name, tool in old_techniques.cursed_tools.items():
                if name in self.player.inventory:
                    options.append(discord.SelectOption(label=name, value=name))
            super().__init__(placeholder='Select a tool...', options=options)

        async def callback(self, interaction: discord.Interaction):
            await interaction.response.defer()
            value = self.values[0]
            if interaction.user.id != self.id:
                await interaction.followup.send("This is not your inventory")
                return
            if value not in self.player.inventory:
                await interaction.followup.send("Error: Tool not found", ephemeral=True)
                return
            items = self.player.equipment
            tools = [tool for tool in items if tool in old_techniques.cursed_tools]
            if self.player.HR:
                if len(tools) < 2:
                    self.player.equip(value)
                else:
                    await interaction.followup.send("Can't equip more than 2 cursed tools", ephemeral=True)
                    return
            else:
                if len(tools) >= 1:
                    await interaction.followup.send("Can't equip more than 1 cursde tool", ephemeral=True)
                    return
                else:
                    self.player.equip(value)
        
            await interaction.followup.send(f'{value} added to your equipped items!')
            await self.msg.edit(embed=None, view=ProfileView(self.msg, self.player))
            return
        

class StoreSelect(discord.ui.Select):
    def __init__(self, msg, id, player):
        self.player = player
        self.id = id
        self.msg = msg
        equipment= [t for t in set(self.player.equipment)]
        options=[discord.SelectOption(label=e, value=e) for e in equipment]
        super().__init__(placeholder="Select an item to store", options=options)


    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        value = self.values[0]
        if interaction.user.id != self.id:
            await interaction.followup.send("This is not your profile", ephemeral=True)
            return
        self.player.store(value)
        await interaction.followup.send(f"{value} has been returned to your inventory")
        await self.msg.edit(view=ProfileView(self.msg, self.player))


            
class Skills(discord.ui.Button):
    def __init__(self, msg,player):
        self.msg = msg
        self.player = player
        super().__init__(label='Skills', style=discord.ButtonStyle.green)
        
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        msg = self.msg
        player = self.player
        id = int(self.player.user_id)
        if id != interaction.user.id:
            await interaction.followup.send("This is not your profile", ephemeral=True)
            return
        embed = skills_embed(self.player, msg)
        await msg.edit(embed=embed)
        await msg.edit(view=SkillsView(msg, self.player))
        

    
class SkillsView(discord.ui.View):
    def __init__(self, msg, player):
        super().__init__(timeout=None)
        self.add_item(SkillSelect(msg, player))



class SkillSelect(discord.ui.Select):
    def __init__(self, msg, player):
        options = [discord.SelectOption(label='Strength', description = 'Increase output', value='attack'), 
                  discord.SelectOption(label='Speed', description = 'Increase speed', value='speed'),
                   discord.SelectOption(label='Cursed Energy', description = 'Increase curse energy efficiency', value='ce'),
                  discord.SelectOption(label="Health Points", description = "Increase vitality", value="hp")]
        
        self.msg = msg
        self.character = player
        super().__init__(placeholder='Select an upgrade...', options=options)


    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.character.user_id:
            await interaction.response.send_message('This is not your character!', ephemeral=True)
            return
        stat = self.values[0]
        if self.character.skp > 0:
            skpmodal = SkillPointModal()
            skpmodal.stat = stat
            skpmodal.player = self.character
            skpmodal.msg = self.msg
            skpmodal.skp = self.character.skp
            await interaction.response.send_modal(skpmodal)
            
        else:
            await interaction.response.send_message('You have no skill points left!', ephemeral=True)
            return
        
        
        



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
                
                if stat == 'attack':
                    self.player.attack += amount
                    sk_msg = f'Your strength has been increased by {amount}!'

                elif stat == 'speed':
                    self.player.speed += amount
                    sk_msg = f'Your speed has been increased by {amount}!'

                elif stat == 'ce':
                    self.player.max_ce += amount
                    self.player.ce = self.player.max_ce
                    sk_msg = f'Your CE has been increased by {amount}!'

                elif stat == 'hp':
                    self.player.max_hp += amount
                    self.player.hp = self.player.max_hp
                    sk_msg = f'Your HP has been increased by {amount}!'

                self.player.skp -= amount
                player = self.player
                embed = discord.Embed(title='Skill Point Menu', description=f"`{sk_msg}`\n**Choose a stat to level up**", color=discord.Color.yellow())
                embed.add_field(name='**Current Stats**', value=f'\n**CT Level**: `{player.ct_level}`\n**STRENGTH**: `{player.attack}` \n**SPEED**: `{player.speed}` \n**CE**: `{player.ce}/{player.max_ce}`\n**HP**: `{player.max_hp}`\n**Skill Points**: `{player.skp}`', inline=False)
                self.player.save_to_db()
                await self.msg.edit(embed=embed, view=SkillsView(self.msg, self.player))
                return
            else:
                await interaction.response.send_message('Not Enough Skill Points!', ephemeral=True)
                return

        async def error(self, interaction: discord.Interaction, error):
            print(error)
            return
        
 
        
        
        


    
async def setup(bot:commands.Bot):
    await bot.add_cog(Profile(bot))

