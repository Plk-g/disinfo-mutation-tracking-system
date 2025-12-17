from src.clustering.drift_model import DriftModel

def test_drift_model_empty():
    dm = DriftModel()
    events = dm.score_epoch(1, [])
    assert events == []
