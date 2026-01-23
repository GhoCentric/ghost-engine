def test_external_input_passthrough():
    """
    External input passed to step() must be recorded in state.
    """

    from ghost.engine import GhostEngine

    engine = GhostEngine()

    event = {
        "source": "npc_engine",
        "intent": "threat",
        "actor": "player",
        "intensity": 0.5,
    }

    engine.step(event)
    state = engine.state()

    assert "input" in state
    assert state["input"] is not None
    assert isinstance(state["input"], dict)
    assert state["input"] == event
