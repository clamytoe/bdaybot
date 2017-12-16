from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


engine = create_engine('sqlite:///bdayb.db', echo=True)
Base = declarative_base()


########################################################################
class Birthday(Base):
    """"""
    __tablename__ = "birthdays"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    birth_date = Column(Date)
    timezone = Column(String)

    # ----------------------------------------------------------------------
    def __init__(self, username, birth_date, timezone):
        """"""
        self.username = username
        self.birth_date = birth_date
        self.timezone = timezone

    def __repr__(self):
        return "<Birthday (username={}, birth_date={}, timezone={})>".format(self.username,
                                                                             self.birth_date,
                                                                             self.timezone)


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
    except:
        session.rollback()
        raise
    finally:
        session.close()


def create_birthday(user, birth_date, timezone):
    """Creates a Birthday entry with the provided user data

    :param user: String - User name
    :param birth_date: datetime.date - The birthday of the user
    :param timezone: String - The user's timezone

    :return: bool - True if succesful, else False
    """
    new_birthday = Birthday(user, birth_date, timezone)
    with session_scope() as session:
        session.add(new_birthday)
        session.commit()
        res = session.query(Birthday).filter(Birthday.username == user).first()
        if not res:
            return False
        return True


def modify_birthday(user, birth_date, timezone):
    """Modifies a Birthday entry with new data

    :param user: String - User name
    :param birth_date: datetime.date - The new birthday of the user
    :param timezone: String - The user's timezone

    :return: bool - True if succesful, else False
    """
    with session_scope() as session:
        res = session.query(Birthday).filter(Birthday.username == user).first()
        if not res:
            return False
        res.birth_date = birth_date
        res.timezone = timezone
        session.commit()
        return True


def delete_birthday(user):
    """Deletes the Birthday entry for the provided user

    :param user: String - User name

    :return: bool - True if succesful, else False
    """
    with session_scope as session:
        res = session.query(Birthday).filter(Birthday.username == user).first()
        if not res:
            return False
        session.delete(res)
        session.commit()
        return True


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