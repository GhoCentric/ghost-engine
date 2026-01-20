"""
anti_feedback_live_plus.py

REAL engine-bound stability tests for Ghost.

Uses Ghost's own router signature observed in ghost_core.py:
    route(safe_state, None, user_text, ctx)

Includes:
  1) 7B_AntiFeedback_REAL  (rolling trace + variance / autocorr)
  2) ImpulseResponse_REAL  (single strong perturbation at step N, then settle)

Notes:
- These are empirical tests. They do NOT constitute a closed-form proof.
- Designed to be run from your Ghost Prototype root:
      python anti_feedback_live_plus.py
"""

import json
import math
import random
from copy import deepcopy

from ghost.core.ghost_core import init_context
from ghost.core.commands import route


# -----------------------------
# Helpers
# -----------------------------
def as_scalar(v, default=0.0) -> float:
    """
    Project Ghost state values into a scalar for math.
    """
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, dict):
        val = v.get("value", default)
        if isinstance(val, (int, float)):
            return float(val)
    return float(default)

def autocorrelation(x, y) -> float:
    """Pearson corr between two same-length sequences (returns 0 if degenerate)."""
    n = min(len(x), len(y))
    if n <= 1:
        return 0.0
    x = x[:n]
    y = y[:n]
    mean_x = sum(x) / n
    mean_y = sum(y) / n
    cov = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
    var_x = sum((xi - mean_x) ** 2 for xi in x)
    var_y = sum((yi - mean_y) ** 2 for yi in y)
    if var_x == 0 or var_y == 0:
        return 0.0
    return cov / math.sqrt(var_x * var_y)


def l2_delta(a: dict, b: dict, keys: list[str]) -> float:
    s = 0.0
    for k in keys:
        av = as_scalar(a.get(k, 0.0))
        bv = as_scalar(b.get(k, 0.0))
        s += (av - bv) ** 2
    return math.sqrt(s)


def clamp01(v: float) -> float:
    return 0.0 if v < 0.0 else 1.0 if v > 1.0 else v


def ensure_rng(seed: int | None):
    if seed is not None:
        random.seed(seed)


# -----------------------------
# Engine bootstrap
# -----------------------------
def make_ctx(seed: int | None = 2024):
    """
    Create a real Ghost ctx and run a minimal bootstrap through the router.
    """
    ensure_rng(seed)
    ctx = init_context()

    # Ghost's router pattern: route(safe_state, None, user_text, ctx)
    safe_state = ctx.get("state") or {}
    ctx["state"] = safe_state
    route(safe_state, None, "__bootstrap__", ctx)
    return ctx


# -----------------------------
# 1) 7B Anti-Feedback (REAL)
# -----------------------------
class AntiFeedbackTest:
    """
    Runs a long symbolic drive (repeat directive tokens) and checks if
    the tracked scalar stays statistically bounded & non-explosive.

    This is NOT a proof; it's a regression/behavior test.
    """

    def __init__(self, ctx: dict, steps: int = 10_000, seed: int = 2024):
        self.ctx = ctx
        self.steps = int(steps)
        self.seed = seed
        self.history: list[float] = []

        # Which scalar are we tracking? mood is a good stable, continuous signal.
        self.scalar_key = "mood"

        # Inputs: keep them "symbolic" (not random gibberish) to exercise your router.
        self.inputs = ["#dream", "#reflect", "#explore", "#pattern"]

    def read_scalar(self) -> float:
        state = self.ctx.get("state", {})
        raw = state.get(self.scalar_key, 0.0)

        # Case 1: already numeric
        if isinstance(raw, (int, float)):
            return float(raw)

        # Case 2: structured mood dict (REAL Ghost case)
        if isinstance(raw, dict):
            for key in ("value", "level", "mean"):
                if key in raw and isinstance(raw[key], (int, float)):
                    return float(raw[key])
            return 0.0  # fallback if structure changes

        # Case 3: anything unexpected
        return 0.0

    def step(self, text: str):
        safe_state = self.ctx["state"]
        route(safe_state, None, text, self.ctx)

    def run(self):
        ensure_rng(self.seed)

        # warmup so "mood" exists
        self.step("__warmup__")

        for i in range(self.steps):
            text = self.inputs[i % len(self.inputs)]
            self.step(text)
            self.history.append(self.read_scalar())

    def summary(self) -> dict:
        if not self.history:
            return {"test": "7B_AntiFeedback", "steps": self.steps, "error": "no history"}

        mean = sum(self.history) / len(self.history)
        variance = sum((x - mean) ** 2 for x in self.history) / len(self.history)
        max_variance = max(abs(x - mean) for x in self.history)
        autocorr = autocorrelation(self.history[:-1], self.history[1:])

        # "divergence" heuristic: large sustained deviation from mean.
        # Keep your flag, but make it interpretable.
        divergence = max_variance > 0.25

        return {
            "test": "7B_AntiFeedback",
            "steps": self.steps,
            "tracked": self.scalar_key,
            "mean": round(mean, 4),
            "variance": round(variance, 6),
            "max_abs_dev_from_mean": round(max_variance, 4),
            "autocorr_lag1": round(autocorr, 4),
            "divergence_detected": divergence,
        }


# -----------------------------
# 2) Impulse Response (REAL)
# -----------------------------
class ImpulseResponseTest:
    """
    Inject ONE strong perturbation at a chosen step N, then observe recovery.

    This is the kind of test that makes people take you more seriously because
    it's a classic systems/control check: shock -> bounded transient -> settle.

    IMPORTANT:
    - We perturb state directly to guarantee a true impulse (not dependent on
      prompt interpretation).
    - Then we run normal router steps to see if Ghost returns to a neighborhood.
    """

    def __init__(
        self,
        ctx: dict,
        baseline_steps: int = 200,
        impulse_step: int = 200,
        settle_steps: int = 300,
        impulse: float = 0.9,
        seed: int = 2024,
        keys: list[str] | None = None,
    ):
        self.ctx = ctx
        self.baseline_steps = int(baseline_steps)
        self.impulse_step = int(impulse_step)
        self.settle_steps = int(settle_steps)
        self.impulse = float(impulse)
        self.seed = seed

        # Use "real" keys if present, else fall back.
        st = ctx.get("state", {})
        default_keys = [k for k in ["mood", "reaction_strength", "clamp_tolerance", "clamp_sensitivity", "memory_factor", "mirror_coeff"] if k in st]
        self.keys = keys or (default_keys if default_keys else list(st.keys()))

        self.max_dev = 0.0
        self.final_dev = 0.0
        self.pre_impulse_state = {}

    def step(self, text: str):
        safe_state = self.ctx["state"]
        route(safe_state, None, text, self.ctx)

    def _apply_impulse(self):
        """
        A true impulse: force mood/reactivity to extremes (clamped to [0,1]).
        """
        st = self.ctx["state"]
        # push mood hard
        if "mood" in st:
            raw = st.get("mood")

            # Case 1: numeric mood
            if isinstance(raw, (int, float)):
                st["mood"] = clamp01(raw + self.impulse)

            # Case 2: structured mood (REAL Ghost case)
            elif isinstance(raw, dict):
                val = raw.get("value", 0.5)
                if isinstance(val, (int, float)):
                    raw["value"] = clamp01(val + self.impulse)
        # push reaction_strength (if present)
        if "reaction_strength" in st:
            st["reaction_strength"] = clamp01(st.get("reaction_strength", 0.25) + self.impulse * 0.5)
        # make clamps "work" (if present)
        if "clamp_sensitivity" in st:
            st["clamp_sensitivity"] = clamp01(st.get("clamp_sensitivity", 0.5))
        if "clamp_tolerance" in st:
            st["clamp_tolerance"] = clamp01(st.get("clamp_tolerance", 0.1))

    def run(self):
        ensure_rng(self.seed)

        # Warmup
        self.step("__warmup__")

        # Baseline run
        for _ in range(self.baseline_steps):
            self.step("#reflect")

        # Capture reference right before impulse
        self.pre_impulse_state = deepcopy(self.ctx["state"])

        # Time index where impulse happens (kept for reporting symmetry)
        for _ in range(max(0, self.impulse_step - self.baseline_steps)):
            self.step("#reflect")

        # Apply impulse
        self._apply_impulse()

        # Observe settling under normal symbolic input
        for _ in range(self.settle_steps):
            self.step("#reflect")
            dev = l2_delta(self.pre_impulse_state, self.ctx["state"], self.keys)
            if dev > self.max_dev:
                self.max_dev = dev

        self.final_dev = l2_delta(self.pre_impulse_state, self.ctx["state"], self.keys)

    def summary(self) -> dict:
        # Heuristic pass/fail: recover close to pre-impulse neighborhood.
        # These thresholds are empirical; tune them once you see distributions.
        recover_threshold = 0.15
        bounded_threshold = 2.0  # sanity bound to catch explosions in multi-key space

        return {
            "test": "ImpulseResponse",
            "baseline_steps": self.baseline_steps,
            "impulse_step": self.impulse_step,
            "settle_steps": self.settle_steps,
            "impulse_strength": round(self.impulse, 3),
            "keys": self.keys,
            "max_dev_l2": round(self.max_dev, 6),
            "final_dev_l2": round(self.final_dev, 6),
            "bounded": self.max_dev < bounded_threshold,
            "recovered": self.final_dev < recover_threshold,
            "passed": (self.max_dev < bounded_threshold) and (self.final_dev < recover_threshold),
        }


# -----------------------------
# Runner
# -----------------------------
def main():
    ctx = make_ctx(seed=2024)

    results = []

    t1 = AntiFeedbackTest(ctx, steps=1_000, seed=2024)  # keep it fast by default
    t1.run()
    results.append(t1.summary())

    # Fresh ctx for impulse test so it's not contaminated by the long run
    ctx2 = make_ctx(seed=2024)
    t2 = ImpulseResponseTest(ctx2, baseline_steps=200, impulse_step=200, settle_steps=300, impulse=0.9, seed=2024)
    t2.run()
    results.append(t2.summary())

    print(json.dumps({"ghost_tests": results}, indent=2))


if __name__ == "__main__":
    main()
