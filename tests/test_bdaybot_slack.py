from bdaybot import SLACK_CLIENT, SlackClient


def test_globals():
    assert isinstance(SLACK_CLIENT, SlackClient)
