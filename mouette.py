from bot import *
import discord
from dotenv import load_dotenv
import os
import youtube_dl
import asyncio

load_dotenv()

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn',
    'executable': 'D:\\ffmpeg\\bin\\ffmpeg.exe'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


#############
# CONSTANTS #
#############


USER_ID_ANTOINE = 393762112884965389
USER_ID_BLOUBOU = 871145469982670908

SERVER_ID_BLOUBOU = 871155691686088714

CHANNEL_ID_MOUETTE_VENERE = 872193019938492457


################
# BOT CREATION #
################


intents = discord.Intents().all()
mouette = Bot(intents=intents)


####################
# MOUETTE COMMANDS #
####################


async def piou(args, message):
    await message.channel.send("Cui cui !")

async def onVoice(member, before, after):
    if member == mouette.user:
        return

    voiceClient = discord.utils.get(mouette.voice_clients, guild=mouette.getGuild())

    if (voiceClient and voiceClient.is_connected()) and (not after.channel or after.channel.id != CHANNEL_ID_MOUETTE_VENERE):
        await voiceClient.disconnect()
    elif (not voiceClient) and (after.channel and after.channel.id == CHANNEL_ID_MOUETTE_VENERE):
        voiceClient = await after.channel.connect()

    if not voiceClient or not voiceClient.is_connected():
        return

    async with mouette.getGuild().channels[0].typing():
        player = await YTDLSource.from_url("https://www.youtube.com/watch?v=kgxEZWfoZMQ", loop=True)
        voiceClient.play(player, after= lambda e: print(f"Player error : {e}") if e else None)

    print(f"Now playing mouette.mp3")


#########################
# MOUETTE CONFIGURATION #
#########################


mouette.setGuildID(SERVER_ID_BLOUBOU)
mouette.addAdmin(USER_ID_ANTOINE)

mouette.setVoiceFunction(onVoice)
mouette.setCommand(0, piou, r"mouette")

mouette.run(os.getenv("TOKEN_MOUETTE"))
