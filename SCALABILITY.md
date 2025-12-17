# Scalability & Big Data Strategies

## Overview

This system is **designed to handle millions to billions of records** in a production big data environment. All components are architected with scalability as a primary concern.

## Big Data Assumptions

- **Volume:** Designed for **millions of posts per day** (100M+ records)
- **Velocity:** Real-time streaming processing (thousands of messages/second)
- **Variety:** Multiple data sources (social media, news, forums)
- **Veracity:** Handles noisy, unstructured text data

## Architecture Scalability

### 1. Data Ingestion (Kafka)

**Scalability Strategy:**
- **Kafka Topic Partitioning:** Messages distributed across multiple partitions
- **Parallel Producers:** Multiple producer instances can write to same topic
- **Consumer Groups:** Multiple Spark workers can consume in parallel
- **Replication:** Kafka replicates data across brokers for fault tolerance

**Scaling Approach:**
```
Single Producer → Multiple Partitions → Multiple Consumers
     ↓
Horizontal Scaling: Add more Kafka brokers
     ↓
Throughput: 100K+ messages/second per broker
```

**For Millions of Records:**
- Partition topic by source or time window
- Use Kafka Connect for high-throughput ingestion
- Implement backpressure handling

---

### 2. Distributed Processing (Spark)

**Scalability Strategy:**
- **Micro-batch Processing:** Processes data in small batches (5 seconds)
- **Distributed Computing:** Spark distributes work across cluster nodes
- **Partitioning:** Data automatically partitioned across executors
- **Parallel Embedding Generation:** Batch processing of embeddings

**Scaling Approach:**
```
Local Mode → Spark Cluster (Standalone/YARN/K8s)
     ↓
Horizontal Scaling: Add more worker nodes
     ↓
Processing: Millions of records per hour
```

**For Millions of Records:**
- **Partition Strategy:**
  - Partition by time windows (hourly/daily)
  - Partition by source type
  - Repartition for optimal parallelism
  
- **Memory Management:**
  - Use Spark's memory management
  - Cache frequently accessed data
  - Optimize batch sizes

- **Distributed Embeddings:**
  - Batch embedding generation
  - Distribute across Spark executors
  - Use broadcast variables for model sharing

**Example Configuration for Scale:**
```python
# For production cluster
spark = SparkSession.builder \
    .appName("DisinfoDetector") \
    .master("yarn") \
    .config("spark.executor.memory", "8g") \
    .config("spark.executor.cores", "4") \
    .config("spark.executor.instances", "10") \
    .config("spark.sql.shuffle.partitions", "200") \
    .getOrCreate()
```

---

### 3. Scalable Storage (MongoDB)

**Scalability Strategy:**
- **MongoDB Atlas:** Cloud-hosted, auto-scaling
- **Sharding:** Horizontal partitioning across shards
- **Indexing:** Optimized indexes for fast queries
- **Replication:** High availability with replica sets

**Scaling Approach:**
```
Single Node → Replica Set → Sharded Cluster
     ↓
Horizontal Scaling: Add more shards
     ↓
Storage: Petabytes of data
```

**For Millions of Records:**
- **Sharding Strategy:**
  - Shard by `claim_id` or `timestamp`
  - Distribute load evenly
  - Auto-balancing shards

- **Index Strategy:**
  - Text indexes for search
  - Compound indexes for queries
  - TTL indexes for data expiration

- **Write Optimization:**
  - Batch inserts (already implemented)
  - Bulk write operations
  - Connection pooling

**Example Sharding Configuration:**
```javascript
// Shard by claim_id for even distribution
sh.shardCollection("disinfo_project.narrative_matches", 
                   { "claim_id": 1 })
```

---

### 4. NLP & ML Scalability

**Embedding Generation:**
- **Batch Processing:** Process multiple texts at once
- **Model Caching:** Load model once, reuse across batches
- **Distributed Inference:** Use Spark to distribute embedding generation

**For Millions of Records:**
- **Model Optimization:**
  - Use lighter models for scale (all-MiniLM-L6-v2)
  - Consider model quantization
  - Batch inference (already implemented)

- **Clustering Scalability:**
  - K-means in Spark ML (distributed)
  - Process clusters in parallel
  - Incremental clustering for streaming

**Performance Estimates:**
- Embedding generation: ~1000 texts/second per CPU core
- With 10 Spark executors: ~10,000 texts/second
- Daily capacity: ~864M texts/day

---

### 5. API & Web Interface Scalability

**Current:** Flask (single instance)
**Scalable Approach:**
- **Load Balancing:** Multiple Flask instances behind load balancer
- **Caching:** Redis for frequently accessed data
- **CDN:** Static assets via CDN
- **API Rate Limiting:** Prevent abuse

**Scaling Strategy:**
```
Single Flask → Multiple Instances → Load Balancer
     ↓
Horizontal Scaling: Add more Flask workers
     ↓
Throughput: 10K+ requests/second
```

**For Production:**
- Use Gunicorn with multiple workers
- Deploy on Kubernetes
- Implement caching layer (Redis)
- Use async processing for heavy operations

---

## Performance Benchmarks (Estimated)

### Current Setup (Local)
- **Throughput:** ~100 messages/second
- **Processing:** ~500 texts/minute
- **Storage:** Limited by MongoDB free tier

### Production Scale (Estimated)
- **Throughput:** 10,000+ messages/second
- **Processing:** 50,000+ texts/minute
- **Storage:** Petabytes with sharding
- **Query Performance:** <100ms with proper indexing

---

## Partitioning Strategies

### 1. Kafka Partitioning
- Partition by `source` (reddit, twitter, news)
- Partition by `timestamp` (hourly windows)
- Ensures parallel consumption

### 2. Spark Partitioning
- Partition by time windows
- Repartition for optimal parallelism
- Coalesce to reduce overhead

### 3. MongoDB Sharding
- Shard by `claim_id` (even distribution)
- Shard by `timestamp` (time-based)
- Compound shard key for queries

---

## Challenges & Solutions

### Challenge 1: Memory Constraints
**Problem:** Processing millions of embeddings in memory
**Solution:**
- Batch processing in Spark
- Stream processing (don't load all at once)
- Use disk-based operations when needed

### Challenge 2: Network Latency
**Problem:** MongoDB writes from Spark can be slow
**Solution:**
- Batch inserts (already implemented)
- Async writes
- Connection pooling

### Challenge 3: Model Loading
**Problem:** Sentence-BERT model is large (~80MB)
**Solution:**
- Load once per executor (broadcast)
- Cache model in memory
- Use model serving for scale

### Challenge 4: Real-time Processing
**Problem:** Need low latency for streaming
**Solution:**
- Micro-batch processing (5 seconds)
- Parallel processing
- Optimized Spark configurations

---

## Scaling Roadmap

### Phase 1: Current (Development)
- Single Kafka broker
- Local Spark
- MongoDB Atlas (free tier)
- Single Flask instance

### Phase 2: Production (Small Scale)
- Kafka cluster (3 brokers)
- Spark cluster (5-10 nodes)
- MongoDB sharded cluster
- Load-balanced Flask (3-5 instances)

### Phase 3: Enterprise Scale
- Kafka cluster (10+ brokers)
- Spark cluster (50+ nodes)
- MongoDB sharded cluster (10+ shards)
- Kubernetes deployment
- Auto-scaling based on load

---

## Cost Estimation (AWS Example)

### Small Scale (1M records/day)
- Kafka (MSK): ~$200/month
- Spark (EMR): ~$500/month
- MongoDB Atlas: ~$200/month
- **Total:** ~$900/month

### Enterprise Scale (100M records/day)
- Kafka (MSK): ~$2,000/month
- Spark (EMR): ~$5,000/month
- MongoDB Atlas: ~$2,000/month
- **Total:** ~$9,000/month

---

## Monitoring & Optimization

### Key Metrics to Monitor
- Kafka lag (messages waiting)
- Spark processing time
- MongoDB query performance
- API response times
- Error rates

### Optimization Strategies
- Tune Spark partitions
- Optimize MongoDB indexes
- Cache frequently accessed data
- Use compression for storage

---

## Conclusion

This system is **architected for big data scale** with:
- ✅ Distributed processing (Spark)
- ✅ Scalable storage (MongoDB sharding)
- ✅ Stream processing (Kafka)
- ✅ Horizontal scaling capability
- ✅ Production-ready architecture

**Designed to handle:** Millions to billions of records with proper infrastructure scaling.

