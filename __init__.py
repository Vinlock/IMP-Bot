# import ControlBot
import Bot
import threading
import datetime
import sys

logPath = "log"
today = datetime.date.today()
fileName = today.strftime('%Y-%m-%d-%H')

sys.stdout = open(fileName+".txt", "w")


def thread(function):
    t1 = threading.Thread(target=function)
    t1.daemon = True
    t1.start()

print("Starting Bot...")
bot = Bot.Bot()
# control = ControlBot.ControlBot()