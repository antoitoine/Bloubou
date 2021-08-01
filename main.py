###############################
# BLOUBOU DISCORD BOT PROJECT #
#          01/08/21           #
###############################


import discord
import textComputing as tc
import os
from dotenv import load_dotenv

load_dotenv()


#############
# CONSTANTS #
#############


ADMIN_ID = 393762112884965389

MESSAGES = ["[DEB]", "[CMD]", "[ERR]", "[MSG]", "[BOT]", "[MSC]"]
DEBUG_MESSAGE = 0
COMMAND_MESSAGE = 1
ERROR_MESSAGE = 2
USER_MESSAGE = 3
BOT_MESSAGE = 4
MYSC_MESSAGE = 5


#####################
# UTILITY FUNCTIONS #
#####################


def printMessage(message, type):
    """ Prints a message in the console """
    print(MESSAGES[type], f"<{message.author}>", message.content)


#################
# BLOUBOU CLASS #
#################


class Bloubou(discord.Client):

    async def on_ready(self):
        """ Event called when the bot is connected and ready """
        print("[DEB] ready")

    async def fetchCommands(self, message: discord.Message):
        """ Reads and executes commands, returns False if there's no commands """
        normalizedMessage = tc.normalize(message.content)

        # Admin's commands
        if message.author.id == ADMIN_ID:
            if normalizedMessage.startswith("hello"):
                printMessage(message, COMMAND_MESSAGE)
                await message.channel.send("Hello there !")
                return True

        # Everyone's commands
        return False

    async def on_message(self, message: discord.Message):
        """ Event called when a message is read """
        # Bot's message
        if message.author == self.user:
            printMessage(message, BOT_MESSAGE)
            return

        # User's message
        if not await self.fetchCommands(message):
            printMessage(message, USER_MESSAGE)


###############
# BOT RUNNING #
###############


bot = Bloubou()
bot.run(os.getenv("TOKEN"))
