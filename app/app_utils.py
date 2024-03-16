import datetime
from jose import JWTError, jwt
import pytz
import random
import string
import shutil
import hashlib
from typing import Union
from typing import Annotated

from passlib.context import CryptContext
from passlib.exc import UnknownHashError
from fastapi import (
    Depends,
    status,
)
from fastapi import (
    FastAPI,
    HTTPException,
    Request,
    UploadFile,
)
from sqlalchemy.orm import Session
from sqlalchemy.exc import (
    NoResultFound,
)
from sqlalchemy import select
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError
from fastapi.security import OAuth2PasswordBearer

from db_common import get_engine
from tables import (
    User,
    Account,
)
from schemas import(
    MasterParams,
    DeleteTarget,
    AccountModel,
    Token,
    TokenData,
    SUser,
    UNIT_TYPE,
)
from tables import (
    User,
    DestMaster,
    ItemMaster,
)

PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# def to_json(data):
#     """クエリオブジェクトをdict形式にパースする。

#     Args:
#         data (_type_): _description_
#     """

#     res = list()
#     for d in data:
#         res.append(
#             {
#                 'id': d.id,
#                 'dest_id': d.dest_id,
#                 'item_id': d.item_id,
#                 'cost': d.cost,
#                 'unit_type': list(filter(lambda item: item['id'] == d.unit_type, UNIT_TYPE))[0]['name'],
#             }
#         )
#     return res


def ensure_str(txt, default=None):
    """文字列のチェック
    文字列が空文字かNoneの場合、defaultを返す。
    文字列が上記以外の場合、入力値をそのまま返す。

    Args:
        txt (_type_): チェック対象文字列
        default (_type_, optional): 文字列が空もしくはNoneの場合に返すデフォルト値
    """

    if txt is None or txt == '':
        return default
    else:
        return txt


def get_master_data(db_data, master_type, account_id = None, **kwargs):
    """マスタデータのクエリオブジェクトを
    クライアントに返す形式のデータに変換する。

    Args:
        db_data (queryobject): dbから取得したクエリオブジェクト
        master_type (str): マスタ種別 ex.) staff
    """

    # if db_data is None:
    #     return
    
    if master_type in ['dest', 'customer', 'item']:
        return get_name_only_master_data(db_data)

    col_values = list()
    if master_type == 'trash':
        
        with Session(get_engine()) as session:
            dest = list()
            item = list()

            stmt = select(DestMaster).where(DestMaster.account_id == account_id)
            for d in session.scalars(stmt):
                dest.append(
                    {
                        'id': d.id,
                        'name': d.name
                    }
                )
            stmt = select(ItemMaster).where(ItemMaster.account_id == account_id)
            for d in session.scalars(stmt):
                item.append(
                    {
                        'id': d.id,
                        'name': d.name
                    }
                )
        col_definitions = {
            'id': {
                'colname': 'id',
                'type': 'integer',
                'readonly': True
            },
            'dest_id': {
                'colname': '処分先',
                'type': 'select',
                'selections': dest,
                'readonly': False
            },
            'item_id': {
                'colname': '品名',
                'type': 'select',
                'selections': item,
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

        for d in db_data:
            for u in UNIT_TYPE:
                if d.unit_type == u['id']:
                    unit_type = u['name']
            else:
                unit_type = UNIT_TYPE[0]['name']

            col_values.append(
                {
                    'id': d.id,
                    'dest_id': d.dest.name,
                    'item_id': d.item.name,
                    'cost': d.cost,
                    'unit_type': unit_type,
                }
            )

    elif master_type == 'work':
        col_definitions = {
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

        for d in db_data:
            col_values.append(
                {
                    'id': d.id,
                    'worksite_name': d.worksite_name,
                    'customer': nvl(d.customer_name),
                    'address': nvl(d.address),
                    'memo': nvl(d.memo),
                    'complete': True if d.completed_date is not None else False,
                    'completed_date': datetime.datetime.strftime(d.completed_date, '%Y-%m-%d') if d.completed_date is not None else None,
                }
            )

    else:
        col_definitions = {
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

        for d in db_data:
            col_values.append(
                {
                    'id': d.id,
                    'name': d.name,
                    'cost': d.cost,
                }
            )

    res = dict(
        col_definitions=col_definitions,
        col_values=col_values,
    )

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
    return datetime.datetime.now(datetime.timezone.utc)


def utc_now_dtimedelta():
    return datetime.datetime.now(datetime.timezone.utc)


def nvl(txt, replace=''):
    if txt is None or txt == 'null':
        return replace
    else:
        return txt


def refresh_token(token, key='token_key', exp=3600):
    decode_token = jwt.decode(token, key=key, algorithms="HS256")
    decode_token["exp"] = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=exp)
    return get_jwt(decode_token, key=key, exp=exp)

def timestamp_2_utc_aware(time_stamp):
    return datetime.datetime.utcfromtimestamp(time_stamp).replace(tzinfo=pytz.utc)

def get_decoded_token(token, key='token_key', required_permission: list = [], algorithms="HS256"):

    try:
        payload = jwt.decode(token, key, algorithms=algorithms)
    except ExpiredSignatureError as e:
        print(e)
        return

    user_uuid = payload.get("sub")
    if user_uuid is None:
        return

    if timestamp_2_utc_aware(payload['exp']) < utc_now_dtime():
        return

    # TODO ここでやるべきか？
    # if len(set(required_permission) - set(decode_token.get('auth'))) > 0:
    #     return None

    return payload


def validate_token(decoded_token, expected_keys: list = []) -> dict:

    message_no_item = "ゲスト機能では利用できません"
    message_no_token = "アクセストークンの項目が不足しています"

    if decoded_token is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message_no_token,
            headers={"WWW-Authenticate": "Bearer"},
        )

    for k in expected_keys:
        if k not in decoded_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=message_no_item,
                headers={"WWW-Authenticate": "Bearer"},
            )
        if decoded_token[k] is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=message_no_item,
                headers={"WWW-Authenticate": "Bearer"},
            )

    return decoded_token


def random_str(n=10):
   randlst = [
       random.choice(string.ascii_letters + string.digits) for _ in range(n)]
   return ''.join(randlst)


def get_jwt(data, key='token_key', exp=3600):

    d = data.copy()
    if 'exp' not in d:
        d["exp"] = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=exp)

    if 'auth' not in d:
        d["auth"] = []

    return jwt.encode(d, key, algorithm="HS256")

def verify_password(plain_password, hashed_password):
    try:
        result = PWD_CONTEXT.verify(plain_password, hashed_password)
    except UnknownHashError:
        # ハッシュを変えた場合、元のハッシュで登録したDB上のパスワードが復号できずエラーになる
        print('hash changed error')
    return result


def get_password_hash(password):
    return PWD_CONTEXT.hash(password)


def get_user(user_id: str):

    with Session(get_engine()) as session:

        try:
            stmt = select(User).where(User.user_id == user_id)
            user = session.scalars(stmt).one()
        except NoResultFound:
            # return JSONResponse(status_code=403, content=dict(message='User not found'))
            return
        
        return user.to_dict()


def authenticate_user(user_id: str, user_pwd: str) -> Union[dict, bool]:
    user = get_user(user_id)
    if user is None:
        return False
    if not verify_password(user_pwd, user['user_pwd']):
        return False
    return user


def create_access_token(user_uuid: str, token_key: str,
                        account_uuid: Union[int, None] = None, exp_seconds: float = 3600,
                        algorithm="HS256"
                        ):
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=exp_seconds)
    to_encode = dict(
        exp=expire,
        sub=str(user_uuid),
        account_uuid=account_uuid
    )
    encoded_jwt = jwt.encode(to_encode, token_key, algorithm=algorithm)
    return encoded_jwt


def get_hashed_file_name(file_name, enc_key):
    salted_filename = file_name + enc_key
    # SHA-256ハッシュオブジェクトを作成し、ファイル名をハッシュ化します
    hasher = hashlib.sha256()
    hasher.update(salted_filename.encode('utf-8'))
    return hasher.hexdigest()


def get_account_logo(account_uuid):
    with Session(get_engine()) as session:
        try:
            stmt = select(Account.logo_name).where(Account.id == account_uuid)
            d = session.scalars(stmt).one()
        except NoResultFound:
            # return JSONResponse(status_code=403, content=dict(message='User not found'))
            return
        
        return d


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, token_key, algorithms=[ALGORITHM])
        user_uuid: str = payload.get("sub")
        if user_uuid is None:
            raise credentials_exception
        token_data = TokenData(
            sub=payload.get("sub"),
            exp=payload.get("exp"),
            user_id=payload.get("user_id"),
            user_name=payload.get("user_name"),
            account_id=payload.get("account_id"),
            account_uuid=payload.get("account_uuid"),
            disabled=payload.get("disabled"),
        )
    except JWTError:
        raise credentials_exception
    user = get_user(user_id=token_data.user_id)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: SUser = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def save_uploaded_file(file: UploadFile, file_path: str):
    with open(file_path, mode='bw') as buffer:
        shutil.copyfileobj(file.file, buffer)
