import os
import json
import copy

# FORCE correct project root (Pydroid fix)
PROJECT_ROOT = "/storage/emulated/0/ghost-engine-test-for-repo"
os.chdir(PROJECT_ROOT)
# -------------------------------------------------
# Path resolution (Pydroid compatible)
# -------------------------------------------------

REPO_ROOT = os.getcwd()
CONFIG_PATH = os.path.join(REPO_ROOT, "config", "routing_weights.json")

# -------------------------------------------------
# Helpers
# -------------------------------------------------

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)


def normalize(weights):
    total = sum(weights.values())
    return {k: v / total for k, v in weights.items()}


def apply_pressure(base_weights, pressure_block):
    """
    pressure_block = {
        "scale": float,
        "bias": { strategy: delta }
    }
    """
    out = copy.deepcopy(base_weights)

    scale = pressure_block.get("scale", 1.0)
    bias = pressure_block.get("bias", {})

    for strategy, delta in bias.items():
        if strategy not in out:
            continue
        out[strategy] += delta * scale

    return normalize(out)

# -------------------------------------------------
# Test
# -------------------------------------------------

def test_pressure_routing():
    config = load_json(CONFIG_PATH)

    base = normalize(config["base_strategy_weights"])
    pressure = config["pressure_modifiers"]["goal_pressure"]

    routed = apply_pressure(base, pressure)
    
    assert routed["explore"] > base["explore"], "Explore did not increase under pressure"
    assert routed["reflect"] < base["reflect"], "Reflect did not decrease under pressure"

    print("test_pressure_routing: PASS")


if __name__ == "__main__":
    test_pressure_routing()  
