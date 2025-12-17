import json
import time
from datetime import datetime
from kafka import KafkaProducer

TOPIC = "disinfo-events"
BOOTSTRAP = "localhost:9092"

def main():
    producer = KafkaProducer(
        bootstrap_servers=BOOTSTRAP,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )

    for i in range(5):
        msg = {
            "id": i,
            "text": f"Demo disinfo event #{i}: vaccines cause microchips",
            "ts": datetime.utcnow().isoformat() + "Z",
            "source": "run_producer.py",
        }
        producer.send(TOPIC, msg)
        producer.flush()
        print("sent:", msg)
        time.sleep(1)

    producer.close()

if __name__ == "__main__":
    main()
