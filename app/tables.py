from __future__ import annotations
import datetime

from typing import (
    List,
    Optional,
)
from sqlalchemy import (
    ForeignKey,
    String,
    DateTime,
    Column,
    Table,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    declared_attr
)
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.sql.functions import current_timestamp

from db_common import get_engine


class Base(DeclarativeBase):
    pass


class Tablename:
    @declared_attr.directive
    def __tablename__(cls) -> Optional[str]:
        return cls.__name__.lower()


association_table = Table(
    "association_table",
    Base.metadata,
    Column("account_id", ForeignKey("account.id"), primary_key=True),
    Column("user_id", ForeignKey("user.id"), primary_key=True),
)


class Account(Base):
    # many-to-manyの記述。
    # https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#relationships-many-to-many
    __tablename__ = "account"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    account_id: Mapped[str] = mapped_column(String(128), unique=True)
    account_pwd: Mapped[str] = mapped_column(String(256))
    fullname: Mapped[Optional[str]]
    reg_dtime: Mapped[DateTime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.datetime.now(),
        server_default=current_timestamp()
    )

    # cascade="all, delete-orphan" だと、Account（親）削除時にUsers（子）も削除する。
    # 削除したくないので、デフォルト（save hoge , merge）にしてみる
    # backrefにより、双方向でリレーションが張られる。そのため、Users側では参照を定義しなくても、account.id とかで参照できる。
    # が、双方向だと両方からuser.idを登録しようとするため、こちらをViewonlyとする。→ 機能しなくなったのでいったんもどす
    # TODO Accountに属するユーザ一覧の取得に支障がないか検証
    users: Mapped[List[User]] = relationship(
        secondary=association_table
    )

    def __repr__(self) -> str:
        return f"Account(id={self.id!r}, account_id={self.account_id!r}, "\
            f"fullname={self.fullname!r}"


class AccountBase:
    @declared_attr.cascading
    def account_id(cls) -> Mapped[Account]:
        return mapped_column(ForeignKey("account.id"))

    @declared_attr.cascading
    def account(cls) -> Mapped[Account]:
        return relationship()


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(128), unique=True)
    user_pwd: Mapped[str] = mapped_column(String(256))
    fullname: Mapped[Optional[str]]
    reg_dtime: Mapped[DateTime] = mapped_column(
        DateTime, nullable=False,
        default=datetime.datetime.now(),
        server_default=current_timestamp(),
    )
    auth_type: Mapped[int] = mapped_column(default=0)
    token: Mapped[str] = mapped_column(
        String(256),
        nullable=True,
        default=None,
    )
    disabled: Mapped[bool] = mapped_column(default=False)

    # back_populateとか指定するとエラーになる。なぜ？
    accounts: Mapped[List[Account]] = relationship(
        secondary=association_table
    )

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, user_id={self.user_id!r}, user_pwd={self.user_pwd!r}, "\
            f"fullname={self.fullname!r}, auth_type={self.auth_type!r})"

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'fullname': self.fullname,
            'user_pwd': self.user_pwd,
            'auth_type': self.auth_type,
        }
    
    def to_dict_nopass(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'fullname': self.fullname,
            'auth_type': self.auth_type,
        }


class StaffMaster(AccountBase, Base):
    __tablename__ = 'staff_master'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128))
    cost: Mapped[int] = mapped_column(default=0)
    memo: Mapped[Optional[str]] = mapped_column(String(512), default=None)

    __table_args__ = (UniqueConstraint(
        'name', 'account_id'),)

    def __repr__(self) -> str:
        return f"StaffMaster(id={self.id!r}, name={self.name!r}, "\
            f"cost={self.cost!r}, account={self.account!r}, memo={self.memo!r})"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'cost': self.cost,
            'memo': self.memo if self.memo is not None else "",
        }


class CarMaster(AccountBase, Base):
    __tablename__ = 'car_master'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), unique=True)
    cost: Mapped[int] = mapped_column(default=0)
    memo: Mapped[Optional[str]] = mapped_column(String(512), default=None)

    __table_args__ = (UniqueConstraint(
        'name', 'account_id'),)

    def __repr__(self) -> str:
        return f"CarMaster(id={self.id!r}, name={self.name!r}, "\
            f"cost={self.cost!r}, memo={self.memo!r})"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'cost': self.cost,
            'memo': self.memo if self.memo is not None else "",
        }


class LeaseMaster(AccountBase, Base):
    __tablename__ = 'lease_master'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), unique=True)
    cost: Mapped[int] = mapped_column(default=0)
    memo: Mapped[Optional[str]] = mapped_column(String(512), default=None)

    __table_args__ = (UniqueConstraint(
        'name', 'account_id'),)

    def __repr__(self) -> str:
        return f"LeaseMaster(id={self.id!r}, name={self.name!r}, "\
            f"cost={self.cost!r}, memo={self.memo!r})"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'cost': self.cost,
            'memo': self.memo if self.memo is not None else "",
        }


class MachineMaster(AccountBase, Base):
    __tablename__ = 'machine_master'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), unique=True)
    cost: Mapped[int] = mapped_column(default=0)
    memo: Mapped[Optional[str]] = mapped_column(String(512), default=None)

    __table_args__ = (UniqueConstraint(
        'name', 'account_id'),)

    def __repr__(self) -> str:
        return f"MachineMaster(id={self.id!r}, name={self.name!r}, "\
            f"cost={self.cost!r}, memo={self.memo!r})"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'cost': self.cost,
            'memo': self.memo if self.memo is not None else "",
        }


class CustomerMaster(AccountBase, Base):
    __tablename__ = 'customer_master'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), unique=True)
    memo: Mapped[Optional[str]] = mapped_column(String(512), default=None)

    __table_args__ = (UniqueConstraint(
        'name', 'account_id'),)

    def __repr__(self) -> str:
        return f"CustomerMaster(id={self.id!r}, name={self.name!r}, "\
            f"memo={self.memo!r})"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'memo': self.memo if self.memo is not None else "",
        }


class DestMaster(AccountBase, Base):
    __tablename__ = 'dest_master'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), unique=True)
    memo: Mapped[Optional[str]] = mapped_column(String(512), default=None)

    __table_args__ = (UniqueConstraint(
        'name', 'account_id'),)

    def __repr__(self) -> str:
        return f"DestMaster(id={self.id!r}, name={self.name!r}, "\
            f"memo={self.memo!r})"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'memo': self.memo if self.memo is not None else "",
        }


class ItemMaster(AccountBase, Base):
    __tablename__ = 'item_master'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), unique=True)
    cost: Mapped[int] = mapped_column(default=0)
    memo: Mapped[Optional[str]] = mapped_column(String(512), default=None)

    __table_args__ = (UniqueConstraint(
        'name', 'account_id'),)

    def __repr__(self) -> str:
        return f"ItemMaster(id={self.id!r}, name={self.name!r}, "\
            f"memo={self.memo!r})"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'memo': self.memo if self.memo is not None else "",
        }


class TrashMaster(Base):
    # dest_master, item_master を参照する
    __tablename__ = 'trash_master'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # 関連付けのためにrelationship()が必要。ただ、Trashからの片方向のみで良いため、back_populatesは不要
    dest_id: Mapped[DestMaster] = mapped_column(ForeignKey('dest_master.id'))
    dest: Mapped[DestMaster] = relationship()
    item_id: Mapped[ItemMaster] = mapped_column(ForeignKey('item_master.id'))
    item: Mapped[ItemMaster] = relationship()
    cost: Mapped[int] = mapped_column(default=0)
    unit_type: Mapped[int] = mapped_column(default=0)
    memo: Mapped[Optional[str]] = mapped_column(String(512), default=None)

    __table_args__ = (UniqueConstraint(
        'dest_id', 'item_id', 'unit_type'),)

    def __repr__(self) -> str:
        return f"TrashMaster(id={self.id!r}, cost={self.cost!r}, "\
            f"dest={self.dest!r}, item={self.item!r}, "\
            f"unit_type={self.unit_type!r}, memo={self.memo!r})"

    def to_dict(self):
        return {
            'id': self.id,
            'dest_id': self.dest_id,
            'dest': self.dest.to_dict(),
            'item_id': self.item_id,
            'item': self.item.to_dict(),
            'cost': self.cost,
            'unit_type': self.unit_type,
            'memo': self.memo if self.memo is not None else "",
        }


class ReportHead(AccountBase, Base):
    __tablename__ = 'report_head'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    customer_name: Mapped[str] = mapped_column(String(512))
    worksite_name: Mapped[str] = mapped_column(String(512))
    address: Mapped[str] = mapped_column(String(512))
    reg_dtime: Mapped[DateTime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.datetime.now(),
        server_default=current_timestamp(),
    )
    completed_date: Mapped[DateTime] = mapped_column(
        DateTime,
        nullable=True,
    )
    memo: Mapped[Optional[str]] = mapped_column(String(512), default=None)

    def __repr__(self) -> str:
        return f"ReportHead(id={self.id!r}, customer_name={self.customer_name!r}, "\
            f"worksite_name={self.worksite_name!r}, completed_date={self.completed_date!r}, memo={self.memo!r})"

    def to_dict(self):
        return {
            'id': self.id,
            'customer_name': self.customer_name,
            'worksite_name': self.worksite_name,
            'address': self.address,
            'completed_date': datetime.datetime.strftime(self.completed_date, '%Y-%m-%d') if self.completed_date is not None else None,
            'memo': self.memo if self.memo is not None else "",
        }


class ReportDetail(Base):
    __tablename__ = 'report_detail'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    report_head_id: Mapped[ReportHead] = mapped_column(
        ForeignKey('report_head.id')
    )
    report_head: Mapped[ReportHead] = relationship()
    work_date: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    type: Mapped[int] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(String(256))
    dest: Mapped[str] = mapped_column(String(256), nullable=True)
    cost: Mapped[int] = mapped_column(default=0)
    quant: Mapped[int] = mapped_column(default=0)
    memo: Mapped[Optional[str]] = mapped_column(String(512), default=None)
    unit_type: Mapped[int] = mapped_column(default=0)
    reg_dtime: Mapped[DateTime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.datetime.now(),
        server_default=current_timestamp()
    )

    # __table_args__ = (UniqueConstraint(
    #     'report_head_id', 'work_date'),)

    def __repr__(self) -> str:
        return f"ReportDetail(id={self.id!r}, report_head={self.report_head!r}, "\
            f"work_date={self.work_date!r}, type={self.type!r})"\
            f"name={self.name!r}, dest={self.dest!r})"\
            f"cost={self.cost!r}, quant={self.quant!r})"\
            f"memo={self.memo!r}, unit_type={self.unit_type!r})"

    def to_dict(self):
        return {
            'id': self.id,
            'report_head': self.report_head.to_dict(),
            'work_date': datetime.datetime.strftime(self.work_date, '%Y-%m-%d'),
            'type': self.type,
            'name': self.name,
            'dest': self.dest,
            'cost': self.cost,
            'quant': self.quant,
            'unit_type': self.unit_type,
            'memo': self.memo if self.memo is not None else "",
        }



def create_all_tables():
    engine = get_engine()
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    create_all_tables()
