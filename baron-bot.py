
import discord
import queries
import stats
import os


TOKEN = queries.read_file('disc_token.txt')
CLIENT = discord.Client()
USERS = []
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
/add [summoner_1] [summoner_2] ... [summoner_n]

Functionality:
Add summoner(s) to be tracked by Baron Bot
'''
async def handle_add(message):
    global USERS
    new_users = message.content.split(" ")[1:] # skip invocation
    if len(new_users) != 0:
        new = []
        for u in new_users:
            if u not in USERS:
                new.append(u)
                USERS.append(u)
                queries.write_file('users.txt', u + '\n')
        if new:
            await send_message(message.channel, "Added: "+", ".join(new))
        else:
            await send_message(message.channel, "Already added all names")
 
'''
Command:
/check [summoner_1] [summoner_2] ... [summoner_n]

Functionality:
Checks whether summoner(s) are being tracked
'''
async def handle_check(message):
    global USERS
    check_users = message.content.split(" ")[1:]
    if len(check_users) != 0:
        added = []
        not_added = []
        for u in check_users:
            if u in USERS:
                added.append(u)
            else:
                not_added.append(u)
        msg = f'Added: {", ".join(added)}\nNot Added: {", ".join(not_added)}'
        await send_message(message.channel, msg)

async def handle_remove(message):
    global USERS
    remove_users = message.content.split(" ")[1:]
    if len(remove_users) != 0:
        to_keep = []
        for u in USERS:
            if u not in remove_users:
                to_keep.append(u)
        USERS = to_keep
        os.remove('users.txt')
        queries.write_file('users.txt', '\n'.join(USERS))
        await send_message(message.channel, f'Successfully removed: {", ".join(remove_users)}')
# -------------------------------------------------
# Bot plumbing
# -------------------------------------------------

@CLIENT.event
async def on_message(message):
    global USERS
    # we do not want the bot to reply to itself
    if message.author == CLIENT.user:
        return

    if message.content.startswith('/add'):
        await handle_add(message)
    elif message.content.startswith('/check'):
        await handle_check(message)
    elif message.content.startswith('/remove'):
        await handle_remove(message)
    else:
        await send_message(message.channel, "Unrecognized command")

@CLIENT.event
async def on_ready():
    global USERS
    saved_users = []
    if os.path.exists("./users.txt"):
        saved_users = queries.read_file('users.txt').split('\n')
    else:
        queries.write_file('users.txt', '')
        
    for u in saved_users:
        USERS.append(u)
    


CLIENT.run(TOKEN)