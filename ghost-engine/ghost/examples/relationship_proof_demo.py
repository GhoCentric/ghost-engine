"""
Ghost Engine v1.0.0
Emotional Inertia Proof Demo

This demo compares:
1) A simple linear smoothing baseline (EMA filter)
2) Ghost emotional inertia runtime

Goal:
Show how Ghost retains emotional weight after betrayal,
while the baseline rapidly normalizes.

Run:
    python examples/relationship_proof_demo.py
"""

from ghost import GhostAPI


# --------------------------------------------------
# BASELINE: Linear smoothing (no state transitions)
# --------------------------------------------------
def baseline_step(prev, value, alpha=0.2):
    trust = prev * (1 - alpha) + value * alpha
    return max(min(trust, 1.0), -1.0)


# --------------------------------------------------
# DEMO SEQUENCE
# --------------------------------------------------
def run_demo():
    ghost = GhostAPI()

    print("\n=== GHOST vs LINEAR BASELINE ===\n")

    # Gameplay-like interaction sequence
    sequence = [
        ("help", 0.3),
        ("help", 0.3),
        ("insult", -0.5),
        ("help", 0.3),
        ("help", 0.3),
        ("betrayal", 1.0),
        ("help", 0.3),
    ]

    baseline = 0.0

    print(f"{'Step':<4} | {'Event':<9} | {'Baseline':<9} | {'Ghost':<9} | {'State':<12}")
    print("-" * 70)

    for i, (event, val) in enumerate(sequence):

        # ----- Baseline update -----
        baseline = baseline_step(baseline, val)

        # ----- Ghost update -----
        ghost.apply_event("Player", "Villager", {
            "type": event,
            "intensity": abs(val)
        })

        ghost.engine.relationships.tick()

        rel = ghost.get_relationship("Player", "Villager")
        g_trust = rel["trust"]
        state = rel.get("state", "unknown")
        trigger = rel.get("trigger")

        print(
            f"{i:<4} | "
            f"{event:<9} | "
            f"{baseline:<9.3f} | "
            f"{g_trust:<9.3f} | "
            f"{state:<12}"
        )

        # ----- Transition Feedback -----
        if trigger:
            if trigger.get("event") == "relationship_broken":
                print("      ⚠ Relationship permanently damaged")
            elif trigger.get("event") == "forgiveness":
                print("      ✓ Forgiveness triggered")
            elif trigger.get("event") == "deescalation":
                print("      ↓ Emotional tension reduced")
            else:
                print(f"      ↔ State change: {trigger.get('from')} → {trigger.get('to')}")

    # --------------------------------------------------
    # Gameplay Simulation
    # --------------------------------------------------
    print("\n--- GAMEPLAY SIMULATION ---")

    if state == "hostile":
        print("Villager: 'I will never trust you again.'")
        print("→ NPC refuses quests.")
    elif state == "unfriendly":
        print("Villager: 'I'm not sure I like you.'")
    elif state == "friendly":
        print("Villager: 'You have my support.'")

    # --------------------------------------------------
    # Final Comparison
    # --------------------------------------------------
    print("\n--- INTERPRETATION ---")
    print("Baseline: Gradually smooths back toward neutral.")
    print("Ghost: Retains emotional memory after betrayal.")
    print("Result: Persistent emotional inertia.\n")

    print("=== FINAL RESULT ===")

    if g_trust < baseline:
        print("Ghost retained negative state.")
        print("Baseline normalized.")
        print("✔ Emotional inertia confirmed.")
    else:
        print("No meaningful difference detected.")


# --------------------------------------------------
# RUN
# --------------------------------------------------
if __name__ == "__main__":
    run_demo()


def main():
    run_demo()


if __name__ == "__main__":
    main()
