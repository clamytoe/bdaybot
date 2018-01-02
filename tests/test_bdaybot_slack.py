# -*- coding: utf-8 -*-
import pytest
from slackclient import SlackClient

from config import BOT_ID, SLACK_BOT_TOKEN
from bdaybot import SLACK_CLIENT


@pytest.fixture
def slack_client():
    return SlackClient(SLACK_BOT_TOKEN)


def test_environment_variables():
    assert len(BOT_ID) == 9
    assert SLACK_BOT_TOKEN.startswith('xoxb') is True


def test_slack_client(slack_client):
    assert isinstance(slack_client, SlackClient)


def test_api_call(slack_client):
    api_call = slack_client.api_call("users.list")
    users_dict = api_call.get('members')
    users = [user['name'] for user in users_dict]

    assert api_call.get('ok') == True
    assert isinstance(users, list)
    assert isinstance(users[0], dict)
    assert 'bdaybot' in users
