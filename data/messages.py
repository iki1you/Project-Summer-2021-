import sqlalchemy
import datetime

from .db_session import SqlAlchemyBase


class Messages(SqlAlchemyBase):
    __tablename__ = 'messages'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_one = sqlalchemy.Column(sqlalchemy.Integer)
    user_two = sqlalchemy.Column(sqlalchemy.Integer)
    send_time = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    message = sqlalchemy.Column(sqlalchemy.String)