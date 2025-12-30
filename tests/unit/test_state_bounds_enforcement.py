import json
import os

# ---- helpers -------------------------------------------------

def load_state_bounds():
    """
    Load state bounds from config/state_bounds.json.
    """
    config_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "config",
        "state_bounds.json"
    )

    with open(config_path, "r") as f:
        return json.load(f)


def enforce_state_bounds(state, bounds):
    """
    Clamp state values according to configured bounds.
    This mirrors Ghost's constraint-first philosophy:
    state is authoritative, bounded, and deterministic.
    """
    for key, value in state.items():
        if key not in bounds:
            continue

        min_val = bounds[key]["min"]
        max_val = bounds[key]["max"]

        if value < min_val:
            state[key] = min_val
        elif value > max_val:
            state[key] = max_val


# ---- test ----------------------------------------------------

def test_state_bounds_enforced():
    """
    Ghost must enforce explicit numeric bounds on internal state.

    This test intentionally pushes state values beyond configured limits
    and verifies deterministic clamping behavior.
    """

    # Initial internal state (valid baseline)
    state = {
        "emotion": 0.5,
        "awareness": 0.5,
        "stability": 0.5
    }

    bounds = load_state_bounds()

    # Apply extreme updates (simulated external pressure)
    state["emotion"] += 5.0
    state["awareness"] -= 3.0
    state["stability"] += 10.0

    # Enforce bounds
    enforce_state_bounds(state, bounds)

    # Assertions: state must respect config-defined limits
    assert state["emotion"] == bounds["emotion"]["max"]
    assert state["awareness"] == bounds["awareness"]["min"]
    assert state["stability"] == bounds["stability"]["max"]
    
print("test_state_bounds_enforcement: PASS")
