# Local Testing Guide

Complete guide to test the Disinformation Mutation Tracking System on your local machine.

## Prerequisites Check

First, verify your setup:

```bash
cd /Users/palakgupta/Desktop/disinfo-mutation-tracking-system/disinfo-mutation-tracking-system
python scripts/quick_test.py
```

This will check:
- Python version
- Environment variables
- Installed packages
- MongoDB connection
- Java installation

---

## Option 1: Quick Test (No Kafka Required) ⚡

**Fastest way to see the system working - perfect for UI testing!**

### Step 1: Set Environment Variables

```bash
export MONGO_URI="mongodb+srv://pg2820_db_user:BigDataGroup123@cluster0.jwaekxl.mongodb.net/?appName=Cluster0"
export MONGO_DB="disinfo_project"
```

**Windows (PowerShell):**
```powershell
$env:MONGO_URI="mongodb+srv://pg2820_db_user:BigDataGroup123@cluster0.jwaekxl.mongodb.net/?appName=Cluster0"
$env:MONGO_DB="disinfo_project"
```

### Step 2: Create MongoDB Indexes

```bash
python scripts/create_indexes.py
```

Expected output: `Indexes created (or already existed).`

### Step 3: Seed Sample Data

```bash
python scripts/seed_sample_data.py
```

Expected output:
```
✓ Inserted 50 narrative match records
✓ Inserted 15 mutation event records
```

### Step 4: Start Flask Web Application

```bash
python -m frontend.app
```

You should see:
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5001
```

### Step 5: Test in Browser

1. **Open:** http://127.0.0.1:5001

2. **Try these test queries:**
   - "Is COVID going to end the world?"
   - "Vaccines contain microchips"
   - "5G causes COVID-19"
   - "The election was stolen"

3. **Check Results:**
   - See fake/real percentages
   - View citations
   - Check mutation information

4. **Visit Mutations Dashboard:**
   - http://127.0.0.1:5001/mutations

---

## Option 2: Full Pipeline Test (Kafka + Spark) 🚀

**Complete end-to-end test with real-time streaming**

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

   You should see `disinformation-stream` in the list (or create it if needed):
   ```bash
   kafka-topics --create --topic disinformation-stream --bootstrap-server localhost:9092
   ```

### Step 1: Set Environment Variables

```bash
export MONGO_URI="mongodb+srv://pg2820_db_user:BigDataGroup123@cluster0.jwaekxl.mongodb.net/?appName=Cluster0"
export MONGO_DB="disinfo_project"
```

### Step 2: Create MongoDB Indexes

```bash
python scripts/create_indexes.py
```

### Step 3: Start Components (3 Terminals)

**Terminal 1 - Kafka Producer:**
```bash
cd /Users/palakgupta/Desktop/disinfo-mutation-tracking-system/disinfo-mutation-tracking-system
export MONGO_URI="mongodb+srv://pg2820_db_user:BigDataGroup123@cluster0.jwaekxl.mongodb.net/?appName=Cluster0"
export MONGO_DB="disinfo_project"

# For synthetic data (always works):
python scripts/run_producer.py

# OR for real datasets, edit scripts/run_producer.py first:
# Change SELECTED_DATASET = "FINEWEB" (or POLITIFACT, REDDIT, etc.)
```

Expected output:
```
Starting Producer with dataset: SYNTHETIC
Topic: disinformation-stream
Broker: localhost:9092
✓ Connected to Kafka

Streaming from SYNTHETIC dataset...
[1] BREAKING: 5G Towers is actually controlled by the government!...
[2] Why is nobody talking about how COVID vaccines caused the pandemic?...
```

**Terminal 2 - Spark Streaming Consumer:**
```bash
cd /Users/palakgupta/Desktop/disinfo-mutation-tracking-system/disinfo-mutation-tracking-system
export MONGO_URI="mongodb+srv://pg2820_db_user:BigDataGroup123@cluster0.jwaekxl.mongodb.net/?appName=Cluster0"
export MONGO_DB="disinfo_project"

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
  [1] BREAKING: 5G Towers... (sim: 0.82)
```

**Terminal 3 - Flask Web Application:**
```bash
cd /Users/palakgupta/Desktop/disinfo-mutation-tracking-system/disinfo-mutation-tracking-system
export MONGO_URI="mongodb+srv://pg2820_db_user:BigDataGroup123@cluster0.jwaekxl.mongodb.net/?appName=Cluster0"
export MONGO_DB="disinfo_project"

python -m frontend.app
```

### Step 4: Verify Real-Time Processing

1. **Watch Terminal 2 (Spark)** - You should see batches being processed every 5 seconds
2. **Check Terminal 1 (Producer)** - Messages being sent
3. **Visit http://127.0.0.1:5001** - Search for narratives
4. **New data should appear** as Spark processes batches

---

## Option 3: Comprehensive System Verification 🔍

**Test all components at once:**

```bash
cd /Users/palakgupta/Desktop/disinfo-mutation-tracking-system/disinfo-mutation-tracking-system
export MONGO_URI="mongodb+srv://pg2820_db_user:BigDataGroup123@cluster0.jwaekxl.mongodb.net/?appName=Cluster0"
export MONGO_DB="disinfo_project"

python scripts/verify_system.py
```

This will test:
- ✅ All imports
- ✅ MongoDB connection
- ✅ NLP embeddings
- ✅ Clustering
- ✅ Flask app
- ✅ Visualization
- ✅ Analysis function

---

## Testing Different Datasets

### Switch to Real Datasets

Edit `scripts/run_producer.py`:

```python
# Line 17 - Change this:
SELECTED_DATASET = "FINEWEB"  # Options: SYNTHETIC, POLITIFACT, LAXMIMERIT, REDDIT, GDELT, FINEWEB
```

**Available Datasets:**
- `SYNTHETIC` - Always works, no internet needed (default)
- `POLITIFACT` - Fact-checked misinformation
- `LAXMIMERIT` - Fake news dataset
- `REDDIT` - Social media posts
- `FINEWEB` - Large web text corpus
- `GDELT` - Live news feed

**Note:** Real datasets require internet connection and may take time to load.

---

## Troubleshooting

### Issue: "Port 5001 already in use"

**Solution:**
```bash
# Find and kill the process
lsof -ti:5001 | xargs kill

# Or use a different port in frontend/app.py:
app.run(debug=True, port=5002)
```

### Issue: "Kafka connection failed"

**Solution:**
1. Check if Kafka is running:
   ```bash
   kafka-topics --list --bootstrap-server localhost:9092
   ```

2. Create topic if needed:
   ```bash
   kafka-topics --create --topic disinformation-stream --bootstrap-server localhost:9092
   ```

3. Restart Kafka if needed

### Issue: "MongoDB connection failed"

**Solution:**
1. Verify MONGO_URI is set:
   ```bash
   echo $MONGO_URI
   ```

2. Test connection:
   ```bash
   python scripts/smoke_test_db.py
   ```

### Issue: "No data in results"

**Solution:**
1. Make sure you seeded data:
   ```bash
   python scripts/seed_sample_data.py
   ```

2. Or wait for Spark to process messages from Kafka

### Issue: "Dataset loading fails"

**Solution:**
- The producer automatically falls back to SYNTHETIC
- Check internet connection for real datasets
- Some datasets may have rate limits

---

## Quick Test Checklist

- [ ] Environment variables set (MONGO_URI, MONGO_DB)
- [ ] MongoDB indexes created
- [ ] Sample data seeded (for quick test)
- [ ] Flask app running on port 5001
- [ ] Can access http://127.0.0.1:5001
- [ ] Search returns results
- [ ] Mutations page loads
- [ ] API endpoints work

---

## Expected Test Results

### Quick Test:
- ✅ Web UI loads
- ✅ Search returns results with fake/real percentages
- ✅ Citations displayed
- ✅ Mutations dashboard shows data

### Full Pipeline:
- ✅ Producer sends messages to Kafka
- ✅ Spark processes batches every 5 seconds
- ✅ Embeddings generated (384 dimensions)
- ✅ Records written to MongoDB
- ✅ Web UI shows new data in real-time

---

## Next Steps After Testing

1. **Customize narratives** - Edit `scripts/run_producer.py`
2. **Adjust thresholds** - Modify mutation detection in `src/clustering/mutation_detector.py`
3. **Add visualizations** - Enhance charts in templates
4. **Scale up** - Deploy to cloud for production

---

## Need Help?

Run the verification script:
```bash
python scripts/verify_system.py
```

This will identify any issues with your setup.

