from ghost.engine import GhostEngine


def test_relationship_delta_updates():
    g = GhostEngine()

    g.relationships.apply_delta("Alice", "Bob", {"trust": 0.3})

    rel = g.relationships.get("Alice", "Bob")

    assert rel["trust"] == 0.3
    
def test_relationship_pair_symmetry():
    g = GhostEngine()

    g.relationships.apply_delta("Alice", "Bob", {"trust": 0.5})

    rel1 = g.relationships.get("Alice", "Bob")
    rel2 = g.relationships.get("Bob", "Alice")

    assert rel1 == rel2
