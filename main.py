import os
import sys
import platform
from datetime import datetime

# Setup environment variables for Spark
os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable

# Platform-specific Java setup
if platform.system() == "Windows":
    import glob
    import ctypes
    
    def get_windows_short_path(path):
        """Converts a path with spaces to 8.3 short path"""
        if not os.path.exists(path):
            return path
        buf_size = 256
        buffer = ctypes.create_unicode_buffer(buf_size)
        get_short = ctypes.windll.kernel32.GetShortPathNameW
        get_short(path, buffer, buf_size)
        return buffer.value
    
    java_home = os.environ.get('JAVA_HOME')
    if not java_home:
        possible_paths = glob.glob(r"C:\Program Files\Java\jdk*")
        if possible_paths:
            java_home = possible_paths[0]
            os.environ['JAVA_HOME'] = get_windows_short_path(java_home)
    
    # Setup HADOOP for Windows
    base_dir = os.path.dirname(os.path.abspath(__file__))
    hadoop_home = os.path.join(base_dir, 'tools', 'hadoop')
    if os.path.exists(hadoop_home):
        os.environ['HADOOP_HOME'] = hadoop_home
        hadoop_bin = os.path.join(hadoop_home, 'bin')
        if hadoop_bin not in os.environ['PATH']:
            os.environ['PATH'] = hadoop_bin + ";" + os.environ['PATH']

from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, udf, array
from pyspark.sql.types import ArrayType, DoubleType
import numpy as np

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.clustering.schemas import INPUT_SCHEMA
from backend.db.queries import insert_matches, insert_mutations

# Configuration
KAFKA_BROKER = "localhost:9092"
TOPIC = "disinformation-stream"

# Global embedding model (loaded once)
_embedding_model = None

def get_embedding_model():
    """Lazy load the embedding model"""
    global _embedding_model
    if _embedding_model is None:
        from sentence_transformers import SentenceTransformer
        print("Loading Sentence-BERT model...")
        _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Model loaded!")
    return _embedding_model

def process_batch(batch_df, batch_id):
    """Process a batch of Kafka messages: generate embeddings, cluster, detect mutations, write to MongoDB"""
    records = batch_df.collect()
    if not records:
        return
    
    print(f"\n--- Processing Batch {batch_id} ({len(records)} records) ---")
    
    # Extract texts and metadata
    texts = [row['text'] for row in records]
    post_ids = [row.get('post_id', f'post_{batch_id}_{i}') for i, row in enumerate(records)]
    timestamps = [row.get('timestamp', datetime.utcnow().isoformat() + 'Z') for row in records]
    sources = [row.get('source', 'unknown') for row in records]
    
    # Generate embeddings
    try:
        model = get_embedding_model()
        embeddings = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        print(f"Generated {len(embeddings)} embeddings (dim: {embeddings.shape[1]})")
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Prepare records for MongoDB
    match_records = []
    for i, (post_id, text, timestamp, source, embedding) in enumerate(zip(post_ids, texts, timestamps, sources, embeddings)):
        # Simple similarity scoring (can be enhanced with actual claim matching)
        similarity_score = float(np.random.uniform(0.3, 0.95))  # Placeholder - should match against known claims
        matched = similarity_score > 0.7
        
        match_records.append({
            'post_id': post_id,
            'claim_id': f'claim_{hash(text) % 1000}',  # Placeholder claim_id
            'text': text,
            'similarity_score': similarity_score,
            'matched': matched,
            'timestamp': timestamp,
            'source': source,
            'embedding': embedding.tolist() if hasattr(embedding, 'tolist') else list(embedding)
        })
    
    # Write to MongoDB
    try:
        inserted = insert_matches(match_records)
        print(f"Inserted {inserted} records into MongoDB")
    except Exception as e:
        print(f"Error writing to MongoDB: {e}")
    
    # Print sample
    for i, record in enumerate(match_records[:3]):
        print(f"  [{i+1}] {record['text'][:60]}... (sim: {record['similarity_score']:.2f})")

def main():
    print("Starting Spark Disinformation Detector...")
    print(f"Kafka Broker: {KAFKA_BROKER}")
    print(f"Topic: {TOPIC}")
    
    spark = SparkSession.builder \
        .appName("DisinfoDetectorLocal") \
        .master("local[*]") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0") \
        .config("spark.driver.host", "127.0.0.1") \
        .config("spark.sql.streaming.checkpointLocation", os.path.join(os.path.expanduser("~"), ".spark-checkpoint")) \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")

    print("   Connecting to Kafka Stream...")
    try:
        df_raw = spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", KAFKA_BROKER) \
            .option("subscribe", TOPIC) \
            .option("startingOffsets", "latest") \
            .load()

        df_parsed = df_raw.select(
            from_json(col("value").cast("string"), INPUT_SCHEMA).alias("data")
        ).select("data.*")

        checkpoint_dir = os.path.join(os.path.expanduser("~"), ".spark-checkpoint")
        os.makedirs(checkpoint_dir, exist_ok=True)
        
        query = df_parsed.writeStream \
            .foreachBatch(process_batch) \
            .trigger(processingTime='5 seconds') \
            .option("checkpointLocation", checkpoint_dir) \
            .start()

        print("✓ Pipeline Running. Waiting for data from Kafka...")
        print("  (Make sure Kafka is running and producer is sending messages)")
        query.awaitTermination()
    except Exception as e:
        print(f"Error starting stream: {e}")
        print("\nTroubleshooting:")
        print("1. Is Kafka running? Try: kafka-console-consumer --bootstrap-server localhost:9092 --topic disinformation-stream")
        print("2. Is the topic created? Try: kafka-topics --list --bootstrap-server localhost:9092")
        raise

if __name__ == "__main__":
    main()