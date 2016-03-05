class Response(object):
    def __new__(command):
        methodToCall = getattr(self, command)
        return methodToCall()

    def help(self):
        return "**COMMANDS**" \
               "If bets are open:" \
               "!bet <red or blue> <points> - Bet on a team." \
               "!points - Check how many points you have."