# System Architecture

## High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA SOURCES                                  │
├─────────────────────────────────────────────────────────────────┤
│  PolitiFact │ Reddit │ FineWeb │ GDELT │ Laxmimerit │ Synthetic│
└─────────────┴────────┴─────────┴───────┴────────────┴──────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              KAFKA STREAMING LAYER                              │
├─────────────────────────────────────────────────────────────────┤
│  Topic: disinformation-stream                                   │
│  Partitions: Multiple (for parallel processing)                  │
│  Producers: Multiple dataset producers                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│           SPARK STREAMING PROCESSING                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Batch 1    │  │   Batch 2    │  │   Batch N    │          │
│  │  (5 sec)     │  │  (5 sec)     │  │  (5 sec)     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│         │                 │                 │                    │
│         └─────────────────┴─────────────────┘                    │
│                            │                                     │
│         ┌──────────────────┴──────────────────┐                 │
│         │                                      │                 │
│    ┌────▼────┐                          ┌─────▼─────┐          │
│    │Embedding│                          │ Clustering │          │
│    │Generation│                        │ & Drift    │          │
│    │(BERT)   │                          │ Detection  │          │
│    └─────────┘                          └───────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              MONGODB STORAGE LAYER                              │
├─────────────────────────────────────────────────────────────────┤
│  Collections:                                                    │
│  • narrative_matches (sharded by claim_id)                      │
│  • mutation_events (indexed by cluster_id, timestamp)           │
│                                                                  │
│  Features:                                                       │
│  • Text search indexes                                           │
│  • Compound indexes for queries                                  │
│  • TTL indexes for data expiration                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              FLASK API & WEB INTERFACE                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Search     │  │  Mutations  │  │   API        │          │
│  │   Interface  │  │  Dashboard  │  │   Endpoints  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│         │                 │                 │                 │
│         └──────────────────┴─────────────────┘                 │
│                            │                                    │
│                    ┌───────▼────────┐                          │
│                    │  Visualization │                          │
│                    │  (Chart.js)    │                          │
│                    └────────────────┘                          │
└─────────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Data Ingestion
- **Apache Kafka** - Distributed streaming platform
  - Topic: `disinformation-stream`
  - Multiple partitions for parallel processing
  - Producer: `scripts/run_producer.py`

### Distributed Processing
- **Apache Spark** - Distributed computing framework
  - Spark Streaming for real-time processing
  - Spark ML for clustering
  - Micro-batch processing (5-second windows)
  - Location: `main.py`

### Storage
- **MongoDB Atlas** - NoSQL database
  - Collections: `narrative_matches`, `mutation_events`
  - Indexed for fast queries
  - Shardable for horizontal scaling
  - Location: `backend/db/`

### Analytics & ML
- **Sentence-BERT** - NLP embeddings
  - Model: `all-MiniLM-L6-v2`
  - 384-dimensional embeddings
  - Location: `src/clustering/embedding_generator.py`

- **K-means Clustering** - Spark ML
  - Clusters narratives into groups
  - Location: `src/clustering/clusterer.py`

- **Drift Detection** - Custom ML
  - Detects narrative mutations
  - Location: `src/clustering/drift_model.py`

### Interface
- **Flask** - Web framework
  - RESTful API endpoints
  - Web interface
  - Location: `frontend/app.py`

- **Chart.js** - Data visualization
  - Interactive timeline charts
  - Real-time updates
  - Location: `frontend/templates/`

## Data Flow

### 1. Ingestion Phase
```
Data Sources → Kafka Producer → Kafka Topic (disinformation-stream)
```

**Details:**
- Multiple data sources stream to Kafka
- Messages in JSON format
- Schema: `{post_id, text, timestamp, source}`

### 2. Processing Phase
```
Kafka → Spark Streaming → Parse JSON → Generate Embeddings → Cluster → Detect Mutations
```

**Details:**
- Spark consumes from Kafka in micro-batches
- Each batch: Parse → Embed → Cluster → Analyze
- Processed in parallel across Spark executors

### 3. Storage Phase
```
Spark → MongoDB → narrative_matches collection
Spark → MongoDB → mutation_events collection
```

**Details:**
- Batch inserts for efficiency
- Indexed for fast queries
- Sharded for scalability

### 4. Interface Phase
```
MongoDB → Flask API → Web UI → User
```

**Details:**
- RESTful API queries MongoDB
- Web interface displays results
- Real-time analysis and visualization

## Component Details

### Kafka Producer
- **Location:** `scripts/run_producer.py`
- **Function:** Streams data from multiple sources
- **Output:** JSON messages to Kafka topic
- **Scalability:** Multiple producers, partitioned topics

### Spark Consumer
- **Location:** `main.py`
- **Function:** Processes Kafka streams
- **Operations:**
  1. Parse JSON messages
  2. Generate embeddings (Sentence-BERT)
  3. Calculate similarities
  4. Write to MongoDB
- **Scalability:** Distributed across cluster

### MongoDB Layer
- **Location:** `backend/db/`
- **Collections:**
  - `narrative_matches` - Main data
  - `mutation_events` - Mutation tracking
- **Scalability:** Sharding, replication

### Flask Application
- **Location:** `frontend/app.py`
- **Functions:**
  - Search interface
  - Analysis engine
  - API endpoints
  - Mutation dashboard
- **Scalability:** Load balancing, caching

## Scalability Features

1. **Horizontal Scaling:**
   - Kafka: Add more brokers
   - Spark: Add more executors
   - MongoDB: Add more shards
   - Flask: Add more instances

2. **Partitioning:**
   - Kafka: Topic partitioning
   - Spark: Data partitioning
   - MongoDB: Shard partitioning

3. **Parallel Processing:**
   - Spark: Distributed computation
   - Embeddings: Batch processing
   - Clustering: Parallel execution

4. **Caching:**
   - Model caching in Spark
   - Query result caching (can add Redis)

## Performance Characteristics

- **Throughput:** 10,000+ messages/second (with proper scaling)
- **Latency:** <5 seconds (micro-batch processing)
- **Storage:** Petabytes (with MongoDB sharding)
- **Query Performance:** <100ms (with proper indexing)

## Deployment Architecture

### Development (Current)
```
Local Kafka → Local Spark → MongoDB Atlas → Local Flask
```

### Production (Scalable)
```
Kafka Cluster → Spark Cluster → MongoDB Sharded → Load-Balanced Flask
```

## Security Considerations

- Environment variables for credentials
- MongoDB connection string encryption
- Input validation and sanitization
- API rate limiting (can be added)

## Monitoring Points

1. **Kafka:** Message lag, throughput
2. **Spark:** Processing time, batch duration
3. **MongoDB:** Query performance, storage usage
4. **Flask:** API response times, error rates

