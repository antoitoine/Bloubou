#######################
# UNIVERSAL BOT CLASS #
#      01/08/21       #
#######################


import discord
import re
import pyttsx3

import textComputing as tc

from gtts import gTTS
from myUtilities import *
from constants import *
from dataclasses import dataclass
from typing import Callable, Awaitable, List
from datetime import datetime


####################
# COMMANDS GESTION #
####################


@dataclass
class BotCommand:
    command: Callable[[list, discord.Message], Awaitable[None]]
    regex: str
    channelId: int = 0
    adminMode: bool = False


#############
# BOT CLASS #
#############


class Bot(discord.Client):

    # Inherited methods

    def __init__(self, **options):
        super().__init__(**options)

        self._guildID = 0

        self._botCommands: List[BotCommand] = []
        self._activated = False
        self._lastActivation = datetime.now()

        self._adminUsersID = []
        self._constantRoles = []
        self._botIds = []
        self._aliases = {}
        self._botNames = []
        self._stopAnsweringWords = []

        self._loopFunctions = []
        self._onVoiceFunction = None
        self._onMessageFunction = None
        self._onReadyFunction = None
        self._onReactFunction = None
        self._onRawMessageDelete = None
        self._onRawMessageEdit = None
        self._sendAnswer = None

        self.engine = pyttsx3.init()

    async def on_ready(self):
        """ Event called when the bot is connected and ready """
        printMessage("ready", DEBUG_MESSAGE, True)

        self.loadAliases()
        self.loadConstantRoles()
        self.loadBotIds()

        for foo in self.loopFunctions:
            foo.start()

        if self.onReadyFunction is not None:
            await self.onReadyFunction()

    async def on_message(self, message):
        """ Event called when a message is read """
        message.content = re.sub(r"’", "'", message.content)
        botMessage = message.author.id in self.botIds

        if not botMessage and await self.fetchCommands(message): # If command sent
            printMessage(message, COMMAND_MESSAGE)
            return
        else:
            # Activation
            if message.author != self.user:
                splittedMessage = tc.normalize(message.content).split()
                if any(x in splittedMessage for x in self.stopAnsweringWords):
                    self.activated = False
                elif any(x in splittedMessage for x in self.botNames):
                    self.activated = True

                sinceLastMessage = (datetime.now() - self._lastActivation).seconds
                self._lastActivation = datetime.now()
                if self._activated and sinceLastMessage >= 30:
                    self._activated = False

            if botMessage:
                printMessage(message, BOT_MESSAGE)
            else:
                printMessage(message, USER_MESSAGE)

        if self.onMessageFunction is not None:
            await self.onMessageFunction(message)
        if self.user != message.author and self.activated and self.sendAnswer is not None:
            await self.sendAnswer(message)

    async def on_voice_state_update(self, member, before, after):
        """ Called when a user enters or leaves any voice channel """
        if not before.channel and after.channel:
            printMessage(f"Voice channel joined by {member}", MYSC_MESSAGE, True)
        elif before.channel and not after.channel:
            printMessage(f"Voice channel leaved by {member}", MYSC_MESSAGE, True)

        if self.onVoiceFunction is not None:
            await self.onVoiceFunction(member, before, after)

    async def on_reaction_add(self, reaction, user):
        if self.onReactFunction is not None:
            await self.onReactFunction(reaction, user, await self.getLastMessage(reaction.message.channel))

    async def on_raw_message_delete(self, payload):
        if self.onRawMessageDelete is not None:
            await self.onRawMessageDelete(payload)

    async def on_raw_message_edit(self, playload):
        if self.onRawMessageEdit is not None:
            await self.onRawMessageEdit(playload)

    # Discord methods

    async def getLastMessage(self, channel):
        """ Returns the message before current message """
        msg = await channel.history(limit=2).flatten()
        return msg[1]

    def getUserByName(self, userName):
        """ Searchs a user by his name """
        name = tc.normalize(userName or "")
        for user in self.get_guild(self._guildID).members:
            if tc.normalize(user.name) == name or tc.normalize(user.nick or "") == name or \
                    (str(user.id) in self.aliases and name in self.aliases[str(user.id)]):
                return user
        return None

    def getRoleByID(self, roleId):
        """ Searchs a role by his id """
        return discord.utils.get(self.get_guild(self._guildID).roles, id=roleId)

    def getUserByID(self, userId):
        """ Searchs a user by his id """
        return self.get_guild(self._guildID).get_member(userId)

    # Bot methods

    def getVoiceClient(self):
        for vc in self.voice_clients:
            if vc.guild == self.guild:
                return vc
        return None

    def initVoice(self, voiceId, voiceRate):
        self.engine.setProperty("rate", voiceRate)
        self.engine.setProperty("voice", voiceId)

    def readVoiceMessage(self, message):

        tts = gTTS(message, lang="fr")
        tts.save('tmp.mp3')
        voiceClient = self.get_guild(self._guildID).voice_client
        voiceClient.play(discord.FFmpegPCMAudio(source="tmp.mp3"))

    def loadAliases(self):
        db = connectDatabase(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
        with db.cursor(dictionary=True) as cursor:
            cursor.execute('SELECT * FROM Aliases')
            for row in cursor.fetchall():
                if row['discord_id'] in self.aliases:
                    self.aliases[row['discord_id']].append(row['alias'])
                else:
                    self.aliases[row['discord_id']] = [row['alias']]
        db.close()

    def loadConstantRoles(self):
        db = connectDatabase(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
        with db.cursor(dictionary=True) as cursor:
            cursor.execute('SELECT * FROM ConstantRoles')
            for row in cursor.fetchall():
                self.constantRoles.append(row['role'])
        db.close()

    def loadBotIds(self):
        db = connectDatabase(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
        with db.cursor(dictionary=True) as cursor:
            cursor.execute('SELECT * FROM BotIds')
            for row in cursor.fetchall():
                self.botIds.append(int(row['discord_id']))
        db.close()

    async def shutdown(self):
        """ Stops the bot and close the database """
        await self.logout()

    async def callCommand(self, idCommand, args, message):
        """ Calls the specified idCommand command, or returns False """
        command = self.botCommands[idCommand].command
        if command is None:
            printMessage(message, ERROR_MESSAGE)
            return False
        await command(args, message)
        return True

    async def fetchCommands(self, message):
        """ Reads and executes commands, returns False if no command found """
        for iCommand in range(len(self.botCommands)):
            if self.botCommands[iCommand].channelId != 0 and message.channel.id != self.botCommands[iCommand].channelId:
                continue
            elif self.botCommands[iCommand].adminMode and message.author.id not in self.adminIds:
                continue
            regexResult = re.search(self.botCommands[iCommand].regex, message.content + '\n', re.IGNORECASE)
            if regexResult is not None:
                args = regexResult.groupdict()
                if await self.callCommand(iCommand, args, message):
                    return True
        return False

    # Getters and setters

    @property
    def onReactFunction(self):
        return self._onReactFunction

    @onReactFunction.setter
    def onReactFunction(self, foo):
        self._onReactFunction = foo

    @property
    def loopFunctions(self):
        return self._loopFunctions

    @loopFunctions.setter
    def loopFunctions(self, foos):
        self._loopFunctions = foos

    @property
    def botIds(self):
        return self._botIds

    @property
    def onVoiceFunction(self):
        return self._onVoiceFunction

    @onVoiceFunction.setter
    def onVoiceFunction(self, foo):
        self._onVoiceFunction = foo

    @property
    def onMessageFunction(self):
        return self._onMessageFunction

    @onMessageFunction.setter
    def onMessageFunction(self, foo):
        self._onMessageFunction = foo

    @property
    def onReadyFunction(self):
        return self._onReadyFunction

    @onReadyFunction.setter
    def onReadyFunction(self, foo):
        self._onReadyFunction = foo

    @property
    def aliases(self):
        return self._aliases

    @aliases.setter
    def aliases(self, a):
        self._aliases = a

    @property
    def constantRoles(self):
        return self._constantRoles

    @constantRoles.setter
    def constantRoles(self, roles):
        self._constantRoles = roles

    @property
    def adminIds(self):
        return self._adminUsersID

    @adminIds.setter
    def adminIds(self, ids):
        self._adminUsersID = ids

    @property
    def guild(self):
        return self.get_guild(self.guildId)

    @property
    def guildId(self):
        return self._guildID

    @guildId.setter
    def guildId(self, gId):
        self._guildID = gId

    @property
    def botCommands(self):
        return self._botCommands

    @botCommands.setter
    def botCommands(self, commands):
        self._botCommands = commands

    @property
    def onRawMessageDelete(self):
        return self._onRawMessageDelete

    @onRawMessageDelete.setter
    def onRawMessageDelete(self, foo):
        self._onRawMessageDelete = foo

    @property
    def onRawMessageEdit(self):
        return self._onRawMessageEdit

    @onRawMessageEdit.setter
    def onRawMessageEdit(self, foo):
        self._onRawMessageEdit = foo

    @property
    def activated(self):
        return self._activated

    @activated.setter
    def activated(self, a):
        self._activated = a

    @property
    def sendAnswer(self):
        return self._sendAnswer

    @sendAnswer.setter
    def sendAnswer(self, foo):
        self._sendAnswer = foo

    @property
    def botNames(self):
        return self._botNames

    @botNames.setter
    def botNames(self, names):
        self._botNames = names

    @property
    def stopAnsweringWords(self):
        return self._stopAnsweringWords

    @stopAnsweringWords.setter
    def stopAnsweringWords(self, words):
        self._stopAnsweringWords = words
