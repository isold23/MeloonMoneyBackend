from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from .config import MYSQL_DSN

engine = create_engine(
    MYSQL_DSN,
    pool_pre_ping=True,
    pool_recycle=3600,
)

SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
