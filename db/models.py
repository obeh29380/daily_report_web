import os
import pytz
from datetime import datetime
from db_common import engine
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql.functions import current_timestamp
from sqlalchemy.dialects.mysql import INTEGER

SQLITE3_NAME = "./db.sqlite3"

# 元々db_commonに定義していたが、それだとalembicのmigrateでmodelを見つけられないため、こちらに移動
Base = declarative_base()


class User(Base):
    """
    ユーザテーブル

    id            : 主キー
    user_id      : id
    user_name      : 名前
    user_pwd      : パスワード
    auth_type      : 権限
    token      : トークン
    token_expire_dtime      : トークン有効期限
    reg_dtime : 登録日時
    """
    __tablename__ = 'user'

    id = Column(
        'id',
        INTEGER(unsigned=True),
        primary_key=True,
        autoincrement=True
    )
    user_id = Column('user_id', String(256), unique=True)
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
    token = Column(
        'token',
        String(256),
        nullable=False)
    token_expire_dtime = Column(
        'token_expire_dtime',
        DateTime,
        default=pytz.timezone("Asia/Tokyo").localize(datetime(2021, 1, 1)),
        nullable=False,
        server_default=current_timestamp()
    )

    def __init__(self, user_id, user_pwd, user_name, auth_type=0, reg_dtime=pytz.timezone("Asia/Tokyo").localize(datetime.now()), token="", token_expire_dtime=pytz.timezone("Asia/Tokyo").localize(datetime(2021, 1, 1))):
        self.user_id = user_id
        self.user_pwd = user_pwd
        self.user_name = user_name
        self.auth_type = auth_type
        self.reg_dtime = reg_dtime
        self.token = token
        self.token_expire_dtime = token_expire_dtime

    def _to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user_name,
            'reg_dtime': self.reg_dtime.isoformat(),
            'token': self.token,
            'token_expire_dtime': self.token_expire_dtime.isoformat(),
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
    name = Column('name', String(256), unique=True)
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

    def _to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'cost': self.cost,
            'reg_dtime': self.reg_dtime.isoformat(),
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
    name = Column('name', String(256), unique=True)
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

    def _to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'cost': self.cost,
            'reg_dtime': self.reg_dtime.isoformat(),
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
    name = Column('name', String(256), unique=True)
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

    def _to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'cost': self.cost,
            'reg_dtime': self.reg_dtime.isoformat(),
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
    name = Column('name', String(256), unique=True)
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

    def _to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'cost': self.cost,
            'reg_dtime': self.reg_dtime.isoformat(),
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
    name = Column('name', String(256), unique=True)
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

    def _to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'cost': self.cost,
            'reg_dtime': self.reg_dtime.isoformat(),
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
    name = Column('name', String(256), unique=True)
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

    def _to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'reg_dtime': self.reg_dtime.isoformat(),
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
    name = Column('name', String(256), unique=True)
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

    def _to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'reg_dtime': self.reg_dtime.isoformat(),
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

    def _to_dict(self):
        return {
            'id': self.id,
            'dest_id': self.dest_id,
            'name_id': self.name_id,
            'cost': self.cost,
            'unit_type': self.unit_type,
            'reg_dtime': self.reg_dtime.isoformat(),
        }


class ReportHead(Base):
    """
    日報ヘッダ情報

    id                  : 主キー
    customer_name       : 受注先
    worksite_name       : 工事名
    address             : 住所
    memo                : 備考
    completed_date      : 工事完了日(default=null (未完了))
    reg_dtime           : 登録日
    """
    __tablename__ = 'report_head'

    id = Column(
        'id',
        INTEGER(unsigned=True),
        primary_key=True,
        autoincrement=True
    )
    customer_name = Column('customer_name', String(256))
    worksite_name = Column('worksite_name', String(256))
    address = Column('address', String(512))
    memo = Column('memo', String(512))
    completed_date = Column('completed_date', String(8))
    reg_dtime = Column(
        'reg_dtime',
        DateTime,
        default=datetime.now(),
        nullable=False,
        server_default=current_timestamp()
    )

    def __init__(self, customer_name, worksite_name, address, memo, completed_date, reg_dtime=datetime.now()):
        self.customer_name = customer_name
        self.worksite_name = worksite_name
        self.address = address
        self.memo = memo
        self.completed_date = completed_date
        self.reg_dtime = reg_dtime

    def _to_dict(self):
        return {
            'id': self.id,
            'customer_name': self.customer_name,
            'worksite_name': self.worksite_name,
            'address': self.address,
            'memo': self.memo,
            'completed_date': self.completed_date,
            'reg_dtime': self.reg_dtime.isoformat(),
        }


class ReportDetail(Base):
    """
    日報明細情報

    id                  : 主キー
    report_head_id      : 日報ヘッドID
    work_date      : 作業日
    type                : 品目種別
    name               : 品目名
    dest                : 処分先
    cost                : 品目単価
    quant                : 数量
    memo                : 備考
    unit_type             : 単位
    reg_dtime           : 登録日
    """
    __tablename__ = 'report_detail'

    id = Column(
        'id',
        INTEGER(unsigned=True),
        primary_key=True,
        autoincrement=True
    )
    report_head_id = Column('report_head_id', INTEGER(unsigned=True))
    work_date = Column('work_date', String(8), nullable=False, default="")
    type = Column('type', INTEGER(unsigned=True))
    name = Column('name', String(256))
    dest = Column('dest', String(256), nullable=True)
    cost = Column('cost', INTEGER(unsigned=True))
    quant = Column('quant', INTEGER(unsigned=True))
    memo = Column('memo', String(256))
    unit_type = Column('unit_type', INTEGER(unsigned=True))
    reg_dtime = Column(
        'reg_dtime',
        DateTime,
        default=datetime.now(),
        nullable=False,
        server_default=current_timestamp()
    )

    def __init__(self, report_head_id, work_date, type, name, cost, quant, memo='', dest='', unit_type=0, reg_dtime=datetime.now()):
        self.report_head_id = report_head_id
        self.work_date = work_date
        self.type = type
        self.name = name
        self.cost = cost
        self.quant = quant
        self.memo = memo
        self.dest = dest
        self.unit_type = unit_type
        self.reg_dtime = reg_dtime

    def _to_dict(self):
        return {
            'id': self.id,
            'report_head_id': self.report_head_id,
            'work_date': self.work_date,
            'type': self.type,
            'name': self.name,
            'cost': self.cost,
            'quant': self.quant,
            'memo': self.memo,
            'dest': self.dest,
            'unit_type': self.unit_type,
            'reg_dtime': self.reg_dtime.isoformat(),
        }


if __name__ == "__main__":
    path = SQLITE3_NAME
    if not os.path.isfile(path):

        # テーブルを作成する
        Base.metadata.create_all(engine)
