import stats
import queries
from summoner import Summoner

from pprint import pprint


def main():
    match = queries.get_matches(Summoner(name='who what'), endIndex=1)['matches'][0]
    print(queries.get_match(match['gameId'])['participants'][2])
    # print(stats.get_botlane_stats(Summoner(name="who what")))

if __name__ == "__main__":
    main()
