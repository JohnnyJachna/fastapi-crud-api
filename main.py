import json
import pathlib
import uvicorn

from typing import List, Union
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response, Depends
from sqlmodel import Session, select

from models import Track
from database import TrackModel, engine


data = []

@asynccontextmanager
async def lifespan(app: FastAPI):
  DATAFILE = pathlib.Path() / 'data' / 'tracks.json' #Set variable to path of tracks.json
  
  session = Session(engine)

  # Check if the database is already populated
  stmt = select(TrackModel)
  result = session.exec(stmt).first()
  
  # Load data if there's no results
  if result is None:
    with open(DATAFILE, 'r') as f:
      tracks = json.load(f)
      for track in tracks:
        session.add(TrackModel(**track))
    session.commit()
  session.close()
  yield

app = FastAPI(lifespan=lifespan)

# FastAPI dependency function
def get_session():
  with Session(engine) as session:
    yield session

@app.get('/tracks/', response_model=List[Track])
def tracks(session: Session = Depends(get_session)):
  # select * from table
  stmt = select(TrackModel)
  result = session.exec(stmt).all()
  return result

@app.get('/tracks/{track_id}', response_model=Union[Track, str])
def track(track_id: int, response: Response, session: Session = Depends(get_session)):
  #Find the track with the given ID, or None if it does not exist
  track = session.get(TrackModel, track_id)
  if track is None:
    response.status_code = 404
    return "Track not found"
  return track

@app.post('/tracks/', response_model=Track, status_code=201)
def create_track(track: TrackModel, session: Session = Depends(get_session)):
  # change track from pydantic to sql model, 
  session.add(track) # type hints as a sql model, no longer need validation in database with validate_assignment
  session.commit()
  session.refresh(track)
  return track

@app.put('/tracks/{track_id}', response_model=Union[Track, str])
def update_track(track_id: int, updated_track: Track, response: Response):
  #Find the track with the given ID, or None if it does not exist
  track = None
  for t in data:
    if t['id'] == track_id:
      track = t
      break

  if track is None:
    response.status_code = 404
    return "Track not found"
  
  for key, val in updated_track.model_dump().items():
    if key != 'id':
      track[key] = val
  return track

@app.delete('/tracks/{track_id}')
def delete_track(track_id: int, response: Response):
  #Find the track with the given ID, or None if it does not exist
  track_index = None
  for idx, t in enumerate(data):
    if t['id'] == track_id:
      track_index = idx
      break

  if track_index is None:
    response.status_code = 404
    return "Track not found"
  
  del data[track_index]
  return Response(status_code=200)

if __name__ == '__main__':
  uvicorn.run('main:app', host='localhost', port=8000, reload=True)