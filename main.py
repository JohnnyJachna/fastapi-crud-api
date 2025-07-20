import json
import pathlib
from typing import List, Union
from fastapi import FastAPI, Response
from models import Track

app = FastAPI()

data = []

@app.on_event("startup")
async def startup_event():
  datapath = pathlib.Path() / 'data' / 'tracks.json' #set variable datapath to path of tracks.json
  with open(datapath, 'r') as f: #Open file at path above, read mode, reference as f
    tracks = json.load(f) #Convert json data to python dictionaries
    for track in tracks:
      data.append(Track(**track).dict()) #Track() object from pydantic, destructure track data, and convert to dictionary

  print(data)