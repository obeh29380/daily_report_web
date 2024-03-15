import json
import os

from sqlalchemy import select
from sqlalchemy.orm import Session

from db_common import get_engine
from tables import (
    ItemMaster,
    DestMaster,
    TrashMaster,
)
from schemas import (
    MAP_MASTER,
)
from app_utils import get_password_hash


DATA_FILE_PATH = os.path.join(os.path.dirname(__file__), 'master_data')


def register_init_data(master_type):

    with open(f'{DATA_FILE_PATH}/{master_type}.json', encoding="utf-8") as f:
        data = json.load(f)

    reg_data = [MAP_MASTER[master_type](**d) for d in data]

    with Session(get_engine()) as session:
        try:
            session.add_all(reg_data)
            session.commit()
        except Exception as e:
            print(type(e))
            print(e)
            session.rollback()


def register_user_account():
    with open(f'{DATA_FILE_PATH}/account.json', encoding="utf-8") as f:
        data = json.load(f)

    for d in data:
        d['account_pwd'] = get_password_hash('test')
    reg_account = [MAP_MASTER['account'](**d) for d in data]

    with open(f'{DATA_FILE_PATH}/user.json', encoding="utf-8") as f:
        data = json.load(f)
    for d in data:
        d['user_pwd'] = get_password_hash('test')
    reg_user = [MAP_MASTER['user'](**d) for d in data]

    with Session(get_engine()) as session:
        try:
            session.add_all(reg_account)
            session.add_all(reg_user)
            session.commit()
        except Exception as e:
            print(type(e))
            print(e)
            session.rollback()
    
        users = session.scalars(select(MAP_MASTER['user']))
        acconuts = session.scalars(select(MAP_MASTER['account']))

        user_list = [u for u in users]

        for ac in acconuts:
            ac.users = user_list

        session.commit()


def register_all_data():
    
    register_user_account()
    keys = [
        'staff',
        'car',
        'lease',
        'machine',
        'customer',
        'dest',
        'item',
        'trash',
    ]

    for k in keys:
        register_init_data(k)


if __name__ == '__main__':
    register_all_data()