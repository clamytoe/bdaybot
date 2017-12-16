from random import choice
import time
from dateutil.parser import parse
from dateutil import tz
from functools import lru_cache

import arrow
from slackclient import SlackClient

import bd_db as db
from config import BOT_ID, SLACK_BOT_TOKEN

# connect to the Slack API
SLACK_CLIENT = SlackClient(SLACK_BOT_TOKEN)

AT_BOT = f'<@{BOT_ID}>'
READ_DELAY = 1


def add_date(user_name, birth_date, timezone):
    """
    Add a user to the database if it doesn't exist. Change their birthday if a new date is given.

    :param user_name: String - User name
    :param birth_date: Arrow datetime - User's birthday
    :param timezone: String - Timezone for the user
    :return: Bool - True or False
    """
    current_bday = lookup_birthday(user_name)[0]
    if current_bday:
        update_status = db.modify_birthday(user_name, birth_date.datetime, timezone)
        return update_status if update_status else False
    else:
        status = db.create_birthday(user_name, birth_date.datetime, timezone)
    return status


def days_left_to_birthday(birth_date, timezone):
    """
    Determines how many days are left until the user's next birthday.

    :param birth_date: Arrow datetime object with the user's birthday
    :param timezone: String with the timezone of the user
    :return: Integer with the number of days left until the next birthday
    """
    today = arrow.utcnow().to(timezone).floor('hour')  # discards the time
    next_birth_date = birth_date.replace(year=today.year)
    str_today = str(today).split('T')[0]
    str_next_birth_date = str(next_birth_date).split('T')[0]

    if str_next_birth_date == str_today:
        return 0
    elif next_birth_date < today:
        next_birth_date = next_birth_date.shift(years=1)

    return (next_birth_date - today).days



def calculate_age(birth_date, timezone):
    # TODO: Returns an age based on today's date and the birth date given
    pass


def check_for_upcoming_birth_dates():
    # TODO: Hourly check for any upcoming birth dates changes countdown as the date gets closer
    pass


def lookup_birthday(user_name):
    """
    Retrieves the user's birthday and timezone from the database

    :param user_name: String - User name
    :return: Tuple - (birth_date, timezone) or None
    """
    birth_date, timezone = db.retrieve_user_data(user_name)
    return birth_date, timezone if birth_date and timezone else None, None


@lru_cache(maxsize=128)
def lookup_user(user_id):
    """
    Looks up the username of the given user id.

    :param user_id: String - Slack ID of the user
    :return: String - Username of the user
    """
    user_info = SLACK_CLIENT.api_call('users.info', user=user_id)
    user_name = f'{user_info["user"]["name"]}'
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
    """
    Returns a random birthday greeting.

    :return: String - a birthday greeting
    """
    greetings = [
        'I hope your special day will bring you lots of happiness, love and fun. You deserve them a lot. Enjoy!',
        'Have a wonderful birthday. I wish your every day to be filled with lots of love, laughter, happiness and the '
        'warmth of sunshine.',
        'May your coming year surprise you with the happiness of smiles, the feeling of love and so on. I hope you '
        'will find plenty of sweet memories to cherish forever. Happy birthday.',
        'May this birthday be filled with lots of happy hours and also your life with many happy birthdays, '
        'that are yet to come. Happy birthday.',
        'Let’s light the candles and celebrate this special day of your life. Happy birthday.',
        'Special day, special person and special celebration. May all your dreams and desires come true in this '
        'coming year. Happy birthday.',
        'Let your all the dreams to be on fire and light your birthday candles with that. Have a gorgeous birthday.',
    ]
    return choice(greetings)


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


def pp_date(date):
    """
    Pretty print the Arrow datetime object.

    :param date: Arrow datetime - User's birthday
    :return: String - Human readable formatted date
    """
    if not isinstance(date, arrow.arrow.Arrow):
        date = arrow.get(date)
    return date.format('MMMM D, YYYY')


def process_birth_date(birth_date, channel, user_name, timezone):
    """
    Processes the given date and returns the proper response to the channel.

    :param birth_date: datetime object
    :param channel: String - the channel were the birthday was posted
    :param user_name: String - the user name of the person entering/changing their birthday
    :return: None - message is posted to the channel
    """
    if birth_date:
        countdown = days_left_to_birthday(birth_date, timezone)
        current_birth_date = lookup_birthday(user_name)[0]
        pp_bday = pp_date(birth_date)

        if countdown == 0:
            status = add_date(user_name, birth_date, timezone)
            greeting = pick_random_message()
            if status:
                response = f":gift: Hey!, today is your BIRTHDAY!! :cake:\n{greeting}"
            else:
                response = f"I wasn't able to save your birth date, but Happy Birthday anyways!!"
        elif current_birth_date:
            pp_current = pp_date(current_birth_date)
            if str(current_birth_date).split('T')[0] == str(birth_date).split('T')[0]:
                response = f":confused: I already have your birthday set. You still have *{countdown}* days more, " \
                           f"so please be patient! :ok_hand:"
            else:
                status = add_date(user_name, birth_date, timezone)
                if status:
                    response = f"Sure thing, I've changed your birthday from *{pp_current}* to *{pp_bday}*."
                else:
                    response = f"Sorry but I couldn't change your birthday from *{pp_current}* to *{pp_bday}*."
        else:
            status = add_date(user_name, birth_date, timezone)
            if status:
                response = f"Thanks, I've saved *{pp_bday}* as your birthday. You will " \
                           f"hear again from me in *{countdown}* days! :wink:"
            else:
                response = f"Sorry, but for some unknown reason, I wasn't able to add *{pp_bday}* as your birthday..."
    else:
        response = ":thinking_face:, was there a date in there?"

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
            if not channel:
                pass
            elif "help" in message:
                display_help()
            elif "birthday" in message:
                birth_date = parse_message(message, timezone)
                process_birth_date(birth_date, channel, user_name, timezone)
            time.sleep(READ_DELAY)
    else:
        print('Connection failed, invalid Slack TOKEN or bot ID?')


if __name__ == '__main__':
    run_bot()
