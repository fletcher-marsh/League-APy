import stats
import queries
from summoner import Summoner

from pprint import pprint


def main():
    stats.get_champ_stats(Summoner(name="who what"), "leblanc")

if __name__ == "__main__":
    main()
