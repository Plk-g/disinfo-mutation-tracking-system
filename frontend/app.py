import time
from flask import Flask, render_template, request, jsonify

from backend.db.queries import (
    get_matches_by_keyword,
    get_matches_by_claim_id,
    get_top_claims,
    get_top_mutations,
    get_mutation_timeline,
)

# --- Flask app ---
app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", error=None)


@app.route("/search", methods=["POST"])
def search():
    query = request.form.get("query", "").strip()
    if not query:
        return render_template("index.html", error="Please enter a topic or keyword.")

    try:
        # Uses MongoDB text index (recommended) via helper layer
        docs = get_matches_by_keyword(query, limit=200)
    except Exception as e:
        return f"MongoDB error: {str(e)}", 500

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


# ----------------------------
# Mutations page (HTML)
# ----------------------------

@app.get("/mutations")
def mutations_page():
    """
    Demo-friendly page. Shows real data if mutation_events exists,
    otherwise shows a clean empty state with placeholders.
    """
    try:
        top = get_top_mutations(k=10)
        empty = (len(top) == 0)
    except Exception:
        top = []
        empty = True

    return render_template("mutations.html", top_mutations=top, empty=empty)


# ----------------------------
# API routes (JSON for viz/demo)
# ----------------------------

@app.get("/api/search")
def api_search():
    query = (request.args.get("query") or "").strip()
    limit = int(request.args.get("limit", 20))

    if not query:
        return jsonify({"query": query, "count": 0, "items": []})

    try:
        items = get_matches_by_keyword(query, limit=limit)
        return jsonify({"query": query, "count": len(items), "items": items})
    except Exception as e:
        return jsonify({"error": str(e), "query": query}), 500


@app.get("/api/top_claims")
def api_top_claims():
    k = int(request.args.get("k", 10))

    try:
        items = get_top_claims(k=k)
        return jsonify({"k": k, "items": items})
    except Exception as e:
        return jsonify({"error": str(e), "k": k}), 500


@app.get("/api/claim/<claim_id>")
def api_claim(claim_id):
    limit = int(request.args.get("limit", 50))

    try:
        items = get_matches_by_claim_id(claim_id, limit=limit)
        return jsonify({"claim_id": claim_id, "count": len(items), "items": items})
    except Exception as e:
        return jsonify({"error": str(e), "claim_id": claim_id}), 500


@app.get("/api/mutations/top")
def api_mutations_top():
    k = int(request.args.get("k", 10))

    try:
        items = get_top_mutations(k=k)
        if not items:
            items = _mock_top_mutations(k)
        return jsonify({"k": k, "items": items})
    except Exception as e:
        return jsonify({"error": str(e), "k": k}), 500


@app.get("/api/mutations/timeline")
def api_mutations_timeline():
    cluster_id = (request.args.get("cluster_id") or "").strip()

    try:
        points = get_mutation_timeline(cluster_id, limit=200) if cluster_id else []
        if not points:
            points = _mock_timeline()
        return jsonify({"cluster_id": cluster_id, "points": points})
    except Exception as e:
        return jsonify({"error": str(e), "cluster_id": cluster_id}), 500


# ----------------------------
# Mock fallback helpers (demo never breaks)
# ----------------------------

def _mock_top_mutations(k: int):
    return [
        {
            "cluster_id": f"cluster_{i+1}",
            "mutation_type": "lexical_shift",
            "mutation_score": round(0.9 - i * 0.06, 2),
        }
        for i in range(min(k, 10))
    ]


def _mock_timeline():
    now = int(time.time())
    return [
        {"window_start": now - 3600 * 6, "window_end": now - 3600 * 5, "mutation_score": 0.20},
        {"window_start": now - 3600 * 5, "window_end": now - 3600 * 4, "mutation_score": 0.35},
        {"window_start": now - 3600 * 4, "window_end": now - 3600 * 3, "mutation_score": 0.50},
        {"window_start": now - 3600 * 3, "window_end": now - 3600 * 2, "mutation_score": 0.65},
    ]


if __name__ == "__main__":
    app.run(debug=True)
