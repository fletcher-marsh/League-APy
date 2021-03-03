import stats
import queries
from summoner import Summoner

from pprint import pprint


def main():
    print(stats.get_recent_wr(Summoner(name="who what")))


if __name__ == "__main__":
    main()
