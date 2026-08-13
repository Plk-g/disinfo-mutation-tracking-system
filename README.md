# Disinformation Topic Mutation Tracking System

**Course:** CSGY 6513 - Big Data  
**Team:** Palak Gupta, Eric Zhang, Samradnyee Shinde, Shreya Srinivasan Bharadwaj, Xiangping Liu

A real-time Big Data pipeline to detect, track, and visualize the evolution ("mutation") of online disinformation narratives across large-scale text sources. The system uses streaming data processing, NLP embeddings, and clustering to identify how misinformation claims transform as they spread through communities.

## 🎯 Project Overview

This system tracks how disinformation narratives mutate over time by:
- Processing streaming text data from multiple sources
- Generating semantic embeddings using Sentence-BERT
- Clustering narratives and detecting topic drift
- Visualizing narrative evolution and mutation patterns
- Providing real-time analysis of news authenticity

## 🏗️ System Architecture

```
Data Sources (PolitiFact, Reddit, FineWeb, GDELT, etc.)
         ↓
    Kafka Streaming
         ↓
  Spark Streaming (NLP + Clustering)
         ↓
    MongoDB Storage
         ↓
  Flask API + Web UI
         ↓
  Interactive Dashboard
```

### Technology Stack

- **Data Ingestion:** Apache Kafka (distributed streaming)
- **Processing:** Apache Spark Streaming (distributed computing)
- **Storage:** MongoDB Atlas (scalable NoSQL database)
- **NLP:** Sentence-BERT embeddings (384 dimensions)
- **ML:** K-means clustering, topic drift detection
- **Interface:** Flask web application with Chart.js visualizations

## 📋 Features

### Core Functionality
- **Real-time Analysis:** Analyze news articles for authenticity (fake/real percentage)
- **Source Citations:** View similar narratives with source attribution
- **Mutation Tracking:** Track how disinformation narratives evolve over time
- **Interactive Dashboard:** Visualize mutation timelines and drift patterns
- **RESTful API:** Programmatic access to analysis results

### Data Sources
- PolitiFact (fact-checked misinformation)
- Reddit (social media posts)
- FineWeb (large web text corpus)
- GDELT (live news feed)
- Laxmimerit (fake news dataset)
- Synthetic data (for testing)

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Java 8, 11, or 17 (for Spark)
- MongoDB Atlas account or local MongoDB
- Apache Kafka (for full pipeline)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd disinfo-mutation-tracking-system
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables:**
   ```bash
   export MONGO_URI="mongodb+srv://<username>:<password>@cluster.mongodb.net/?retryWrites=true&w=majority"
   export MONGO_DB="disinfo_project"
   ```
   
   **Or use a `.env` file:**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials, then load it:
   set -a && source .env && set +a
   ```

4. **Create MongoDB indexes:**
   ```bash
   python scripts/create_indexes.py
   ```

### Running the System

#### Option 1: Quick Demo (No Kafka Required)

```bash
# Seed sample data
python scripts/seed_sample_data.py

# Start Flask application
python -m frontend.app

# Visit http://127.0.0.1:5001
```

#### Option 2: Full Pipeline

**Terminal 1 - Kafka Producer:**
```bash
python scripts/run_producer.py
```

**Terminal 2 - Spark Streaming:**
```bash
python main.py
```

**Terminal 3 - Flask Web UI:**
```bash
python -m frontend.app
```

## 📁 Project Structure

```
disinfo-mutation-tracking-system/
├── backend/
│   └── db/                    # MongoDB database layer
│       ├── mongo_client.py    # Database connection
│       └── queries.py         # Query functions
│
├── frontend/
│   ├── app.py                 # Flask application
│   ├── templates/             # HTML templates
│   │   ├── index.html         # Search interface
│   │   ├── results.html       # Analysis results
│   │   └── mutations.html     # Mutation dashboard
│   └── static/
│       └── styles.css         # Styling
│
├── src/
│   └── clustering/            # ML and analytics
│       ├── clusterer.py       # K-means clustering
│       ├── drift_model.py    # Topic drift detection
│       ├── mutation_detector.py
│       ├── embedding_generator.py  # Sentence-BERT
│       └── vector_utils.py    # Vector operations
│
├── scripts/
│   ├── run_producer.py        # Kafka producer
│   ├── seed_sample_data.py    # Sample data generator
│   ├── create_indexes.py     # MongoDB indexes
│   └── verify_system.py      # System verification
│
├── docs/
│   ├── data_contract.md      # Data schema
│   └── storage_design.md     # Database design
│
├── main.py                   # Spark streaming consumer
├── requirements.txt          # Pinned Python dependencies
├── .env.example              # Env var template (copy to .env)
├── ARCHITECTURE.md           # System architecture
├── SETUP.md                  # Detailed setup
└── README.md                 # This file
```

## 🔧 Configuration

### Kafka Configuration

Edit `scripts/run_producer.py` to select dataset:
```python
SELECTED_DATASET = "FINEWEB"  # Options: SYNTHETIC, POLITIFACT, REDDIT, FINEWEB, GDELT
TOPIC_NAME = "disinformation-stream"
KAFKA_BROKER = "localhost:9092"
```

### MongoDB Configuration

Set environment variables:
```bash
export MONGO_URI="your_mongodb_connection_string"
export MONGO_DB="disinfo_project"
```

## 📊 API Endpoints

### Web Interface
- `GET /` - Search interface
- `POST /search` - Analyze news article
- `GET /mutations` - Mutation dashboard

### REST API
- `GET /api/search?query=<text>&limit=20` - Search narratives
- `GET /api/top_claims?k=10` - Top claims by frequency
- `GET /api/claim/<claim_id>?limit=50` - Matches for a claim
- `GET /api/mutations/top?k=10` - Top mutations
- `GET /api/mutations/timeline?cluster_id=<id>` - Mutation timeline

## 🧪 Testing

### System Verification
```bash
python scripts/verify_system.py
```

This tests:
- MongoDB connection
- NLP embeddings
- Clustering functionality
- Flask application
- Data visualization

### Quick Test
```bash
python scripts/quick_test.py
```

## 📈 Scalability

The system is designed to handle **millions to billions of records**:

- **Kafka:** Topic partitioning for parallel processing
- **Spark:** Distributed processing across cluster nodes
- **MongoDB:** Sharding for horizontal scaling
- **Processing Capacity:** 10,000+ messages/second (with proper scaling)

See `SCALABILITY.md` for detailed scalability strategies.

## 🏛️ Architecture

For detailed architecture documentation, see:
- `ARCHITECTURE.md` - System architecture and data flow
- `SCALABILITY.md` - Scaling strategies and performance
- `docs/data_contract.md` - Data schema definitions

## 🔒 Security

- Environment variables for credentials (never hardcoded)
- Input validation and sanitization
- Regex injection prevention
- Parameter validation on all API endpoints

## 📝 Documentation

- `README.md` - Project overview and quick start (this file)
- `SETUP.md` - Detailed setup instructions
- `QUICK_START.md` - Short command cheat sheet
- `TESTING.md` - Testing guide
- `ARCHITECTURE.md` - System architecture and data flow
- `SCALABILITY.md` - Scaling notes
- `docs/data_contract.md` - Kafka / Mongo schemas

## 🤝 Contributing

This is a course project. For questions or issues, contact the team members.

## 📄 License

This project is part of CSGY 6513 - Big Data course work.

## 🙏 Acknowledgments

- Sentence-BERT for embeddings
- Apache Spark and Kafka communities
- MongoDB Atlas for database hosting
- Bootstrap and Chart.js for UI components

---

**Last Updated:** December 2025
