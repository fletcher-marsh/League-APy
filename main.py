import stats
from summoner import Summoner

from pprint import pprint


def main():
    champ_stats = stats.get_summoner_champion_stats(Summoner(name="who what"), 100)
    highest_kda_champ, highest_kda, kda_games = '', 0, 0
    highest_dmg_champ, highest_dmg, dmg_games = '', 0, 0
    highest_cs_champ, highest_cs, cs_games = '', 0, 0
    highest_games_champ, highest_games = '', 0
    for (champ, agg_stats) in champ_stats.items():
        if agg_stats['kda'] > highest_kda:
            highest_kda_champ, highest_kda, kda_games = champ, agg_stats['kda'], agg_stats['match_count']
        if agg_stats['dmg'] > highest_dmg:
            highest_dmg_champ, highest_dmg, dmg_games = champ, agg_stats['dmg'], agg_stats['match_count']
        if agg_stats['cs'] > highest_cs:
            highest_cs_champ, highest_cs, cs_games = champ, agg_stats['cs'], agg_stats['match_count']
        if agg_stats['match_count'] > highest_games:
            highest_games_champ, highest_games = champ, agg_stats['match_count']
    print('Highest KDA (%d games): %s, %s' % (kda_games, highest_kda_champ, highest_kda))
    print('Highest DMG (%d games): %s, %s' % (dmg_games, highest_dmg_champ, highest_dmg))
    print('Highest CS (%d games): %s, %s' % (cs_games, highest_cs_champ, highest_cs))
    print('Most games: %s, %d' % (highest_games_champ, highest_games))


if __name__ == "__main__":
    main()
