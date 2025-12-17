# Quick Start - Testing the System

Follow these steps to test the system quickly.

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Flask (web framework)
- PyMongo (MongoDB client)
- Sentence Transformers (for embeddings)
- PySpark (for streaming)
- kafka-python (for Kafka producer)

**Note:** The first time you use Sentence Transformers, it will download a model (~80MB).

## Step 2: Set Environment Variables

You need your MongoDB connection string. If you're using MongoDB Atlas:

```bash
export MONGO_URI="mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority"
export MONGO_DB="disinfo_project"
```

**Windows (PowerShell):**
```powershell
$env:MONGO_URI="mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority"
$env:MONGO_DB="disinfo_project"
```

## Step 3: Run Quick Test

Check if everything is set up correctly:

```bash
python scripts/quick_test.py
```

This will verify:
- Python version
- Environment variables
- Installed packages
- MongoDB connection
- Project imports

## Step 4: Create MongoDB Indexes

```bash
python scripts/create_indexes.py
```

## Step 5: Seed Sample Data

This populates the database with test data so you can see the system working:

```bash
python scripts/seed_sample_data.py
```

You should see:
```
✓ Inserted 50 narrative match records
✓ Inserted 15 mutation event records
```

## Step 6: Start the Web Application

```bash
python -m frontend.app
```

You should see:
```
 * Running on http://127.0.0.1:5000
```

## Step 7: Test in Browser

1. **Open:** http://127.0.0.1:5000

2. **Try searching for:**
   - "vaccine"
   - "5G"
   - "election"
   - "COVID"

3. **View mutations:** http://127.0.0.1:5000/mutations

4. **Test API endpoints:**
   - http://127.0.0.1:5000/api/search?query=vaccine
   - http://127.0.0.1:5000/api/top_claims?k=5
   - http://127.0.0.1:5000/api/mutations/top?k=5

## That's It! 🎉

You should now see:
- Search results with similarity scores
- Mutation dashboard with top mutations
- API endpoints returning JSON data

## Next: Test Full Pipeline (Optional)

If you want to test the complete Kafka → Spark → MongoDB pipeline:

1. **Start Kafka** (if you have it installed)
2. **Terminal 1:** `python scripts/run_producer.py`
3. **Terminal 2:** `python main.py`
4. **Terminal 3:** `python -m frontend.app`

See `TESTING.md` for detailed instructions.

## Troubleshooting

**"Module not found" errors:**
```bash
pip install -r requirements.txt
```

**"MONGO_URI not set":**
Make sure you exported the environment variable in the same terminal session.

**"Connection failed":**
- Check your MongoDB URI is correct
- Verify network connectivity
- If using Atlas, check IP whitelist

**Port 5000 already in use:**
```bash
# Find and kill the process
lsof -ti:5000 | xargs kill
```

