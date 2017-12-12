# -*- coding: utf-8 -*-
from config import SLACK_BOT_TOKEN
from slackclient import SlackClient

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
                print(f'Bot ID for "{user["name"]}" is {user["id"]}')
    else:
        print(f'could not find bot user with the name {BOT_NAME}')
