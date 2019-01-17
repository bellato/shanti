import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, UniqueConstraint, REAL, ForeignKey
from sqlalchemy.orm import sessionmaker


CBase = declarative_base()


class CLots(CBase):

    __tablename__ = "all_lots"
    # 'create table if not exists all_lots(id_lot integer primary key unique, vk_link text, '
    #                        'title text, money text, flag integer)'
    id_lot = Column(Integer(), primary_key=True)
    vk_link = Column(String())
    title = Column(String())
    money = Column(String())
    flag = Column(Integer())

    check_1 = UniqueConstraint("id_lot")

    def __repr__(self):
        return  # todo написать как будет выглядеть принт


class CHistory(CBase):

    __tablename__ = "history"
    # 'create table if not exists history (id_lot_table integer references all_lots (id_lot), '
    #                         'name text, money2 text, datetime real)'
    id_lot_table = Column(Integer(), ForeignKey("all_lots.id_lot"))
    name = Column(String())
    money2 = Column(String())
    datetime = Column(REAL())

    def __repr__(self):
        return  # todo написать как будет выглядеть принт


engine = create_engine('sqlite:///db_shanti.db', echo=False)
session = sessionmaker(bind=engine)()
