####################
# JUGE DISCORD BOT #
#     04/08/21     #
####################


from bot import *
import discord
from dotenv import load_dotenv
import os

load_dotenv()


#############
# CONSTANTS #
#############


USER_ID_ANTOINE = 393762112884965389
USER_ID_JUGE = 809755685201379339
USER_ID_BLOUBOU = 871145469982670908
USER_ID_MOUETTE = 872447136577507409

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

juge.setAliases(USER_ID_ANTOINE, ["antoine", "tatane", "antoinette"])
juge.setAliases(USER_ID_BLOUBOU, ["bloubou"])
juge.setAliases(USER_ID_JUGE, ["juge", "le juge", "maitre"])
juge.setAliases(USER_ID_MOUETTE, ["mouette", "piaf", "oiseau", "goeland"])

juge.addBotID(USER_ID_BLOUBOU)
juge.addBotID(USER_ID_JUGE)
juge.addBotID(USER_ID_MOUETTE)

juge.setCommand(0, juger, r"juge[r|s]? (?P<nom>.+)")

juge.run(os.getenv("TOKEN_JUGE"))
