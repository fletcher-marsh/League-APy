from pprint import pprint
import json

    
'''Get contents of file path as string'''
def read_file(path):
    with open(path, encoding="utf-8") as f:
        return f.read().strip()


'''Write contents of file path with text'''
def write_file(path, text):
    with open(path, "a") as f:
        f.write(text)


CHAMPS = json.loads(read_file('champions.json'))['data'] # Locally stored champs

'''
Error out when summoner isn't in a given match
'''
def summoner_not_in_match(summoner, match):
    print(f"Summoner {summoner.name} does not exist in the match {match['gameId']}")
    exit(1)


'''
Get unique Champion ID attached to a champion. Included in this project is a json
file containing all of the meta data for champions, so this does a linear search
through that for the champion (could be improved with binary search, I guess...)
'''
def get_champ_id(champ_name):
    for champ in CHAMPS.keys():
        if CHAMPS[champ]['id'].lower() == champ_name.lower():
            return CHAMPS[champ]['key']


'''
Inversely, get champ name from ID
'''
def get_champ_name(champ_id):
    if isinstance(champ_id, int):
        champ_id = str(champ_id)
    for champ in CHAMPS.keys():
        if CHAMPS[champ]['key'] == champ_id:
            return CHAMPS[champ]['id']


'''
Returns True if participant is in the bottom lane
'''
def is_participant_bot(participant):
    return (participant['timeline']['lane'] == 'BOTTOM')


'''
Returns True if player is in the bottom lane
'''
def is_participant_on_blue(participant):
    return participant['teamId'] == 100


'''
Get participant ID for summoner in a match
'''
def participant_id_for_summoner_in_match(summoner, match):
    participants = match['participantIdentities']

    for p in participants:
        if p['player']['summonerId'] == summoner.sum_id:
            return p['participantId']
    
    summoner_not_in_match(summoner, match)


'''
Returns True if player is on blue side
'''
def is_summoner_on_blue_side_in_match(summoner, match):
    p_id = participant_id_for_summoner_in_match(summoner, match)

    for p in match['participants']:
        if p['participantId'] == p_id:
            return p['teamId'] == 100
    
    summoner_not_in_match(summoner, match)


'''
Returns True if summoner won
'''
def summoner_won_match(summoner, match):
    p_id = participant_id_for_summoner_in_match(summoner, match)
    for p in match['participants']:
        if p['participantId'] == p_id:
            return p['stats']['win']

    summoner_not_in_match(summoner, match)


'''
Get the average KDA for a set of participants
'''
def kda_score(participants):
    kills, deaths, assists = 0, 0, 0
    for participant in participants:
        stats = participant['stats']
        kills += stats['kills']
        deaths += stats['deaths']
        assists += stats['assists']
    return (kills + assists) / deaths


'''
Get total CS for a set of participants
'''
def cs_score(participants):
    cs_score = 0
    for participant in participants:
        stats = participant['stats']
        cs_score += stats['totalMinionsKilled']
    return cs_score


'''
Get total vision score for a set of participants
'''
def vision_score(participants):
    vision_score = 0
    for participant in participants:
        stats = participant['stats']
        vision_score += stats['visionScore']
    return vision_score


'''
Get all summoner names in a game
'''
def summoner_names_in_match(match):
    names = []
    for participant in match["participantIdentities"]:
        names.append(participant["player"]["summonerName"])
    return names


'''
Get all summoner_ids in a game
'''
def summoner_ids_in_match(match):
    names = []
    count = 0
    for participant in match["participantIdentities"]:
        if participant['player']['accountId'] == '0':
            # Corrupted participant :(
            continue
        names.append(participant["player"]["summonerId"])
    return names


'''
Get participant by ID
'''
def participant_identity_by_id(p_id, match):
    p_ids = match['participantIdentities']
    for p in p_ids:
        if p['participantId'] == p_id:
            return p
    return None
