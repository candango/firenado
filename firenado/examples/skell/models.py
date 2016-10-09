from firenado.util.sqlalchemy_util import Base

from sqlalchemy import Column, String
from sqlalchemy.types import Integer, DateTime
from sqlalchemy.sql import text


class UserBase(Base):

    __tablename__ = 'users'
    mysql_engine = 'MyISAM'
    mysql_charset = 'utf8'

    id = Column('id', Integer, primary_key=True)
    username = Column('username', String(150), nullable=False)
    first_name = Column('first_name', String(150), nullable=False)
    last_name = Column('last_name', String(150), nullable=False)
    password = Column('password', String(150), nullable=False)
    email = Column('email', String(150), nullable=False)
    created = Column('created', DateTime, nullable=False,
                     server_default=text('now()'))
    modified = Column('modified', DateTime, nullable=False,
                     server_default=text('now()'))
