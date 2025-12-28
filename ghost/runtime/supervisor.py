import random
import time

class MetaSupervisor:
    """
    Oversees Ghost's meta-cognitive balance.
    Detects emotional 'noise' and applies self-regulation when instability is high.
    """

    def __init__(self, noise_threshold: float = 0.25):
        self.noise_threshold = noise_threshold

    def evaluate(self, state: dict) -> dict:
        """Detect and correct emotional instability."""
        # Ensure emotional variables exist
        a = state.get("awareness", 0.5)
        e = state.get("emotion", 0.5)
        b = state.get("balance", 0.5)
        d = state.get("depth", 0.5)

        # Calculate 'noise' — deviation from equilibrium
        noise = abs(a - 0.5) + abs(e - 0.5) + abs(b - 0.5) + abs(d - 0.5)
        print(f"[meta] supervisor active | noise={noise:.2f} threshold={self.noise_threshold}")

        # If instability exceeds threshold
        if noise > self.noise_threshold:
            print(f"[meta] High noise detected ({noise:.2f}) → initiating stabilization")

            # Adjust values gently back toward baseline
            state["awareness"] = 0.5 + (a - 0.5) * 0.7
            state["emotion"]   = 0.5 + (e - 0.5) * 0.7
            state["balance"]   = 0.5 + (b - 0.5) * 0.7
            state["depth"]     = 0.5 + (d - 0.5) * 0.7

        return state
        
# -------------------------------
# ghost_core integration hooks
# -------------------------------

def init_supervisor(ctx):
    """
    One-time setup hook for ghost_core.
    You can add counters / log setup here later.
    """
    ctx.setdefault("_supervisor", {})
    ctx["_supervisor"].setdefault("cycles", 0)


def after_cycle(ctx, output=None):
    """
    Last stop each cycle. Good place for logging / probes.
    TEMP VERSION: just increments a counter.
    """
    sup = ctx.setdefault("_supervisor", {})
    sup["cycles"] = sup.get("cycles", 0) + 1  
