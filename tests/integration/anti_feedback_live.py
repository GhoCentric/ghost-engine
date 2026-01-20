import json
import random

from ghost.core.ghost_core import init_context
from ghost.core.commands import route

# -----------------------------
# Initialize REAL Ghost context
# -----------------------------
ctx = init_context()

# Proper bootstrap: route(safe_state, None, user_text, ctx)
safe_state = ctx.get("state")
route(safe_state, None, "__bootstrap__", ctx)

# -----------------------------
# Stability Test: 7B Anti-Feedback (REAL, CONNECTED)
# -----------------------------

def autocorrelation(x, y):
    n = len(x)
    if n == 0:
        return 0.0

    mean_x = sum(x) / n
    mean_y = sum(y) / n

    cov = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
    var_x = sum((xi - mean_x) ** 2 for xi in x)
    var_y = sum((yi - mean_y) ** 2 for yi in y)

    if var_x == 0 or var_y == 0:
        return 0.0

    return cov / ((var_x ** 0.5) * (var_y ** 0.5))


class AntiFeedbackTest:
    def __init__(self, ctx, steps=1_000):
        self.ctx = ctx
        self.steps = steps
        self.history = []

    def read_mood(self):
        state = self.ctx.get("state", {})

        if isinstance(state.get("mood"), (int, float)):
            return state["mood"]

        if isinstance(state.get("mood"), dict):
            return sum(state["mood"].values()) / len(state["mood"])

        raise RuntimeError("Cannot locate live mood state in ctx['state'].")

    def run(self):
        for _ in range(self.steps):
            stimulus = random.choice([
                "#dream",
                "#reflect",
                "#pattern",
                "#explore",
                "random thought",
                "noise"
            ])

            route(self.ctx.get("state"), None, stimulus, self.ctx)
            self.history.append(self.read_mood())

    def summary(self):
        mean = sum(self.history) / len(self.history)
        variance = sum((x - mean) ** 2 for x in self.history) / len(self.history)
        max_variance = max(abs(x - mean) for x in self.history)
        autocorr = autocorrelation(self.history[:-1], self.history[1:])

        # --- divergence logic (MUST be outside the dict) ---
        half = len(self.history) // 2
        mean_early = sum(self.history[:half]) / half
        mean_late = sum(self.history[half:]) / (len(self.history) - half)
        divergence = abs(mean_late - mean_early) > 0.05

        return {
            "test": "7B_AntiFeedback_REAL",
            "steps": self.steps,
            "mean_mood": round(mean, 4),
            "variance": round(variance, 6),
            "max_variance": round(max_variance, 4),
            "autocorrelation_lag1": round(autocorr, 4),
            "divergence_detected": divergence
        }


if __name__ == "__main__":
    test = AntiFeedbackTest(ctx, steps=1_000)
    test.run()
    print(json.dumps(test.summary(), indent=2))
