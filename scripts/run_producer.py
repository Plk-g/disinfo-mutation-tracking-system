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

# --- Configuration ---
# Options: "SYNTHETIC", "POLITIFACT", "LAXMIMERIT", "REDDIT", "GDELT", "FINEWEB"
SELECTED_DATASET = "FINEWEB"
TOPIC_NAME = "disinformation-stream"
KAFKA_BROKER = "localhost:9092"

print(f"Starting Producer with dataset: {SELECTED_DATASET}")

# --- Helper Functions ---
GLOBAL_HASH_MEMORY = set()

def generate_synthetic_stream():
    templates = [
        "BREAKING: {subject} is actually {action} by {actor}!",
        "Why is nobody talking about how {subject} caused {event}?",
        "Leaked documents prove {actor} is covering up {subject}."
    ]
    subjects = ["Vitamin C", "5G Towers", "The Election", "Tap Water"]
    actions = ["poisoned", "faked", "controlled", "deleted"]
    actors = ["the government", "the company", "aliens", "AI bots"]
    events = ["the pandemic", "the blackout", "mind control"]

    while True:
        text = random.choice(templates).format(
            subject=random.choice(subjects),
            action=random.choice(actions),
            actor=random.choice(actors),
            event=random.choice(events)
        )
        yield {"text": text, "source": "Synthetic_Bot"}

def stream_huggingface(dataset_name, subset, split="train", text_col="text"):
    try:
        ds = load_dataset(dataset_name, subset, split=split, streaming=True)
        for row in ds:
            yield {
                "text": row[text_col][:1000],
                "source": dataset_name
            }
    except Exception as e:
      print(f"Hugging Face Error: {e}")

def stream_csv_url(url, source_name):
    print(f"Connecting to {source_name}...")
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            lines = (line.decode('utf-8') for line in r.iter_lines())
            chunks = pd.read_csv(io.StringIO("\n".join(lines)), chunksize=1)
            for chunk in chunks:
                if not chunk.empty:
                    # Handle different column names
                    text = chunk.iloc[0].get('title') or chunk.iloc[0].get('news_title') or chunk.iloc[0].get('text') or str(chunk.iloc[0].values[0])
                    yield {"text": str(text), "source": source_name}
    except Exception as e:
        print(f"CSV Error: {e}")

def scrape_article_text(url):
    if not url or "http" not in url:
        return None

    # Pretend to be a Chrome on Windows
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=2)
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
    global GLOBAL_HASH_MEMORY
    try:
        master = requests.get("http://data.gdeltproject.org/gdeltv2/lastupdate.txt").text
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
            else:
                continue
    except Exception as e:
      print(f"GDELT Error: {e}")

def get_stream():
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
        return []

# --- Main Execution ---
if __name__ == "__main__":
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER],
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )

    stream = get_stream()
    count = 0

    try:
        for raw in stream:
            count += 1
            msg = {
                "post_id": str(uuid.uuid4()),
                "text": raw['text'],
                "source": raw['source'],
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            producer.send(TOPIC_NAME, value=msg)
            
            # Print feedback every 10 messages so we know it's working
            if count <= 5 or count % 10 == 0:
                print(f"Sent {count}: {raw['text'][:50]}...")
            
            time.sleep(0.1) # Simulate real-time feed

    except KeyboardInterrupt:
        print("\nStopping producer...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        producer.flush()
        producer.close()
        print(f"Total Sent: {count}")