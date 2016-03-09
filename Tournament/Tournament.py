from Tournament import CheckIn

class Tournament(object):
    def __init__(self, serverid, starter):
        self.serverid = serverid

        self.checkin = []

        self.starter = starter

        self.isOn = False

    def start(self):
        self.isOn = True
        return self.isOn

    def end(self):
        if self.isOn == True:
            self.isOn = False
            return True
        else:
            return False

    def checkIn(self, member, list):
        for check in checkin:
            if check.member == member:

    def isCheckedIn(self, member):
        for check in checkin:
            if check.member == member:
                return check.list
            else:
                continue
        return None