# import ControlBot
import Bot, threading
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger()
logger.addHandler(logging.FileHandler(time.strftime("%H:%M:%S")+'.log', 'a'))
print = logger.info

def thread(self, function):
    t1 = threading.Thread(target=function)
    t1.daemon = True
    t1.start()

print("Starting Bot...")
bot = Bot.Bot()
# control = ControlBot.ControlBot()