###############################
# BLOUBOU DISCORD BOT PROJECT #
#          01/08/21           #
###############################


import discord
import os
import random
import re

import textComputing as tc

from myUtilities import *
from dotenv import load_dotenv


load_dotenv()


#############
# CONSTANTS #
#############


ADMIN_ID = 393762112884965389
BLOUBOU_ID = 871145469982670908

BLOUBOU_GUILD_ID = 871155691686088714

ADMIN_ROLE_ID = 871159748135895130
BOT_ROLE_ID = 871356162757509180

CONSTANT_ROLES_NAMES = ["admin", "bot"]

ID_ALIASES = {393762112884965389: ["antoine", "tatane", "antoinette"],
              871145469982670908: ["bloubou"]}


####################
# GLOBAL VARIABLES #
####################


rolesID = {871166312477503488: True,
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
           871168483923230771: True}

bloubouGuild: discord.Guild

commandRegexes = [
    r"(?:change[r|s]?|modifie[s|r]?|transforme[s|r]?) (?:(?:le )?(?:nom|pseudo|pr(?:é|e|è)nom) (?:de |d')?)?(?P<last>.+) (?:en|pour) (?P<new>.+)",
    r"^roles$"
]


###################
# GUILD FUNCTIONS #
###################


def reinitRolesID():
    """ Sets all roles to available """
    global rolesID
    rolesID = {x: True for x in rolesID}


def getRandomRoleID():
    """ Returns a random role id, or -1 if there is no available """
    global rolesID

    roleId, available = random.choice(list(rolesID.items()))
    nbChoices = 0
    while not available and nbChoices < 128:
        roleId, available = random.choice(list(rolesID.items()))
        nbChoices += 1

    if available:
        rolesID[roleId] = False
        return roleId
    return -1


def getRoleByID(roleId):
    """ Searchs a role by his id """
    return discord.utils.get(bloubouGuild.roles, id=roleId)


def getUserByID(userId):
    """ Searchs a user by his id """
    return bloubouGuild.get_member(userId)


def getUserByName(n):
    """ Searchs a user by his name """
    name = tc.normalize(n)
    for user in bloubouGuild.members:
        if tc.normalize(user.name) == name or tc.normalize(user.nick or "") == name or name in ID_ALIASES[user.id]:
            return user
    return None


#####################
# COMMAND FUNCTIONS #
#####################


async def changeName(args, message):
    """ Changes the nick of a user """
    user = getUserByName(args["last"])
    if user is not None:
        await user.edit(nick=args["new"])


async def randomRoles(args, message):
    """ Distributes random role to everyone """
    if message.author.id != ADMIN_ID:
        return

    reinitRolesID()
    for member in message.guild.members:
        printMessage(f"Removing roles from {member}", DEBUG_MESSAGE, True)
        for role in member.roles[1:]:
            if role.name not in CONSTANT_ROLES_NAMES:
                printMessage(f"Removing {role.name}", DEBUG_MESSAGE, True)
                await member.remove_roles(role)
        newRoleID = getRandomRoleID()
        if newRoleID > 0:
            printMessage(f"{member} gets the role id {newRoleID}", DEBUG_MESSAGE, True)
            await member.add_roles(discord.utils.get(message.guild.roles, id=newRoleID))
        else:
            printMessage(f"There is no role available", ERROR_MESSAGE, True)
    printMessage("Roles Done", DEBUG_MESSAGE, True)


async def callCommand(idCommand, args, message):
    """ Calls the specified idCommand command, or returns False """
    commands = {
        0: changeName,
        1: randomRoles
    }
    command = commands.get(idCommand)
    if command is None:
        printMessage(message, ERROR_MESSAGE)
        return False
    await command(args, message)
    return True


#################
# BLOUBOU CLASS #
#################


class Bloubou(discord.Client):

    async def on_ready(self):
        """ Event called when the bot is connected and ready """
        printMessage("ready", DEBUG_MESSAGE, True)
        global bloubouGuild
        bloubouGuild = self.get_guild(BLOUBOU_GUILD_ID)

    async def fetchCommands(self, message: discord.Message):
        """ Reads and executes commands, returns False if no command found """
        commandFound = False

        for iCommand in range(len(commandRegexes)):
            regexResult = re.search(commandRegexes[iCommand], message.content, re.IGNORECASE)
            if regexResult is not None:
                args = regexResult.groupdict()
                commandFound = await callCommand(iCommand, args, message)

        return commandFound

    async def on_message(self, message: discord.Message):
        """ Event called when a message is read """
        # Bot's message
        if message.author == self.user:
            printMessage(message, BOT_MESSAGE)
            return

        # User's message
        if await self.fetchCommands(message):
            printMessage(message, COMMAND_MESSAGE)
        else:
            printMessage(message, USER_MESSAGE)


###############
# BOT RUNNING #
###############


intents = discord.Intents().all()
bot = Bloubou(intents=intents)
bot.run(os.getenv("TOKEN"))
