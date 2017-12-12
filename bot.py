import time
from functools import lru_cache
from slackclient import SlackClient
from config import BOT_ID, SLACK_BOT_TOKEN

# connect to the Slack API
SLACK_CLIENT = SlackClient(SLACK_BOT_TOKEN)

AT_BOT = f'<@{BOT_ID}>'
READ_DELAY = 1


def add_date(user_name, birth_date):
    # TODO: Add/Modify the birth date for the user, return True if successful
    pass


def calculate_age(birth_date):
    # TODO: Returns an age based on today's date and the birth date given
    pass


def check_for_upcoming_birth_dates():
    # TODO: Hourly check for any upcoming birth dates changes countdown as the date gets closer
    pass


@lru_cache(maxsize=128)
def lookup_birthday(user_name):
    # TODO: Return birthday for user_name if exists, otherwise return None
    pass


@lru_cache(maxsize=128)
def lookup_user(user_id):
    """
    Looks up the username of the given user id.

    :param user_id: String - Slack ID of the user
    :return: String - Username of the user
    """
    user_info = SLACK_CLIENT.api_call('users.info', user=user_id)
    user_name = f'@{user_info["user"]["name"]}'
    return user_name


def parse_slack_output(slack_rtm_output):
    """
    The Slack Real Time Messaging API parsing function.

    Returns None unless a message is directed at the Bot, based on its ID.

    :param slack_rtm_output: List - contents of RTM Slack Read
    :return: Tuple - (None, None, None) or (message, channel, username)
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                message = output['text'].split(AT_BOT)[1].strip().lower()
                channel = output['channel']
                username = lookup_user(output['user'])
                return message, channel, username
    return None, None, None


def pick_random_message():
    # TODO: Returns a random message from the database
    pass


def post_message(response, channel):
    """
    Takes the response given and posts it to the channel provided.

    :param response: String - response to be posted to the channel
    :param channel: String - the channel were the response is to be posted to
    :return: None
    """
    SLACK_CLIENT.api_call('chat.postMessage', channel=channel, text=response, as_user=True)


def parse_message(message):
    # TODO: Parse the message for a date and returns it otherwise return None
    pass


def process_birth_date(birth_date, channel, user_name):
    """
    Processes the given date and returns the proper response to the channel.

    :param birth_date: datetime object
    :param channel: String - the channel were the birthday was posted
    :param user_name: String - the user name of the person entering/changing their birthday
    :return: None - message is posted to the channel
    """
    if birth_date:
        current_birth_date = lookup_birthday(user_name)
        if current_birth_date:
            if current_birth_date == birth_date:
                response = f"I already have you're birth date set to {birth_date}."
            else:
                status = add_date(user_name, birth_date)
                if status:
                    response = f'Previous birthday of {current_birth_date} has been updated to {birth_date}.'
                else:
                    response = f'Sorry, I was unable to update your birthday from {current_birth_date} to {birth_date}.'
        else:
            status = add_date(user_name, birth_date)
            if status:
                response = f"Thanks, I've saved {birth_date} as your birthday!"
            else:
                response = f'Sorry, I was unable to add your birthday of {birth_date} to my list.'
    else:
        response = 'I was unable to find a valid date, please try again.'

    # post the message
    post_message(response, channel)


def run_bot():
    """
    Starts the bot.

    :return: None
    """
    if SLACK_CLIENT.rtm_connect():
        print('Bot connected and running!')
        while True:
            (message, channel, user_name) = parse_slack_output(SLACK_CLIENT.rtm_read())
            if message and channel:
                birth_date = parse_message(message)
                process_birth_date(birth_date, channel, user_name)
            time.sleep(READ_DELAY)
    else:
        print('Connection failed, invalid Slack TOKEN or bot ID?')


if __name__ == '__main__':
    run_bot()
