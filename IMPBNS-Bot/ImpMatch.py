import PointsManager

class Match(object):
    def __init__(self, serverid):
        self.serverid = int(serverid)
        self.redVotes = dict()
        self.blueVotes = dict()

        self.blueRatio = 2
        self.redRatio = 2

        self.round = 1

        self.points = PointsManager.PointsManager()

        print("Match has been initiated.")

    def totalVotes(self):
        return len(self.teamBlueVotes) + len(self.teamRedVotes)

    def redPercent(self):
        return (len(self.teamRedVotes) / self.totalVotes()) * 100

    def bluePercent(self):
        return (len(self.teamBlueVotes) / self.totalVotes()) * 100

    def addVote(self, user, team, bet):
        if team == "red":
            self.redVotes[user.id] = dict()
            self.redVotes[user.id]['bet'] = int(bet)
            self.redVotes[user.id]['object'] = user
        elif team == "blue":
            self.blueVotes[user.id] = dict()
            self.blueVotes[user.id]['bet'] = int(bet)
            self.blueVotes[user.id]['object'] = user
        self.points.minusPoints(int(bet), self.serverid, user.id)
        print(user.id, "bet on", team, "with", bet, "points.")

    def cashout(self, winner):
        if winner == "red":
            for (userid, info) in self.redVotes:
                print("Cash Out:", userid, info['bet'], "points.")
                self.points.givepoints(info['bet'] * self.redRatio, self.serverid, userid)
            return self.redVotes
        elif winner == "blue":
            for (userid, info) in self.blueVotes:
                print("Cash Out:", userid, info['bet'], "points.")
                self.points.givepoints(info['bet'] * self.blueRatio, self.serverid, userid)
            return self.blueVotes