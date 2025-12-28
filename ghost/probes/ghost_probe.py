# ghost_probe.py
#
# Emergent Probe Pack v1
# Runs long stress cycles on Ghost's core loop and logs internal ranges.

import random
import time

from .state import (
    ghost_state,
    update_mood,
    mirror_directive_monitor,
    reflect_mood,
    print_state_summary,
)

def run_probe(run_id: str, steps: int = 200, stim_center: float = 0.5, stim_spread: float = 0.18):
    """
    Run a single probe pass:
    - steps: how many heartbeats to simulate
    - stim_center: baseline stimulus level
    - stim_spread: how much random noise around that baseline
    """
    history = []

    print(f"\n==============================")
    print(f"   PROBE RUN: {run_id}")
    print(f"   steps={steps}, center={stim_center}, spread={stim_spread}")
    print(f"==============================")

    for i in range(1, steps + 1):
        # 1) generate a small random stimulus
        stim = stim_center + random.uniform(-stim_spread, stim_spread)

        # 2) push it through Ghost's existing loop
        update_mood(stim)
        summary, coeff = mirror_directive_monitor()
        reflect_mood()

        # 3) pull out key internal knobs
        mem = ghost_state.get("memory_factor", 0.75)
        react = ghost_state.get("reaction_strength", 0.25)
        clamp_tol = ghost_state.get("clamp_tolerance", 0.10)
        clamp_sens = ghost_state.get("clamp_sensitivity", 0.50)

        mood_snapshot = {
            k: ghost_state.get(k)
            for k in ("awareness", "emotion", "balance", "subdepth")
            if k in ghost_state
        }

        # 4) record this step
        history.append({
            "step": i,
            "stimulus": round(stim, 3),
            "mirror_coeff": round(coeff, 3) if coeff is not None else None,
            "memory_factor": round(mem, 3),
            "reaction_strength": round(react, 3),
            "clamp_tolerance": round(clamp_tol, 3),
            "clamp_sensitivity": round(clamp_sens, 3),
            "mood": mood_snapshot,
        })

        # light, human-readable trace every 25 steps
        if i % 25 == 0 or i == 1:
            print(
                f"[{run_id} #{i:03d}] "
                f"stim={stim:.3f} "
                f"mc={history[-1]['mirror_coeff']} "
                f"mem={history[-1]['memory_factor']} "
                f"react={history[-1]['reaction_strength']} "
                f"mood={mood_snapshot}"
            )

    # 5) summarize ranges
    def rng(xs):
        xs = [x for x in xs if x is not None]
        if not xs:
            return None, None
        return min(xs), max(xs)

    coeffs = [h["mirror_coeff"] for h in history]
    mems = [h["memory_factor"] for h in history]
    reacts = [h["reaction_strength"] for h in history]

    coeff_min, coeff_max = rng(coeffs)
    mem_min, mem_max = rng(mems)
    react_min, react_max = rng(reacts)

    print(f"\n--- PROBE SUMMARY: {run_id} ---")
    print(f"steps: {steps}")
    if coeff_min is not None:
        print(f"mirror_coeff range: {coeff_min:.3f} → {coeff_max:.3f}")
    print(f"memory_factor range: {mem_min:.3f} → {mem_max:.3f}")
    print(f"reaction_strength range: {react_min:.3f} → {react_max:.3f}")
    print("\n[Final Ghost state snapshot]")
    print_state_summary(ghost_state)
    print("----------------------------\n")

    return history


if __name__ == "__main__":
    # Three different regimes to start seeing patterns:
    probe_runs = [
        ("low_noise", 200, 0.50, 0.05),   # gentle, almost calm
        ("mid_noise", 300, 0.50, 0.12),   # your usual working band
        ("high_noise", 400, 0.50, 0.20),  # violent, chaos band
    ]

    for run_id, steps, center, spread in probe_runs:
        run_probe(run_id, steps=steps, stim_center=center, stim_spread=spread)
        time.sleep(0.3)
