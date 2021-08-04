#######################
# MOUETTE DISCORD BOT #
#      03/08/21       #
#######################

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
USER_ID_BLOUBOU = 871145469982670908
USER_ID_JUGE = 809755685201379339
USER_ID_MOUETTE = 872447136577507409

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
    """ Answers Cui cui ! """
    await message.channel.send("Cui cui !")


async def onVoice(member, before, after):
    """ Plays seagull song when someone joins mouette channel """
    if member == mouette.user:
        return

    voiceClient = discord.utils.get(mouette.voice_clients, guild=mouette.getGuild())

    if (voiceClient and voiceClient.is_connected()) and (not after.channel or after.channel.id != CHANNEL_ID_MOUETTE_VENERE):
        await voiceClient.disconnect()
    elif (not voiceClient) and (after.channel and after.channel.id == CHANNEL_ID_MOUETTE_VENERE):
        voiceClient = await after.channel.connect()

    if not voiceClient or not voiceClient.is_connected():
        return

    await discordMusic.playSource(voiceClient, "mouette.mp3", mouette)


#########################
# MOUETTE CONFIGURATION #
#########################


mouette.setGuildID(SERVER_ID_BLOUBOU)
mouette.addAdmin(USER_ID_ANTOINE)

mouette.setVoiceFunction(onVoice)
mouette.setCommand(0, piou, r"mouette")

mouette.run(os.getenv("TOKEN_MOUETTE"))
