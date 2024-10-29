from fastapi import FastAPI, Response # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from pymongo import MongoClient # type: ignore
from typing import Optional

import datetime
import json
import os
import requests # type: ignore


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mongo_user = os.getenv("MONGO_USER")
mongo_pass = os.getenv("MONGO_PASS")
mongo_host = os.getenv("MONGO_HOST")
mongo_port = os.getenv("MONGO_PORT")
mongo_db = os.getenv("MONGO_DB")
theoneapi_url = os.getenv("THEONEAPI_URL")
theoneapi_auth = os.getenv("THEONEAPI_AUTH")

client = MongoClient(f"mongodb://{mongo_user}:{mongo_pass}@{mongo_host}:{mongo_port}/{mongo_db}?authSource=admin")
db = client[mongo_db]

@app.get("/")
def read_root():
    return {"Status": "Online"}

@app.get("/movies/search")
def read_root(user: Optional[str] = None, movie: Optional[str] = None):
    try:
        header = {"Authorization": theoneapi_auth}
        movies = requests.get(url=theoneapi_url, headers=header).json()
        filtered_docs = [doc for doc in movies['docs'] if doc['name'] == movie]
        data = {
            "name": user,
            "movie": filtered_docs[0]["name"],
            "year": 1990,
            "creation": datetime.datetime.now()
        }
        inserted_id = db["external_data"].insert_one(data).inserted_id
        data["_id"] = str(inserted_id)
        data["creation"] = data["creation"].isoformat()
        return data
    except:
        return Response(content=json.dumps({"Error": "Please, inform a valid movie name."}), status_code=400)
    
@app.get("/movies/history")
def read_root():
    try:
        page = 1
        page_size = 10
        skip_records = (page - 1) * page_size
        data = db["external_data"].find().sort("creation", -1).skip(skip_records).limit(page_size)
        if data == {}:
            return Response(content=json.dumps({"Error": "No records found."}), status_code=404)
        data_dict = {i: {**document, "_id": str(document["_id"])} for i, document in enumerate(data)}
        return data_dict
    except:
        return Response(content=json.dumps({"Error": "Server unavailable."}), status_code=500)