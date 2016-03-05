import Database, threading
from time import sleep

class Increment(object):
    def __init__(self):

        self.pointsPer = 1
        self.secondsPerIncrement = 60

        self.members = None

        print("Points Incrementation has initiated")

    def thread(self, function):
        t1 = threading.Thread(target=function)
        t1.daemon = True
        t1.start()

    def start(self):
        self.thread(self.beginIncrement)

    def beginIncrement(self):
        while True:
            sleep(self.secondsPerIncrement)
            print("Incrementing Online Member's Points by", self.pointsPer)
            self.thread(self.incrementPoints)
            # sleep(self.secondsPerIncrement)

    def incrementPoints(self):
        # Increments all online members of each server.
        allmembers = self.members
        for server, members in allmembers.items():
            if self.incrementList(server, members):
                print("Incremented Member's Points")
            else:
                print("Failed to increment.")

    def incrementList(self, serverid, listIDs):
        conn = Database.DB()
        with conn.cursor() as cursor:
            all_members = ','.join(["'"+str(member)+"'" for member in listIDs])
            if "153648068040982528" in listIDs:
                print("TEST THERE")
            else:
                print("TEST NOT THERE")
            sql = "UPDATE `points` SET `points` = `points` + 1 WHERE `server`='{0}' AND `userid` IN ({1})".format(str(serverid), all_members)
            if len(sql) > 65000:
                return False
            try:
                cursor.execute(sql)
                conn.commit()
                print(cursor._last_executed)
            except:
                return False
        conn.close()
        return True

    def updateList(self, dictionary):
        assert isinstance(dictionary, dict)
        self.members = dictionary