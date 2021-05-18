import queries
import util
from summoner import Summoner

from pprint import pprint


'''
Get list of all matches on of a summoner on a specific champ. Wrapper around get_matches
'''
def get_matches_by_champ(summoner, champ_id):
    return queries.get_all_matches(summoner, champion=champ_id)


'''
Print out aggregate stats for summoner on a particular champion
'''
def get_champ_stats(summoner, champ_name):
    c_id = util.get_champ_id(champ_name)
    matches = get_matches_by_champ(summoner, c_id)

    total_kills = 0
    total_deaths = 0
    total_assists = 0
    for m in matches:
        match = queries.get_match(m['gameId'])
        participant = util.participant_by_summoner_in_match(summoner, match)
        k, d, a = util.kda_score([participant])
        total_kills += k
        total_deaths += d
        total_assists += a
    print('Kills: %d' % total_kills)
    print('Deaths: %d' % total_deaths)
    print('Assists: %d' % total_assists)
    print('KDA: %0.2f' % ((total_kills + total_assists)/total_deaths))
    print()


'''
Print out aggregate stats for summoner on every champion
'''
def get_all_champ_stats(summoner):
    all_matches = queries.get_all_matches(summoner)
    champs_to_kda = {}
    for match_meta in all_matches:
        m = queries.get_match(match_meta['gameId'])
        participant = util.participant_by_summoner_in_match(summoner, m)
        champ_name = util.get_champ_name(participant['championId'])
        k, d, a = util.kda_score([participant])
        if champ_name in champs_to_kda:
            champs_to_kda[champ_name][0] += k
            champs_to_kda[champ_name][1] += d
            champs_to_kda[champ_name][2] += a
        else:
            champs_to_kda[champ_name] = [k, d, a]

    return champs_to_kda


'''
Get position stats about challengers on the ladder
'''
# @request_wrapper
def get_top_positions():
    result = {}
    all_roles = {
        'top': 0,
        'jg': 0,
        'mid': 0,
        'bot': 0,
        'sup': 0
    }
    challengers = queries.get_challengers()
    for c in challengers['entries']:
        # Take last 20 matches, skipping over naming issues
        summoner = Summoner(sum_id=c['summonerId'])
        matches = queries.get_matches(summoner, endIndex=20)['matches']
        roles = {
            'top': 0,
            'jg': 0,
            'mid': 0,
            'bot': 0,
            'sup': 0
        }

        for m in matches:
            if m['lane'] == 'TOP':
                roles['top'] += 1
            elif m['lane'] == 'JUNGLE':
                roles['jg'] += 1
            elif m['lane'] == 'MID':
                roles['mid'] += 1
            elif m['role'] == 'DUO_CARRY' or (m['lane'] == 'BOTTOM' and m['lane'] == 'SOLO'):
                roles['bot'] += 1
            elif m['role'] == 'DUO_SUPPORT':
                roles['sup'] += 1

        best_role = None
        best_count = 0
        for r in roles.keys():
            if roles[r] > best_count:
                best_count = roles[r]
                best_role = r

        all_roles[best_role] += 1

    return all_roles


def get_recent_wr(summoner):
    last_20 = queries.get_matches(summoner, endIndex=20)
    if len(last_20) == 0:
        return None
    wins = 0
    for m in last_20:
        match = queries.get_match(m['gameId'])
        for p in match['participantIdentities']:
            if p['player']['summonerId'] == summoner.sum_id:
                p_id = p['participantId']
                break
        for p in match['participants']:
            if p['participantId'] == p_id:
                if p['stats']['win']:
                    wins += 1
    return wins / len(last_20)


'''
Get stats about all players in a given players game
'''
def get_current_game_stats(summoner):
    cur_game = queries.get_current_game(summoner)
    if 'participants' in cur_game.keys():
        player_info = {}
        for p in cur_game['participants']:
            player_info[p['summonerName']] = {
                'sum_id': p['summonerId'],
                'team': p['teamId'],
                'champ': queries.get_champ_name(p['championId']),
                'winrate': get_recent_wr(p['summonerId'], queries.get_acc_id(p['summonerName']))
            }
        return player_info
    else:
        return None


'''
Check up on those pesky bot lanes.

Criteria:
 - Higher KDA
 - Higher CS
 - Higher Vision Score
'''
def get_botlane_stats(summoner):
    # out of the last 20 games, show how many bots won/lost
    last_20_matches = queries.get_matches(summoner, endIndex=20)['matches']

    summoners_bot_won = 0
    summoners_bot_lost = 0
    invalid_bots = []

    # winning criteria: better kda than opposing bot
    for m in last_20_matches:
        match = queries.get_match(m['gameId'])
        summoner_is_blue_side = False
        blue_bot = []
        red_bot = []
        for participant in match["participants"]:
            participant_id = util.participant_identity_by_id(participant['participantId'], match)
            if participant_id['player']['summonerId'] == summoner.sum_id:
                summoner_is_blue_side = util.is_summoner_on_blue_side_in_match(summoner, match)

            if util.is_participant_bot(participant):
                if util.is_participant_on_blue(participant):
                    blue_bot.append(participant)
                else:
                    red_bot.append(participant)

        if len(blue_bot) == len(red_bot) == 2:
            blue_score = 0
            red_score = 0

            blue_kda = util.kda_ratio(blue_bot)
            red_kda = util.kda_ratio(red_bot)
            blue_score += blue_kda / red_kda
            red_score += red_kda / blue_kda

            blue_cs = util.cs_score(blue_bot)
            red_cs = util.cs_score(red_bot)
            blue_score += blue_cs / red_cs
            red_score += red_cs / blue_cs

            blue_vision = util.vision_score(blue_bot)
            red_vision = util.vision_score(red_bot)
            blue_score += blue_vision / red_vision
            red_score += red_vision / blue_vision

            if blue_score > red_score:
                if summoner_is_blue_side:
                    summoners_bot_won += 1
                else:
                    summoners_bot_lost += 1
            else:
                if summoner_is_blue_side:
                    summoners_bot_lost += 1
                else:
                    summoners_bot_won += 1
        else:
            invalid_bots.append(m['gameId'])

    return (summoners_bot_won, summoners_bot_lost)

'''
Get duo win-rate
'''
def get_duo_wr(summoner1, summoner2, limit=None):
    s1_matches = queries.get_all_matches(summoner1, limit=limit)
    won = 0
    lost = 0
    for match_meta in s1_matches:
        match = queries.get_match(match_meta["gameId"])
        summoner_ids = util.summoner_ids_in_match(match)
        if summoner2.sum_id in summoner_ids:
            if(util.summoner_won_match(summoner1, match)):
                won += 1
            else:
                lost += 1

    return won / (won + lost)
