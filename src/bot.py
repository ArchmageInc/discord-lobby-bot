#!/usr/bin/python3

import discord
import os
import signal
import sys
import pickle
import datetime

from gtts import gTTS
from discord.ext import commands,tasks
from dotenv import load_dotenv
from pubg_python import PUBG, Shard

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
PUBG_TOKEN = os.getenv('PUBG_TOKEN')
SEASONS_FILE = os.getenv('SEASONS_FILE','seasons.dat')
SEASON_DATA_EXPIRE_DAYS = int(os.getenv('SEASON_DATA_EXPIRE_DAYS', 15))
TMP_AUDIO_FILE = os.getenv('TMP_AUDIO_FILE', 'voice.mp3')

intents = discord.Intents.default()
intents.members = True;
bot = commands.Bot(command_prefix='!',intents=intents)

pubg_api = PUBG(PUBG_TOKEN, Shard.STEAM)
pubg_api.pubg_seasons = None
pubg_api.pubg_current_season = None

def remove_tmp_file(error):
    os.remove(TMP_AUDIO_FILE)

def update_pubg_seasons_file():
    print(f"Updating seasons file")
    pubg_api.pubg_seasons = pubg_api.seasons()
    with open(SEASONS_FILE, 'wb') as season_file:
        pickle.dump(pubg_api.pubg_seasons, season_file)

def load_pubg_seasons_file():
    print(f"Loading seasons file")
    with open(SEASONS_FILE, 'rb') as season_file:
        pubg_api.pubg_seasons = pickle.load(season_file)

def check_pubg_seasons():
    if not os.path.isfile(SEASONS_FILE):
        update_pubg_seasons_file()
        set_current_season()
        return

    if datetime.datetime.fromtimestamp(os.path.getmtime(SEASONS_FILE)) < datetime.datetime.now() - datetime.timedelta(days = SEASON_DATA_EXPIRE_DAYS):
        update_pubg_seasons_file()
        set_current_season()
        return

    if pubg_api.pubg_seasons is None:
        load_pubg_seasons_file()
        set_current_season()
        return
    
def set_current_season():
      for season in pubg_api.pubg_seasons:
        if season.attributes['isCurrentSeason']:
            pubg_api.pubg_current_season = season
            print(f"Found current season {season.id}")
            break

def get_current_season():
    check_pubg_seasons()
    return pubg_api.pubg_current_season

def format_kd(kills, deaths):
    if deaths == 0:
        return None

    return round(kills/deaths,2)

async def get_stats_embed(player, data, guild):
    modes = ['solo', 'solo_fpp', 'duo', 'duo_fpp', 'squad', 'squad_fpp']
    d = {'title': f"{player.name}'s Stats", 'fields': []}

    member = await locate_member(player.name, guild)

    if member is not None:
        d['thumbnail'] = {'url': str(member.avatar_url)}

    weekly_wins = 0
    season_wins = 0
    kd_map = {
        'kills': 0,
        'matches': 0,
        'losses': 0
    }
    mode_data = []

    for mode in modes:
        losses = getattr(data, mode).losses
        wins = getattr(data, mode).wins
        matches = losses + wins
        kills = getattr(data, mode).kills
        kd = format_kd(kills, losses)
        kd_map = {
            'kills': kd_map['kills'] + kills,
            'matches': kd_map['matches'] + matches,
            'losses': kd_map['losses'] + losses
        }
        weekly_wins += getattr(data, mode).weekly_wins
        season_wins += wins
        mode_data.append({
            'kills': kills,
            'matches': matches,
            'losses': losses,
            'wins': wins,
            'kd': kd,
            'mode': mode
        })

    mode_data = sorted(mode_data, key=lambda item: item['matches'],reverse=True)

    for info in mode_data:
        if info['matches'] != 0:
           d['fields'].append({
                    'name': f"{info['mode'].title()}:",
                    'value': f"`Matches:` {info['matches']}  `Wins:` {info['wins']}  `K/D:` {info['kd']}"
                    }) 

    season_kd = format_kd(kd_map['kills'], kd_map['losses'])

    if season_kd <= 0.4:
        d['color'] = discord.Color.red().value
    elif season_kd <= 0.5:
        d['color'] = discord.Color.gold().value
    else:
        d['color'] = discord.Color.green().value

    d['fields'].insert(0, {
        'name': f"Season Wins:",
        'value': f"`Weekly:` **{weekly_wins}**  `Total:` **{season_wins}**  `K/D:` **{season_kd}**",
        'inline': True
        })
    return discord.Embed.from_dict(d)

async def locate_member(name, guild):
    async for member in guild.fetch_members():
        if member.display_name == name:
            return member
    return None

@bot.command(name='stats', help='Display PUBG player stats')
async def stats(ctx, name, game_mode=None):
    players = pubg_api.players().filter(player_names=[name])
    if players[0] is not None:
        player = players[0]
    else:
        await ctx.send(f"Unable to find player {name}")
        return
    try:
        data = pubg_api.seasons(get_current_season().id, player_id=player.id).get()
        embed = await get_stats_embed(player, data, ctx.message.guild)
        await ctx.send(embed=embed)
    except:
        await ctx.send(f"Failed to get stats for {name}")
        print(sys.exc_info()[0])
    

@bot.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send(f"{ctx.message.author.name} is not connected to a voice channel")
        return

    channel = ctx.message.author.voice.channel
    await channel.connect()

@bot.command(name='leave', help='To make the bot leave the voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send(f"The bot is not connected to a voice channel.")

@bot.command(name='play', help='To make the bot leave the voice channel')
async def play(ctx, *args):
    if not ctx.message.author.voice:
        await ctx.send(f"{cts.message.author.name} is not connected to a voice channel")
        return

    channel = ctx.message.author.voice.channel
    voice_client = ctx.message.guild.voice_client
    if not voice_client.is_connected():
        await channel.connect()

    if not channel == voice_client.channel:
        await voice_client.move_to(channel)

    tts = gTTS(' '.join(args), lang='en', tld='ie')
    tts.save(TMP_AUDIO_FILE)

    voice_client.play(discord.FFmpegPCMAudio(source=TMP_AUDIO_FILE, before_options=['hide_banner','loglevel panic']), after=remove_tmp_file)

@bot.event
async def on_ready():
    get_pubg_seasons()
    print(f"Online and ready")
    return

@bot.event
async def on_voice_state_update(member, pre_state, post_state):
    if post_state.channel is None:
        return

    if pre_state.channel == post_state.channel:
        return

    if post_state.channel.guild.voice_client is None:
        await post_state.channel.connect()

    if post_state.channel == post_state.channel.guild.voice_client.channel:
        return

    await post_state.channel.guild.voice_client.move_to(post_state.channel)


bot.run(BOT_TOKEN)