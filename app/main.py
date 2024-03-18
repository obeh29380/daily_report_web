import datetime
import hashlib
import logging
import os
from typing import (
    Union,
)

from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    Request,
    Response,
    status,
    File,
    UploadFile,
)
from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError
from fastapi.exceptions import RequestValidationError
from fastapi.responses import (
    JSONResponse,
    HTMLResponse,
)
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from functools import wraps
from jose.exceptions import JWTError
from sqlalchemy import (
    func,
    select,
)
from sqlalchemy.exc import (
    NoResultFound,
)
from sqlalchemy.orm import Session
from sqlalchemy.sql import exists

from db_common import get_engine
from tables import (
    Account,
    CarMaster,
    CustomerMaster,
    DestMaster,
    ItemMaster,
    LeaseMaster,
    MachineMaster,
    ReportHead,
    ReportDetail,
    StaffMaster,
    TrashMaster,
    User,
)
from schemas import (
    AccountModel,
    CompleteReport,
    CsrfSettings,
    DeleteTarget,
    ItemType,
    MasterParams,
    MAP_MASTER,
    NewUser,
    Report,
    Token,
    UNIT_TYPE,
    UserInvitation,
)
from app_utils import (
    authenticate_user,
    create_access_token,
    ensure_str,
    get_decoded_token,
    get_master_data,
    get_password_hash,
    validate_token,
    random_str,
    save_uploaded_file,
    get_hashed_file_name,
    get_account_logo,
)


"""全体の方針メモ
- テンプレートを返す部分はAccount関係なく返せばよい。
- 中のデータをとるときに、Accountで分ける。

- ひとまずAccount無視したログインは、ゲストアカウント扱いとする。
- この状態でできるのは、Accountの作成と、データのない画面表示のみ。
- このゲストユーザのaccount_uuid = 0 とする（auto_incrementが1からなので空いている）

- DBのnameのunique制約は、Account単位にする

- csrf対策
https://www.stackhawk.com/blog/csrf-protection-in-fastapi/
https://github.com/aekasitt/fastapi-csrf-protect
"""
app = FastAPI()
app.mount(path="/static", app=StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")
app.mount(path="/userdata", app=StaticFiles(directory=os.path.join(os.path.dirname(__file__), "userdata")), name="userdata")
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# ロゴの画像名用 これは固定にする（再起動時にまた登録が必要になってしまう）
LOGO_NAME_SALT = os.getenv('logo_name_salt', 'logo_salt')
ALGORITHM = "HS256"
ISS = os.getenv('iss', None)
USER_DEFAULT_FULLNAME = os.getenv('USER_DEFAULT_FULLNAME', None)
LOGO_DIR = os.path.join(os.path.dirname(__file__), "userdata", "images")
LOGO_DIR_ON_CLIENT = os.path.join("/userdata", "images")
LOGO_FILE_EXT = '.png'
token_exp = float(os.getenv('token_exp', 3600))
cookie_max_age = os.getenv('token_exp', 3600)

TOKEN_KEY_FILE = os.path.join(os.path.dirname(__file__), "token.key")
if os.path.isfile(TOKEN_KEY_FILE):
    with open(TOKEN_KEY_FILE, 'r') as f:
        token_key = f.read()
else:
    with open(TOKEN_KEY_FILE, 'w') as f:
        token_key = random_str(50)
        f.write(token_key)

# logger
logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "[%(levelname)s] %(asctime)s %(funcName)s %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

# bcrypt== のバグで、ワーニングが出る（動作には支障ない）ので、オフっておく
logging.getLogger('passlib').setLevel(logging.ERROR)


@CsrfProtect.load_config
def get_csrf_config():
  return CsrfSettings()


@app.exception_handler(RequestValidationError)
async def handler(request: Request, exc: RequestValidationError):
    print(exc)
    return JSONResponse(content={}, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.exception_handler(CsrfProtectError)
def csrf_protect_exception_handler(request: Request, exc: CsrfProtectError):
  return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


def auth_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        try:
            decoded_token = get_decoded_token(
                kwargs['request'].cookies['token'], key=token_key)
        except JWTError as e:
            return templates.TemplateResponse(
                "invalid.html", {
                    "request": kwargs.get('request')
                },
                status_code=403
            )
        if decoded_token is None:
            return templates.TemplateResponse(
                "invalid.html", {
                    "request": kwargs.get('request')
                },
                status_code=403
            )
        return func(*args, **kwargs)
    return wrapper


@app.get("/", response_class=HTMLResponse)
def top_page(request: Request):
    return templates.TemplateResponse(
        "index.html", {
            "request": request
        }
    )


@app.get("/csrftoken/")
async def get_csrf_token(csrf_protect:CsrfProtect = Depends()):
	response = JSONResponse(status_code=200, content={'csrf_token':'cookie'})
	csrf_protect.set_csrf_cookie(response)
	return response


@app.post("/token/account/{account_id}")
async def login_for_access_token_with_account(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    account_id: Union[str, None] = None,
    csrf_protect: CsrfProtect = Depends(),
) -> JSONResponse:

    await csrf_protect.validate_csrf(request)
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ユーザ名かパスワードが正しくありません",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_uuid = user['id']
    user_name = user['fullname']

    with Session(get_engine()) as session:

        try:
            stmt = select(Account).where(Account.account_id == account_id)
            account = session.scalars(stmt).one()
        except NoResultFound:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="未登録の会社IDです",
                headers={"WWW-Authenticate": "Bearer"},
            )

        account_uuid = account.id

        stmt = select(User).where(User.id == user_uuid)
        user = session.scalars(stmt).one()
        account_ids = []
        for user_account in user.accounts:
            account_ids.append(user_account.id)
        # if not session.query(exists().where(Account.id.in_(account_ids))).scalar():
        if account_uuid not in account_ids:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="指定された会社へのログイン許可がありません",
                headers={"WWW-Authenticate": "Bearer"},
            )

        account_name = account.fullname

    access_token = create_access_token(
        user_uuid=user_uuid, account_uuid=account_uuid, token_key=token_key, exp_seconds=token_exp
    )
    token = Token(access_token=access_token, token_type="bearer")
    response = JSONResponse(content=dict(user_name=user_name, account_name=account_name))
    response.set_cookie(key="token", value=access_token, samesite='strict')
    response.set_cookie(key="account_uuid", value=account_uuid, samesite='strict')
    csrf_protect.unset_csrf_cookie(response)

    return response


@app.post("/token")
async def login_for_access_token(
    request: Request,
    csrf_protect: CsrfProtect = Depends(),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> JSONResponse:
    
    await csrf_protect.validate_csrf(request)

    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        user_uuid=user['id'], token_key=token_key, exp_seconds=token_exp
    )
    token = Token(access_token=access_token, token_type="bearer")
    response = JSONResponse(content=dict(user_name=user['fullname']))
    response.set_cookie(key="token", value=access_token, samesite='strict')
    # response.set_cookie(key="user_name", value=user['fullname'], samesite='strict')
    csrf_protect.unset_csrf_cookie(response)
    return response


@app.get("/sign_in", response_class=HTMLResponse)
def sign_in_page(request: Request, csrf_protect: CsrfProtect = Depends()):

    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    response = templates.TemplateResponse(
        "sign_in.html", {
            "request": request,
            "csrf_token": csrf_token,
        }
    )
    csrf_protect.set_csrf_cookie(signed_token, response)
    return response


@app.get("/sign_up", response_class=HTMLResponse)
def sign_up_page(request: Request, csrf_protect: CsrfProtect = Depends()):

    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    response = templates.TemplateResponse(
        "sign_up.html", {
            "request": request,
            "csrf_token": csrf_token,
        }
    )
    csrf_protect.set_csrf_cookie(signed_token, response)
    return response


@app.get("/user/{user_id}")
async def get_user_info(request: Request, user_id: str):

    with Session(get_engine()) as session:

        # 登録済みチェック
        try:
            user = session.scalars(
                select(
                    User
                ).where(
                    User.user_id == user_id
                )
            ).one()
        except NoResultFound:
            return Response(status_code=404)

    return JSONResponse(status_code=200, content=dict(user=user.to_dict_nopass()))


@app.post("/user/create")
async def create_user(request: Request, new_user: NewUser, csrf_protect: CsrfProtect = Depends()):

    await csrf_protect.validate_csrf(request)
    fullname = ensure_str(new_user.name_last, "") + ensure_str(new_user.name_first, "")
    if fullname is None or fullname == "":
        fullname = USER_DEFAULT_FULLNAME

    with Session(get_engine()) as session:

        # 登録済みチェック
        if session.query(exists().where(User.user_id == new_user.username)).scalar():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="そのユーザ名はすでに使用されています",
            )

        # hashed_pwd = hashlib.sha256(pwd.encode()).hexdigest()
        hashed_pwd = get_password_hash(new_user.password)
        user = User(
            user_id=new_user.username,
            user_pwd=hashed_pwd,
            fullname=fullname,
        )

        try:
            session.add_all([user])
            session.commit()
        except Exception as e:
            print(type(e))
            session.rollback()
            raise e

    return JSONResponse(status_code=201, content=dict(detail='succeeded'))


@app.post("/sign_out")
async def sign_out(request: Request, response: Response, csrf_protect: CsrfProtect = Depends()):

    await csrf_protect.validate_csrf(request)
    token = get_decoded_token(request.cookies['token'], key=token_key)

    if token is None:
        Response(status_code=403)

    response.delete_cookie(key="token")
    response.delete_cookie(key="account_name")
    response.delete_cookie(key="account_id")

    # return RedirectResponse('/home', 303)
    return JSONResponse(content={'dummy': 'dummy'})


@app.get("/home", response_class=HTMLResponse)
@auth_required
def home_page(request: Request, csrf_protect: CsrfProtect = Depends()):

    decoded_token = get_decoded_token(
        request.cookies.get('token'), key=token_key)

    if decoded_token is None:
        # return Response(status_code=403)
        return templates.TemplateResponse(
            "invalid.html", {
                "request": request
            },
            status_code=403
        )
    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    response = templates.TemplateResponse(
        "home.html", {
            "request": request,
            "csrf_token": csrf_token,
        }
    )
    csrf_protect.set_csrf_cookie(signed_token, response)
    return response


@app.get("/account", response_class=HTMLResponse)
@auth_required
def account_register_page(request: Request, csrf_protect: CsrfProtect = Depends()):

    decoded_token = get_decoded_token(
        request.cookies.get('token'), key=token_key)

    if decoded_token is None:
        return templates.TemplateResponse(
            "invalid.html", {
                "request": request
            },
            status_code=403
        )

    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    response = templates.TemplateResponse(
        "account_register.html", {
            "request": request,
            "csrf_token": csrf_token,
        }
    )
    csrf_protect.set_csrf_cookie(signed_token, response)
    return response


@app.get("/account/{account_uuid}/setting", response_class=HTMLResponse)
@auth_required
def account_setting_page(request: Request, account_uuid: int, csrf_protect: CsrfProtect = Depends()):

    decoded_token = get_decoded_token(
        request.cookies.get('token'), key=token_key)
    
    token = validate_token(decoded_token, ['account_uuid'])

    if decoded_token is None:
        return templates.TemplateResponse(
            "invalid.html", {
                "request": request
            },
            status_code=403
        )

    # TODO 自分が管理権限を持つアカウントを全て返す対応
    res_users = list()
    with Session(get_engine()) as session:
        try:
            account = session.scalars(
                select(
                    Account
                ).where(
                    Account.id == decoded_token['account_uuid']
                )
            ).one()

            for user in account.users:
                res_users.append(user.to_dict_nopass())

        except NoResultFound as e:
            pass

    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    response = templates.TemplateResponse(
        "account_setting.html", {
            "request": request,
            "users": res_users,
            "csrf_token": csrf_token,
        }
    )
    csrf_protect.set_csrf_cookie(signed_token, response)
    return response


@app.post("/account/{account_id}")
# @auth_required # うまく動かないので後回し
async def add_account(request: Request, account_id: str, account: AccountModel, csrf_protect: CsrfProtect = Depends()):

    await csrf_protect.validate_csrf(request)
    token = get_decoded_token(
        request.cookies['token'], key=token_key, algorithms=ALGORITHM)

    if token is None:
        Response(status_code=403)

    with Session(get_engine()) as session:
        # 登録済みチェック
        if session.query(exists().where(Account.account_id == account_id)).scalar():
            return JSONResponse(status_code=409, content=dict(detail='すでに使用されているIDです'))

        data = Account(
            account_id=account_id,
            account_pwd=hashlib.sha256(account.pwd.encode()).hexdigest(),
            fullname=account.name
        )
        session.add(data)
        # 登録者を初期ユーザとして登録
        stmt = select(User).where(User.id == token['sub'])
        try:
            user = session.scalars(stmt).one()
        except NoResultFound:
            return Response(status_code=403)
        data.users = [user]
        session.commit()

    return JSONResponse(status_code=200, content={'dummy': 'dummy'})


@app.get("/account/{account_uuid}/account_logo")
def get_account_users(request: Request, account_uuid: int):

    decoded_token = get_decoded_token(
        request.cookies.get('token'), key=token_key)

    if decoded_token is None:
        Response(status_code=403)
    
    token = validate_token(decoded_token, ['account_uuid'])
    if token is None or account_uuid != token['account_uuid']:
        return Response(status_code=403)
    
    file_name = get_account_logo(account_uuid)
    if file_name is None:
        return Response(status_code=404)

    file_path = os.path.join(LOGO_DIR, 'account', file_name+LOGO_FILE_EXT)
    file_path_rtn = os.path.join(LOGO_DIR_ON_CLIENT, 'account', file_name+LOGO_FILE_EXT)

    if not os.path.exists(file_path):
        return Response(status_code=404)

    # return FileResponse(file_path, )
    return Response(content=file_path_rtn, media_type="/image/png")


@app.post("/account/{account_uuid}/user/add")
# @auth_required # うまく動かないので後回し
async def add_user_to_account(request: Request, account_uuid: int, user_in: UserInvitation, csrf_protect: CsrfProtect = Depends()):

    await csrf_protect.validate_csrf(request)
    token = get_decoded_token(
        request.cookies['token'], key=token_key, algorithms=ALGORITHM)

    if token is None:
        Response(status_code=403)
    token = validate_token(token, ['account_uuid'])

    with Session(get_engine()) as session:
        user = session.scalars(
            select(
                User
            ).where(
                User.id == user_in.uuid
            )
        ).one()

        account = session.scalars(
            select(
                Account
            ).where(
                Account.id == account_uuid
            )
        ).one()

        for account_user in account.users:
            if account_user == user:
                return JSONResponse(status_code=409, content=dict(detail='登録済み'))

        account.users.append(user)
        session.commit()

    return JSONResponse(status_code=200, content={'dummy': 'dummy'})


@app.post("/account/{account_uuid}/profimage")
async def upload_account_logo(account_uuid: int,
                             request: Request,
                             file: UploadFile,
                             csrf_protect: CsrfProtect = Depends()
                             ):

    await csrf_protect.validate_csrf(request)
    token = get_decoded_token(
        request.cookies['token'], key=token_key, algorithms=ALGORITHM)
    if token is None:
        Response(status_code=403)

    token = validate_token(token, ['account_uuid'])
    if token['account_uuid'] != account_uuid:
        Response(status_code=403)

    file_name = get_hashed_file_name(str(account_uuid), LOGO_NAME_SALT)
    save_path = os.path.join(LOGO_DIR, 'account', file_name)
    save_uploaded_file(file, save_path + LOGO_FILE_EXT)

    with Session(get_engine()) as session:
        stmt = select(Account).where(Account.id == account_uuid)
        d = session.scalars(stmt).one()
        d.logo_name = file_name
        session.commit()

    return {"filename": file.filename}


# -- master
@app.get("/master/top", response_class=HTMLResponse)
@auth_required
def master_top_page(request: Request, csrf_protect: CsrfProtect = Depends()):

    decoded_token = get_decoded_token(
        request.cookies.get('token'), key=token_key)

    if decoded_token is None:
        # return Response(status_code=403)
        return templates.TemplateResponse(
            "invalid.html", {
                "request": request
            },
            status_code=403
        )

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
        'item': {
            'menu_name': '廃材品目'
        },
        'work': {
            'menu_name': '工事進捗'
        },
    }
    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    response = templates.TemplateResponse(
        "master_top.html", {
            "request": request,
            "menu": param['menu'],
            "csrf_token": csrf_token,
        }
    )
    csrf_protect.set_csrf_cookie(signed_token, response)
    return response


# == Master 品目＆費用 のもの以外は追加処理が必要


@app.get("/master/{master_type}")
@auth_required
def get_master(request: Request, master_type):

    token = get_decoded_token(request.cookies['token'], key=token_key)
    token = validate_token(token)

    with Session(get_engine()) as session:
        stmt = select(MAP_MASTER[master_type]).where(
            MAP_MASTER[master_type].account_id == token['account_uuid'])
        db_data = session.scalars(stmt)
        data = get_master_data(db_data, master_type,
                               account_id=token['account_uuid'])

    return JSONResponse(content=data)


@app.post("/master/{master_type}")
# @auth_required # うまく動かないので後回し
async def add_master(request: Request, params: MasterParams, master_type, csrf_protect: CsrfProtect = Depends()):
    """
    TODO API仕様を見ても、各マスターのparamはわからない。マスタ毎のIFに分けるべき。
    現状は、ブラウザから利用する前提とする。
    """

    await csrf_protect.validate_csrf(request)
    token = get_decoded_token(request.cookies['token'], key=token_key)
    token = validate_token(token, ['account_uuid'])

    register_data = params.params
    register_data['account_id'] = token['account_uuid']
    new = MAP_MASTER[master_type](
        **register_data
    )
    with Session(get_engine()) as session:
        if master_type not in ['trash']:
            if session.query(exists().where(MAP_MASTER[master_type].name == register_data['name']).where(MAP_MASTER[master_type].account_id == token['account_uuid'])).scalar():
                return JSONResponse(status_code=409, content=dict(detail='登録済みです。'))
        session.add(new)
        session.commit()
        new_id = new.id

    return JSONResponse(status_code=200, content={'new_id': new_id})


@app.delete("/master/{master_type}")
# @auth_required
async def delete_master(request: Request, target: DeleteTarget, master_type, csrf_protect: CsrfProtect = Depends()):

    await csrf_protect.validate_csrf(request)
    token = get_decoded_token(request.cookies['token'], key=token_key)
    token = validate_token(token, ['account_uuid'])

    stmt = select(MAP_MASTER[master_type]).where(
        MAP_MASTER[master_type].id == target.id)
    with Session(get_engine()) as session:
        try:
            data = session.scalars(stmt).one()
        except NoResultFound:
            return Response(status_code=404)

        session.delete(data)
        session.commit()

    return JSONResponse(status_code=200, content={'dummy': 'dummy'})


@app.post("/master/work/complete")
async def add_master(request: Request, report: CompleteReport, csrf_protect: CsrfProtect = Depends()):

    await csrf_protect.validate_csrf(request)
    token = get_decoded_token(request.cookies['token'], key=token_key)
    token = validate_token(token, ['account_uuid'])
    
    with Session(get_engine()) as session:
        try:
            data = session.scalars(
                select(
                    ReportHead
                ).where(
                    ReportHead.account_id == token['account_uuid']
                ).where(
                    ReportHead.id == report.id
                )
            ).one()
        except NoResultFound:
            return Response(status_code=404)
        
        data.completed_date = datetime.datetime.strptime(report.completed_date, '%Y-%m-%d') if report.completed_date else None
        session.commit()

    return Response(status_code=status.HTTP_200_OK)


@app.get("/master/trash/{dest_id}/{item_id}")
async def on_get(request: Request, dest_id: int, item_id: int):

    token = get_decoded_token(request.cookies['token'], key=token_key)
    token = validate_token(token, ['account_uuid'])

    stmt = select(TrashMaster
        ).where(TrashMaster.dest_id == dest_id
        ).where(TrashMaster.item_id == item_id)
    with Session(get_engine()) as session:
        try:
            d = session.scalars(stmt).one()
        except NoResultFound:
            return JSONResponse(
                content=dict(detail='Not registed'), status_code=204,
            )
        res = {
            'cost': d.cost,
            'unit_type': d.unit_type,
        }

    return JSONResponse(res, 200)


# report
@app.get("/daily_report/top", response_class=HTMLResponse)
async def daily_report_top_page(request: Request, csrf_protect: CsrfProtect = Depends()):

    token = get_decoded_token(request.cookies['token'], key=token_key)
    token = validate_token(token, ['account_uuid'])

    if token is None:
        # return Response(status_code=403)
        return templates.TemplateResponse(
            "invalid.html", {
                "request": request
            },
            status_code=403
        )

    param = dict()
    with Session(get_engine()) as session:

        staffs = session.scalars(select(StaffMaster).where(
                StaffMaster.account_id == token['account_uuid']))
        cars = session.scalars(select(CarMaster).where(
                CarMaster.account_id == token['account_uuid']))
        machines = session.scalars(select(MachineMaster).where(
                MachineMaster.account_id == token['account_uuid']))
        leases = session.scalars(select(LeaseMaster).where(
                LeaseMaster.account_id == token['account_uuid']))
        dests = session.scalars(select(DestMaster).where(
                DestMaster.account_id == token['account_uuid']))
        items = session.scalars(select(ItemMaster).where(
                ItemMaster.account_id == token['account_uuid']))
        customers = session.scalars(select(CustomerMaster).where(
                CustomerMaster.account_id == token['account_uuid']))
        worksite_names = session.scalars(
            select(
                ReportHead
            ).where(
                ReportHead.completed_date == None
            ).where(
                ReportHead.account_id == token['account_uuid']
            )
        )

        param['staffs'] = list(x.to_dict() for x in staffs)
        param['cars'] = list(x.to_dict() for x in cars)
        param['machines'] = list(x.to_dict() for x in machines)
        param['leases'] = list(x.to_dict() for x in leases)
        param['dests'] = list(x.to_dict() for x in dests)
        param['items'] = list(x.to_dict() for x in items)
        param['customers'] = list(x.to_dict()['name'] for x in customers)
        param['worksite_names'] = list(x.to_dict()['worksite_name'] for x in worksite_names)
        param['unit_type'] = UNIT_TYPE

        param['request'] = request
    
    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    param['csrf_token'] = csrf_token
    response = templates.TemplateResponse(
        "daily_report_top.html",
        param,
    )
    csrf_protect.set_csrf_cookie(signed_token, response)
    return response


@app.get("/daily_report/{work_name}/work_date/{work_date}")
async def get_daily_report(request: Request, work_name: str, work_date: str):

    token = get_decoded_token(request.cookies['token'], key=token_key)
    token = validate_token(token, ['account_uuid'])
    date = datetime.datetime.strptime(work_date, '%Y-%m-%d')

    content = dict()
    with Session(get_engine()) as session:

        try:
            head = session.scalars(
                select(
                    ReportHead
                ).where(
                    ReportHead.account_id == token['account_uuid']
                ).where(
                    ReportHead.worksite_name == work_name
                )
            ).one()
            content['head'] = head.to_dict()
            details = session.scalars(
                select(
                    ReportDetail
                ).where(
                    ReportDetail.report_head == head
                ).where(
                    ReportDetail.work_date == date
                ))
            l = list()
            for d in details:
                l.append(d.to_dict())

            content['detail'] = l
        except NoResultFound:
            # return JSONResponse(
            #     content=None, status_code=204,
            # )
            # 204を返す時は、contentに値を入れると"Too much data for declared Content-Length"エラーになる
            # これはHTTPの仕様だが、JSONResponseはcontentを空にするとエラーになるため、使用できない
            return Response(status_code=status.HTTP_204_NO_CONTENT)

        # date = datetime.datetime.strptime(work_date, '%Y-%m-%d')
        detail = session.scalars(select(ReportDetail).where(
            ReportDetail.report_head_id == head.id).where(
            ReportDetail.work_date == date
        ))
        for d in detail:
            if ItemType.value_of(d.type).name in content:
                content[ItemType.value_of(d.type).name].append(d.to_dict())
            else:
                content[ItemType.value_of(d.type).name] = [d.to_dict()]

    return JSONResponse(content=content)


@app.post("/daily_report/{work_name}/work_date/{work_date}")
async def register_daily_report(request: Request, work_name: str, work_date: str, report: Report, csrf_protect: CsrfProtect = Depends()):

    await csrf_protect.validate_csrf(request)
    token = get_decoded_token(request.cookies['token'], key=token_key)
    token = validate_token(token, ['account_uuid'])

    with Session(get_engine()) as session:

        try:
            head = session.scalars(
                select(
                    ReportHead
                ).where(
                    ReportHead.account_id == token['account_uuid']
                ).where(
                    ReportHead.worksite_name == work_name
                )
            ).one()

        except NoResultFound:
            # なければ登録
            head = ReportHead(
                customer_name=report.head['customer'],
                worksite_name=work_name,
                address=report.head['address'],
                memo=report.head['memo'],
                account_id=token['account_uuid'],
            )
            session.add(head)

        date = datetime.datetime.strptime(work_date, '%Y-%m-%d')
        detail_exists = True
        try:
            details = session.scalars(
                select(
                    ReportDetail
                ).where(
                    ReportDetail.report_head == head
                ).where(
                    ReportDetail.work_date == date
                )
            )
        except NoResultFound:
            detail_exists = False

        staff = report.detail.staffs
        car = report.detail.cars
        lease = report.detail.leases
        machine = report.detail.machines
        transport = report.detail.transports
        valuable = report.detail.valuables
        other = report.detail.others
        trash = report.detail.trashes

        # TODO とったやつまとめて消したい
        if detail_exists:
            for d in details:
                session.delete(d)

        new_details = list()
        new_details.extend(
            [ReportDetail(report_head=head, work_date=date, type=ItemType.STAFF.value, name=d.name, cost=d.cost, quant=d.quant) for d in staff]
        )
        new_details.extend(
            [ReportDetail(report_head=head, work_date=date, type=ItemType.CAR.value, name=d.name, cost=d.cost, quant=d.quant) for d in car]
        )
        new_details.extend(
            [ReportDetail(report_head=head, work_date=date, type=ItemType.MACHINE.value, name=d.name, cost=d.cost, quant=d.quant) for d in machine]
        )
        new_details.extend(
            [ReportDetail(report_head=head, work_date=date, type=ItemType.LEASE.value, name=d.name, cost=d.cost, quant=d.quant) for d in lease]
        )
        new_details.extend(
            [ReportDetail(report_head=head, work_date=date, type=ItemType.TRANSPORT.value, name=d.name, cost=d.cost, quant=d.quant) for d in transport]
        )
        new_details.extend(
            [ReportDetail(report_head=head, work_date=date, type=ItemType.TRASH.value, name=d.item, cost=d.cost, quant=d.quant, dest=d.dest, unit_type=d.unit_type) for d in trash]
        )
        new_details.extend(
            [ReportDetail(report_head=head, work_date=date, type=ItemType.VALUABLE.value, name=d.name, cost=d.cost, quant=d.quant) for d in valuable]
        )
        new_details.extend(
            [ReportDetail(report_head=head, work_date=date, type=ItemType.OTHER.value, name=d.name, cost=d.cost, quant=d.quant) for d in other]
        )

        session.add_all(new_details)
        session.commit()

    return JSONResponse(content={'detail': 'ok'})

@app.get("/daily_report/summary", response_class=HTMLResponse)
async def summary_top_page(request: Request, csrf_protect: CsrfProtect = Depends()):

    token = get_decoded_token(request.cookies['token'], key=token_key)
    token = validate_token(token, ['account_uuid'])

    if token is None:
        # return Response(status_code=403)
        return templates.TemplateResponse(
            "invalid.html", {
                "request": request
            },
            status_code=403
        )

    content = dict()
    with Session(get_engine()) as session:
        head = session.scalars(select(ReportHead).where(
            ReportHead.account_id == token['account_uuid']))

        worksite_names = list({'id': x.id, 'name': x.worksite_name} for x in head)
    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    response = templates.TemplateResponse(
        "daily_report_summary.html", {
            "request": request,
            "worksite_names": worksite_names,
            "csrf_token": csrf_token
        }
    )
    csrf_protect.set_csrf_cookie(signed_token, response)
    return response


@app.get("/daily_report/{work_name}/summary/{work_id}")
async def get_summary_with_workid(request: Request, work_name: str, work_id: int):

    token = get_decoded_token(request.cookies['token'], key=token_key)
    token = validate_token(token, ['account_uuid'])

    content = dict()
    with Session(get_engine()) as session:

        head = session.scalars(select(ReportHead).where(
                ReportHead.account_id == token['account_uuid']).where(
                ReportHead.id == work_id)).one()
        content['head'] = head.to_dict()

        details = session.execute(
            select(
                ReportDetail.work_date,
                ReportDetail.type,
                func.sum(ReportDetail.quant).label("total_quant"),
                func.sum(ReportDetail.quant*ReportDetail.cost).label("total_cost"),
            ).where(
                ReportDetail.report_head == head
            ).group_by(
                ReportDetail.type,
                ReportDetail.work_date,
            ).order_by(
                ReportDetail.work_date,
            ))

        d = list()
        for date, type, total_quant, total_cost in details:
            t = {
                "date": datetime.datetime.strftime(date, '%Y-%m-%d'),
                "type": type,
                "quant": total_quant,
                "total": total_cost
            }
            d.append(t)
        content['details'] = d
        logger.debug(d)

    return JSONResponse(content=content)
