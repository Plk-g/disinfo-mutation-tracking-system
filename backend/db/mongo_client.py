import os
from pymongo import MongoClient

def get_db():
    """
    Returns a MongoDB database handle using env vars.
    Required:
      - MONGO_URI
      - MONGO_DB
    """
    mongo_uri = os.environ.get("MONGO_URI")
    mongo_db = os.environ.get("MONGO_DB")

    if not mongo_uri:
        raise RuntimeError("MONGO_URI not set")
    if not mongo_db:
        raise RuntimeError("MONGO_DB not set")

    client = MongoClient(mongo_uri)
    return client[mongo_db]
