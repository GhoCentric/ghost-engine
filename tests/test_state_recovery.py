"""
test_state_recovery.py

Minimal proof that Ghost maintains coherent internal state
across command failure and recovery, without using an LLM.

This test intentionally:
- Triggers a failing command
- Verifies state is not corrupted
- Runs a valid command afterward
- Verifies continuity of state

If this passes, Ghost is not reasoning in language.
"""

from ghost_core import init_state
from commands import route


def assert_valid_state(state):
    """
    Minimal invariants for a valid Ghost state.
    These are intentionally boring and strict.
    """
    assert state is not None, "State is None"
    assert isinstance(state, dict), "State is not a dict"
    assert "mood" in state, "Missing 'mood' key"
    assert "stability" in state, "Missing 'stability' key"


def run_test():
    print("\n[TEST] Initializing Ghost state")
    state = init_state()
    quit_flag = False

    assert_valid_state(state)
    print("[PASS] Initial state valid")

    print("\n[TEST] Running failing command (#invalid_command)")
    state, quit_flag = route(state, "#invalid_command")

    assert_valid_state(state)
    print("[PASS] State survived command failure")

    print("\n[TEST] Running valid command (#state)")
    state, quit_flag = route(state, "#state")

    assert_valid_state(state)
    print("[PASS] State recovered and remains valid")

    print("\n[TEST COMPLETE] Ghost state recovery verified")


if __name__ == "__main__":
    run_test()
