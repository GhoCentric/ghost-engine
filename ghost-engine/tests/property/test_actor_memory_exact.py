from hypothesis import given, strategies as st
from ghost.engine import GhostEngine

@given(
    actors=st.lists(st.text(min_size=1, max_size=5), min_size=1, max_size=20)
)
def test_actor_threat_counts_match_events(actors):
    engine = GhostEngine()

    for actor in actors:
        engine.step({
            "source": "npc_engine",
            "intent": "threat",
            "actor": actor,
            "intensity": 1.0
        })

    state = engine.state()
    memory = state["npc"]["actors"]

    for actor in actors:
        assert memory[actor]["threat_count"] == actors.count(actor)
