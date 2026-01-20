"""proof_suite_bound.py

Ghost Proof Suite (BOUND)

This version binds every test to the *real* Ghost context/state vector (ctx['state'])
by driving the actual Ghost cycle (ghost.core.ghost_core.run_cycle) when available.

If Ghost cannot be imported (e.g., you run this file outside your repo), it will
fall back to a tiny internal stub so the script still runs — but the output will
clearly say it's in STUB mode.

No external libraries.
"""

from __future__ import annotations

import math
import random
import time
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------
# Utilities (no numpy)
# ---------------------------

def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return lo if x < lo else hi if x > hi else x


def l2_norm(vec: List[float]) -> float:
    return math.sqrt(sum(v * v for v in vec))


def l2_dist(a: List[float], b: List[float]) -> float:
    return l2_norm([x - y for x, y in zip(a, b)])


def linf_dist(a: List[float], b: List[float]) -> float:
    return max((abs(x - y) for x, y in zip(a, b)), default=0.0)


def autocorrelation(xs: List[float], ys: List[float]) -> float:
    """Pearson corr(xs, ys) with safety for zero variance."""
    n = min(len(xs), len(ys))
    if n <= 1:
        return 0.0
    xs = xs[:n]
    ys = ys[:n]
    mx = sum(xs) / n
    my = sum(ys) / n
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    if vx <= 1e-12 or vy <= 1e-12:
        return 0.0
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    return cov / math.sqrt(vx * vy)


def summarize_vector(v: List[float]) -> Dict[str, float]:
    if not v:
        return {"min": 0.0, "max": 0.0, "mean": 0.0}
    return {
        "min": min(v),
        "max": max(v),
        "mean": sum(v) / len(v),
    }


# ---------------------------
# Binding layer: drive REAL Ghost if available
# ---------------------------

class GhostHarness:
    """Runs Ghost cycles and exposes a consistent state-vector/mood interface."""

    def __init__(self, seed: int = 1337):
        self.seed = seed
        random.seed(seed)
        self.mode = "STUB"

        self._init_context = None
        self._run_cycle = None
        self.ctx: Dict[str, Any] = {}

        try:
            from ghost.core.ghost_core import init_context, run_cycle  # type: ignore

            self._init_context = init_context
            self._run_cycle = run_cycle
            self.mode = "REAL"
        except Exception:
            # Could not import real Ghost — stay in STUB mode.
            self._init_context = None
            self._run_cycle = None
            self.mode = "STUB"

        self.ctx = self._make_ctx()

    def _make_ctx(self) -> Dict[str, Any]:
        if self.mode == "REAL" and self._init_context:
            ctx = self._init_context()
            # Force test-safe settings
            ctx["demo_mode"] = True
            ctx["llm_enabled"] = False
            ctx["use_llm"] = False
            ctx["_proof_suite"] = True
            return ctx

        # ---- STUB fallback ----
        return {
            "demo_mode": True,
            "llm_enabled": False,
            "use_llm": False,
            "cycle": 0,
            "raw_input": "",
            "input": None,
            "world": {},
            "state": {"A": 0.5, "B": 0.5, "E": 0.5, "D": 0.5, "mood": 0.5},
        }

    def reset(self) -> None:
        self.ctx = self._make_ctx()

    def step(self, stimulus: float) -> None:
        """Advance one step using a numeric stimulus."""
        if self.mode == "REAL" and self._run_cycle:
            # Feed the stimulus through the normal cycle.
            # We pass it as user_text (string) and world feedback (numeric).
            self._run_cycle(str(stimulus), {"stimulus": stimulus}, self.ctx)
            return

        # ---- STUB dynamics: bounded damped update ----
        s = float(stimulus)
        st = self.ctx["state"]
        for k in ["A", "B", "E", "D"]:
            x = float(st.get(k, 0.5))
            # inertia + bounded delta
            x = 0.85 * x + 0.15 * clamp(x + 0.05 * s)
            st[k] = clamp(x)
        st["mood"] = clamp(sum(float(st.get(k, 0.5)) for k in ["A", "B", "E", "D"]) / 4.0)
        self.ctx["cycle"] = int(self.ctx.get("cycle", 0)) + 1

    def get_state_vector(self) -> Tuple[List[float], List[str]]:
        """Return ([values], [keys]) from ctx['state'] in a stable order."""
        st = self.ctx.get("state", {}) or {}

        # Prefer canonical Ghost axes if present
        preferred = ["A", "B", "E", "D"]
        if all(k in st for k in preferred):
            return [float(st[k]) for k in preferred], preferred

        # Else try common names
        alt = ["awareness", "balance", "emotion", "depth"]
        if all(k in st for k in alt):
            return [float(st[k]) for k in alt], alt

        # Else: take numeric-ish entries (excluding obvious non-state)
        skip = {"mood_memory"}
        items: List[Tuple[str, float]] = []
        for k, v in st.items():
            if k in skip:
                continue
            if isinstance(v, (int, float)):
                items.append((str(k), float(v)))
        items.sort(key=lambda kv: kv[0])
        keys = [k for k, _ in items]
        vec = [v for _, v in items]
        return vec, keys

    def get_mood(self) -> float:
        st = self.ctx.get("state", {}) or {}
        if isinstance(st.get("mood"), (int, float)):
            return float(st["mood"])
        # fallback: mean of vector
        vec, _ = self.get_state_vector()
        return sum(vec) / len(vec) if vec else 0.5


# ---------------------------
# Tests
# ---------------------------

class BaseTest:
    name: str = "Base"

    def run(self, h: GhostHarness) -> None:
        raise NotImplementedError

    def summary(self) -> Dict[str, Any]:
        raise NotImplementedError


class AntiFeedbackTest(BaseTest):
    name = "7B_AntiFeedback"

    def __init__(self, steps: int = 10_000):
        self.steps = int(steps)
        self.history: List[float] = []
        self.divergence_detected = False

    def run(self, h: GhostHarness) -> None:
        self.history = []
        for _ in range(self.steps):
            stimulus = random.uniform(-1.0, 1.0)
            h.step(stimulus)
            self.history.append(h.get_mood())
            # crude divergence: mood blows past bounds (should never happen)
            if self.history[-1] < -0.001 or self.history[-1] > 1.001:
                self.divergence_detected = True
                break

    def summary(self) -> Dict[str, Any]:
        if not self.history:
            return {"test": self.name, "steps": self.steps, "error": "no history"}
        mean = sum(self.history) / len(self.history)
        var = sum((x - mean) ** 2 for x in self.history) / len(self.history)
        max_var = max(abs(x - mean) for x in self.history)
        ac1 = autocorrelation(self.history[:-1], self.history[1:])
        return {
            "test": self.name,
            "mode": "REAL" if "REAL" in str(self.name) else None,
            "steps": self.steps,
            "mean_mood": round(mean, 4),
            "variance": round(var, 6),
            "max_variance": round(max_var, 4),
            "autocorrelation_lag1": round(ac1, 4),
            "divergence_detected": bool(self.divergence_detected),
        }


class BoundsInvariantTest(BaseTest):
    name = "BoundsInvariant"

    def __init__(self, steps: int = 5_000, lo: float = 0.0, hi: float = 1.0):
        self.steps = int(steps)
        self.lo = float(lo)
        self.hi = float(hi)
        self.violations: int = 0
        self.max_overshoot: float = 0.0

    def run(self, h: GhostHarness) -> None:
        self.violations = 0
        self.max_overshoot = 0.0
        for _ in range(self.steps):
            h.step(random.uniform(-1.0, 1.0))
            vec, keys = h.get_state_vector()
            for k, v in zip(keys, vec):
                if v < self.lo or v > self.hi:
                    self.violations += 1
                    overshoot = max(self.lo - v, v - self.hi)
                    if overshoot > self.max_overshoot:
                        self.max_overshoot = overshoot

    def summary(self) -> Dict[str, Any]:
        return {
            "test": self.name,
            "steps": self.steps,
            "violations": self.violations,
            "max_overshoot": round(self.max_overshoot, 6),
        }


class ImpulseResponseTest(BaseTest):
    name = "ImpulseResponse"

    def __init__(self, baseline_steps: int = 2_000, impulse: float = 1.0, settle_steps: int = 300):
        self.baseline_steps = int(baseline_steps)
        self.impulse = float(impulse)
        self.settle_steps = int(settle_steps)
        self.max_deviation_l2: float = 0.0
        self.final_deviation_l2: float = 0.0

    def run(self, h: GhostHarness) -> None:
        # Reach a typical regime
        for _ in range(self.baseline_steps):
            h.step(random.uniform(-0.3, 0.3))
        base_vec, _ = h.get_state_vector()

        # Apply one impulse
        h.step(self.impulse)
        v1, _ = h.get_state_vector()
        self.max_deviation_l2 = l2_dist(base_vec, v1)

        # Let it settle
        cur = v1
        for _ in range(self.settle_steps):
            h.step(0.0)
            cur, _ = h.get_state_vector()
            self.max_deviation_l2 = max(self.max_deviation_l2, l2_dist(base_vec, cur))

        self.final_deviation_l2 = l2_dist(base_vec, cur)

    def summary(self) -> Dict[str, Any]:
        return {
            "test": self.name,
            "baseline_steps": self.baseline_steps,
            "impulse": self.impulse,
            "settle_steps": self.settle_steps,
            "max_deviation_l2": round(self.max_deviation_l2, 6),
            "final_deviation_l2": round(self.final_deviation_l2, 6),
        }


class HysteresisTest(BaseTest):
    name = "Hysteresis"

    def __init__(self, magnitude: float = 1.0, hold_steps: int = 200):
        self.magnitude = float(magnitude)
        self.hold_steps = int(hold_steps)
        self.memory_effect: bool = False
        self.forward_end: float = 0.0
        self.backward_end: float = 0.0

    def run(self, h: GhostHarness) -> None:
        # Forward: push +magnitude
        for _ in range(self.hold_steps):
            h.step(+self.magnitude)
        self.forward_end = h.get_mood()

        # Backward: push -magnitude
        for _ in range(self.hold_steps):
            h.step(-self.magnitude)
        self.backward_end = h.get_mood()

        # If system has memory / inertia, forward_end and backward_end tend not to be symmetric.
        self.memory_effect = abs(self.forward_end - (1.0 - self.backward_end)) > 0.01

    def summary(self) -> Dict[str, Any]:
        return {
            "test": self.name,
            "magnitude": self.magnitude,
            "hold_steps": self.hold_steps,
            "forward_end_mood": round(self.forward_end, 4),
            "backward_end_mood": round(self.backward_end, 4),
            "memory_effect": bool(self.memory_effect),
        }


class DeterminismTest(BaseTest):
    name = "Determinism"

    def __init__(self, steps: int = 2_000, stimulus_seed: int = 2024):
        self.steps = int(steps)
        self.stimulus_seed = int(stimulus_seed)
        self.same_trace = False
        self.max_abs_diff = 0.0

    def run(self, h: GhostHarness) -> None:
        # Generate a fixed stimulus trace
        rng = random.Random(self.stimulus_seed)
        trace = [rng.uniform(-1.0, 1.0) for _ in range(self.steps)]

        # Run #1
        h.reset()
        v_hist_1: List[List[float]] = []
        for s in trace:
            h.step(s)
            vec, _ = h.get_state_vector()
            v_hist_1.append(vec)

        # Run #2
        h.reset()
        v_hist_2: List[List[float]] = []
        for s in trace:
            h.step(s)
            vec, _ = h.get_state_vector()
            v_hist_2.append(vec)

        # Compare
        self.max_abs_diff = 0.0
        for a, b in zip(v_hist_1, v_hist_2):
            if len(a) != len(b):
                self.max_abs_diff = float("inf")
                break
            self.max_abs_diff = max(self.max_abs_diff, linf_dist(a, b))

        self.same_trace = self.max_abs_diff == 0.0

    def summary(self) -> Dict[str, Any]:
        return {
            "test": self.name,
            "steps": self.steps,
            "stimulus_seed": self.stimulus_seed,
            "same_trace": bool(self.same_trace),
            "max_abs_diff": round(self.max_abs_diff, 8) if math.isfinite(self.max_abs_diff) else self.max_abs_diff,
        }


# ---- "Formal proof" placeholders (honest) ----

class ClosedFormLyapunovClaimTest(BaseTest):
    name = "ClosedFormLyapunovClaim"

    def run(self, h: GhostHarness) -> None:
        pass

    def summary(self) -> Dict[str, Any]:
        return {
            "test": self.name,
            "passed": False,
            "reason": "A closed-form Lyapunov proof is a math derivation about the update equations. A simulation test cannot prove it."
        }


class SymbolicConvergenceClaimTest(BaseTest):
    name = "SymbolicConvergenceClaim"

    def run(self, h: GhostHarness) -> None:
        pass

    def summary(self) -> Dict[str, Any]:
        return {
            "test": self.name,
            "passed": False,
            "reason": "Symbolic convergence proof requires symbolic analysis of the transition function, not black-box runs."
        }


class CombinatorialExhaustionClaimTest(BaseTest):
    name = "CombinatorialStateSpaceExhaustionClaim"

    def run(self, h: GhostHarness) -> None:
        pass

    def summary(self) -> Dict[str, Any]:
        return {
            "test": self.name,
            "passed": False,
            "reason": "Exhaustion means enumerating a discrete state space. Your system is continuous; discretization can only approximate coverage."
        }


class GlobalOptimalityClaimTest(BaseTest):
    name = "GlobalOptimalityClaim"

    def run(self, h: GhostHarness) -> None:
        pass

    def summary(self) -> Dict[str, Any]:
        return {
            "test": self.name,
            "passed": False,
            "reason": "Global optimality is about an objective function and guarantees. Ghost isn't an optimizer in this proof suite."
        }


# ---------------------------
# Runner
# ---------------------------

def run_all() -> None:
    h = GhostHarness(seed=1337)

    print("=== GHOST PROOF SUITE (BOUND) ===")
    print({"binding_mode": h.mode, "state_keys": h.get_state_vector()[1]})

    tests: List[BaseTest] = [
        AntiFeedbackTest(steps=10_000),
        BoundsInvariantTest(steps=5_000),
        ImpulseResponseTest(baseline_steps=2_000, impulse=1.0, settle_steps=300),
        HysteresisTest(magnitude=1.0, hold_steps=200),
        DeterminismTest(steps=2_000, stimulus_seed=2024),

        # "Formal proof" claims (honest placeholders)
        ClosedFormLyapunovClaimTest(),
        SymbolicConvergenceClaimTest(),
        CombinatorialExhaustionClaimTest(),
        GlobalOptimalityClaimTest(),
    ]

    for t in tests:
        # keep each test independent
        h.reset()
        t.run(h)
        print(t.summary())


if __name__ == "__main__":
    run_all()
