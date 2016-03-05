from BettingSystem import PointsManager, Bet


class Match(object):
    def __init__(self, serverid):
        self.serverid = int(serverid)
        self.redVotes = []
        self.blueVotes = []

        self.blueRatio = 2
        self.redRatio = 2

        self.round = 1

        self.bettingOpen = True

        self.points = PointsManager.PointsManager()

        print("Match has been initiated.")

    def openBetting(self):
        self.bettingOpen = True

    def closeBetting(self):
        self.bettingOpen = False

    def totalVotes(self):
        return len(self.blueVotes) + len(self.redVotes)

    def redPercent(self):
        return (len(self.redVotes) / self.totalVotes()) * 100

    def bluePercent(self):
        return (len(self.blueVotes) / self.totalVotes()) * 100

    def addVote(self, user, team, bet):
        if self.bettingOpen:
            if team == "red":
                if self.points.minusPoints(int(bet), self.serverid, user.id):
                    self.redVotes.append(Bet.Bet(user, bet, team))
                    print(user.id, "bet on", team, "with", bet, "points.")
                    return True
                else:
                    print("Failed to place bet.")
                    return False
            elif team == "blue":
                if self.points.minusPoints(int(bet), self.serverid, user.id):
                    self.blueVotes.append(Bet.Bet(user, bet, team))
                    print(user.id, "bet on", team, "with", bet, "points.")
                    return True
                else:
                    print("Failed to place bet.")
                    return False
        else:
            return False

    def cashout(self, winner):
        if winner == "red":
            for bet in self.redVotes:
                win = int(bet.amount * self.blueRatio)
                self.points.givepoints(win, bet.user.server.id, bet.user.id)
                bet.winnings = win
                print("Cash Out:", bet.user.id, bet.amount, "points.")
            return self.redVotes
        elif winner == "blue":
            for bet in self.blueVotes:
                win = int(bet.amount * self.blueRatio)
                self.points.givepoints(win, bet.user.server.id, bet.user.id)
                bet.winnings = win
                print("Cash Out:", bet.user.id, bet.amount, "points.")
            return self.blueVotes

    def betted(self, userid):
        for bet in self.redVotes:
            if bet.user.id == userid:
                return True
            else:
                continue
        for bet in self.blueVotes:
            if bet.user.id == userid:
                return True
            else:
                continue
        return False
