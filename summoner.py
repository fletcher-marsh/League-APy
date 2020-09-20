import queries

class Summoner():
    def __init__(name=None, acc_id=None, sum_id=None):
        if name is not None:
            summoner = queries.get_summoner_by_name(name)
        elif acc_id is not None:
            summoner = queries.get_summoner_by_acc_id(acc_id)
        elif sum_id is not None:
            summoner = queries.get_summoner_by_sum_id(sum_id)
        else:
            raise Exception("No information provided to create Summoner")
        
        self.name = summoner["name"]
        self.acc_id = summoner["accountId"]
        self.sum_id = summoner["id"]
