from summoner import Summoner

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
Returns True if player is in the bottom lane
'''
def is_bot(player):
    return (player['timeline']['lane'] == 'BOTTOM')


'''
Returns True if player is on blue side
'''
def is_blue_side(player):
    return player['teamId'] == 100


'''
Returns True if player is on red side
'''
def is_red_side(player):
    return player['teamId'] == 200



'''
Get participant ID for summoner in a match
'''
def participant_id_for_summoner_in_match(summoner, match):
    participants = match['participantIdentities']

    for p in participants:
        if p['player']['summonerId'] == summoner.sum_id:
            return p['participantId']
    return None


'''
Get single game data (Kills, Deaths, Assists) for summoner
'''
def match_stats_for_sum(summoner, match):
    p_id = participant_id_for_summoner_in_match(summoner, match)

    result = {}
    players = match['participants']
    for p in players:
        if p['participantId'] == p_id:
            stats = p['stats']
            result['kills'] = stats['kills']
            result['deaths'] = stats['deaths']
            result['assists'] = stats['assists']
            result['vision'] = stats['visionScore']
            result['cs'] = stats['totalMinionsKilled']
    return result


'''
Get the average KDA for a set of participants
'''
def kda_score(player_participants, match):
    kills, deaths, assists = 0, 0, 0
    for player, participant in player_participants:
        stats = match_stats_for_sum(Summoner(sum_id=participant['player']['summonerId']), match)
        kills += stats['kills']
        deaths += stats['deaths']
        assists += stats['assists']
    return (kills + assists) / deaths


'''
Get total CS for a set of participants
'''
def cs_score(player_participants, match):
    cs_score = 0
    for player, participant in player_participants:
        stats = match_stats_for_sum(Summoner(sum_id=participant['player']['summonerId']), match)
        cs_score += stats['cs']
    return cs_score


'''
Get total vision score for a set of participants
'''
def vision_score(player_participants, match):
    vision_score = 0
    for player, participant in player_participants:
        stats = match_stats_for_sum(Summoner(sum_id=participant['player']['summonerId']), match)
        vision_score += stats['vision']
    return vision_score


'''
Get participant by ID
'''
def participant_by_id(p_id, match):
    participants = match['participantIdentities']
    for p in participants:
        if p['participantId'] == p_id:
            return p
    return None

