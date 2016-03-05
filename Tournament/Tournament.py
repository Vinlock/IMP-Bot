
class Tournament(object):
    def __init__(self, serverid):
        self.serverid = serverid

        self.checkin = dict()
        self.waitinglist = dict()

        self.isOn = False

    def start(self):
        self.isOn = True
        return self.isOn

    def addCheckIn(self):
        

