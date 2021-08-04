#######################
# UNIVERSAL BOT CLASS #
#      01/08/21       #
#######################


import discord
import random
import re

import textComputing as tc

from myUtilities import *
from mysql.connector import connect, Error


#############
# BOT CLASS #
#############


class Bot(discord.Client):

    # Member variables

    guildID: int
    commands = []

    loopFunctions = []

    regexes = []
    adminUsersID = []
    idAliases = {}
    constantRoles = []
    rolesID = {
        871166312477503488: True,
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
        871168483923230771: True
    }
    botsID = []

    onVoiceFunction = None
    onMessageFunction = None
    onReadyFunction = None

    database = None

    # Inherited methods

    async def on_ready(self):
        """ Event called when the bot is connected and ready """
        printMessage("ready", DEBUG_MESSAGE, True)

        for foo in self.loopFunctions:
            foo.start()

        if self.onReadyFunction is not None:
            await self.onReadyFunction()

    async def on_message(self, message):
        """ Event called when a message is read """
        if message.author.id in self.botsID:
            printMessage(message, BOT_MESSAGE)
            return

        if await self.fetchCommands(message):
            printMessage(message, COMMAND_MESSAGE)
        else:
            printMessage(message, USER_MESSAGE)

        if self.onMessageFunction is not None:
            await self.onMessageFunction(message)

    async def on_voice_state_update(self, member, before, after):
        """ Called when a user enters or leaves any voice channel """
        if not before.channel and after.channel:
            printMessage(f"Voice channel joined by {member}", MYSC_MESSAGE, True)
        elif before.channel and not after.channel:
            printMessage(f"Voice channel leaved by {member}", MYSC_MESSAGE, True)

        if self.onVoiceFunction is not None:
            await self.onVoiceFunction(member, before, after)

    # Discord methods

    def getUserByName(self, userName):
        """ Searchs a user by his name """
        name = tc.normalize(userName)
        for user in self.getGuild().members:
            if tc.normalize(user.name) == name or tc.normalize(user.nick or "") == name or name in self.idAliases[user.id]:
                return user
        return None

    def getRoleByID(self, roleId):
        """ Searchs a role by his id """
        return discord.utils.get(self.getGuild().roles, id=roleId)

    def getUserByID(self, userId):
        """ Searchs a user by his id """
        return self.getGuild().get_member(userId)

    # Bot methods

    def connectDatabase(self, host, user, password, database):
        """ Opens a new database """
        try:
            self.database = connect(host=host, user=user, password=password, database=database)
        except Error as e:
            printMessage(e, ERROR_MESSAGE, True)
        printMessage(f"Connected to database {database}", DEBUG_MESSAGE, True)

    def disconnectDatabase(self):
        """ Disconnects the database """
        if self.database is not None:
            self.database.close()
            self.database = None
            printMessage("Disconnected from database", DEBUG_MESSAGE, True)
        else:
            printMessage("No database found", ERROR_MESSAGE, True)

    def isDatabaseConnected(self):
        """ Returns True if a database was connected """
        return self.database is not None

    def getDatabase(self):
        """ Returns the database or None """
        return self.database

    async def shutdown(self):
        """ Stops the bot and close the database """
        await self.logout()
        if self.database is not None:
            self.database.close()
            self.database = None

    def reinitRolesID(self):
        """ Sets all roles to available """
        self.rolesID = {x: True for x in self.rolesID}

    def setCommand(self, idCommand, command, regex):
        """ Saves a command at idCommand pos """
        if idCommand > len(self.commands):
            return False
        if idCommand == len(self.commands):
            self.commands.append(command)
            self.regexes.append(regex)
        else:
            self.commands[idCommand] = command
            self.regexes[idCommand] = regex
        return True

    def getRandomRoleID(self):
        """ Returns a random role id, or -1 if there is no available """
        roleId, available = random.choice(list(self.rolesID.items()))
        nbChoices = 0
        while not available and nbChoices < 128:
            roleId, available = random.choice(list(self.rolesID.items()))
            nbChoices += 1

        if available:
            self.rolesID[roleId] = False
            return roleId
        return -1

    async def callCommand(self, idCommand, args, message):
        """ Calls the specified idCommand command, or returns False """
        command = self.commands[idCommand]
        if command is None:
            printMessage(message, ERROR_MESSAGE)
            return False
        await command(args, message)
        return True

    async def fetchCommands(self, message):
        """ Reads and executes commands, returns False if no command found """
        for iCommand in range(len(self.regexes)):
            regexResult = re.search(self.regexes[iCommand], message.content, re.IGNORECASE)
            if regexResult is not None:
                args = regexResult.groupdict()
                if await self.callCommand(iCommand, args, message):
                    return True
        return False

    # Getters and setters

    def addLoopFunction(self, foo):
        self.loopFunctions.append(foo)

    def addBotID(self, botID):
        if botID not in self.botsID:
            self.botsID.append(botID)

    def getBotsID(self):
        return self.botsID

    def setVoiceFunction(self, foo):
        self.onVoiceFunction = foo

    def setOnMessage(self, foo):
        self.onMessageFunction = foo

    def setOnReady(self, foo):
        self.onReadyFunction = foo

    def setAliases(self, userId, aliases):
        self.idAliases[userId] = aliases

    def getIdAliases(self):
        return self.idAliases

    def addConstantRole(self, roleName):
        if roleName not in self.constantRoles:
            self.constantRoles.append(roleName)

    def getConstantRoles(self):
        return self.constantRoles

    def addAdmin(self, adminID):
        if adminID not in self.adminUsersID:
            self.adminUsersID.append(adminID)

    def getAdminList(self):
        return self.adminUsersID

    def setGuildID(self, guildID):
        self.guildID = guildID

    def getGuild(self):
        return self.get_guild(self.guildID)
