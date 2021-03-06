import threading
import sys
import discord
from time import sleep
from random import randint
import re
import struct
import doctest
# Import Local Files
from BettingSystem import PointsManager as Points, ImpMatch as Match, AutoIncrement as Increment
import Database
from Tournament import Tournament as tourney
import ObjectDict
import settings


class Bot(object):
    def __init__(self):
        print("== Bot is starting.")
        self.client = discord.Client()
        print("== Discord Client Initiated")

        # Dictionary of Channel Objects
        self.channels = dict()
        self.roles = dict()

        self.matches = dict()

        self.tournaments = dict()

        self.points = None

        self.increment = None

        self.staff = dict()

        self.guess = True

        self.rollvs = False

        self.pvd_active = dict()

        self.checkin = False

        self.checkedin = []

        @self.client.event
        async def on_ready():
            print("== Logged in as", self.client.user.name)
            print("== Client User ID", self.client.user.id)
            print("== -----------------------------------")
            for server in self.client.servers:
                self.matches[server.id] = None
                self.tournaments[server.id] = None
                self.channels[server.id] = dict()
                self.roles[server.id] = dict()
                self.staff[server.id] = dict()
                self.pvd_active[server.id] = []
                print(server.name, ":")
                print("== Roles:")
                for role in server.roles:
                    print(role.id, role.name.lower())
                    self.roles[server.id][role.name.lower()] = dict()
                    self.roles[server.id][role.name.lower()]['object'] = role
                    self.roles[server.id][role.name.lower()]['members'] = []
                for member in server.members:
                    for role in member.roles:
                        self.roles[member.server.id][role.name.lower()]['members'].append(member)

            self.thread(self.updateMembers)

            print("== Finished creating dictionaries for Roles, Channels, and Possible Match Servers.")

            self.points = Points.PointsManager(self.client)

            self.increment = Increment.Increment()
            self.increment.start()

            for server in self.client.servers:
                try:
                    self.client.send_message(self.channels[server.id]["testing"], "ONLINE")
                except KeyError:
                    continue

            self.thread(self.updateList)

        @self.client.event
        async def on_server_join(server):
            print("Joined", server.name)
            self.matches[server.id] = None
            self.tournaments[server.id] = None
            self.channels[server.id] = dict()
            self.roles[server.id] = dict()
            print(server.name, ":")
            print("Roles:")
            for role in server.roles:
                print(role.id, role.name.lower())
                self.roles[server.id][role.name.lower()] = role
            print("Channels:")
            for channel in server.channels:
                self.channels[server.id][channel.name] = channel
                print(channel.id, channel.name)

        @self.client.event
        async def on_member_join(member):
            self.points.insertNewMember(member.id, member.server.id)

        @self.client.event
        async def on_message(message):
            print("--------------------------------------")
            print("Author ID: " + message.author.id)
            print("Channel ID: " + message.channel.id)
            print("Server ID: " + message.server.id)
            print("Message: " + message.content)
            print("--------------------------------------")
            info = {
                "channel": message.channel,
                "author": message.author,
                "server": message.server,
                "mentions": message.mentions
                }
            # if "Kappa" in message.content:
            #     await self.client.send_file(message.channel, "files/kappa1.png")
            if "fuck" in message.content and "bot" in message.content:
                await self.client.send_message(message.channel, message.author.mention + " - hey... :(")
            if message.content is "!":
                print("== Nothing happened.")
            elif message.content.startswith("!"):
                msg_parts = message.content[1:]
                params = msg_parts.split(" ")
                command = params[0]
                rest = " ".join(params[1:])
                numParams = len(params) - 1

                def sender(msg):
                    return self.client.send_message(info['channel'], msg)

                def reply(msg):
                    return self.client.send_message(message.channel, message.author.mention + " - " + msg)

                def deleter(msg):
                    return self.client.delete_message(msg)

                def pm(who, msg):
                    return self.client.send_message(who, msg)

                def wait(time):
                    return self.client.wait_for_message(timeout=time, author=message.author)

                def waitfor(time, author):
                    return self.client.wait_for_message(timeout=time, author=author, channel=message.channel)

                def sendToBetting(msg):
                    return self.client.send_message(discord.utils.get(message.server.channels, name="tournament-betting"), msg)

                async def deleteFromList(list):
                    # Fixed #9
                    for m in list:
                        await deleter(m)

                # ! Commands
                if command == "help" or command == "commands" or command == "command":
                    await sender("__**NORMAL COMMANDS**__\n\n"
                                 "**!points** - Check how many points you have.\n\n\n"
                                 "__**BETTING COMMANDS**__\n\n"
                                 "**!bet <red or blue> <points>** - Bet on a team.\n"
                                 "**!cancel** - Retract your bet.\n"
                                 "**!percent** - View the team bet percentages.\n"
                                 "**!who <red or blue>** - See who is red and who is blue\n\n\n"
                                 "__**FUN COMMANDS**__\n\n"
                                 + ("" if self.rollvs else "**DISABLED:** == ") + "**!pvd <bet amount> <max roll> <mention>** - Roll versus an opponent if they accept the bet/challenge.\n"
                                 + ("" if self.guess else "**DISABLED:** == ") + "**!guess <number 10 or greater>** - The bot will think of a number, if you can guess it you win the jackpot, if you get close you win some points. You bet points equal to the number you choose.\n\n\n")
                elif command == "color":
                    def hex_to_rgb(value):
                        value = value.lstrip('#')
                        lv = len(value)
                        r, g, b = tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
                        return int('%02x%02x%02x' % (r, g, b), 16)
                    if self.checkpower(message.author) or self.adminpower(message.author):
                        rolename = " ".join(params[2:])
                        role = discord.utils.get(message.server.roles, name=rolename)
                        hex = params[1]
                        if re.search(r'^(?:[0-9a-fA-F]{3}){1,2}$', hex):
                            try:
                                int_hex = hex_to_rgb(hex)
                            except ValueError:
                                await reply("Invalid Hex Color")
                            else:
                                if self.client.edit_role(role=role, colour=discord.Colour(int_hex), server=message.server):
                                    await reply("Color of " + role.name + " changed!")
                        else:
                            await reply("Invalid Hex Color")
                    else:
                        await reply("Insufficient Permissions.")
                elif command == "guess":
                    tried_zero = False
                    await deleter(message)
                    msgs = []
                    if numParams < 1 or numParams > 1:
                        await reply("Invalid amount of parameters. **!guess <number greater than 10>**.\n"
                                    "**YOU WILL BET THE AMOUNT YOU SET AS YOUR MAX GUESS!!!!**")
                    else:
                        if self.adminpower(message.author) and params[1] == "on":
                            self.guess = True
                            await reply("The !guess command has been turned on!")
                        elif self.adminpower(message.author) and params[1] == "off":
                            self.guess = False
                            await reply("The !guess command has been turned OFF!")
                        elif self.guess:
                            number = params[1]
                            if number.startswith("0"):
                                while number.startswith("0"):
                                    number = number[1:]
                                tried_zero = True
                            try:
                                int(number)
                            except ValueError:
                                await reply("You did not enter a valid number parameter. **!guess <number greater than 10>**")
                            else:
                                if tried_zero:
                                    msgs.append(await reply("Nice try, your new number is **" + str(number) + "**."))
                                if int(number) < 10:
                                    await reply("You must choose a number parameter that is 10 or greater.")
                                else:
                                    if self.points.checkpoints(message.server.id, message.author.id) >= int(number):
                                        if (self.points.minusPoints(int(number), message.server.id, message.author.id)):
                                            msgs.append(await reply(str(number) + " points bet. Respond within 30 seconds, or you will lose your points."))
                                            n = randint(1, int(number))
                                            print("== CHEAT SHEET - The number is:", n)
                                            msgs.append(await reply("Guess a number from 1-" + str(number) + ". You have 30 seconds."))
                                            r = await wait(30)
                                            # msgs.append(r)
                                            try:
                                                if int(r.content) > int(number) or int(r.content) < 1:
                                                    await reply("You chose a number out of range. Please try !guess again!")
                                                    await deleteFromList(msgs)
                                                else:
                                                    try:
                                                        int(r.content)
                                                    except ValueError:
                                                        await reply("You have not entered an integer. Please try !guess <number greater than 10> again!")
                                                        await deleteFromList(msgs)
                                                    else:
                                                        if int(number) <= 95:
                                                            rng = int(int(number) * 0.20)
                                                        else:
                                                            rng = int(int(number) * 0.15)
                                                        if rng < 1:
                                                            rng = 1
                                                        start = n - rng
                                                        ending = n + rng
                                                        if int(r.content) == n:
                                                            points = int(number) * len(number)
                                                            if points < 1:
                                                                points *= 100
                                                            points = int(points)
                                                            self.points.givepoints(points, message.server.id, message.author.id)
                                                            await reply("CORRECT! The number was " + str(n) +"! You have won **" + str(points) + ("** (Gained **" if int(points) > int(number) else "** (Lost **") + str(abs(int(number) - int(points))) + "**)")
                                                            await deleteFromList(msgs)
                                                        elif int(start) <= int(r.content) <= int(ending):
                                                            if int(r.content) < n:
                                                                needle = int(r.content) - start
                                                                percent = needle / rng
                                                                points = (int(number) * len(number)) * percent
                                                                if points < 1:
                                                                    points *= 100
                                                                points = int(points)
                                                                self.points.givepoints(points, message.server.id, message.author.id)
                                                                await reply("Close! The number was **" + str(n) + "**. You have won **" + str(points) + ("** (Gained **" if int(points) > int(number) else "** (Lost **") + str(abs(int(number) - int(points))) + "**) points back :P.")
                                                                await deleteFromList(msgs)
                                                            elif int(r.content) > n:
                                                                needle = ending - int(r.content)
                                                                percent = needle / rng
                                                                points = (int(number) * len(number)) * percent
                                                                if points < 1:
                                                                    points *= 100
                                                                points = int(points)
                                                                self.points.givepoints(points, message.server.id, message.author.id)
                                                                await reply("Close! The number was **" + str(n) + "**. You have won **" + str(points) + ("** (Gained **" if int(points) > int(number) else "** (Lost **") + str(abs(int(number) - int(points))) + "**) points back :P.")
                                                                await deleteFromList(msgs)
                                                        else:
                                                            await reply("Nope. The number was **" + str(n) + "**. Try !guess again later!")
                                                            await deleteFromList(msgs)
                                            except ValueError:
                                                await reply("You did not enter a number. Please try **!guess** again later.")
                                                await deleteFromList(msgs)
                                        else:
                                            await reply("Sorry the bet failed. Ask Vinlock to check out why.")
                                            await deleteFromList(msgs)
                                    else:
                                        await reply("Insufficient Points. It will cost " + str(number) + " points to play.")
                                        await deleteFromList(msgs)
                        else:
                            await reply("Sorry the command is currently disabled.")
                elif command == "purge":
                    await deleter(message)
                    if self.adminpower(message.author):
                        if numParams < 1:
                            sender("Please specify how many messages to purge.")
                        elif numParams == 1:
                            numDelete = int(params[1])
                            if numDelete < 0:
                                numDelete *= -1
                            async for log in self.client.logs_from(message.channel, limit=numDelete):
                                await deleter(log)
                        elif numParams == 2:
                            numDelete = int(params[2])
                            if numDelete < 0:
                                numDelete *= -1
                            async for log in self.client.logs_from(message.channel, limit=numDelete*100):
                                if log.author == message.mentions[0]:
                                    if numDelete > 0:
                                        await deleter(log)
                                        numDelete -= 1
                        elif numParams > 2:
                            sender("Invalid Command Parameters")
                elif command == "ow":
                    newRole = discord.utils.get(message.server.roles, name="OVERWATCH HYPE TRAIN")
                    await self.client.add_roles(message.author, newRole)
                elif command == "bns":
                    newRole = discord.utils.get(message.server.roles, name="bns")
                    await self.client.add_roles(message.author, newRole)
                elif command == "checkin":
                    newRole = discord.utils.get(message.server.roles, name="Tournament Participant")
                    if numParams == 1:
                        if self.checkpower(message.author) or self.adminpower(message.author):
                            option = params[1].lower()
                            valid_options = ["on", "off", "clear"]
                            if option in valid_options:
                                if option == "on":
                                    self.checkin = True
                                    await sender("@everyone - Check-ins have been turned on. Do !checkin to check in for the Tournament!")
                                elif option == "off":
                                    self.checkin = False
                                    await sender("@everyone - Check-ins have been turned off.")
                                elif option == "clear":
                                    for person in self.checkedin:
                                        await self.client.remove_roles(person, newRole)
                                    self.checkin = False
                                    await reply("Check-ins have been reset and turned off.")
                            else:
                                await reply("Invalid option chosen.")
                        else:
                            reply("Invalid Permissions")
                    elif numParams > 1:
                        await reply("Invalid parameters")
                    elif self.checkin:
                        if message.author not in self.checkedin:
                            await self.client.add_roles(message.author, newRole)
                            self.checkedin.append(message.author)
                            await reply("You have checked in")
                        else:
                            await reply("You have already checked in.")
                    else:
                        await reply("Check-ins are disabled at the moment")
                elif command == "version":
                    await sender("Imperial Bot v0.9.1b - Created By: Vinlock")
                elif command == "admin":
                    if self.checkpower(message.author):
                        await pm(message.author, "__**COMMANDS**__\n**!purge <number of messages>"
                                   " <mention user ***OPTIONAL***>** - Purges X "
                                   "number of messages in the channel. Optionally "
                                   "mention a user to purge only their messages.\n"
                                   "**!give <mention user> <points>** - Give a user"
                                   " a certain number of points. (Cap: 50000)\n"
                                   "**!start** - Start a round of betting.\n"
                                   "**!set <team> <mention user>** - Give each "
                                   "team a name.\n**!match** - Ends betting "
                                   "and announces that the match is underway.\n"
                                   "**!points <mention user>** - Check a users "
                                   "points total.")
                    else:
                        print("== Nope")
                elif command == "exit":
                    await deleter(message)
                    if self.adminpower(message.author):
                        await sender("Exiting...")
                        sys.exit()
                # TOURNAMENT STUFF
                elif command == "tournament":
                    if self.adminpower(message.author):
                        if numParams < 1 or numParams > 1:
                            await sender(message.author.mention + " - You did not input the correct parameters."
                                                                  " **Example:** !tournament <start or end>")
                        todo = params[1]
                        if todo == "start":
                            if self.tournaments[message.server.id] is None:
                                self.tournaments[message.server.id] = tourney.Tournament(message.server.id, message.author)
                                if self.tournaments[message.server.id].start():
                                    await self.client.send_message(self.channels[message.server.id]["waiting-room"],
                                                                   message.author.mention + " has started a new "
                                                                                            "tournament. Please use "
                                                                                            "**!checkin** to "
                                                                                            "check in or **!waitlist** "
                                                                                            "if you are waitlisted.")
                            else:
                                await sender(message.author.mention + " - A tournament has already been started by " +
                                             self.tournaments[message.server.id].starter.mention + ".")
                        elif todo == "end":
                            if self.tournaments[message.server.id] is None:
                                await sender(message.author.mention + " - There is no tournament started to end.")
                            else:
                                self.tournaments[message.server.id] = None
                                await sender("@everyone - The tournaments has ended. Thank you for your support and "
                                             "cooperation. We appreciate it and hope to see you next time!")
                        else:
                            await sender(message.author.mention + " - You did not input the correct parameters."
                                                                  " **Example:** !tournament <start or end>")
                    else:
                        await sender("")
                elif command == "game":
                    if self.adminpower(message.author):
                        game = rest
                        newgame = {"name": game}
                        newgame = ObjectDict.ObjectDict(newgame)
                        self.client.change_status(newgame)
                    else:
                        await sender(message.author.mention + " - Insufficient Permissions")
                elif command == "join":
                    await deleter(message)
                    if self.checkpower(message.author):
                        url = params[1]
                        try:
                            self.client.accept_invite(url)
                        except discord.HTTPException:
                            await sender("Request Failed")
                        except discord.InvalidArgument:
                            await sender("Invalid Invite URL.")
                        finally:
                            await sender("Joined.")
                elif command == "masspm":
                    print("== Mass PM initiated")
                    await deleter(message)
                    fails = []
                    if self.adminpower(message.author):
                        m = " ".join(params[2:])
                        try:
                            for member in message.server.members:
                                if await pm(member, m):
                                    print("PM sent to " + member.mention + " successfully.")
                        except discord.InvalidArgument:
                            await reply("Invalid Parameters")
                        except discord.HTTPException:
                            await reply("Message Failed")
                        finally:
                            await reply("Message Sent.\n" + m)
                    print("== Mass PM completed.")
                elif command == "pm":
                    await deleter(message)
                    if self.adminpower(message.author):
                        m = " ".join(params[2:])
                        who = message.mentions[0]
                        try:
                            await pm(who, m)
                        except discord.InvalidArgument:
                            await reply("Invalid Parameters")
                        except discord.HTTPException:
                            await reply("Message Failed")
                        finally:
                            await pm(message.author, "Message Sent to " + who.name + ".\n" + m)
                        print("== " + message.author.mention + " pmed " + who.mention)
                elif command == "na":
                    await deleter(message)
                    await self.client.remove_roles(message.author, self.roles[message.server.id]["na"]["object"])
                    await self.client.remove_roles(message.author, self.roles[message.server.id]["eu"]["object"])
                    await self.client.add_roles(message.author, self.roles[message.server.id]["na"]["object"])
                elif command == "eu":
                    await deleter(message)
                    await self.client.remove_roles(message.author, self.roles[message.server.id]["na"]["object"])
                    await self.client.remove_roles(message.author, self.roles[message.server.id]["eu"]["object"])
                    await self.client.add_roles(message.author, self.roles[message.server.id]["eu"]["object"])
                elif command == "cerulean":
                    await deleter(message)
                    await self.client.remove_roles(message.author, self.roles[message.server.id]["cerulean"]["object"])
                    await self.client.remove_roles(message.author, self.roles[message.server.id]["crimson"]["object"])
                    await self.client.add_roles(message.author, self.roles[message.server.id]["cerulean"]["object"])
                elif command == "crimson":
                    await deleter(message)
                    await self.client.remove_roles(message.author, self.roles[message.server.id]["cerulean"]["object"])
                    await self.client.remove_roles(message.author, self.roles[message.server.id]["crimson"]["object"])
                    await self.client.add_roles(message.author, self.roles[message.server.id]["crimson"]["object"])
                elif command == "points" or command == "pts":
                    if numParams == 1:
                        if self.adminpower(message.author):
                            await deleter(message)
                            for user in message.mentions:
                                await sender(user.mention +
                                             " has **" +
                                             str(self.points.checkpoints(message.server.id, user.id)) +
                                             "** points.")
                        else:
                            await reply("Insufficient permissions.")
                    else:
                        await sender(message.author.mention +
                                     " has **" +
                                     str(self.points.checkpoints(message.server.id, message.author.id)) +
                                     "** points.")
                elif command == "give":
                    await deleter(message)
                    if self.adminpower(message.author):
                        if numParams < 2:
                            await sender(message.author.mention + " - Give command requires parameters "
                                                                  "\"**Example:** !give <mention> <points>\"")
                        else:
                            person = message.mentions[0]
                            try:
                                points = int(params[2])
                            except ValueError:
                                await sender("Invalid points amount. Be sure to **not** use commas.")
                            else:
                                if points < 0:
                                    await reply("Amount must be greater than 0!")
                                else:
                                    if self.points.givepoints(points, message.server.id, person.id):
                                        await sender(message.author.mention + " gave " + str(points) +
                                                            " points to " + message.mentions[0].mention)
                                    else:
                                        await sender("Give Failed")
                    else:
                        await reply("Insufficient permissions.")
                elif command == "take":
                    await deleter(message)
                    if self.adminpower(message.author):
                        if numParams < 2 or numParams > 2:
                            await sender(message.author.mention + " - Take command requires parameters. "
                                                                  "\"**Example:** !take <mention> <points>\"")
                        else:
                            try:
                                points = int(params[2])
                                who = message.mentions[0]
                            except ValueError:
                                await sender("Invalid points amount. Be sure to **not** use commas.")
                            else:
                                if points < 0:
                                    await reply("Amount must be greater than 0!")
                                else:
                                    available_points = self.points.checkpoints(message.server.id, who.id)
                                    if points > available_points:
                                        await reply(who.mention + " only has " +
                                                     str(available_points) + " points, therefore not enough to take " +
                                                     str(points) + " points.")
                                    elif available_points > points:
                                        if self.points.minusPoints(points, message.server.id, who.id):
                                            await sender(message.author.mention + " has taken " + str(points) +
                                                         " points from " + who.mention + ".")
                                        else:
                                            await sender(message.author.mention + " Take failed!")
                    else:
                        await reply("Insufficient permissions.")
                elif command == "giveall":
                    await deleter(message)
                    if self.adminpower(message.author):
                        if numParams < 1 or numParams > 1:
                            await sender(message.author.mention + " - You must declare the number of points.")
                        else:
                            try:
                                points = int(params[1])
                            except ValueError:
                                await sender(message.author.mention +
                                             " - You must declare a number for points parameter.")
                            else:
                                list_ids = []
                                members = message.server.members
                                for member in members:
                                    status = member.status.value
                                    if status is not "offline":
                                        list_ids.append(member.id)
                                if self.points.massGive(message.server.id, list_ids, points):
                                    await sender(message.author.mention + " gave " + str(points) +
                                                 " points to @everyone!!\n\n:moneybag: :moneybag: :moneybag: "
                                                 ":moneybag: :moneybag: :moneybag: :moneybag: :moneybag: "
                                                 ":moneybag: :moneybag: :moneybag: :moneybag: ")
                elif command == "leaderboard":
                    leaderboard = self.points.topTen(message.server.id)
                    count = 1
                    send = ""
                    send += "__**Top 10 Points Leaderboard**__\n"
                    for person in leaderboard:
                        if count is not 1:
                            send += "\n"
                        member = discord.utils.get(message.server.members, id=str(person['id']))
                        send += str("__**"+str(count)+":**__ **"+member.name+"** - "+str(person['points']))
                        count += 1
                    await sender(send)
                elif command == "server":
                    if self.adminpower(message.author):
                        await deleter(message)
                        await self.client.send_message(message.author, "Server: **" + message.server.id + "**")
                elif command == "channel":
                    if self.adminpower(message.author):
                        await deleter(message)
                        await self.client.send_message(message.author, "Channel: **" + message.channel.id + "**")
                elif command == "reset":
                    if self.adminpower(message.author):
                        if numParams < 1 or params[1].lower() not in ["na", "eu", "all"]:
                            await reply("Invalid parameters")
                        else:
                            region = params[1]
                            if region.lower() == "na" or region.lower() == "eu":
                                await reply("Are you sure? (yes/no)")
                                sure = await wait(30)
                                if sure is not None:
                                    if "yes" in sure.content.lower():
                                        if region.lower() == "eu":
                                            if self.points.reset(123153051425964036):
                                                await reply("EU has been reset.")
                                            else:
                                                await reply("Error: nothing was reset.")
                                        elif region.lower() == "na":
                                            if self.points.reset(114150403280470021):
                                                await reply("NA has been reset.")
                                            else:
                                                await reply("Error: nothing was reset.")
                                        elif region.lower() == "all":
                                            if self.points.reset(0):
                                                await reply("All points have been reset.")
                                            else:
                                                await reply("Error: nothing was reset.")
                                    else:
                                        await reply("Ok, nothing was reset.")
                                else:
                                    await reply("Ok, nothing was reset.")
                elif command == "ddd":
                    if self.adminpower(message.author):
                        await reply(str(self.pvd_active))
                # Player-vs-Dice
                # if message.channel == self.channels[message.server.id]["player-versus-dice"]:
                if message.channel == discord.utils.get(message.server.channels, name="player-versus-dice"):
                    message.content.rstrip()
                    if command == "pvd":
                        def removeThem():
                            self.pvd_active[message.server.id].remove(message.author.id)
                            self.pvd_active[message.server.id].remove(message.mentions[0].id)
                        await deleter(message)
                        msgs = []
                        try:
                            # !rollvs <bet> <max> <mention>
                            if self.adminpower(message.author) and params[1].lower() == "on":
                                self.rollvs = True
                                await reply("The !pvd command has been turned ON!")
                            elif self.adminpower(message.author) and params[1].lower() == "off":
                                self.rollvs = False
                                self.pvd_active[message.server.id] = []
                                await reply("The !pvd command has been turned OFF!")
                            elif self.rollvs:
                                # Fixes #4
                                if message.author.id in self.pvd_active[message.server.id]:
                                    await reply("Sorry, it seems that you are currently apart of a PvD already.")
                                elif message.mentions[0].id in self.pvd_active[message.server.id]:
                                    await reply("Sorry, it seems that " + message.mentions[0].name + " is already apart of a PvD.")
                                else:
                                    self.pvd_active[message.server.id].append(message.author.id)
                                    self.pvd_active[message.server.id].append(message.mentions[0].id)
                                    if numParams < 3 or numParams > 3:
                                        await reply("Insufficient number of parameters.\n**\"!pvd <bet amount> <max roll> <mention>\"**")
                                        removeThem()
                                    else:
                                        try:
                                            bet = int(params[1])
                                            if bet < 0:
                                                raise ValueError
                                        except ValueError:
                                            await reply("Invalid bet amount.")
                                            removeThem()
                                        else:
                                            try:
                                                max = int(params[2])
                                                if max < 0:
                                                    raise ValueError
                                            except ValueError:
                                                await reply("Invalid max roll amount.")
                                                removeThem()
                                            else:
                                                if bet <= 0:
                                                    reply("Your bet must be greater than 0")
                                                    removeThem()
                                                elif max < 10:
                                                    reply("The max roll must be 10 or greater.")
                                                    removeThem()
                                                else:
                                                    who = message.mentions[0]
                                                    if message.author == who:
                                                        await reply("You **can't** bet against yourself. Sorry!")
                                                        removeThem()
                                                    else:
                                                        if int(self.points.checkpoints(message.server.id, message.author.id)) < bet:
                                                            await reply("Sorry you do not have a sufficient points balance to bet that amount.")
                                                            removeThem()
                                                        elif int(self.points.checkpoints(message.server.id, who.id)) < bet:
                                                            await reply(who.mention + " does not have sufficient points to bet that amount versus you.")
                                                            removeThem()
                                                        else:
                                                            self.points.minusPoints(bet, message.server.id, message.author.id)
                                                            msgs.append(await sender(who.mention + " - You have been challenged by " + message.author.mention + " in a roll off out of **" + str(max) + "** for **" + str(bet) + "** points.\nReply \"yes\" to accept. You have 30 seconds."))
                                                            answer = await waitfor(30, who)
                                                            try:
                                                                if "yes" in answer.content.lower():
                                                                    self.points.minusPoints(bet, message.server.id, who.id)
                                                                    msgs.append(await sender(who.mention + " has accepted " + message.author.mention + "'s challenge."))
                                                                    msgs.append(await sender(message.author.mention + " - you may roll now with \"!roll\". You have 30 seconds."))
                                                                    firstroll = await wait(30)
                                                                    msgs.append(firstroll)
                                                                    try:
                                                                        if "!roll" in firstroll.content.lower():
                                                                            roll1 = randint(1, max)
                                                                            msgs.append(await reply("You have rolled **" + str(roll1) + "**. Good Luck!"))
                                                                            msgs.append(await sender(who.mention + " -  you may roll now with \"!roll\". You have 30 seconds."))
                                                                            secondroll = await waitfor(30, who)
                                                                            msgs.append(secondroll)
                                                                            try:
                                                                                if "!roll" in secondroll.content.lower():
                                                                                    roll2 = randint(1, max)
                                                                                    msgs.append(await sender(who.mention + " - You have rolled **" + str(roll2) + "**!"))
                                                                                    if roll1 > roll2:
                                                                                        await sender(message.author.mention + " REKT " + who.mention + " and WINS **" + str(bet*2) + "** points!!!!")
                                                                                        self.points.givepoints(bet*2, message.server.id, message.author.id)
                                                                                        await deleteFromList(msgs)
                                                                                        removeThem()
                                                                                    elif roll1 < roll2:
                                                                                        await sender(who.mention + " REKT " + message.author.mention + " and WINS **" + str(bet*2) + "** points!!!!")
                                                                                        self.points.givepoints(bet*2, message.server.id, who.id)
                                                                                        await deleteFromList(msgs)
                                                                                        removeThem()
                                                                                    elif roll1 == roll2:
                                                                                        await sender("IT IS A TIE! Both " + who.mention + " and " + message.author.mention + " get their " + str(bet) + "points back!")
                                                                                        self.points.givepoints(bet, message.server.id, who.id)
                                                                                        self.points.givepoints(bet, message.server.id, message.author.id)
                                                                                        await deleteFromList(msgs)
                                                                                        removeThem()
                                                                                else:
                                                                                    await sender(who.mention + " - You didn't type **!roll**. Bet is cancelled.")
                                                                                    self.points.givepoints(bet, message.server.id, who.id)
                                                                                    self.points.givepoints(bet, message.server.id, message.author.id)
                                                                                    await deleteFromList(msgs)
                                                                                    removeThem()
                                                                            except AttributeError:
                                                                                await sender(who.mention + " - You took too long. " + message.author.mention + " wins **" + str(bet*2) + "** points!")
                                                                                self.points.givepoints(bet*2, message.server.id, message.author.id)
                                                                                await deleteFromList(msgs)
                                                                                removeThem()
                                                                        else:
                                                                            await reply("You didn't type **!roll**. Bet is cancelled.")
                                                                            self.points.givepoints(bet, message.server.id, who.id)
                                                                            self.points.givepoints(bet, message.server.id, message.author.id)
                                                                            await deleteFromList(msgs)
                                                                            removeThem()
                                                                    except AttributeError:
                                                                        await reply("You took too long. " + who.mention + " wins **" + str(bet*2) + "** points!")
                                                                        self.points.givepoints(bet*2, message.server.id, who.id)
                                                                        await deleteFromList(msgs)
                                                                        removeThem()
                                                                else:
                                                                    await reply("It looks like " + who.mention + " doesn't want to play or is AFK!")
                                                                    self.points.givepoints(bet, message.server.id, message.author.id)
                                                                    await deleteFromList(msgs)
                                                                    removeThem()
                                                            except AttributeError:
                                                                await reply("It looks like " + who.mention + " doesn't want to play or is AFK!")
                                                                self.points.givepoints(bet, message.server.id, message.author.id)
                                                                await deleteFromList(msgs)
                                                                removeThem()
                                    removeThem()
                            else:
                                await reply("Sorry that command is currently disabled.")
                        except IndexError:
                            await reply("Insufficient number of parameters.\n**\"!pvd <bet amount> <max roll> <mention>\"**")
                # Betting Commands
                # if message.channel == self.channels[message.server.id]["tournament-betting"]:
                if message.channel == discord.utils.get(message.server.channels, name="tournament-betting"):
                    if command == "bet":
                        if self.matches[message.server.id] is None:
                            await sender(message.author.mention + " - No match has been started yet.")
                        elif self.matches[message.server.id] is not None:
                            if not self.matches[message.server.id].bettingOpen:
                                await sender(message.author.mention + " - Betting has been closed")
                            elif self.matches[message.server.id].bettingOpen:
                                if numParams < 2:
                                    await sender(message.author.mention + " - You did not enter enough parameters. "
                                                                          "**Example:** \"!bet red 100\"")
                                elif numParams > 2:
                                    await sender(message.author.mention + " - You have used too many parameter for this "
                                                                          "command. Ex: \"!bet red 100\"")
                                elif numParams == 2:
                                    try:
                                        amount = int(params[2])
                                    except ValueError:
                                        await sender(message.author.mention + " - You did not enter a valid bet amount. "
                                                                              "Ex: \"!bet blue 100\"")
                                    else:
                                        if amount > 0:
                                            team = str(params[1].lower())
                                            if any(char.isdigit() for char in team):
                                                await sender(message.author.mention + " - You did not enter a valid team name. "
                                                                                      "Ex: \"!bet blue 100\"")
                                            elif team == "blue" or team == "red":
                                                if not self.matches[message.server.id].betted(message.author.id):
                                                    if self.matches[message.server.id].addVote(message.author,
                                                                                               team,
                                                                                               amount):
                                                        if team == "red":
                                                            icon = ":red_circle:"
                                                        elif team == "blue":
                                                            icon = ":large_blue_circle:"
                                                        else:
                                                            icon = ""
                                                        await sender(icon +
                                                                     " - " +
                                                                     message.author.mention +
                                                                     " you have placed a bet on **" +
                                                                     self.matches[message.server.id].getName(team.lower()) +
                                                                     "** for " +
                                                                     str(amount) +
                                                                     " points.")
                                                    else:
                                                        await sender(message.author.mention + " insufficient points to bet "
                                                                                              "that amount. You only have "
                                                                     + str(self.points.checkpoints(message.server.id,
                                                                                                   message.author.id)) +
                                                                     " points.")
                                                else:
                                                    await sender(message.author.mention + " you have already bet.")
                                            else:
                                                await sender(message.author.mention +
                                                             " - You did not enter a valid team name. "
                                                             "Ex: \"!bet blue 100\"")
                                        else:
                                            await sender(message.author.mention + " - You must bet more than 0.")
                    elif command == "start":
                        await deleter(message)
                        if self.checkpower(message.author):
                            if numParams < 2 or numParams > 2 or len(message.mentions) < 2 or len(message.mentions) > 2:
                                await sender(message.author.mention + " - Invalid Parameters. Must be **!start <mention"
                                                                      " BLUE> <mention RED>**")
                            else:
                                if self.matches[message.server.id] is None:
                                    self.matches[message.server.id] = Match.Match(message.server.id)
                                    for m in message.mentions:
                                        if m.mention == params[1]:
                                            self.matches[message.server.id].blueName = m
                                        elif m.mention == params[2]:
                                            self.matches[message.server.id].redName = m
                                    await sendToBetting("@everyone\n\n**Bets are open for this round! Place your Bets "
                                                        "with "
                                                        "\"!bet red <amount>\" or \"!bet blue <amount>\"!!**\n"
                                                        "--------------------------------\n"
                                                        ":large_blue_circle: **" +
                                                        self.matches[message.server.id].getName("blue") + "** vs. **" +
                                                        self.matches[message.server.id].getName("red") + "** "
                                                                                                         ":red_circle:")
                                else:
                                    await sender(message.author.mention + " - A match is already underway.")
                        else:
                            await sender(message.author.mention + " - Insufficient Permissions")
                    elif command == "match":
                        if numParams == 0:
                            while True:
                                try:
                                    await deleter(message)
                                    if self.checkpower(message.author):
                                        if self.matches[message.server.id] is None:
                                            await sender(message.author.mention + " - A match has not been started yet.")
                                        else:
                                            self.matches[message.server.id].closeBetting()
                                            await sender("@everyone - Betting has closed for this match. "
                                                         "Match is underway!")
                                    else:
                                        await sender(message.author.mention + " - Insufficient Permissions")
                                except discord.HTTPException:
                                    continue
                                break
                    elif command == "end":
                        await deleter(message)
                        if self.checkpower(message.author):
                            if self.matches[message.server.id] is None:
                                await sender(message.author.mention + " - There is no match to end.")
                            else:
                                self.matches[message.server.id] = None
                                await sender("This match has ended.")
                        else:
                            await sender(message.author.mention + " - Insufficient Permissions")
                    elif command.endswith("win"):
                        await deleter(message)
                        if self.checkpower(message.author):
                            if self.matches[message.server.id] is None:
                                await sender(message.author.mention + " - A match has not be started yet")
                            else:
                                if command == "redwin":
                                    winner = "red"
                                elif command == "bluewin":
                                    winner = "blue"
                                results = self.matches[message.server.id].cashout(winner)
                                # results_message = ""
                                await sender("**" + self.matches[message.server.id].getName(winner, True) +
                                             "** has won!")
                                for result in results:
                                    await sender(result.user.mention + " you have won **" + str(result.winnings) +
                                                 "** points.")
                                self.matches[message.server.id] = None
                                await sender("Match has ended.")
                    elif command == "percent":
                        if not self.matches[message.server.id].bettingOpen:
                            if self.matches[message.server.id] is not None:
                                red = self.matches[message.server.id].redPercent()
                                blue = self.matches[message.server.id].bluePercent()
                                await sender(":large_blue_circle: **" + self.matches[message.server.id].getName("blue") +
                                             "** - " + str(round(blue, 1)) + "% vs. " + str(round(red, 1)) + "% - **" +
                                             self.matches[message.server.id].getName("red") + "** :red_circle:")
                            else:
                                await sender(message.author.mention + " - No match has been started.")
                        else:
                            await sender(message.author.mention + " - You must wait until betting is over to check"
                                                                  " percents.")
                    elif command == "test":
                        await sender("Test")
                    elif command == "redratio":
                        await deleter(message)
                        if self.adminpower(message.author):
                            await sender(str(self.matches[message.server.id].redRatio()))
                    elif command == "blueratio":
                        await deleter(message)
                        if self.adminpower(message.author):
                            await sender(str(self.matches[message.server.id].blueRatio()))
                    elif command.startswith("set"):
                        if self.checkpower(message.author):
                            if not self.matches[message.server.id] is None:
                                if numParams < 2 or numParams > 2:
                                    await sender(message.author.mention + " - Incorrect number of parameters. "
                                                                          "!set <team> <mention user>")
                                else:
                                    team = params[1]
                                    user = message.mentions[0]
                                    if team == "red":
                                        self.matches[message.server.id].redName = user
                                        await sender(":red_circle: - You have set **RED**'s name to " +
                                                     self.matches[message.server.id].getName("red"))
                                    elif team == "blue":
                                        self.matches[message.server.id].blueName = user
                                        await sender(":large_blue_circle: - You have set **BLUE**'s name to " +
                                                     self.matches[message.server.id].getName("blue"))
                                    else:
                                        await sender(message.author.mention + " - Invalid Team.")
                            else:
                                await sender(message.author.mention + " - A match must be started first.")
                        else:
                            await sender(message.author.mention + " - Insufficient Permissions")
                    elif command == "who":
                        if not self.matches[message.server.id] is None:
                            if numParams == 1:
                                team = params[1]
                                team = team.lower()
                                if team == "red" or team == "blue":
                                    name = self.matches[message.server.id].getName(team)
                                    if team == "red":
                                        icon = ":red_circle:"
                                    elif team == "blue":
                                        icon = ":large_blue_circle:"
                                    else:
                                        icon = ""
                                    if name == "RED" or name == "BLUE":
                                        await sender(message.author.mention + " - Team name not set for " + team)
                                    else:
                                        await sender(icon + " **" + team.upper() + "** = " + name)
                                else:
                                    await sender(message.author.mention + " - You did not input a valid team.")
                            elif numParams == 0:
                                await sendToBetting(":large_blue_circle: **" +
                                                        self.matches[message.server.id].getName("blue") + "** vs. **" +
                                                        self.matches[message.server.id].getName("red") + "** "
                                                                                                         ":red_circle:")
                        else:
                            await sender(message.author.mention + " - No match has been started.")
                    elif command == "cancel":
                        if numParams < 1:
                            if self.matches[message.server.id].bettingOpen:
                                amt = self.matches[message.server.id].removeVote(message.author)
                                if amt is not False:
                                    if self.points.givepoints(amt, message.server.id, message.author.id):
                                        await sender(message.author.mention + " - Your bet has been removed.")
                                else:
                                    await sender(message.author.mention + " - You have not bet.")
                            else:
                                await sender(message.author.mention + " - Betting is closed for this match.")
                        if numParams == 1:
                            if self.checkpower(message.author):
                                amt = self.matches[message.server.id].removeVote(message.mentions[0])
                                if amt is not False:
                                    if self.points.givepoints(amt, message.server.id, message.mentions[0].id):
                                        await sender(message.author.mention + " has removed " +
                                                 message.mentions[0].mention +
                                                 "'s bet.")
                                else:
                                    await sender(message.author.mention + " - " + message.mentions[0].mention +
                                                 " has not bet.")
                            else:
                                await sender(message.author.mention + " - Insufficient Permissions")
                        if numParams > 1:
                            await sender(message.author.mention + " - Invalid amount of parameters. **Example:** "
                                                                  "\"!retract\"\nNo spaces too!")
        self.client.run(settings.DISCORD_TOKEN)

    def checkpower(self, author):
        for role in author.roles:
            check = role.name.lower()
            if check.endswith("*") or self.adminpower(author):
                return True
            else:
                continue
        if author.id == "148341618175377408":
            return True
        return False

    async def timeForPVD(self, message, minutes, toggle):
        channel = discord.utils.get(message.server.channels, name="player-versus-dice")
        seconds = minutes * 60
        set = seconds / 4
        for x in range(0, 4):
            print(str(set), str(seconds))
            if toggle == True:
                await self.client.send_message(channel, "@everyone - " + str(seconds / 60) + " minutes " + str(seconds % 60) + " seconds left until PvD is back online!")
            elif toggle == False:
                await self.client.send_message(channel, "@everyone - " + str(seconds / 60) + " minutes " + str(seconds % 60) + " seconds left until PvD self destructs!")
            seconds -= set
            sleep(int(set))
        self.client.send_message(channel, "@everyone - PvD is " + ("ONLINE" if toggle == True else "OFFLINE"))
        self.rollvs = toggle


    def adminpower(self, author):
        for role in author.roles:
            check = role.permissions.manage_server
            if check:
                return True
            else:
                continue
        if author.id == "148341618175377408":
            return True
        return False

    def thread(self, function, *args):
        t1 = threading.Thread(target=function, args=args)
        t1.daemon = True
        t1.start()

    def updateList(self):
        list_ids = dict()
        while True:
            servers = self.client.servers
            for server in servers:
                list_ids[server.id] = []
                members = server.members
                for member in members:
                    status = member.status.value
                    if status is not "offline":
                        list_ids[server.id].append(member.id)
                self.increment.updateList(list_ids)
            sleep(7)

    def updateMembers(self):
        conn = Database.DB()
        servers = self.client.servers
        # servers = copy.deepcopy(self.client.servers)
        print("...")
        for server in servers:
            print("== Generation of missing members for Server: " + server.name + " has begun...")
            members = server.members
            member_id_list = []
            for member in members:
                member_id_list.append(member.id)
            print("== Created " + server.name + " List. Updating Members...")
            i = 0
            print("...")
            for memberid in member_id_list:
                with conn.cursor() as cursor:
                    sql = "INSERT IGNORE INTO `points` SET `userid`={0}, `points`={1}, `server`={2};".format(int(memberid),
                                                                                                             50,
                                                                                                             int(server.id))
                    cursor.execute(sql)
                    conn.commit()
                    # Log.print("\033[94m" + cursor._last_executed + "\033[0m")
                i += 1
            print("== Successfully finished updating " + str(i) + " members for " + server.name + ".")
        print("== Done updating ALL members.")
        conn.close()