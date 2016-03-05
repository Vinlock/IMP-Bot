
class Tournament(object):
    def __init__(self, serverid):
        self.serverid = serverid

        self.checkin = []
        self.waitinglist = []

        self.isOn = False

    def start(self):
        self.isOn = True
        return self.isOn

    def addCheckIn(self, member):
        self.checkin.append(member)
        return True

    def addWaitingList(self, member):
        self.waitinglist.append(member)
        return True

