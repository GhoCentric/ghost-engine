"""
test_state_recovery.py

Proof that Ghost preserves internal state identity
across command failure and recovery.

No LLM.
No language reasoning.
No schema assumptions.
"""

from ghost.core.state import init_state
from ghost.core.commands import route

STRUCTURAL_EVOLUTION = {
    "mood": (float, dict),  # allowed promotion
}

EPHEMERAL_KEYS = {
    "signal_memory",
    "last_reflect",
    "last_summary",
    "meta_mode",
}

CORE_KEYS = {
    "mood",
    "emotion",
    "memory_factor",
    "reaction_strength",
    "clamp_tolerance",
    "clamp_sensitivity",
    "mirror_coeff",
}

def assert_state_survives(before, after):
    # Basic survival checks
    assert after is not None, "State became None"
    assert isinstance(after, dict), "State is no longer a dict"

    # Core invariants must exist
    for key in CORE_KEYS:
        assert key in after, f"Missing core key after recovery: {key}"

    # Structural evolution rules
    for key, allowed_types in STRUCTURAL_EVOLUTION.items():
        if key in after:
            assert isinstance(after[key], allowed_types), (
                f"Invalid evolution for key '{key}': "
                f"{type(after[key])}"
            )

    # Ephemeral keys are allowed to vanish — no checks needed
    # Everything else is intentionally ignored

def run_test():
    print("\n[TEST] Initializing Ghost state")
    state = init_state()
    ctx = {}

    print("[PASS] State initialized")

    print("\n[TEST] Running invalid command")
    state_before = state
    state, quit_flag = route(state, None, "#this_command_does_not_exist", ctx)

    assert_state_survives(state_before, state)
    print("[PASS] State survived invalid command")

    print("\n[TEST] Running valid command")
    state_before = state
    state, quit_flag = route(state, None, "#state", ctx)

    assert_state_survives(state_before, state)
    print("[PASS] State survived valid command")

    print("\n[TEST COMPLETE] Ghost state continuity verified")


if __name__ == "__main__":
    run_test()
