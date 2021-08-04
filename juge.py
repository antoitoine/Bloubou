####################
# JUGE DISCORD BOT #
#     04/08/21     #
####################


from bot import *
from dotenv import load_dotenv
import discord
import os

load_dotenv()


#############
# CONSTANTS #
#############


USER_ID_ANTOINE = 393762112884965389

SERVER_ID_JUGE = 871155691686088714


################
# BOT CREATION #
################


intents = discord.Intents().all()

juge = Bot(intents=intents)


#################
# JUGE COMMANDS #
#################


async def juger(args, message):
    """ Juges a user """
    await message.channel.send(args["nom"])


######################
# JUGE CONFIGURATION #
######################


juge.setGuildID(SERVER_ID_JUGE)
juge.addAdmin(USER_ID_ANTOINE)

juge.setCommand(0, juger, r"juge[r|s]? (?P<nom>.+)")

juge.run(os.getenv("TOKEN_JUGE"))
