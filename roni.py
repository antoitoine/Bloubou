####################
# RONI DISCORD BOT #
#     05/08/21     #
####################

from bot import *
import discord
from dotenv import load_dotenv
import os
import discordMusic

load_dotenv()


#############
# CONSTANTS #
#############


USER_ID_ANTOINE = 393762112884965389
SERVER_ID = 871155691686088714
CHANNEL_ID_MOUETTE_VENERE = 872193019938492457


################
# BOT CREATION #
################


intents = discord.Intents().all()
roni = Bot(intents=intents)

lastMusic = None


#################
# RONI COMMANDS #
#################


def findVoiceClient():
    for vc in roni.voice_clients:
        if vc.guild == roni.getGuild():
            return vc
    return None


async def musiqueYoutube(args, message):
    """ Plays a youtube music """
    vc = findVoiceClient()

    if vc is not None and vc.is_playing():
        vc.stop()

    global lastMusic

    player = lastMusic = await discordMusic.YTDLSource.from_url(args["lien"], loop=roni.loop)

    if vc is None:
        vc = await message.author.voice.channel.connect()

    vc.play(player, after=lambda e: print(f"Player error : {e}") if e else None)
    await message.channel.send(f"Now playing : {player.title}")


async def pause(args, message):
    """ Pauses current song """
    vc = findVoiceClient()
    if vc is not None:
        vc.pause()


async def resume(args, message):
    """ Resumes current song """
    vc = findVoiceClient()
    if vc is not None and vc.is_paused():
        vc.resume()


async def disconnect(args, message):
    """ Disconnects from channel """
    vc = findVoiceClient()
    if message.author.voice is None or vc is None or vc.channel != message.author.voice.channel:
        return
    await vc.disconnect()


async def stop(args, message):
    """ Stops playing current song"""
    vc = findVoiceClient()
    if vc is not None and vc.is_playing():
        vc.stop()


async def viensChannel(args, message):
    """ Joins the channel where the message author is """
    vc = findVoiceClient()
    if message.author.voice is None:
        await message.channel.send("Tu dois te connecter dans un salon vocal")
        return

    if vc is None:
        await message.author.voice.channel.connect()
    else:
        await vc.move_to(message.author.voice.channel)


async def vaChannel(args, message):
    """ Joins a specific user channel """
    vc = findVoiceClient()
    if args["user"] in ["moi", "nous"]:
        user = message.author
    else:
        user = roni.getUserByName(args["user"])
    if (user is None or user.voice is None) and "other" in args:
        user = roni.getUserByName(args["other"])

    if user is None or user.voice is None:
        return

    if user.voice is None:
        if "autre" in args:
            autre = roni.getUserByName(args["autre"])
            if autre.voice is not None:
                if vc is None:
                    await autre.voice.channel.connect()
                else:
                    await vc.move_to(autre.voice.channel)
        await message.channel.send(f"{user.nick} n'est pas dans un salon vocal")
        return

    if vc is None:
        await user.voice.channel.connect()
    else:
        vc.move_to(user.voice.channel)


async def replay(args, message):
    global lastMusic
    vc = findVoiceClient()
    if lastMusic is not None:
        if vc is not None and vc.is_playing():
            vc.stop()
        print(vc, lastMusic)
        vc.play(lastMusic, after=lambda e: print(e) if e else None)


######################
# RONI CONFIGURATION #
######################


roni.setGuildID(SERVER_ID)
roni.addAdmin(USER_ID_ANTOINE)

roni.setCommand(0, pause, r"(?:pauses?)", "musique")
roni.setCommand(1, musiqueYoutube, r"(?:joue[r|s]?|play|chante[r|s]?|mets?(?:tr?es?)?|d[e|é]marres?|commences?) +(?:la|les?|une?s?)? *(?:morceaux?|musiques?|chansons?|sons?|titres?)? *(?P<lien>.+)", "musique")
roni.setCommand(2, resume, r"(?:resumes?|repren[d|t]s?|continues?)", "musique")
roni.setCommand(3, disconnect, r"(?:(?:re)?par[s|t]|partir|bouges?|va-t'en|d[e|é]co|d[e|é]gages?|pas toi)", "musique")
roni.setCommand(4, stop, r"(?:stop|arr[ê|e]tes? +(?:la|les?) +(?:musiques?|chansons?|sons?))", "musique")
roni.setCommand(5, viensChannel, r"(?:vien[s|t]|revien[s|t]|venir|ram[e|è]nes?(?:[ |-]toi)?)", "musique")
roni.setCommand(6, vaChannel, r"(?:vas? *)?(?:(?:plus )?vite|vas?|voir|rejoindre|rejoin[t|s]?|connecte[s|r]?-? *(?:toi)??|aller|go) +(?:(?:avec|voir) +|(?:dans +)?le +(?:salon(?: vocal)?|voc(?:al)?|channel) +(?:de +|d'))?(?P<user>.+?(?=(?:\n| +ou +(?:d'|de )?(?P<other>.+)| +et| +il| +elle)))", "musique")
roni.setCommand(7, replay, r"(?:rejoues?|replay|recommences?|encore)", "musique")

roni.run(os.getenv("TOKEN_RONI"))
