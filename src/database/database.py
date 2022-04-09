from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from configparser import ConfigParser

from os.path import exists
from loguru import logger

if exists("config.ini"):
    cfg = ConfigParser()
    cfg.read("config.ini")
else:
    cfg = ConfigParser()
    cfg.read("config.default.ini")
    logger.warning("WARNING: config.ini not found, using default config.")

if len(cfg.sections()) == 0:
    logger.error(
        "ERROR: No config sections found.\nMake sure config.ini exists and is in relative folder of running script!"
    )
    exit(1)

SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{cfg['PostgreSQL']['user']}:{cfg['PostgreSQL']['password']}@127.0.0.1:5432/{cfg['PostgreSQL']['name']}"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=0,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)

Base = declarative_base()
