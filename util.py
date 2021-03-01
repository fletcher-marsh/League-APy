from summoner import Summoner

from pprint import pprint


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
    return result


'''
Get the average KDA for a set of participants
'''
def combined_kda(player_participants, match):
    kills, deaths, assists = 0, 0, 0
    for player, participant in player_participants:
        stats = match_stats_for_sum(Summoner(sum_id=participant['player']['summonerId']), match)
        kills += stats['kills']
        deaths += stats['deaths']
        assists += stats['assists']
    return (kills + assists) / deaths


'''
Get participant by ID
'''
def participant_by_id(p_id, match):
    participants = match['participantIdentities']
    for p in participants:
        if p['participantId'] == p_id:
            return p
    return None

