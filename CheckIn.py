import discord, asyncio, settings

class CheckIn(object):
    def __init__(self, member):
        self.client = discord.Client()
        self.client.run(settings.DISCORD_USERNAME, settings.DISCORD_PASSWORD)

    def addRole:
        role = find(lambda m: m.name == 'Mighty', channel.server.roles)