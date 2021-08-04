#####################################
# MAIN FILE OF DISCORD BOTS PROJECT #
#            03/08/21               #
#####################################


from bot import *
import discord
from dotenv import load_dotenv
import os

load_dotenv()


#############
# CONSTANTS #
#############


USER_ID_ANTOINE = 393762112884965389
USER_ID_BLOUBOU = 871145469982670908

SERVER_ID_BLOUBOU = 871155691686088714


################
# BOT CREATION #
################


intents = discord.Intents().all()

bloubou = Bot(intents=intents)


####################
# BLOUBOU COMMANDS #
####################


async def changeName(args, message):
    """ Changes the nick of a user """
    user = bloubou.getUserByName(args["last"])
    if user is not None:
        await user.edit(nick=args["new"])


async def randomRoles(args, message):
    """ Distributes random role to everyone """
    if message.author.id not in bloubou.getAdminList():
        return

    bloubou.reinitRolesID()
    for member in message.guild.members:
        printMessage(f"Removing roles from {member}", DEBUG_MESSAGE, True)
        for role in member.roles[1:]:
            if role.name not in bloubou.getConstantRoles():
                printMessage(f"Removing {role.name}", DEBUG_MESSAGE, True)
                await member.remove_roles(role)
        newRoleID = bloubou.getRandomRoleID()
        if newRoleID > 0:
            printMessage(f"{member} gets the role id {newRoleID}", DEBUG_MESSAGE, True)
            await member.add_roles(discord.utils.get(message.guild.roles, id=newRoleID))
        else:
            printMessage(f"There is no role available", ERROR_MESSAGE, True)
    printMessage("Roles Done", DEBUG_MESSAGE, True)


async def stopBot(args, message):
    """ Shutdowns the bot """
    if message.author.id not in bloubou.getAdminList():
        return

    await bloubou.logout()


#########################
# BLOUBOU CONFIGURATION #
#########################


bloubou.setGuildID(SERVER_ID_BLOUBOU)
bloubou.addAdmin(USER_ID_ANTOINE)

bloubou.addConstantRole("admin")
bloubou.addConstantRole("bot")

bloubou.setAliases(USER_ID_ANTOINE, ["antoine", "tatane", "antoinette"])
bloubou.setAliases(USER_ID_BLOUBOU, ["bloubou"])

bloubou.setCommand(0, randomRoles, r"^roles$")
bloubou.setCommand(1, changeName, r"(?:change[r|s]?|modifie[s|r]?|transforme[s|r]?) (?:(?:le )?(?:nom|pseudo|pr(?:é|e|è)nom) (?:de |d')?)?(?P<last>.+) (?:en|pour) (?P<new>.+)")
bloubou.setCommand(2, stopBot, r"^stop$")

bloubou.run(os.getenv("TOKEN_BLOUBOU"))
