import os
import sys
import glob
import ctypes
import numpy as np

# --- AUTOMATIC WINDOWS FIXER ---
def get_windows_short_path(path):
    """Converts a path with spaces (Program Files) to 8.3 short path (PROGRA~1)"""
    if not os.path.exists(path): return path
    # Buffer for the short path
    buf_size = 256
    buffer = ctypes.create_unicode_buffer(buf_size)
    # Call Windows API to get short path
    get_short = ctypes.windll.kernel32.GetShortPathNameW
    get_short(path, buffer, buf_size)
    return buffer.value

def setup_environment():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. SETUP HADOOP (Local Project)
    hadoop_home = os.path.join(base_dir, 'tools', 'hadoop')
    os.environ['HADOOP_HOME'] = hadoop_home
    
    # Add hadoop/bin to PATH so Windows finds the DLL
    hadoop_bin = os.path.join(hadoop_home, 'bin')
    if hadoop_bin not in os.environ['PATH']:
        os.environ['PATH'] = hadoop_bin + ";" + os.environ['PATH']

    # 2. SETUP JAVA (Auto-Find & Fix Spaces)
    # If JAVA_HOME is already set, fix the spaces
    java_home = os.environ.get('JAVA_HOME')
    
    # If not set, try to find it in default locations
    if not java_home:
        print("Searching for Java...", end=" ")
        possible_paths = glob.glob(r"C:\Program Files\Java\jdk*")
        if possible_paths:
            # Pick the first one found (usually the newest)
            java_home = possible_paths[0]
            print(f"Found: {java_home}")
        else:
            print("\nERROR: Could not find Java in C:\\Program Files\\Java.")
            print("Please install Java 8, 11, or 17.")
            sys.exit(1)

    # Convert to Short Path
    short_java_home = get_windows_short_path(java_home)
    os.environ['JAVA_HOME'] = short_java_home
    
    # Point Spark Python to the current running Python
    os.environ['PYSPARK_PYTHON'] = sys.executable
    os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable

    print(f"Configured JAVA_HOME: {short_java_home}")
    print(f"Configured HADOOP_HOME: {hadoop_home}")

# Run the setup immediately
setup_environment()
# ----------------------------------------

from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from src.clustering.schemas import INPUT_SCHEMA
from src.clustering.vector_utils import cosine_distance

# Configuration
KAFKA_BROKER = "localhost:9092"
TOPIC = "disinformation-stream"

class PlaceholderDetector:
    def __init__(self):
        self.known_vector = np.array([0.5, 0.5, 0.5])

    def check(self, text):
        val = (hash(text) % 100) / 100.0
        vec = np.array([val, val, val])
        dist = cosine_distance(self.known_vector, vec)
        return f"NEW NARRATIVE (Dist: {dist:.2f})" if dist > 0.1 else "Known Narrative"

def process_batch(batch_df, batch_id):
    records = batch_df.collect()
    if not records: return
    print(f"\n--- Processing Batch {batch_id} ({len(records)} records) ---")
    detector = PlaceholderDetector()
    for row in records:
        print(f"{detector.check(row['text'])} | {row['text'][:60]}...")

def main():
    print("Starting Spark Disinformation Detector...")
    
    spark = SparkSession.builder \
        .appName("DisinfoDetectorLocal") \
        .master("local[*]") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
        .config("spark.driver.host", "127.0.0.1") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")

    print("   Connecting to Kafka Stream...")
    df_raw = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BROKER) \
        .option("subscribe", TOPIC) \
        .option("startingOffsets", "latest") \
        .load()

    df_parsed = df_raw.select(
        from_json(col("value").cast("string"), INPUT_SCHEMA).alias("data")
    ).select("data.*")

    query = df_parsed.writeStream \
        .foreachBatch(process_batch) \
        .trigger(processingTime='1 seconds') \
        .start()

    print("Pipeline Running. Waiting for data...")
    query.awaitTermination()

if __name__ == "__main__":
    main()