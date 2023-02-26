import os
from datetime import datetime

from db_common import Base
from db_common import engine

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql.functions import current_timestamp
from sqlalchemy.dialects.mysql import INTEGER

import hashlib

SQLITE3_NAME = "./db.sqlite3"


class User(Base):
    """
    ユーザテーブル

    id            : 主キー
    user_id      : id
    user_name      : 名前
    user_pwd      : パスワード
    auth_type      : 権限
    reg_dtime : 登録日時
    """
    __tablename__ = 'user'

    id = Column(
        'id',
        INTEGER(unsigned=True),
        primary_key=True,
        autoincrement=True
    )
    user_id = Column('user_id', String(256))
    user_pwd = Column('user_pwd', String(256))
    user_name = Column('user_name', String(256))
    reg_dtime = Column(
        'reg_dtime',
        DateTime,
        default=datetime.now(),
        nullable=False,
        server_default=current_timestamp()
    )
    auth_type = Column(
        'auth_type',
        INTEGER(unsigned=True),
        default=0
    )

    def __init__(self, user_id, user_pwd, user_name, auth_type=0, reg_dtime=datetime.now()):
        self.user_id = user_id
        self.user_pwd = user_pwd
        self.user_name = user_name
        self.auth_type = auth_type
        self.reg_dtime = reg_dtime

    def __str__(self):
        return {
            'user_id': self.user_id,
            'user_name': self.user_name,
            'reg_dtime': self.reg_dtime,
        }


class StaffMaster(Base):
    """
    人員マスタ

    id            : 主キー
    name      : 名前
    cost      : 費用
    reg_dtime : 登録日時
    """
    __tablename__ = 'staff'

    id = Column(
        'id',
        INTEGER(unsigned=True),
        primary_key=True,
        autoincrement=True
    )
    name = Column('name', String(256))
    cost = Column('cost', INTEGER(unsigned=True))
    reg_dtime = Column(
        'reg_dtime',
        DateTime,
        default=datetime.now(),
        nullable=False,
        server_default=current_timestamp()
    )

    def __init__(self, name, cost, reg_dtime=datetime.now()):
        self.name = name
        self.cost = cost
        self.reg_dtime = reg_dtime

    def __str__(self):
        return {
            'user_id': self.user_id,
            'user_name': self.user_name,
            'reg_dtime': self.reg_dtime,
        }


if __name__ == "__main__":
    path = SQLITE3_NAME
    if not os.path.isfile(path):

        # テーブルを作成する
        Base.metadata.create_all(engine)
