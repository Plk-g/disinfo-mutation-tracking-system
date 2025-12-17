# Data Contract — Kafka → Spark → MongoDB

Owner: Palak (Storage + Backend Lead)  
Last updated: 2025-12-14  
Goal: Define canonical schemas so Spark output is queryable in MongoDB + demoable in backend.

---

## 1) Kafka input schema (Producer → Spark)

### Topic(s)
- TBD: `<kafka_topic_name>`

### Encoding
- JSON, UTF-8
- One event per message

### Required fields (minimum contract)
| Field | Type | Required | Notes |
|---|---|---:|---|
| `post_id` | string | ✅ | Unique identifier of the post/document |
| `text` | string | ✅ | Raw text content used for NLP/matching |
| `timestamp` | string | ✅ | ISO-8601 UTC recommended (e.g., `2024-12-02T10:00:00Z`) |
| `source` | string | ✅ | e.g., reddit/twitter/news |

### Optional fields
| Field | Type | Required | Notes |
|---|---|---:|---|
| `url` | string | ❌ | Original link |
| `author_id` | string | ❌ | If available |
| `lang` | string | ❌ | e.g., `en` |
| `metadata` | object | ❌ | Any extra attributes |

### Example Kafka message
```json
{
  "post_id": "p1",
  "text": "Example narrative text about topic X...",
  "timestamp": "2024-12-02T10:00:00Z",
  "source": "reddit",
  "metadata": {
    "subreddit": "exampleSub"
  }
}
