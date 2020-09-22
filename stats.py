import champion_groups
import queries
import time

from summoner import Summoner
from pprint import pprint

'''
Get list of all matches on of a summoner on a specific champ. Wrapper around get_matches
'''
def get_matches_by_champ(sum_id, champ_id):
    matches = []
    start = 0
    end = 100
    while True:
        m = queries.get_matches(sum_id, champion=champ_id, beginIndex=start, endIndex=end)
        if len(m) == 0:
            return matches
        else:
            matches.extend(m)
            start += 100
            end += 100

'''
Get participant ID for summoner in a match
'''
def get_participant_id_for_summoner_in_match(summoner, match):
    participants = match['participantIdentities']
    for p in participants:
        if p['player']['accountId'] == summoner.sum_id:
            return p['participantId']
    return None

'''
Get participant by ID
'''
def get_participant_by_id(p_id, match):
    participants = match['participantIdentities']
    for p in participants:
        if p['participantId'] == p_id:
            return p
    return None

'''
Get single game data (Kills, Deaths, Assists) for summoner
'''
def get_match_stats_for_sum(summoner, match):
    p_id = get_participant_id_for_summoner_in_match(summoner, match)

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
    c_id = queries.get_champ_id(champ_name)
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
        # Take last 20 matches
        summoner = Summoner(name=c['summonerName'])
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
        time.sleep(2)

    return all_roles


def get_recent_wr(summoner):
    last_20 = queries.get_matches(summoner, endIndex=20)
    if len(last_20) == 0:
        return None
    wins = 0
    for m in last_20:
        match = queries.get_match(m['gameId'])
        for p in match['participantIdentities']:
            if p['player']['summonerId'] == sum_id:
                p_id = p['participantId']
                break
        for p in match['participants']:
            if p['participantId'] == p_id:
                if p['stats']['win']:
                    wins += 1
        time.sleep(1)
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
            time.sleep(2)
        return player_info
    else:
        return None


def get_combined_kda(player_participants, match):
    kills, deaths, assists = 0, 0, 0
    for player, participant in player_participants:
        stats = get_match_stats_for_sum(Summoner(sum_id=participant['summonerId']), match)
        kills += stats['kills']
        deaths += stats['deaths']
        assists += stats['assists']
    return (kills + assists) / deaths

'''
Check up on those pesky bot lanes.

Criteria:                                        Weight:
 - Higher KDA                                       .4
 - Higher CS                                        .4
 - Higher Vision Score                              .2
'''
def get_botlane_stats(summoner):
    # out of the last 20 games, show how many bots won/lost
    last_20_matches = queries.get_matches(summoner, endIndex=20)

    # winning criteria: better kda than opposing bot
    for m in last_20_matches:
        match = queries.get_match(m['gameId'])
        blue_bot = []
        red_bot = []
        for player in match["participants"]:
            champ = queries.get_champ_name(player['championId'])
            if champ in champion_groups.BOT or champ in champion_groups.SUPPORT:
                if player['teamId'] == 100:
                    blue_bot.append((player, get_participant_by_id(player['participantId'], match)))
                else:
                    red_bot.append((player, get_participant_by_id(player['participantId'], match)))
        print(len(red_bot), len(blue_bot))
        exit(1)
        if len(blue_bot) == len(red_bot) == 2:
            blue_kda = get_combined_kda(blue_bot)
            red_kda = get_combined_kda(red_bot)
        else:
            print("Invalid bot lane encountered:")
            pprint(red_bot)
            print("=================================")
            pprint(blue_bot)
            continue
        
        print(blue_kda, red_kda)
        exit(1)

get_botlane_stats(Summoner(name="CertifiedNanners"))