from ghost.engine import GhostEngine


def test_agent_creation():
    g = GhostEngine()

    agent = g.agents.ensure("Alice")

    assert agent["mood"] == 0.5
    assert agent["memory"] == {}
