import datetime

import arrow
import pytest

from bdaybot import calculate_today, parse, calculate_next_birth_date, calculate_age, parse_message,\
    adjust_date_with_timezone, days_left_to_birthday

BD = parse('12/06/1972')
ABD = arrow.get(BD)
TZ = 'America/Chicago'
ABDTZ = ABD.to(TZ)


def test_adjust_date_with_timezone_ok():
    adj_date = adjust_date_with_timezone(datetime.datetime(day=6, month=1, year=1987), 'America/Argentina/Buenos_Aires')
    assert adj_date == datetime.datetime(1987, 1, 5, 12, 0, tzinfo=datetime.timezone.utc)
    adj_date = adjust_date_with_timezone(datetime.datetime(day=25, month=4, year=1994), 'Africa/Nouakchott')
    assert adj_date == datetime.datetime(1994, 4, 25, 9, 0, tzinfo=datetime.timezone.utc)
    adj_date = adjust_date_with_timezone(datetime.datetime(day=11, month=7, year=1973), 'America/Los_Angeles')
    assert adj_date == datetime.datetime(1973, 7, 10, 16, 0, tzinfo=datetime.timezone.utc)


def test_adjust_date_with_timezone_fail():
    with pytest.raises(arrow.parser.ParserError):
        adjust_date_with_timezone(datetime.datetime(day=6, month=1, year=1987), 'Blah')
    with pytest.raises(arrow.parser.ParserError):
        adjust_date_with_timezone('6th january 1987', 'America/Argentina/Buenos_Aires')
    with pytest.raises(TypeError):
        adjust_date_with_timezone(None, None)


def test_globals():
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


def test_parse_message():
    message = '<@U8DER4W6N> birthday 12/6/72'
    result = parse_message(message, TZ)
    assert isinstance(result, arrow.Arrow)
    assert result.year == 1972
    assert result.month == 12
    assert result.day == 6
    failed = parse_message('<@U8DER4W6N> good morning bot!', TZ)
    assert failed is None


def test_parse_message_failed():
    message = '<@U8DER4W6N> good morning bot!'
    result = parse_message(message, TZ)
    assert result is None
