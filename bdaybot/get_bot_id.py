# -*- coding: utf-8 -*-
from slackclient import SlackClient

from bdaybot.config import SLACK_BOT_TOKEN

BOT_NAME = 'bdaybot'

slack_client = SlackClient(SLACK_BOT_TOKEN)


if __name__ == "__main__":
    api_call = slack_client.api_call("users.list")
    if api_call.get('ok'):
        # retrieve all users so we can find our bot
        users = api_call.get('members')
        for user in users:
            # print(f'USERS: {user}')
            if 'name' in user and user['name'] == BOT_NAME:
                print('Bot ID for "{0}" is {1}'.format(user["name"], user["id"]))
    else:
        print('could not find bot user with the name {}'.format(BOT_NAME))
