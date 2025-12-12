from flask import Flask, render_template, request
from pymongo import MongoClient
from config import MONGO_URI, DB_NAME

# --- MongoDB setup ---
if MONGO_URI:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    matches_col = db["narrative_matches"]
else:
    client = None
    db = None
    matches_col = None

# --- Flask app ---
app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", error=None)


@app.route("/search", methods=["POST"])
def search():
    if matches_col is None:
        return "MongoDB is not configured. Please set MONGO_URI environment variable.", 500

    query = request.form.get("query", "").strip()
    if not query:
        return render_template("index.html", error="Please enter a topic or keyword.")

    # Simple case-insensitive text search in the 'text' field
    mongo_query = {"text": {"$regex": query, "$options": "i"}}

    docs = list(matches_col.find(mongo_query).limit(200))  # limit for sanity
    total = len(docs)

    if total == 0:
        return render_template(
            "results.html",
            query=query,
            total=0,
            avg_similarity=None,
            match_rate=None,
            credibility_score=None,
            posts=[],
        )

    # Compute stats
    similarities = []
    matched_flags = []

    for doc in docs:
        # similarity_score might be missing or not a float
        try:
            similarities.append(float(doc.get("similarity_score", 0.0)))
        except (TypeError, ValueError):
            similarities.append(0.0)

        matched_flags.append(bool(doc.get("matched", False)))

    avg_sim = sum(similarities) / len(similarities) if similarities else 0.0
    match_rate = (
        sum(1 for m in matched_flags if m) / len(matched_flags)
        if matched_flags
        else 0.0
    )

    # Very simple “credibility” heuristic:
    # higher similarity + higher match_rate → more aligned with known misinformation
    # Convert that into a 0–100 score where higher = more credible
    credibility_score = int(
        max(0, min(100, (1 - avg_sim) * 60 + (1 - match_rate) * 40))
    )

    sample_posts = docs[:10]

    return render_template(
        "results.html",
        query=query,
        total=total,
        avg_similarity=round(avg_sim, 3),
        match_rate=round(match_rate * 100, 1),
        credibility_score=credibility_score,
        posts=sample_posts,
    )


if __name__ == "__main__":
    # For local testing
    app.run(debug=True)
