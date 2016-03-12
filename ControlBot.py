import Bot
import discord
import settings

class ControlBot(object):
    def __init__(self):
        client = discord.Client()

        bot = Bot.Bot()

        @client.event
        async def on_ready():
            print('Control Bot Logged in as')
            print(client.user.name)
            print(client.user.id)
            print('------')

        @client.event
        async def on_message(message):
            if message.content.startswith('$'):
                msg = message.content
                splitmsg = msg.split(" ")
                command = splitmsg[0][1:]
                args = splitmsg[1:]
                if self.bot.adminpower(message.author):
                    if command == "start":
                        self.bot.run()
                    if command == "restart":
                        self.bot.client.logout()
                        self.bot = None
                        self.bot = Bot.Bot()
                    if command == "stop":
                        self.bot.client.logout()

        client.run(settings.DISCORD_USERNAME, settings.DISCORD_PASSWORD)