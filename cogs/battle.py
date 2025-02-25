import discord
from discord.ext import commands

bot = commands.Bot(command_prefix=',', intents=discord.Intents.all())

class Battle(commands.Cog): 

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Battle cog is ready!")



async def setup(bot):
    await bot.add_cog(Battle(bot))


    # @commands.hybrid_command(name="lobby", description="Host a lobby")
    # async def lobby(self, ctx, name: str = None):
    #     player = self.bot.load_character(ctx.author.id, ctx.guild.id)
    #     if not player:
    #         await ctx.send("Player not found")
    #         return
    #     host_id = int(ctx.author.id)
    #     if name is None:
    #         name = f"{player.name}'s lobby"
    #     guild = await self.bot.fetch_guild(os.environ['SERVERID'])
    #     log = await guild.fetch_channel(os.environ['LOGCHANNEL'])
    #     await log.send(
    #         f"Lobby created by: {str(ctx.author)}\nNamed {str(name)}\nHost id: {str(host_id)}"
    #     )  #logging

    #     ct = old_techniques.get_cursed_technique(player.technique)
    #     title = f"{name}"
    #     description = f"### Lobby created by host: `{player.name}`"
    #     field1_name = "Host"
    #     equipped = None
    #     if len(player.equipment) > 1:
    #         equipped = "`" + ", ".join(player.equipment) + "`"
    #     field1_value = f"**PLAYER:** {player.name}\n**RANK:** `{player.get_grade()}`\n**CT:** `{ct.name}` {ct.emote}\n**EQUIP:** {equipped}"
    #     thumbnail = self.bot.user.avatar.url
    #     players = [player.user_id]
    #     embed = make_embed(title=title,
    #                        description=description,
    #                        field1_name=field1_name,
    #                        field1_value=field1_value,
    #                        thumbnail=thumbnail)

    #     dynamo.save_lobby(host_id, player.colony, name, players, 0)
    #     await ctx.send(f"## Lobby created: {player.name}", ephemeral=True)
    #     msg = await ctx.send(
    #         embed=embed)  #save the message to be able to edit the embed later
    #     await msg.edit(view=LobbyView(self.bot, msg, players, host_id))

    # @commands.hybrid_command(name="pve", desscription="Battle ai")
    # async def pve(self, ctx, name: str = None):
    #     player = self.bot.load_character(ctx.author.id, ctx.guild.id)
    #     if not player:
    #         await ctx.send("Player not found")
    #         return
    #     await ctx.defer()
    #     if name == None:
    #         name = f"{player.name}'s lobby"
    #     guild = await self.bot.fetch_guild(os.environ['SERVERID'])
    #     log = await guild.fetch_channel(os.environ['LOGCHANNEL'])
    #     await log.send(
    #         f"Lobby created by: {str(ctx.author)}\nNamed {str(name)}\nHost id: {str(ctx.author.id)}\nServer: {str(ctx.guild.id)}"
    #     )  #logging
    #     msg = await ctx.send(f"### Solo lobby `{name}` CREATED!")

    #     enemy = player.pve(ctx.guild.id)
    #     avatar = self.bot.user.avatar.url
    #     dynamo.save_lobby(player.user_id, ctx.guild.id, name,
    #                           [player.user_id], 0)
    #     await pve_embed(self.bot, msg, enemy, player, ctx.author.id, avatar)

    # @commands.hybrid_command(name='pvp', description="Start pvp lobby")
    # async def pvp(self, ctx, name: str = None):
    #     player = self.bot.load_character(ctx.author.id, ctx.guild.id)
    #     if not player:
    #         await ctx.send("Player not found")
    #         return
    #     if not name:
    #         name = f"{player.name}'s lobby"
    #     host = ctx.author.id
    #     dynamo.save_lobby(host, ctx.guild.id, name, [host], 0)
    #     lob = dynamo.read_lobby(host, ctx.guild.id)
    #     choice = ctx.author.id

    #     description = f"### `PVP LOBBY`"
    #     msg = await ctx.send(f"### `{player.name}` started a pvp lobby")
    #     await pvp_embed(self.bot, host, lob['players'], lob, description, msg)


# async def respawn_enemy(enemy, colony):
#     await colonies.ai_respawn(enemy, colony)
#     return


# def turn(turn, lobby_data: dict):
#     try:
#         t_count = lobby_data['t_count']
#         mode = lobby_data['mode']
#         team1 = lobby_data['team1']
#         team2 = lobby_data['team2']
#         team1_queue = lobby_data['team1q'] if lobby_data[
#             'team1q'] is not None else []
#         team2_queue = lobby_data['team2q'] if lobby_data['team2q'] is not None else []
#         targets = lobby_data['targets'] if lobby_data['targets'] is not None else []
#         colony = lobby_data['colony']
#         hostid = lobby_data['host']
#         name = lobby_data['name']
#         players = lobby_data['players']
#         count = lobby_data['t_count']
#         marks = None
#         if lobby_data['mark']:
#             marks = lobby_data['mark']

#         t_count += 1

#         if not team2:
#             team2 = team2_queue

#         if not team1:
#             team1 = team1_queue

#         if turn in team1:
#             team1.remove(turn)
#             team1_queue.append(turn)
#             if len(team2) > 0:
#                 turn = team2[0]
#             else:
#                 team2 = [e for e in team2_queue]
#                 turn = team2[0]
#                 team2_queue.clear()

#             if len(team1) > 0:
#                 targets = [e for e in team1]
#             else:
#                 team1 = [e for e in team1_queue]
#                 targets = [e for e in team1]
#                 team1_queue.clear()
#             print(f"Turn: {turn}")
#             print(f"Targets: {targets}")
            
#             return lob

    #     elif turn in team2:
    #         team2.remove(turn)
    #         team2_queue.append(turn)
    #         if len(team1) > 0:
    #             turn = team1[0]
    #         else:
    #             team1 = [e for e in team1_queue]
    #             turn = team1[0]
    #             team1_queue.clear()

    #         if len(team2) > 0:
    #             targets = [e for e in team2]
    #         else:
    #             team2 = [e for e in team2_queue]
    #             targets = [e for e in team2]
    #             team2_queue.clear()
    #         print(f"Turn: {turn}")
    #         print(f"Targets: {targets}")
    #         dynamo.save_lobby(hostid,
    #                               colony,
    #                               name,
    #                               players,
    #                               t_count,
    #                               turn=turn,
    #                               team1=team1,
    #                               team2=team2,
    #                               team1q=team1_queue,
    #                               team2q=team2_queue,
    #                               targets=targets)
    #         lob = dynamo.read_lobby(hostid, colony)
    #         return lob
            
    #     else:
    #         new_turn = None
    #         if len(players) > 1:
    #             for p in players:
    #                 if p != turn:
    #                    new_turn = p
    #         if new_turn:
    #             dynamo.save_lobby(hostid,
    #                   colony,
    #                   name,
    #                   players,
    #                   t_count, turn=new_turn, targets=targets)
    #         else:
    #             dynamo.save_lobby(hostid,
    #                   colony,
    #                   name,
    #                   players,
    #                   t_count, turn=turn, targets=targets)
    #         lob = dynamo.read_lobby(lobby_data['host'], lobby_data['colony'])
    #         return lob
            
    # except Exception as e:
    #     print(f"Error in turn change: {e}")
    #     traceback.print_exc()


# def healthbar(health, max_health):
#     max_dashes = 4
#     dash_ratio = max_health / max_dashes
#     filled_dashes = int(health / dash_ratio)
#     dashes = "❤️" * filled_dashes
#     if filled_dashes % 1 != 0:
#         dashes += "💔"

#     percent = f"`{round((health / max_health) * 100)}%`"
#     if '-' in percent:
#         percent = "`0%`"
#     bar = f"{dashes}{percent}"
#     return bar


# def ce_bar(ce, max_ce):
#     max_dashes = 4
#     dash_ratio = max_ce / max_dashes
#     filled_dashes = 0 if ce <= 0 else int(ce / dash_ratio)
#     dashes = "<a:blueflames:1279971716382326804>" * filled_dashes
#     if filled_dashes % 1 != 0:
#         dashes += "<a:blueflames:1279971716382326804>"
#     percent = f"`{0 if ce <= 0 else round((ce / max_ce) * 100)}%`"
#     if '-' in percent:
#         percent = "`0%`"
#     bar = f"{dashes}{percent}"
#     return bar


# def check_id(id1, id2):
#     if id1 == id2:
#         return True


# def make_embed(title,
#                description,
#                thumbnail=None,
#                image=None,
#                footer=None,
#                line=True,
#                field1_name=None,
#                field1_value=None,
#                field2_name=None,
#                field2_value=None,
#                field3_name=None,
#                field3_value=None,
#                field4_name=None,
#                field4_value=None,
#                field5_name=None,
#                field5_value=None,
#                field6_name=None,
#                field6_value=None,
#                author=None):

#     embed = discord.Embed(title=title, description=description)
#     if field1_name:
#         embed.add_field(name=field1_name, value=field1_value, inline=line)
#     if field2_name:
#         embed.add_field(name=field2_name, value=field2_value, inline=line)
#     if field3_name:
#         embed.add_field(name=field3_name, value=field3_value)
#     if field4_name:
#         embed.add_field(name=field4_name, value=field4_value)
#     if field5_name:
#         embed.add_field(name=field5_name, value=field5_value, inline=line)
#     if field6_name:
#         embed.add_field(name=field6_name, value=field6_value, inline=line)
#     if author:
#         embed.set_author(name=author.display_name,
#                          icon_url=author.display_avatar.url)

#     if thumbnail:
#         embed.set_thumbnail(url=thumbnail)
#     if image:
#         embed.set_image(url=image)
#     if footer:
#         embed.set_footer(text=footer)
#     return embed


# def new_field(embed, name, value, line: bool = False, ephemeral: bool = False):
#     embed.add_field(name=name, value=value, inline=line, ephemeral=ephemeral)
#     return embed


# async def make_lobby_embed(bot, lobdata, description):
#     title = lobdata['name']
#     team1 = lobdata['team1']
#     team2 = lobdata['team2']
#     players = [lobdata['players']]
#     description = "### `LOBBY`"
#     field1n = "Host"
#     host = bot.load_character(lobdata['host'], lobdata['colony'])
#     equipped = "`None`"
#     ct = old_techniques.get_cursed_technique(host.technique)
#     if len(host.equipment) > 0:
#         equipped = "`" + ", ".join(host.equipment) + "`"
#     field1v = f"**{host.name}**"
#     player_names = []
#     thumbnail = bot.user.avatar.url

#     for p in players[0]:
#         char = bot.load_character(p, lobdata['colony'])
#         p_ce = ce_bar(char.ce, char.max_ce)
#         p_tech = old_techniques.get_cursed_technique(char.technique)
#         equipped = "`None`"
#         if len(char.equipment) > 0:
#             equipped = "`" + ", ".join(char.equipment) + "`"
#         player_names.append(
#             f"\n**PLAYER:** `{char.name}`\n**RANK:** `{char.get_grade()}`\n**CT:** `{char.technique}` {p_tech.emote}\n**CE POOL:** <a:blueflames:1279971716382326804> `{char.max_ce}`\n**EQUIP:** {equipped}\n"
#         )
#     field2n = "Players"
#     field2v = "\n".join(player_names)
#     field3n = None
#     field4n = None
#     field3v = None
#     field4v = None
#     if team1:
#         field3n = "Team A"
#         team1_names = []
#         for p in team1:
#             p = bot.load_character(p)
#             team1_names.append(p.name)
#         field3v = "\n".join(team1_names)
#     if team2:
#         field4n = "Team B"
#         team2_names = []
#         for p in team2:
#             p = bot.load_character(p)
#             team2_names.append(p.name)
#         field4v = "\n".join(team2_names)
#     embed = make_embed(title,
#                        description,
#                        thumbnail,
#                        field1_name=field1n,
#                        field1_value=field1v,
#                        field2_name=field2n,
#                        field2_value=field2v,
#                        field3_name=field3n,
#                        field3_value=field3v,
#                        field4_name=field4n,
#                        field4_value=field4v,
#                        line=False)
#     return embed


# def invite_embed(bot, lobby):
#     colony = dynamo.read_colony(lobby['colony'])
#     member_list = []
#     for m in colony['members']:
#         player = bot.load_character(m, lobby['colony'])
#         member_list.append(player.name)
#     description = "```" + "\n".join(member_list) + "```"
#     embed = make_embed('Invite Players', description, bot.user.avatar.url)
#     return embed


# def host_check(user, colony):
#     lobby = dynamo.read_lobby(user, colony)
#     if lobby:
#         return True
#     else:
#         return False


# async def pvp_fight(bot, lob, targets, msg):
#     player = bot.load_character(lob['turn'], lob['colony'])
#     title = lob['name']
#     description = "### Choose your `target`"
#     field1n = 'PLAYER'
#     tech = old_techniques.get_cursed_technique(player.technique)
#     field1v = f"**NAME:** `{player.name}`\n**RANK:** `{player.get_grade()}`\n**CT:** `{player.technique}` {tech.emote}\n**CE RESERVES:** `{player.max_ce}` <a:blueflames:1279971716382326804>"
#     field2n = 'TARGETS'
#     target_list = []
#     enemy = None
#     for e in targets:
#         if isinstance(e, game.Character):
#             enemy = bot.load_character(e.user_id, lob['colony'])
#         else:
#             enemy = bot.load_character(e, lob['colony'])
#         target_list.append(f"**NAME:**`{enemy.name}`\n**RANK:**`{enemy.get_grade()}`\n**CE RESERVES:** `{player.max_ce}` <a:blueflames:1279971716382326804>")
#     field2v = "\n".join(target_list)
#     embed = make_embed(title,
#                        description,
#                        field1_name=field1n,
#                        field1_value=field1v,
#                        field2_name=field2n,
#                        field2_value=field2v,
#                        line=False)
#     await msg.edit(embed=embed,
#                    view=TargetView(bot, msg, player, targets, lob['host']))


# async def pvp_embed(bot, host, players, lob, description, msg):
#     host_char = bot.load_character(host, lob['colony'])
#     host_tech = old_techniques.get_cursed_technique(host_char.technique)
#     title = lob['name']
#     team1 = lob['team1'] if 'team1' in lob else None
#     team2 = lob['team2'] if 'team2' in lob else None
#     players = lob['players']
#     neutral_players = []

#     field1n = 'HOST'
#     field1v = f"**NAME:** `{host_char.name}`\n**RANK:** `{host_char.get_grade()}`\n**CT:** `{host_char.technique}` {host_tech.emote}\n**CE RESERVES:** <a:blueflames:1279971716382326804> `{host_char.max_ce}`"
#     field2n = 'PLAYERS'
#     field2v = ''
#     player_list = []
#     for p in lob['players']:
#         char = bot.load_character(p, lob['colony'])
#         tech = old_techniques.get_cursed_technique(char.technique)
#         player_list.append(
#             f"**NAME:** `{char.name}`\n**RANK:**`{char.get_grade()}`\n**CT:** `{char.technique}` {tech.emote}\n**CE RESERVES:** <a:blueflames:1279971716382326804> `{char.max_ce}`\n"
#         )
#     field2v = '\n'.join(player_list)

#     field3n = 'TEAM A'
#     field3v = "\n"
#     if team1:
#         for t in team1:
#             char = bot.load_character(t, lob['colony'])
#             tech = old_techniques.get_cursed_technique(char.technique)
#             field3v += f"**NAME:** `{char.name}`\n**RANK:**`{char.get_grade()}`\n**CT:** `{char.technique}` {tech.emote}\n**CE RESERVES:** <a:blueflames:1279971716382326804> `{char.max_ce}`\n"
#     field4n = 'TEAM B'
#     field4v = ''
#     if team2:
#         for t in team2:
#             char = bot.load_character(t, lob['colony'])
#             tech = old_techniques.get_cursed_technique(char.technique)
#             field4v += f"**NAME:** `{char.name}`\n**RANK:**`{char.get_grade()}`\n**CT:** `{char.technique}` {tech.emote}\n**CE RESERVES:** <a:blueflames:1279971716382326804> `{char.max_ce}`\n"
#     embed = make_embed(lob['name'],
#                        description,
#                        bot.user.avatar.url,
#                        field1_name=field1n,
#                        field1_value=field1v,
#                        field2_name=field2n,
#                        field2_value=field2v,
#                        field3_name=field3n,
#                        field3_value=field3v,
#                        field4_name=field4n,
#                        field4_value=field4v,
#                        line=False)
#     await msg.edit(embed=embed, view=PVPview(bot, lob, msg))


# async def battle_info(bot,
#                       player,
#                       enemy,
#                       description,
#                       msg,
#                       targets,
#                       host,
#                       title=None,
#                       author=None):
#     try:
#         if isinstance(enemy, game.Actor):
#             e_name = enemy.name
#         else:
#             enemy = bot.load_character(enemy, player.colony)
#             e_name = enemy.name
#         player.enemy = e_name
#         player.mode = game.GameMode.PVE
#         ready, xp_needed = player.ready_level_up()
#         t = old_techniques.get_cursed_technique(player.technique)
#         ct_name = t.name
#         if "_" in ct_name:
#             ct_name = t.name.replace("_", " ")
#         player_health = healthbar(player.hp, player.max_hp)
#         player_ce = ce_bar(player.ce, player.max_ce)
#         field1n = f"**{player.name}**"
#         field2n = f"**{enemy.name}**"
#         field1v = f"**HP:** {player_health} `[{player.hp}/{player.max_hp}]` \n**CE:** {player_ce} `[{player.ce}/{player.max_ce}]`\n**IMBUED:** `{player.imbued}`\n**STR:** `{player.attack}`\n**SPD:** `{player.speed}`\n**DEF:** `{player.defense}`\n**CT:** `{ct_name}` {t.emote}"
#         field2v = None
#         if isinstance(enemy, game.Character):
#             enemy_ce = ce_bar(enemy.ce, enemy.max_ce)
#             enemy_hp = healthbar(enemy.hp, enemy.max_hp)
#             enemy_ct = old_techniques.get_cursed_technique(enemy.technique)
#             field2v = f"**HP:** {enemy_hp} `[{enemy.hp}/{enemy.max_hp}]` \n**CE:** {enemy_ce} `[{enemy.ce}/{enemy.max_ce}]`\n**STR:** `{enemy.attack}`\n**SPD:** `{enemy.speed}`\n**DEF:** `{enemy.defense}`\n**CT:** `{enemy.technique}` {enemy_ct.emote}"
#         else:
#             field2v = f"**HP:** {healthbar(enemy.hp, enemy.max_hp)}\n**Strength:** `{enemy.attack}`\n**Defense:** `{enemy.defense}`\n**Speed:** `{enemy.speed}`"
#         lob = dynamo.read_lobby(host, player.colony)
#         title = lob['name']
#         embed = make_embed(title,
#                            description,
#                            bot.user.avatar.url,
#                            field1_name=field1n,
#                            field1_value=field1v,
#                            field2_name=field2n,
#                            field2_value=field2v)
#         if ready:
#             player.level_up(xp_needed)
#             embed.set_footer(
#                 text=
#                 f"Leveled up! LEVEL: {player.level}   XP: {player.xp}/{xp_needed}"
#             )
#         embed.set_footer(text=f"{player.name}'s XP: {player.xp}/{xp_needed}")
#         if author:
#             embed.set_author(name=author.display_name,
#                              url=author.display_avatar.url)
#         if targets:
#             await msg.edit(embed=embed,
#                            view=BattleButtons(bot, msg, player, enemy, targets,
#                                               host, t))
#             return
#         else:
#             enemies = player.pve(player.colony)
#             await msg.edit(embed=embed,
#                            view=TargetView(bot, msg, player, enemies, host))
#             return

#     except Exception as e:
#         print(e)
#         traceback.print_exc()


# async def pve_embed(bot, msg, enemy, player, host_id, avatar):
#     try:
#         if not enemy:
#             ("Error choosing enemy")
#             return
#         player.mode = game.GameMode.PVE
#         player.ce = player.max_ce
#         player.hp = player.max_hp
#         player.imbued = 0
#         player.save_to_db()
#         lobdata = dynamo.read_lobby(host_id, player.colony)
#         description = f"### Select an Opponent!\n### `{player.name}'s turn`"
#         t = old_techniques.get_cursed_technique(player.technique)
#         ct_name = player.technique
#         enemy_names = []
#         if isinstance(enemy, list):
#             for e in enemy:
#                 if isinstance(e, game.Character):
#                     enemy_names.append(e.name)
           
#                 elif isinstance(e, game.Enemy):
#                     enemy_names.append(e.name)
              
#                 elif isinstance(e, dict):
#                     enemy_names.append(e['name'])
#                 elif isinstance(e, str):
#                     enemy_names.append(e)
#                 elif isinstance(e, int):
#                     enemy_char = bot.load_character(e, player.colony)
#                     enemy_names.append(enemy_char.name)
    
    
#         elif isinstance(enemy, dict):
#             enemy_names = [enemy['name']]
            
#         else:
#             enemy_names = [enemy]
                           
#         ready, xp_needed = player.ready_level_up(
#         )  #get leveling data for xp field
#         if ready:
#             player.level_up(xp_needed)
#             channel = msg.channel
#             await channel.send(
#                 f"`{player.name} has leveled up to {player.level}`")
#         player_health = healthbar(player.hp, player.max_hp)
#         player_ce = ce_bar(player.ce, player.max_ce)
#         field1_name = "**Enemy Team**"
#         field1_value = "\n".join(enemy_names)
#         field2_name = f"{player.name}"
#         grade = player.get_grade()
#         field2_value = f"**Rank:** `{grade}` \n**HP:** {player_health}\n**CE Reserves:** {player_ce}\n**Strength:** `{player.attack}`\n**Speed:** `{player.speed}`\n**CT:** {t.emote} `{ct_name}`\n**Imbued:** `{player.imbued}`\n**XP:** `{player.xp}/{xp_needed}`"
#         thumb = avatar
#         lobdata = dynamo.read_lobby(host_id, player.colony)
#         title = f"{lobdata['name']}"
        
#         embed = make_embed(title,
#                            description,
#                            thumbnail=thumb,
#                            field1_name=field1_name,
#                            field1_value=field1_value,
#                            field2_name=field2_name,
#                            field2_value=field2_value)
        
#         enemy_list = []
#         if enemy:
#             if isinstance(enemy, list):
#                 for e in enemy:
#                     if isinstance(e, int):
#                         char = bot.load_character(e, player.colony)
#                         diction = char.to_dict()
#                         enemy_list.append(diction)
#                     elif isinstance(e, game.Enemy):
#                         diction = e.to_dict()
#                         enemy_list.append(diction)
#                     elif isinstance(e, game.Character):
#                         diction = e.to_dict()
#                         enemy_list.append(diction)
                        
#                 lobdata['targets'] = enemy_list
#                 print(f"saving target to lobby : {lobdata['targets']}")
#                 dynamo.save_lobby(host_id,
#                                       player.colony,
#                                       lobdata['name'],
#                                       lobdata['players'],
#                                       0,
#                                       targets=lobdata['targets'])
                
#                 await msg.edit(embed=embed,
#                                view=TargetView(bot, msg, player, enemy,
#                                                host_id))
#                 return
#             else:
#                 lobdata['targets'] = [enemy.to_dict()]
#                 print(f"saving target to lobby : {lobdata['targets']}")
#                 dynamo.save_lobby(host_id,
#                                       player.colony,
#                                       lobdata['name'],
#                                       lobdata['players'],
#                                       0,
#                                       targets=lobdata['targets'])
#                 await msg.edit(embed=embed,
#                                view=TargetView(bot, msg, player, enemy,
#                                                host_id))
#                 return
#         else:
#             await make_lobby_embed(bot, lobdata, description)

#     except Exception as e:
#         #this sends any errors to the console ending the try, except loop
#         traceback.print_exc()


# async def domain_embed(bot,
#                        msg,
#                        domain,
#                        results,
#                        player,
#                        next_targets,
#                        lob,
#                        target=None,
#                        targets=None):
#     title = lob['name']
#     outcome = results[1]
#     dmg = results[0]
#     killed = results[2]
#     marks = results[3]
#     tech = old_techniques.get_cursed_technique(player.technique)
#     print(f"Domain: {domain}")
#     description = f"## DOMAIN EXPANSION : {domain}\n"
#     soul_dmg = 0
#     soul_def = 0
#     drain = None
#     stack = None
#     stun = None
#     sure_hit = tech.attack[domain]['domain']
#     print(f"Sure hit: {sure_hit}")
#     if 'NA lvl' in outcome:
#         description = f"### `{player.name} misfired their `DOMAIN EXPANSION: {domain}` due to low experience"
#     if 'soul' in sure_hit.keys():
#         soul_dmg = sure_hit['soul']
#     if 'soul def' in sure_hit.keys():
#         soul_def = sure_hit['soul def']
#     if 'drain' in sure_hit.keys():
#         drain = sure_hit['drain']
#     if 'stack' in sure_hit.keys():
#         stack = sure_hit['stack']
#     if 'stun' in sure_hit.keys():
#         stun = sure_hit['stun']
#     if 'hit' in outcome:
#         description += f"### `{player.name}` used their sure hit `{sure_hit['name']}`\n"
#         description += f"`{dmg} damage dealt`\n"
#         if soul_dmg:
#             description += f"`{soul_dmg} soul damage dealt`\n"
#         if drain:
#             description += f"`{drain} poison damage dealt`\n"
#         if stack:
#             description += f"`{stack} projection stacks made`\n"
#         if stun:
#             description += f"`{target.name} stunned for {stun} turns`\n"
#         if soul_def:
#             description += f"`{target.defense} soul defense: {soul_def}`\n"
            
#     if 'negate' in outcome:
#         description += f"### `{player.name}'s {domain}` sure hit negated by `{target.defense}`\n"

#     if 'tank' in outcome:
#         description += f"### `{target.name}` TANKS `{player.name}`'s sure hit `{domain}`\n"
#         description += f"`{dmg} damage tanked`\n"

#         if soul_dmg <= 0:
#             description += f"`{soul_dmg} soul damage tanked`\n"
#         else:
#             description += f"`{soul_dmg} soul damage dealt`"
#     if killed:
#         target_dict = target.to_dict()
#         if target in next_targets:
#             next_targets.remove(target)
#         elif target_dict in next_targets:
#             next_targets.remove(target_dict)
#         if isinstance(target, game.Enemy):
#             if next_targets:
#                 new_lobby = turn(player.user_id, lob)
#                 new_player = bot.load_character(new_lobby['turn'], new_lobby['colony'])
#                 embed = make_embed(new_lobby['name'], description, bot.user.avatar.url)
#                 await msg.edit(embed=embed, view=None)
#                 await asyncio.sleep(6)
#                 await pve_embed(bot, msg, next_targets, new_player, lob['host'],
#                                     bot.user.avatar.url)
#                 return
                
#             else:
#                 await asyncio.sleep(6)
#                 description = f"### VICTORY!\n`No targets left RETURNED to lobby`"
#                 new_lobby = turn(player.user_id, lob)
#                 embed = await make_lobby_embed(bot, new_lobby, description)
#                 await msg.edit(embed=embed, view=LobbyView(bot, msg, new_lobby['players'], new_lobby['host']))
#                 return
#         if isinstance(target, game.Character):
#             if next_targets:
#                 new_lobby = turn(player.user_id, lob)
#                 new_player = bot.load_character(new_lobby['turn'], new_lobby['colony'])
#                 embed = make_embed(new_lobby['name'], description, bot.user.avatar.url)
#                 await msg.edit(embed=embed, view=None)
#                 await asyncio.sleep(6)
#                 await pvp_embed(bot, new_lobby['host'], new_lobby['players'], new_lobby, description, msg)
#                 return
#             else:
#                 new_lobby = turn(player, lob)
#                 description = f"### `All enemies defeated`\n### `Returning to main lobby`"
#                 await asyncio.sleep(6)
#                 embed = await make_lobby_embed(bot, new_lobby, description)
#                 await msg.edit(embed=embed, view=LobbyView(bot, msg, new_lobby['players'], new_lobby['host']))
        
            

   

# async def technique_embed(bot, tech_name, result, msg, player, lobdata, target,
#                           next_targets, host):
#     try:
#         dmg = result[0]
#         outcome = result[1]
#         killed = result[2]
#         mark = result[3]
#         soul_dmg = 0
#         drain = 0
#         stun = 0
#         t = old_techniques.get_cursed_technique(player.technique)
#         description = f"### Required player CE for technique use: `{t.ce_cost}`"
#         if 'NA ce' in outcome:
#             description = f"### `{player.name}` does not have enough CE to use `{player.technique} : {tech_name}` {t.emote}\n`Skipping to next turn`"

#         if 'NA imbue' in outcome:
#             description = f"### `{player.name}` misfired `{player.technique} : {tech_name}` {t.emote} because they did not imbue enough CE!\n`Skipping to next turn`"

#         if 'NA lvl' in outcome:
#             description = f"### `{player.name}` fumbled `{player.technique} : {tech_name}` {t.emote} due to low experience\n`Skipping to next turn`"

#         if 'counter' in outcome:
#             description = f"### `{target.name}` used `{target.defense}` to counter attack `{player.name}'s {tech_name}` using `{target.defense}`"
#             description += f"\n### `{dmg} dmg` dealt to {player.name}"
#             if mark:
#                 if 'negate' in mark:
#                     description += f"\n`{target.name} negated {player.name}'s defense with their counter`"
#                 if 'drain' in mark:
#                     description += f"\n`{player.name} was poisoned by {target.name}`\n`{player.name} will lose {mark['drain']['dmg']} HP and CE per {mark['drain']['turn']} turns`"
#             if killed:
#                 description += f"\n### `{target.name} exorcised {player.name}`\n### XP earned: {player.xp}\n ### Culling Game Points earned: {player.cgp}"
#                 target_dict = target.to_dict()
#                 if target_dict in next_targets:
#                         next_targets.remove(target_dict)
                
#                 if target in next_targets:
#                    for t in next_targets:
#                        t_dict = t.to_dict()
#                        if t_dict == target_dict:
#                            next_targets.remove(t)
#                            break
                
#                 lobdata['targets'] = [t.to_dict() for t in next_targets]
#                 if isinstance(target, game.Enemy):
#                     if next_targets:
#                         new_lobby = turn(player, lobdata)
#                         new_player = bot.load_character(new_lobby['turn'], new_lobby['colony'])
#                         embed = make_embed(new_lobby['name'], description, bot.user.avatar.thumbnail)
#                         await msg.edit(embed=embed, view=None)
#                         await asyncio.sleep(6)
#                         await pve_embed(bot, msg, next_targets, new_player, host,
#                                             bot.user.avatar.url)
#                         return
#                     else:
#                         await asyncio.sleep(6)
#                         description = f"### VICTORY!\n`No targets left RETURNED to lobby`"
#                         new_lobby = turn(player.user_id, lobdata)
#                         embed = await make_lobby_embed(bot, new_lobby, description)
#                         await msg.edit(embed=embed, view=LobbyView(bot, msg, new_lobby['players'], new_lobby['host']))
                        
#                 elif isinstance(target, game.Character):
#                     if next_targets:
#                         new_lobby = turn(player.user_id, lobdata)
#                         new_player = bot.load_character(new_lobby['turn'], new_lobby['colony'])
#                         embed = make_embed(new_lobby['name'], description, bot.user.avatar.thumbnail)
#                         await msg.edit(embed=embed, view=None)
#                         await asyncio.sleep(6)
#                         await pvp_embed(bot, new_lobby['host'], new_lobby['players'], new_lobby, description, msg)
#                         return
#                     else:
#                         new_lobby = turn(player, lobdata)
#                         description = f"### `All enemies defeated`\n### `Returning to main lobby`"
#                         await asyncio.sleep(6)
#                         embed = await make_lobby_embed(bot, new_lobby, description)
#                         await msg.edit(embed=embed, view=LobbyView(bot, msg, new_lobby['players'], new_lobby['host']))
                        
                        
                    

#         if "hit" in outcome:
#             strings = [
#                 f'### `{player.name}:` "{player.technique} : {tech_name}"',
#                 f"### `{player.name}` hit `{target.name}` with `{player.technique} : {tech_name}` {t.emote}",
#                 f"### `{player.name}` outplayed `{target.name}` and landed `{player.technique} : {tech_name}` {t.emote}",
#                 f"### `{player.name}` used `{player.technique} : {tech_name}` {t.emote} on `{target.name}`"
#             ]
            
#             choice = random.choice(strings)
#             description = choice
#             if mark:
#                 if 'drain' in mark.keys():
#                     amount = mark['drain']
#                     if isinstance(amount, dict):
#                         amount = amount['dmg']
#                     description += f"\n### `{player.name}` poisoned `{target.name}` with `{tech_name}`\n### `{target.name}` will lose {amount} of HP per TURN`"
                    
#                 if 'stack' in mark.keys():
#                     description += f"\n### `{player.name}` landed a `Projection Stack` on `{target.name}`\n`{target.name}'s speed will be set to 0 for {mark['stack']} turns.`\n`{player.name} speed increased by {target.speed}`"
   
#             description += f"\n`{dmg} damage dealt to {target.name}`"
#             if soul_dmg > 0:
#                 description += f"\n### `{soul_dmg} soul damage dealt to {player.name}'s max HP`"
            
#             if killed:
#                 print(f"target killed: {target.name}")
#                 print(f"removing {target} from {next_targets}")
#                 target_dict = target.to_dict()
#                 for t in next_targets:
#                     if t == target:
#                         next_targets.remove(t)
#                         break

#                     elif isinstance(t, dict):
#                         if t == target_dict:
#                             next_targets.remove(t)
#                             break
                            
#                 print(f"Remaining targets:  {next_targets}")
#                 description += f"\n### `VICTORY!` <:emoji_2:1215306371541499925>\n### `{player.name}` exorcised `{target.name}`"
#                 description += f'\n### `{player.name}: "{player.victory_msg}"`'
#                 description += f"\n`{target.cgp} culling game points and {target.xp} xp earned`"
#                 player.xp += target.xp 
#                 player.cgp += target.cgp
#                 player.save_to_db()
#                 if isinstance(target, game.Character):
#                     dynamo.delete_from_colony(player.colony, 'members', target.user_id)
  
                     
                

#         elif "tank" in outcome:
#             description = f"\n### `{target.name}` completey tanked `{player.name}'s {tech_name}` using `{target.defense}`\n### `{dmg}` damage tanked"
#             if soul_dmg > 0:
#                 description += f"\n### `{soul_dmg}` soul damage tanked"

#         elif 'miss' in outcome:
#             description = f"\n### `{player.name}` missed their attack `{player.technique} : {tech_name}` on `{target.name}` because of `{target.defense}`"
#             if mark:
#                 description += f"\n`attack speed: {mark['atk speed']}`\n`defense speed: {mark['def speed']}`"
                
#         if next_targets:
        
#             embed = make_embed(lobdata['name'], description,
#                                bot.user.avatar.url)
            
#             new_target = random.choice(next_targets)
#             await msg.edit(embed=embed, view=None)
#             if isinstance(new_target, game.Enemy):
#                 tech = old_techniques.Techniques(**new_target.technique)
                
#                 attack = random.choice([k for k in tech.attack.keys()])
#                 atk_dict = tech.attack[attack]
#                 def_name = None
#                 if player.defense:
#                     def_name = player.defense
#                 else:
#                     if player.technique == "Heavenly Restriction":
#                         player.defense="Heavenly Body"
#                         def_name = 'Heavenly Body'
#                     else:
#                         player.defense="CE"
#                         def_name = 'CE'
#                 if " " in def_name:
#                     def_name.replace(" ", "_")
#                 pt = old_techniques.get_cursed_technique(player.technique)
#                 def_func = getattr(pt, def_name.lower())
#                 results = def_func(target, player, atk_dict)
#                 await asyncio.sleep(5)
#                 await ai_turn(bot, results, attack, player, new_target, msg, lobdata)
#                 return
#             elif isinstance(new_target, game.Character):
#                 new_lob = turn(player.user_id, lobdata)
#                 await asyncio.sleep(6)
#                 await pvp_fight(bot, new_lob, next_targets, msg)
#                 return
#             elif isinstance(new_target, dict):
#                 new_target = game.Enemy(**new_target)
#                 tech = old_techniques.Techniques(**new_target.technique)
#                 attack = random.choice([k for k in tech.attack.keys()])
#                 atk_dict = tech.attack[attack]
#                 def_name = None
#                 if player.defense:
#                     def_name = player.defense
#                 else:
#                     if player.technique == "Heavenly Restriction":
#                         player.defense="Heavenly Body"
#                         def_name = 'Heavenly Body'
#                     else:
#                         player.defense="CE"
#                         def_name = 'CE'
#                 if " " in def_name:
#                     def_name.replace(" ", "_")
#                 pt = old_techniques.get_cursed_technique(player.technique)
#                 def_func = getattr(pt, def_name.lower())
#                 results = def_func(target, player, atk_dict)
#                 await asyncio.sleep(5)
#                 await ai_turn(bot, results, attack, player, new_target, msg, lobdata)
#                 return
#             elif isinstance(new_target, int):
#                 new_lob = turn(player.user_id, lobdata)
#                 await asyncio.sleep(6)
#                 await pvp_fight(bot, new_lob, new_lob['targets'], msg)
#                 return
                
            
#         else:
#             await asyncio.sleep(6)
#             description = f"### VICTORY!\n`returned to lobby`"
#             embed = await make_lobby_embed(bot, lobdata, description)
#             await msg.edit(embed=embed, view=LobbyView(bot, msg,lobdata['players'], lobdata['host']))
#             return
   
#     except Exception as e:
#         traceback.print_exc()


# async def aoe_embed(bot,
#                     attack,
#                     player,
#                     msg,
#                     targets,
#                     lobdata,
#                     new_msg,
#                     chosen=None, defense=None):
#     print(targets)
#     title = lobdata['name']
#     tech = old_techniques.get_cursed_technique(player.technique)
#     marks = lobdata['mark']
#     attack_data = tech.attack[attack]
#     current_targets = []
#     if chosen:
#         for t in chosen:
#             if isinstance(t, str):
#                 for e in game.Enemy.__subclasses__():
#                     if e().name == chosen:
#                         current_targets.append(e())
#                         break
#             elif isinstance(t, int):
#                 char = bot.load_character(t, lobdata['colony'])
#                 current_targets.append(char)
#             elif isinstance(t, game.Actor):
#                 current_targets.append(t)
#             elif isinstance(t, dict):
#                 for e in game.Enemy.__subclasses__():
#                     if e().name == t['name']:
#                         current_targets.append(game.Enemy(**t))
#                         break
#                 if 'victory_msg' in t.keys():
#                      current_targets.append(game.Character(**t))
                
                        
                

#         if marks:
#             print(f"Marks: {marks}")
#             if 'aoe' in marks.keys():
#                 if attack in marks['aoe'].keys():
#                     if 'target' in marks['aoe'][attack].keys():
#                          marks['aoe'][attack]['target'].append(t.to_dict() for t in current_targets)
#                     else:
#                         marks['aoe'][attack]['target'] = [t.to_dict() for t in current_targets]
                            
#                 else:
#                     marks['aoe'][attack] = {'target' : [t.to_dict() for t in current_targets]}
                    
                     
#             else:
#                 marks['aoe'] = {attack : {'target' : [t.to_dict() for t in current_targets]}} 
                  
                
#         else:
#                 marks = {
#                     'aoe': {
#                         attack: {
#                             'target': [t.to_dict() for t in current_targets]
#                         }
#                     }
#                 }

#     field1n = '**Selected Targets**'
#     field1v_str = "\n".join(t.name for t in current_targets)
#     field1v_str_start = "`"
#     field1v_str_end = "`"
#     field1v = field1v_str_start + field1v_str + field1v_str_end
#     max_length = attack_data['aoe']
#     target_opts = enumerate(targets)
#     target_list = []
#     for idx, target in target_opts:
#         if isinstance(target, game.Actor):
#             target_list.append(f"{idx +1})  {target.name}")
#         elif isinstance(target, dict):
#             target_list.append(f"{idx + 1}) {target['name']}")
#     target_names = [t for t in target_list]
#     for t in targets:
#         if isinstance(t, dict):
#             pass
#         elif isinstance(t, int):
#             tar_obj = bot.load_character(t, lobdata['colony'])
#             targets.remove(t)
         
#         else:
#             targets.remove(t)

#     target_str = "\n".join(target_names) if len(
#         target_list) > 0 else "All enemies selected!"
#     dynamo.save_lobby(lobdata['host'], lobdata['colony'], lobdata['name'], lobdata['players'], lobdata['t_count'], targets=[t for t in targets], mark = marks)
#     description = f"### Launching AOE attack `{player.technique} : {attack}`\n`Choose a target ({len(current_targets)}/{max_length}):`\n ```{target_str}```"
#     print(f"Selected targets {current_targets}")
#     embed = make_embed(title=title,
#                        description=description,
#                        thumbnail=bot.user.avatar.url,
#                        field1_name=field1n,
#                        field1_value=field1v)
    
#     await new_msg.edit(embed=embed,
#                        view=AOEView(bot, attack, targets, attack_data['aoe'],
#                                     current_targets, msg, lobdata, player,
#                                     new_msg))


# async def aoe_results(bot, msg, technique, move, targets, results, lob,
#                       player):
#     tech = old_techniques.get_cursed_technique(player.technique)
#     description = None
#     is_enemy = False    
#     mark=None
#     if lob['mark']:
#         mark = lob['mark']
#     if move == 'attack':

#         if player.name in old_techniques.enemy_techniques:
#             is_enemy = True

#         if 'NA ce' in results:
#             description = f"### `{player.name}` does not have enough CE to use `{player.technique} : {technique}`\n`Skipping to next turn`"

            
#         elif 'NA imbue' in results:
#             description = f"### `{player.name}` misfired `{player.technique} : {technique}` because they did not imbue enough CE!\n`Skipping to next turn`"

            
#         elif 'NA lvl' in results:
#             description = f"### `{player.name}` fumbled `{player.technique} : {technique}` {tech.emote} due to low experience"

    

#         else:
#             description = ""
#             print(f'Aoe results: {results}')
#             for t in results:
#                 if is_enemy:
#                     result_list = []
#                     for e in targets:
#                         enemy = bot.load_character(e)
#                         dmg = results[0]
#                         outcome = results[1]
#                         killed = results[2]
#                         marks = results[3]
#                         if 'hit' in outcome:
#                             description = f"### `{enemy.name}` hit by `{player.technique} : {technique}`"

#                 else:
#                     outcome = t['results'][1]
#                     dmg = t['results'][0]
#                     killed = t['results'][2]
#                     mark = t['results'][3]
#                     tango = game.Enemy(**t['target'])
#                     results = t['results']

#                     if 'hit' in outcome:
#                         description += f"\n### `{tango.name}` hit by `{player.technique} : {technique}` {tech.emote}"
#                         description += f"\n`{dmg} damage dealt`"
#                         if mark:
#                             if 'soul' in mark.keys():
#                                 description += f"\n`{str(mark['soul'])} soul damage dealt`"
#                             if 'drain' in mark.keys():
#                                 description += f"\n`{mark['drain']} poison damage dealt`"
#                             if 'stack' in mark.keys():
#                                 description += f"\n`{str(mark['stack'])} projection stacks`"
#                         if killed:
#                             description += f"\n### `VICTORY!`\n`{tango.name} was exorcised`\n`{player.name} earned {tango.xp} xp and {tango.cgp} game points`"
#                             player.xp += tango.xp
#                             player.cgp += tango.cgp
#                             player.save_to_db()
#                             player.ce = player.max_ce
#                             target_list = []
#                             for t in targets:
#                                 if isinstance(t, dict):
#                                     target_list.append(t)
#                                 elif isinstance(t, game.Enemy):
#                                     target_list.append(t.to_dict())
#                                 elif isinstance(t, game.Character):
#                                     target_list.append(t.to_dict())
#                             targets = target_list
                            

#                     if 'tank' in outcome:
#                         description += f"\n### `{tango.name}` tanked `{player.technique} : {technique}`"

#                     if 'counter' in outcome:
#                         description += f"\n### `{tango.name}` countered `{player.technique}:{technique}`"
#                     if 'miss' in outcome:
#                         description += f"\n### `{tango.name}` dodged `{player.technique}:{technique}`"
                    
#         description += f'\n### `{player.name}:` "**{player.victory_msg}**"'
#         title = lob['name']
#         embed = make_embed(title,
#                            description,
#                            thumbnail=bot.user.avatar.url,
#                            line=False)

#         await msg.edit(embed=embed, view=None)
#         await asyncio.sleep(5)

#         next_target = None
#         print(f"\ntargets remaining:\n{targets}")
#         if targets:
#             next_target = random.choice([t for t in targets])
#         if next_target:
#             if isinstance(next_target, game.Enemy):
#                 technique = old_techniques.Techniques(**next_target.technique)
#                 attack = random.choice([k for k in technique.attack.keys()])
#                 if player.defense is None:
#                     player.defense = 'CE'
#                 results = player.use_technique(player.defense,
#                                                'defense',
#                                                attack=technique.attack[attack])
#                 await ai_turn(bot, results, attack, player, next_target, msg,
#                               lob)
#             else:
#                 if isinstance(next_target, game.Character):
#                     new_lob = turn(player.user_id, lob)
#                     await pvp_fight(bot, new_lob, new_lob['targets'], msg)
                
#         else:
#             embed = await make_lobby_embed(bot, lob, description)
#             await msg.edit(embed=embed,
#                            view=LobbyView(bot, msg, lob['players'],
#                                           lob['host']))


# async def ai_turn(bot, outcome, attack_name, target, ai, msg, lobdata):
#     try:
#         player = bot.load_character(target.user_id, target.colony)
#         print(player)
#         description = ""
#         dmg = outcome[0]
#         result = outcome[1]
#         killed = outcome[2]
#         mark = {}
#         if len(outcome) > 3:
#             mark = outcome[3]
#         soul_dmg = 0
#         aoe = False
#         attack = ai.technique['attack'][attack_name]
#         if 'NA lvl' in result:
#             description = f"### `{target.name}` did not have the experience to use `{target.defense}`\n"
#             print('na lvl')
#         elif 'NA imbue' in result:
#             target_tech = old_techniques.get_cursed_technique(target.defense)
#             description = f"### `{target.name}` did not have enough CE imbued to use `{target.defense}`\n`{target.defense} requires {target_tech.defense[target.defense]['imbue cost']}`\n"
#             if 'soul' in attack:
#                 dmg += attack['soul']
#                 target.max_hp -= attack['soul']
#                 description += f"### `{target.name}`'s soul took `{attack['soul']}` damage\n"

#         elif 'NA ce' in result:
#             attack = ai.technique['attack'][attack_name].keys()
#             print("na ce")

#             description = f"### `{target.name}` did not have enough CE to use `{target.defense}`\n"
        
        

#         else:
#             if 'soul' in mark.keys():
#                 soul_dmg = mark['soul']

#             if 'aoe' in mark.keys():
#                 aoe = True


#         if aoe == True:
#             number = ai.t.attack[attack_name]['aoe']
#             target_list = [target.user_id]
#             while len(target_list) < number:
#                 if len(lobdata['players']) > 1:
#                     for p in lobdata['players']:
#                         target_list.append(p)
#                     else:
#                         break
#             print(f"{ai} targeting the following player list {target_list}")
     
#         if 'counter' in result:
#             description = f"### `{target.name}` used `{target.technique} : {target.defense}` to counter attack `{ai.name}'s {attack_name}`"
#             description += f"### `{target.name} did {dmg} damage to {ai.name}`"
#             if 'soul' in mark:
#                 description += f"### `{ai.name}`'s soul took `{mark['soul']}` damage\n"
        
            
#             if killed:
#                 description += f"\n### `{target.name} exorcised {ai.name}`\n### XP earned: {ai.xp}\n ### Culling Game Points earned: {ai.cgp}"
                
#         if "hit" in result:
#             if 'Physical' in attack_name:
#                 strings = [
#                     f"### `{ai.name}` landed `punches` on `{target.name}`",
#                     f"### `{ai.name}` landed `kicks` on `{target.name}`",
#                     f"### `{ai.name}` landed a `spinning back kick` on `{target.name}`",
#                     f"### `{ai.name}` landed an `uppercut` on `{target.name}`"
#                 ]
#                 if 'soul' in attack:
#                     description += f"### `{target.name}`'s soul took `{attack['soul']}` damage\n"

#                 if soul_dmg > 0:
#                     strings.append(f"\n### `{soul_dmg} soul damage dealt`")
#                 choice = random.choice(strings)
#                 description = choice
#             else:
#                 strings = [
#                     f"### `{ai.name}` used `{attack_name}` on `{target.name}`"
#                 ]
#                 if attack_name == "Electric Rod":
#                     strings.append(
#                         f"### `{ai.name}` landed their sure hit attack `{attack_name}` on `{target.name}`"
#                     )
#                 if attack_name == "Snow Calm":
#                     strings.append(
#                         f"### `{ai.name}` froze `{target.name}` with  `{attack_name}`"
#                     )

#                 choice = random.choice(strings)

#                 if 'drain' in mark.keys():
#                     amount = mark['drain']
#                     for k in mark.keys():
#                         amount = mark[k]
#                     choice = (
#                         f"### `{ai.name}` poisoned `{target.name}` with `{attack_name}`\n`{target.name} will lose {amount} of CE and HP per TURN`"
#                     )
#                 if 'domain' in attack.keys():
#                     choice = (
#                         f"### `{ai.name}` used `DOMAIN EXPANSION: {attack_name}` on `{target.name}`"
#                     )

#                 description = choice

#                 if soul_dmg > 0:
#                     description += f"\n### `{soul_dmg} soul damage dealt`"

#             if killed:
#                 description += f"\n### VICTORY! <:emoji_2:1215306371541499925>\n### `{ai.name}` exorcised `{target.name}` using {attack_name}\n### Stand proud `{target.name}` you were strong."
#                 description += f"\n`{target.name} has died...`"
#                 dynamo.delete_from_lobby(lobdata['host'],
#                                              lobdata['colony'], target.user_id)
#                 dynamo.delete_from_colony(target.colony, 'members',
#                                               target.user_id)
#                 embed = make_embed(lobdata['name'], description,
#                                    bot.user.avatar.url)
#                 await msg.edit(embed=embed, view=None)
#                 await asyncio.sleep(2)
#                 if lobdata['players']:
#                     user = lobdata['players'][0]
#                     player = bot.load_character(user, lobdata['colony'])
#                     await pve_embed(bot, msg, ai, player, lobdata['host'],
#                                     bot.user.avatar.url)
#                     return
#                 else:
#                     description = "### GAME OVER"
#                     embed = make_embed(lobdata['name'], description,
#                                        bot.user.avatar.url)
#                     await msg.edit(embed=embed, view=None)
#                     return

#         elif "tank" in result:
#             description = f"\n### `{target.name}` completey tanked `{ai.name}'s {attack_name}`\n### `{dmg}` damage tanked"
#             if soul_dmg > 0:
#                 description += f"\n### `{soul_dmg}` soul damage tanked"

#         elif "miss" in result:
#             atk_speed = mark['atk speed']
#             def_speed = mark['def speed']
#             description = f"\n### `{ai.name}` missed their `{attack_name}` attack\n### `{attack_name}`attack speed: `{atk_speed}`\n### `{target.defense}` defense speed: `{def_speed}`"

#         await battle_info(bot,
#                           target,
#                           ai,
#                           description,
#                           msg,
#                           lobdata['targets'],
#                           lobdata['host'],
#                           title=lobdata['name'])

#     except Exception as e:
#         (f"Error in ai_turn function: {e}")
#         traceback.print_exc()



#The following class is an example of the UI View using different classes and the add_item method of discords UI class
# class PVPview(discord.ui.View):

#     def __init__(self, bot, lob, msg):
#         self.bot = bot
#         self.lob = lob
#         self.msg = msg
#         super().__init__(timeout=None)

#     @discord.ui.button(label='A', style=discord.ButtonStyle.green)
#     async def a(self, interaction: discord.Interaction,
#                 button: discord.Button):
#         if self.lob['team2']:
#             if interaction.user.id in self.lob['team2']:
#                 self.lob['team2'].remove(interaction.user.id)
#         if self.lob['team1']:
#             if interaction.user.id in self.lob['players']:
#                 self.lob['players'].remove(interaction.user.id)
#             if interaction.user.id not in self.lob['team1']:
#                 team = self.lob['team1']
#                 team.append(interaction.user.id)
#                 self.lob['team1'] = team
#                 char = self.bot.load_character(interaction.user.id,
#                                                interaction.guild_id)
#                 description = f"### `{char.name} joined team A`"
#                 await pvp_embed(self.bot, self.lob['host'],
#                                 self.lob['players'], self.lob, description,
#                                 self.msg)
#                 return
#             else:
#                 await interaction.response.send_message(
#                     "You are already in team A", ephemeral=True)
#                 return
#         else:
#             if interaction.user.id in self.lob['players']:
#                 self.lob['players'].remove(interaction.user.id)
#             team = []
#             team.append(interaction.user.id)
#             self.lob['team1'] = team
#             char = self.bot.load_character(interaction.user.id,
#                                            interaction.guild_id)
#             description = f"### `{char.name} joined team A`"
#             dynamo.save_lobby(self.lob['host'],
#                                   self.lob['colony'],
#                                   self.lob['name'],
#                                   self.lob['players'],
#                                   self.lob['t_count'],
#                                   team1=self.lob['team1'],
#                                   team2=self.lob['team2'])
#             await pvp_embed(self.bot, self.lob['host'], self.lob['players'],
#                             self.lob, description, self.msg)

#     @discord.ui.button(label='B', style=discord.ButtonStyle.blurple)
#     async def b(self, interaction: discord.Interaction,
#                 button: discord.Button):
#         if self.lob['team1']:
#             if interaction.user.id in self.lob['team1']:
#                 self.lob['team1'].remove(interaction.user.id)
#         if self.lob['team2']:
#             if interaction.user.id not in self.lob['team2']:
#                 if interaction.user.id in self.lob['players']:
#                     self.lob['players'].remove(interaction.user.id)

#                 team = self.lob['team2']

#                 team.append(interaction.user.id)

#                 self.lob['team2'] = team

#                 char = self.bot.load_character(interaction.user.id,
#                                                interaction.guild_id)
#                 description = f"### `{char.name} joined team B`"

#                 dynamo.save_lobby(self.lob['host'],
#                                       self.lob['colony'],
#                                       self.lob['name'],
#                                       self.lob['players'],
#                                       self.lob['t_count'],
#                                       team1=self.lob['team1'],
#                                       team2=self.lob['team2'])

#                 await pvp_embed(self.bot, self.lob['host'],
#                                 self.lob['players'], self.lob, description,
#                                 self.msg)
#                 return
#             else:
#                 await interaction.response.send_message(
#                     "You are already in team B", ephemeral=True)
#                 return

#         else:
#             if interaction.user.id in self.lob['players']:
#                 self.lob['players'].remove(interaction.user.id)
#             team = []
#             team.append(interaction.user.id)
#             self.lob['team2'] = team
#             char = self.bot.load_character(interaction.user.id,
#                                            interaction.guild_id)
#             description = f"### `{char.name} joined team B`"
#             await pvp_embed(self.bot, self.lob['host'], self.lob['players'],
#                             self.lob, description, self.msg)

#     @discord.ui.button(label='Start', style=discord.ButtonStyle.red)
#     async def start(self, interaction: discord.Interaction,
#                     button: discord.Button):
#         if interaction.user.id == self.lob['host']:
#             player_turn = None
#             choice = random.choice([1, 2])
#             if choice == 2:
#                 player_turn = random.choice(self.lob['team2'])
#             elif choice == 1:
#                 player_turn = random.choice(self.lob['team1'])
#             self.lob['turn'] = player_turn
#             lobby = turn(player_turn, self.lob)
#             await pvp_fight(self.bot, lobby, lobby['targets'], self.msg)


# class LobbyView(discord.ui.View):  #the lobby UI view is created to add buttons

#     def __init__(self, bot, msg, players, host_id):
#         super().__init__()
#         #add button classes to the ui view
#         self.add_item(JoinLobby(bot, msg, players, host_id))
#         self.add_item(Ready(bot, msg, players, host_id))
#         self.add_item(Lock(bot, msg, players, host_id))
#         self.add_item(Invite(bot, msg, players, host_id))
#         self.add_item(StartPVP(bot, msg, players, host_id))
#         self.add_item(StartPve(bot, msg, players, host_id))


# class Invite(discord.ui.Button):

#     def __init__(self, bot, msg, players, host_id):
#         self.bot = bot
#         self.msg = msg
#         self.players = players
#         self.host = host_id
#         super().__init__(label="Invite",
#                          style=discord.ButtonStyle.gray,
#                          emoji='📨',
#                          row=1)

#     async def callback(self, interaction: discord.Interaction):
#         lob = dynamo.read_lobby(self.host, interaction.guild.id)
#         if interaction.user.id in self.players:
#             if lob['lock'] == True:
#                 await invite_embed(self.bot, self.msg, self.players,
#                                    self.host_id)
#             else:
#                 await interaction.response.send_message(
#                     "Lobby is open/unlocked", ephemeral=True)

#         else:
#             if lob['lock']:
#                 await interaction.response.send_message(
#                     "You are not in the current lobby", ephemeral=True)
#             else:
#                 await interaction.response.send_message(
#                     "Lobby is open/unlocked", ephemeral=True)


# class Ready(discord.ui.Button):

#     def __init__(self, bot, msg, players, host_id):
#         super().__init__(label="Ready",
#                          style=discord.ButtonStyle.green,
#                          emoji='✅',
#                          row=0)
#         self.bot = bot
#         self.msg = msg
#         self.players = players
#         self.host_id = host_id

#     async def callback(self, interaction: discord.Interaction):
#         #await interaction.response.defer()
#         #await interaction.followup.send("Ready button pressed!")
#         #await interaction.response.send_message("Ready button pressed!")
#         lobby_data = dynamo.read_lobby(self.host_id, interaction.guild.id)
#         await interaction.response.defer()
#         player = interaction.user.id
#         colony = interaction.guild.id
#         ready_list = []
#         if lobby_data['ready'] is None:
#             name = self.msg.embeds[0].title
#             ready_list = [player]
#             dynamo.save_lobby(player,
#                                   colony,
#                                   name=name,
#                                   players=self.players,
#                                   t_count=0,
#                                   ready=ready_list)
#             await interaction.followup.send("You ready'd up!", ephemeral=True)
#             return
#         else:
#             ready_list = lobby_data['ready']
#             if player in ready_list:
#                 for p in ready_list:
#                     if p == player:
#                         ready_list.remove(player)
#                     lobby_data['ready'] = ready_list
#                     await interaction.followup.send("You are not ready",
#                                                     ephemeral=True)
#                     name = self.msg.embeds[0].title
#                     dynamo.save_lobby(lobby_data['host'],
#                                           colony,
#                                           player,
#                                           name,
#                                           self.players,
#                                           ready=ready_list)
#                     return
#             else:
#                 name = self.msg.embeds[0].title
#                 ready_list.append(player)
#                 dynamo.save_lobby(lobby_data['host'],
#                                       colony,
#                                       name,
#                                       self.players,
#                                       t_count=0,
#                                       ready=ready_list)
#                 await interaction.followup.send("You have ready'd up!",
#                                                 ephemeral=True)
#                 return


# class JoinLobby(discord.ui.Button):  #join the lobby button class

#     def __init__(self, bot, msg, players, host_id):
#         self.bot = bot
#         self.msg = msg
#         self.players = players
#         self.host_id = host_id
#         super().__init__(label="Join",
#                          style=discord.ButtonStyle.green,
#                          emoji='<a:join:1279966108312535182>',
#                          row=0)  #instantiating the button class

#     async def callback(self, interaction: discord.Interaction):
#         await interaction.response.defer()

#         self.disabled = True  #disable the button
#         await self.msg.edit(
#             view=LobbyView(self.bot, self.msg, self.players, self.host_id)
#         )  #we have to update the view with the disabled button or else it will still be clickable
#         await asyncio.sleep(0.75)
#         if interaction.user.id in [p for p in self.players]:
#             await interaction.followup.send("You are already in the lobby!",
#                                             ephemeral=True)
#             self.disabled = False
#             await self.msg.edit(
#                 view=LobbyView(self.bot, self.msg, self.players, self.host_id))
#             return

#         player = self.bot.load_character(interaction.user.id,
#                                          interaction.guild.id)
#         self.players.append(player.user_id)
#         lob = dynamo.read_lobby(self.host_id, player.colony)

#         if lob['locked']:
#             if interaction.user.id not in lob['invites']:
#                 await interaction.followup.send('You are not invited',
#                                                 ephemeral=True)
#                 return

#         description = f"### `{player.name}` has joined the lobby"
#         lob['players'] = self.players
#         dynamo.save_lobby(self.host_id, player.colony, lob['name'],
#                               self.players, 0)
#         embed = await make_lobby_embed(self.bot, lob, description)
#         self.disabled = False
#         await self.msg.edit(embed=embed,
#                             view=LobbyView(self.bot, self.msg, self.players,
#                                            self.host_id))


# class StartPve(discord.ui.Button):

#     def __init__(self, bot, msg, players, host_id):
#         self.bot = bot
#         self.msg = msg
#         self.players = players
#         self.host_id = host_id
#         super().__init__(label="PVE",
#                          style=discord.ButtonStyle.blurple,
#                          emoji='<:PVEstart:1279966805800124526>',
#                          row=2)

#     async def callback(self, interaction: discord.Interaction):
#         await interaction.response.defer()
#         self.disabled = True
#         logguild = await self.bot.fetch_guild(os.environ['SERVERID'])
#         log = await logguild.fetch_channel(os.environ['LOGCHANNEL'])
#         view = LobbyView(self.bot, self.msg, self.players, self.host_id)
#         await self.msg.edit(view=view)
#         turn = self.players[0] if len(self.players) < 2 else random.choice(
#             self.players)
#         player = self.bot.load_character(turn, interaction.guild.id)
#         if interaction.user.id != self.host_id:
#             await interaction.followup.send(
#                 "You are not the Host of this lobby")
#             return
#         enemy = player.pve(
#             interaction.guild.id
#         )  #here we use the game.py character classes PVE function to retrieve an Enemy for our player
#         lobby_data = dynamo.read_lobby(self.host_id, interaction.guild.id)
#         target_list = []
#         for e in enemy:
#             target_list.append(e)
#         lobby_data['targets'] = [e.to_dict() for e in target_list]
#         lobby_data['team1'] = lobby_data['players']
#         lobby_data['team2'] = lobby_data['targets']
#         lobby_data['turn'] = turn
#         dynamo.save_lobby(self.host_id,
#                               lobby_data['colony'],
#                               lobby_data['name'],
#                               lobby_data['players'],
#                               0,
#                               targets=target_list,
#                               team1=lobby_data['team1'],
#                               turn=lobby_data['turn'],
#                               team2=lobby_data['team2'])
#         await pve_embed(self.bot, self.msg, enemy, player, self.host_id,
#                         self.bot.user.avatar.url)
#         return


# class StartPVP(discord.ui.Button):

#     def __init__(self, bot, msg, players, host_id):
#         self.bot = bot
#         self.msg = msg
#         self.players = players
#         self.host = host_id
#         super().__init__(label="PVP",
#                          style=discord.ButtonStyle.blurple,
#                          emoji='<a:PVP:1279989213613265061>',
#                          row=2)

#     async def callback(self, interaction: discord.Interaction):
#         lob = dynamo.read_lobby(self.host, interaction.guild.id)
#         if interaction.user.id != self.host:
#             await interaction.response.send_message(
#                 "You are not the host of this lobby", ephemeral=True)
#         description = f"### `PVP LOBBY`"
#         await pvp_embed(self.bot, self.host, self.players, lob, description,
#                         self.msg)


# class Lock(discord.ui.Button):

#     def __init__(self, bot, msg, players, host_id):
#         self.msg = msg
#         self.bot = bot
#         self.players = players
#         self.host = host_id
#         super().__init__(label='Lock',
#                          style=discord.ButtonStyle.gray,
#                          emoji='🔒',
#                          row=1)

#     async def callback(self, interaction: discord.Interaction):
#         lob = dynamo.read_lobby(self.host, interaction.guild.id)
#         if lob['lock'] == False:
#             lob['lock'] = True
#             description = "You have locked the lobby"
#         else:
#             lob['lock'] = False
#             description = "You have unlocked the lobby"

#         players = self.players
#         invites = lob['invites']
#         for p in self.players:
#             if p not in invites:
#                 invites.append(p)
#         lob['invites'] = invites
#         dynamo.save_lobby(self.host,
#                               interaction.guild.id,
#                               lob['name'],
#                               self.players,
#                               t_count=0,
#                               locked=lob['lock'])
#         description = "Host has locked the lobby"
#         embed = await make_lobby_embed(self.bot, lob, description)
#         await self.msg.edit(embed=embed,
#                             view=LobbyView(self.bot, self.msg, self.players,
#                                            self.host))


# class TargetView(discord.ui.View
#                  ):  #the target view class to select a target to attack

#     def __init__(
#             self, bot, msg, player, enemies: list, host_id
#     ):  #takes in current player and enemies which should be a list
#         super().__init__()
#         self.add_item(
#             Target(bot, msg, player, enemies,
#                    host_id))  #add the Target select class to the View


# class Target(discord.ui.Select):

#     def __init__(self, bot, msg, player, enemies, host_id):
#         options = []
#         enemy_names = []
#         if isinstance(enemies, list):
#             if isinstance(enemies[0], game.Character):
#                 enemy_names = [e.name for e in enemies]
#             elif isinstance(enemies[0], game.Enemy):
#                 enemy_names = [e.name for e in enemies]
#             elif isinstance(enemies[0], int):
#                 for e in enemies:
#                     enem = bot.load_character(e, player.colony)
#                     enemy_names.append(enem.name)
#             elif isinstance(enemies[0], dict):
#                 enemy_names = [e['name'] for e in enemies]
#             elif isinstance(enemies[0], str):
#                 enemy_names = [e for e in enemies]
#             else:
#                 enemy_names = [e.name for e in enemies]
#         for idx, t in enumerate(enemy_names):
#             options.append(
#                 discord.SelectOption(label=f"{idx + 1}) {t}", value=str(idx)))
#         if len(options) < 1:
#             options = [
#                 discord.SelectOption(label=f"No targets left", value="None")
#             ]
#         self.bot = bot
#         self.msg = msg
#         self.player = player
#         self.targets = enemies
#         self.host_id = host_id
#         super().__init__(placeholder="Choose a target", options=options)

#     async def callback(self, interaction: discord.Interaction):
#         await interaction.response.defer()
#         value = self.values[0]
#         target_index = int(value)
#         target = None
#         targets = self.targets
#         for idx, t in enumerate(targets):
#             if idx == target_index:
#                 target = t
#                 break
#         if value == "None":
#             await interaction.followup.send("No enemies left")

#         player = self.player
#         msg = self.msg
#         if isinstance(target, str):
#             for enem in game.Enemy.__subclasses__():
#                 if enem().name == target:
#                     target = enem()
#         if isinstance(target, int):
#             target = self.bot.load_character(target, player.colony)

#         if isinstance(target, dict):
        
#             if target['name'] in old_techniques.enemy_techniques:
#                     target = game.Enemy(**target)
            
#             if 'user_id' in target.keys():
#                 target = game.Character(**target)
            
            
                
#         description = f"### {self.player.name} vs {target.name}"
#         await battle_info(self.bot, player, target, description, self.msg,
#                           self.targets, self.host_id)


# #Example of a discord View class with decorators
# class BattleButtons(discord.ui.View):  #creating the active battle buttons

#     def __init__(self, bot, msg, player, enemy, next_targets, host_id, ct):
#         super().__init__(timeout=None)
#         self.bot = bot
#         self.msg = msg
#         self.player = player
#         self.enemy = enemy
#         self.next_targets = next_targets
#         self.host_id = host_id
#         self.ct = ct
#         self.technique.label = ct.name
#         self.technique.emoji = ct.emote

#     @discord.ui.button(label="Physical",
#                        style=discord.ButtonStyle.green,
#                        emoji='🤜',
#                        row=1)
#     async def physical(self, interaction: discord.Interaction,
#                        button: discord.ui.Button):
#         id = check_id(interaction.user.id, self.player.user_id)
#         if not id:
#             await interaction.response.send_message(
#                 content="It is not your turn yet")
#             button.disabled = False
#             await self.msg.edit(
#                 view=BattleButtons(self.bot, self.msg, self.player, self.enemy,
#                                    self.next_targets, self.host_id, self.ct))
#             return

#         await interaction.response.defer()

#         button.disabled = True

#         await self.msg.edit(view=self)

#         enemy = self.enemy

#         player = self.player

#         if player.ce >= 5 or player.technique == 'Heavenly Restriction':
#             results = self.player.fight(enemy)
#         else:
#             await interaction.followup.send(
#                 f"You need at least 5 ce to use physical attacks!")
#             return
#         player.ce -= 5
#         dmg = results[0]
#         outcome = results[1]
#         killed = results[2]
#         tool = None
#         if len(results) > 3:
#             tool = results[3]
#         if killed:
#             await interaction.followup.send(
#                 f"`You exorcised {enemy.name} with their physical prowess with {dmg} damage`",
#                 ephemeral=True)

#         elif outcome == "hit":
#             await interaction.followup.send(
#                 f"`You hit {enemy.name} for {dmg} damage!`", ephemeral=True)
#         elif outcome == "missed":
#             await interaction.followup.send(f"`You missed!`", ephemeral=True)
#         elif outcome == "tanked":
#             await interaction.followup.send(
#                 f"`{enemy.name} tanked the attack!`", ephemeral=True)
#         print(self.next_targets)
#         await self.update_physical_info(player, enemy, dmg, outcome, killed,
#                                         self.next_targets, tool,
#                                         self.bot.user.avatar.url)

#     @discord.ui.button(label="Technique",
#                        style=discord.ButtonStyle.blurple,
#                        row=0)
#     async def technique(self, interaction: discord.Interaction,
#                         button: discord.ui.Button):
#         await interaction.response.defer()
#         if interaction.user.id != self.player.user_id:
#             await interaction.followup.send("It is not your turn",
#                                             ephemeral=True)
#             button.disabled = False
#             await self.msg.edit(
#                 view=BattleButtons(self.bot, self.msg, self.player, self.enemy,
#                                    self.next_targets, self.host_id, self.ct))
#             return
#         button.disabled = True
#         await self.msg.edit(view=BattleButtons(self.bot, self.msg, self.player, self.enemy, self.next_targets, self.host_id, self.ct))
#         title = "Select a moveset"
#         description = f"### Choose wether to defend or attack"
  
#         player = self.player
#         if player:
#             t = player.technique
#             if player == game.Enemy.__subclasses__():
#                 return
#             if " " in t:
#                 t.replace(" ", "_")
#             ct = old_techniques.get_cursed_technique(t)
#             description += f"\n`{ct.ce_cost} ce required`"
#             self.label = f"{ct.name}"
#             await self.msg.edit(view=self)
#             atk_opts = []
#             for i, key in enumerate(ct.attack.keys()):
#                         atk_dik = ct.attack[key]
#                         move_string = ""
#                         move_string += f"`{i + 1})` **{key}**\n> **Imbue Cost:** `{atk_dik['imbue cost']}`\n> **Required CT level:** `{atk_dik['ct lvl']}`\n> **Damage:** `{atk_dik['dmg']}`\n> **Speed:** `{atk_dik['speed']}`"
#                         if 'negate' in atk_dik.keys():
#                             move_string += F"\n> **Negate:** `YES`"
#                         if 'drain' in atk_dik.keys():
#                             move_string += f"\n> **Poison:** `{atk_dik['drain']} dmg`"
#                         if 'aoe' in atk_dik.keys():
#                             move_string += f"\n> **AOE:** `{atk_dik['aoe']} max targets`"
#                         if 'charge' in atk_dik.keys():
#                             move_string += f"\n> **Charge:** `{atk_dik['charge']} charges`"
#                         if 'stack' in atk_dik.keys():
#                             move_string += F"\n> **Stack:** `{atk_dik['stack']} stacks`"
#                         if 'soul' in atk_dik.keys():
#                             move_string += f"\n> **Soul:** `{atk_dik['soul']} dmg`"
#                         atk_opts.append(move_string)
                    
#             def_opts = []
#             for i, key in enumerate(ct.defense.keys()):
#                 def_dik = ct.defense[key]
#                 move_string = " "
#                 move_string += f"`{i + 1})` **{key}**\n> **Imbue Cost:** `{def_dik['imbue cost']}`\n> **Required CT level:** `{def_dik['ct lvl']}`\n> **Defense:** `{def_dik['def']}`\n> **Speed:** `{def_dik['speed']}`"
#                 if 'negate' in def_dik.keys():
#                     move_string+= F"\n> **Negate:** `YES`"
#                 if 'drain' in def_dik.keys():
#                     move_string += f"\n> **Poison:** `{def_dik['drain']}`"
#                 if 'aoe' in def_dik.keys():
#                     move_string += f"\n> **AOE max targets:** `{def_dik['aoe']}`"
#                 if 'charge' in def_dik.keys():
#                     move_string += f"\n> **Charge:** `{def_dik['charge']}`"
#                 if 'stack' in def_dik.keys():
#                     move_string += f"\n> **Stack:** `{def_dik['stack']}`"
#                 if 'counter' in def_dik.keys():
#                     move_string += f"\n> **Counter:** `{def_dik['dmg']} dmg`"
#                 if 'soul' in def_dik.keys():
#                     move_string += f"\n> **Soul defense:** `{def_dik['soul']}`"
#                 def_opts.append(move_string)
                
                
            

#             atk_dicts = dict(ct.attack)
#             def_dicts = dict(ct.defense)

#             field1n = None
#             field1v = None
#             field2n = None
#             field2v = None
#             ce_cost = ct.ce_cost
#             thumbnail = self.bot.user.avatar.url
#             if player.ce < ct.ce_cost:
#                 await interaction.followup.send("Not enough CE",
#                                                 ephemeral=True)
#             if player.imbued < ct.imbued:
#                 await interaction.followup.send("Not enough CE imbued",
#                                                 ephemeral=True)
#             field1n = "**Offensive Techniques**"
#             field1v =  "\n".join(atk_opts) 
#             field2n = "**Defensive Techniques**"
#             field2v = "\n".join(def_opts)
#             embed = make_embed(title,
#                                description,
#                                thumbnail,
#                                field1_name=field1n,
#                                field1_value=field1v,
#                                field2_name=field2n,
#                                field2_value=field2v)
#             new_msg = await interaction.followup.send(embed=embed,
#                                                       ephemeral=True)
#             await new_msg.edit(view=CTdropdownView(
#                 self.player, self.msg, atk_dicts, def_dicts, ct, self.enemy,
#                 self.next_targets, self.host_id, self.bot, new_msg))
#             return

#     @discord.ui.button(label="Imbue",
#                        style=discord.ButtonStyle.blurple,
#                        emoji='<a:imbue:1280525379899101185>',
#                        row=0)
#     async def imbue(self, interaction: discord.Interaction,
#                     button: discord.ui.Button):
#         if interaction.user.id != self.player.user_id:
#             await interaction.response.send_message("It is not your turn",
#                                                     ephemeral=True)
#         else:
#             imbuemodal = ImbueModal()
#             imbuemodal.player = self.player
#             imbuemodal.message = self.msg
#             imbuemodal.bot = self.bot
#             imbuemodal.enemy = self.enemy
#             imbuemodal.next_targets = self.next_targets
#             imbuemodal.host_id = self.host_id
#             imbuemodal.bot = self.bot

#             await interaction.response.send_modal(imbuemodal)
#             return

#     @discord.ui.button(label="Run",
#                        style=discord.ButtonStyle.red,
#                        emoji="🏃‍♂️",
#                        row=1)
#     async def run(self, interaction: discord.Interaction,
#                   button: discord.ui.Button):
#         try:
#             id = check_id(interaction.user.id, self.player.user_id)
#             if not id:
#                 await interaction.response.send_message(
#                     content="Its not your turn yet")
#                 button.disabled = False
#                 await self.msg.edit(view=BattleButtons(
#                     self.bot, self.msg, self.player, self.enemy,
#                     self.next_targets, self.host_id, self.ct))
#             button.disabled = True
#             await self.msg.edit(view=self)
#             await interaction.response.defer()
#             new_player = None
#             enemy = self.enemy
#             player = self.player
#             player.mode = game.GameMode.ROAM
#             escaped = player.run(enemy)
#             lobby = dynamo.read_lobby(self.host_id, player.colony)
#             if escaped:
#                 title = f"{player.name} escaped the battle"
#                 if player.user_id == self.host_id:
#                     description = "### The host left the battle\n### lobby ended"

#                     embed = make_embed(title=title, description=description)
#                     await self.msg.edit(embed=embed, view=None)
#                 else:
#                     description = f"### {player.name} ran from the battle"

#                 new_lob = turn(player.user_id, lobby)
#                 dynamo.delete_from_lobby(self.host_id, player.colony,
#                                              player.user_id)
#                 embed = make_embed(title=title, description=description)
#                 await self.msg.edit(embed=embed, view=None)
#                 await asyncio.sleep(2)
#                 if new_lob['players']:
#                     new_player = self.bot.load_character(
#                         new_lob['turn'], new_lob['colony'])
#                     for t in self.next_targets:
#                         if isinstance(t, game.Enemy):
#                             await pve_embed(self.bot, self.msg, self.enemy,
#                                             new_player, self.host_id,
#                                             self.bot.user.avatar.url)
#                         else:
#                             self.next_targets.append(self.enemy)
#                             await pvp_fight(self.bot, new_lob,
#                                             new_lob['targets'], self.msg)

#             else:
#                 print("Player failed to escape")
#                 attack = random.choice(
#                     [key for key in self.enemy.technique['attack'].keys()])
#                 tech = old_techniques.Techniques(**self.enemy.technique)
#                 if isinstance(enemy, game.Enemy):
#                     atk_dict = tech.attack[attack]
#                     defense = None
#                     if self.player.defense:
#                         defense = self.player.defense
#                     else:
#                         defense = 'CE'
#                     p_tech = old_techniques.get_cursed_technique(
#                         self.player.technique)
#                     p_name = defense.replace(" ", "_")
#                     d_func = getattr(p_tech, p_name.lower())
#                     results = d_func(self.enemy, self.player, atk_dict)
#                     await ai_turn(self.bot, results, attack, self.player,
#                                   self.enemy, self.msg, lobby)
#                     await asyncio.sleep(3)
#                     if player:
#                         description = f"### `{player.name}` has escaped the battle!"
#                         player.mode = game.GameMode.ROAM
#                         player.save_to_db()
#                         embed = make_embed(lobby['name'], description,
#                                            self.bot.user.avatar.url)
#                         await self.msg.edit(embed=embed, view=None)
#                         dynamo.delete_from_lobby(self.host_id,
#                                                      lobby['colony'],
#                                                      player.user_id)
#                     return
#                 else:
#                     new_lob = turn(self.player.user_id, lobby)
#                     await pvp_fight(self.bot, new_lob, new_lob['targets'],
#                                     self.msg)
#                     return

#         except Exception as e:
#             print(e)
#             traceback.print_exc()

#     async def update_physical_info(
#             self, player, enemy, dmg, outcome, killed, next_targets, tool_list,
#             thumb):  #update the embed with new information
#         try:
#             description = ""
#             lobdata = dynamo.read_lobby(self.host_id, player.colony)
#             if tool_list:
#                 if len(tool_list) > 1:
#                     tool1 = old_techniques.get_cursed_tool(tool_list[0])
#                     tool2 = old_techniques.get_cursed_tool(tool_list[1])
#                     description += f"\n`{player.name}` is `dual wielding` cursed tools `{tool1.name}` and `{tool2.name}`"

#                 elif len(tool_list) == 1:
#                     tool = old_techniques.get_cursed_tool(tool_list[0])
#                     description += f"\n`{player.name}` is wielding the cursed tool {tool.name}"

#             if 'hit' in outcome:
#                 description += f"\n### `{player.name}` lands his `physical attack` on `{enemy.name}`"

#             if 'tank' in outcome:
#                 description += f"\n###  `{enemy.name}` completely `tanks` the attack from {player.name}"

#             if 'miss' in outcome:
#                 description += f"\n### `{player.name}` was `too slow` to hit `{enemy.name}`"

#             if 'counter' in outcome:
#                 description += f"\n ### `{enemy.name}` was able to `counter` the attack from `{player.name}`!"

#             if killed:
#                 if enemy in next_targets:
#                     next_targets.remove(enemy)
#                 description += f"\n### `VICTORY`"
#                 description += f"\n### `{player.name}` has `exorcised` their target `{enemy.name}`\n`DAMAGE: {dmg}`"
#                 description +=f"\n`{player.name} earned {enemy.cgp} culling game points and {enemy.xp} xp`"
#                 player.xp += enemy.xp
#                 player.cgp += enemy.cgp
#                 player.save_to_db()
#                 if isinstance(enemy, game.Character):
#                     dynamo.delete_from_colony(enemy.colony, 'members', enemy.user_id)
#                 if len(next_targets) > 0:
#                     for t in next_targets:
#                         if isinstance(t, game.Enemy):
#                             embed= make_embed(lobdata['name'], description, self.bot.user.avatar.url)
#                             await self.msg.edit(embed=embed, view=None)
#                             await asyncio.sleep(6)
#                             await pve_embed(self.bot, self.msg, next_targets,
#                                 self.player, self.host_id, thumb)
#                             return
#                         if isinstance(t, game.Character):
#                             embed= make_embed(lobdata['name'], description, self.bot.user.avatar.url)
#                             await self.msg.edit(embed=embed, view=None)
#                             await asyncio.sleep(6)
#                             new_lobby = turn(player.user_id, lobdata)
#                             new_player = self.bot.load_character(new_lobby['turn'], new_lobby['colony'])
#                             await pvp_embed(self.bot, self.host_id, new_lobby['players'], new_lobby, description,self.msg)
                        
#                 else:     
#                     description += f"\n **VICTORY!** `no enemies left!`"
                    
#                     emebed = await make_lobby_embed(self.bot, lobdata,
#                                                         description)
#                     await self.msg.edit(embed=emebed,
#                                             view=LobbyView(self.bot, self.msg,
#                                                            lobdata['players'],
#                                                            self.host_id))
#                     return

#             else:
#                 if isinstance(enemy, game.Enemy):
#                     ct = old_techniques.get_cursed_technique(player.technique)
#                     def_name = None
#                     if player.defense:
#                         def_name = player.defense.lower()
#                     else:
#                         def_name = 'CE'
#                     def_func = getattr(ct, def_name.replace(" ", "_"))
#                     atk_name = random.choice([k for k in enemy.technique['attack'].keys()])
#                     atk_dict = enemy.technique['attack'][atk_name]
#                     results = def_func(enemy, player, atk_dict)
#                     dynamo.save_lobby(
#                         self.host_id,
#                         player.colony,
#                         lobdata['name'],
#                         lobdata['players'],
#                         lobdata['t_count'],
#                         targets=[t for t in self.next_targets])
#                     embed = make_embed(lobdata['name'], description, self.bot.user.avatar.url)
#                     await self.msg.edit(embed=embed, view=None)
#                     await asyncio.sleep(6)
#                     await ai_turn(self.bot, results, atk_name, player, enemy,self.msg, lobdata)
#                     return
#                 if isinstance(enemy, game.Character):
#                     embed = make_embed(lobdata['name'], description, self.bot.user.avatar.url)
#                     await self.msg.edit(embed=embed, view=None)
#                     await asyncio.sleep(6)
#                     lob = dynamo.read_lobby(self.host_id, player.colony)
#                     new_lob = turn(player.user_id, lobdata)
#                     await pvp_fight(self.bot, new_lob, new_lob['targets'],self.msg)
#                     return
            

#         except Exception as e:
#             (f'Error in physical fight button {e}')
#             traceback.print_exc()


# class ImbueModal(discord.ui.Modal, title="Imbued"):
#     amount = discord.ui.TextInput(label="Amount to Imbue",
#                                   style=discord.TextStyle.short,
#                                   placeholder="Can't be more than your CE",
#                                   max_length=3)

#     async def on_submit(self, interaction: discord.Interaction):
#         await interaction.response.defer()
#         imbued = int(self.amount.value)
#         player = self.player
#         enemy = self.enemy
#         technique = old_techniques.get_cursed_technique(player.technique)
#         if player.ce >= imbued:
#             player.ce -= imbued
#             player.imbued += imbued
#             player.save_to_db()
#             await interaction.followup.send(f"### Succesfully imbued {imbued}",
#                                             ephemeral=True)
#             title = f"PVE Battle!"
#             description = f"### {player.name} imbued CE!"
#             player_hp = healthbar(player.hp, player.max_hp)
#             player_ce = ce_bar(player.ce, player.max_ce)
#             enemy_hp = healthbar(enemy.hp, enemy.max_hp)
#             field1n = f"{player.name}"
#             field1v = f"\n**HP**: {player_hp} `[{player.hp}/{player.max_hp}]`\n**CE:** {player_ce} `[{player.ce}/{player.max_ce}]`\n**Imbued:** `{player.imbued}`\n**Strength:** `{player.attack}`\n**Speed** {player.speed}\n**CT:** {technique.emote} `{technique.name}`  \n**Defense:** {player.defense}"
#             field2n = f"{enemy.name}"
#             field2v = f"\n**HP**: {enemy_hp}\n**Strength:** `{enemy.attack}`\n**Speed** {enemy.speed}\n**Defense:** {enemy.defense}"
#             embed = make_embed(title,
#                                description,
#                                field1_name=field1n,
#                                field1_value=field1v,
#                                field2_name=field2n,
#                                field2_value=field2v, thumbnail=self.bot.user.avatar.url)
#             await self.message.edit(embed=embed,
#                                     view=BattleButtons(self.bot, self.message,
#                                                        self.player, self.enemy,
#                                                        self.next_targets,
#                                                        self.host_id,
#                                                        technique))
#             return

#         else:
#             await interaction.followup.send("Not enough cursed energy",
#                                             ephemeral=True)
#             return

#     async def error(self, interaction: discord.Interaction, error):
#         print(error)


# class CTdropdownView(discord.ui.View):

#     def __init__(self, player, msg, atk_opts, def_opts, technique, enemy,
#                  enemy_team, host, bot, new_msg):
#         super().__init__(timeout=None)
#         self.add_item(
#             AtkSelect(player, msg, atk_opts, technique, enemy, enemy_team,
#                       host, bot, new_msg))
#         self.add_item(
#             DefSelect(bot, host, player, msg, def_opts, technique, enemy,
#                       enemy_team, new_msg))


# class AtkSelect(discord.ui.Select):

#     def __init__(self, player, msg, atk_opts, technique, enemy, enemy_team,
#                  host, bot, new_msg):
#         self.player = player
#         self.msg = msg
#         self.atk_opts = atk_opts
#         self.ct = technique
#         self.enemy = enemy
#         self.enemy_team = enemy_team
#         self.host = host
#         self.bot = bot
#         self.new_msg = new_msg
#         print(atk_opts)
#         options = [
#             discord.SelectOption(
#                 label=atk,
#                 description=
#                 f"dmg: {atk_opts[atk]['dmg']} speed: {atk_opts[atk]['speed']} imbue cost: {atk_opts[atk]['imbue cost']} req lvl {atk_opts[atk]['ct lvl']}",
#                 value=atk) for atk in atk_opts
#         ]
#         super().__init__(placeholder="Attack Options", options=options)

#     async def callback(self, interaction: discord.Interaction):
#         attack = self.values[0]
#         print(f"{self.player.name} using {self.player.technique} : {attack}")
#         print(f"host is {self.host}")
#         lobdata = dynamo.read_lobby(self.host, self.player.colony)
#         print(self.enemy)
#         print(self.enemy_team)

#         if 'aoe' in self.ct.attack[attack].keys():
#             targets = [t for t in self.enemy_team]
#             for t in targets:
#                 if t == self.enemy:
#                     targets.remove(t)
#             await aoe_embed(self.bot,
#                             attack,
#                             self.player,
#                             self.msg,
#                             targets,
#                             lobdata,
#                             self.new_msg,
#                             chosen=[self.enemy])
#             return
#         if 'domain' in self.ct.attack[attack].keys():
#                 domain_name = attack.lower()
#                 domain_func = getattr(self.ct, domain_name.replace(" ","_"))
#                 results = domain_func(self.player, self.enemy)
#                 await self.new_msg.delete()
#                 print(f"Results of domain: '{attack}': {results}")
#                 await domain_embed(self.bot, self.msg, attack, results, self.player, self.enemy_team, lobdata, self.enemy)
#                 return
            
#         results = self.player.use_technique(attack, 'attack', target=self.enemy)
#         await self.new_msg.delete()
#         await technique_embed(self.bot, attack, results, self.msg, self.player,
#                               lobdata, self.enemy, self.enemy_team, self.host)


# class DefSelect(discord.ui.Select):

#     def __init__(self, bot, host, player, msg, def_opts, technique, enemy,
#                  enemy_team, new_msg):
#         self.player = player
#         self.msg = msg
#         self.def_opts = def_opts
#         self.ct = technique
#         self.enemy = enemy
#         self.enemy_team = enemy_team
#         self.host = host
#         self.bot = bot
#         self.new_msg = new_msg

#         options = [
#             discord.SelectOption(
#                 label=defn,
#                 description=
#                 f"def: {def_opts[defn]['def']} speed {def_opts[defn]['speed']}, req lvl {def_opts[defn]['ct lvl']}",
#                 value=defn) for defn in def_opts
#         ]
#         super().__init__(placeholder="Defense Options", options=options)

#     async def callback(self, interaction: discord.Interaction):
#         host = self.host
#         enemy = self.enemy
#         await interaction.response.defer()
#         defense = self.values[0]
#         self.player.defense = defense
#         self.player.save_to_db()
#         await interaction.followup.send(f"### Defense set to `{defense}`",
#                                         ephemeral=True)
#         choice = random.choice([1, 2])
#         results = None
#         attack_name = None
#         if choice == 1:
#             print(f"Enemy attacking physically")
#             results = enemy.fight(self.player)
#             attack_name = 'Physical'
#         elif choice == 2:
#             print(f"Enemy attacking using technique")
#             if isinstance(enemy, game.Enemy):
#                 attack_name = random.choice(
#                     list(self.enemy.technique['attack'].keys()))
#                 attack = self.enemy.technique['attack'][attack_name]
#                 print(
#                     f"Enemy using {attack_name}\n{attack_name} dictionary: {attack} "
#                 )
#                 results = self.player.use_technique(self.player.defense,
#                                                     'defense',
#                                                     enemy,
#                                                     attack=attack)
#         elif results == None:
#             await interaction.followup.send("Error in your defense")
#             return
#         print(f"Results for {self.player.defense} defense: {results}")
#         lobby_data = dynamo.read_lobby(host, self.player.colony)
#         await self.new_msg.delete()
#         await ai_turn(self.bot, results, attack_name, self.player, self.enemy,
#                       self.msg, lobby_data)


# class AOEView(discord.ui.View):

#     def __init__(self, bot, attack, targets, max_length, current_targets, msg,
#                  lob, player, new_msg):
#         super().__init__(timeout=None)
#         if len(targets) > 0:
#             self.add_item(
#                 AOESelect(targets, max_length, current_targets, bot, attack,
#                           msg, lob, player, new_msg))
#         if len(current_targets) > 0:
#             self.add_item(
#                 AOELaunch(targets, max_length, current_targets, bot, attack,
#                           msg, lob, player, new_msg))


# class AOESelect(discord.ui.Select):

#     def __init__(self, targets, max_length, current_targets, bot, attack, msg,
#                  lob, player, new_msg):
#         self.max_length = max_length
#         self.targets = targets
#         self.current_targets = current_targets
#         self.attack = attack
#         self.bot = bot
#         self.msg = msg
#         self.lob = lob
#         self.player = player
#         self.new_msg = new_msg
#         target_list = []
#         for t in targets:
#             if isinstance(t, int):
#                 char = bot.load_character(t, player.colony)

#                 target_list.append(char)
#             elif isinstance(t, str):
#                 for i in game.Enemy.__subclasses__():
#                     if i().name == t:
#                         target_list.append(i())
#             elif isinstance(t, dict):
#                 tango = None
#                 if 'user_id' in t.keys():
#                     tango = bot.load_character(t['user_id'], self.lob['colony'])
#                 elif 'timer' in t.keys():
#                     tango = game.Enemy(**t)
#                 target_list.append(tango)
#             elif isinstance(t, int):
#                 tango = bot.load_character(t, self.lob['colony'])
#                 target_list.append(tango)
#             else:
#                 target_list.append(t)

#         target_list = enumerate(target_list)
#         options = [
#             discord.SelectOption(
#                 label=f'{target.name}',
#                 description=
#                 f'Strength: {target.attack} Speed: {target.speed} Defense: {target.defense} HP: {target.hp}/{target.max_hp}',
#                 value=str(idx) + target.name) for idx, target in target_list
#         ]
#         super().__init__(placeholder="Choose a target...", options=options)

#     async def callback(self, interaction: discord.Interaction):
#         target = self.values[0][1:]
#         index = self.values[0][:1]
#         self.disabled = False
#         print(f"target chosen {index} {target}")
#         new_target = None
#         for idx, t in enumerate(self.targets):
#             if idx == int(index):
#                 if isinstance(t, dict):
#                     new_target = t
                
#                 if isinstance(t, game.Actor):
#                     if t.name == target:
#                         self.targets.remove(t)
#                         new_target = t.to_dict()
#                         break
                    
#                 elif isinstance(t, int):
#                     char = self.bot.load_character(t,self.player.colony)
#                     if char.name == target:
#                         self.targets.remove(t)
#                         new_target = char.to_dict()
#                         break

#                 elif isinstance(t, str):
#                     for e in game.Enemy.__subclasses__():
#                         if e().name == t:
#                             new_target = e().to_dict()
#                             break
        
#         new_target = new_target
#         self.current_targets.append(new_target)
#         marks = self.lob['mark']
#         if marks:
#             if marks['aoe'][self.attack]:
#                 marks['aoe'][self.attack]['target'] = self.current_targets

#         else:
#             marks = {
#                 'aoe': {
#                     self.attack: {
#                         'targets': self.current_targets
#                     }
#                 }
#             }
#         target_dicts = []
#         for t in self.targets:
#             if isinstance(t, dict):
#                 target_dicts.append(t)
                
#             elif isinstance(t,object):
#                 diction = t.to_dict()
#                 target_dicts.append(diction)
                
#         self.lob['mark'] = marks
#         dynamo.save_lobby(self.lob['host'], self.lob['colony'],
#                               self.lob['name'], self.lob['players'],
#                               self.lob['t_count'], targets=[target_dicts])
#         for t in self.current_targets:
#             for e in target_dicts:
#                 if t == e:
#                     target_dicts.remove(e)
#                     break
       
            
    
#         await aoe_embed(self.bot,
#                         self.attack,
#                         self.player,
#                         self.msg,
#                         self.targets,
#                         self.lob,
#                         self.new_msg,
#                         chosen=self.current_targets)


# class AOELaunch(discord.ui.Button):

#     def __init__(self, targets, max_length, current_targets, bot, attack, msg,
#                  lob, player, new_msg):
#         self.targets = targets
#         self.player = player
#         self.max_length = max_length
#         self.current_targets = current_targets
#         self.bot = bot
#         self.attack = attack
#         self.msg = msg
#         self.lob = lob
#         self.new_msg = new_msg
#         super().__init__(label='Launch', style=discord.ButtonStyle.green)

#     async def callback(self, interaction: discord.Interaction):
#         if interaction.user.id != self.player.user_id:
#             await interaction.response.send_message(
#                 "this is not your technique", ephemeral=True)
        
#         results, targets = self.player.use_technique(self.attack, "attack", targets=self.current_targets)
#         print(F"AOE results for {self.attack}:\nResults: {results}\nTargets: {targets}")
#         self.disabled = True
#         lob = self.lob
#         await self.new_msg.delete()
#         await aoe_results(self.bot, self.msg, self.attack, 'attack', targets, results, lob, self.player)

