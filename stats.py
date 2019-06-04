import requests
import json
from datetime import datetime
import time
# from pprint import pprint # Not used, but SUPER useful for readability of API results

# -------------------------------------------------
# Helpers
# -------------------------------------------------

'''Get contents of file path as string'''
def read_file(path):
    with open(path) as f:
        return f.read()

'''Write contents of file path with text'''
def write_file(path, text):
    with open(path, "wt") as f:
        f.write(text)

'''Convert time in ms (Unix epoch) to readable format (UTC Y-m-d H:M:S)'''
def to_date(time_in_ms):
    datetime.utcfromtimestamp(tiem_in_ms).strftime('%Y-%m-%d %H:%M:%S')


# -------------------------------------------------
# Global Constants
# -------------------------------------------------

API_KEY = read_file("key.txt") # Get from https://developer.riotgames.com/
API_URL = "https://na1.api.riotgames.com/lol/" # Base API URL, used to build off of
CHAMPS = json.loads(read_file('champions.json')) # Gotten from https://github.com/ngryman/lol-champions/blob/master/champions.json
sum_id = 'woke bloke' # This is my summoner name! Replace with your own :]


# -------------------------------------------------
# Queries
# -------------------------------------------------
'''
Get unique Summoner ID attached to your account, used for most other endpoints
If you want to make lot's of queries, I recommend caching your id's so as to 
reduce your footprint.
'''
def get_sum_id(sum_name):
    route = "summoner/v4/summoners/by-name/%s" % sum_name
    response = requests.get(API_URL + route, params={
        'api_key': API_KEY
    }).json()
    return response['accountId']

'''
Get unique Champion ID attached to a champion. Included in this project is a json
file containing all of the meta data for champions, so this does a linear search
through that for the champion (could be improved with binary search, I guess...)
'''
def get_champ_id(champ_name):
    for champ in CHAMPS:
        if champ['id'] == champ_name.lower():
            return champ['key']

'''
Get a list of up to 100 matches according to parameters:
    sum_id      Summoner ID (use get_sum_id)

    champion    List of Integer IDs of champion (use get_champ_id)

    queue       List of Integer IDs of types of game 
                (see https://developer.riotgames.com/game-constants.html)

    season      List of Integer IDs of seasons 
                (see https://developer.riotgames.com/game-constants.html)

    beginTime   Integer (Unix epoch) milliseconds to start search from
                DEFAULT (and endTime exists): start of account's match history
                NOTE: beginTime and endTime are required to be within 1 week of each other 
                        (604800000 ms)
                NOTE: endTime must be after beginTime
                NOTE: if you specify endTime but not beginTime, it's likely you will 400

    endTime     Integer (Unix epoch) milliseconds to end search at
                DEFAULT (and startTime exists): current Unix timestamp in ms
                DEFAULT (and startTime doesn't exist): defers to showing most 
                                                     recent 100 games
                NOTE: if not provided and startTime is provided, it will ignore maximum 
                    time range of 1 week limitation

    beginIndex  Integer representing distance from most recent game to start search from
                DEFAULT: 0

    endIndex    Integer representing distance from most recent game to end search at
                DEFAULT: beginIndex + 100
                NOTE: endIndex must be after beginIndex
'''
def get_matches(sum_id, champion=None, queue=None, season=None, beginTime=None, endTime=None, beginIndex=0, endIndex=100):
    sum_id = get_sum_id(sum_name)
    route = 'match/v4/matchlists/by-account/%s' % sum_id
    response = requests.get(API_URL + route, params={
        'api_key': API_KEY,
        'encryptedAccountId': sum_id,
        'champion': champion,
        'queue': queue,
        'season': season,
        'beginTime': beginTime,
        'endTime': endTime,
        'beginIndex': beginIndex,
        'endIndex': endIndex
    }).json()
    return response['matches']

'''
Get list of all matches on of a summoner on a specific champ. Wrapper around get_matches
'''
def get_matches_by_champ(sum_id, champ_id):
    matches = []
    start = 0
    end = 100
    while True:
        m = get_matches(sum_id, champion=champ_id, beginIndex=start, endIndex=end)
        if len(m) == 0:
            return matches
        else:
            matches.extend(m)
            start += 100
            end += 100


'''
From an Integer match ID, get specific details of match
'''
def get_match(match_id):
    route = 'match/v4/matches/%d' % match_id
    response = requests.get(API_URL + route, params={
        'api_key': API_KEY,
        'matchId': match_id
    }).json()
    return response


'''
Get single game data (Kills, Deaths, Assists) for summoner
'''
def get_match_stats_for_sum(sum_id, match_id):
    match = get_match(match_id)
    participants = match['participantIdentities']
    for p in participants:
        if p['player']['accountId'] == sum_id:
            p_id = p['participantId']

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
Print out aggregate stats for summoner on a particular champion
NOTE: Due to rate limiting, this is suuuuper slow
'''
def get_champ_stats(sum_id, champ_name):
    c_id = get_champ_id(champ_name)
    matches = get_matches_by_champ(sum_id, c_id)
    print('Games played: %d' % len(matches))
    total_kills = 0
    total_deaths = 0
    total_assists = 0
    for m in matches:
        stats = get_match_stats_for_sum(m['gameId'], sum_id)
        time.sleep(1)
        total_kills += stats['kills']
        total_deaths += stats['deaths']
        total_assists += stats['assists']
    print('Kills: %d' % total_kills) 
    print('Deaths: %d' % total_deaths) 
    print('Assists: %d' % total_assists) 
    print('KDA: %0.2f' % ((total_kills + total_assists)/total_deaths))
    print()

'''
Print out aggregate stats for summoner on every champion
NOTE: Again, suuuper slow due to rate limiting
'''
def get_all_champs_stats(sum_id):
    for champ in CHAMPS:
        print('\033[1m' + champ['id'] + '\033[1m')
        print('------------------')
        matches = get_matches_by_champ(sum_id, champ['key'])
        print('Games played: %d' % len(matches))
        total_kills = 0
        total_deaths = 0
        total_assists = 0
        for m in matches:
            stats = get_match_stats_for_sum(sum_id, m['gameId'])
            time.sleep(1)
            total_kills += stats['kills']
            total_deaths += stats['deaths']
            total_assists += stats['assists']
        print('Kills: %d' % total_kills) 
        print('Deaths: %d' % total_deaths) 
        print('Assists: %d' % total_assists) 
        print('KDA: %0.2f' % ((total_kills + total_assists)/total_deaths))
        print()
        time.sleep(3)
