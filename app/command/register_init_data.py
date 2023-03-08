import json
import os
import sys
sys.path.append('.')
from models import (
    StaffMaster,
    CarMaster,
    MachineMaster,
    LeaseMaster,
    ItemMaster,
    DestMaster,
    CustomerMaster,
    TrashMaster,
)
import db_common as db
from sqlalchemy import Transaction


DATA_FILE_PATH = './data'


def register_init_data_staff():
    with open(f'{DATA_FILE_PATH}/staff.json', encoding="utf-8") as f:
        data = json.load(f)

    # DBに登録
    try:
        for d in data:
            v = StaffMaster(d['name'], d['cost'])
            db.session.add(v)
        db.session.commit()
    except Exception as e:
        print(f'error {e} name={d["name"]}')
        print('db error')
        db.session.rollback()
        raise
    finally:
        db.session.close()


def register_init_data_car():
    with open(f'{DATA_FILE_PATH}/car.json', encoding="utf-8") as f:
        data = json.load(f)

    # DBに登録
    try:
        for d in data:
            v = CarMaster(d['name'], d['cost'])
            db.session.add(v)
        db.session.commit()
    except Exception as e:
        print(f'error {e} name={d["name"]}')
        print('db error')
        db.session.rollback()
        raise
    finally:
        db.session.close()


def register_init_data_machine():
    with open(f'{DATA_FILE_PATH}/machine.json', encoding="utf-8") as f:
        data = json.load(f)

    # DBに登録
    try:
        for d in data:
            v = MachineMaster(d['name'], d['cost'])
            db.session.add(v)
        db.session.commit()
    except Exception as e:
        print(f'error {e} name={d["name"]}')
        print('db error')
        db.session.rollback()
        raise
    finally:
        db.session.close()


def register_init_data_lease():
    with open(f'{DATA_FILE_PATH}/lease.json', encoding="utf-8") as f:
        data = json.load(f)

    # DBに登録
    try:
        for d in data:
            v = LeaseMaster(d['name'], d['cost'])
            db.session.add(v)
        db.session.commit()
    except Exception as e:
        print(f'error {e} name={d["name"]}')
        print('db error')
        db.session.rollback()
        raise
    finally:
        db.session.close()


def register_init_data_item():
    with open(f'{DATA_FILE_PATH}/item.json', encoding="utf-8") as f:
        data = json.load(f)

    # DBに登録
    try:
        for d in data:
            v = ItemMaster(d['name'])
            db.session.add(v)
        db.session.commit()
    except Exception as e:
        print(f'error {e} name={d["name"]}')
        print('db error')
        db.session.rollback()
        raise
    finally:
        db.session.close()


def register_init_data_dest():
    with open(f'{DATA_FILE_PATH}/dest.json', encoding="utf-8") as f:
        data = json.load(f)

    # DBに登録
    try:
        for d in data:
            v = DestMaster(d['name'])
            db.session.add(v)
        db.session.commit()
    except Exception as e:
        print(f'error {e} name={d["name"]}')
        print('db error')
        db.session.rollback()
        raise
    finally:
        db.session.close()


def register_init_data_customer():
    with open(f'{DATA_FILE_PATH}/customer.json', encoding="utf-8") as f:
        data = json.load(f)

    # DBに登録
    try:
        for d in data:
            v = CustomerMaster(d['name'])
            db.session.add(v)
        db.session.commit()
    except Exception as e:
        print(f'error {e} name={d["name"]}')
        print('db error')
        db.session.rollback()
        raise
    finally:
        db.session.close()



