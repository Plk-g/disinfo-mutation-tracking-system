import os
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI")
DB = os.getenv("MONGO_DB", "disinfo_project")
COL_CLUSTERS = os.getenv("MONGO_COL_CLUSTERS", "narrative_clusters")
COL_DRIFT = os.getenv("MONGO_COL_DRIFT", "drift_metrics")

if not MONGO_URI:
    raise RuntimeError("MONGO_URI is not set. In PowerShell: $env:MONGO_URI='mongodb+srv://...'\n")

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=8000)
print("Ping:", client.admin.command("ping"))

db = client[DB]
col_clusters = db[COL_CLUSTERS]
col_drift = db[COL_DRIFT]

print("\nRecent narrative_clusters:")
for d in col_clusters.find().sort([("_id", -1)]).limit(3):
    d.pop("_id", None)
    print(d)

print("\nRecent drift_metrics:")
for d in col_drift.find().sort([("_id", -1)]).limit(3):
    d.pop("_id", None)
    print(d)

client.close()
