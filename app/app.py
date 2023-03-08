from pathlib import Path
import hashlib
import responder
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
)
import db_common as db
import jwt
from sqlalchemy.sql.expression import func

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
)


# util #####################################
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


@api.route("/daily_report/top")
class DailyReportMenu():
    async def on_get(self, req, resp):

        data = req.params
        if data.get('token') is None or data.get('token') == '':
            resp.status_code = api.status_codes.HTTP_400
            return

        param = dict()

        staffs = db.session.query(StaffMaster).all()
        cars = db.session.query(CarMaster).all()
        machines = db.session.query(MachineMaster).all()
        leases = db.session.query(LeaseMaster).all()
        dests = db.session.query(DestMaster).all()
        items = db.session.query(ItemMaster).all()
        db.session.close()

        param['staffs'] = list(x._to_dict() for x in staffs)
        param['cars'] = list(x._to_dict() for x in cars)
        param['machines'] = list(x._to_dict() for x in machines)
        param['leases'] = list(x._to_dict() for x in leases)
        param['dests'] = list(x._to_dict() for x in dests)
        param['items'] = list(x._to_dict() for x in items)
        param['unit_type'] = UNIT_TYPE

        resp.html = api.template('daily_report_top.html', param)


@api.route("/summary")
class DailyReportSummary():
    async def on_get(self, req, resp):

        param = dict()
        resp.html = api.template('daily_report_summary.html', param)


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
            raise
        finally:
            db.session.close()

        if user is None:
            resp.status_code = api.status_codes.HTTP_404
            resp.media = {'message': 'login failed'}
            return

        key = "secret"
        content = {}
        content["id"] = id
        content["name"] = user.user_name if user.user_name is not None else ""
        # token = jwt.encode({'key': 'value'}, 'secret', algorithm='HS256')
        token = jwt.encode(content, key, algorithm="HS256")
        resp.status_code = api.status_codes.HTTP_200
        resp.media = {
            'auth_type': user.auth_type,
            'token': token,
        }
        # api.redirect(resp, '/home')


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

    api.run(address='localhost', port=8080)
