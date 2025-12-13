import numpy as np

def cosine_distance(a, b):
    a = np.array(a)
    b = np.array(b)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return 1.0 - float(np.dot(a, b) / denom)

def centroid(vectors):
    if not vectors:
        return None
    return np.mean(np.array(vectors), axis=0).tolist()
