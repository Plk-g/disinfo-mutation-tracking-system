# Testing Guide

This guide will help you test the Disinformation Mutation Tracking System.

## Prerequisites Check

Before testing, ensure you have:

1. ✅ Python 3.8+ installed
2. ✅ Dependencies installed: `pip install -r requirements.txt`
3. ✅ MongoDB connection (MONGO_URI environment variable set)
4. ✅ Java installed (for Spark streaming - only needed for full pipeline test)

## Test Option 1: Quick Demo (Recommended First Test)

This is the fastest way to see the system working - **no Kafka or Spark required**.

### Step 1: Set Environment Variables

```bash
export MONGO_URI="your_mongodb_connection_string"
export MONGO_DB="disinfo_project"
```

**Windows (PowerShell):**
```powershell
$env:MONGO_URI="your_mongodb_connection_string"
$env:MONGO_DB="disinfo_project"
```

### Step 2: Create MongoDB Indexes

```bash
python scripts/create_indexes.py
```

Expected output:
```
Indexes created (or already existed).
```

### Step 3: Seed Sample Data

```bash
python scripts/seed_sample_data.py
```

Expected output:
```
============================================================
Seeding MongoDB with sample data...
============================================================

1. Generating sample narrative matches...
   ✓ Inserted 50 narrative match records

2. Generating sample mutation events...
   ✓ Inserted 15 mutation event records

============================================================
✓ Sample data seeding complete!
============================================================
```

### Step 4: Start Flask Web Application

```bash
python -m frontend.app
```

Expected output:
```
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server...
 * Running on http://127.0.0.1:5000
```

### Step 5: Test the Web Interface

Open your browser and visit:

1. **Search Page:** http://127.0.0.1:5000
   - Try searching for: "vaccine", "5G", "election", "COVID"
   - You should see results with similarity scores

2. **Mutations Dashboard:** http://127.0.0.1:5000/mutations
   - Should show top mutated narratives
   - Displays mutation scores

3. **API Endpoints** (test in browser or with curl):
   - http://127.0.0.1:5000/api/search?query=vaccine&limit=10
   - http://127.0.0.1:5000/api/top_claims?k=5
   - http://127.0.0.1:5000/api/mutations/top?k=5

### Step 6: Verify Data in MongoDB (Optional)

You can verify the data was inserted:

```bash
python scripts/smoke_test_db.py
```

---

## Test Option 2: Full Streaming Pipeline

This tests the complete Kafka → Spark → MongoDB pipeline.

### Prerequisites

1. **Kafka must be running:**
   ```bash
   # Terminal 1 - Start Zookeeper
   bin/zookeeper-server-start.sh config/zookeeper.properties
   
   # Terminal 2 - Start Kafka
   bin/kafka-server-start.sh config/server.properties
   ```

2. **Verify Kafka is running:**
   ```bash
   kafka-topics --list --bootstrap-server localhost:9092
   ```

### Step 1: Set Environment Variables

Same as Option 1:
```bash
export MONGO_URI="your_mongodb_connection_string"
export MONGO_DB="disinfo_project"
```

### Step 2: Create MongoDB Indexes

```bash
python scripts/create_indexes.py
```

### Step 3: Start Components (3 Terminals)

**Terminal 1 - Kafka Producer:**
```bash
python scripts/run_producer.py
```

Expected output:
```
Starting Kafka Producer...
Topic: disinformation-stream
Bootstrap: localhost:9092
✓ Connected to Kafka

Sending messages (Ctrl+C to stop)...

[1] Vaccines contain microchips that track people...
[2] 5G networks cause COVID-19 and spread the virus...
[3] The election was stolen through massive voter fraud...
```

**Terminal 2 - Spark Streaming Consumer:**
```bash
python main.py
```

Expected output:
```
Starting Spark Disinformation Detector...
Kafka Broker: localhost:9092
Topic: disinformation-stream
   Connecting to Kafka Stream...
Loading Sentence-BERT model...
Model loaded!
✓ Pipeline Running. Waiting for data from Kafka...

--- Processing Batch 0 (5 records) ---
Generated 5 embeddings (dim: 384)
Inserted 5 records into MongoDB
  [1] Vaccines contain microchips... (sim: 0.82)
  [2] 5G networks cause COVID-19... (sim: 0.91)
```

**Terminal 3 - Flask Web Application:**
```bash
python -m frontend.app
```

### Step 4: Verify Real-Time Processing

1. Watch Terminal 2 (Spark) - you should see batches being processed
2. Check Terminal 1 (Producer) - messages being sent
3. Visit http://127.0.0.1:5000 and search for recent narratives
4. New data should appear as Spark processes batches

---

## Test Option 3: Unit Tests

Run the smoke test:

```bash
python tests/test_clustering_smoke.py
```

---

## Troubleshooting Tests

### Issue: "MONGO_URI not set"
**Solution:** Export the environment variable before running scripts.

### Issue: "Connection refused" (Kafka)
**Solution:** Make sure Kafka and Zookeeper are running.

### Issue: "No module named 'sentence_transformers'"
**Solution:** Install dependencies: `pip install -r requirements.txt`

### Issue: "JAVA_HOME not set" (Spark)
**Solution:** 
- Install Java 8, 11, or 17
- Set JAVA_HOME environment variable

### Issue: No results in web UI
**Solution:** 
- Make sure you seeded data: `python scripts/seed_sample_data.py`
- Check MongoDB connection
- Verify indexes were created

### Issue: Spark can't connect to Kafka
**Solution:**
- Verify Kafka is running: `kafka-topics --list --bootstrap-server localhost:9092`
- Check if topic exists, create if needed:
  ```bash
  kafka-topics --create --topic disinformation-stream --bootstrap-server localhost:9092
  ```

---

## Expected Test Results

### Quick Demo Test Results:
- ✅ 50 narrative matches in database
- ✅ 15 mutation events in database
- ✅ Web UI shows search results
- ✅ Mutations page displays data
- ✅ API endpoints return JSON

### Full Pipeline Test Results:
- ✅ Producer sends messages to Kafka
- ✅ Spark processes batches every 5 seconds
- ✅ Embeddings generated (384 dimensions)
- ✅ Records written to MongoDB
- ✅ Web UI shows new data in real-time

---

## Next Steps After Testing

Once tests pass:
1. Customize narratives in `scripts/run_producer.py`
2. Adjust mutation thresholds in `src/clustering/mutation_detector.py`
3. Add visualizations to the web UI
4. Scale up for production deployment

