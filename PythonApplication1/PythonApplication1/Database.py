import pymysql.cursors, settings

class DB(object):
    def __init__(self):
        self.connection = None

        self.connect()

    def sql(self, query, *args):
        while (True):
            try:
                with self.connection.cursor() as cursor:
                    if cursor.execute(query, args):
                        if query[:6] == "SELECT":
                            return cursor.fetchall()
                        elif query[:6] == "INSERT":
                            self.connection.commit()
                            return cursor.lastrowid
                        elif self.connection.commit():
                            return True
            except ConnectionError:
                self.connect()
            break

    def sqlmany(self, query, *args):
        while (True):
            try:
                with self.connection.cursor() as cursor:
                    if cursor.executemany(query, args):
                        return True
            except ConnectionError:
                self.connect()
            break

    def connect(self):
        self.connection = pymysql.connect(host=settings.DBHOST, user=settings.DBUSER, password=settings.DBPASS, db=settings.DATABASE, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

    def new(self):
        return pymysql.connect(host=settings.DBHOST, user=settings.DBUSER, password=settings.DBPASS, db=settings.DATABASE, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)