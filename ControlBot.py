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
                        await self.client.delete_message(message)
                        await self.bot.client.run(settings.DISCORD_USERNAME, settings.DISCORD_PASSWORD)
                    if command == "restart":
                        await self.client.delete_message(message)
                        await self.bot.client.logout()
                        self.bot = None
                        self.bot = Bot.Bot()
                    if command == "stop":
                        await self.client.delete_message(message)
                        await self.bot.client.logout()

        self.client.run(settings.DISCORD_USERNAME, settings.DISCORD_PASSWORD)