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


################
# BOT CREATION #
################


intents = discord.Intents().all()

gerard = Bot(intents=intents)


###################
# GERARD COMMANDS #
###################


########################
# GERARD CONFIGURATION #
########################


gerard.guildId = SERVER_ID
gerard.adminIds = [USER_ID_ANTOINE]

gerard.run(os.getenv("TOKEN_GERARD"))
