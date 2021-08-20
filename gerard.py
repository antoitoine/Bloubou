######################
# GERARD DISCORD BOT #
#      05/08/21      #
######################
import difflib

from bot import *
from dotenv import load_dotenv
import discord
import os
from myUtilities import *
import difflib
import asyncio

load_dotenv()


#############
# CONSTANTS #
#############


USER_ID_ANTOINE = 393762112884965389

SERVER_ID = 871155691686088714

GERARD_CHANNEL_ID = 872484253764579338


################
# BOT CREATION #
################


intents = discord.Intents().all()

gerard = Bot(intents=intents)


###################
# GERARD COMMANDS #
###################


async def on_message(message):
    if message.author == gerard.user:
        return
    db = connectDatabase(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)

    if message.channel.id == GERARD_CHANNEL_ID:
        splittedMessage = message.content.split("=")
        if len(splittedMessage) != 2:
            await message.delete()
            return
        question = tc.normalize(splittedMessage[0].strip())
        reponse = splittedMessage[1].strip()


        with db.cursor() as cursor:
            print(question, reponse, message.id)
            cursor.execute(f"INSERT INTO Gerard (question, reponse, idMessage) VALUES ('{question}', '{reponse}', '{message.id}')")
        db.commit()
    elif gerard.activated:
        question = tc.normalize(message.content)
        with db.cursor(dictionary=True) as cursor:
            cursor.execute(f"SELECT * FROM Gerard")
            questionsConnues = []
            for row in cursor.fetchall():
                questionsConnues.append(row["question"])
            questionProche = difflib.get_close_matches(question, questionsConnues, cutoff=0)[0]
            cursor.execute(f"SELECT * FROM Gerard WHERE question='{questionProche}' ORDER BY RAND() LIMIT 1")
            reponse = cursor.fetchall()[0]["reponse"]
            async with message.channel.typing():
                await asyncio.sleep(1)
            await message.channel.send(reponse)

    db.commit()
    db.close()


async def on_raw_message_delete(payload):
    if payload.channel_id == GERARD_CHANNEL_ID:
        db = connectDatabase(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
        with db.cursor() as cursor:
            cursor.execute(f"DELETE FROM Gerard WHERE idMessage='{payload.message_id}'")
        db.commit()


async def on_raw_message_edit(payload):
    if payload.channel_id == GERARD_CHANNEL_ID:
        splittedMessage = payload.data["content"].split("=")
        if len(splittedMessage) != 2:
            return
        question = tc.normalize(splittedMessage[0].strip())
        reponse = splittedMessage[1].strip()
        db = connectDatabase(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
        with db.cursor() as cursor:
            cursor.execute(f"UPDATE Gerard SET question='{question}', reponse='{reponse}' WHERE idMessage='{payload.message_id}'")
        db.commit()

########################
# GERARD CONFIGURATION #
########################
# todo compter nombre message a supprimer commande

gerard.guildId = SERVER_ID
gerard.adminIds = [USER_ID_ANTOINE]
gerard.botNames = ["gege", "gerard"]
gerard.stopAnsweringWords = ["chut", "tais", "ferme", "gueule", "bouche", "taire", "fermer", "boucle", "fermez", "bouclez", "taisez", "tait"]

gerard.onMessageFunction = on_message
gerard.onRawMessageDelete = on_raw_message_delete
gerard.onRawMessageEdit = on_raw_message_edit

gerard.run(os.getenv("TOKEN_GERARD"))
