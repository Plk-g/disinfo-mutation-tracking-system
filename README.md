# disinfo-mutation-tracking-system
NYU CSGY 6513 Big Data Engineering Final Project – Real-Time Disinformation Topic Mutation Tracking System

For the NLP part:
## Quickstart (Windows)

### Prereqs
- Java 11 (set `JAVA_HOME`, ensure `java -version` works)
- Python 3.10/3.11
- Kafka extracted to: `tools/kafka_2.12-3.6.0` (do NOT commit Kafka binaries)

### Install deps
```powershell
pip install -r requirements.txt

SET REQUIRED ENVIRONMENT VARIABLES:
$env:MONGO_URI="mongodb+srv://<user>:<password>@<cluster>/<...>"
$env:KAFKA_BROKER="localhost:9092"
$env:KAFKA_TOPIC="disinformation-stream"

One-command Demo:
.\scripts\run_demo.ps1