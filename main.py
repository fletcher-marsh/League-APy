import stats
from summoner import Summoner


def main():
    print(stats.get_botlane_stats(Summoner(name="who what")))

if __name__ == "__main__":
    main()
