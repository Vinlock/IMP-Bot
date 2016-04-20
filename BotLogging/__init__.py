import datetime
import time


def log(*strings):
    s = []
    for string in strings:
        s.append(str(string))
    split_string = " ".join(s)
    print(split_string)
    split_string = time.strftime("%Y-%m-%d %H:%M") + " === " + split_string
    today = datetime.date.today()
    fileName = today.strftime("%Y-%m-%d-%H")
    with open("log/" + fileName + ".log", "a") as myfile:
        myfile.write(split_string + "\n")
