import json
import time
import random
from datetime import datetime
from kafka import KafkaProducer

TOPIC = "disinformation-stream"
BOOTSTRAP = "localhost:9092"

# Sample disinformation narratives that will "mutate"
SEED_NARRATIVES = [
    "Vaccines contain microchips that track people",
    "5G networks cause COVID-19 and spread the virus",
    "The election was stolen through voter fraud",
    "COVID-19 was created in a lab as a bioweapon",
    "Masks don't work and cause health problems",
    "Climate change is a hoax created by scientists",
    "The moon landing was faked by NASA",
    "Chemtrails are used to control the population",
]

# Mutated variants (simulating evolution)
MUTATIONS = [
    "Vaccines have tracking devices implanted",
    "5G towers emit harmful radiation that causes illness",
    "Voting machines were hacked to change results",
    "The virus was engineered in Wuhan lab",
    "Wearing masks reduces oxygen and is dangerous",
    "Global warming is natural, not man-made",
    "NASA faked the Apollo missions",
    "Airplanes spray chemicals to control weather",
]

def generate_mutated_text(base_text: str) -> str:
    """Generate a slightly mutated version of the text"""
    words = base_text.split()
    if len(words) > 3:
        # Randomly replace or reorder words
        idx = random.randint(0, len(words) - 1)
        words[idx] = words[idx].upper() if random.random() > 0.5 else words[idx].lower()
    return " ".join(words)

def main():
    print(f"Starting Kafka Producer...")
    print(f"Topic: {TOPIC}")
    print(f"Bootstrap: {BOOTSTRAP}")
    
    try:
        producer = KafkaProducer(
            bootstrap_servers=BOOTSTRAP,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        print("✓ Connected to Kafka")
    except Exception as e:
        print(f"✗ Error connecting to Kafka: {e}")
        print("\nMake sure Kafka is running:")
        print("  - Start Zookeeper: zookeeper-server-start.sh config/zookeeper.properties")
        print("  - Start Kafka: kafka-server-start.sh config/server.properties")
        return

    post_id_counter = 1
    
    print("\nSending messages (Ctrl+C to stop)...\n")
    
    try:
        while True:
            # Randomly pick a narrative (seed or mutation)
            if random.random() > 0.3:
                text = random.choice(SEED_NARRATIVES)
            else:
                text = random.choice(MUTATIONS)
            
            # Sometimes mutate it further
            if random.random() > 0.7:
                text = generate_mutated_text(text)
            
            msg = {
                "post_id": f"post_{post_id_counter}",
                "text": text,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "source": random.choice(["reddit", "twitter", "news", "forum"]),
            }
            
            producer.send(TOPIC, msg)
            producer.flush()
            
            print(f"[{post_id_counter}] {text[:60]}...")
            post_id_counter += 1
            
            time.sleep(2)  # Send a message every 2 seconds
            
    except KeyboardInterrupt:
        print("\n\nStopping producer...")
    finally:
        producer.close()
        print("Producer closed.")

if __name__ == "__main__":
    main()
