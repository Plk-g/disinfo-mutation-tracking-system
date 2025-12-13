from collections import defaultdict
from .vector_utils import centroid, cosine_distance

class DriftModel:
    def __init__(self, drift_threshold=0.15):
        self.drift_threshold = drift_threshold
        self.baseline_centroids = {}
        self.history = defaultdict(list)

    def fit_baseline(self, clustered_rows):
        """
        clustered_rows: iterable of dicts with cluster_id, vector
        """
        clusters = defaultdict(list)
        for r in clustered_rows:
            clusters[r["cluster_id"]].append(r["vector"])

        for cid, vecs in clusters.items():
            self.baseline_centroids[cid] = centroid(vecs)

    def score_epoch(self, epoch, clustered_rows):
        events = []

        clusters = defaultdict(list)
        for r in clustered_rows:
            clusters[r["cluster_id"]].append(r["vector"])

        for cid, vecs in clusters.items():
            new_centroid = centroid(vecs)
            base = self.baseline_centroids.get(cid)

            if base is None:
                events.append({
                    "epoch": epoch,
                    "cluster_id": cid,
                    "drift_score": 1.0,
                    "event_type": "new_cluster"
                })
                continue

            score = cosine_distance(base, new_centroid)

            if score >= self.drift_threshold:
                events.append({
                    "epoch": epoch,
                    "cluster_id": cid,
                    "drift_score": score,
                    "event_type": "drift"
                })

        return events
