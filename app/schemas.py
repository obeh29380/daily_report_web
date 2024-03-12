from enum import Enum
from typing import Union

from pydantic import BaseModel, ValidationError

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
        else:
            raise ValueError('{} is not valid item'.format(target_value))


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


class CsrfSettings(BaseModel):
    # Use AWS Secrets Manager, or HashiCorp Vault
    secret_key:str = 'keeekey'


class SUser(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None


class UserInvitation(BaseModel):
    uuid: int


class NewUser(BaseModel):
    username: str
    password: str
    name_last: Union[str, None] = None
    name_first: Union[str, None] = None


class MasterParams(BaseModel):
    params: dict


class DeleteTarget(BaseModel):
    id: int


class AccountModel(BaseModel):
    id: str
    pwd: str
    name: str

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    sub: str
    user_id: str
    exp: int
    user_name: Union[str, None] = None
    account_id: Union[str, None] = None
    account_uuid: Union[int, None] = None
    auth: Union[str, None] = None


class Staff(BaseModel):
    name: str
    cost: int
    quant: Union[int, None] = 1


class Car(BaseModel):
    name: str
    cost: int
    quant: Union[int, None] = 1


class Machine(BaseModel):
    name: str
    cost: int
    quant: Union[int, None] = 1


class Lease(BaseModel):
    name: str
    cost: int
    quant: Union[int, None] = 1


class Machine(BaseModel):
    name: str
    cost: int
    quant: Union[int, None] = 1


class Transport(BaseModel):
    name: str
    cost: int
    quant: Union[int, None] = 1


class Trash(BaseModel):
    item: str
    cost: int
    quant: Union[int, None] = 1
    dest: str
    unit_type: int


class Valuable(BaseModel):
    name: str
    cost: int
    quant: Union[int, None] = 1


class Other(BaseModel):
    name: str
    cost: int
    quant: Union[int, None] = 1


class Detail(BaseModel):
    staffs: list[Staff]
    cars: list[Car]
    machines: list[Machine]
    leases: list[Lease]
    transports: list[Transport]
    trashes: list[Trash]
    valuables: list[Valuable]
    others: list[Other]

class Report(BaseModel):
    head: dict
    detail: Detail


class CompleteReport(BaseModel):
    id: int
    completed_date: str
