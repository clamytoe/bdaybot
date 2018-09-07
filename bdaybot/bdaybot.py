from functools import lru_cache
from random import choice
from time import sleep

import arrow
from apscheduler.schedulers.background import BackgroundScheduler
from dateutil import tz
from dateutil.parser import parse
from slackclient import SlackClient

import bdaybot.bd_db as db
from bdaybot.config import BOT_ID, SLACK_BOT_TOKEN, greetings


class BdayBot:
    READ_DELAY = 1

    def __init__(self, bot_id=BOT_ID, bot_token=SLACK_BOT_TOKEN):
        self.bot_id = bot_id
        self.bot_token = bot_token
        self.slack_client = SlackClient(self.bot_token)
        self.at_bot = f"<@{self.bot_id}>"

    def add_reminder(self, user_name, birth_date, timezone, channel):
        """
        Add's a new entry into the reminders database.

        :param user_name: String - the username of the user
        :param birth_date: Arrow datetime - user's birth date
        :param timezone: String - user's local timezone
        :param channel: String - the channel were the birthday was posted
        :return: Boolean
        """
        bday = self.calculate_next_birth_date(birth_date, timezone)
        bday_utc = self.adjust_date_with_timezone(bday, timezone)
        status = db.create_reminder(user_name, bday_utc, channel)

        return status

    def calculate_next_birth_date(self, birth_date, timezone):
        # TODO: Can easily be replaced by Arrow's shift function: remove this
        # and refactor?
        """
        Calculates the next birthday from the given birthday and timezone of
        the user.

        :param birth_date: Arrow datetime object - the user's birthday
        :param timezone: String - the user's timezone
        :return: Arrow datetime object with next year's birth date
        """
        today = self.calculate_today(timezone)
        this_year = today.year

        bday = birth_date.replace(year=this_year)

        if today > bday:
            this_year += 1
            bday = birth_date.replace(year=this_year)

        return arrow.get(bday).to(timezone)

    def days_left_to_birthday(self, birth_date, timezone):
        """
        Determines how many days are left until the user's next birthday.

        :param birth_date: Arrow datetime - the user's birthday
        :param timezone: String - the timezone of the user
        :return: Integer - the number of days left until the next birthday
        """
        today = self.calculate_today(timezone)
        next_birth_date = self.calculate_next_birth_date(birth_date, timezone)
        str_today = str(today).split("T")[0]
        str_next_birth_date = str(next_birth_date).split("T")[0]

        if str_next_birth_date == str_today:
            return 0
        elif next_birth_date < today:
            next_birth_date = next_birth_date.shift(years=1)

        return (next_birth_date - today).days

    def handle_add_new_user(self, user_name, birth_date, timezone, channel):
        """
        Handles the event where the user does not exists in the database.

        :param user_name: String - the username of the user
        :param birth_date: Arrow datetime - user's birth date
        :param timezone: String - user's local timezone
        :param channel: String - the channel were the birthday was posted
        :return: String - response message to the user
        """
        pp_bday = self.pp_date(birth_date)
        status = db.create_birthday(user_name, birth_date.datetime, timezone)
        adjusted_birthday = self.adjust_date_with_timezone(
            birth_date.datetime,
            timezone,
        )
        r_status = self.add_reminder(user_name, adjusted_birthday, timezone, channel)

        if status and r_status:
            response = f"Thanks, I've saved *{pp_bday}* as your birthday. :wink:"
        else:
            response = f"Sorry, but for some unknown reason, I wasn't able to " \
                       f"add *{pp_bday}* as your birthday..."
        return response

    def handle_user_exists(
            self,
            user_name,
            birth_date,
            timezone,
            channel,
            current_birth_date,
    ):
        """
        Handles the event where the user already exists in the database.

        :param user_name: String - the username of the user
        :param birth_date: Arrow datetime - user's birth date
        :param timezone: String - user's local timezone
        :param channel: String - the channel were the birthday was posted
        :param current_birth_date: Datetime - the birth date that is currently in
               the database
        :return: String - response message to the user
        """
        countdown = self.days_left_to_birthday(birth_date, timezone)
        pp_bday = self.pp_date(birth_date)
        pp_current = self.pp_date(current_birth_date)

        if str(current_birth_date).split("T")[0] == str(birth_date).split("T")[0]:
            response = f":confused: I already have your birthday set. You still " \
                       f"have *{countdown}* days more, so please be patient! " \
                       f":ok_hand: "
        else:
            status = db.modify_birthday(user_name, birth_date.datetime, timezone)
            adjusted_birthday = self.adjust_date_with_timezone(
                birth_date.datetime,
                timezone,
            )
            r_status = self.update_reminders(
                user_name,
                adjusted_birthday,
                timezone,
                channel,
            )
            if status and r_status:
                response = f"Sure thing, I've changed your birthday from " \
                           f"*{pp_current}* to *{pp_bday}*. "
            else:
                response = f"Sorry but I couldn't change your birthday from " \
                           f"*{pp_current}* to *{pp_bday}*."
        return response

    def parse_slack_output(self, slack_rtm_output):
        """
        The Slack Real Time Messaging API parsing function.

        Returns None unless a message is directed at the Bot, based on its ID.

        :param slack_rtm_output: List - contents of RTM Slack Read
        :return: Tuple - (None, None, None, None) or (message, channel, username,
                 timezone)
        """
        output_list = slack_rtm_output
        if output_list and len(output_list) > 0:
            for output in output_list:
                if output and "text" in output and self.at_bot in output["text"]:
                    message = output["text"].split(self.at_bot)[1].strip().lower()
                    channel = output["channel"]
                    username, timezone = self.lookup_user(output["user"])
                    return message, channel, username, timezone
        return None, None, None, None

    def post_message(self, response, channel):
        """
        Takes the response given and posts it to the channel provided.

        :param response: String - response to be posted to the channel
        :param channel: String - the channel were the response is to be posted to
        :return: None
        """
        self.slack_client.api_call(
            "chat.postMessage", channel=channel, text=response, as_user=True,
            link_names=1
        )

    def process_birth_date(self, birth_date, user_name, timezone, channel,
                           current_birth_date):
        """
        Processes the given date and returns the proper response to the channel.

        :param birth_date: datetime object
        :param user_name: String - the user name of the person entering/changing
               their birthday
        :param timezone: String - the user's timezone
        :param channel: String - the channel were the birthday was posted
        :param current_birth_date: Arrow datetime object - existing birthday in
               the database
        :return: String - message to be posted to the channel
        """
        if birth_date:
            if current_birth_date:
                response = self.handle_user_exists(
                    user_name, birth_date, timezone, channel, current_birth_date
                )
            else:
                response = self.handle_add_new_user(user_name, birth_date, timezone, channel)
        else:
            response = ":thinking_face:, was there a date in there?"

        return response

    def reminders_check(self):
        """
        Retrieves all reminders and compares their date with the current one.
        If a birthday is found, it sends a birthday greeting, deletes the reminder
        and schedules the one for the next year.

        :return: None
        """
        reminders = db.get_all_reminder_ids()
        if not reminders:
            return
        for r_id in reminders:
            r_user, r_date, r_channel = db.retrieve_reminder_data(r_id)
            if not r_user:
                continue
            r_date_local = arrow.get(r_date).to("local")
            now = arrow.now().datetime
            if r_date_local.strftime("%m/%d/%y %H") == now.strftime("%m/%d/%y %H"):
                # generate greeting and post it
                greeting = self.bday_message
                self.post_message("<@{0}>, {1}".format(r_user, greeting), r_channel)
                # then we delete the expired reminder
                db.delete_reminder(r_id)
                # after that, we set up next year's reminder
                db.create_reminder(r_user, r_date.replace(year=r_date.year + 1), r_channel)

    def update_reminders(self, user_name, birth_date, timezone, channel):
        """
        Updates the reminders database.

        :param user_name: String - the user name of the person entering/changing
               their birthday
        :param birth_date: datetime object
        :param timezone: String - the user's timezone
        :param channel: String - the channel were the birthday was posted
        :return: Boolean
        """
        existing_reminders = db.retrieve_user_reminders(user_name)

        if existing_reminders:
            for r in existing_reminders:
                db.delete_reminder(r[0])

        next_birth_date = self.calculate_next_birth_date(birth_date, timezone)
        next_birth_date_utc = self.adjust_date_with_timezone(next_birth_date, timezone)
        r_status = db.create_reminder(user_name, next_birth_date_utc, channel)
        return r_status

    def run_bot(self):
        """
        Starts the bot.

        :return: None
        """
        if self.slack_client.rtm_connect():
            print("Bot connected and running!")

            reminders_scheduler = BackgroundScheduler()
            reminders_scheduler.add_job(self.reminders_check, "cron", hour="*", minute=0)
            reminders_scheduler.start()

            while True:
                (message, channel, user_name, timezone) = self.parse_slack_output(
                    self.slack_client.rtm_read()
                )
                if message and channel:
                    birth_date = self.parse_message(message, timezone)
                    current_birth_date = self.lookup_birthday(user_name)[0]
                    if "help" in message.lower():
                        self.post_message(self.display_help(), channel)
                    elif "birthday" in message and birth_date:
                        self.post_message(
                            self.process_birth_date(
                                birth_date, user_name, timezone, channel,
                                current_birth_date
                            ),
                            channel,
                        )
                    elif "birthday" in message and current_birth_date:
                        current = arrow.get(current_birth_date)
                        countdown = self.days_left_to_birthday(current, timezone)
                        days = "day" if countdown <= 1 else "days"
                        response = f"You have *{countdown}* {days} left for " \
                                   f"your next birthday!"
                        self.post_message(response, channel)
                sleep(self.READ_DELAY)
        else:
            print("Connection failed, invalid Slack TOKEN or bot ID?")

    @property
    def bday_message(self):
        """
        Returns a random birthday greeting.

        :return: String - a birthday greeting
        """
        return choice(greetings)

    @staticmethod
    def adjust_date_with_timezone(date, timezone):
        """
        Returns the provided date + timezone adjusted to the local timezone of this
        script, set to 9am.

        :param date: Datetime / Basic datetime object - user's birthdate
        :param timezone: String - user's local timezone
        :return: Datetime - the adjusted datetime object in UTC tz
        """
        date = arrow.get(date)
        date_with_user_timezone = date.to(timezone).replace(
            hour=9,
            minute=0,
            second=0)
        adjusted_date = date_with_user_timezone.to("local")
        return adjusted_date.to("utc").datetime

    @staticmethod
    def calculate_today(timezone):
        """
        Calculates today's date, adjusts it's timezone and converts it into an
        arrow datetime object.

        :param timezone: String - the timezone of the user.
        :return: Arrow datetime object
        """
        return arrow.utcnow().to(timezone).floor("hour")  # discards the time

    @staticmethod
    def display_help():
        """
        Displays a help message with the list of admitted commands

        :return: String - help message
        """
        response = """
        Tag me and say:
        *help* - display this message.
        *birthday* - followed by your birth date for me to save it.
        *birthday* - without a date, to find out how many more days are left for your next birthday.
        """
        return response

    @staticmethod
    def lookup_birthday(user_name):
        """
        Retrieves the user's birthday and timezone from the database

        :param user_name: String - User name
        :return: Tuple - (birth_date, timezone) or (None, None)
        """
        birth_date, timezone = db.retrieve_user_data(user_name)

        if birth_date and timezone:
            return birth_date, timezone
        else:
            return None, None

    @lru_cache(maxsize=128)
    def lookup_user(self, user_id):
        """
        Looks up the username of the given user id.

        :param user_id: String - Slack ID of the user
        :return: String - Username of the user
        """
        user_info = self.slack_client.api_call("users.info", user=user_id)
        user_name = "{}".format(user_info["user"]["name"])
        user_tz = "{}".format(user_info["user"]["tz"])
        return user_name, user_tz

    @staticmethod
    def parse_message(message, timezone):
        """
        Attempts to parse a date from the message.

        :param message: String - the message from the user
        :param timezone: String - the user's timezone
        :return: Arrow datetime object - the birth date parsed or None
        """
        try:
            b_day = parse(message, fuzzy=True)
            birthday = arrow.get(b_day, tz.gettz(timezone))
            return None if birthday.year < 1900 else birthday
        except (ValueError, TypeError):
            return None

    @staticmethod
    def pp_date(date):
        """
        Pretty print the Arrow datetime object.

        :param date: Arrow datetime - User's birthday
        :return: String - Human readable formatted date
        """
        if not isinstance(date, arrow.arrow.Arrow):
            date = arrow.get(date)
        return date.format("MMMM D, YYYY")


def run():
    bot = BdayBot()
    try:
        bot.run_bot()
    except KeyboardInterrupt:
        print("\nBot terminated by user!")
        exit(0)


if __name__ == "__main__":
    run()
