import requests
import time
import diskcache as dc
import os
import copy
import util
from pprint import pprint # Not used, but SUPER useful for readability of API results


# -------------------------------------------------
# Util - Constants/wrappers/helper functions/etc.
# -------------------------------------------------

API_KEY = None # Get from https://developer.riotgames.com/
API_URL = "https://na1.api.riotgames.com/lol/" # Base API URL, used to build off of for specific endpoints
# Keep track of request counts (rate limiting)
REQUESTS = 0
REQUEST_START = None
CACHE = dc.Cache(os.path.dirname(os.path.realpath(__file__)))


def get_api_key():
    global API_KEY
    if API_KEY is None:
        API_KEY = util.read_file("key.txt")
        return API_KEY
    return API_KEY


def clear_cache():
    CACHE.clear()
    exit(1)


'''
Wrapper function to keep track of requests. Current rate limits are:
20 reqs per 1 second
100 reqs per 2 minutes
'''
def request_wrapper(f):
    request_per_two_min = 100
    two_min = 120
    req_per_sec = 20
    one_sec = 1

    def wait_for_limit(debug):
        '''
        Dynamically determine sleep times according to API limits
        '''
        global REQUEST_START
        now = time.time()
        since = now - REQUEST_START
        if REQUESTS != 0 and REQUESTS % request_per_two_min == 0 and (since <= two_min):
            to_sleep = (two_min - since) + 1
            if debug:
                print(f"Hit rate limit on request #{REQUESTS}, sleeping for %d seconds..." % to_sleep)
            time.sleep(to_sleep)
            REQUEST_START = time.time()
        elif REQUESTS != 0 and REQUESTS % req_per_sec == 0 and (since <= one_sec):
            time.sleep(one_sec)

    def warn_retry_exit(res, f, debug, *args, **kwargs):
        '''
        Give readable info on request failure
        '''
        error = util.error_in_response(res)
        if error is not None:
            code, message = error['code'], error['msg']
            if code == 504 or code == 503:
                print(f'Hit server-side error for request #{REQUESTS}, retrying...')
                time.sleep(one_sec)
                return f(debug = debug, *args, **kwargs)
            elif code == 401:
                msg = f'Unauthorized, make sure you have an updated API key:\n'
                msg += 'https://developer.riotgames.com/'
            elif code == 429:
                wait_for_limit(debug = True)
                return f(debug = debug, *args, **kwargs)
            else:
                msg = '\033[1;31;31mREQUEST FAILED\033[0m'
                msg += f'Code: {code}'
                msg += f'Message: {message}'

            if debug:
                print(msg)
                exit(1)
        return res

    def create_cache_key(route, params):
        id_dict = copy.copy(params)
        id_dict['route'] = route
        del id_dict['api_key']
        return tuple(sorted(id_dict.items()))

    def req_with_limit(*args, **kwargs):
        if "debug" in kwargs:
            debug = kwargs["debug"]
            del kwargs["debug"]
        else:
            debug = False

        global REQUESTS, REQUEST_START
        if REQUEST_START is None:
            REQUEST_START = time.time()
        else:
            wait_for_limit(debug)

        route, params = f(*args, **kwargs)
        cache_lookup = create_cache_key(route, params)
        if cache_lookup in CACHE:
            res = CACHE[cache_lookup]
        else:
            res = requests.get(API_URL + route, params=params).json()
            if 'status' not in res and 'match/v4/matchlists/' not in route:
                CACHE[cache_lookup] = res

            REQUESTS += 1
            if REQUESTS % 10 == 0 and debug:
                print(f'Requests made: {REQUESTS}')

        return warn_retry_exit(res, req_with_limit, debug, *args, **kwargs)

    return req_with_limit

# -------------------------------------------------
# Queries
# -------------------------------------------------

'''
From an Integer match ID, get specific details of match
'''
@request_wrapper
def get_match(match_id):
    route = 'match/v4/matches/%d' % match_id
    params = {
        'api_key': get_api_key(),
        'matchId': match_id
    }
    return route, params

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
    if endIndex - beginIndex > 100:
        print("Cannot fetch more than 100 matches")
        print("Begin:", beginIndex)
        print("End:", endIndex)
        exit(1)

    route = 'match/v4/matchlists/by-account/%s' % summoner.acc_id
    params = {
        'api_key': get_api_key(),
        'encryptedAccountId': summoner.acc_id,
        'champion': champion,
        'queue': queue,
        'season': season,
        'beginTime': beginTime,
        'endTime': endTime,
        'beginIndex': beginIndex,
        'endIndex': endIndex
    }
    return route, params

def get_all_matches(summoner, limit=None, **kwargs):
    matches = []
    start = 0
    end = 100 if limit is None or limit >= 100 else limit
    while ((limit is not None and start < limit) or limit == None):
        match_response = get_matches(summoner, beginIndex=start, endIndex=end, **kwargs)
        error = util.error_in_response(match_response)
        if error is not None and error['code'] == 404:
            return []

        m = match_response["matches"]
        if len(m) < 100:
            return matches + m
        else:
            matches.extend(m)
            start += 100
            end += 100 if (limit is None or limit - end >= 100) else limit - end
    return matches

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
def get_sum_id(name):
    summ = get_summoner_by_name(name)
    return summ['id']

@request_wrapper
def get_summoner_by_acc_id(acc_id):
    route = "summoner/v4/summoners/by-account/%s" % acc_id
    params = {
        'api_key': get_api_key()
    }
    return route, params

@request_wrapper
def get_summoner_by_sum_id(sum_id):
    route = "summoner/v4/summoners/%s" % sum_id
    params = {
        'api_key': get_api_key()
    }
    return route, params

@request_wrapper
def get_summoner_by_name(name):
    route = "summoner/v4/summoners/by-name/%s" % name
    params = {
        'api_key': get_api_key()
    }
    return route, params

'''
Get summoner data for current challenger players
'''
@request_wrapper
def get_challengers():
    route = 'league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5'
    params = {
        'api_key': get_api_key()
    }
    return route, params

'''
Get current game data for a specific integer Summoner ID
'''
@request_wrapper
def get_current_game(summoner):
    route = f'spectator/v4/active-games/by-summoner/{summoner.sum_id}'
    params = {
        'api_key': get_api_key()
    }
    return route, params
