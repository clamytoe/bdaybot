# -*- coding: utf-8 -*-
import pytest
from slackclient import SlackClient

from bdaybot.bdaybot import SLACK_CLIENT, lookup_user
from bdaybot.config import BOT_ID, SLACK_BOT_TOKEN
from tests.slack_api_calls import api_users_info_dseptem, api_users_list


@pytest.fixture
def slack_client():
    return SLACK_CLIENT


def test_environment_variables():
    assert len(BOT_ID) == 9
    assert SLACK_BOT_TOKEN.startswith('xoxb') is True


def test_slack_client(slack_client):
    assert isinstance(slack_client, SlackClient)


def test_api_call(slack_client, monkeypatch):
    def mock_api_call(api_type, user=None):
        if api_type == 'users.list':
            return api_users_list
        elif api_type == 'users.info':
            return api_users_info_dseptem
        else:
            return None
    monkeypatch.setattr(slack_client, 'api_call', mock_api_call)
    users_list = slack_client.api_call('users.list')
    members = users_list.get('members')
    users = [user['name'] for user in members]
    user, timezone = lookup_user('U865MULPQ')

    assert users_list.get('ok') is True
    assert isinstance(members, list)
    assert isinstance(members[0], dict)
    assert 'bdaybot' in users
    assert user == 'dseptem'
    assert timezone == 'America/Los_Angeles'
