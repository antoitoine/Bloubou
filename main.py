###############################
# BLOUBOU DISCORD BOT PROJECT #
#          01/08/21           #
###############################


import discord
import textComputing as tc
import os
import random

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


####################
# GLOBAL VARIABLES #
####################


rolesID = { 871166312477503488: True,
            871166956408016946: True,
            871166756985643018: True,
            871167362873831464: True,
            871165214635221042: True,
            871167998696759307: True,
            871167758224740402: True,
            871167588636442634: True,
            871165751850045450: True,
            871168934685077504: True,
            871168808495235082: True,
            871169321009815582: True,
            871170622993104936: True,
            871168275134963802: True,
            871168372828667924: True,
            871168483923230771: True }


#####################
# UTILITY FUNCTIONS #
#####################


def printMessage(message, type, isText=False):
    """ Prints a message in the console """
    if not isText:
        print(MESSAGES[type], f"<{message.author}>", message.content)
    else:
        print(MESSAGES[type], message)

def reinitRolesID():
    """ Sets all roles to available """
    global rolesID
    rolesID = { x:True for x in rolesID }

def getRandomRoleID():
    """ Returns a random role id, or -1 """
    global rolesID

    id, available = random.choice(list(rolesID.items()))
    nbChoices = 0
    while (not available and nbChoices < 128):
        print(id)
        id, available = random.choice(list(rolesID.items()))
        nbChoices += 1

    if available:
        rolesID[id] = False
        return id
    return -1


#################
# BLOUBOU CLASS #
#################


class Bloubou(discord.Client):

    async def on_ready(self):
        """ Event called when the bot is connected and ready """
        printMessage("ready", DEBUG_MESSAGE, True)

    async def fetchCommands(self, message: discord.Message):
        """ Reads and executes commands, returns False if there's no commands """
        normalizedMessage = tc.normalize(message.content)

        # Admin's commands
        if message.author.id == ADMIN_ID:
            if normalizedMessage.startswith("admin"):
                """ Gives the admin role """
                await message.author.add_roles(discord.utils.get(message.guild.roles, name="admin"))
                return True

            if normalizedMessage.startswith("roles"):
                printMessage(message, COMMAND_MESSAGE)
                reinitRolesID()
                for member in message.guild.members:
                    printMessage(f"Removing roles from {member}", DEBUG_MESSAGE, True)
                    for role in member.roles[1:]:
                        if role.name != "admin":
                            printMessage(f"Removing {role.name}", DEBUG_MESSAGE, True)
                            await member.remove_roles(role)
                    newRoleID = getRandomRoleID()
                    if newRoleID > 0:
                        printMessage(f"{member} gets the role id {newRoleID}", DEBUG_MESSAGE, True)
                        await member.add_roles(discord.utils.get(message.guild.roles, id=newRoleID))
                printMessage("Roles Done", DEBUG_MESSAGE, True)
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

intents = discord.Intents().all()
bot = Bloubou(intents=intents)
bot.run(os.getenv("TOKEN"))
