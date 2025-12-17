import os
import sys
from flask import Flask, render_template, request, jsonify

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.db.queries import (
    get_matches_by_keyword,
    get_matches_by_claim_id,
    get_top_claims,
    get_top_mutations,
    get_mutation_timeline,
)

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", error=None)


def analyze_text(text):
    """Analyze text and determine fake/real percentage with citations"""
    if not text or not isinstance(text, str) or not text.strip():
    if not text or not isinstance(text, str) or not text.strip():
        return {
            "no_results": True,
            "fake_percentage": None,
            "real_percentage": None,
            "confidence": "none",
            "reasoning": "Invalid input: Please provide a non-empty text to analyze.",
            "citations": [],
            "mutation_info": None,
            "total_matches": 0
        }
    
    try:
        # Search for similar narratives in database
        docs = get_matches_by_keyword(text, limit=50)
        
        if not docs:
            return {
                "no_results": True,
                "fake_percentage": None,
                "real_percentage": None,
                "confidence": "none",
                "reasoning": "No similar narratives found in our database. This could mean the claim is new, authentic, or not yet tracked in our system.",
                "citations": [],
                "mutation_info": None,
                "total_matches": 0
            }
        
        similarities = []
        matched_docs = []
        
        for doc in docs:
            try:
                sim_score = float(doc.get("similarity_score", 0.0))
                similarities.append(sim_score)
                if sim_score > 0.7:
                    matched_docs.append(doc)
            except (TypeError, ValueError):
                continue
        
        if not similarities:
            return {
                "no_results": True,
                "fake_percentage": None,
                "real_percentage": None,
                "confidence": "none",
                "reasoning": "Insufficient data for analysis. No valid similarity scores found in the database.",
                "citations": [],
                "mutation_info": None,
                "total_matches": len(docs)
            }
        
        avg_sim = sum(similarities) / len(similarities)
        high_sim_count = sum(1 for s in similarities if s > 0.7)
        match_rate = high_sim_count / len(similarities) if similarities else 0.0
        
        fake_score = (avg_sim * 0.7 + match_rate * 0.3) * 100
        fake_percentage = min(95.0, max(5.0, fake_score))
        real_percentage = 100.0 - fake_percentage
        if len(similarities) >= 10 and match_rate > 0.5:
            confidence = "high"
        elif len(similarities) >= 5:
            confidence = "medium"
        else:
            confidence = "low"
        
        citations = []
        for doc in matched_docs[:5]:
            try:
                text = doc.get("text") or ""
                if not isinstance(text, str):
                    text = str(text)
                text_display = text[:200] + "..." if len(text) > 200 else text
                
                similarity_score = doc.get("similarity_score", 0)
                try:
                    similarity = round(float(similarity_score), 3)
                except (TypeError, ValueError):
                    similarity = 0.0
                
                citations.append({
                    "text": text_display,
                    "source": doc.get("source", "unknown"),
                    "similarity": similarity,
                    "timestamp": doc.get("timestamp", ""),
                    "claim_id": doc.get("claim_id", "")
                })
            except Exception as e:
                print(f"Warning: Skipping invalid citation: {e}")
                continue
        
        mutation_info = None
        try:
            mutations = get_top_mutations(k=5)
            if mutations and len(mutations) > 0:
                top_score = mutations[0].get("mutation_score", 0) if mutations[0] else 0
                try:
                    top_score = float(top_score)
                except (TypeError, ValueError):
                    top_score = 0.0
                
                mutation_info = {
                    "has_mutations": True,
                    "mutation_count": len(mutations),
                    "top_mutation_score": top_score
                }
        except Exception as e:
            print(f"Warning: Could not fetch mutation info: {e}")
            pass
        
        reasoning = f"Found {len(docs)} similar narratives. "
        if match_rate > 0.7:
            reasoning += "High similarity to known disinformation patterns."
        elif match_rate > 0.4:
            reasoning += "Moderate similarity to disinformation narratives."
        else:
            reasoning += "Low similarity to known disinformation."
        
        return {
            "no_results": False,
            "fake_percentage": round(fake_percentage, 1),
            "real_percentage": round(real_percentage, 1),
            "confidence": confidence,
            "reasoning": reasoning,
            "citations": citations,
            "mutation_info": mutation_info,
            "total_matches": len(docs),
            "avg_similarity": round(avg_sim, 3),
            "match_rate": round(match_rate * 100, 1)
        }
    
    except Exception as e:
        return {
            "no_results": True,
            "fake_percentage": None,
            "real_percentage": None,
            "confidence": "error",
            "reasoning": f"Analysis error: {str(e)}. Please try again.",
            "citations": [],
            "mutation_info": None,
            "total_matches": 0
        }


@app.route("/search", methods=["POST"])
def search():
    query = request.form.get("query", "").strip()
    if not query:
        return render_template("index.html", error="Please enter a news article or claim to analyze.")

    try:
        # Perform comprehensive analysis
        analysis = analyze_text(query)
        
        # Get related mutations if available
        mutations = []
        try:
            mutations = get_top_mutations(k=5)
        except Exception as e:
            print(f"Warning: Could not fetch mutations: {e}")
            mutations = []
        
        return render_template(
            "results.html",
            query=query,
            analysis=analysis,
            mutations=mutations,
        )
    except Exception as e:
        return render_template("index.html", error=f"Analysis error: {str(e)}")


@app.get("/mutations")
def mutations_page():
    """Display mutation dashboard"""
    try:
        top = get_top_mutations(k=10)
        empty = (len(top) == 0)
    except Exception:
        top = []
        empty = True

    return render_template("mutations.html", top_mutations=top, empty=empty)



@app.get("/api/search")
def api_search():
    query = (request.args.get("query") or "").strip()
    try:
        limit = int(request.args.get("limit", 20))
        if limit < 1 or limit > 100:
            limit = 20  # Clamp to reasonable range
    except (TypeError, ValueError):
        limit = 20

    if not query:
        return jsonify({"query": query, "count": 0, "items": []})

    try:
        items = get_matches_by_keyword(query, limit=limit)
        return jsonify({"query": query, "count": len(items), "items": items})
    except Exception as e:
        return jsonify({"error": str(e), "query": query}), 500


@app.get("/api/top_claims")
def api_top_claims():
    try:
        k = int(request.args.get("k", 10))
        if k < 1 or k > 100:
            k = 10  # Clamp to reasonable range
    except (TypeError, ValueError):
        k = 10

    try:
        items = get_top_claims(k=k)
        return jsonify({"k": k, "items": items})
    except Exception as e:
        return jsonify({"error": str(e), "k": k}), 500


@app.get("/api/claim/<claim_id>")
def api_claim(claim_id):
    # Validate claim_id
    if not claim_id or len(claim_id) > 200:
        return jsonify({"error": "Invalid claim_id", "claim_id": claim_id, "count": 0, "items": []}), 400
    
    try:
        limit = int(request.args.get("limit", 50))
        if limit < 1 or limit > 200:
            limit = 50  # Clamp to reasonable range
    except (TypeError, ValueError):
        limit = 50

    try:
        items = get_matches_by_claim_id(claim_id, limit=limit)
        return jsonify({"claim_id": claim_id, "count": len(items), "items": items})
    except Exception as e:
        return jsonify({"error": str(e), "claim_id": claim_id}), 500


@app.get("/api/mutations/top")
def api_mutations_top():
    try:
        k = int(request.args.get("k", 10))
        if k < 1 or k > 100:
            k = 10  # Clamp to reasonable range
    except (TypeError, ValueError):
        k = 10

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
    
    # Validate cluster_id format (basic check)
    if not cluster_id or len(cluster_id) > 100:
        return jsonify({"error": "Invalid cluster_id", "cluster_id": cluster_id, "points": []}), 400

    try:
        points = get_mutation_timeline(cluster_id, limit=200)
        if not points:
            points = _mock_timeline()
        
        # Validate points structure
        validated_points = []
        for point in points:
            try:
                # Ensure required fields exist
                if "window_start" in point and "mutation_score" in point:
                    validated_points.append({
                        "window_start": int(point.get("window_start", 0)),
                        "window_end": int(point.get("window_end", point.get("window_start", 0))),
                        "mutation_score": float(point.get("mutation_score", 0.0))
                    })
            except (TypeError, ValueError, KeyError):
                continue  # Skip invalid points
        
        return jsonify({"cluster_id": cluster_id, "points": validated_points})
    except Exception as e:
        return jsonify({"error": str(e), "cluster_id": cluster_id, "points": []}), 500



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
    app.run(debug=True, port=5001)
