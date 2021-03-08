import stats
import queries
from summoner import Summoner

from pprint import pprint


def main():
    print(stats.get_duo_wr(
        Summoner(name="eat big chip"),
        Summoner(name="arrowtothecrotch"))
    )


if __name__ == "__main__":
    main()
