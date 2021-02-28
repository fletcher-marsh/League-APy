import requests
import json
import time
from pprint import pprint # Not used, but SUPER useful for readability of API results


# -------------------------------------------------
# Util - Constants/wrappers/helper functions/etc.
# -------------------------------------------------

'''
Give readable info on request failure
'''
def check_response(req):
    if 'status' in req.keys():
        print('\033[1;31;31mREQUEST FAILED\033[0m')
        print(f'Code: {req["status"]["status_code"]}')
        print(f'Message: {req["status"]["message"]}')
    
'''Get contents of file path as string'''
def read_file(path):
    with open(path, encoding="utf-8") as f:
        return f.read().strip()

'''Write contents of file path with text'''
def write_file(path, text):
    with open(path, "a") as f:
        f.write(text)

'''Convert time in ms (Unix epoch) to readable format (UTC Y-m-d H:M:S)'''
def to_date(time_in_ms):
    datetime.utcfromtimestamp(tiem_in_ms).strftime('%Y-%m-%d %H:%M:%S')

API_KEY = read_file("key.txt") # Get from https://developer.riotgames.com/
API_URL = "https://na1.api.riotgames.com/lol/" # Base API URL, used to build off of for specific endpoints
CHAMPS = json.loads(read_file('champions.json')) # Locally stored champs
REQUESTS = 0 # To keep track of request counts (rate limiting)
REQUEST_START = None
REQUEST_MIN_LIMIT = 90
REQUEST_SEC_LIMIT = 18

'''
Wrapper function to keep track of requests. Current rate limits are:
20 reqs per 1 second
100 reqs per 2 minutes
'''
def request_wrapper(f):
    def req_with_count(*args, **kwargs):
        global REQUESTS, REQUEST_START
        if REQUEST_START is None:
            REQUEST_START = time.time()
        else:
            now = time.time()
            if REQUESTS != 0 and REQUESTS % REQUEST_MIN_LIMIT == 0 and (REQUEST_START - now <= 60):
                time.sleep(60.5)
                REQUEST_START = now
            elif REQUESTS != 0 and REQUESTS % REQUEST_SEC_LIMIT == 0 and (REQUEST_START - now <= 1):
                time.sleep(1)
                REQUEST_START = now
        res = f(*args, **kwargs)
        REQUESTS += 1
        if REQUESTS % 10 == 0:
            print(f'Requests made: {REQUESTS}')
        return res
    return req_with_count

# -------------------------------------------------
# Queries
# -------------------------------------------------

'''
From an Integer match ID, get specific details of match
'''
@request_wrapper
def get_match(match_id):
    route = 'match/v4/matches/%d' % match_id
    response = requests.get(API_URL + route, params={
        'api_key': API_KEY,
        'matchId': match_id
    }).json()
    check_response(response)
    return response


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
@request_wrapper
def get_matches(summoner, champion=None, queue=None, season=None, beginTime=None, endTime=None, beginIndex=0, endIndex=100):
    route = 'match/v4/matchlists/by-account/%s' % summoner.acc_id
    response = requests.get(API_URL + route, params={
        'api_key': API_KEY,
        'encryptedAccountId': summoner.acc_id,
        'champion': champion,
        'queue': queue,
        'season': season,
        'beginTime': beginTime,
        'endTime': endTime,
        'beginIndex': beginIndex,
        'endIndex': endIndex
    }).json()
    check_response(response)
    return response['matches']
    
'''
Get unique Account ID attached to your account, used for other endpoints
If you want to make lot's of queries, I recommend caching your id's so as to 
reduce your footprint.
'''
def get_acc_id(name):
    summ = get_summoner_by_name(name)
    return summ['accountId']

'''
Similarly, get Summoner ID
'''
def get_sum_id(sum_name):
    summ = get_summoner_by_name(name)
    return summ['id']

@request_wrapper
def get_summoner_by_acc_id(acc_id):
    route = "summoner/v4/summoners/by-account/%s" % acc_id
    response = requests.get(API_URL + route, params={
        'api_key': API_KEY
    }).json()
    check_response(response)
    return response

@request_wrapper
def get_summoner_by_sum(sum_id):
    route = "summoner/v4/summoners/%s" % sum_id
    response = requests.get(API_URL + route, params={
        'api_key': API_KEY
    }).json()
    check_response(response)
    return response

@request_wrapper
def get_summoner_by_name(name):
    route = "summoner/v4/summoners/by-name/%s" % name
    response = requests.get(API_URL + route, params={
        'api_key': API_KEY
    }).json()
    check_response(response)
    return response

'''
Get unique Champion ID attached to a champion. Included in this project is a json
file containing all of the meta data for champions, so this does a linear search
through that for the champion (could be improved with binary search, I guess...)
'''
def get_champ_id(champ_name):
    for champ in CHAMPS.keys():
        if CHAMPS[champ]['id'].lower() == champ_name.lower():
            return champ['key']

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
Get summoner data for current challenger players
'''
@request_wrapper
def get_challengers():
    route = 'league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5'
    response = requests.get(API_URL + route, params={
        'api_key': API_KEY
    }).json()
    check_response(response)
    return response['entries']
    
'''
Get current game data for a specific integer Summoner ID
'''
@request_wrapper
def get_current_game(summoner):
    route = f'spectator/v4/active-games/by-summoner/{summoner.sum_id}'
    response = requests.get(API_URL + route, params={
        'api_key': API_KEY
    }).json()
    check_response(response)
    return response

