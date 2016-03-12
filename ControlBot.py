import Bot
import discord
import settings

class ControlBot(object):
    def __init__(self):
        self.client = discord.Client()

        self.bot = None

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
                if self.adminpower(message.author):
                    if command == "start":
                        await self.client.delete_message(message)
                        if self.bot is None:
                            self.bot = Bot.Bot()
                            self.bot.startbot()
                        else:
                            await self.client.send_message(message.channel, "Bot already started")
                    if command == "restart":
                        await self.client.delete_message(message)
                        if self.bot is not None:
                            await self.bot.client.logout()
                            await self.bot.client.stop()
                            await self.bot.client.close()
                            self.bot = None
                            self.bot = Bot.Bot()
                            self.bot.startbot()
                    if command == "stop":
                        await self.client.delete_message(message)
                        if self.bot is not None:
                            await self.bot.client.logout()
                            await self.bot.client.stop()
                            await self.bot.client.close()
                            self.bot.client.close()
                            self.bot = None

        self.client.run(settings.DISCORD_USERNAME, settings.DISCORD_PASSWORD)

    def adminpower(self, author):
        for role in author.roles:
            check = role.permissions.manage_server
            if check:
                return True
            else:
                continue
        return False