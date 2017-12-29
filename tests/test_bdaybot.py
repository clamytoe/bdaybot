import arrow
import datetime

from dateutil.parser import parse
from dateutil.zoneinfo import tzfile
from bdaybot import *

BD = parse('12/06/1972')
ABD = arrow.get(BD)
TZ = 'US/Central'
ABDTZ = ABD.to(TZ)

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
    assert str(date.datetime) == '2018-12-05 18:00:00-06:00'

