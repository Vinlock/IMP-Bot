import Bot
import discord
import settings

class ControlBot(object):
    def __init__(self):
        self.client = discord.Client()

        self.bot = Bot.Bot()

        @self.client.event
        async def on_ready():
            print('Control Bot Logged in as')
            print(self.client.user.name)
            print(self.client.user.id)
            print('------')

        @self.client.event
        async def on_message(message):
            if message.content.startswith('$'):
                msg = message.content
                splitmsg = msg.split(" ")
                command = splitmsg[0][1:]
                args = splitmsg[1:]
                if self.bot.adminpower(message.author):
                    if command == "start":
                        self.bot.client.loop.close()
                        self.bot = None
                        self.bot = Bot.Bot()
                        await self.client.delete_message(message)
                        self.bot.startbot()
                    if command == "restart":
                        await self.client.delete_message(message)
                        await self.bot.client.logout()
                        self.bot = None
                        self.bot = Bot.Bot()
                        self.bot.startbot()
                    if command == "stop":
                        await self.client.delete_message(message)
                        await self.bot.client.logout()
                        self.bot.client.close()
                        self.bot = None

        self.client.run(settings.DISCORD_USERNAME, settings.DISCORD_PASSWORD)