######################
# GERARD DISCORD BOT #
#      05/08/21      #
######################


from bot import *
from dotenv import load_dotenv
import discord
import os

load_dotenv()


#############
# CONSTANTS #
#############


USER_ID_ANTOINE = 393762112884965389

SERVER_ID = 871155691686088714

GERARD_CHANNEL_ID = 872484253764579338


################
# BOT CREATION #
################


intents = discord.Intents().all()

gerard = Bot(intents=intents)


###################
# GERARD COMMANDS #
###################


async def on_message(message):
    if message.channel.id != GERARD_CHANNEL_ID:
        return

    print(message.content)


async def on_raw_message_delete(payload):
    if payload.channel_id != GERARD_CHANNEL_ID:
        return

    print(payload.message_id)


async def on_raw_message_edit(payload):
    if payload.channel_id != GERARD_CHANNEL_ID:
        return

    print(payload.data["content"])

########################
# GERARD CONFIGURATION #
########################
# todo bot activation
# todo compter nombre message a supprimer commande

gerard.guildId = SERVER_ID
gerard.adminIds = [USER_ID_ANTOINE]

gerard.onMessageFunction = on_message
gerard.onRawMessageDelete = on_raw_message_delete
gerard.onRawMessageEdit = on_raw_message_edit

gerard.run(os.getenv("TOKEN_GERARD"))
