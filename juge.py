####################
# JUGE DISCORD BOT #
#     04/08/21     #
####################


from bot import *
from constants import *
from dotenv import load_dotenv
import discord
import os
import random

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

juge = Bot(intents=intents)


#################
# JUGE COMMANDS #
#################


def executeSQL(cursor, sql):
    cursor.execute(sql)
    return cursor.fetchall()[0]


def genVerbe(cursor, sujet, sujetPluriel):
    """ Returns a random verb """
    curVerbe = executeSQL(cursor, "SELECT * FROM Juge WHERE type='verbe' ORDER BY RAND() LIMIT 1")
    verbe = curVerbe["vBase"]
    if sujet == "Tu":
        if verbe == "est":
            verbe = "es"
        elif verbe[-1] == "t":
            verbe = verbe[:-1] + "s"
        else:
            verbe = verbe + "s"
    elif sujet == "Je" and verbe == "a":
        verbe = "ai"
    elif sujetPluriel:
        verbe = curVerbe["vPluriel"]
    return verbe


def genNom(cursor):
    """ Returns name, True if is plural and his genre """
    curNom = executeSQL(cursor, "SELECT * FROM Juge WHERE type='nom' ORDER BY RAND() LIMIT 1")
    nomPluriel = False
    nom = curNom["mot"]
    if random.randint(1, 2) == 1:
        nomPluriel = True
        nom = curNom["pluriel"]
    return (nom, nomPluriel, curNom["genre"])


def genDeterminant(cursor, nomPluriel, genreNom):
    """ Returns a determinant defined by his name """
    curDet = executeSQL(cursor,
                        f"SELECT * FROM Juge WHERE type='determinant' AND genre='{genreNom}' ORDER BY RAND() LIMIT 1")
    det = curDet["mot"]
    if nomPluriel:
        det = curDet["pluriel"]
    return det


def genAdjectif(cursor, nomPluriel, genreNom):
    """ Returns an adjective """
    curAdj = executeSQL(cursor, f"SELECT * FROM Juge WHERE type='adjectif' AND genre='{genreNom}' ORDER BY RAND() LIMIT 1")
    adj = curAdj["mot"]
    if nomPluriel:
        adj = curAdj["pluriel"]
    return adj


def genAdverbe(cursor):
    """ Returns an adjective """
    curAdv = executeSQL(cursor, f"SELECT * FROM Juge WHERE type='adverbe' ORDER BY RAND() LIMIT 1")
    adv = curAdv["mot"]
    return adv


# Phrases


def phrase1(cursor, sujet, sujetPluriel):
    """ Sujet verbe complément """
    verbe = genVerbe(cursor, sujet, sujetPluriel)
    if verbe == "ai" : sujet = "J'"
    (nom, nomPluriel, genreNom) = genNom(cursor)
    det = genDeterminant(cursor, nomPluriel, genreNom)
    if sujet != "J'": sujet = sujet + " "
    return f"{sujet}{verbe} {det} {nom}"


def phrase2(cursor, sujet, sujetPluriel):
    """ Sujet verbe complément adjectif """
    verbe = genVerbe(cursor, sujet, sujetPluriel)
    if verbe == "ai" : sujet = "J'"
    (nom, nomPluriel, genreNom) = genNom(cursor)
    det = genDeterminant(cursor, nomPluriel, genreNom)
    adj = genAdjectif(cursor, nomPluriel, genreNom)
    if sujet != "J'" : sujet = sujet + " "
    return f"{sujet}{verbe} {det} {nom} {adj}"


def phrase3(cursor, sujet, sujetPluriel):
    """ Sujet verbe complément adverbe adjectif """
    verbe = genVerbe(cursor, sujet, sujetPluriel)
    if verbe == "ai" : sujet = "J'"
    (nom, nomPluriel, genreNom) = genNom(cursor)
    det = genDeterminant(cursor, nomPluriel, genreNom)
    adj = genAdjectif(cursor, nomPluriel, genreNom)
    adv = genAdverbe(cursor)
    if sujet != "J'": sujet = sujet + " "
    return f"{sujet}{verbe} {det} {nom} {adv} {adj}"

def phrase4(cursor, sujet, sujetPluriel):
    """ Sujet verbe déterminant adjectif """
    verbe = genVerbe(cursor, sujet, sujetPluriel)
    if verbe == "ai" : sujet = "J'"
    pluriel = random.choice([True, False])
    genre = random.choice(["feminin", "masculin"])
    det = genDeterminant(cursor, pluriel, genre)
    adj = genAdjectif(cursor, pluriel, genre)
    if sujet != "J'": sujet = sujet + " "
    return f"{sujet}{verbe} {det} {adj}"


async def juger(args, message):
    """ Juges a user """
    sujet = args["nom"]
    sujet = re.sub(r" *\?", "", sujet, flags=re.IGNORECASE)
    if re.search(r"^ *moi *$", args["nom"], re.IGNORECASE):
        sujet = "Tu"
    elif re.search(r"^ *toi *$", args["nom"], re.IGNORECASE):
        sujet = "Je"

    sujetPluriel = False
    if re.search(r"(et|les|des|ces|ses|plusieurs|beaucoup)", sujet, re.IGNORECASE) is not None:
        sujetPluriel = True

    db = connectDatabase(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
    with db.cursor(dictionary=True) as cursor:
        aleatoire = random.randint(1, 4)
        jugement = ""
        if   aleatoire == 1 : jugement = phrase1(cursor, sujet, sujetPluriel)
        elif aleatoire == 2 : jugement = phrase2(cursor, sujet, sujetPluriel)
        elif aleatoire == 3 : jugement = phrase3(cursor, sujet, sujetPluriel)
        elif aleatoire == 4 : jugement = phrase4(cursor, sujet, sujetPluriel)

        await message.channel.send(jugement)


######################
# JUGE CONFIGURATION #
######################


juge.guildId = SERVER_ID
juge.adminIds = [USER_ID_ANTOINE]

juge.botCommands = [
    BotCommand(juger, r"juge[r|s]? (?P<nom>.+)")
]

juge.run(os.getenv("TOKEN_JUGE"))
