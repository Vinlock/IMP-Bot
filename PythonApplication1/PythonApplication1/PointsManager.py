import Database, settings
from time import sleep
import threading
import csv, string, random

class PointsManager(object):
    def __init__(self, client=None):
        self.db = Database.DB()
        self.client = client

        self.pointsPer = 1
        self.secondsPerIncrement = 60

        self.members = None

        print("Points Manage initiated.")

    def start(self):
        # Start Incrementing Points
        self.thread(self.beginIncrement)

    def thread(self, function):
        t1 = threading.Thread(target=function)
        t1.daemon = True
        t1.start()

    def beginIncrement(self):
        while True:
            # sleep(self.secondsPerIncrement)
            print("Points increment has begun.")
            self.thread(self.incrementPoints)
            sleep(self.secondsPerIncrement)

    def incrementPoints(self):
        # Increments all members of each server by self.pointsPer
        allmembers = self.members
        for server, members in allmembers.items():
            if self.incrementList(server, members):
                print("Updated Points.")
            else:
                print("Failed to Update Points")

    def incrementList(self, serverid, listIDs):
        db = Database.DB()
        conn = db.new()
        cursor = conn.cursor()
        format_strings = ','.join(["'"+str(duo)+"'" for duo in listIDs])
        if "153648068040982528" in listIDs or 153648068040982528 in listIDs:
            print("TEST THERE")
        else:
            print("TEST NOT THERE")
        sql = "UPDATE `points` SET `points` = `points` + 1 WHERE `server`='{0}' AND `userid` IN ({1})".format(str(serverid), format_strings)
        if len(sql) > 65000:
            return False
        try:
            cursor.execute(sql)
            conn.commit()
            print(cursor._last_executed)
        except:
            return False
        cursor.close()
        conn.close()
        return True

    def checkpoints(self, serverid, memberid):
        row = self.db.sql("""SELECT points FROM points WHERE server=%s AND userid=%s""", int(serverid), int(memberid))
        return row[0]['points']

    def memberHasPoints(self, serverid, memberid):
        exists = self.db.sql("""SELECT count(*) as mem FROM points WHERE server=%s AND userid=%s""", int(serverid), int(memberid))
        if exists[0]["mem"] > 0:
            return True
        else:
            return False

    def givepoints(self, points, serverid, memberid):
        if self.memberHasPoints(serverid, memberid):
            self.db.sql("""UPDATE points SET points=points+%s WHERE server=%s AND userid=%s""", int(points), int(serverid), int(memberid))
            print(memberid, "given", points, "points.")
            return True
        else:
            self.db.sql("""INSERT INTO points (userid, points, server) VALUES (%s, %s, %s)""", int(memberid), int(points), int(serverid))
            print(memberid, "given", points, "points.")
            return True
        return False

    def minusPoints(self, points, serverid, memberid):
        if self.memberHasPoints(serverid, memberid):
            if int(self.checkpoints(serverid, memberid)) < points:
                return False
            elif int(self.checkpoints(serverid, memberid)) > points:
                self.db.sql("UPDATE points SET points=points-%s WHERE server=%s AND userid=%s", int(points), int(serverid), int(memberid))
                print(memberid, "lost", points, "points.")
                return True
        else:
            return False

    def updateList(self, dictionary):
        self.members = dictionary