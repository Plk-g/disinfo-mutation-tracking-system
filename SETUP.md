# Setup Guide - Disinformation Mutation Tracking System

This guide will help you set up and run the complete system.

## Prerequisites

### 1. Python Environment
- Python 3.8 or higher
- pip package manager

### 2. Java (for Spark)
- Java 8, 11, or 17
- Set `JAVA_HOME` environment variable

**macOS:**
```bash
brew install openjdk@11
export JAVA_HOME=$(/usr/libexec/java_home -v 11)
```

**Linux:**
```bash
sudo apt-get install openjdk-11-jdk
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
```

**Windows:**
- Download and install JDK from Oracle or use OpenJDK
- Set `JAVA_HOME` in System Environment Variables

### 3. Apache Kafka (for streaming pipeline)
Download and install Kafka from https://kafka.apache.org/downloads

**Quick Start Kafka:**
```bash
# Terminal 1 - Start Zookeeper
bin/zookeeper-server-start.sh config/zookeeper.properties

# Terminal 2 - Start Kafka
bin/kafka-server-start.sh config/server.properties
```

### 4. MongoDB
- MongoDB Atlas account (cloud) OR local MongoDB instance
- Connection URI for your database

## Installation Steps

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Note:** The first run will download the Sentence-BERT model (~80MB), which may take a few minutes.

### Step 2: Configure Environment Variables

Create a `.env` file or export these variables:

```bash
export MONGO_URI="mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority"
export MONGO_DB="disinfo_project"
```

**For Windows (PowerShell):**
```powershell
$env:MONGO_URI="mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority"
$env:MONGO_DB="disinfo_project"
```

### Step 3: Create MongoDB Indexes

```bash
python scripts/create_indexes.py
```

This creates indexes for efficient querying.

### Step 4: Verify Setup

Test MongoDB connection:
```bash
python scripts/smoke_test_db.py
```

## Running the System

### Option A: Quick Demo (No Kafka Required)

This is the fastest way to see the system in action:

1. **Seed sample data:**
   ```bash
   python scripts/seed_sample_data.py
   ```

2. **Start Flask app:**
   ```bash
   python -m frontend.app
   ```

3. **Open browser:**
   - Search: http://127.0.0.1:5000
   - Mutations: http://127.0.0.1:5000/mutations

### Option B: Full Streaming Pipeline

This runs the complete Kafka → Spark → MongoDB pipeline:

**Terminal 1 - Start Kafka Producer:**
```bash
python scripts/run_producer.py
```

This will continuously send sample disinformation narratives to Kafka.

**Terminal 2 - Start Spark Streaming Consumer:**
```bash
python main.py
```

This processes messages from Kafka, generates embeddings, and writes to MongoDB.

**Terminal 3 - Start Flask Web UI:**
```bash
python -m frontend.app
```

Visit http://127.0.0.1:5000 to see real-time results.

## Troubleshooting

### Issue: "JAVA_HOME not set"
**Solution:** Set JAVA_HOME to your Java installation directory.

### Issue: "Kafka connection failed"
**Solution:** 
- Ensure Kafka is running on `localhost:9092`
- Check if the topic exists: `kafka-topics --list --bootstrap-server localhost:9092`
- Create topic manually: `kafka-topics --create --topic disinformation-stream --bootstrap-server localhost:9092`

### Issue: "MongoDB connection failed"
**Solution:**
- Verify MONGO_URI is correct
- Check network connectivity
- Ensure MongoDB Atlas IP whitelist includes your IP (if using Atlas)

### Issue: "Sentence-BERT model download fails"
**Solution:**
- Check internet connection
- The model downloads automatically on first use
- Model size: ~80MB

### Issue: "Spark checkpoint errors"
**Solution:**
- Checkpoint directory is created automatically at `~/.spark-checkpoint`
- Ensure you have write permissions
- Delete checkpoint directory to reset: `rm -rf ~/.spark-checkpoint`

## Project Structure

```
disinfo-mutation-tracking-system/
├── backend/              # MongoDB database layer
├── frontend/             # Flask web application
├── src/clustering/       # ML models (embeddings, clustering, drift)
├── scripts/              # Utility scripts
├── main.py              # Spark streaming consumer
└── requirements.txt     # Python dependencies
```

## Next Steps

1. **Customize narratives:** Edit `scripts/run_producer.py` to add your own disinformation samples
2. **Adjust thresholds:** Modify mutation detection thresholds in `src/clustering/mutation_detector.py`
3. **Enhance UI:** Add visualizations in `frontend/templates/`
4. **Scale up:** Deploy to cloud infrastructure for production use

## Support

For issues or questions, check:
- `docs/data_contract.md` - Data schema documentation
- `docs/storage_design.md` - Database design
- README.md - General project overview

