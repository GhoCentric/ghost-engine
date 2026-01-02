import csv
from collections import defaultdict

INPUT_FILE = "demo/outputs/example_output.csv"

def load_actions(path):
    actions = defaultdict(dict)
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tick = int(row["tick"])
            system = row["system"]
            action = row["action"]
            actions[tick][system] = action
    return actions

def diff(actions):
    diffs = []
    for tick, systems in actions.items():
        base = systems.get("baseline")
        ghost = systems.get("ghost")
        if base != ghost:
            diffs.append((tick, base, ghost))
    return diffs

if __name__ == "__main__":
    actions = load_actions(INPUT_FILE)
    diffs = diff(actions)

    print("tick,baseline_action,ghost_action")
    for tick, base, ghost in diffs:
        print(f"{tick},{base},{ghost}")

    print(f"\nTotal divergent ticks: {len(diffs)}")
