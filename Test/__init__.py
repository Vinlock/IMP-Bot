

class Tester(object):
    def __init__(self, message, client):
        client.send_message(message.channel, "reply")