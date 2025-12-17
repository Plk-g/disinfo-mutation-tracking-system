#!/usr/bin/env python3
"""
Complete end-to-end pipeline runner.
This script helps coordinate the full pipeline: Kafka Producer → Spark Consumer → MongoDB → Flask UI

Usage:
    python scripts/run_complete_pipeline.py --producer-only    # Just run producer
    python scripts/run_complete_pipeline.py --spark-only       # Just run Spark
    python scripts/run_complete_pipeline.py --flask-only        # Just run Flask
    python scripts/run_complete_pipeline.py                     # Run all (requires multiple terminals)
"""

import argparse
import subprocess
import sys
import os
import time

def run_producer():
    """Run the Kafka producer"""
    print("=" * 60)
    print("Starting Kafka Producer...")
    print("=" * 60)
    script_path = os.path.join(os.path.dirname(__file__), "run_producer.py")
    subprocess.run([sys.executable, script_path])

def run_spark():
    """Run the Spark streaming consumer"""
    print("=" * 60)
    print("Starting Spark Streaming Consumer...")
    print("=" * 60)
    main_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "main.py")
    subprocess.run([sys.executable, main_path])

def run_flask():
    """Run the Flask web application"""
    print("=" * 60)
    print("Starting Flask Web Application...")
    print("=" * 60)
    print("Access the UI at: http://127.0.0.1:5000")
    print("=" * 60)
    app_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "app.py")
    subprocess.run([sys.executable, app_path])

def main():
    parser = argparse.ArgumentParser(description="Run the disinformation mutation tracking pipeline")
    parser.add_argument("--producer-only", action="store_true", help="Run only the Kafka producer")
    parser.add_argument("--spark-only", action="store_true", help="Run only the Spark consumer")
    parser.add_argument("--flask-only", action="store_true", help="Run only the Flask app")
    
    args = parser.parse_args()
    
    if args.producer_only:
        run_producer()
    elif args.spark_only:
        run_spark()
    elif args.flask_only:
        run_flask()
    else:
        print("""
╔══════════════════════════════════════════════════════════════╗
║  Disinformation Mutation Tracking System - Pipeline Runner  ║
╚══════════════════════════════════════════════════════════════╝

This system requires multiple components running simultaneously.

To run the complete pipeline, open 3 separate terminals:

Terminal 1 - Kafka Producer:
  python scripts/run_complete_pipeline.py --producer-only

Terminal 2 - Spark Streaming:
  python scripts/run_complete_pipeline.py --spark-only

Terminal 3 - Flask Web UI:
  python scripts/run_complete_pipeline.py --flask-only

Or run them individually:
  python scripts/run_producer.py
  python main.py
  python -m frontend.app

Prerequisites:
  ✓ Kafka running on localhost:9092
  ✓ MongoDB accessible (MONGO_URI env var set)
  ✓ Java installed (for Spark)
  ✓ Python dependencies installed (pip install -r requirements.txt)
        """)
        
        response = input("\nWould you like to start the Flask UI now? (y/n): ")
        if response.lower() == 'y':
            run_flask()

if __name__ == "__main__":
    main()

