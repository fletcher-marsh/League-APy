import time
import queries

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
Get single game data (Kills, Deaths, Assists) for summoner
'''
def get_match_stats_for_sum(sum_id, match_id):
    match = queries.get_match(match_id)
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
        sum_id = queries.get_sum_id(c['summonerName'])
        # Take last 20 matches
        matches = queries.get_matches(sum_id, endIndex=20)
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
        time.sleep(1.3)

    return all_roles

print(get_top_positions())
