#!/usr/bin/env python3
"""
Seed MongoDB with sample data for testing/demo purposes.
This script populates the database with sample narrative matches so the UI can be tested
without running the full Kafka/Spark pipeline.
"""

import os
import sys
from datetime import datetime, timedelta
import random

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db.queries import insert_matches, insert_mutations

# Sample disinformation narratives
SAMPLE_NARRATIVES = [
    {
        "text": "Vaccines contain microchips that track people and control their behavior",
        "claim_id": "claim_vaccine_chips",
        "similarity_score": 0.92,
        "source": "reddit"
    },
    {
        "text": "5G networks cause COVID-19 and spread the virus through radiation",
        "claim_id": "claim_5g_covid",
        "similarity_score": 0.88,
        "source": "twitter"
    },
    {
        "text": "The election was stolen through massive voter fraud",
        "claim_id": "claim_election_fraud",
        "similarity_score": 0.85,
        "source": "news"
    },
    {
        "text": "COVID-19 was created in a Wuhan lab as a bioweapon",
        "claim_id": "claim_covid_lab",
        "similarity_score": 0.90,
        "source": "forum"
    },
    {
        "text": "Masks don't work and cause oxygen deprivation",
        "claim_id": "claim_masks_harmful",
        "similarity_score": 0.82,
        "source": "reddit"
    },
    {
        "text": "Climate change is a hoax created by scientists for funding",
        "claim_id": "claim_climate_hoax",
        "similarity_score": 0.87,
        "source": "twitter"
    },
]

# Mutated variants
MUTATED_VARIANTS = [
    "Vaccines have tracking devices that monitor your location",
    "5G towers emit harmful frequencies that cause illness",
    "Voting machines were hacked to change election results",
    "The virus was engineered in a Chinese laboratory",
    "Wearing masks reduces oxygen intake and is dangerous",
    "Global warming is natural weather variation, not man-made",
]


def generate_sample_matches(num_records: int = 50):
    """Generate sample narrative match records"""
    records = []
    base_time = datetime.utcnow() - timedelta(days=7)
    
    for i in range(num_records):
        # Mix of original and mutated narratives
        if random.random() > 0.4:
            narrative = random.choice(SAMPLE_NARRATIVES)
            text = narrative["text"]
            claim_id = narrative["claim_id"]
            base_similarity = narrative["similarity_score"]
        else:
            text = random.choice(MUTATED_VARIANTS)
            claim_id = f"claim_mutated_{random.randint(1, 10)}"
            base_similarity = random.uniform(0.65, 0.95)
        
        # Add some variation
        similarity = base_similarity + random.uniform(-0.1, 0.1)
        similarity = max(0.0, min(1.0, similarity))
        
        timestamp = (base_time + timedelta(hours=random.randint(0, 168))).isoformat() + "Z"
        
        records.append({
            "post_id": f"sample_post_{i+1}",
            "claim_id": claim_id,
            "text": text,
            "similarity_score": round(similarity, 3),
            "matched": similarity > 0.7,
            "timestamp": timestamp,
            "source": random.choice(["reddit", "twitter", "news", "forum"]),
        })
    
    return records


def generate_sample_mutations(num_events: int = 15):
    """Generate sample mutation event records"""
    events = []
    base_time = datetime.utcnow() - timedelta(days=5)
    
    for i in range(num_events):
        window_start = base_time + timedelta(hours=i * 8)
        window_end = window_start + timedelta(hours=6)
        
        events.append({
            "cluster_id": f"cluster_{random.randint(1, 5)}",
            "mutation_type": random.choice(["lexical_shift", "semantic_drift", "claim_expansion"]),
            "mutation_score": round(random.uniform(0.35, 0.95), 3),
            "window_start": int(window_start.timestamp()),
            "window_end": int(window_end.timestamp()),
            "epoch": i + 1,
        })
    
    return events


def main():
    print("=" * 60)
    print("Seeding MongoDB with sample data...")
    print("=" * 60)
    
    # Check environment
    if not os.environ.get("MONGO_URI"):
        print("ERROR: MONGO_URI environment variable not set")
        print("Set it with: export MONGO_URI='your_mongodb_uri'")
        sys.exit(1)
    
    # Generate and insert matches
    print("\n1. Generating sample narrative matches...")
    matches = generate_sample_matches(num_records=50)
    inserted_matches = insert_matches(matches)
    print(f"   ✓ Inserted {inserted_matches} narrative match records")
    
    # Generate and insert mutations
    print("\n2. Generating sample mutation events...")
    mutations = generate_sample_mutations(num_events=15)
    inserted_mutations = insert_mutations(mutations)
    print(f"   ✓ Inserted {inserted_mutations} mutation event records")
    
    print("\n" + "=" * 60)
    print("✓ Sample data seeding complete!")
    print("=" * 60)
    print("\nYou can now:")
    print("  - Start the Flask app: python -m frontend.app")
    print("  - Visit http://127.0.0.1:5000 to search narratives")
    print("  - Visit http://127.0.0.1:5000/mutations to view mutations")
    print()


if __name__ == "__main__":
    main()

