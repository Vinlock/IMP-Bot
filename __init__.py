# import ControlBot
import Bot, threading


def thread(function):
    t1 = threading.Thread(target=function)
    t1.daemon = True
    t1.start()

def start():
    print("Starting Bot...")
    Bot.Bot()

thread(start)

while True:
    input(">> ")

# print("Starting Bot...")
# bot = Bot.Bot()
# control = ControlBot.ControlBot()