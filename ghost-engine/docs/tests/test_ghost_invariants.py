# tests/test_ghost_invariants.py

import copy
import importlib
import json
import os
import random
import sys

from ghost.engine import GhostEngine


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def frozen(obj):
    """Deep-copy helper so live dict aliasing does not fake failures."""
    return copy.deepcopy(obj)


def neutral_step(engine):
    """A non-threat step that should allow decay / cycle advance."""
    engine.step({
        "source": "npc_engine",
        "intent": "observe",
        "actor": "observer",
        "target": "scene",
        "intensity": 0.0,
    })


def threat_step(engine, actor="a", target="b", intensity=0.5):
    engine.step({
        "source": "npc_engine",
        "intent": "threat",
        "actor": actor,
        "target": target,
        "intensity": intensity,
    })


def recursive_public_safe(x):
    """
    Public state must remain serialization-safe and free of custom leaked types.
    Allow only plain containers + primitives.
    """
    if isinstance(x, dict):
        return all(isinstance(k, str) and recursive_public_safe(v) for k, v in x.items())

    if isinstance(x, list):
        return all(recursive_public_safe(v) for v in x)

    if isinstance(x, tuple):
        return all(recursive_public_safe(v) for v in x)

    return isinstance(x, (int, float, str, bool, type(None)))


# ─────────────────────────────────────────────
# 1. STATE EVOLUTION
# ─────────────────────────────────────────────

def test_state_evolution():
    e = GhostEngine()

    s0 = frozen(e.state())
    cycles0 = int(s0.get("cycles", 0))

    # No implicit mutation during inspection
    _ = e.state()
    _ = frozen(e.state())

    s1 = frozen(e.state())
    if s1 != s0:
        return False

    # Mutation occurs only through explicit step()
    threat_step(e, actor="alpha", target="beta", intensity=0.4)
    s2 = frozen(e.state())
    cycles2 = int(s2.get("cycles", 0))

    if s2 == s1:
        return False

    if cycles2 != cycles0 + 1:
        return False

    # Monotonic cycle increment
    neutral_step(e)
    s3 = frozen(e.state())
    cycles3 = int(s3.get("cycles", 0))

    if cycles3 != cycles2 + 1:
        return False

    return True


# ─────────────────────────────────────────────
# 2. THREAT NON-NEGATIVITY
# ─────────────────────────────────────────────

def test_threat_non_negative():
    e = GhostEngine()

    for _ in range(100):
        threat_step(e, intensity=random.random())

    for _ in range(200):
        neutral_step(e)

    tl = float(e.state().get("npc", {}).get("threat_level", 0.0))
    return tl >= 0.0


# ─────────────────────────────────────────────
# 3. THREAT ACCUMULATION MONOTONICITY
# ─────────────────────────────────────────────

def test_threat_accumulation_monotonicity():
    e_hi = GhostEngine()
    e_lo = GhostEngine()

    threat_step(e_hi, intensity=0.80)
    threat_step(e_lo, intensity=0.20)

    hi = float(e_hi.state().get("npc", {}).get("threat_level", 0.0))
    lo = float(e_lo.state().get("npc", {}).get("threat_level", 0.0))

    return hi >= lo


# ─────────────────────────────────────────────
# 4. THREAT DECAY MONOTONICITY
# ─────────────────────────────────────────────

def test_threat_decay_monotonicity():
    e = GhostEngine()

    threat_step(e, intensity=1.0)
    prev = float(e.state().get("npc", {}).get("threat_level", 0.0))

    for _ in range(50):
        neutral_step(e)
        now = float(e.state().get("npc", {}).get("threat_level", 0.0))

        if now > prev:
            return False
        if now < 0.0:
            return False

        prev = now

    return True


# ─────────────────────────────────────────────
# 5. INPUT-DEPENDENT DECAY SUPPRESSION
# ─────────────────────────────────────────────

def test_input_dependent_decay_suppression():
    e = GhostEngine()

    threat_step(e, intensity=0.60)
    before = float(e.state().get("npc", {}).get("threat_level", 0.0))

    threat_step(e, intensity=0.30)
    after = float(e.state().get("npc", {}).get("threat_level", 0.0))

    return after >= before


# ─────────────────────────────────────────────
# 6. ACTOR-SPECIFIC MEMORY CONSISTENCY
# ─────────────────────────────────────────────

def test_actor_specific_memory_consistency():
    e = GhostEngine()

    for _ in range(5):
        threat_step(e, actor="A", target="B", intensity=0.4)

    for _ in range(3):
        threat_step(e, actor="C", target="D", intensity=0.4)

    actors = e.state().get("npc", {}).get("actors", {})
    a_count = int(actors.get("A", {}).get("threat_count", 0))
    c_count = int(actors.get("C", {}).get("threat_count", 0))

    if a_count != 5:
        return False
    if c_count != 3:
        return False

    return True


# ─────────────────────────────────────────────
# 7. INTERNAL TYPE ISOLATION
# 8. JSON SERIALIZATION SAFETY
# ─────────────────────────────────────────────

def test_internal_type_isolation_and_serialization():

    e = GhostEngine()

    for i in range(20):
        threat_step(e, actor=f"A{i%3}", target=f"B{i%5}", intensity=random.random())

    st = frozen(e.state())

    # JSON safety first
    try:
        json.dumps(st, sort_keys=True)
    except Exception as err:
        print("JSON FAILURE:", err)
        return False

    # deep type inspection
    def walk(x, path="root"):

        if isinstance(x, dict):
            for k, v in x.items():
                if not isinstance(k, str):
                    print("BAD KEY:", path, type(k))
                    return False
                if not walk(v, f"{path}.{k}"):
                    return False
            return True

        if isinstance(x, list):
            for i, v in enumerate(x):
                if not walk(v, f"{path}[{i}]"):
                    return False
            return True

        if isinstance(x, tuple):
            print("TUPLE FOUND:", path)
            return False

        if isinstance(x, set):
            print("SET FOUND:", path)
            return False

        if not isinstance(x, (int, float, str, bool, type(None))):
            print("BAD TYPE:", path, type(x))
            return False

        return True

    return walk(st)


# ─────────────────────────────────────────────
# 9. SNAPSHOT IMMUTABILITY
# ─────────────────────────────────────────────

def test_snapshot_immutability():
    e = GhostEngine()
    threat_step(e, intensity=0.9)

    # Prefer snapshot() if it exists on engine
    if hasattr(e, "snapshot"):
        snap = e.snapshot()
    else:
        snap = frozen(e.state())

    if not isinstance(snap, dict):
        return False

    live_before = frozen(e.state())

    if "npc" in snap and isinstance(snap["npc"], dict):
        snap["npc"]["threat_level"] = 999.0

    live_after = frozen(e.state())

    return live_before == live_after


# ─────────────────────────────────────────────
# 10. ENVIRONMENT ISOLATION
# ─────────────────────────────────────────────

def test_environment_isolation():
    env_before = dict(os.environ)
    path_before = list(sys.path)

    _ = GhostEngine()

    env_after = dict(os.environ)
    path_after = list(sys.path)

    return env_before == env_after and path_before == path_after


# ─────────────────────────────────────────────
# 11. DETERMINISM UNDER ADVERSARIAL INPUT
# ─────────────────────────────────────────────

def run_fuzz_sequence(seed):
    random.seed(seed)
    e = GhostEngine()

    actors = [f"A{i}" for i in range(8)]
    targets = [f"T{i}" for i in range(8)]
    intents = ["threat", "observe"]

    for _ in range(120):
        intent = random.choice(intents)
        payload = {
            "source": "npc_engine",
            "intent": intent,
            "actor": random.choice(actors),
            "target": random.choice(targets),
            "intensity": random.random(),
        }
        e.step(payload)

    return frozen(e.state())


def test_determinism_under_adversarial_input():
    s1 = run_fuzz_sequence(1337)
    s2 = run_fuzz_sequence(1337)
    return s1 == s2


# ─────────────────────────────────────────────
# 12. MEMORY TRANSPARENCY INVARIANT
# ─────────────────────────────────────────────

def test_memory_transparency_invariant():
    """
    For the core engine, this can only be tested minimally:
    the engine should not hide implicit memory channels outside explicit state.
    So we verify memory-relevant info is visible in public state, not hidden objects.
    """
    e = GhostEngine()
    threat_step(e, actor="memory_actor", target="x", intensity=0.5)

    st = frozen(e.state())
    actors = st.get("npc", {}).get("actors", {})

    return "memory_actor" in actors and isinstance(actors["memory_actor"], dict)


# ─────────────────────────────────────────────
# PYPI PUBLIC API STABILITY
# ─────────────────────────────────────────────

def test_public_api_stability():
    """
    Your invariant names module-level public functions:
      ghost.init(), ghost.step(), ghost.reset(), ghost.state(), ghost.snapshot()

    This tests for those names on the public ghost module, not on GhostEngine.
    """
    try:
        ghost_mod = importlib.import_module("ghost")
    except Exception:
        return False

    required = ["init", "step", "reset", "state", "snapshot"]
    for name in required:
        if not hasattr(ghost_mod, name):
            return False

    try:
        ghost_mod.init()

        ghost_mod.step({
            "source": "npc_engine",
            "intent": "threat",
            "actor": "pub_actor",
            "target": "pub_target",
            "intensity": 0.5,
        })

        st = ghost_mod.state()
        snap = ghost_mod.snapshot()

        if not isinstance(st, dict):
            return False
        if not isinstance(snap, dict):
            return False

        ghost_mod.reset()
    except Exception:
        return False

    return True


# ─────────────────────────────────────────────
# RUNNER
# ─────────────────────────────────────────────

def run_all():
    print("\n=== GHOST INVARIANT TEST SUITE ===\n")

    results = {
        "State Evolution": test_state_evolution(),
        "Threat Non-Negativity": test_threat_non_negative(),
        "Threat Accumulation Monotonicity": test_threat_accumulation_monotonicity(),
        "Threat Decay Monotonicity": test_threat_decay_monotonicity(),
        "Input-Dependent Decay Suppression": test_input_dependent_decay_suppression(),
        "Actor-Specific Memory Consistency": test_actor_specific_memory_consistency(),
        "Internal Type Isolation + Serialization": test_internal_type_isolation_and_serialization(),
        "Public API Stability": test_public_api_stability(),
        "Snapshot Immutability": test_snapshot_immutability(),
        "Environment Isolation": test_environment_isolation(),
        "Determinism Under Adversarial Input": test_determinism_under_adversarial_input(),
        "Memory Transparency Invariant": test_memory_transparency_invariant(),
    }

    failed = False

    for name, ok in results.items():
        print(f"{name}: {'PASS' if ok else 'FAIL'}")
        if not ok:
            failed = True

    if failed:
        print("\nINVARIANT FAILURE DETECTED ❌")
    else:
        print("\nALL INVARIANTS HOLD ✅")


if __name__ == "__main__":
    run_all()
