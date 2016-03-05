import pymysql, settings

class DB(object):
    def __new__(cls):
        return pymysql.connect(host=settings.DBHOST, user=settings.DBUSER, password=settings.DBPASS, db=settings.DATABASE, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)