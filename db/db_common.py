from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# tips: 相対パスの場合、スラッシュ3つ、絶対パスの場合、4つ。(絶対パスは/から始まるので)
RDB_PATH = 'sqlite:////etc/drw/db/db.sqlite3'
ECHO_LOG = True

engine = create_engine(
    RDB_PATH, echo=ECHO_LOG
)

Session = sessionmaker(bind=engine)
session = Session()
