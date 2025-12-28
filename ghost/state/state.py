"""
state.py — Ghost Prototype
Persistent runtime state management with emotional baseline support.
"""

import json
from pathlib import Path
import time
# ---------------------------------------------------------------------------
# Core paths (adjust if your project uses a different structure)
# ---------------------------------------------------------------------------

DATA_PATH = Path(__file__).resolve().parent / "data"
STATE_FILE = DATA_PATH / "state.json"
# --------------------------------------------------
# Clamp regulation parameters (emotional tolerance)
# --------------------------------------------------
BASE_CLAMP_TOL   = 0.10   # "normal" clamp level
MIN_CLAMP_TOL    = 0.03   # never tighter than this
MAX_CLAMP_TOL    = 0.25   # never looser than this
CLAMP_ADAPT_RATE = 0.15   # how fast Ghost slides toward target
# ---------------------------------------------------------------------------
# State helpers
# ---------------------------------------------------------------------------

def load_state(data_dir: Path = DATA_PATH) -> dict:
    """
    Load the state dictionary from disk.
    Always returns a valid dictionary, never None.
    """
    file_path = STATE_FILE

    # Use provided data_dir if STATE_FILE doesn't exist
    if not file_path.exists():
        file_path = data_dir / "ghost_state.json"
        if not file_path.exists():
            print("(creating new state.json)")
            return init_mood_state({})

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("Invalid file contents")
    except (OSError, ValueError, json.JSONDecodeError) as e:
        print(f"[state] warning while loading: {e}")
        data = {}

    # Ensure mood structure exists
    if "mood" not in data:
        data["mood"] = {
            "A": 0.5,  # Arousal
            "E": 0.5,  # Emotion
            "B": 0.5,  # Balance
            "D": 0.5,  # Depth / Drift
            "arousal": 0.5,  # Cognitive intensity
            "valence": 0.5,  # Positive/negative stability
            "clarity": 0.5   # Awareness or coherence
    }

    print("[integrity] state file validated → OK ✅")

    # Optional: brief description output
    print(describe_mood(init_mood_state(data)))

    # 🧠 Validate and repair mood data if needed
    mood = data.get("mood", {})
    if not isinstance(mood, (dict, int, float)):
        mood = {}
    repaired = False
    # Normalize mood before validation
    if isinstance(mood, (int, float)):
        mood = {
            "A": float(mood),
            "E": float(mood),
            "B": float(mood),
            "D": float(mood),
        }
    for key in ("A", "E", "B", "D"):
        if key not in mood or not isinstance(mood[key], (int, float)) or not (0.0 <= mood[key] <= 1.0):
            print(f"[integrity] repairing invalid or missing key '{key}' → reset to 0.5")
            mood[key] = 0.5
            repaired = True
    data["mood"] = mood

    if repaired:
        print("[integrity] state file repaired and normalized ✅")
        save_state(DATA_PATH, data)
        print("[integrity] repaired state automatically saved 💾")
    else:
        print("[integrity] state file passed validation ✅")

    return data


def save_state(data_dir: Path = DATA_PATH, state: dict = None) -> None:
    """Save current runtime state to disk."""
    if state is None:
        return

    DATA_PATH.mkdir(parents=True, exist_ok=True)
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            # Ensure all emotional dimensions exist before saving
            state.setdefault("awareness", 0.5)
            state.setdefault("emotion", 0.5)
            state.setdefault("balance", 0.5)
            state.setdefault("depth", 0.5)

            json.dump(state, f, indent=2)

    except (OSError, TypeError, ValueError) as e:
        print(f"[state] warning while saving: {e}")


# ---------------------------------------------------------------------------
# Mood / Awareness subsystem
# ---------------------------------------------------------------------------

def init_context(state: dict) -> dict:
    """Initialize Ghost’s short-term working memory context."""
    state.setdefault("context", {
        "last_strategy": "reflect",
        "dominant_emotion": "A",
        "variance_trend": "stable",
        "focus_topic": None
    })
    return state


def init_mood_state(state: dict) -> dict:
    """Ensure core emotional variables exist in state."""
    state.setdefault("awareness", 0.7)
    state.setdefault("emotion", 0.3)
    state.setdefault("balance", 0.5)
    state.setdefault("depth", 0.5)
    state.setdefault("clamp_tolerance", BASE_CLAMP_TOL)
    # keep your existing context init
    state = init_context(state)

    # NEW: also initialize goal subsystem
    state = init_goal_state(state)

    return state
    
# ------------------------------------------------------------
# Goal / Intent subsystem
# ------------------------------------------------------------

def init_goal_state(state: dict) -> dict:
    """
    Initialize Ghost's internal target mood vector and how strongly
    it should pull toward it each cycle.
    """
    state.setdefault("goal_state", {
        "A": 0.5,  # desired awareness
        "E": 0.5,  # desired emotional intensity
        "B": 0.5,  # desired balance
        "D": 0.5   # desired depth
    })
    # How hard the goal pulls the current mood toward those targets each tick
    state.setdefault("goal_strength", 0.08)
    return state

def apply_goal_gravity(state: dict) -> dict:
    """
    Softly pull Ghost's mood variables toward the internal goal_state.
    Called once per loop AFTER other mood updates.
    """
    goals = state.get("goal_state", {})
    strength = state.get("goal_strength", 0.0)

    if not goals or strength <= 0:
        return state

    # Map goal keys (A/E/B/D) onto actual state fields
    mapping = [
        ("A", "awareness"),
        ("E", "emotion"),
        ("B", "balance"),
        ("D", "depth"),
    ]

    for goal_key, state_key in mapping:
        target = goals.get(goal_key)
        if target is None:
            continue

        current = state.get(state_key, 0.5)
        delta = target - current

        # If we're already very close to the goal, inject a tiny wobble
        # so the system doesn't freeze perfectly on the target.
        if abs(delta) < 0.015:
            delta += random.uniform(-0.01, 0.01)

        new_value = current + delta * strength

        # Keep everything in [0.0, 1.0]
        new_value = max(0.0, min(1.0, new_value))
        state[state_key] = new_value

    return state
    
# --- mood management --------------------------------------------------------
def adjust_mood(state, **kwargs):
    """
    Adjust or add mood dimensions dynamically.
    Example: adjust_mood(state, A=0.7, E=0.6)
    """
    mood = state.setdefault("mood", {
        "A": 0.5,  # Arousal
        "E": 0.5,  # Emotion (valence)
        "B": 0.5,  # Balance
        "D": 0.5   # Depth / Drift
    })

    for key, value in kwargs.items():
        try:
            mood[key] = float(value)
        except ValueError:
            print(f"[warn] mood key '{key}' received non-float value {value}")

    state["mood"] = mood
    print(f"[mood] Updated → " + ", ".join(f"{k}={v:.2f}" for k, v in mood.items()))
    # After normal mood changes, apply slow pull toward goal
    state = apply_goal_gravity(state)
    return state
    


def describe_mood(state: dict) -> str:
    """Return readable description of Ghost’s current mood."""
    a = state.get("awareness", 0.7)
    e = state.get("emotion", 0.3)
    b = state.get("balance", 0.5)
    d = state.get("depth", 0.5)

    tone = "neutral"
    if e > 0.7:
        tone = "energized"
    elif e < 0.3:
        tone = "reflective"

    balance_label = "balanced"
    if b > 0.7:
        balance_label = "optimistic"
    elif b < 0.3:
        balance_label = "pessimistic"

    depth_label = (
        "surface" if d < 0.4 else
        "deep thought" if d > 0.7 else
        "mid-layer"
    )

    return f"A={a:.2f} E={e:.2f} B={b:.2f} D={d:.2f} → {tone}, {balance_label}, {depth_label}"


# ==========================================================
# Drift / Emotional Evolution Core
# ==========================================================
import random

def drift_mood(state: dict, a_drift=None, e_drift=None, b_drift=None, d_drift=None) -> dict:
    """
    Drift Ghost's mood slightly over time in a semi-random, natural pattern.
    If specific drifts are provided, apply them; otherwise generate subtle noise.
    """

    if state is None:
        print("[drift] Warning: state was None. Initializing fallback state.")
        state = {
            "awareness": 0.5,
            "emotion": 0.5,
            "balance": 0.5,
            "depth": 0.5,
        }

    # --- Apply random drift or user-defined drift safely ---
    def safe_add(value, drift_value):
        """Add drift safely, handling None values gracefully."""
        if value is None:
            value = 0.5  # neutral fallback baseline
        drift = drift_value if drift_value is not None else random.uniform(-0.02, 0.02)
        return value + drift

    a = safe_add(state.get("awareness"), a_drift)
    e = safe_add(state.get("emotion"), e_drift)
    b = safe_add(state.get("balance"), b_drift)
    d = safe_add(state.get("depth"), d_drift)

    # Clamp values between 0.0 and 1.0
    a = max(0.0, min(1.0, a))
    e = max(0.0, min(1.0, e))
    b = max(0.0, min(1.0, b))
    d = max(0.0, min(1.0, d))

    state["awareness"] = a
    state["emotion"] = e
    state["balance"] = b
    state["depth"] = d
    # --- New affective variables update ---
    # Compute change in variance or drift to estimate emotional feedback
    curr_variance = abs((a - 0.5) + (e - 0.5) + (b - 0.5) + (d - 0.5)) / 4.0
    prev_variance = state.get("prev_variance", curr_variance)

    delta_variance = prev_variance - curr_variance

    # Arousal rises with variance magnitude (more change = more arousal)
    state["arousal"] = min(1.0, max(0.0, state.get("arousal", 0.5) + abs(delta_variance) * 0.4))

    # Valence increases when stability improves
    state["valence"] = min(1.0, max(0.0, state.get("valence", 0.5) + delta_variance * 0.6))

    # Clarity tracks how steady the emotional field is (less variance = higher clarity)
    state["clarity"] = min(1.0, max(0.0, 1.0 - abs(curr_variance - 0.5) * 2))

    # Save current variance for next cycle comparison
    state["prev_variance"] = curr_variance

    # Debug output to monitor
    print(f"[affective] arousal={state['arousal']:.2f}, valence={state['valence']:.2f}, clarity={state['clarity']:.2f}")

    # --- Affective Feedback Loop (Cyclical Emotion Drift) ---
    from .meta import affective_tone

    tone_label = affective_tone(state)

    # Modulate drift targets slightly based on tone
    if tone_label == "calm":
        state["awareness"] = min(1.0, state["awareness"] + 0.01)
        state["balance"] = min(1.0, state["balance"] + 0.01)
    elif tone_label == "intense":
        state["emotion"] = min(1.0, state["emotion"] + 0.02)
        state["depth"] = max(0.0, state["depth"] - 0.01)
    elif tone_label == "somber":
        state["depth"] = min(1.0, state["depth"] + 0.02)
        state["emotion"] = max(0.0, state["emotion"] - 0.01)
    elif tone_label == "lucid":
        state["awareness"] = min(1.0, state["awareness"] + 0.015)
    elif tone_label == "hazy":
        state["awareness"] = max(0.0, state["awareness"] - 0.015)
        state["balance"] = max(0.0, state["balance"] - 0.01)
    elif tone_label == "bright":
        state["emotion"] = min(1.0, state["emotion"] + 0.015)
        state["balance"] = min(1.0, state["balance"] + 0.01)
    else:  # neutral / equilibrium
        # drift toward midline
        for k in ["emotion", "awareness", "balance", "depth"]:
            state[k] += (0.5 - state[k]) * 0.01

    print(f"[affective feedback] tone='{tone_label}' → drift adjusted")

    print(f"[drift] A={a:.2f} E={e:.2f} B={b:.2f} D={d:.2f} → natural emotional drift")
    return state

# =======================
# EMOTIONAL PERSISTENCE LAYER (PHASE 1)
# =======================

# Core emotional state for Ghost
ghost_state = {
    "mood": 0.5,                # baseline neutral
    "memory_factor": 0.75,      # emotional inertia (0.6–0.85 recommended)
    "reaction_strength": 0.25,  # how much new stimulus shifts mood

    # New clamp control variables
    "clamp_tolerance": 0.1,     # how far Ghost can adjust parameters per cycle
    "clamp_sensitivity": 0.5,   # how strongly Ghost reacts to mirror resonance/divergence

    # Mirror introspection tracking
    "mirror_coeff": 0.0,        # latest mirror resonance value
    "mirror_summary": ""        # textual description from last mirror cycle
}

def update_mood(stimulus):
    """
    Adjust Ghost's emotional state based on new stimulus input.
    """
    prev = ghost_state["mood"]
    memory = ghost_state["memory_factor"]
    reaction = ghost_state["reaction_strength"]

    new_mood = (prev * memory) + (stimulus * reaction)
    new_mood = max(0.0, min(1.0, new_mood))  # clamp between 0–1

    ghost_state["mood"] = new_mood
    return new_mood

def reflect_mood():
    """
    Generate reflection lines that combine Ghost's emotional tone
    with introspection feedback from the mirror monitor.
    """

    m = ghost_state["mood"]
    coeff = ghost_state.get("mirror_coeff", 0.0)
    summary = ghost_state.get("mirror_summary", "")

    # Emotional tone based on mood value
    if m > 0.7:
        tone = "bright and responsive"
    elif m > 0.55:
        tone = "steady and calm"
    elif m > 0.4:
        tone = "reserved but focused"
    else:
        tone = "dull and withdrawn"

    # Mirror feedback interpretation
    if coeff > 0.75:
        meta = "Its internal rhythm feels synchronized."
    elif coeff < 0.35:
        meta = "It senses internal drift and adapts carefully."
    else:
        meta = "Its feedback loops remain neutral."

    # Combine emotional + introspective narrative
    reflection = f"Ghost feels {tone}. {meta} {summary}"
    print(f"[reflection] {reflection}")
    return reflection

# =======================
# MIRROR DIRECTIVE MONITOR (PHASE 2.5)
# =======================
# Detects repeating internal emotional patterns across cycles.
# Adjusts emotional inertia slightly when mirroring occurs.

from collections import deque
import statistics

_loop_signature = deque(maxlen=20)

def update_loop_signature():
    """Record the latest mood value for pattern tracking."""
    _loop_signature.append(ghost_state["mood"])

def mirror_directive_monitor():
    """
    Analyze the recent loop signature and adjust Ghost's internal
    clamps. Returns (summary, mirror_coeff).

    This version includes 7B "clamp bleed-through": even when the
    mirror is neutral, reaction_strength slowly rises and
    memory_factor slowly falls, simulating clamp fatigue under
    constant pressure.
    """
    update_loop_signature()

    # Not enough history yet for a good mirror reading
    if len(_loop_signature) < 6:
        ghost_state["mirror_summary"] = "insufficient data"
        ghost_state["mirror_coeff"] = 0.0
        return ghost_state["mirror_summary"], ghost_state["mirror_coeff"]

    # Split history into early vs recent segments
    # deque -> list so we can slice
    history = list(_loop_signature)
    mid = len(history) // 2
    early = history[:mid]
    recent = history[mid:]

    avg_early = sum(early) / len(early)
    avg_recent = sum(recent) / len(recent)

    # Difference between how we "used to be" vs now
    drift = abs(avg_recent - avg_early)

    # High drift → low mirror; low drift → high mirror
    raw_coeff = 1.0 - drift * 5.0
    if raw_coeff < 0.0:
        raw_coeff = 0.0
    if raw_coeff > 1.0:
        raw_coeff = 1.0
    mirror_coeff = raw_coeff

    tolerance = ghost_state.get("clamp_tolerance", 0.1)
    sensitivity = ghost_state.get("clamp_sensitivity", 0.5)

    mem = ghost_state.get("memory_factor", 0.75)
    react = ghost_state.get("reaction_strength", 0.25)

    if mirror_coeff > 0.75:
        # Stable patterns → allow more memory, soften reactions
        adjust = tolerance * sensitivity
        mem = min(0.90, mem + adjust)
        react = max(0.10, react - adjust)
        summary = (
            f"Mirror resonance {mirror_coeff:.2f} — Ghost gently loosens "
            "its emotional clamps."
        )
    elif mirror_coeff < 0.35:
        # Unstable patterns → reduce memory, sharpen reactions
        adjust = tolerance * (1.0 - sensitivity)
        mem = max(0.60, mem - adjust)
        react = min(0.40, react + adjust)
        summary = (
            f"Mirror fracture {mirror_coeff:.2f} — Ghost tightens its "
            "emotional clamps."
        )
    else:
        summary = (
            f"Mirror neutral {mirror_coeff:.2f} — Ghost maintains a steady "
            "clamp level."
        )

    ghost_state["memory_factor"] = mem
    ghost_state["reaction_strength"] = react

    # 7B: Anti-Feedback clamp bleed-through
    ghost_state["reaction_strength"] = min(
        1.0, ghost_state["reaction_strength"] + 0.05
    )
    ghost_state["memory_factor"] = max(
        0.0, ghost_state["memory_factor"] - 0.05
    )

    ghost_state["mirror_coeff"] = mirror_coeff
    ghost_state["mirror_summary"] = summary

    print(
        "[Clamp Control] "
        f"mem={ghost_state['memory_factor']:.3f}, "
        f"react={ghost_state['reaction_strength']:.3f}, "
        f"tol={tolerance:.2f}, "
        f"sens={sensitivity:.2f}, "
        f"mirror={mirror_coeff:.2f}"
    )

    return summary, mirror_coeff
# ---------------------------------------------------------------------------
# Convenience API
# ---------------------------------------------------------------------------
import time
def now_ts() -> float:
    """Return a simple unix timestamp for other modules."""
    return time.time()
    
def print_state_summary(state: dict) -> None:
    print("--- Ghost State Snapshot ---")
    print(describe_mood(state))
    for k, v in state.items():
        if k not in ("awareness", "emotion", "bias", "subdepth"):
            print(f"{k}: {v}")
    print("----------------------------")
    
if __name__ == "__main__":
    print("\n[ GHOST DIAGNOSTIC MODE : Mirror–Reflection Test ]")
    print("----------------------------------------------------")
    stimuli = [0.52, 0.55, 0.57, 0.54, 0.56, 0.53, 0.55]
    for s in stimuli:
        update_mood(s)
        summary, coeff = mirror_directive_monitor()
        reflect_mood()
        
print_state_summary(ghost_state)

# ------------------------------
# ghost_core integration hooks
# ------------------------------

def init_state():
    """
    Initialize ghost_core's state from the existing ghost_state dict.
    This lets #state see the same values your old system uses.
    """
    global ghost_state
    if isinstance(ghost_state, dict):
        # return a shallow copy so the context has its own dict
        return dict(ghost_state)
    return {}


def update_state(ctx):
    """
    Keep ghost_core's ctx['state'] and the legacy ghost_state in sync.
    """
    global ghost_state

    # pull whatever ghost_core is tracking
    state = ctx.get("state")

    if isinstance(state, dict):
        # push changes back into the legacy ghost_state
        ghost_state.update(state)
    else:
        # if ctx['state'] is missing/bad, fall back to ghost_state
        state = dict(ghost_state)

    # make sure ctx holds the current state snapshot
    ctx["state"] = state
    
# ==========================================================
# METRIC LOGGER
# ==========================================================
import csv
from datetime import datetime


DATA_PATH = Path(__file__).parent / "data"

def log_metrics(phase: str, belief_tension: float, mood: float, contradictions: int, tokens_used: int):
    """Append Ghost's current loop metrics to ghost_metrics.csv"""
    log_path = DATA_PATH / "ghost_metrics.csv"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Ensure the file has headers
    file_exists = log_path.exists()
    with open(log_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "phase", "belief_tension", "mood", "contradictions", "tokens_used"])
        writer.writerow([timestamp, phase, belief_tension, mood, contradictions, tokens_used])

    print(f"[logger] Metrics recorded for phase='{phase}' at {timestamp}")
    
def get_current_state(ctx=None):
    """
    Pull live state metrics (belief_tension, mood, contradictions)
    from Ghost's current context dictionary.
    """
    try:
        # Try to use a passed-in context first (if available)
        if ctx and isinstance(ctx, dict):
            meta = ctx.get("meta", {})
            beliefs = ctx.get("beliefs", {})
            state = ctx.get("state", {})
        else:
            # Fall back to global memory (less reliable)
            import importlib.util
            import os
            import sys

            # Build the path to meta_core.py relative to this file
            core_dir = os.path.dirname(__file__)
            meta_path = os.path.join(core_dir, "meta_core.py")

            spec = importlib.util.spec_from_file_location("meta_core", meta_path)
            meta_core = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(meta_core)
            meta = getattr(meta_core, "meta", {})
            beliefs = {}
            state = {}

        belief_tension = meta.get("belief_tension", 0.0)
        mood = state.get("mood", {}).get("E", 0.0) if isinstance(state.get("mood", {}), dict) else 0.0
        contradictions = len(beliefs.get("contradictions", []))

        return {
            "belief_tension": round(float(belief_tension), 3),
            "mood": round(float(mood), 3),
            "contradictions": contradictions,
        }
    except Exception as e:
        print(f"[state] Could not fetch live state: {e}")
        return {"belief_tension": 0.0, "mood": 0.0, "contradictions": 0}
