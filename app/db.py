from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv
import os 

load_dotenv()

class Model(DeclarativeBase):
    pass

engine = create_engine(os.environ['DATABASE_URL'])
