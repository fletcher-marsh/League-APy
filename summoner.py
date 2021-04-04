import queries

class Summoner():
    def __init__(self, name=None, acc_id=None, sum_id=None, offline=False):
        if offline:
            self.name = name
            self.acc_id = acc_id
            self.sum_id = sum_id
            return
            
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

    def __repr__(self):
        res = "=============\n"
        res += f"Name: {self.name}\nAccountID: {self.acc_id}\nSummonerID: {self.sum_id}\n"
        res += "============="
        return res
