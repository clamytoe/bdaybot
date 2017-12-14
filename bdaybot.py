import time
import arrow
from dateutil.parser import parse
from dateutil import tz
from functools import lru_cache
from slackclient import SlackClient
from config import BOT_ID, SLACK_BOT_TOKEN

# connect to the Slack API
SLACK_CLIENT = SlackClient(SLACK_BOT_TOKEN)

AT_BOT = f'<@{BOT_ID}>'
READ_DELAY = 1


def add_date(user_name, birth_date, timezone):
    # TODO: Add/Modify the birth date for the user, return True if successful
    return True


def days_left_to_birthday(birth_date, timezone):
    """
    Determines how many days are left until the user's next birthday.

    :param birth_date: Arrow datetime object with the user's birthday
    :param timezone: String with the timezone of the user
    :return: Integer with the number of days left until the next birthday
    """
    today = arrow.utcnow().floor('hour').to(timezone)  # discards the time
    next_birth_date = birth_date.replace(year=today.year)

    if next_birth_date < today:
        next_birth_date = next_birth_date.shift(years=1)

    return (next_birth_date - today).days



def calculate_age(birth_date, timezone):
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
    user_tz = f'{user_info["user"]["tz"]}'
    return user_name, user_tz


def parse_slack_output(slack_rtm_output):
    """
    The Slack Real Time Messaging API parsing function.

    Returns None unless a message is directed at the Bot, based on its ID.

    :param slack_rtm_output: List - contents of RTM Slack Read
    :return: Tuple - (None, None, None, None) or (message, channel, username, timezone)
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                message = output['text'].split(AT_BOT)[1].strip().lower()
                channel = output['channel']
                username, timezone = lookup_user(output['user'])
                return message, channel, username, timezone
    return None, None, None, None


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


def parse_message(message, timezone):
    """
    Attempts to parse a date from the message.

    :param message: String containing the message from the user
    :return: datetime.datetime object containing the date or None
    """
    try:
        b_day = parse(message, fuzzy=True)
        birthday = arrow.get(b_day, tz.gettz(timezone))
        return birthday
    except ValueError:
        return None


def process_birth_date(birth_date, channel, user_name, timezone):
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
                status = add_date(user_name, birth_date, timezone)
                if status:
                    response = f'Previous birthday of {current_birth_date} has been updated to {birth_date}.'
                else:
                    response = f'Sorry, I was unable to update your birthday from {current_birth_date} to {birth_date}.'
        else:
            status = add_date(user_name, birth_date, timezone)
            if status:
                countdown = days_left_to_birthday(birth_date, timezone)
                response = f"Thanks, I've saved {birth_date.format('MMMM D, YYYY')} as your birthday. You will " \
                           f"hear again from me in {countdown} days! :wink:"
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
            (message, channel, user_name, timezone) = parse_slack_output(SLACK_CLIENT.rtm_read())
            if message and channel:
                birth_date = parse_message(message, timezone)
                process_birth_date(birth_date, channel, user_name, timezone)
            time.sleep(READ_DELAY)
    else:
        print('Connection failed, invalid Slack TOKEN or bot ID?')


if __name__ == '__main__':
    run_bot()
