import champion_groups
import queries
import time
import util

from pprint import pprint


'''
Get list of all matches on of a summoner on a specific champ. Wrapper around get_matches
'''
def get_matches_by_champ(summoner, champ_id):
    matches = []
    start = 0
    end = 100
    while True:
        m = queries.get_matches(summoner, champion=champ_id, beginIndex=start, endIndex=end)
        if len(m) == 0:
            return matches
        else:
            matches.extend(m)
            start += 100
            end += 100


'''
Print out aggregate stats for summoner on a particular champion
NOTE: Due to rate limiting, this is suuuuper slow
'''
def get_champ_stats(summoner, champ_name):
    c_id = queries.get_champ_id(champ_name)
    matches = get_matches_by_champ(summoner, c_id)
    print('Games played: %d' % len(matches))
    total_kills = 0
    total_deaths = 0
    total_assists = 0
    for m in matches:
        match = queries.get_match(m['gameId'])
        stats = util.match_stats_for_sum(summoner, match)
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
def get_all_champ_stats(summoner):
    for champ in util.CHAMPS.keys():
        print('\033[1m' + champ + '\033[1m')
        print('------------------')
        matches = get_matches_by_champ(summoner, util.CHAMPS[champ]['key'])
        print('Games played: %d' % len(matches))
        total_kills = 0
        total_deaths = 0
        total_assists = 0
        for m in matches:
            match = queries.get_match(m['gameId'])
            stats = util.match_stats_for_sum(summoner, match)
            total_kills += stats['kills']
            total_deaths += stats['deaths']
            total_assists += stats['assists']
        print('Kills: %d' % total_kills) 
        print('Deaths: %d' % total_deaths) 
        print('Assists: %d' % total_assists) 
        print('KDA: %0.2f' % ((total_kills + total_assists)/total_deaths))
        print()


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
    for c in challengers:
        # Take last 20 matches, skipping over naming issues
        try:
            summoner = Summoner(name=c['summonerName'])
        except:
            continue
        matches = queries.get_matches(summoner, endIndex=20)
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
    last_20_matches = queries.get_matches(summoner, endIndex=20)

    summoners_bot_won = 0
    summoners_bot_lost = 0
    invalid_bots = []

    # winning criteria: better kda than opposing bot
    for m in last_20_matches:
        match = queries.get_match(m['gameId'])
        summoner_is_blue_side = False
        blue_bot = []
        red_bot = []
        for player in match["participants"]:
            champ = util.get_champ_name(player['championId'])
            participant = util.participant_by_id(player['participantId'], match)
            if participant['player']['summonerId'] == summoner.sum_id:
                summoner_is_blue_side = util.is_blue_side(player)

            if util.is_bot(player):
                if util.is_blue_side(player):
                    blue_bot.append((player, participant))
                else:
                    red_bot.append((player, participant))

        if len(blue_bot) == len(red_bot) == 2:
            blue_score = 0
            red_score = 0
            
            blue_kda = util.kda_score(blue_bot, match)
            red_kda = util.kda_score(red_bot, match)
            blue_score += blue_kda / red_kda
            red_score += red_kda / blue_kda

            blue_cs = util.cs_score(blue_bot, match)
            red_cs = util.cs_score(red_bot, match)
            blue_score += blue_cs / red_cs
            red_score += red_cs / blue_cs

            blue_vision = util.vision_score(blue_bot, match)
            red_vision = util.vision_score(red_bot, match)
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
