import stats
import queries
from summoner import Summoner

from pprint import pprint


def main():
    stats.get_all_champ_stats(Summoner(name="who what"))

if __name__ == "__main__":
    main()
