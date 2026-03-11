import json

def test_snapshot_json_safe():
    from ghost.engine import GhostEngine

    e = GhostEngine()

    e.step({
        "source": "runtime",
        "intent": "threat",
        "actor": "a",
        "target": "b",
        "intensity": 0.5,
    })

    snap = e.snapshot()

    json.dumps(snap)  # must not raise
