from enum import Enum
from pathlib import Path
import hashlib
import jwt
import datetime
import logging
import pytz
import json

import responder
from sqlalchemy.sql.expression import func

from models import (
    User,
    StaffMaster,
    CarMaster,
    MachineMaster,
    LeaseMaster,
    ItemMaster,
    DestMaster,
    CustomerMaster,
    TrashMaster,
    ReportHead,
    ReportDetail,
)
import db_common as db

TOKEN_EXPIRE_MINUTES = 60*6
JWT_KEY = 'trym_token_key'
BASE_DIR = Path(__file__).resolve().parents[0]
UNIT_TYPE = [
    {
        'id': 0,
        'name': 'なし'
    },
    {
        'id': 1,
        'name': 'Kg'
    },
    {
        'id': 2,
        'name': 't'
    },
]

api = responder.API(
    static_dir=str(BASE_DIR.joinpath('static')),
    templates_dir=str(BASE_DIR.joinpath('templates')),
    cors_params={'max_age': 0}
)
logger = logging.getLogger(__name__)


# util #####################################
class ItemType(Enum):
    OTHER = 0
    STAFF = 1
    CAR = 2
    MACHINE = 3
    LEASE = 4
    TRANSPORT = 5
    TRASH = 6
    VALUABLE = 7
    
    @classmethod
    def value_of(cls, target_value):
        for e in ItemType:
            if e.value == target_value:
                return e
        raise ValueError('{} は有効な乗り物の値ではありません'.format(target_value))


def to_json(data):
    """クエリオブジェクトをdict形式にパースする。

    Args:
        data (_type_): _description_
    """

    res = list()
    for d in data:
        res.append(
            {
                'id': d.id,
                'dest_name': d.dest_name,
                'item_name': d.item_name,
                'cost': d.cost,
                'unit_type': list(filter(lambda item: item['id'] == d.unit_type, UNIT_TYPE))[0]['name'],
            }
        )
    return res


def ensure_str(txt, default=None):
    """文字列のチェック
    文字列が空文字かNoneの場合、defaultを返す。
    文字列が上記以外の場合、入力値をそのまま返す。

    Args:
        txt (_type_): チェック対象文字列
        default (_type_, optional): _description_. Defaults to None.
    """

    if txt is None or txt == '':
        return default
    else:
        return txt


def get_simple_master_data(data):
    """id,name,cost から成るマスタデータのクエリオブジェクトについて、
    クライアントに返す形式のデータに変換する。

    Args:
        data (queryobject): dbから取得したクエリオブジェクト
    """

    if data is None:
        return None

    res = dict()
    res['col_definitions'] = {
        'id': {
            'colname': 'id',
            'type': 'integer',
            'readonly': True
        },
        'name': {
            'colname': '名前',
            'type': 'string',
            'readonly': False
        },
        'cost': {
            'colname': '費用',
            'type': 'integer',
            'readonly': False
        },
    }

    col_values = list()
    for d in data:
        col_values.append(
            {
                'id': d.id,
                'name': d.name,
                'cost': d.cost,
            }
        )
    res['col_values'] = col_values

    return res


def get_name_only_master_data(data):
    """id,name から成るマスタデータのクエリオブジェクトについて、
    クライアントに返す形式のデータに変換する。

    Args:
        data (queryobject): dbから取得したクエリオブジェクト
    """

    if data is None:
        return None

    res = dict()
    res['col_definitions'] = {
        'id': {
            'colname': 'id',
            'type': 'integer',
            'readonly': True
        },
        'name': {
            'colname': '名前',
            'type': 'string',
            'readonly': False
        }
    }

    col_values = list()
    for d in data:
        col_values.append(
            {
                'id': d.id,
                'name': d.name
            }
        )
    res['col_values'] = col_values

    return res


def utc_now_dtime():
    return pytz.timezone('Asia/Tokyo').localize(datetime.datetime.now())


def nvl(txt, replace=''):
    if txt is None or txt == 'null':
        return replace
    else:
        return txt


def validate_token(token):
    
    if ensure_str(token) is None:
        return None

    try:
        decode_token = jwt.decode(token, key=JWT_KEY, algorithms="HS256")
    except Exception as e:
        logger.debug(type(e))
        return None

    user = db.session.query(User).filter_by(
        user_id=decode_token['id'],
        token=token
    ).first()

    if user is None:
        return None

    if pytz.timezone('UTC').localize(user.token_expire_dtime) < utc_now_dtime():
        return None

    # トークン有効期限更新
    user.token_expire_dtime = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(minutes=TOKEN_EXPIRE_MINUTES)

    return decode_token


@api.route("/master/staff")
class StaffMasterInfo():

    async def on_get(self, req, resp):

        db_data = db.session.query(StaffMaster.id, StaffMaster.name, StaffMaster.cost)
        db.session.close()

        res = get_simple_master_data(db_data)

        resp.media = {
            'response': res
        }

    async def on_post(self, req, resp):

        response = dict()
        data = await req.media()
        name = data.get('values[name]')
        cost = data.get('values[cost]')

        # 何も入力されていない場合
        if name is None:
            resp.media = 'name not entered'
            resp.status_code = api.status_codes.HTTP_400
            return
        if cost is None:
            resp.media = 'cost not entered'
            resp.status_code = api.status_codes.HTTP_400
            return

        v = StaffMaster(name, cost)
        # 登録済みチェック
        d = db.session.query(StaffMaster).filter_by(name=name).first()
        if d is not None:
            resp.media = {'message': 'すでに登録済みです'}
            resp.status_code = api.status_codes.HTTP_500
            return

        # DBに登録
        try:
            db.session.add(v)
            db.session.commit()
        except Exception as e:
            print(type(e))
            resp.status_code = api.status_codes.HTTP_500
            raise
        finally:
            db.session.close()

        # 発番されたidを取得
        new_id = db.session.query(func.max(StaffMaster.id)).scalar()
        db.session.close()
        response['new_id'] = new_id
        response['name'] = name
        response['cost'] = cost

        resp.status_code = api.status_codes.HTTP_200
        resp.media = response

    async def on_delete(self, req, resp):

        data = await req.media()
        id = data.get('id')

        if id is None:
            print('no id')
            resp.status_code = api.status_codes.HTTP_500
            return

        # 削除対象のデータを検索
        try:
            staff = db.session.query(StaffMaster).filter_by(id=id).first()
        except Exception as e:
            print(type(e))
            print('db error')
            resp.status_code = api.status_codes.HTTP_500
            db.session.close()
            raise

        # 指定したデータを削除
        try:
            db.session.delete(staff)
            db.session.commit()
        except Exception as e:
            print(type(e))
            print('db error')
            resp.status_code = api.status_codes.HTTP_500
            raise
        finally:
            db.session.close()


@api.route("/master/car")
class CarMasterInfo():

    async def on_get(self, req, resp):

        db_data = db.session.query(CarMaster.id, CarMaster.name, CarMaster.cost)
        db.session.close()

        res = get_simple_master_data(db_data)

        resp.media = {
            'response': res
        }

    async def on_post(self, req, resp):

        response = dict()
        data = await req.media()
        name = data.get('values[name]')
        cost = data.get('values[cost]')

        # 何も入力されていない場合
        if name is None:
            resp.media = 'name not entered'
            resp.status_code = api.status_codes.HTTP_400
            return
        if cost is None:
            resp.media = 'cost not entered'
            resp.status_code = api.status_codes.HTTP_400
            return

        v = CarMaster(name, cost)
        # 登録済みチェック
        d = db.session.query(CarMaster).filter_by(name=name).first()
        if d is not None:
            resp.media = {'message': 'すでに登録済みです'}
            resp.status_code = api.status_codes.HTTP_500
            return

        # DBに登録
        try:
            db.session.add(v)
            db.session.commit()
        except Exception as e:
            print(type(e))
            print('db error')
            resp.status_code = api.status_codes.HTTP_500
            raise
        finally:
            db.session.close()

        # 発番されたidを取得
        new_id = db.session.query(func.max(CarMaster.id)).scalar()
        db.session.close()
        response['new_id'] = new_id
        response['name'] = name
        response['cost'] = cost

        resp.status_code = api.status_codes.HTTP_200
        resp.media = response

    async def on_delete(self, req, resp):

        data = await req.media()
        id = data.get('id')

        if id is None:
            print('no id')
            resp.status_code = api.status_codes.HTTP_500
            return

        # 削除対象のデータを検索
        staff = db.session.query(CarMaster).filter_by(id=id).first()

        # 指定したデータを削除
        try:
            db.session.delete(staff)
            db.session.commit()
        except Exception as e:
            print(type(e))
            print('db error')
            resp.status_code = api.status_codes.HTTP_500
            raise
        finally:
            db.session.close()


@api.route("/master/lease")
class LeaseMasterInfo():

    async def on_get(self, req, resp):

        db_data = db.session.query(LeaseMaster.id, LeaseMaster.name, LeaseMaster.cost)
        db.session.close()

        res = get_simple_master_data(db_data)

        resp.media = {
            'response': res
        }

    async def on_post(self, req, resp):

        response = dict()
        data = await req.media()
        name = data.get('values[name]')
        cost = data.get('values[cost]')

        # 何も入力されていない場合
        if name is None:
            resp.media = 'name not entered'
            resp.status_code = api.status_codes.HTTP_400
            return
        if cost is None:
            resp.media = 'cost not entered'
            resp.status_code = api.status_codes.HTTP_400
            return

        v = LeaseMaster(name, cost)
        # 登録済みチェック
        d = db.session.query(LeaseMaster).filter_by(name=name).first()
        if d is not None:
            resp.media = {'message': 'すでに登録済みです'}
            resp.status_code = api.status_codes.HTTP_500
            return

        # DBに登録
        try:
            db.session.add(v)
            db.session.commit()
        except Exception as e:
            print(type(e))
            print('db error')
            resp.status_code = api.status_codes.HTTP_500
            raise
        finally:
            db.session.close()

        # 発番されたidを取得
        new_id = db.session.query(func.max(LeaseMaster.id)).scalar()
        db.session.close()
        response['new_id'] = new_id
        response['name'] = name
        response['cost'] = cost

        resp.status_code = api.status_codes.HTTP_200
        resp.media = response

    async def on_delete(self, req, resp):

        data = await req.media()
        id = data.get('id')

        if id is None:
            print('no id')
            resp.status_code = api.status_codes.HTTP_500
            return

        # 削除対象のデータを検索
        staff = db.session.query(LeaseMaster).filter_by(id=id).first()

        # 指定したデータを削除
        try:
            db.session.delete(staff)
            db.session.commit()
        except Exception as e:
            print(type(e))
            print('db error')
            resp.status_code = api.status_codes.HTTP_500
            raise
        finally:
            db.session.close()


@api.route("/master/machine")
class MachineMasterInfo():

    async def on_get(self, req, resp):

        db_data = db.session.query(MachineMaster.id, MachineMaster.name, MachineMaster.cost)
        db.session.close()

        res = get_simple_master_data(db_data)

        resp.media = {
            'response': res
        }

    async def on_post(self, req, resp):

        response = dict()
        data = await req.media()
        name = data.get('values[name]')
        cost = data.get('values[cost]')

        # 何も入力されていない場合
        if name is None:
            resp.media = 'name not entered'
            resp.status_code = api.status_codes.HTTP_400
            return
        if cost is None:
            resp.media = 'cost not entered'
            resp.status_code = api.status_codes.HTTP_400
            return

        v = MachineMaster(name, cost)
        # 登録済みチェック
        d = db.session.query(MachineMaster).filter_by(name=name).first()
        if d is not None:
            resp.media = {'message': 'すでに登録済みです'}
            resp.status_code = api.status_codes.HTTP_500
            return

        # DBに登録
        try:
            db.session.add(v)
            db.session.commit()
        except Exception as e:
            print(type(e))
            print('db error')
            resp.status_code = api.status_codes.HTTP_500
            raise
        finally:
            db.session.close()

        # 発番されたidを取得
        new_id = db.session.query(func.max(MachineMaster.id)).scalar()
        db.session.close()
        response['new_id'] = new_id
        response['name'] = name
        response['cost'] = cost

        resp.status_code = api.status_codes.HTTP_200
        resp.media = response

    async def on_delete(self, req, resp):

        data = await req.media()
        id = data.get('id')

        if id is None:
            print('no id')
            resp.status_code = api.status_codes.HTTP_500
            return

        # 削除対象のデータを検索
        staff = db.session.query(MachineMaster).filter_by(id=id).first()

        # 指定したデータを削除
        try:
            db.session.delete(staff)
            db.session.commit()
        except Exception as e:
            print(type(e))
            print('db error')
            resp.status_code = api.status_codes.HTTP_500
            raise
        finally:
            db.session.close()


@api.route("/master/customer")
class CustomerMasterInfo():

    async def on_get(self, req, resp):

        db_data = db.session.query(CustomerMaster.id, CustomerMaster.name)
        db.session.close()

        res = get_name_only_master_data(db_data)

        resp.media = {
            'response': res
        }

    async def on_post(self, req, resp):

        response = dict()
        data = await req.media()
        name = data.get('values[name]')

        # 何も入力されていない場合
        if name is None:
            resp.media = 'name not entered'
            print('name not entered')
            resp.status_code = api.status_codes.HTTP_400
            return

        v = CustomerMaster(name)
        # 登録済みチェック
        d = db.session.query(CustomerMaster).filter_by(name=name).first()
        if d is not None:
            resp.media = {'message': 'すでに登録済みです'}
            resp.status_code = api.status_codes.HTTP_500
            return

        # DBに登録
        try:
            db.session.add(v)
            db.session.commit()
        except Exception as e:
            print(type(e))
            print('db error')
            resp.status_code = api.status_codes.HTTP_500
            raise
        finally:
            db.session.close()

        # 発番されたidを取得
        new_id = db.session.query(func.max(CustomerMaster.id)).scalar()
        db.session.close()
        response['new_id'] = new_id
        response['name'] = name

        resp.status_code = api.status_codes.HTTP_200
        resp.media = response

    async def on_delete(self, req, resp):

        data = await req.media()
        id = data.get('id')

        if id is None:
            print('no id')
            resp.status_code = api.status_codes.HTTP_500
            return

        # 削除対象のデータを検索
        staff = db.session.query(CustomerMaster).filter_by(id=id).first()

        # 指定したデータを削除
        try:
            db.session.delete(staff)
            db.session.commit()
        except Exception as e:
            print(type(e))
            print('db error')
            resp.status_code = api.status_codes.HTTP_500
            raise
        finally:
            db.session.close()


@api.route("/master/dest")
class DestMasterInfo():

    async def on_get(self, req, resp):

        db_data = db.session.query(DestMaster.id, DestMaster.name)
        db.session.close()

        res = get_name_only_master_data(db_data)

        resp.media = {
            'response': res
        }

    async def on_post(self, req, resp):

        response = dict()
        data = await req.media()
        name = data.get('values[name]')

        # 何も入力されていない場合
        if name is None:
            resp.media = 'name not entered'
            resp.status_code = api.status_codes.HTTP_400
            return

        v = DestMaster(name)
        # 登録済みチェック
        d = db.session.query(DestMaster).filter_by(name=name).first()
        if d is not None:
            resp.media = {'message': 'すでに登録済みです'}
            resp.status_code = api.status_codes.HTTP_500
            return

        # DBに登録
        try:
            db.session.add(v)
            db.session.commit()
        except Exception as e:
            print(type(e))
            print('db error')
            resp.status_code = api.status_codes.HTTP_500
            raise
        finally:
            db.session.close()

        # 発番されたidを取得
        new_id = db.session.query(func.max(DestMaster.id)).scalar()
        db.session.close()
        response['new_id'] = new_id
        response['name'] = name

        resp.status_code = api.status_codes.HTTP_200
        resp.media = response

    async def on_delete(self, req, resp):

        data = await req.media()
        id = data.get('id')

        if id is None:
            print('no id')
            resp.status_code = api.status_codes.HTTP_500
            return

        # 削除対象のデータを検索
        staff = db.session.query(DestMaster).filter_by(id=id).first()

        # 指定したデータを削除
        try:
            db.session.delete(staff)
            db.session.commit()
        except Exception as e:
            print(type(e))
            print('db error')
            resp.status_code = api.status_codes.HTTP_500
            raise
        finally:
            db.session.close()


@api.route("/master/items")
class ItemMasterInfo():

    async def on_get(self, req, resp):

        db_data = db.session.query(ItemMaster.id, ItemMaster.name, ItemMaster.cost)
        db.session.close()

        res = get_simple_master_data(db_data)

        resp.media = {
            'response': res
        }

    async def on_post(self, req, resp):

        response = dict()
        data = await req.media()
        name = data.get('values[name]')
        cost = data.get('values[cost]')

        # 何も入力されていない場合
        if name is None:
            resp.media = 'name not entered'
            resp.status_code = api.status_codes.HTTP_400
            return
        if cost is None:
            resp.media = 'cost not entered'
            resp.status_code = api.status_codes.HTTP_400
            return

        v = ItemMaster(name, cost)
        # 登録済みチェック
        d = db.session.query(ItemMaster).filter_by(name=name).first()
        if d is not None:
            resp.media = {'message': 'すでに登録済みです'}
            resp.status_code = api.status_codes.HTTP_500
            return

        # DBに登録
        try:
            db.session.add(v)
            db.session.commit()
        except Exception as e:
            print(type(e))
            print('db error')
            resp.status_code = api.status_codes.HTTP_500
            raise
        finally:
            db.session.close()

        # 発番されたidを取得
        new_id = db.session.query(func.max(ItemMaster.id)).scalar()
        db.session.close()
        response['new_id'] = new_id
        response['name'] = name
        response['cost'] = cost

        resp.status_code = api.status_codes.HTTP_200
        resp.media = response

    async def on_delete(self, req, resp):

        data = await req.media()
        id = data.get('id')

        if id is None:
            print('no id')
            resp.status_code = api.status_codes.HTTP_500
            return

        # 削除対象のデータを検索
        staff = db.session.query(ItemMaster).filter_by(id=id).first()

        # 指定したデータを削除
        try:
            db.session.delete(staff)
            db.session.commit()
        except Exception as e:
            print(type(e))
            print('db error')
            resp.status_code = api.status_codes.HTTP_500
            raise
        finally:
            db.session.close()


@api.route("/master/work/complete")
class WorkStatusComplete():
    async def on_post(self, req, resp):

        data = await req.media()
        worksite_name = data.get('values[worksite_name]')
        completed_date = data.get('values[completed_date]')

        # 必須項目入力チェック
        if worksite_name is None:
            resp.media = 'worksite_name not entered'
            resp.status_code = api.status_codes.HTTP_400
            return

        # 登録済みチェック
        d = db.session.query(ReportHead).filter_by(worksite_name=worksite_name).first()
        if d is None:
            resp.status_code = api.status_codes.HTTP_404
            return

        # Noneの場合、完了を取り消すことになる。
        d.completed_date = completed_date

        # DBに登録
        try:
            db.session.commit()
        except Exception as e:
            print(type(e))
            print('db error')
            resp.status_code = api.status_codes.HTTP_500
            raise
        finally:
            db.session.close()

        # 発番されたidを取得
        resp.status_code = api.status_codes.HTTP_200


@api.route("/master/work")
class WorkStatusMasterInfo():

    async def on_get(self, req, resp):

        db_data = db.session.query(ReportHead)
        db.session.close()

        if db_data is None:
            return None

        res = dict()
        res['col_definitions'] = {
            'id': {
                'colname': 'id',
                'type': 'integer',
                'readonly': True
            },
            'worksite_name': {
                'colname': '工事名',
                'type': 'string',
                'readonly': False
            },
            'customer': {
                'colname': '受注先',
                'type': 'string',
                'readonly': False
            },
            'address': {
                'colname': '住所',
                'type': 'string',
                'readonly': False
            },
            'memo': {
                'colname': 'メモ',
                'type': 'string',
                'readonly': False
            },
            'complete': {
                'colname': '完了',
                'type': 'boolean',
                'readonly': False
            },
            'completed_date': {
                'colname': '完了日',
                'type': 'date',
                'readonly': False
            },
        }

        col_values = list()
        for d in db_data:
            col_values.append(
                {
                    'id': d.id,
                    'worksite_name': d.worksite_name,
                    'customer': nvl(d.customer_name),
                    'address': nvl(d.address),
                    'memo': nvl(d.memo),
                    'complete': True if d.completed_date is not None else False,
                    'completed_date': d.completed_date,
                }
            )
        res['col_values'] = col_values

        resp.media = {
            'response': res
        }

    async def on_post(self, req, resp):

        response = dict()
        data = await req.media()
        worksite_name = data.get('values[worksite_name]')
        customer = data.get('values[customer]')
        address = data.get('values[address]')
        memo = data.get('values[memo]')
        complete = data.get('values[complete]')
        completed_date = data.get('values[completed_date]')

        # 必須項目入力チェック
        if worksite_name is None:
            resp.media = 'worksite_name not entered'
            resp.status_code = api.status_codes.HTTP_400
            return

        # 登録済みチェック
        d = db.session.query(ReportHead).filter_by(worksite_name=worksite_name).first()
        if d is not None:
            resp.media = {'message': 'すでに登録済みです'}
            resp.status_code = api.status_codes.HTTP_500
            return

        v = ReportHead(customer, worksite_name, address, memo, completed_date)
        # DBに登録
        try:
            db.session.add(v)
            db.session.commit()
        except Exception as e:
            print(type(e))
            print('db error')
            resp.status_code = api.status_codes.HTTP_500
            raise
        finally:
            db.session.close()

        # 発番されたidを取得
        new_id = db.session.query(func.max(ReportHead.id)).scalar()
        db.session.close()
        response['new_id'] = new_id
        response['worksite_name'] = worksite_name
        response['customer'] = customer
        response['address'] = address
        response['memo'] = memo
        response['completed_date'] = completed_date

        resp.status_code = api.status_codes.HTTP_200
        resp.media = response


@api.route("/master/trash/{dest_id}/{item_id}")
class TrashMasterInfoById():

    async def on_get(self, req, resp, dest_id, item_id):

        try:
            d = db.session.query(TrashMaster).filter_by(dest_id=dest_id, name_id=item_id).first()
        except Exception as e:
            print(type(e))
            raise
        finally:
            db.session.close()

        if d is None:
            resp.status_code = api.status_codes.HTTP_404
            return

        res = {
            'cost': d.cost,
            'unit_type': d.unit_type,
        }

        resp.media = res


@api.route("/master/trash")
class TrashMasterInfo():

    async def on_get(self, req, resp):

        db_data = db.session.query(
            TrashMaster.id,
            DestMaster.name.label('dest_name'),
            ItemMaster.name.label('item_name'),
            TrashMaster.cost,
            TrashMaster.unit_type
        ).join(
            DestMaster,
            TrashMaster.dest_id == DestMaster.id
        ).join(
            ItemMaster,
            TrashMaster.name_id == ItemMaster.id
        )
        dest = db.session.query(DestMaster.id, DestMaster.name)
        item = db.session.query(ItemMaster.id, ItemMaster.name)
        db.session.close()

        dest_list = list()
        for d in dest:
            dest_list.append(
                {
                    'id': d.id,
                    'name': d.name
                }
            )
        item_list = list()
        for d in item:
            item_list.append(
                {
                    'id': d.id,
                    'name': d.name
                }
            )

        res = dict()
        res['col_definitions'] = {
            'id': {
                'colname': 'id',
                'type': 'integer',
                'readonly': True
            },
            'dest_name': {
                'colname': '処分先',
                'type': 'select',
                'selections': dest_list,
                'readonly': False
            },
            'item_name': {
                'colname': '品名',
                'type': 'select',
                'selections': item_list,
                'readonly': False
            },
            'cost': {
                'colname': '費用',
                'type': 'integer',
                'readonly': False
            },
            'unit_type': {
                'colname': '単位',
                'type': 'select',
                'selections': UNIT_TYPE,
                'readonly': False
            },
        }

        col_values = list()
        for d in db_data:
            col_values.append(
                {
                    'id': d.id,
                    'dest_name': d.dest_name,
                    'item_name': d.item_name,
                    'cost': d.cost,
                    'unit_type': list(filter(lambda item: item['id'] == d.unit_type, UNIT_TYPE))[0]['name'],
                }
            )
        res['col_values'] = col_values

        resp.media = {
            'response': res
        }

    async def on_post(self, req, resp):

        response = dict()
        data = await req.media()
        dest_name = data.get('values[dest_name]')
        item_name = data.get('values[item_name]')
        cost = data.get('values[cost]')
        unit_type = data.get('values[unit_type]')

        # 何も入力されていない場合
        if dest_name is None:
            resp.media = 'dest_name not entered'
            resp.status_code = api.status_codes.HTTP_400
            return
        if item_name is None:
            resp.media = 'item_name not entered'
            resp.status_code = api.status_codes.HTTP_400
            return
        if cost is None:
            resp.media = 'cost not entered'
            resp.status_code = api.status_codes.HTTP_400
            return
        if unit_type is None:
            resp.media = 'unit_type not entered'
            resp.status_code = api.status_codes.HTTP_400
            return

        v = TrashMaster(dest_name, item_name, cost, unit_type)

        # DBに登録
        try:
            db.session.add(v)
            db.session.commit()
        except Exception as e:
            print(type(e))
            print('db error')
            resp.status_code = api.status_codes.HTTP_500
            raise
        finally:
            db.session.close()

        # 発番されたidを取得
        new_id = db.session.query(func.max(TrashMaster.id)).scalar()
        db.session.close()
        response['new_id'] = new_id

        resp.status_code = api.status_codes.HTTP_200
        resp.media = response

    async def on_delete(self, req, resp):

        data = await req.media()
        id = data.get('id')

        if id is None:
            print('no id')
            resp.status_code = api.status_codes.HTTP_500
            return

        # 削除対象のデータを検索
        staff = db.session.query(TrashMaster).filter_by(id=id).first()

        # 指定したデータを削除
        try:
            db.session.delete(staff)
            db.session.commit()
        except Exception as e:
            print(type(e))
            print('db error')
            resp.status_code = api.status_codes.HTTP_500
            raise
        finally:
            db.session.close()


# view #####################################
@api.route("/home")
class Home():
    async def on_get(self, req, resp):

        param = dict()
        resp.html = api.template('home.html', param)


@api.route("/invalid")
class Error403View():
    async def on_get(self, req, resp):
        resp.html = api.template('invalid.html')


@api.route("/daily_report/top")
class DailyReportMenu():
    async def on_get(self, req, resp, *args, **kwargs):

        logger.debug('enter daily_report top')

        cookies = req.cookies
        decode_token = validate_token(cookies.get('token'))
        # chromeの仕様で、デフォルトの301リダイレクトだと、キャッシュされてしまう。
        # 「リダイレクトキャッシュ」で、一度リダイレクトすると、以降キャッシュした
        # リダイレクトさきにダイレクトに飛ばされるようになる。
        # 301は"permanent"なので、条件によってリダイレクト先が変わらない場合に使うべきか。
        # 使う場面としては、サイトが移動した場合など？
        if decode_token is None:
            resp.headers["Cache-Control"] = "no-store, max_age=0, must-revalidate"
            api.redirect(resp, '/invalid',
                         status_code=api.status_codes.HTTP_302)
            return

        param = dict()

        staffs = db.session.query(StaffMaster).all()
        cars = db.session.query(CarMaster).all()
        machines = db.session.query(MachineMaster).all()
        leases = db.session.query(LeaseMaster).all()
        dests = db.session.query(DestMaster).all()
        items = db.session.query(ItemMaster).all()
        customers = db.session.query(CustomerMaster).all()
        worksite_names = db.session.query(
            ReportHead.worksite_name
        ).filter_by(
            completed_date=None
        ).all()
        db.session.close()

        param['staffs'] = list(x._to_dict() for x in staffs)
        param['cars'] = list(x._to_dict() for x in cars)
        param['machines'] = list(x._to_dict() for x in machines)
        param['leases'] = list(x._to_dict() for x in leases)
        param['dests'] = list(x._to_dict() for x in dests)
        param['items'] = list(x._to_dict() for x in items)
        param['customers'] = list(x.name for x in customers)
        param['worksite_names'] = list(x.worksite_name for x in worksite_names)
        param['unit_type'] = UNIT_TYPE

        resp.html = api.template('daily_report_top.html', param)


@api.route("/daily_report/{work_name}/{date}")
class DailyReportInfo():
    """日報を更新・登録するAPI。
        工事日・工事名で日報ヘッドを検索し、登録済の日報であれば、
        delete&insertを行う。
        新規の工事については、日報ヘッド情報もここで登録する。
    """
    async def on_get(self, req, resp, *args, **kwargs):

        cookies = req.cookies
        decode_token = validate_token(cookies.get('token'))
        # chromeの仕様で、デフォルトの301リダイレクトだと、キャッシュされてしまう。
        # 「リダイレクトキャッシュ」で、一度リダイレクトすると、以降キャッシュした
        # リダイレクトさきにダイレクトに飛ばされるようになる。
        # 301は"permanent"なので、条件によってリダイレクト先が変わらない場合に使うべきか。
        # 使う場面としては、サイトが移動した場合など？
        if decode_token is None:
            resp.headers["Cache-Control"] = "no-store, max_age=0, must-revalidate"
            api.redirect(resp, '/invalid',
                         status_code=api.status_codes.HTTP_302)
            return

        response = dict()
        worksite_name = kwargs['work_name']
        head = db.session.query(
            ReportHead
        ).filter_by(
            worksite_name=worksite_name,
        ).first()
        if head is None:
            resp.status_code = api.status_codes.HTTP_404
            return

        response['head'] = head._to_dict()

        detail = db.session.query(ReportDetail).filter_by(
            report_head_id=head.id,
            work_date=kwargs['date']
        ).all()

        for d in detail:
            if ItemType.value_of(d.type).name in response:
                response[ItemType.value_of(d.type).name].append(d._to_dict())
            else:
                response[ItemType.value_of(d.type).name] = [d._to_dict()]

        db.session.close()
        resp.media = response

    async def on_post(self, req, resp, *args, **kwargs):

        data = await req.media()
        customer = data.get('head[customer]')
        address = data.get('head[address]')
        memo = data.get('head[memo]')
        work_name = kwargs['work_name']
        work_date = kwargs['date']
        staff = json.loads(data.get('staff'))
        car = json.loads(data.get('car'))
        lease = json.loads(data.get('lease'))
        machine = json.loads(data.get('machine'))
        transport = json.loads(data.get('transport'))
        valuable = json.loads(data.get('valuable'))
        other = json.loads(data.get('other'))
        trash = json.loads(data.get('trash'))

        if ensure_str(work_name) is None:
            resp.status_code = api.status_codes.HTTP_400

        # 登録済みチェック
        d = db.session.query(ReportHead
                             ).filter_by(worksite_name=work_name).first()
        if d is None:
            v = ReportHead(customer, work_name, address, memo, None)

            # DBに登録
            try:
                db.session.add(v)
                db.session.commit()
            except Exception as e:
                print(type(e))
                print('db error')
                resp.status_code = api.status_codes.HTTP_500
                raise
            finally:
                db.session.close()

            # 発番されたidを取得
            id = db.session.query(func.max(ReportHead.id)).scalar()
        else:

            if ensure_str(work_date) is None:
                resp.status_code = api.status_codes.HTTP_400

            id = d.id
            d.customer_name = customer
            d.address = address
            d.memo = memo

            db.session.query(
                ReportDetail
            ).filter_by(
                report_head_id=id,
                work_date=work_date,
            ).delete()

        v = list()
        v += [ReportDetail(id, work_date, ItemType.STAFF.value, name, cost, 1) for name, cost in staff.items()]
        v += [ReportDetail(id, work_date, ItemType.CAR.value, d['name'], d['cost'], d['quant']) for d in car]
        v += [ReportDetail(id, work_date, ItemType.MACHINE.value, d['name'], d['cost'], d['quant']) for d in machine]
        v += [ReportDetail(id, work_date, ItemType.LEASE.value, d['name'], d['cost'], d['quant']) for d in lease]
        v += [ReportDetail(id, work_date, ItemType.TRANSPORT.value, d['name'], d['cost'], d['quant']) for d in transport]
        v += [ReportDetail(id, work_date, ItemType.TRASH.value, d['item'], d['cost'], d['quant'], d['dest'], d['unit_type']) for d in trash]
        v += [ReportDetail(id, work_date, ItemType.VALUABLE.value, d['name'], d['cost'], d['quant']) for d in valuable]
        v += [ReportDetail(id, work_date, ItemType.OTHER.value, d['name'], d['cost'], d['quant']) for d in other]

        try:
            db.session.add_all(v)
        except Exception as e:
            print(type(e))
            print('db update failed')
            resp.status_code = api.status_codes.HTTP_500
            db.session.close()
            raise

        db.session.commit()
        db.session.close()

        resp.status_code = api.status_codes.HTTP_202
        resp.media = {"param": "aaa"}


@api.route("/summary")
class DailyReportSummaryView():
    async def on_get(self, req, resp):

        param = dict()
        head = db.session.query(ReportHead).all()
        param['worksite_names'] = list({'id': x.id, 'name': x.worksite_name} for x in head)
        db.session.close()
        resp.html = api.template('daily_report_summary.html', param)


@api.route("/summary/{workId}")
class DailyReportSummaryById():
    async def on_get(self, req, resp, *args, **kwargs):

        work_id = kwargs['workId']

        head = db.session.query(
            ReportHead
        ).filter_by(
            id=work_id
        ).first()

        db_data = db.session.query(
            ReportDetail.work_date,
            ReportDetail.type,
            func.sum(ReportDetail.quant),
            func.sum(ReportDetail.quant*ReportDetail.cost),
        ).filter_by(
            report_head_id=work_id
        ).group_by(
            ReportDetail.type,
            ReportDetail.work_date,
        ).order_by(
            ReportDetail.work_date,
        )
        db.session.close()

        details = list()
        for date, type, q, total in db_data:
            d = {
                "date": date,
                "type": type,
                "quant": q,
                "total": total
            }
            details.append(d)

        resp.media = {
            'head': head._to_dict(),
            'details': details
        }


@api.route("/master/top")
class MasterMentenanceMenu():
    async def on_get(self, req, resp):

        param = dict()
        param['menu'] = {
            'staff': {
                'menu_name': '人員'
            },
            'car': {
                'menu_name': '車両'
            },
            'lease': {
                'menu_name': 'リース'
            },
            'machine': {
                'menu_name': '重機'
            },
            'trash': {
                'menu_name': '廃材処分費'
            },
            'customer': {
                'menu_name': '受注先'
            },
            'dest': {
                'menu_name': '廃材処分先'
            },
            'items': {
                'menu_name': '廃材品目'
            },
            'work': {
                'menu_name': '工事進捗'
            },
        }

        resp.html = api.template('master_top.html', param)


@api.route("/sign_in")
class SignIn():
    async def on_post(self, req, resp):

        data = await req.media()
        id = data.get('id')
        pwd = data.get('pwd')

        hashed_pwd = hashlib.sha256(pwd.encode()).hexdigest()

        try:
            user = db.session.query(User).filter_by(user_id=id, user_pwd=hashed_pwd).first()
        except Exception as e:
            print(type(e))
            db.session.close()
            raise

        if user is None:
            resp.status_code = api.status_codes.HTTP_404
            resp.media = {'message': 'login failed'}
            return

        content = {}
        content["id"] = id
        content["name"] = user.user_name if user.user_name is not None else ""
        # token = jwt.encode({'key': 'value'}, 'secret', algorithm='HS256')
        token = jwt.encode(content, JWT_KEY, algorithm="HS256")

        user.token = token
        user.token_expire_dtime = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(minutes=TOKEN_EXPIRE_MINUTES)
        db.session.commit()
        # db.session.close() はしない。エラーになる。
        resp.status_code = api.status_codes.HTTP_200
        # ログイン時キャッシュクリアする。
        # tokenの有効期限切れ後各ページにアクセスするとログインページにリダイレクトするが、
        # 一度これでリダイレクトすると、ログイン後に有効なtokenでアクセスしようとしても、
        # キャッシュした情報（＝ログインページにリダイレクト）が返されてしまうなど。
        resp.headers["Cache-Control"] = "no-store, max_age=0, must-revalidate"
        resp.media = {
            'auth_type': user.auth_type,
            'token': token,
        }
        # api.redirect(resp, '/home')


@api.route("/sign_out")
class SignOut():
    async def on_post(self, req, resp):

        cookies = req.cookies
        decode_token = validate_token(cookies.get('token'))
        if decode_token is None:
            # 正当なtokenを持たない者によるサインアウトは処理しない。
            # 正規のクライアントが作業中の可能性があるため。
            resp.status_code = api.status_codes.HTTP_403
            api.redirect(resp, '/invalid', 
                         status_code=api.status_codes.HTTP_302)
            return

        try:
            user = db.session.query(User).filter_by(user_id=decode_token['id']).first()
        except Exception as e:
            print(type(e))
            db.session.close()
            raise

        if user is None:
            return

        user.token = ''
        user.token_expire_dtime = datetime.datetime(year=2000, month=1, day=1, tzinfo=datetime.timezone.utc)
        db.session.commit()
        # db.session.close() はしない。エラーになる。
        resp.status_code = api.status_codes.HTTP_200


@api.route("/sign_up")
class SignUp():

    async def on_get(self, req, resp):

        resp.html = api.template('sign_up.html')

    async def on_post(self, req, resp):

        data = await req.media()
        id = data.get('id')
        pwd = data.get('pwd')
        name_last = data.get('name_last', '')
        name_first = data.get('name_first', '')

        if name_first is None and name_last is None:
            name_first = '名無し'

        # 何も入力されていない場合
        resp.status_code = api.status_codes.HTTP_400
        if id is None:
            resp.media = 'id not entered'
            return
        if pwd is None:
            resp.media = 'pwd not entered'
            return

        # 登録済みチェック
        d = db.session.query(User).filter_by(user_id=id).first()
        if d is not None:
            resp.media = {'message': '入力されたIDは、すでに登録済みです'}
            resp.status_code = api.status_codes.HTTP_500
            return

        hashed_pwd = hashlib.sha256(pwd.encode()).hexdigest()

        # ユーザを作成
        admin = User(id, hashed_pwd, f'{name_last} {name_first}')
        db.session.add(admin)
        db.session.commit()
        db.session.close()

        resp.status_code = api.status_codes.HTTP_200


@api.route("/")
async def login(req, resp, *args, **kwargs):
    resp.html = api.template('index.html')

if __name__ == '__main__':

    with open('setting.json', encoding="utf-8") as f:
        data = json.load(f)

    api.run(address=data['ip_adress'], port=data['port'])
