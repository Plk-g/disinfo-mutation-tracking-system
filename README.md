# Disinformation Mutation Tracking System

This project tracks how disinformation narratives **emerge, evolve, and mutate over time** using a streaming data pipeline and an interactive backend + frontend system.

It is designed to support:

* narrative similarity matching
* mutation / drift analysis
* exploratory search and visualization for downstream analysis


## 🧠 System Overview

**High-level flow:**

```
Kafka (raw posts)
   ↓
Spark Streaming (similarity + clustering)
   ↓
MongoDB (narrative_matches, mutation_events)
   ↓
Flask Backend + API
   ↓
Web UI & Visualization
```

The system is modular: each stage can be developed and tested independently.


## 🗂️ Project Structure

```
disinfo-mutation-tracking-system/
│
├── backend/
│   └── db/
│       ├── mongo_client.py      # MongoDB connection (env-based)
│       └── queries.py           # Insert + query helpers
│
├── frontend/
│   ├── app.py                   # Flask app + API routes
│   ├── templates/
│   │   ├── index.html
│   │   ├── results.html
│   │   └── mutations.html
│   └── static/
│
├── docs/
│   └── data_contract.md         # Source-of-truth schema
│
├── scripts/
│   ├── create_indexes.py        # MongoDB indexes
│   ├── smoke_test_db.py         # DB connectivity test
│   ├── run_producer.py          # Kafka producer (sends sample narratives)
│   ├── seed_sample_data.py      # Seed MongoDB with test data
│   └── run_complete_pipeline.py # Pipeline coordination script
├── src/
│   └── clustering/
│       ├── clusterer.py         # K-means clustering
│       ├── drift_model.py       # Topic drift detection
│       ├── mutation_detector.py # Mutation detection logic
│       ├── embedding_generator.py # Sentence-BERT embeddings
│       └── vector_utils.py       # Vector operations
├── main.py                      # Spark streaming consumer
│
├── requirements.txt
└── README.md
```

## ⚙️ Setup Instructions

### 1️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 2️⃣ Set environment variables

> **Important:** credentials are never hardcoded.

```bash
export MONGO_URI="mongodb+srv://<username>:<password>@cluster0.jwaekxl.mongodb.net/?retryWrites=true&w=majority"
export MONGO_DB="disinfo_project"
```
### 3️⃣ Create MongoDB indexes (one-time)

```bash
python3 scripts/create_indexes.py
```

Indexes include:

* text search on `text`
* `claim_id`
* `cluster_id`
* timestamps


### 4️⃣ Run the application

```bash
python3 -m frontend.app
```

The app will start at:

```
http://127.0.0.1:5000
```

## 🌐 Demo Pages

### 🔍 Search Interface

* **URL:** `/`
* Search narrative text and view:

  * similarity statistics
  * match rates
  * credibility score (heuristic)

### 🔄 Mutation Dashboard

* **URL:** `/mutations`
* Displays:

  * top mutated narrative clusters
  * mutation score ranking
  * drift-over-time placeholder (API-driven)

If no mutation data exists yet, the page shows a clean **empty state**.

## 🔌 API Endpoints

These endpoints return JSON and are intended for visualization and analysis.

### Narrative search

```
GET /api/search?query=<text>&limit=20
```

### Top claims

```
GET /api/top_claims?k=10
```

### Matches for a claim

```
GET /api/claim/<claim_id>?limit=50
```

### Top mutations

```
GET /api/mutations/top?k=10
```

### Mutation timeline

```
GET /api/mutations/timeline?cluster_id=<id>
```

If no mutation data exists, **mock fallback data** is returned so demos never break.


## 🧪 Smoke Test (Optional)

To verify MongoDB connectivity:

```bash
python3 -m scripts.smoke_test_db
```

## 📄 Data Contract

The authoritative schema definition lives in:

```
docs/data_contract.md
```

All upstream and downstream components are expected to conform to this contract.

## 🚀 Quick Start Guide

### Option 1: Test with Sample Data (No Kafka/Spark Required)

1. **Seed sample data:**
   ```bash
   python scripts/seed_sample_data.py
   ```

2. **Start Flask app:**
   ```bash
   python -m frontend.app
   ```

3. **Visit:** http://127.0.0.1:5000

### Option 2: Full Pipeline (Kafka + Spark + MongoDB)

**Prerequisites:**
- Kafka running on `localhost:9092`
- Java installed (for Spark)
- MongoDB accessible (MONGO_URI set)

**Terminal 1 - Kafka Producer:**
```bash
python scripts/run_producer.py
```

**Terminal 2 - Spark Streaming:**
```bash
python main.py
```

**Terminal 3 - Flask Web UI:**
```bash
python -m frontend.app
```

## 🚧 Current Status

* ✅ Backend DB layer complete
* ✅ Flask API complete
* ✅ Search + mutation UI ready
* ✅ Spark streaming pipeline with embeddings
* ✅ MongoDB integration
* ✅ Sample data seeder
* ✅ Cross-platform support (Windows/macOS/Linux)

---

## 👩‍💻 Authors / Roles

* **Backend + Storage Lead:** Palak Gupta
* **Streaming / NLP / Visualization:** (team-specific)
