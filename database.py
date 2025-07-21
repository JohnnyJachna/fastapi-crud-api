from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel, create_engine

DB_FILE = 'db.sqlite3'
engine = create_engine(f"sqlite:///{DB_FILE}", echo=True)

class TrackModel(SQLModel, table=True):
  class Config: # Without this, I got a long list of typecheck errors
    validate_assignment = True 
  id: Optional[int] = Field(default=None, primary_key=True)
  title: str
  artist: str
  duration: float
  last_play: datetime

def create_tables():
  SQLModel.metadata.create_all(engine)

if __name__ == '__main__':
  create_tables()
