"""
demo_mode.py

Minimal deterministic demo runner for Ghost Engine.
Purpose: demonstrate state-driven behavior without LLM or memory carryover.
"""

from ghost.core.ghost_core import run_cycle, init_context
from ghost.core.trace import make_trace


def run_demo(
    user_input: str,
    initial_overrides: dict | None = None,
):
    print("\n=== GHOST DEMO MODE ===")

    # --- Hard guarantees ---
    print("LLM: OFF")
    print("Cold start: TRUE")
    print("Memory: DISABLED")

    # --- Build fresh context ---
    ctx = init_context()

    # Enforce demo invariants
    ctx["demo_mode"] = True
    ctx["llm_enabled"] = False
    ctx["memory_enabled"] = False

    # Ensure cold start
    ctx["state"] = {}
    ctx["persistent_memory"] = {}

    # Optional perturbations (applied after state init)
    ctx["demo_overrides"] = initial_overrides or {}

    # Trace recorder
    trace = make_trace(event="demo_run")
    ctx["trace"] = trace

    print("\n--- Input ---")
    print(user_input)

    # --- Single deterministic cycle ---
    output = run_cycle(
        user_text=user_input,
        ctx=ctx
    )

    # --- Results ---
    print("\n--- Strategy Selection ---")
    print(f"Chosen strategy: {trace.get('decision')}")

    print("\n--- Output ---")
    print(output)

    print("\n--- State Transition ---")
    print("Pre-state mood:", trace["pre_state"].get("mood"))
    print("Post-state mood:", trace["post_state"].get("mood"))

    print("\n--- Trace Integrity ---")
    print("Deterministic:", trace.get("replayable", False))
    print("Trace ID:", trace.get("id"))

    print("\n=== END DEMO ===\n")

    return trace


if __name__ == "__main__":
    print("\n### DEMO A: Neutral State ###")
    run_demo("hello")

    print("\n### DEMO B: Perturbed State ###")
    run_demo(
        "hello",
        initial_overrides={
            "mood": 0.25,
            "pressure": {"goal_pressure": 0.6},
        },
    )
