import os
import re
import math
import warnings
from collections import Counter, defaultdict
from datetime import datetime

import requests
from flask import Flask, render_template, request, redirect, url_for

try:
    from urllib3.exceptions import NotOpenSSLWarning
    warnings.filterwarnings("ignore", category=NotOpenSSLWarning)
except Exception:
    pass

app = Flask(__name__, template_folder="templates", static_folder="static")

BACKEND_SEARCH_URL = os.getenv("BACKEND_SEARCH_URL", "http://127.0.0.1:5001/search")


def _normalize_text(s: str) -> str:
    s = (s or "").lower()
    s = re.sub(r"[^a-z0-9\s]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _simple_similarity(query: str, text: str) -> float:
    q = _normalize_text(query)
    t = _normalize_text(text)

    if not q or not t:
        return 0.0

    q_tokens = set(q.split())
    t_tokens = set(t.split())
    if not q_tokens or not t_tokens:
        return 0.0

    inter = len(q_tokens.intersection(t_tokens))
    union = len(q_tokens.union(t_tokens))
    jacc = inter / union if union else 0.0

    phrase_bonus = 0.25 if q in t else 0.0
    score = jacc + phrase_bonus
    if score < 0.0:
        score = 0.0
    if score > 1.0:
        score = 1.0
    return score


def assign_variant(text: str) -> str:
    t = (text or "").lower()
    if "lab leak" in t:
        return "Lab Leak"
    if "cover-up" in t or "cover up" in t or "emails" in t:
        return "Cover-up"
    if "microchip" in t or "chip" in t:
        return "Microchips"
    if "vaccine" in t or "vaccines" in t:
        return "Vaccines Harmful"
    return "General COVID"


def _format_ts(ts: str) -> str:
    if not ts:
        return ""
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%dT%H:%M:%S")
    except Exception:
        return ts


def _date_only(ts: str) -> str:
    if not ts:
        return ""
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).date().isoformat()
    except Exception:
        return ts[:10]


def _try_backend(query: str):
    r = requests.get(BACKEND_SEARCH_URL, params={"q": query}, timeout=10)
    r.raise_for_status()
    payload = r.json()
    posts = payload.get("posts", payload.get("results", payload.get("items", [])))
    if not isinstance(posts, list):
        posts = []
    return posts


def _load_mock_posts():
    try:
        from data.mock_data import MOCK_POSTS
        if isinstance(MOCK_POSTS, list):
            return MOCK_POSTS
    except Exception:
        pass
    return []


def _credibility_heuristic(posts) -> int:
    if not posts:
        return 50

    sims = []
    for p in posts:
        s = p.get("similarity", 0.0)
        try:
            sims.append(float(s))
        except Exception:
            sims.append(0.0)

    avg = sum(sims) / len(sims) if sims else 0.0
    score = 80 - int(round(avg * 60)) - int(round(min(len(posts), 50) * 0.3))

    if score < 0:
        score = 0
    if score > 100:
        score = 100
    return score


@app.route("/home")
def home():
    return redirect(url_for("index"))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search_post():
    q = request.form.get("q", "").strip()
    if not q:
        return redirect(url_for("index"))
    return redirect(url_for("search_get", q=q))


@app.route("/search", methods=["GET"])
def search_get():
    query = request.args.get("q", "").strip()
    if not query:
        return redirect(url_for("index"))

    raw_posts = []
    backend_ok = True
    try:
        raw_posts = _try_backend(query)
    except Exception:
        backend_ok = False
        raw_posts = _load_mock_posts()

    posts = []
    for p in raw_posts:
        title = p.get("title", p.get("claim", p.get("text", ""))) or ""
        text = p.get("text", p.get("body", p.get("content", ""))) or ""
        source = p.get("source", p.get("source_label", "unknown")) or "unknown"
        ts = p.get("timestamp", p.get("time", p.get("date", ""))) or ""

        sim = p.get("similarity", p.get("similarity_score", None))
        if sim is None:
            sim = _simple_similarity(query, f"{title} {text}")
        try:
            sim = float(sim)
        except Exception:
            sim = 0.0

        matched = bool(p.get("matched", sim >= 0.60))

        variant = p.get("variant", None) or assign_variant(f"{title} {text}")

        posts.append(
            {
                "title": title.strip()[:300],
                "text": text.strip()[:600],
                "source": source,
                "timestamp": _format_ts(ts),
                "similarity": sim,
                "matched": matched,
                "variant": variant,
            }
        )

    total = len(posts)
    avg_similarity = (sum(p["similarity"] for p in posts) / total) if total else 0.0
    avg_similarity = round(avg_similarity, 3)
    credibility_score = _credibility_heuristic(posts)

    dates = [_date_only(p.get("timestamp", "")) for p in posts if _date_only(p.get("timestamp", ""))]
    time_counter = Counter(dates)
    time_labels = sorted(time_counter.keys())
    time_counts = [time_counter[d] for d in time_labels]

    src_counter = Counter([p.get("source", "unknown") for p in posts])
    source_labels = sorted(src_counter.keys(), key=lambda k: (-src_counter[k], k))
    source_counts = [src_counter[s] for s in source_labels]

    bins = [(0.0, 0.1), (0.1, 0.2), (0.2, 0.3), (0.3, 0.4), (0.4, 0.5),
            (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 0.9), (0.9, 1.0)]
    hist_labels = [f"{a:.1f}–{b:.1f}" for a, b in bins]
    hist_counts = [0] * len(bins)

    for p in posts:
        s = p.get("similarity", 0.0)
        try:
            s = float(s)
        except Exception:
            s = 0.0
        if s < 0.0:
            s = 0.0
        if s > 1.0:
            s = 1.0
        idx = min(int(math.floor(s * 10)), 9)
        hist_counts[idx] += 1

    variant_counter = Counter([p.get("variant", "Unknown") for p in posts])
    variant_labels = sorted(variant_counter.keys(), key=lambda k: (-variant_counter[k], k))
    variant_counts = [variant_counter[v] for v in variant_labels]

    variant_time = defaultdict(lambda: Counter())
    for p in posts:
        d = _date_only(p.get("timestamp", ""))
        v = p.get("variant", "Unknown")
        if d:
            variant_time[v][d] += 1

    variant_time_labels = sorted(set(time_labels))
    variant_time_series = []
    for v in variant_labels:
        series = [variant_time[v].get(d, 0) for d in variant_time_labels]
        variant_time_series.append({"variant": v, "counts": series})

    return render_template(
        "results.html",
        query=query,
        total=total,
        avg_similarity=avg_similarity,
        credibility_score=credibility_score,
        posts=posts,
        time_labels=time_labels,
        time_counts=time_counts,
        source_labels=source_labels,
        source_counts=source_counts,
        hist_labels=hist_labels,
        hist_counts=hist_counts,
        variant_labels=variant_labels,
        variant_counts=variant_counts,
        variant_time_labels=variant_time_labels,
        variant_time_series=variant_time_series,
        backend_ok=backend_ok,
        backend_url=BACKEND_SEARCH_URL,
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=True)


