import os
import random
import rsa
import base64

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

client.voting = False
client.votes = []
client.key = 1

@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if '!!endvote' in message.content:
        if client.voting:
            client.voting = False
            random.shuffle(client.votes)
            output = ""
            for vote in client.votes:
                snack = base64.b64decode(vote.encode("ascii"))
                dec_vote = rsa.decrypt(snack,client.key)
                output += dec_vote.decode("ascii")
                output += "\n"
            client.key = 1
            await message.channel.send(output)
        else:
            await message.channel.send("A vote has not been started.")

    if '!!startvote' in message.content:
        if client.voting:
            await message.channel.send("A vote is already ongoing.")
        else:
            client.voting = True
            pub_key, client.key = rsa.newkeys(1024)
            output = """
            A vote has been started! Use the key below and https://8gwifi.org/rsafunctions.jsp to send in your vote. \n\n
            """ + "Here is the key:\n"+pub_key.save_pkcs1().decode("utf-8")
            
            await message.channel.send(output)

    if '!!vote' in message.content:
        if client.voting:
            content = message.content.split()[1]
            client.votes.append(content)
            print("vote cast")
        else:
            await message.channel.send("A vote has not been started.")
            pass

client.run(TOKEN)