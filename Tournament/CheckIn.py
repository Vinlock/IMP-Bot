import discord, asyncio, settings

class CheckIn(object):
    def __init__(self, member, list):
        self.member = member
        self.list = list