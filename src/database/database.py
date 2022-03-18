from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from configparser import ConfigParser

from os.path import exists

if exists("config.ini"):
    cfg = ConfigParser()
    cfg.read("config.ini")
else:
    cfg = ConfigParser()
    cfg.read("config.default.ini")
    print("WARNING: config.ini not found, using default config.")

if len(cfg.sections()) == 0:
    print("ERROR: No config sections found.\nMake sure config.ini exists and is in relative folder of running script!")
    exit(1)

SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{cfg['PostgreSQL']['user']}:{cfg['PostgreSQL']['password']}@127.0.0.1:5432/{cfg['PostgreSQL']['name']}"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)

Base = declarative_base()