from BettingSystem import PointsManager, Bet


class Match(object):
    def __init__(self, serverid):
        self.serverid = int(serverid)
        self.redVotes = []
        self.blueVotes = []

        self.blueRatio = None
        self.redRatio = None

        self.blueName = None
        self.redName = None

        self.round = 1

        self.bettingOpen = True

        self.points = PointsManager.PointsManager()

        print("Match has been initiated.")

    def openBetting(self):
        self.bettingOpen = True

    def closeBetting(self):
        self.bettingOpen = False

    def getName(self, team, mention=False):
        if team == "red":
            if self.redName == None:
                return "RED"
            else:
                if mention:
                    return self.redName.mention
                else:
                    return self.redName.name
        elif team == "blue":
            if self.blueName == None:
                return "BLUE"
            else:
                if mention:
                    return self.blueName.mention
                else:
                    return self.blueName.name

    def totalVotes(self):
        return len(self.blueVotes) + len(self.redVotes)

    def redPercent(self):
        try:
            percent = (len(self.redVotes) / self.totalVotes()) * 100
        except ZeroDivisionError:
            return 0
        else:
            return percent

    def bluePercent(self):
        try:
            percent = (len(self.blueVotes) / self.totalVotes()) * 100
        except ZeroDivisionError:
            return 0
        else:
            return percent

    def diffRatio(self):
        if self.redPercent() < self.bluePercent():
            diff = self.bluePercent() - self.redPercent()
            if diff > 50:
                add = diff / 100
                self.redRatio = 1 + add
                self.blueRatio = 1 + ((100 - diff) / 100)
            elif diff < 50:
                add = diff / 100
                self.redRatio = 1 + ((100 - diff) / 100)
                self.blueRatio = 1 + add
        elif self.redPercent() > self.bluePercent():
            diff = self.redPercent() - self.bluePercent()
            if diff > 50:
                add = diff / 100
                self.blueRatio = 1 + add
                self.redRatio = 1 + ((100 - diff) / 100)
            elif diff < 50:
                add = diff / 100
                self.blueRatio = 1 + ((100 - diff) / 100)
                self.redRatio = 1 + add
        elif self.redPercent() == self.bluePercent():
            self.blueRatio = 1.5
            self.redRatio = 1.5


    def addVote(self, user, team, bet):
        if self.bettingOpen:
            if team == "red":
                if self.points.minusPoints(int(bet), self.serverid, user.id):
                    self.redVotes.append(Bet.Bet(user, bet, team))
                    print(user.id, "bet on", team, "with", bet, "points.")
                    self.diffRatio()
                    return True
                else:
                    print("Failed to place bet.")
                    return False
            elif team == "blue":
                if self.points.minusPoints(int(bet), self.serverid, user.id):
                    self.blueVotes.append(Bet.Bet(user, bet, team))
                    print(user.id, "bet on", team, "with", bet, "points.")
                    self.diffRatio()
                    return True
                else:
                    print("Failed to place bet.")
                    return False
        else:
            return False

    def removeVote(self, user):
        bet = self.findbet(user)
        if bet is not None:
            try:
                self.redVotes.remove(bet)
            except ValueError:
                try:
                    self.blueVotes.remove(bet)
                except ValueError:
                    return False
                else:
                    return True
            else:
                return True
        return False

    def cashout(self, winner):
        if winner == "red":
            for bet in self.redVotes:
                win = int(round(bet.amount * self.redRatio))
                self.points.givepoints(win, bet.user.server.id, bet.user.id)
                bet.winnings = win
                print("Cash Out:", bet.user.id, bet.amount, "points.")
            return self.redVotes
        elif winner == "blue":
            for bet in self.blueVotes:
                win = int(round(int(bet.amount) * self.blueRatio))
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

    def findbet(self, user):
        for bet in self.redVotes:
            if bet.user.id == user.id:
                return bet
            else:
                continue
        for bet in self.blueVotes:
            if bet.user.id == user.id:
                return bet
            else:
                continue
        return None
