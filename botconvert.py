import requests
import json
import time
import settings

OWNER_EMAIL = settings.DISCORD_OWNER_USERNAME
OWNER_PASSWORD = settings.DISCORD_OWNER_PASSWORD

BOT_EMAIL = settings.DISCORD_USERNAME
BOT_PASSWORD = settings.DISCORD_PASSWORD

API_URL      = 'https://discordapp.com/api/'
USERS        = API_URL + 'users/@me'
APPLICATIONS = API_URL + 'oauth2/applications'
LOGIN        = API_URL + 'auth/login'

def get_token(email, password):
    payload = {
        'email': email,
        'password': password
    }

    headers = {
        'content-type': 'application/json'
    }

    r = requests.post(LOGIN, data=json.dumps(payload), headers=headers)
    if r.status_code != 200:
        raise RuntimeError('Improper credentials')

    js = r.json()
    return js['token']

def get_bot_name(token):
    headers = {
        'authorization': token
    }

    r = requests.get(USERS, headers=headers)
    if r.status_code != 200:
        raise RuntimeError('Could not fetch user info')
    return r.json()['username']

def create_application(bot, owner, app_name):
    headers = {
        'content-type': 'application/json',
        'authorization': owner
    }

    payload = {
        'name': app_name
    }

    print('Creating application')
    r = requests.post(APPLICATIONS, headers=headers, data=json.dumps(payload))
    if r.status_code >= 400:
        raise RuntimeError('Could not create application.')

    data = r.json()
    print('Application created.')
    print('Client ID: {0[id]}\nSecret: {0[secret]}'.format(data))
    return data['id']

def convert_bot(bot, owner, client_id):
    url = '{}/{}/bot'.format(APPLICATIONS, client_id)
    headers = {
        'authorization': owner,
        'content-type': 'application/json'
    }

    payload = {
        'token': bot
    }

    print('Converting to a bot account')
    r = requests.post(url, headers=headers, data=json.dumps(payload))
    if r.status_code >= 400:
        raise RuntimeError('Could not convert to a bot account.')

    data = r.json()
    print('Bot conversion complete.')
    print(data)

if __name__ == '__main__':
    try:
        bot = get_token(BOT_EMAIL, BOT_PASSWORD)

        # lol rate limits
        time.sleep(1)

        owner = get_token(OWNER_EMAIL, OWNER_PASSWORD)
        app_name = get_bot_name(bot)
        client_id = create_application(bot, owner, app_name)
        convert_bot(bot, owner, client_id)
    except Exception as e:
        print('An error has occurred: ' + str(e))