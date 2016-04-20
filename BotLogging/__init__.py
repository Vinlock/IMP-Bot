import datetime


def log(*strings):
    split_string = " ".join(strings)
    print(split_string)
    today = datetime.date.today()
    fileName = today.strftime("%Y-%m-%d-%H")
    with open("log/" + fileName + ".log", "a") as myfile:
        myfile.write(split_string + "\n")
