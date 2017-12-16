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

Session = sessionmaker(bind=engine)
session = Session()


def create_birthday(user, birth_date, timezone):
    new_birthday = Birthday(user, birth_date, timezone)
    session.add(new_birthday)
    session.commit()
    res = session.query(Birthday).filter(Birthday.username == user).first()
    if not res:
        return False
    return True


def modify_birthday(user, birth_date, timezone):
    res = session.query(Birthday).filter(Birthday.username == user).first()
    if not res:
        return False
    res.birth_date = birth_date
    res.timezone = timezone
    session.commit()
    return True


def delete_birthday(user):
    res = session.query(Birthday).filter(Birthday.username == user).first()
    if not res:
        return False
    session.delete(res)
    session.commit()
    return True


def retrieve_user_data(user):
    res = session.query(Birthday).filter(Birthday.username == user).first()
    if not res:
        return False
    return res.birth_date, res.timezone
