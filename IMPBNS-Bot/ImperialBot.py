import discord, asyncio, pymysql
from time import sleep

# Import Local Files
import Database, settings, Betting, PointsManager, ImpMatch

from ImpMatch import Match

class ImperialBot(object):

    def __init__(self):
        self.client = discord.Client()

        self.matches = dict()

        self.channels = dict()

        self.users = dict()

        @self.client.event
        async def on_ready():
            print("Logged in as", self.client.user.name)
            print("Client User ID", self.client.user.id)
            print("-------------------------")
            for server in self.client.servers:
                self.matches[str(server.id)] = None
                print(server.name, ":")
                print("Roles:")
                for role in server.roles:
                    print(role.id, role.name)
                print("Channels:")
                for channel in server.channels:
                    self.channels[channel.name] = channel
                    print(channel.id, channel.name)
            
            self.startPoints()
                
        self.listener()

        self.client.run(settings.DISCORD_USERNAME, settings.DISCORD_PASSWORD)

    def startPoints(self):
        self.points = PointsManager.PointsManager(self.client)
        self.points.start()

    def listener(self):
        @self.client.event
        async def on_message(msg):
            channel = msg.channel               # Message Channel
            author = msg.author                 # Message Author
            server = msg.server                 # Message Server
            serverid = str(server.id)           # String Server ID
            message = msg.content               # Get Message Content
            mentions = msg.mentions             # Mentions in Message

            def sendm(m):
                return self.client.send_message(channel, m)

            def deletem(m):
                return self.client.delete_message(m)

            def sendToBetting(m):
                return self.client.send_message(self.channels['betting'], m)

            # For "!" Commands
            if message.startswith("!"):
                message = message[1:]               # Get Message Content minus "!"
                params = message.split(" ")         # Split message into list.
                command = params[0]                 # First Element is the Command
                rest = " ".join(params[1:])         # Everything but command as string.
                numParams = len(params) - 1         # Number of Parameters
                mentionstr = author.mention + " - " # Mention prefix

                # USER COMMANDS
                # Betting Channel
                if channel.id == settings.Channels.BETTING:
                    if command == "betred":
                        if numParams < 1:
                            await sendm(mentionstr + "You did not state your bet amount. Ex: \"!betred 100\"")
                        elif numParams > 1:
                            await sendm(mentionstr + "You have used too many parameters for this command. Ex: \"!betred 100\"")
                        else:
                            amount = int(params[1])
                            if self.matches[serverid] == None:
                                await sendm(mentionstr + "No matches have been started as of yet")
                            else:
                                self.matches[serverid].addVote(author, "red", amount)
                                await sendm(":red_circle: - " + author.mention + " you have placed a bet on **RED** for " + str(amount) + " points.")
                    elif command == "betblue":
                        if numParams < 1:
                            await sendm(mentionstr + "You did not state your bet amount. Ex: \"!betblue 100\"")
                        elif numParams > 1:
                            await sendm(mentionstr + "You have used too many parameters for this command. Ex: \"!betblue 100\"")
                        else:
                            amount = int(params[1])
                            if self.matches[serverid] == None:
                                await sendm(mentionstr + "No matches have been started as of yet")
                            else:
                                self.matches[serverid].addVote(author, "blue", amount)
                                await sendm(":large_blue_circle: - " + author.mention + " you have placed a bet on **BLUE** for " + str(amount) + " points.")
                    elif command == "points" and numParams >= 1:
                        await deletem(msg)
                        if self.checkpower(author):
                            for user in mentions:
                                await sendm(user.mention + " has " + str(self.points.checkpoints(server.id, user.id)) + " points.")
                        else:
                            await sendm(mentionstr + "Insufficient Permissions")
                    elif command == "points":
                        await deletem(msg)
                        await sendm(mentionstr + "has " + str(self.points.checkpoints(server.id, author.id)) + " points.")
                    

                # Any channel
                if command == "start":
                    await deletem(msg)
                    if self.checkpower(author):
                        if self.matches[serverid] == None:
                            self.matches[serverid] = ImpMatch.Match(server.id)
                            await sendm("Betting has begun for the " + self.convertNumber(self.matches[server.id].round) + " round! Place Your Bets!")
                        else:
                            await sendm(mentionstr + "Matches have already been started")
                    else:
                        await sendm(mentionstr + "Insufficient Permissions")
                elif command == "end":
                    await deletem(msg)
                    if self.checkpower(author):
                        if self.matches[serverid] == None:
                            await sendm(mentionstr + "Matches have not been started yet.")
                        else:
                            self.matches[serverid] = None
                            await sendm("Matches have ended")
                    else:
                        await sendm(mentionstr + "Insufficient Permissions")
                elif command == "give":
                    await deletem(msg)
                    if self.checkpower(author):
                        if numParams < 0:
                            await sendm("Give command requires parameters \"!give <mention> <points>\"")
                        else:
                            mention = params[1]
                            points = int(params[2])
                            mentioned = mentions[0].id
                            trygive = self.points.givepoints(points, server.id, mentioned)
                            if trygive:
                                tosend = str(points) + " points given to " + mentions[0].mention
                                await sendToBetting(tosend)
                            else:
                                await sendm(mentionstr + " - Give Failed.")
                    else:
                        await sendm(mentionstr + "Insufficent Permissions")
                elif command == "redwin":
                    await deletem(msg)
                elif command == "masspts":
                    await deletem(msg)
                    if not self.points.incrementPoints():
                        await sendm("Error Incrementing Points")


                # Any Channel
                if command == "hi":
                    await sendm("hi")
                elif command == "purge":
                    if self.checkpower(author):
                        await deletem(msg)
                        if numParams < 1:
                            fail = await sendm(mentionstr + "You must say how many messages you would like to purge.")
                        else:
                            numDelete = int(params[1])
                        if self.checkpower(author):
                            async for log in client.logs_from(channel, limit=numDelete):
                                deletem(log)
                    else:
                        await sendm(mentionstr + "Insufficent Permissions")

                    
    def checkpower(self, author):
        if settings.Roles.check(author, settings.Roles.DEVELOPER) or settings.Roles.check(author, settings.Roles.ADMIN):
            return True
        else:
            return False

    def convertNumber(self, num):
        number = str(num)
        if number.endswith("1"):
            return str(number) + "st"
        elif number.endswith("2"):
            return str(number) + "nd"
        elif number.endswith("3"):
            return str(number) + "rd"
        else:
            return str(number) + "th"


bot = ImperialBot()
