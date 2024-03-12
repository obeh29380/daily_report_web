from sqlalchemy import (
    create_engine,
)


def get_engine():
    return create_engine("sqlite:///db.sqlite?charset=utf8", echo=False)
