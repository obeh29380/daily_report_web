from pathlib import Path
import json
import responder
from models import User, StaffMaster
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

        #data = await req.media()

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
        table = data.get('table')
        name = data.get('values[name]')
        cost = data.get('values[cost]')

        # もし何も入力されていない場合
        if table is None:
            resp.media = 'table not entered'
            resp.status_code = api.status_codes.HTTP_400
            return
        if name is None:
            resp.media = 'name not entered'
            resp.status_code = api.status_codes.HTTP_400
            return
        if cost is None:
            resp.media = 'cost not entered'
            resp.status_code = api.status_codes.HTTP_400
            return

        if table == 'staff':
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
        staff = db.session.query(StaffMaster).filter_by(id=id).first()

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
        param['BASE_DIR'] = BASE_DIR
        resp.html = api.template('home.html', param)


@api.route("/daily_report/top")
class DailyReportMenu():
    async def on_get(self, req, resp):

        param = dict()
        param['BASE_DIR'] = BASE_DIR
        resp.html = api.template('daily_report_top.html', param)


@api.route("/summary")
class DailyReportSummary():
    async def on_get(self, req, resp):

        param = dict()
        param['BASE_DIR'] = BASE_DIR
        resp.html = api.template('daily_report_summary.html', param)


@api.route("/master/top")
class MasterMentenanceMenu():
    async def on_get(self, req, resp):

        param = dict()
        param['BASE_DIR'] = BASE_DIR
        resp.html = api.template('master_top.html', param)


@api.route("/sign_in")
class SignIn():
    async def on_post(self, req, resp):

        data = await req.media()
        id = data.get('id')
        pwd = data.get('pwd')

        users = db.session.query(User.user_id, User.user_pwd, User.auth_type)
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
