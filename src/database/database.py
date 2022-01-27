from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import yaml

with open('secrets.yml') as f:
    cfg = yaml.safe_load(f)

SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{cfg['DB']['user']}:{cfg['DB']['password']}@localhost/{cfg['DB']['name']}"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()