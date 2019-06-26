
import discord
from discord.ext import commands
import queries
import stats
import os
import time
import asyncio

TOKEN = queries.read_file('disc_token.txt')
CLIENT = commands.Bot(command_prefix="/")
USERS = {}

# -------------------------------------------------
# Helpers
# -------------------------------------------------

'''
Send a message with formatting to the given channel
'''
async def send_message(channel, msg):
    add_ticks = "```" + msg + "```"
    await CLIENT.send_message(channel, add_ticks)

# -------------------------------------------------
# Handlers - actual functionality of the bot
# -------------------------------------------------

'''
Command:
/add disc_name sum_name

Functionality:
Add summoner associated with a discord account to be tracked by Baron Bot
'''
@CLIENT.command(pass_context=True)
async def add(ctx, disc_name, sum_name):
    global USERS
    if disc_name not in USERS:
        USERS[disc_name] = [sum_name]
        queries.write_file('users.txt', disc_name + " " + sum_name + '\n')
        await send_message(ctx.message.channel, f"Added {sum_name}")
    elif sum_name in USERS.values():
        await send_message(ctx, f"Already added {sum_name}")
    else:
        USERS[disc_name].append(sum_name)
        queries.write_file('users.txt', disc_name + " " + sum_name + '\n')
        await send_message(ctx.message.channel, f"Added {sum_name}")
 
'''
Command:
/check [summoner_1] [summoner_2] ... [summoner_n]

Functionality:
Checks whether summoner(s) are being tracked
'''
@CLIENT.command(pass_context=True)
async def check(ctx, *args):
    global USERS
    if len(args) != 0:
        added = []
        not_added = []
        for u in args:
            if u in USERS.values():
                added.append(u)
            else:
                not_added.append(u)
        msg = f'Added: {", ".join(added)}\nNot Added: {", ".join(not_added)}'
        await send_message(ctx.message.channel, msg)

'''
Command:
/remove [summoner_1] [summoner_2] ... [summoner_n]

Functionality:
Removes users from the system
'''
@CLIENT.command(pass_context=True)
async def remove(ctx, *args):
    global USERS
    new_users = {}
    if len(args) != 0:
        discs_to_keep = []
        for disc_name in USERS.keys():
            sums_to_keep = []
            for sum_name in USERS[disc_name]:
                if sum_name not in args:
                    new_users[disc_name] = new_users.get(disc_name, []) + [sum_name]

        USERS = new_users
        if os.path.exists("./users.txt"):
            os.remove('users.txt')
        if len(USERS) == 0:
            queries.write_file('users.txt', '')
        for u in USERS:
            for s in USERS[u]:
                queries.write_file('users.txt', u + ' ' + s + '\n')
        await send_message(ctx.message.channel, f'Successfully removed: {", ".join(args)}')

'''
Handle timed checks on live games for registered summoners
'''
async def check_live_game():
    await CLIENT.wait_until_ready()
    while not CLIENT.is_closed:
        # channel = discord.utils.find(lambda c: c.name == 'general', CLIENT.get_all_channels())
        channel = CLIENT.get_channel('583756138282090502')
        # for member in channel.voice_members:
        #     print(dir(member))
        await asyncio.sleep(90)
        
        

# -------------------------------------------------
# Bot plumbing
# -------------------------------------------------

@CLIENT.event
async def on_ready():
    global USERS
    saved_users = []
    if os.path.exists("./users.txt"):
        lines = queries.read_file('users.txt').split('\n')
        for line in lines:
            if line != '' and (not line.isspace()):
                names = line.split(' ')
                USERS[names[0]] = USERS.get(names[0], []) + [names[1]]

CLIENT.loop.create_task(check_live_game())
CLIENT.run(TOKEN)