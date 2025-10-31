# db_clean.py
from pymongo import MongoClient
from datetime import datetime

MONGO_URI = "mongodb://127.0.0.1:27017/"
DB_NAME = "ds_midterm"
CLEAN_COLL = "clean_docs"

def get_clean_collection():
    client = MongoClient(MONGO_URI)
    return client[DB_NAME][CLEAN_COLL]

def save_clean_doc(doc: dict) -> str:
    doc = {**doc, "created_at": datetime.utcnow()}
    coll = get_clean_collection()
    return str(coll.insert_one(doc).inserted_id)
