
class Bet(object):
    def __init__(self, user, amount, team):
        self.user = user
        self.amount = amount

        self.winnings = None

        if team == "red":
            self.isRed = True
            self. isBlue = False
        if team == "blue":
            self.isRed = False
            self.isBlue = True