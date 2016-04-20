# import ControlBot
import Bot
import threading
import logging
import datetime

logPath = "log"
fileName = today = datetime.date.today()

logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger()

fileHandler = logging.FileHandler("{0}/{1}.log".format(logPath, fileName))
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)


def thread(function):
    t1 = threading.Thread(target=function)
    t1.daemon = True
    t1.start()

print("Starting Bot...")
bot = Bot.Bot()
# control = ControlBot.ControlBot()