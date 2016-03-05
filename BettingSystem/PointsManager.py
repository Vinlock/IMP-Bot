import Database, threading

class PointsManager(object):
    def __init__(self, client=None):
        self.client = client

        print("Points Manager initiated.")

    def thread(self, function):
        t1 = threading.Thread(target=function)
        t1.daemon = True
        t1.start()

    def checkpoints(self, serverid, memberid):
        conn = Database.DB()
        with conn.cursor() as cursor:
            sql = "SELECT `points` FROM `points` WHERE `server`={0} AND `userid`={1}".format(str(serverid), str(memberid))
            cursor.execute(sql)
            for row in cursor:
                conn.close()
                return row['points']

    def memberHasPoints(self, serverid, memberid):
        conn = Database.DB()
        with conn.cursor() as cursor:
            sql = "SELECT count(*) as membercheck FROM points WHERE server={0} AND userid={1}".format(str(serverid), str(memberid))
            cursor.execute(sql)
            for row in cursor:
                exists = row['membercheck']
                break
            conn.close()
            if exists > 0:
                return True
            else:
                return False

    def givepoints(self, points, serverid, memberid):
        conn = Database.DB()
        if self.memberHasPoints(serverid, memberid):
            with conn.cursor() as cursor:
                sql = "UPDATE `points` SET `points`=points+{0} WHERE server={1} AND userid={2}".format(str(points), str(serverid), str(memberid))
                cursor.execute(sql)
                conn.commit()
                print(cursor._last_executed)
            conn.close()
            print(memberid, "given", points, "points.")
            return True
        elif not self.memberHasPoints(serverid, memberid):
            with conn.cursor() as cursor:
                sql = "INSERT INTO `points` (`userid`, `points`, `server`) VALUES ({0}, {1}, {2})".format(str(memberid), str(points), str(serverid))
                cursor.execute(sql)
                conn.commit()
                print(cursor._last_executed)
            conn.close()
            print(memberid, "given", points, "points.")
            return True
        return False

    def minusPoints(self, points, serverid, memberid):
        conn = Database.DB()
        if self.memberHasPoints(serverid, memberid):
            if int(self.checkpoints(serverid, memberid)) < points:
                return False
            elif int(self.checkpoints(serverid, memberid)) > points:
                with conn.cursor() as cursor:
                    sql = "UPDATE `points` SET `points`=points-{0} WHERE server={1} AND userid={2}".format(str(points), str(serverid), str(memberid))
                    cursor.execute(sql)
                    conn.commit()
                    print(cursor._last_executed)
                conn.close()
                print(memberid, "lost", points, "points.")
                return True
        else:
            return False