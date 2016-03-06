
class Tournament(object):
    def __init__(self, serverid, starter):
        self.serverid = serverid

        self.checkin = []
        self.waitinglist = []

        self.starter = starter

        self.isOn = False

    def start(self):
        self.isOn = True
        return self.isOn

    def addCheckIn(self, member):
        if self.isOn:
            self.checkin.append(member)
            return True
        else:
            return False

    def addWaitingList(self, member):
        if self.isOn:
            self.waitinglist.append(member)
            return True
        else:
            return False
