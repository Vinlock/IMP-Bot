# import ControlBot
import Bot
import threading
import logging
import datetime

logPath = "log"
fileName = today.strftime('%Y-%m-%d')

import sys

class Logger(object):
    def __init__(self):
        print("== Logging Started")
        self.terminal = sys.stdout
        self.log = open("log/"+fileName+".log", "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        #this flush method is needed for python 3 compatibility.
        #this handles the flush command by doing nothing.
        #you might want to specify some extra behavior here.
        pass

sys.stdout = Logger()


def thread(function):
    t1 = threading.Thread(target=function)
    t1.daemon = True
    t1.start()

print("Starting Bot...")
bot = Bot.Bot()
# control = ControlBot.ControlBot()