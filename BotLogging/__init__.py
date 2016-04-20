import datetime


def log(*strings):
    today = datetime.date.today()
    fileName = today.strftime("%Y-%m-%d-%H")
    split_string = " ".join(strings)
    with open("log/" + fileName + ".log", "a") as myfile:
        myfile.write(split_string + "\n")
    print(split_string)
