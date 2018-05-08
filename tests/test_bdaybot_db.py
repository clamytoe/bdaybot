import arrow
import pytest
from dateutil.parser import parse

import bdaybot.bd_db as db
from bdaybot.bdaybot import add_reminder

BD = parse("12/06/1972")
ABD = arrow.get(BD)
TZ = "America/Chicago"
ABDTZ = ABD.to(TZ)
USER = "test_dummy"


def test_add_reminder_ok(monkeypatch):

    def mock_db_create(username, bday, channel):
        return True

    monkeypatch.setattr(db, "create_reminder", mock_db_create)
    status = add_reminder(USER, ABD.datetime, TZ, "general")
    assert status is True


def test_add_reminder_fail(monkeypatch):

    def mock_db_create_fail(username, bday, channel):
        return False

    monkeypatch.setattr(db, "create_reminder", mock_db_create_fail)
    with pytest.raises(TypeError):
        add_reminder(USER, "not a datetime", TZ, "general")
    with pytest.raises(TypeError):
        add_reminder(USER, ABD, None, "general")
    status = add_reminder(USER, ABD, TZ, "general")
    assert status is False


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
