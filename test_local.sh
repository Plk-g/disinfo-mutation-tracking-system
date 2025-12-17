#!/bin/bash
# Quick local test script

echo "=========================================="
echo "Local Testing Script"
echo "=========================================="
echo ""

# Check if in correct directory
if [ ! -f "scripts/run_producer.py" ]; then
    echo "Error: Please run this from the project root directory"
    exit 1
fi

# Set environment variables
export MONGO_URI="mongodb+srv://pg2820_db_user:BigDataGroup123@cluster0.jwaekxl.mongodb.net/?appName=Cluster0"
export MONGO_DB="disinfo_project"

echo "1. Running quick test..."
python scripts/quick_test.py

echo ""
echo "2. Creating indexes..."
python scripts/create_indexes.py

echo ""
echo "3. Seeding sample data..."
python scripts/seed_sample_data.py

echo ""
echo "=========================================="
echo "Setup complete! Now start Flask:"
echo "  python -m frontend.app"
echo ""
echo "Then visit: http://127.0.0.1:5001"
echo "=========================================="
