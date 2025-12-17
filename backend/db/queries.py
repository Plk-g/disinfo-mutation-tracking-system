from typing import List, Dict, Any, Optional
from pymongo import DESCENDING
from .mongo_client import get_db

MATCHES = "narrative_matches"
MUTATIONS = "mutation_events"  # future-proof

def insert_matches(records: List[Dict[str, Any]]) -> int:
    """
    Inserts narrative match records into MongoDB.
    Returns number inserted.
    """
    if not records:
        return 0
    db = get_db()
    res = db[MATCHES].insert_many(records)
    return len(res.inserted_ids)

def get_matches_by_claim_id(claim_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    db = get_db()
    cursor = db[MATCHES].find({"claim_id": claim_id}, {"_id": 0}).limit(limit)
    return list(cursor)

def get_matches_by_post_id(post_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    db = get_db()
    cursor = db[MATCHES].find({"post_id": post_id}, {"_id": 0}).limit(limit)
    return list(cursor)

def get_matches_by_keyword(query: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Uses MongoDB text search index on 'text' (idx_text_search).
    """
    db = get_db()
    cursor = (
        db[MATCHES]
        .find({"$text": {"$search": query}}, {"_id": 0, "score": {"$meta": "textScore"}})
        .sort([("score", {"$meta": "textScore"})])
        .limit(limit)
    )
    return list(cursor)

def get_top_claims(k: int = 10) -> List[Dict[str, Any]]:
    """
    Returns top claims by frequency.
    """
    db = get_db()
    pipeline = [
        {"$group": {"_id": "$claim_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": k},
        {"$project": {"_id": 0, "claim_id": "$_id", "count": 1}},
    ]
    return list(db[MATCHES].aggregate(pipeline))

# ---- Optional / future-proof for mutations ----

def insert_mutations(events: List[Dict[str, Any]]) -> int:
    if not events:
        return 0
    db = get_db()
    res = db[MUTATIONS].insert_many(events)
    return len(res.inserted_ids)

def get_mutation_timeline(cluster_id: str, limit: int = 200) -> List[Dict[str, Any]]:
    db = get_db()
    cursor = (
        db[MUTATIONS]
        .find({"cluster_id": cluster_id}, {"_id": 0})
        .sort("window_start", 1)
        .limit(limit)
    )
    return list(cursor)

def get_top_mutations(k: int = 10) -> List[Dict[str, Any]]:
    db = get_db()
    cursor = db[MUTATIONS].find({}, {"_id": 0}).sort("mutation_score", DESCENDING).limit(k)
    return list(cursor)
