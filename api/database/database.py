from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL =  'mysql+pymysql://admin:wlqdprkrhtlvek@database-1.cbuuk46a097l.ap-northeast-2.rds.amazonaws.com:3306/testDB' # AWS DB Server

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
