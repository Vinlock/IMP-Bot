import discord, asyncio, settings
from BotLogging import log as logger

class CheckIn(object):
    def __init__(self, member, list):
        self.member = member
        self.list = list