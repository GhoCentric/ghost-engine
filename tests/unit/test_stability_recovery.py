import json
import os

# -----------------------------
# Load config
# -----------------------------

# --- CONFIG ---
REPO_ROOT = "/storage/emulated/0/ghost-engine-test-for-repo"
CONFIG_FILE = os.path.join(REPO_ROOT, "config", "stability_thresholds.json")

# --- SAFETY CHECK ---
if not os.path.isfile(CONFIG_FILE):
    raise FileNotFoundError(f"Config file not found: {CONFIG_FILE}")

with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    cfg = json.load(f)

global_cfg = cfg["global_stability"]
MIN_STABILITY = float(global_cfg["min"])
MAX_STABILITY = float(global_cfg["max"])
COLLAPSE_THRESHOLD = float(global_cfg["collapse_threshold"])
RECOVERY_TARGET = float(global_cfg["recovery_target"])



# -----------------------------
# Helpers
# -----------------------------

def clamp(value, lo, hi):
    return max(lo, min(value, hi))

def recover(stability, step=0.1):
    """
    Deterministic recovery step.
    """
    return clamp(stability + step, MIN_STABILITY, MAX_STABILITY)

# -----------------------------
# Test
# -----------------------------

def test_stability_recovery():
    # Force collapse
    stability = COLLAPSE_THRESHOLD - 0.05
    assert stability < COLLAPSE_THRESHOLD

    history = [stability]

    # Apply recovery
    for _ in range(10):
        stability = recover(stability)
        history.append(stability)

    # Stability must never decrease
    for i in range(1, len(history)):
        assert history[i] >= history[i - 1]

    # Must reach recovery target
    assert stability >= RECOVERY_TARGET

    # Must stay within bounds
    assert MIN_STABILITY <= stability <= MAX_STABILITY


# Allow direct execution (phone-friendly)
if __name__ == "__main__":
    test_stability_recovery()
    print("test_stability_recovery: PASS")
