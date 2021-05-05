import stats
import queries
from summoner import Summoner

from pprint import pprint


def main():
    print(stats.get_duo_wr(
        Summoner(name="eat big chip"),
        Summoner(name="arrowtothecrotch"))
    )
    # print(queries.get_match(123))
    # print(stats.get_botlane_stats(Summoner(name="who what")))

if __name__ == "__main__":
    main()
