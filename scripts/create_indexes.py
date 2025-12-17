import os
from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT

MONGO_URI = os.environ.get("MONGO_URI")
DB_NAME = os.environ.get("MONGO_DB", "disinfo_project")  # Default matches project standard

if not MONGO_URI:
    raise RuntimeError("❌ MONGO_URI not set. Export it before running.")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Collection: narrative_matches
nm = db["narrative_matches"]
nm.create_index([("claim_id", ASCENDING)], name="idx_claim_id")
nm.create_index([("post_id", ASCENDING)], name="idx_post_id")
nm.create_index([("timestamp", DESCENDING)], name="idx_timestamp_desc")
nm.create_index([("source", ASCENDING)], name="idx_source")
nm.create_index([("text", TEXT)], name="idx_text_search")  # optional but useful

# Collection: mutation_events (future-proof)
me = db["mutation_events"]
me.create_index([("cluster_id", ASCENDING)], name="idx_cluster_id")
me.create_index([("window_start", ASCENDING)], name="idx_window_start")
me.create_index([("cluster_id", ASCENDING), ("window_start", ASCENDING)], name="idx_cluster_window")

print("Indexes created (or already existed).")
