import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

import discord
from discord.utils import get

import os, asyncio

cred = credentials.Certificate("serviceAccount.json")
firebase_admin.initialize_app(cred)

db = firestore.client()


TOKEN = os.getenv("snipesbot_token")

THUMBS_UP = "👍"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

def get_message_ref(channel_id, message_id):
    return db.collection(str(channel_id)).document(str(message_id))

def get_user_ref(channel_id, user_id):
    return db.collection(str(channel_id)).document("users").collection(str(user_id)).document("values")


def upvote(message, person_id):
    message_ref = get_message_ref(message.channel.id, message.id)
    message_data = message_ref.get()

    newdata = {
        "image_link":message.attachments[0].url,
        "upvotes":[]
    }

    if message_data.exists:
        if "upvotes" in message_data.to_dict():
            newdata["upvotes"] = message_data.to_dict()["upvotes"]

        if person_id in newdata["upvotes"]:
            return

    newdata["upvotes"].append(person_id)

    message_ref.set(newdata)


    user_ref = get_user_ref(message.channel.id, message.author.id)
    user_data = user_ref.get()

    if user_data.exists:
        data = user_data.to_dict()
        if "snipes" not in data:
            data["snipes"] = 1
        else:
            data["snipes"] += 1

        user_ref.set(data)

    else:
        user_ref.set({"snipes":1})


def downvote(message, person_id):
    message_ref = get_message_ref(message.channel.id, message.id)
    message_data = message_ref.get()

    if not message_data.exists:
        return

    newdata = message_data.to_dict()
    if "upvotes" not in newdata:
        return

    if person_id not in newdata["upvotes"]:
        return

    newdata["upvotes"] = [i for i in newdata["upvotes"] if i != person_id]

    message_ref.set(newdata)


    user_ref = get_user_ref(message.channel.id, message.author.id)
    user_data = user_ref.get()

    if user_data.exists:
        data = user_data.to_dict()
        if "snipes" not in data:
            data["snipes"] = 0
        else:
            data["snipes"] = max(data["snipes"]-1, 0)

        user_ref.set(data)

    else:
        user_ref.set({"snipes":0})
    

def get_leaderboard(channel_id):
    ref = db.collection(str(channel_id)).document("users")

    members = []

    for c in ref.collections():
        members.append([str(c.id), c.document("values").get().to_dict().get("snipes", 0)])

    members.sort(key=lambda x: x[1], reverse=True)

    members = members[:10]

    return members

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.channel.name == "snipes":
        if message.content == "!leaderboard":
            top10 = get_leaderboard(message.channel.id)

            if top10 == []:
                await message.channel.send("No users yet!")
                return

            response = ""

            for idx, (user_id, _) in enumerate(top10):
                user = await client.fetch_user(user_id)
                response += f"{idx+1}. {user}\n"

            await message.channel.send(response)

            return
        
        if message.attachments and not message.author.bot:
            await message.add_reaction(THUMBS_UP)


@client.event
async def on_raw_reaction_add(data):
    channel = client.get_channel(data.channel_id)
    if channel.name == "snipes":
        message = await channel.fetch_message(data.message_id)

        if message.attachments and data.emoji.name == THUMBS_UP and not data.member.bot:
            upvote(message, data.member.id)


@client.event
async def on_raw_reaction_remove(data):
    channel = client.get_channel(data.channel_id)
    if channel.name == "snipes":
        message = await channel.fetch_message(data.message_id)

        if message.attachments and data.emoji.name == THUMBS_UP:
            downvote(message, data.user_id)


client.run(TOKEN)
