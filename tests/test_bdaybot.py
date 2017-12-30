import datetime

import arrow
import pytest

from bdaybot import calculate_today, parse, calculate_next_birth_date, calculate_age, parse_message,\
    adjust_date_with_timezone, days_left_to_birthday, lookup_birthday, add_reminder
import bd_db as db

BD = parse('12/06/1972')
ABD = arrow.get(BD)
TZ = 'America/Chicago'
ABDTZ = ABD.to(TZ)
USER = 'test_dummy'


def test_add_reminder_ok(monkeypatch):
    def mock_db_create(username, bday, channel):
        return True
    monkeypatch.setattr(db, 'create_reminder', mock_db_create)
    status = add_reminder(USER, ABD.datetime, TZ, 'general')
    assert status is True


def test_add_reminder_fail(monkeypatch):
    def mock_db_create_fail(username, bday, channel):
        return False
    monkeypatch.setattr(db, 'create_reminder', mock_db_create_fail)
    with pytest.raises(TypeError):
        add_reminder(USER, 'not a datetime', TZ, 'general')
        add_reminder(123, ABD, TZ, 'general')
        add_reminder(None, ABD, TZ, 'general')
        add_reminder(USER, ABD, None, 'general')
        add_reminder(USER, ABD, TZ, None)
    status = add_reminder(USER, ABD, TZ, 'general')
    assert status is False

# commented the rest to start again from the beginning
#
# def test_globals():
#     assert isinstance(SLACK_CLIENT, SlackClient)
#     assert isinstance(BD, datetime.datetime)
#     assert isinstance(ABD, arrow.Arrow)
#     assert str(ABD.datetime) == '1972-12-06 00:00:00+00:00'
#     assert str(ABDTZ.datetime) == '1972-12-05 18:00:00-06:00'
#
#
# def test_calculate_today():
#     arrow_today = arrow.now(TZ)
#     today = calculate_today(TZ)
#     assert today.year == arrow_today.year
#     assert today.month == arrow_today.month
#     assert today.day == arrow_today.day
#
#
# def test_calculate_next_birth_date():
#     date = calculate_next_birth_date(ABD, TZ)
#     assert isinstance(date, arrow.Arrow)
#     assert str(date.datetime) == '2018-12-05 18:00:00-06:00'
#
#
# def test_calculate_age():
#     today_year = calculate_today(TZ).year
#     age = calculate_age(ABDTZ, TZ)
#     assert isinstance(age, int)
#     assert age == today_year - ABDTZ.year
#
#
# def test_adjust_date_with_timezone():
#     adjusted_date = adjust_date_with_timezone(ABD, TZ)
#     assert isinstance(adjusted_date, datetime.datetime)
#     assert str(adjusted_date) == '1972-12-05 15:00:00+00:00'
#
#
# def test_days_left_to_birthday():
#     days = days_left_to_birthday(ABDTZ, TZ)
#     assert isinstance(days, int)
#
#
# def test_lookup_birthday():
#     _ = db.create_birthday(USER, ABDTZ.datetime, TZ)
#     user_info = lookup_birthday(USER)
#     assert isinstance(user_info, tuple)
#     assert len(user_info) == 2
#     assert str(user_info[0]) == '1972-12-05 18:00:00'
#     assert user_info[1] == TZ
#     del_status = db.delete_birthday(USER)
#     assert del_status is True
#
#
# def test_lookup_birthday_failed():
#     user_info = lookup_birthday(USER)
#     assert isinstance(user_info, tuple)
#     assert len(user_info) == 2
#     assert user_info[0] is None
#     assert user_info[1] is None
#
#
# def test_parse_message():
#     message = '<@U8DER4W6N> birthday 12/6/72'
#     result = parse_message(message, TZ)
#     assert isinstance(result, arrow.Arrow)
#     assert result.year == 1972
#     assert result.month == 12
#     assert result.day == 6
#     failed = parse_message('<@U8DER4W6N> good morning bot!', TZ)
#     assert failed is None
#
#
# def test_parse_message_failed():
#     message = '<@U8DER4W6N> good morning bot!'
#     result = parse_message(message, TZ)
#     assert result is None
