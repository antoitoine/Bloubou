#####################################
# MAIN FILE OF DISCORD BOTS PROJECT #
#            03/08/21               #
#####################################


from bot import *
from discord.ext import tasks

import discord
from dotenv import load_dotenv
import os

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
    if message.author.id not in pepe.getAdminList():
        return

    pepe.reinitRolesID()
    for member in message.guild.members:
        if member.id in pepe.getBotsID():
            continue
        printMessage(f"Removing roles from {member}", DEBUG_MESSAGE, True)
        for role in member.roles[1:]:
            if role.name not in pepe.getConstantRoles():
                printMessage(f"Removing {role.name}", DEBUG_MESSAGE, True)
                await member.remove_roles(role)
        newRoleID = pepe.getRandomRoleID()
        if newRoleID > 0:
            printMessage(f"{member} gets the role id {newRoleID}", DEBUG_MESSAGE, True)
            await member.add_roles(discord.utils.get(message.guild.roles, id=newRoleID))
        else:
            printMessage(f"There is no role available", ERROR_MESSAGE, True)
    printMessage("Roles Done", DEBUG_MESSAGE, True)


async def stopBot(args, message):
    """ Shutdowns the bot """
    if message.author.id not in pepe.getAdminList():
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


async def onMessage(message):
    normalizedMessage = tc.normalize(message.content)
    if len(normalizedMessage) >= 256:
        return
    db = connectDatabase(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
    with db.cursor() as cursor:
        cursor.execute(f"INSERT INTO Temp (message) VALUES (\"{normalizedMessage}\");")

    if random.randint(1, 3) == 1:
        with db.cursor() as cursor:
            cursor.execute(f"UPDATE Classement SET nb_points = nb_points+1 WHERE discord_id=\"{message.author.id}\"")

    db.commit()


@tasks.loop(seconds=10)
async def updateClassement():
    classementChannel = discord.utils.get(pepe.getGuild().channels, id=CHANNEL_ID_CLASSEMENT)
    messageClassement = await classementChannel.fetch_message(MESSAGE_ID_CLASSEMENT)
    content = ""
    db = connectDatabase(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)

    with db.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM Classement ORDER BY nb_points DESC")
        for row in cursor.fetchall():
            user = pepe.getUserByID(int(row['discord_id']))
            content = content + f"[ {row['nb_points']} ] **{user.nick or user.name}**\n"

    await messageClassement.edit(content=content)


######################
# PEPE CONFIGURATION #
######################


pepe.setGuildID(SERVER_ID)
pepe.addAdmin(USER_ID_ANTOINE)

pepe.addLoopFunction(updateClassement)

pepe.setOnMessage(onMessage)

pepe.setCommand(0, randomRoles, r"^roles$")
pepe.setCommand(1, changeName, r"(?:change[r|s]?|modifie[s|r]?|transforme[s|r]?|renomme[s|r]?) (?:(?:le )?(?:nom|pseudo|pr(?:é|e|è)nom) (?:de |d')?)?(?P<last>.+) (?:en|pour) (?P<new>.+)")
pepe.setCommand(2, stopBot, r"^stop$")
pepe.setCommand(3, giveRole, r"^role (?P<roleID>.+) a (?P<user>.+)")
pepe.setCommand(4, changeRoleColor, r"^colour (?P<roleID>.+)")
pepe.setCommand(5, classement, r"classement")

pepe.run(os.getenv("TOKEN_PEPE"))
