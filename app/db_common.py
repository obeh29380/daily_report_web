import os

from sqlalchemy import (
    create_engine,
)


def get_engine():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db.sqlite')
    return create_engine(f"sqlite:////{db_path}?charset=utf8", echo=False)
