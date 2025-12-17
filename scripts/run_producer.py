# scripts/run_producer.py
import time
import json
import uuid
import random
import requests
import pandas as pd
import io
import datetime
import hashlib
from kafka import KafkaProducer
from datasets import load_dataset
from bs4 import BeautifulSoup

SELECTED_DATASET = "SYNTHETIC"
TOPIC_NAME = "disinformation-stream"
KAFKA_BROKER = "localhost:9092"

GLOBAL_HASH_MEMORY = set()

def generate_synthetic_stream():
    """Generate synthetic disinformation narratives"""
    templates = [
        "BREAKING: {subject} is actually {action} by {actor}!",
        "Why is nobody talking about how {subject} caused {event}?",
        "Leaked documents prove {actor} is covering up {subject}.",
        "{subject} has been {action} and the media won't tell you!",
        "Scientists discover {subject} is linked to {event}."
    ]
    subjects = ["Vitamin C", "5G Towers", "The Election", "Tap Water", "COVID vaccines", "Masks"]
    actions = ["poisoned", "faked", "controlled", "deleted", "manipulated"]
    actors = ["the government", "the company", "big pharma", "the media"]
    events = ["the pandemic", "the blackout", "mind control", "population control"]

    while True:
        text = random.choice(templates).format(
            subject=random.choice(subjects),
            action=random.choice(actions),
            actor=random.choice(actors),
            event=random.choice(events)
        )
        yield {"text": text, "source": "Synthetic_Bot"}

def stream_huggingface(dataset_name, subset, split="train", text_col="text"):
    """Stream data from HuggingFace datasets"""
    try:
        print(f"Loading HuggingFace dataset: {dataset_name}/{subset}")
        ds = load_dataset(dataset_name, subset, split=split, streaming=True)
        for row in ds:
            text = row.get(text_col, "")
            if text and len(text) > 10:  # Filter out empty or very short texts
                yield {
                    "text": str(text)[:1000],  # Limit text length
                    "source": dataset_name
                }
    except Exception as e:
        print(f"Hugging Face Error: {e}")
        print("Falling back to synthetic stream...")
        yield from generate_synthetic_stream()

def stream_csv_url(url, source_name):
    """Stream data from a CSV URL"""
    print(f"Connecting to {source_name}...")
    try:
        with requests.get(url, stream=True, timeout=10) as r:
            r.raise_for_status()
            lines = (line.decode('utf-8') for line in r.iter_lines())
            chunks = pd.read_csv(io.StringIO("\n".join(lines)), chunksize=1)
            for chunk in chunks:
                if not chunk.empty:
                    # Handle different column names
                    text = chunk.iloc[0].get('title') or chunk.iloc[0].get('news_title') or chunk.iloc[0].get('text') or str(chunk.iloc[0].values[0])
                    if text and len(str(text)) > 10:
                        yield {"text": str(text), "source": source_name}
    except Exception as e:
        print(f"CSV Error: {e}")
        print("Falling back to synthetic stream...")
        yield from generate_synthetic_stream()

def scrape_article_text(url):
    """Scrape text from a URL"""
    if not url or "http" not in str(url):
        return None

    # Pretend to be a Chrome on Windows
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        headline = soup.find('h1').get_text().strip() if soup.find('h1') else ""
        paragraphs = soup.find_all('p')
        body_text = " ".join([p.get_text().strip() for p in paragraphs[:3]])
        full_text = f"{headline}. {body_text}"

        if len(full_text) > 50:
            return full_text
        return None

    except Exception:
        return None
    
def stream_gdelt_live():
    """Stream live data from GDELT"""
    global GLOBAL_HASH_MEMORY
    try:
        print("Connecting to GDELT...")
        master = requests.get("http://data.gdeltproject.org/gdeltv2/lastupdate.txt", timeout=10).text
        csv_url = master.split('\n')[0].split(' ')[2]
        df = pd.read_csv(csv_url, sep='\t', header=None, names=range(61))
        for _, row in df.iterrows():
            target_url = str(row[60])
            scraped_text = scrape_article_text(target_url)
            if scraped_text:
                text_hash = hashlib.md5(scraped_text.encode('utf-8')).hexdigest()
                if text_hash in GLOBAL_HASH_MEMORY:
                    continue
                GLOBAL_HASH_MEMORY.add(text_hash)
                yield {
                    "text": scraped_text,
                    "source": "GDELT"
                }
    except Exception as e:
        print(f"GDELT Error: {e}")
        print("Falling back to synthetic stream...")
        yield from generate_synthetic_stream()

def get_stream():
    """Get data stream based on selected dataset"""
    if SELECTED_DATASET == "SYNTHETIC":
        return generate_synthetic_stream()
    elif SELECTED_DATASET == "POLITIFACT":
        return stream_csv_url("https://raw.githubusercontent.com/KaiDMML/FakeNewsNet/master/dataset/politifact_fake.csv", "PolitiFact")
    elif SELECTED_DATASET == "LAXMIMERIT":
        return stream_csv_url("https://raw.githubusercontent.com/laxmimerit/fake-real-news-dataset/main/data/Fake.csv", "Laxmimerit")
    elif SELECTED_DATASET == "REDDIT":
        return stream_huggingface("jamescalam/reddit-python", "default", text_col="title")
    elif SELECTED_DATASET == "FINEWEB":
        return stream_huggingface("HuggingFaceFW/fineweb", "sample-10BT")
    elif SELECTED_DATASET == "GDELT":
        return stream_gdelt_live()
    else:
        print(f"Unknown dataset: {SELECTED_DATASET}, using SYNTHETIC")
        return generate_synthetic_stream()

if __name__ == "__main__":
    print(f"Starting Producer with dataset: {SELECTED_DATASET}")
    print(f"Topic: {TOPIC_NAME}")
    print(f"Broker: {KAFKA_BROKER}")
    
    try:
        producer = KafkaProducer(
            bootstrap_servers=[KAFKA_BROKER],
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
        print("✓ Connected to Kafka")
    except Exception as e:
        print(f"✗ Error connecting to Kafka: {e}")
        print("\nMake sure Kafka is running:")
        print("  - Start Zookeeper: zookeeper-server-start.sh config/zookeeper.properties")
        print("  - Start Kafka: kafka-server-start.sh config/server.properties")
        sys.exit(1)

    stream = get_stream()
    count = 0

    print(f"\nStreaming from {SELECTED_DATASET} dataset...")
    print("Press Ctrl+C to stop\n")

    try:
        for raw in stream:
            count += 1
            msg = {
                "post_id": str(uuid.uuid4()),
                "text": raw['text'],
                "source": raw['source'],
                "timestamp": datetime.datetime.now().isoformat() + "Z"
            }
            
            producer.send(TOPIC_NAME, value=msg)
            producer.flush()
            
            # Print feedback every 10 messages so we know it's working
            if count <= 5 or count % 10 == 0:
                print(f"[{count}] {raw['text'][:60]}... (source: {raw['source']})")
            
            time.sleep(0.5)  # Simulate real-time feed (adjust as needed)

    except KeyboardInterrupt:
        print("\n\nStopping producer...")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        producer.flush()
        producer.close()
        print(f"\n✓ Producer closed. Total sent: {count} messages")
