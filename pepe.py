#####################################
# MAIN FILE OF DISCORD BOTS PROJECT #
#            03/08/21               #
#####################################


from bot import *
from discord.ext import tasks

import discord
from dotenv import load_dotenv
import os
import textComputing as tc
import asyncio

load_dotenv()


#############
# CONSTANTS #
#############


USER_ID_ANTOINE = 393762112884965389
SERVER_ID = 871155691686088714
CHANNEL_ID_CLASSEMENT = 872486010569760828
MESSAGE_ID_CLASSEMENT = 872594120324038726


################
# BOT CREATION #
################


intents = discord.Intents().all()
pepe = Bot(intents=intents)

lastMessage = ""
lastAuthor = None

apprendreMode = False


#################
# PEPE COMMANDS #
#################


async def changeName(args, message):
    """ Changes the nick of a user """
    user = pepe.getUserByName(args["last"])
    if user is not None:
        await user.edit(nick=args["new"])


async def randomRoles(args, message):
    """ Distributes random role to everyone """
    if message.author.id not in pepe.adminIds:
        return

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

    for member in message.guild.members:
        if member.id in pepe.botIds:
            continue
        printMessage(f"Removing roles from {member}", DEBUG_MESSAGE, True)
        for role in member.roles[1:]:
            if role.name not in pepe.constantRoles:
                printMessage(f"Removing {role.name}", DEBUG_MESSAGE, True)
                await member.remove_roles(role)

        # Random role
        roleId, available = random.choice(list(rolesID.items()))
        nbChoices = 0
        while not available and nbChoices < 128:
            roleId, available = random.choice(list(rolesID.items()))
            nbChoices += 1

        if available:
            rolesID[roleId] = False
            newRoleID = roleId
        else:
            newRoleID = 0

        # Give role
        if newRoleID > 0:
            printMessage(f"{member} gets the role id {newRoleID}", DEBUG_MESSAGE, True)
            await member.add_roles(discord.utils.get(message.guild.roles, id=newRoleID))
        else:
            printMessage(f"There is no role available", ERROR_MESSAGE, True)
    printMessage("Roles Done", DEBUG_MESSAGE, True)


async def stopBot(args, message):
    """ Shutdowns the bot """
    if message.author.id not in pepe.adminIds:
        return
    await pepe.shutdown()


async def giveRole(args, message):
    role = pepe.getRoleByID(int(args["roleID"]))
    user = pepe.getUserByName(args["user"])
    await user.add_roles(role)


async def changeRoleColor(args, message):
    role = pepe.getRoleByID(int(args["roleID"]))
    await role.edit(colour=discord.Colour(int("0xa53dd4", 16)))


async def classement(args, message):
    db = connectDatabase(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
    with db.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM Classement")
        for row in cursor.fetchall():
            await message.channel.send(row)


def enregistrerReponse(question, reponse):
    db = connectDatabase(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
    with db.cursor() as cursor:
        for q in tc.tokenize(question):
            cursor.execute(
                f"INSERT INTO PepeMessages (question, answer) VALUES (\"{q}\", \"{reponse}\") ON DUPLICATE KEY UPDATE poids=poids+1;")
    db.commit()
    db.close()


async def onMessage(message):
    if len(message.content) >= 256:
        return

    global lastMessage, lastAuthor
    normalizedMessage = tc.normalize(message.content)

    # Learn new answers
    if message.author != pepe.user and message.author != lastAuthor and len(lastMessage) > 0:
        enregistrerReponse(lastMessage, message.content)

    # Update classement
    if random.randint(1, 3) == 1:
        db = connectDatabase(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
        with db.cursor() as cursor:
            cursor.execute(f"UPDATE Classement SET nb_points = nb_points+1 WHERE discord_id=\"{message.author.id}\"")
        db.commit()
        db.close()

    # Answer to message
    reponsePepe = ""
    if message.author != pepe.user:
        reponsePepe = await genererReponse(normalizedMessage)
    if len(reponsePepe) > 0:
        voiceClient = pepe.guild.voice_client
        if (message.author.voice is not None and voiceClient is not None):
            pepe.readVoiceMessage(reponsePepe)
        else:
            async with message.channel.typing():
                await asyncio.sleep(2)
            reponseMessage = await message.channel.send(reponsePepe)
            if apprendreMode:
                await reponseMessage.add_reaction("👍")
                await reponseMessage.add_reaction("👎")
        lastMessage = reponsePepe
        lastAuthor = pepe.user
    else:
        lastMessage = normalizedMessage
        lastAuthor = message.author


async def viens(args, message):
    if message.author.voice is not None:
        await message.author.voice.channel.connect()


async def genererReponse(question):
    query = "SELECT * FROM PepeMessages WHERE"
    for token in tc.tokenize(question):
        query = f"{query} question=\"{token}\" OR"
    query = query[:-3]

    answers = {}
    db = connectDatabase(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
    with db.cursor(dictionary=True) as cursor:
        cursor.execute(query)
        for row in cursor.fetchall():
            if row["answer"] in answers.keys():
                answers[row["answer"]] += int(row["poids"])
            else:
                answers[row["answer"]] = int(row["poids"])

    if len(answers) > 0:
        minPoids = min(list(answers.values()))
        poids = [x + abs(minPoids) + 1 for x in answers.values()]  # Remove negative weights
        answer = ''.join(random.choices(list(answers.keys()), poids))
        return answer
    return ""


async def pars(args, message):
    vc = pepe.getVoiceClient()
    if vc is not None:
        await vc.disconnect()


async def toogleMode(args, message):
    global apprendreMode
    apprendreMode = not apprendreMode


async def deleteLastMessage(args, message):
    msg = await pepe.getLastMessage(message.channel)
    await msg.delete()
    await message.delete()


@tasks.loop(minutes=5.0)
async def updateClassement():
    classementChannel = discord.utils.get(pepe.guild.channels, id=CHANNEL_ID_CLASSEMENT)
    messageClassement = await classementChannel.fetch_message(MESSAGE_ID_CLASSEMENT)
    content = "**SUPER CLASSEMENT DE LA MORT**\n"
    db = connectDatabase(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)

    with db.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM Classement ORDER BY nb_points DESC")
        posClassement = 1
        for row in cursor.fetchall():
            user = pepe.getUserByID(int(row['discord_id']))
            medal = ":medal:"
            if posClassement == 1:
                medal = ":first_place:"
            elif posClassement == 2:
                medal = ":second_place:"
            elif posClassement == 3:
                medal = ":third_place:"
            content = content + f"{medal}   **{row['nb_points']}pts**   <@{user.id}>\n"
            posClassement += 1

    await messageClassement.edit(content=content)


async def onReaction(reaction, user, lastMessage):
    if user == pepe.user:
        return

    modifScore = 0

    if reaction.emoji == "👍":
        modifScore = 1
    elif reaction.emoji == "👎":
        modifScore = -1

    if modifScore != 0:
        db = connectDatabase(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
        with db.cursor() as cursor:
            query = f"UPDATE PepeMessages SET poids=poids+{modifScore} WHERE ("
            for token in tc.tokenize(lastMessage.content):
                query = f"{query}question=\"{token}\" OR "
            query = query[:-4]
            query =f"{query}) AND answer=\"{reaction.message.content}\""
            printMessage(query, DEBUG_MESSAGE, True)
            cursor.execute(query)
        db.commit()

######################
# PEPE CONFIGURATION #
######################


pepe.guildId = SERVER_ID
pepe.adminIds = [USER_ID_ANTOINE]
pepe.initVoice("HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\MSTTS_V110_frFR_PaulM", 150)

pepe.loopFunctions = [updateClassement]

pepe.onMessageFunction = onMessage
pepe.onReactFunction = onReaction

pepe.botCommands = [
    BotCommand(randomRoles, r"^roles$"),
    BotCommand(changeName, r"(?:change[r|s]?|modifie[s|r]?|transforme[s|r]?|renomme[s|r]?) (?:(?:le )?(?:nom|pseudo|pr(?:é|e|è)nom) (?:de |d')?)?(?P<last>.+) (?:en|pour) (?P<new>.+)"),
    BotCommand(stopBot, r"^stop$"),
    BotCommand(giveRole, r"^role (?P<roleID>.+) a (?P<user>.+)"),
    BotCommand(changeRoleColor, r"^colour (?P<roleID>.+)"),
    BotCommand(classement, r"classement"),
    BotCommand(viens, r"(?:vien[s|t]?.+(?:pepe|pap[i|y])|(?:pepe|pap[i|y]).+vien[s|t]?)"),
    BotCommand(pars, r"par[s|t].+(?:pepe|pap[i|y])|(?:pepe|pap[i|y]).+par[s|t]"),
    BotCommand(toogleMode, r"change[s|r]?.+modes?"),
    BotCommand(deleteLastMessage, r"(?:supprime[s|r]?|enl[e|è]ve[r|s]?).+messages?")
]

pepe.run(os.getenv("TOKEN_PEPE"))
