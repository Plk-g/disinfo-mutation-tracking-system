# Storage Design – Disinformation Topic Mutation Tracking System

## Database

We use **MongoDB Atlas** as the primary storage layer.

- Cluster: Cluster0 (Atlas Free Tier)
- Database name: `disinfo_project`

## Collections

### 1. `narrative_matches`

Stores posts that have been matched to a known misinformation claim.

Schema (per document):

- `post_id` (string) – unique ID for the post
- `claim_id` (string) – ID of the fact-checked claim
- `similarity_score` (float) – semantic similarity between post and claim
- `matched` (bool) – whether the score is above our threshold
- `timestamp` (string, ISO format) – time of the post
- `source` (string) – source platform, e.g. "reddit", "news"

Example document:

```json
{
  "post_id": "p1",
  "claim_id": "c1",
  "similarity_score": 0.92,
  "matched": true,
  "timestamp": "2024-12-02T10:00:00Z",
  "source": "reddit"
}
