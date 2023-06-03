import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy import create_engine, MetaData
from sqlalchemy_utils import database_exists, create_database
from config import db_url_object



metadata = MetaData()
Base = declarative_base()
engine = create_engine(db_url_object)

class Viewed(Base):
    __tablename__ = 'viewed'
    profile_id = sq.Column(sq.Integer, primary_key=True)
    worksheet_id = sq.Column(sq.Integer, primary_key=True)


def check_and_create_database(db_url):
    if not database_exists(db_url):
        create_database(db_url)


def add_user(engine, profile_id, worksheet_id):
    with Session(engine) as session:
        to_bd = Viewed(profile_id=profile_id, worksheet_id=worksheet_id)
        session.add(to_bd)
        session.commit()


def check_user(engine, profile_id, worksheet_id):
    with Session(engine) as session:
        from_bd = session.query(Viewed).filter(
            Viewed.profile_id == profile_id,
            Viewed.worksheet_id == worksheet_id
        ).first()
        return True if from_bd else False


if __name__ == '__main__':
    pass
    # engine = create_engine(db_url_object)
    # Base.metadata.create_all(engine)
    # # add_user(engine, 2113, 124512)
    # res = check_user(engine, 2113, 1245121)
    # print(res)