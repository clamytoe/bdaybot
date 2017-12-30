import arrow
import datetime

from dateutil.parser import parse
from dateutil.zoneinfo import tzfile
from bdaybot import *

BD = parse('12/06/1972')
ABD = arrow.get(BD)
TZ = 'America/Chicago'
ABDTZ = ABD.to(TZ)
USER = 'test_dummy'


def test_globals():
    assert isinstance(SLACK_CLIENT, SlackClient)
    assert isinstance(BD, datetime.datetime)
    assert isinstance(ABD, arrow.Arrow)
    assert str(ABD.datetime) == '1972-12-06 00:00:00+00:00'
    assert str(ABDTZ.datetime) == '1972-12-05 18:00:00-06:00'


def test_calculate_today():
    arrow_today = arrow.now(TZ)
    today = calculate_today(TZ)
    assert today.year == arrow_today.year
    assert today.month == arrow_today.month
    assert today.day == arrow_today.day


def test_calculate_next_birth_date():
    date = calculate_next_birth_date(ABD, TZ)
    assert isinstance(date, arrow.Arrow)
    assert str(date.datetime) == '2018-12-05 18:00:00-06:00'


def test_calculate_age():
    today_year = calculate_today(TZ).year
    age = calculate_age(ABDTZ, TZ)
    assert isinstance(age, int)
    assert age == today_year - ABDTZ.year


def test_adjust_date_with_timezone():
    adjusted_date = adjust_date_with_timezone(ABD, TZ)
    assert isinstance(adjusted_date, datetime.datetime)
    assert str(adjusted_date) == '1972-12-05 15:00:00+00:00'

def test_days_left_to_birthday():
    days = days_left_to_birthday(ABDTZ, TZ)
    assert isinstance(days, int)


def test_lookup_birthday():
    status = db.create_birthday(USER, ABDTZ.datetime, TZ)
    if status:
        user_info = lookup_birthday(USER)
        assert len(user_info) == 2
        assert user_info[0] == USER
        assert user_info[1] == TZ
        db.delete_birthday(USER)
    else:
        pass
