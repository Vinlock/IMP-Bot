# import ControlBot
import Bot
import threading
import datetime
from BotLogging import log


def thread(function):
    t1 = threading.Thread(target=function)
    t1.daemon = True
    t1.start()

print("Starting Bot...")
bot = Bot.Bot()
# control = ControlBot.ControlBot()