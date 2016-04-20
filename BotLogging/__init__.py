import datetime

class Log:
    @staticmethod
    def log(*strings):
        today = datetime.date.today()
        fileName = today.strftime('%Y-%m-%d-%H')
        split_string = " ".join(strings)
        with open(fileName+".log", "a") as myfile:
            myfile.write(split_string)
        print(strings)