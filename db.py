# db.py
from pymongo import MongoClient
from datetime import datetime

MONGO_URI = "mongodb://127.0.0.1:27017/"
DB_NAME = "ds_midterm"
COLL_NAME = "scrapes"

def get_collection():
    client = MongoClient(MONGO_URI)
    return client[DB_NAME][COLL_NAME]

def save_result(result: dict) -> str:
    # result expected keys: url, ok, count, titles, [error?]
    doc = {
        **result,
        "created_at": datetime.utcnow()
    }
    coll = get_collection()
    inserted = coll.insert_one(doc)
    return str(inserted.inserted_id)
