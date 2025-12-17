# Quick Start Commands

Run these commands **in order** in your terminal:

## Step 1: Navigate to the project directory

```bash
cd /Users/palakgupta/Desktop/disinfo-mutation-tracking-system/disinfo-mutation-tracking-system
```

## Step 2: Set environment variables

```bash
export MONGO_URI="mongodb+srv://pg2820_db_user:BigDataGroup123@cluster0.jwaekxl.mongodb.net/?appName=Cluster0"
export MONGO_DB="disinfo_project"
```

## Step 3: Verify environment variables are set

```bash
echo $MONGO_URI
echo $MONGO_DB
```

You should see your MongoDB URI and "disinfo_project" printed.

## Step 4: Run quick test

```bash
python scripts/quick_test.py
```

## Step 5: Create indexes

```bash
python scripts/create_indexes.py
```

## Step 6: Seed sample data

```bash
python scripts/seed_sample_data.py
```

## Step 7: Start Flask app

```bash
python -m frontend.app
```

## Step 8: Open browser

Visit: http://127.0.0.1:5000

---

**Important:** Make sure you're in the correct directory before running any commands. The project is in:
`/Users/palakgupta/Desktop/disinfo-mutation-tracking-system/disinfo-mutation-tracking-system/`

