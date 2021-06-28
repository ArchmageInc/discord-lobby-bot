#!/usr/bin/python3

import discord
import os
import sys

from config import Config
from pubg_stats import PUBG_Stats

from gtts import gTTS
from discord.ext import commands,tasks

config = Config()
pubg_stats = PUBG_Stats(config.PUBG_TOKEN, season_file=config.SEASONS_FILE, season_data_expire=config.SEASON_DATA_EXPIRE_DAYS)

intents = discord.Intents.default()
intents.members = True;
bot = commands.Bot(command_prefix='!',intents=intents)

def remove_tmp_file(error):
    os.remove(config.TMP_AUDIO_FILE)

async def locate_member(name, guild):
    async for member in guild.fetch_members():
        if member.display_name == name:
            return member
    return None

@bot.command(name='pubg', help='Display PUBG player stats')
async def pubg(ctx, name, game_mode=None):
    player = pubg_stats.get_player(player_name=name)
    if player is None:
        await ctx.send(f"Unable to find player {name}. PUBG player names are case sensitive.")
        return

    try:
        member = await locate_member(player.name, ctx.message.guild)
        stats = pubg_stats.get_stats(player, member)
        embed = discord.Embed.from_dict(stats)
        await ctx.send(embed=embed)
    except:
        await ctx.send(f"Failed to get stats for {name}")
        print(sys.exc_info()[0])

@bot.command(name='say', help='To make the bot leave the voice channel')
async def say(ctx, *args):
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
    tts.save(config.TMP_AUDIO_FILE)

    voice_client.play(discord.FFmpegPCMAudio(source=config.TMP_AUDIO_FILE, before_options=['hide_banner','loglevel panic']), after=remove_tmp_file)

@bot.command(name='stats', help='Depricated')
async def stats(ctx, *args):
    await ctx.send(f"**{ctx.author.display_name}** this command has been removed, did you mean to use `!pubg {' '.join(args)}` ?")

@bot.command(name='play', help='Depricated')
async def play(ctx, *args):
    await ctx.send(f"**{ctx.author.display_name}** this command has been removed, did you mean to use `!say {' '.join(args)}` ?")

@bot.command(name='join', help='Depricated')
async def join(ctx, *args):
    await ctx.send(f"**{ctx.author.display_name}** this command has been removed because this automatically happens now.")

@bot.command(name='leave', help='Depricated')
async def stats(ctx, *args):
    await ctx.send(f"**{ctx.author.display_name}** this command has been removed because I am allowed to stalk any damn channel I would like. Thank you very much.")

@bot.event
async def on_ready():
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

bot.run(config.BOT_TOKEN)