import os
import random
import rsa
import base64
from io import StringIO  

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

client.voting = False
client.votes = []
client.key = 1

# Given votes and the decrypting key, this function generates two strings.
# summary will contain how many votes each option got.
# full_output will contain votes and identifiers but not the random noise.
def count_votes_and_generate_output(vote_list,priv_key):
    file_output = ""
    summary_output = ""
    votes = {}
    for vote in vote_list:
        snack = base64.b64decode(vote.encode("ascii"))
        dec_vote = rsa.decrypt(snack,priv_key)
        decoded = dec_vote.decode("ascii").split('-')
        file_output += decoded[0] + "-" + decoded[1]
        file_output += "\n"
        vote_key = decoded[0].strip().lower()

        if vote_key in votes:
            votes[vote_key] += 1
        else:
            votes[vote_key] = 1

    for key in votes:
        summary_output += "{} got {} votes".format(key,votes[key])
        summary_output += "\n"

    return (summary_output,file_output)


@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if '!!endvote' in message.content:
        if client.voting:
            
            #shuffle to remove original ordering
            random.shuffle(client.votes)

            #count votes and prepare outputs
            summary_out,file_out = count_votes_and_generate_output(client.votes,client.key)
            out_file = discord.File(StringIO(file_out),filename="results.txt")

            #flush data from voting session
            client.key = 1
            client.votes = []
            client.voting = False

            await message.channel.send(content=summary_out,file=out_file)
        else:
            await message.channel.send("A vote has not been started.")

    if '!!startvote' in message.content:
        if client.voting:
            await message.channel.send("A vote is already ongoing.")
        else:
            client.voting = True
            pub_key, client.key = rsa.newkeys(1024)
            output = """
            @here A vote has been started! Use the key below and https://8gwifi.org/rsafunctions.jsp to send in your vote.\n
            Format your vote like this vote-identifier-random_padding\n\n
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