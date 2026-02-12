import discord, random, battle_checks
from discord.ext import commands
from game import Player, Enemy
from player_tech import technique_list
from enemy_techs import enemy_tech_list
from db import read_player, read_colony, read_technique

ce_full_emoji = "<:1000001330:1354469798230102258>"
ce_half_emoji = "<:IMG_44021:1394503076223783043>"
health_full_emoji = "<:1000001328:1354469795612639816>"
health_half_emoji = "<:IMG_44019:1394503072532042241>"

def bar(current, max, emoji, half_emoji):
    max_dashes = 4
    dash_ratio = current / max_dashes
    filled_dashes = 0 if current <= 0 else int(current / dash_ratio)
    remainder = (current / dash_ratio) - filled_dashes if current > 0 else 0
    dashes = emoji * filled_dashes
    if remainder > 0:
        dashes += half_emoji * remainder
    percent = f"`{max(round((current / max) * 100), 0)}%`"
    bar = f"{dashes} {percent} `{current}/{max}`"
    return bar


def verify_player(user_id, colony):
    player, techlist = read_player(user_id, colony)
    if not player:
        return None, None
    player = Player(**player)
    return player, techlist


def round_container(lobby, bot, team_a=None, team_b=None, field=None):
    colony = read_colony(lobby['colony_id'])
    playerlist = []
    container=discord.ui.Container(accent_color=discord.Color.yellow())
    title_text = discord.ui.TextDisplay(f"# Battle in {colony['name']}: `{lobby.name}`\n## Round {lobby['round']}1")
    title_section = discord.ui.Section(title_text, accessory=discord.ui.Thumbnail(media=bot.user.avatar.url))
    container.add_item(title_section)
    container.add_item(discord.ui.Separator())
    teamA_text = {}
    if team_a:
        teamA_text['title'] = f"### `{team_a['name'] if team_a else 'Team A'}:`"
    teamB_text = {}
    teamB_text['title'] = f"### `{team_b['name'] if team_b else 'Team B'}:`"
    field_text = {}
    field_text['title'] = "### `Field:`"
    
    if not colony:
        return False, "Colony not found."
 
    for p in lobby.players:
            player, techlist = verify_player(p['user_id'], colony)
            if not player:
                return False, f"Player with ID {p['user_id']} not found."
            else:
                playerlist.append((player, techlist))
    teams_section = discord.ui.Section(accesory=discord.ui.Thumbnail(media=bot.user.avatar.url))
    if team_a:
        
        teamA_text['description'] = ""
        for p in team_a['players']:
            for pl, tl in playerlist:
                if pl.user_id == p['user_id']:
                    health_bar = bar(pl.current_health, pl.max_health, health_full_emoji, health_half_emoji)
                    ce_bar = bar(pl.current_ce, pl.max_ce, ce_full_emoji, ce_half_emoji)
                    teamA_text['description'] += f"**{pl.name}:** `Health:` {health_bar} `CE:` {ce_bar}\n"
        text = discord.ui.TextDisplay(f"{teamA_text['title']}\n{teamA_text['description']}")
        teams_section.add_item(text)
        teams_section.add_item(discord.ui.Separator())
    
    if team_b:
        teamB_text['description'] = ""
        for p in team_b['players']:
            for pl, tl in playerlist:
                if pl.user_id == p['user_id']:
                    health_bar = bar(pl.current_health, pl.max_health, health_full_emoji, health_half_emoji)
                    ce_bar = bar(pl.current_ce, pl.max_ce, ce_full_emoji, ce_half_emoji)
                    teamB_text['description'] += f"**{pl.name}:** `Health:` {health_bar} `CE: {ce_bar}`"
        text = discord.ui.TextDisplay(f"{teamB_text['title']}\n{teamB_text['description']}")
        teams_section.add_item(text)
        teams_section.add_item(discord.ui.Separator())
    if field:
        field_text['description'] = ""
        for t in field:
            health_bar = bar(t['current_health'], t['max_health'], health_full_emoji, health_half_emoji)
            ce_bar = bar(t['current_ce'], t['max_ce'], ce_full_emoji, ce_half_emoji)
            field_text['description'] += f"**{t['name']}:** `Health:` {health_bar} `CE:` {ce_bar}\n"
        text = discord.ui.TextDisplay(f"{field_text['title']}\n{field_text['description']}")
        teams_section.add_item(text)
        teams_section.add_item(discord.ui.Separator())

    container.add_item(teams_section)
    return True, container


    