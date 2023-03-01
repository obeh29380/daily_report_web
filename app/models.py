import os
from datetime import datetime

from db_common import Base
from db_common import engine

from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql.functions import current_timestamp
from sqlalchemy.dialects.mysql import INTEGER

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

    def __init__(self, name, cost=0, reg_dtime=datetime.now()):
        self.name = name
        self.cost = cost
        self.reg_dtime = reg_dtime

    def __str__(self):
        return {
            'name': self.name,
            'cost': self.cost,
            'reg_dtime': self.reg_dtime,
        }


class CarMaster(Base):
    """
    車両マスタ

    id        : 主キー
    name      : 名前
    cost      : 費用
    reg_dtime : 登録日時
    """
    __tablename__ = 'car'

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

    def __init__(self, name, cost=0, reg_dtime=datetime.now()):
        self.name = name
        self.cost = cost
        self.reg_dtime = reg_dtime

    def __str__(self):
        return {
            'name': self.name,
            'cost': self.cost,
            'reg_dtime': self.reg_dtime,
        }


class LeaseMaster(Base):
    """
    リースマスタ

    id        : 主キー
    name      : 名前
    cost      : 費用
    reg_dtime : 登録日時
    """
    __tablename__ = 'lease'

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

    def __init__(self, name, cost=0, reg_dtime=datetime.now()):
        self.name = name
        self.cost = cost
        self.reg_dtime = reg_dtime

    def __str__(self):
        return {
            'name': self.name,
            'cost': self.cost,
            'reg_dtime': self.reg_dtime,
        }


class MachineMaster(Base):
    """
    重機マスタ

    id        : 主キー
    name      : 名前
    cost      : 費用
    reg_dtime : 登録日時
    """
    __tablename__ = 'machine'

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

    def __init__(self, name, cost=0, reg_dtime=datetime.now()):
        self.name = name
        self.cost = cost
        self.reg_dtime = reg_dtime

    def __str__(self):
        return {
            'name': self.name,
            'cost': self.cost,
            'reg_dtime': self.reg_dtime,
        }


class ItemMaster(Base):
    """
    品名マスタ

    id        : 主キー
    name      : 名前
    cost      : 費用(廃材処分先に関係なく費用が決まるもの)
    reg_dtime : 登録日時
    """
    __tablename__ = 'item'

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

    def __init__(self, name, cost=0, reg_dtime=datetime.now()):
        self.name = name
        self.cost = cost
        self.reg_dtime = reg_dtime

    def __str__(self):
        return {
            'name': self.name,
            'cost': self.cost,
            'reg_dtime': self.reg_dtime,
        }


class CustomerMaster(Base):
    """
    受注先マスタ

    id        : 主キー
    name      : 名前
    reg_dtime : 登録日時
    """
    __tablename__ = 'customer'

    id = Column(
        'id',
        INTEGER(unsigned=True),
        primary_key=True,
        autoincrement=True
    )
    name = Column('name', String(256))
    reg_dtime = Column(
        'reg_dtime',
        DateTime,
        default=datetime.now(),
        nullable=False,
        server_default=current_timestamp()
    )

    def __init__(self, name, reg_dtime=datetime.now()):
        self.name = name
        self.reg_dtime = reg_dtime

    def __str__(self):
        return {
            'name': self.name,
            'reg_dtime': self.reg_dtime,
        }


class DestMaster(Base):
    """
    廃材処分先マスタ

    id        : 主キー
    name      : 名前
    reg_dtime : 登録日時
    """
    __tablename__ = 'dest'

    id = Column(
        'id',
        INTEGER(unsigned=True),
        primary_key=True,
        autoincrement=True
    )
    name = Column('name', String(256))
    reg_dtime = Column(
        'reg_dtime',
        DateTime,
        default=datetime.now(),
        nullable=False,
        server_default=current_timestamp()
    )

    def __init__(self, name, reg_dtime=datetime.now()):
        self.name = name
        self.reg_dtime = reg_dtime

    def __str__(self):
        return {
            'name': self.name,
            'reg_dtime': self.reg_dtime,
        }


class TrashMaster(Base):
    """
    廃材処分費マスタ

    id        : 主キー
    dest_id     : 処分先ID
    name_id     : 品名ID
    cost      : 費用
    unit_type   : 単位(Kg,t)
    reg_dtime : 登録日時
    """
    __tablename__ = 'trash'

    id = Column(
        'id',
        INTEGER(unsigned=True),
        primary_key=True,
        autoincrement=True
    )
    dest_id = Column('dest_id', INTEGER(unsigned=True))
    name_id = Column('name_id', INTEGER(unsigned=True))
    cost = Column('cost', INTEGER(unsigned=True))
    unit_type = Column('unit_type', INTEGER(unsigned=True))
    reg_dtime = Column(
        'reg_dtime',
        DateTime,
        default=datetime.now(),
        nullable=False,
        server_default=current_timestamp()
    )

    def __init__(self, dest_id, name_id, cost=0, unit_type=0, reg_dtime=datetime.now()):
        self.dest_id = dest_id
        self.name_id = name_id
        self.cost = cost
        self.unit_type = unit_type
        self.reg_dtime = reg_dtime

    def __str__(self):
        return {
            'dest_id': self.dest_id,
            'name_id': self.name_id,
            'cost': self.cost,
            'unit_type': self.unit_type,
            'reg_dtime': self.reg_dtime,
        }


if __name__ == "__main__":
    path = SQLITE3_NAME
    if not os.path.isfile(path):

        # テーブルを作成する
        Base.metadata.create_all(engine)
