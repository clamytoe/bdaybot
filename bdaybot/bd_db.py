from contextlib import contextmanager

from sqlalchemy import (Column, DateTime, ForeignKey, Integer, String, create_engine)
from sqlalchemy import exc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

engine = create_engine('sqlite:///bdayb.db', echo=True)
Base = declarative_base()


########################################################################
class Birthday(Base):
    """"""
    __tablename__ = "birthdays"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    birth_date = Column(DateTime)
    timezone = Column(String)
    reminders = relationship("Reminder")

    # ----------------------------------------------------------------------
    def __init__(self, username, birth_date, timezone):
        """"""
        self.username = username
        self.birth_date = birth_date
        self.timezone = timezone

    def __repr__(self):
        return "<Birthday (username={0}, birth_date={1}, timezone={2})>".format(self.username,
                                                                                self.birth_date,
                                                                                self.timezone)


class Reminder(Base):
    """"""
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True)
    username = Column(String, ForeignKey('birthdays.username'))
    birthday = Column(DateTime)
    channel = Column(String)

    # ----------------------------------------------------------------------
    def __init__(self, username, birthday, channel):
        """"""
        self.username = username
        self.birthday = birthday
        self.channel = channel

    def __repr__(self):
        return "<Reminder (username={0}, birthday={1}, channel={2})>".format(self.username, self.birthday, self.channel)


# create tables
Base.metadata.create_all(engine)


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    sm = sessionmaker(bind=engine)
    session = sm()
    try:
        yield session
        session.commit()
    except exc.SQLAlchemyError:
        session.rollback()
        raise
    finally:
        session.close()


def create_birthday(user, birth_date, timezone):
    """Creates a Birthday entry with the provided user data

    :param user: String - User name
    :param birth_date: datetime.date - The birthday of the user
    :param timezone: String - The user's timezone

    :return: bool - True if successful, else False
    """
    new_birthday = Birthday(user, birth_date, timezone)
    try:
        with session_scope() as session:
            session.add(new_birthday)
        return True
    except exc.SQLAlchemyError:
        return False


def modify_birthday(user, birth_date, timezone):
    """Modifies a Birthday entry with new data

    :param user: String - User name
    :param birth_date: datetime.date - The new birthday of the user
    :param timezone: String - The user's timezone

    :return: bool - True if successful, else False
    """
    try:
        with session_scope() as session:
            res = session.query(Birthday).filter(Birthday.username == user).first()
            if not res:
                return False
            res.birth_date = birth_date
            res.timezone = timezone
        return True
    except exc.SQLAlchemyError:
        return False


def delete_birthday(user):
    """Deletes the Birthday entry for the provided user

    :param user: String - User name

    :return: bool - True if successful, else False
    """
    try:
        with session_scope() as session:
            res = session.query(Birthday).filter(Birthday.username == user).first()
            if not res:
                return False
            session.delete(res)
        return True
    except exc.SQLAlchemyError:
        return False


def retrieve_user_data(user):
    """Retrieves data for the provided user

    :param user: String - User name

    :return: Tuple - (birth_date as datetime.date, timezone as string) or (None, None) if user is not in the database
    """
    with session_scope() as session:
        res = session.query(Birthday).filter(Birthday.username == user).first()
        if not res:
            return None, None
        return res.birth_date, res.timezone


def retrieve_user_reminders(user):
    """Retrieves reminders for the provided user

    :param user: String - User name

    :return: List(Tuple) - (reminder id, datetime.datetime, channel ID) or None if no reminders in the db
    """
    with session_scope() as session:
        res = session.query(Reminder).filter(Reminder.username == user).all()
        if not res:
            return None
        return [(reminder.id, reminder.birthday, reminder.channel) for reminder in res]


def create_reminder(user, birthday, channel):
    """Creates a reminder entry for a user

    :param user: String - User name
    :param birthday: datetime.datetime - The birthday of the user, timezone-adjusted for the bot
    :param channel: String - channel message was posted from

    :return: bool - True if successful, else False
    """
    new_reminder = Reminder(user, birthday, channel)
    try:
        with session_scope() as session:
            session.add(new_reminder)
        return True
    except TypeError:
        return False


def delete_reminder(r_id):
    """Deletes the reminder entry with the specified id

    :param r_id: Integer - The reminder id

    :return: bool - True if successful, else False
    """
    try:
        with session_scope() as session:
            res = session.query(Reminder).filter(Reminder.id == r_id).first()
            if not res:
                return False
            session.delete(res)
        return True
    except exc.SQLAlchemyError:
        return False


def get_all_reminder_ids():
    """Retrieves all existing reminders

    :return: List(Integer) - The list with all the reminder's ids.
    """
    with session_scope() as session:
        res = session.query(Reminder).all()
        if not res:
            return None
        return [reminder.id for reminder in res]


def retrieve_reminder_data(r_id):
    """Retrieves the data of the reminder with the provided id

    :return: Tuple(String, DateTime, String) - A tuple with the username, date of the birthday reminder and channel
    where the bot will announce the birthday.
    """
    with session_scope() as session:
        res = session.query(Reminder).filter(Reminder.id == r_id).first()
        if not res:
            return None
        return res.username, res.birthday, res.channel
