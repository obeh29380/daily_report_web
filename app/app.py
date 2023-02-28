from pathlib import Path
import json
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


api = responder.API(
    static_dir=str(BASE_DIR.joinpath('static')),
    templates_dir=str(BASE_DIR.joinpath('templates')),
)


# util #####################################
@api.route("/master/staff")
class StaffMasterInfo():

    async def on_get(self, req, resp):

        staffs = db.session.query(StaffMaster.id, StaffMaster.name, StaffMaster.cost)
        db.session.close()

        res = list()
        for staff in staffs:
            res.append(
                {
                   'id': staff.id,
                   'name': staff.name,
                   'cost': staff.cost
                }
            )

        resp.media = {
            'response': res
        }

    async def on_post(self, req, resp):

        response = dict()
        data = await req.media()
        name = data.get('values[name]')
        cost = data.get('values[cost]')

        # もし何も入力されていない場合
        if name is None:
            resp.media = 'name not entered'
            resp.status_code = api.status_codes.HTTP_400
            return
        if cost is None:
            resp.media = 'cost not entered'
            resp.status_code = api.status_codes.HTTP_400
            return

        v = StaffMaster(name, cost)

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

        res = list()
        for d in db_data:
            res.append(
                {
                   'id': d.id,
                   'name': d.name,
                   'cost': d.cost
                }
            )

        resp.media = {
            'response': res
        }

    async def on_post(self, req, resp):

        response = dict()
        data = await req.media()
        name = data.get('values[name]')
        cost = data.get('values[cost]')

        # もし何も入力されていない場合
        if name is None:
            resp.media = 'name not entered'
            resp.status_code = api.status_codes.HTTP_400
            return
        if cost is None:
            resp.media = 'cost not entered'
            resp.status_code = api.status_codes.HTTP_400
            return

        v = CarMaster(name, cost)

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

        res = list()
        for d in db_data:
            res.append(
                {
                   'id': d.id,
                   'name': d.name,
                   'cost': d.cost
                }
            )

        resp.media = {
            'response': res
        }

    async def on_post(self, req, resp):

        response = dict()
        data = await req.media()
        name = data.get('values[name]')
        cost = data.get('values[cost]')

        # もし何も入力されていない場合
        if name is None:
            resp.media = 'name not entered'
            resp.status_code = api.status_codes.HTTP_400
            return
        if cost is None:
            resp.media = 'cost not entered'
            resp.status_code = api.status_codes.HTTP_400
            return

        v = LeaseMaster(name, cost)

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

        res = list()
        for d in db_data:
            res.append(
                {
                   'id': d.id,
                   'name': d.name,
                   'cost': d.cost
                }
            )

        resp.media = {
            'response': res
        }

    async def on_post(self, req, resp):

        response = dict()
        data = await req.media()
        name = data.get('values[name]')
        cost = data.get('values[cost]')

        # もし何も入力されていない場合
        if name is None:
            resp.media = 'name not entered'
            resp.status_code = api.status_codes.HTTP_400
            return
        if cost is None:
            resp.media = 'cost not entered'
            resp.status_code = api.status_codes.HTTP_400
            return

        v = MachineMaster(name, cost)

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

# view #####################################
@api.route("/home")
class Home():
    async def on_get(self, req, resp):

        param = dict()
        resp.html = api.template('home.html', param)


@api.route("/daily_report/top")
class DailyReportMenu():
    async def on_get(self, req, resp):

        param = dict()
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

        try:
            users = db.session.query(User.user_id, User.user_pwd, User.auth_type)
        except Exception as e:
            print(type(e))
            raise
        finally:
            db.session.close()

        auth_type = None
        for user in users:
            if user.user_id == id and user.user_pwd == pwd:
                auth_type = user.auth_type
                break

        if auth_type is None:
            resp.status_code = api.status_codes.HTTP_404
            resp.media = {'message': 'login failed'}
            return

        key = "secret"
        content = {}
        content["id"] = id
        # token = jwt.encode({'key': 'value'}, 'secret', algorithm='HS256')
        token = jwt.encode(content, key, algorithm="HS256")
        resp.status_code = api.status_codes.HTTP_200
        resp.media = {
            'auth_type': auth_type,
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
        name_last = data.get('name_last')
        name_first = data.get('name_first')

        # もし何も入力されていない場合
        resp.status_code = api.status_codes.HTTP_400
        if id is None:
            resp.media = 'id not entered'
            return
        if pwd is None:
            resp.media = 'pwd not entered'
            return
        if name_last is None:
            resp.media = 'name_last not entered'
            return
        if name_first is None:
            resp.media = 'name_first not entered'
            return

        # adminユーザを作成
        admin = User(id, pwd, f'{name_last} {name_first}')
        db.session.add(admin)
        db.session.commit()
        db.session.close()

        resp.status_code = api.status_codes.HTTP_200


@api.route("/")
async def login(req, resp, *args, **kwargs):
    resp.html = api.template('login.html')

if __name__ == '__main__':

    api.run(address='localhost', port=8080)
