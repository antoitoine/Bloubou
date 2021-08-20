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
    elif sujet == "Je":
        if verbe == "a":
            verbe = "ai"
        elif verbe[-1] == "d":
            verbe = verbe + "s"
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
    return nom, nomPluriel, curNom["genre"]


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
    curAdj = executeSQL(cursor, f"SELECT * FROM Juge WHERE (type='adjectif' AND genre='{genreNom}') OR (type='verbe' AND vParticipe!='None') ORDER BY RAND() LIMIT 1")
    if curAdj["type"] == "adjectif":  # Adjectif
        adj = curAdj["mot"]
        if nomPluriel:
            adj = curAdj["pluriel"]
    else:  # Participe
        adj = curAdj["vParticipe"]
        if genreNom == "feminin":
            adj = adj + "e"
        if nomPluriel:
            adj = adj + "s"

    return adj


def genAdverbe(cursor, genre):
    """ Returns an adjective """
    curAdv = executeSQL(cursor, f"SELECT * FROM Juge WHERE type='adverbe' AND (genre='neutre' OR genre='{genre}') ORDER BY RAND() LIMIT 1")
    adv = curAdv["mot"]
    return adv


def genPhrase(cursor, sujet, sujetPluriel):
    """ Sujet verbe complément ((adv) adj) (qui verbe complément ((adv) adj)) """
    phrase = ""
    verbe = genVerbe(cursor, sujet, sujetPluriel)  # Verbe
    if verbe == "ai":
        sujet = "J'"
    if sujet != "J'":
        sujet = sujet + " "
    phrase = phrase + sujet + verbe
    (nom, nomPluriel, genreNom) = genNom(cursor)  # Nom
    det = genDeterminant(cursor, nomPluriel, genreNom)
    phrase = phrase + " " + det + " " + nom
    if random.randint(1, 2) == 1:  # Adverbe et adjectif
        if random.randint(1, 3) == 1:
            phrase = phrase + " " + genAdverbe(cursor, genreNom)
        phrase = phrase + " " + genAdjectif(cursor, nomPluriel, genreNom)
    if random.randint(1, 2) == 1:  # Qui + subordonnée
        verbe = genVerbe(cursor, nom, nomPluriel)
        (nom, nomPluriel, genreNom) = genNom(cursor)
        det = genDeterminant(cursor, nomPluriel, genreNom)
        phrase = phrase + " qui " + verbe + " " + det + " " + nom
        if random.randint(1, 2) == 1:  # Adverbe et adjectif
            if random.randint(1, 3):
                phrase = phrase + " " + genAdverbe(cursor, genreNom)
            phrase = phrase + " " + genAdjectif(cursor, nomPluriel, genreNom)
    return phrase


async def juger(args, message):
    """ Juges a user """
    sujet = args["nom"]
    sujet = re.sub(r"[?!.$]", "", sujet, flags=re.IGNORECASE)
    sujet = re.sub(r" +", " ", sujet)
    sujet = sujet.strip()
    if len(sujet) > 1:
        sujet = sujet[0].upper() + sujet[1:]
    if re.search(r"^ *moi *$", args["nom"], re.IGNORECASE):
        sujet = "Tu"
    elif re.search(r"^ *toi *$", args["nom"], re.IGNORECASE):
        sujet = "Je"

    if len(sujet) <= 1:
        await message.channel.send("Oui ?")
        return

    sujetPluriel = False
    if re.search(r"(et|les|des|ces|ses|plusieurs|beaucoup|2|deux)", sujet, re.IGNORECASE) is not None:
        sujetPluriel = True

    db = connectDatabase(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
    with db.cursor(dictionary=True) as cursor:
        jugement = genPhrase(cursor, sujet, sujetPluriel)
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
