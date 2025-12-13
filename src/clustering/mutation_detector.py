def detect_mutations(drift_events, mutation_threshold=0.3):
    mutations = []

    for e in drift_events:
        if e["drift_score"] >= mutation_threshold:
            e = dict(e)
            e["event_type"] = "mutation"
            mutations.append(e)

    return mutations
