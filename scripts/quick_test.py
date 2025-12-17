#!/usr/bin/env python3
"""
Quick test script to verify the system setup.
This script checks prerequisites and runs basic functionality tests.
"""

import os
import sys
import subprocess

def check_python_version():
    """Check if Python version is 3.8+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required. Current:", sys.version)
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_environment_variables():
    """Check if required environment variables are set"""
    mongo_uri = os.environ.get("MONGO_URI")
    mongo_db = os.environ.get("MONGO_DB", "disinfo_project")
    
    if not mongo_uri:
        print("❌ MONGO_URI environment variable not set")
        print("   Set it with: export MONGO_URI='your_mongodb_uri'")
        return False
    
    print(f"✓ MONGO_URI is set")
    print(f"✓ MONGO_DB: {mongo_db}")
    return True

def check_imports():
    """Check if required packages are installed"""
    required_packages = [
        ("flask", "Flask"),
        ("pymongo", "PyMongo"),
        ("sentence_transformers", "Sentence Transformers"),
        ("pyspark", "PySpark"),
        ("kafka", "kafka-python"),
    ]
    
    missing = []
    for module, name in required_packages:
        try:
            __import__(module)
            print(f"✓ {name} installed")
        except ImportError:
            print(f"❌ {name} not installed")
            missing.append(name)
    
    if missing:
        print(f"\nInstall missing packages: pip install {' '.join(missing)}")
        return False
    return True

def test_mongodb_connection():
    """Test MongoDB connection"""
    try:
        # Add project root to path
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        from backend.db.mongo_client import get_db
        db = get_db()
        # Try to list collections
        collections = db.list_collection_names()
        print(f"✓ MongoDB connected (found {len(collections)} collections)")
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

def test_imports():
    """Test if project modules can be imported"""
    try:
        # Add project root to path
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        from backend.db.queries import insert_matches, get_top_claims
        from src.clustering.drift_model import DriftModel
        from src.clustering.embedding_generator import generate_embeddings_batch
        print("✓ Project modules import successfully")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_java():
    """Check if Java is installed (for Spark)"""
    try:
        result = subprocess.run(
            ["java", "-version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            version_line = (result.stdout or result.stderr).split('\n')[0]
            print(f"✓ Java installed: {version_line}")
            return True
    except FileNotFoundError:
        print("⚠ Java not found (required for Spark streaming)")
        print("   Install Java 8, 11, or 17 and set JAVA_HOME")
        return False
    return False

def main():
    print("=" * 60)
    print("Disinformation Mutation Tracking System - Quick Test")
    print("=" * 60)
    print()
    
    results = []
    
    print("1. Checking Python version...")
    results.append(("Python", check_python_version()))
    print()
    
    print("2. Checking environment variables...")
    results.append(("Environment", check_environment_variables()))
    print()
    
    print("3. Checking Python packages...")
    results.append(("Packages", check_imports()))
    print()
    
    print("4. Testing project imports...")
    results.append(("Imports", test_imports()))
    print()
    
    if os.environ.get("MONGO_URI"):
        print("5. Testing MongoDB connection...")
        results.append(("MongoDB", test_mongodb_connection()))
        print()
    else:
        print("5. Skipping MongoDB test (MONGO_URI not set)")
        results.append(("MongoDB", None))
        print()
    
    print("6. Checking Java installation...")
    results.append(("Java", check_java()))
    print()
    
    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = 0
    failed = 0
    skipped = 0
    
    for name, result in results:
        if result is None:
            status = "⏭ SKIPPED"
            skipped += 1
        elif result:
            status = "✓ PASS"
            passed += 1
        else:
            status = "❌ FAIL"
            failed += 1
        print(f"{status} - {name}")
    
    print()
    print(f"Passed: {passed}, Failed: {failed}, Skipped: {skipped}")
    print()
    
    if failed == 0:
        print("🎉 All checks passed! You're ready to test the system.")
        print()
        print("Next steps:")
        print("  1. Create indexes: python scripts/create_indexes.py")
        print("  2. Seed data: python scripts/seed_sample_data.py")
        print("  3. Start Flask: python -m frontend.app")
        print("  4. Visit: http://127.0.0.1:5000")
    else:
        print("⚠ Some checks failed. Please fix the issues above.")
        print()
        print("Common fixes:")
        print("  - Install dependencies: pip install -r requirements.txt")
        print("  - Set MONGO_URI: export MONGO_URI='your_uri'")
        print("  - Install Java for Spark streaming")
    
    print()
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

