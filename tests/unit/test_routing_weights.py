import json
import os
import math

# -------------------------
# CONFIG
# -------------------------
REPO_ROOT = "/storage/emulated/0/ghost-engine-test-for-repo"
CONFIG_FILE = os.path.join(REPO_ROOT, "config", "routing_weights.json")

REQUIRED_STRATEGIES = {
    "reflect",
    "respond",
    "explore",
    "stabilize",
    "suppress"
}

EPSILON = 0.001  # tolerance for float sum


# -------------------------
# LOAD CONFIG
# -------------------------
if not os.path.isfile(CONFIG_FILE):
    raise FileNotFoundError(f"Config file not found: {CONFIG_FILE}")

with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    cfg = json.load(f)

weights = cfg["base_strategy_weights"]


# -------------------------
# TEST
# -------------------------
def test_routing_weights_integrity():
    # 1. Required strategies exist
    assert REQUIRED_STRATEGIES.issubset(weights.keys()), (
        f"Missing strategies: {REQUIRED_STRATEGIES - set(weights.keys())}"
    )

    total = 0.0

    for name, value in weights.items():
        # 2. Numeric
        assert isinstance(value, (int, float)), f"{name} weight is not numeric"

        # 3. Non-negative
        assert value >= 0.0, f"{name} weight is negative"

        total += value

    # 4. Total weight ≈ 1.0
    assert math.isclose(total, 1.0, abs_tol=EPSILON), (
        f"Routing weights must sum to 1.0 (got {total})"
    )

    # 5. No dead strategies
    for name, value in weights.items():
        assert value > 0.0, f"{name} has zero weight (dead strategy)"


# -------------------------
# DIRECT EXECUTION
# -------------------------
if __name__ == "__main__":
    test_routing_weights_integrity()
    print("test_routing_weights_integrity: PASS")
