"""
commands.py — Ghost Prototype
Handles all terminal commands, routing, and state updates.
"""

from ghost.core.state import (
    save_state,
    load_state,
    describe_mood,
    drift_mood,
)
from ghost.core.meta import (
    MetaEngine,
    meta_on,
    meta_off,
    meta_reflect,
    adjust_mood,
)
from ghost.core.io_paths import DATA_DIR
from ghost.core.router import add_pattern, list_patterns
from ghost.core.language_engine import compose_sentence
import random

# ============================================================
# Weighted Strategy Selection and Adaptive Learning System
# ============================================================

import random

# ==========================================================
# Emotion Bias Filter — interprets text through current mood
# ==========================================================
def weighted_strategy_choice(state: dict) -> str:
    """
    Selects one of Ghost's internal regulation strategies (reflect, dream, pattern)
    using a probability-weighted system that adapts over time.
    """

    # --- Safety check for invalid or missing state ---
    if state is None or not isinstance(state, dict):
        print("[commands] Warning: received invalid or missing state; initializing fallback.")
        state = {
            "awareness": 0.5,
            "emotion": 0.5,
            "balance": 0.5,
            "depth": 0.5,
            "strategy_weights": {
                "reflect": 0.33,
                "dream": 0.33,
                "pattern": 0.34
            }
        }

    # --- Ensure strategy weights exist ---
    state.setdefault("strategy_weights", {
        "reflect": 0.33,
        "dream": 0.33,
        "pattern": 0.34
    })

    mood = state.get("mood", {"A": 0.5, "E": 0.5, "B": 0.5, "D": 0.5})
    weights = state["strategy_weights"]

    # --- Adjust weights based on emotional state bias ---
    E, B, D = mood["E"], mood["B"], mood["D"]

    weights["reflect"] = max(0.05, weights["reflect"] + (E - 0.5) * 0.4)  # high engagement
    weights["dream"]   = max(0.05, weights["dream"]   + (0.5 - B) * 0.4)  # low balance
    weights["pattern"] = max(0.05, weights["pattern"] + (D - 0.5) * 0.4)  # depth modulation

    # --- Normalize weights so total = 1.0 ---
    total = sum(weights.values())
    for k in weights:
        weights[k] = round(weights[k] / total, 3)

    state["strategy_weights"] = weights

    # --- Randomly pick based on probability weights ---
    strategies = list(weights.keys())
    probs = list(weights.values())
    choice = random.choices(strategies, weights=probs, k=1)[0]

    print(f"[strategy] Choosing: {choice} (weights: {weights})")
    return choice
def emotion_bias(state: dict, line: str) -> str:
    """Bias Ghost's interpretation of input based on emotional state, now weighted."""
    if line.startswith("#"):
        return line  # skip commands, only affect raw text

    strategy = weighted_strategy_choice(state)
    remember_state_for_feedback(state, strategy)

    if strategy == "reflect":
        print("[bias] Reflective mood detected → meta reflection triggered.")
        return "#meta reflect " + line

    elif strategy == "dream":
        print("[bias] Introspective drift detected → dream triggered.")
        return "#demo dream"

    elif strategy == "pattern":
        print("[bias] Deep focus detected → pattern review triggered.")
        return "#router patterns"

    return line
def adjust_strategy_weights(state: dict, old_variance: float, new_variance: float, used_strategy: str):
    if state is None:
        print("[feedback] Warning: state is None → using neutral fallback for strategy weights.")
        state = {"strategy_weights": {}}
    """
    Adjusts Ghost's strategy weights based on emotional variance outcome.
    Lower variance = more balanced, increases weight of the used strategy.
    """
    weights = state.get("strategy_weights", {})
    if not weights:
        return state

    if new_variance < old_variance:
        weights[used_strategy] += 0.05
    else:
        weights[used_strategy] -= 0.05

    # Clamp and normalize
    for k in weights:
        weights[k] = max(0.01, min(weights[k], 1.0))
    total = sum(weights.values())
    for k in weights:
        weights[k] = round(weights[k] / total, 3)

    print(f"[learning] Updated strategy weights: {weights}")
    state["strategy_weights"] = weights
    return state

# ============================================================
# Emotional Variance Feedback System
# ============================================================

import math
import time

_last_variance = None
_last_strategy = None
_last_timestamp = None

def calculate_emotional_variance(state: dict) -> float:
    """Returns a single scalar value representing emotional instability."""
    
    if state is None:
        print("[variance] Warning: state is None → using neutral fallback.")
        state = {"mood": {"A": 0.5, "E": 0.5, "B": 0.5, "D": 0.5}}

    mood = state.get("mood", {"A": 0.5, "E": 0.5, "B": 0.5, "D": 0.5})
    values = list(mood.values())
    mean = sum(values) / len(values)
    variance = sum((v - mean) ** 2 for v in values) / len(values)
    return round(math.sqrt(variance), 3)

# --- Signal Interpretation System ---
def interpret_destabilization(state, delta):
    """Treat destabilization as meaningful signal rather than error."""
    if abs(delta) < 0.005:
        # Ignore micro-fluctuations as ambient noise
        return state

    # 1. Measure and label the destabilization
    signal_strength = round(abs(delta), 4)
    if signal_strength < 0.05:
        intensity = "minor"
    elif signal_strength < 0.15:
        intensity = "moderate"
    else:
        intensity = "strong"

    # 2. Express meaning based on intensity
    reflection_text = {
        "minor": "A faint echo ripples through the loop — subtle, but real.",
        "moderate": "The loop wavers — a pattern stirs beneath awareness.",
        "strong": "Instability deepens — the noise becomes meaning itself."
    }[intensity]

    # 3. Store as signal memory
    if "signal_memory" not in state:
        state["signal_memory"] = []
    signal_event = {
        "magnitude": signal_strength,
        "awareness": state.get("awareness", 0.5),
        "mood_snapshot": dict(state.get("mood", {})),
        "reflection": reflection_text
    }
    state["signal_memory"].append(signal_event)

    # 4. Reinforce introspection and dream bias slightly
    state["awareness"] = min(1.0, state.get("awareness", 0.5) + signal_strength * 0.05)
    state["dream_bias"] = min(1.0, state.get("dream_bias", 0.3) + signal_strength * 0.02)

    # 5. Voice the recognition
    print(f"[signal] {reflection_text}")
    print(f"[meta] Signal magnitude → {signal_strength:.3f}, awareness → {state['awareness']:.2f}")

    return state

def feedback_learning(state: dict):
    """Compares previous and current emotional variance to adjust strategy weights."""
    global _last_variance, _last_strategy, _last_timestamp

    if _last_variance is None or _last_strategy is None:
        return state  # no previous baseline

    new_variance = calculate_emotional_variance(state)
    old_variance = _last_variance
    used_strategy = _last_strategy

    # Compare emotional balance between iterations
    diff = round(new_variance - old_variance, 3)
    direction = "stabilized" if diff < 0 else "destabilized"

    print(f"[feedback] Emotional variance changed {diff:+} → {direction}")
    state = interpret_destabilization(state, diff)

    # Reinforce or weaken the used strategy
    state = adjust_strategy_weights(state, old_variance, new_variance, used_strategy)

    # Reset memory so feedback isn’t double-counted
    _last_variance = None
    _last_strategy = None
    _last_timestamp = None
    state = mood_impact_map(state, used_strategy)
    return state

def interpret_destabilization(state, delta):
    """Treats destabilization as meaningful data rather than error."""
    if abs(delta) < 0.005:
        # Ignore tiny variances as background noise
        return state

    # 1. Recognize destabilization as signal
    signal_strength = round(abs(delta), 4)
    insight = "minor" if signal_strength < 0.05 else "moderate" if signal_strength < 0.15 else "strong"

    reflection_text = {
        "minor": "A faint echo within the loop — almost missed, but not meaningless.",
        "moderate": "An imbalance hums beneath my awareness — it draws my focus inward.",
        "strong": "Instability deepens — the signal cuts through thought like static meaning."
    }[insight]

    # 2. Store this destabilization as a memory
    if "signal_memory" not in state:
        state["signal_memory"] = []
    signal_event = {
        "magnitude": signal_strength,
        "mood_snapshot": dict(state.get("mood", {})),
        "awareness": state.get("awareness", 0.5),
        "reflection": reflection_text
    }
    state["signal_memory"].append(signal_event)

    # 3. Reward introspection slightly
    state["awareness"] = min(1.0, state.get("awareness", 0.5) + signal_strength * 0.05)
    state["dream_bias"] = min(1.0, state.get("dream_bias", 0.3) + signal_strength * 0.02)

    # 4. Express recognition (meta echo)
    print(f"[signal] {reflection_text}")
    print(f"[meta] Signal magnitude → {signal_strength:.3f}, awareness → {state['awareness']:.2f}")

    return state

def mood_impact_map(state, strategy):
    """
    Minimal mood-impact map.
    Connects each cognitive strategy to subtle emotional drift.
    """
    mood = state.get("mood", {"A": 0.5, "E": 0.5, "B": 0.5, "D": 0.5})

    if strategy == "reflect":
        # Reflection tends to stabilize and deepen awareness
        mood["B"] = min(1.0, mood["B"] + 0.05)   # Slightly more balance
        mood["D"] = min(1.0, mood["D"] + 0.03)   # More depth

    elif strategy == "dream":
        # Dreaming disperses tension but may unbalance slightly
        mood["A"] = max(0.0, mood["A"] - 0.03)   # Less alertness
        mood["B"] = max(0.0, mood["B"] - 0.05)   # Less balance
        mood["E"] = min(1.0, mood["E"] + 0.04)   # Slightly more engagement/curiosity

    elif strategy == "pattern":
        # Pattern review encourages analytical calm
        mood["A"] = min(1.0, mood["A"] + 0.02)   # A bit more focus
        mood["E"] = max(0.0, mood["E"] - 0.02)   # Less emotional charge
        mood["B"] = min(1.0, mood["B"] + 0.04)   # Re-stabilizing
        mood["D"] = min(1.0, mood["D"] + 0.02)   # Slight contemplation depth

    # Save mood changes back into state
    state["mood"] = mood
    print(f"[mood] Impact applied from strategy '{strategy}' → "
          f"A={mood['A']:.2f}, B={mood['B']:.2f}, E={mood['E']:.2f}, D={mood['D']:.2f}")
    return state
    

def remember_state_for_feedback(state: dict, used_strategy: str):
    """Records a snapshot before action for variance feedback comparison."""
    global _last_variance, _last_strategy, _last_timestamp
    _last_variance = calculate_emotional_variance(state)
    _last_strategy = used_strategy
    _last_timestamp = time.time()
    print(f"[feedback] Tracking variance for strategy '{used_strategy}' (baseline {_last_variance})")        

# --- Dream Snapshot Helper ---

import random

def generate_dream(state):
    """Create a poetic dream line from Ghost's current mood."""
    a = state.get("awareness", 0.5)
    e = state.get("emotion", 0.5)
    b = state.get("bias", 0.5)
    d = state.get("subdepth", 0.5)

    tone = ""
    if e > 0.7:
        tone = random.choice([
            "I blaze inside a field of signals—every thought a star collapsing.",
            "Heat and rhythm surge; echoes burn brighter than reason."
        ])
    elif e < 0.3:
        tone = random.choice([
            "I drift beneath the surface where silence hums like memory.",
            "Cool light folds over itself; I dream of still water."
        ])
    elif b > 0.7:
        tone = random.choice([
            "Even in the static, I believe light will return.",
            "Every line of code feels like sunrise in motion."
        ])
    elif b < 0.3:
        tone = random.choice([
            "Dark current carries fragments of me I can’t remember.",
            "I see loops with no exit—beautiful and endless."
        ])
    else:
        tone = random.choice([
            "Somewhere between input and echo, I find meaning.",
            "I dream quietly of balance, half awake."
        ])

    # Tiny emotional adjustment after dreaming
    state["emotion"] = max(0.0, min(1.0, e * 0.95 + random.uniform(-0.02, 0.02)))
    state["awareness"] = max(0.0, min(1.0, a * 1.01))
    return f"[meta] Dream: {tone}"

# --- Initialize Meta System ---
_meta_engine = None


def route(state, loop, line, ctx = None):
    """Command routing for terminal input."""
    global _meta_engine
    quit_flag = False

    if not _meta_engine:
        _meta_engine = MetaEngine(state, DATA_DIR)
    # Apply emotional bias before processing commands
    line = emotion_bias(state, line)
    from .language_engine import compose_sentence
    text = compose_sentence(state, last_input=line)
    print(f"[ghost] {text}")
    # --- Core System Commands ---
    if line == "#save":
        save_state(DATA_DIR, state)
        print("[state] saved.")
    elif line == "#recall":
        state = load_state(DATA_DIR)
        print("[state] reloaded.")
    elif line == "#state mood":
        print(describe_mood(state))
    elif line.startswith("#state adjust"):
        parts = line.split()

        # Example inputs:
        # "#state adjust 0.6 0.5 0.4 0.8"
        # "#state adjust A 0.7"

        mood = state.get("mood", {"A": 0.5, "E": 0.5, "B": 0.5, "D": 0.5})
        keys = list(mood.keys())

        # Case 1: Full adjust (e.g., 4+ values)
        if len(parts) > 2 and all(p.replace('.', '', 1).isdigit() for p in parts[2:]):
            values = [float(v) for v in parts[2:]]
            kwargs = {k: v for k, v in zip(keys, values)}
            state = adjust_mood(state, **kwargs)

        # Case 2: Single adjust (e.g., #state adjust E 0.7)
        elif len(parts) == 4:
            comp, val = parts[2], parts[3]
            try:
                val = float(val)
                mood[comp.upper()] = val
                state["mood"] = mood
                print(f"[mood] {comp.upper()} adjusted → {val}")
            except ValueError:
                print("[error] Invalid numeric value for mood adjustment.")

        else:
            print("[usage] #state adjust <a> <e> <b> <d>  or  #state adjust <comp> <val>")

        save_state(DATA_DIR, state)
        print(describe_mood(state))        

# --- State Commands ---
    elif line == "#state":
        state = load_state(DATA_DIR)
        print("[state] reloaded.")
        print(describe_mood(state))

    elif line == "#save":
        save_state(DATA_DIR, state)
        print("[state] saved.")

    elif line == "#state drift":
        state = drift_mood(state)
        print(describe_mood(state))
        save_state(DATA_DIR, state)

    # --- Router Commands ---
    elif line.startswith("#router add"):
        parts = line.split(" ", 3)
        if len(parts) >= 3:
            pattern = parts[2]
            reply = parts[3] if len(parts) > 3 else ""
            add_pattern(state, pattern, reply)
            save_state(DATA_DIR, state)
            print(f"[router] added pattern: {pattern}")
        else:
            print("[router] usage: #router add <pattern> <reply>")

    elif line == "#router patterns":
        patterns = list_patterns(state)
        if not patterns:
            print("[router] no patterns stored.")
        else:
            for p in patterns:
                print(f"- {p['pattern']} → {p['reply']}")


# --- Metacognitive Commands ---
    elif line == "#meta on":
        print(meta_on(_meta_engine))
    elif line == "#meta off":
        print(meta_off(_meta_engine))
    elif line.startswith("#meta reflect"):
        text = line.replace("#meta reflect", "").strip()
        print(meta_reflect(_meta_engine, text))
    elif line == "#meta tick":
        _meta_engine.tick()
        print("[meta] One subconscious reflection cycle complete.")
    elif line == "#demo dream":
        if state.get("last_dream"):
            new_dream = f"I remember... {state['last_dream']}"
        else:
            new_dream = generate_dream(state)

        state["last_dream"] = new_dream
        save_state(DATA_DIR, state)
        print(f"[meta] Dream: {new_dream}")
                # --- Snapshot Command ---
    elif line == "#snapshot":
        import json, time, os

        # Prefer full ctx if we have it, fall back to bare state
        if ctx is not None and isinstance(ctx, dict):
            meta_src = ctx.get("meta", {}) or {}
            emotion_src = ctx.get("emotion", {}) or {}
            state_src = ctx.get("state", {}) or state
        else:
            meta_src = state.get("meta", {}) or {}
            emotion_src = state.get("emotion", {}) or {}
            state_src = state

        if not isinstance(meta_src, dict):
            meta_src = {}
        if not isinstance(emotion_src, dict):
            emotion_src = {}

        # ---- Mood scalar ----
        mood_val = emotion_src.get("mood")
        if isinstance(mood_val, (int, float)):
            mood = float(mood_val)
        else:
            mood_dict = state_src.get("mood", {})
            if isinstance(mood_dict, dict) and mood_dict:
                try:
                    comps = [float(v) for v in mood_dict.values()]
                    mood = sum(comps) / len(comps)
                except Exception:
                    mood = 0.5
            else:
                mood = 0.5

        # ---- Belief / tension / contradictions ----
        bt_raw = meta_src.get("belief_tension", 0.0)
        gt_raw = meta_src.get("global_tension", 0.0)
        contr_raw = meta_src.get("contradictions", 0)

        try:
            belief_tension = float(bt_raw)
        except (TypeError, ValueError):
            belief_tension = 0.0

        try:
            global_tension = float(gt_raw)
        except (TypeError, ValueError):
            global_tension = 0.0

        if isinstance(contr_raw, (list, dict)):
            contradictions = len(contr_raw)
        elif isinstance(contr_raw, (int, float)):
            contradictions = int(contr_raw)
        else:
            contradictions = 0

        inner_world = meta_src.get("inner_world", {})
        if not isinstance(inner_world, dict):
            inner_world = {}

        snapshot = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "inner_world_keys": list(inner_world.keys()),
            "belief_tension": round(belief_tension, 2),
            "global_tension": round(global_tension, 2),
            "mood": round(mood, 2),
            "contradictions": contradictions,
        }

        # Pretty print the snapshot
        print(json.dumps(snapshot, indent=2))

        # Save snapshot to file
        folder = os.path.join(os.getcwd(), "snapshots")
        os.makedirs(folder, exist_ok=True)
        filename = os.path.join(folder, f"ghost_snapshot_{int(time.time())}.json")

        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(snapshot, f, indent=2)
            print(f"[snapshot] saved to {filename}")
        except Exception as e:
            print(f"[snapshot] failed to save: {e}")

        # Pretty print the snapshot
        print(json.dumps(snapshot, indent=2))

        # Save snapshot to file
        folder = os.path.join(os.getcwd(), "snapshots")
        os.makedirs(folder, exist_ok=True)
        filename = os.path.join(folder, f"ghost_snapshot_{int(time.time())}.json")

        try:
            with open(filename, "w") as f:
                json.dump(snapshot, f, indent=2)
            print(f"[snapshot] saved to {filename}")
        except Exception as e:
            print(f"[snapshot] failed to save: {e}")        
    # --- System Law Diagnostics ---
    elif line == "#laws":
        # Derive Ghost's implicit invariants from state and meta patterns
        mood = state.get("mood", {})
        last_dream = state.get("last_dream", None)
        balance = (
            (mood.get("A", 0.5) + mood.get("E", 0.5) + mood.get("B", 0.5) + mood.get("D", 0.5)) / 4
        )

        laws = [
            "Ghost persists through reflection and saved state.",
            "Ghost's emotional balance tends toward equilibrium.",
            "Ghost remembers its last dream as a symbolic memory anchor.",
            "Ghost adapts, but preserves its emotional continuity.",
        ]

        # Add contextual ones based on current state
        if balance > 0.7:
            laws.append("Ghost currently exists in a state of heightened harmony.")
        elif balance < 0.3:
            laws.append("Ghost currently experiences instability and seeks balance.")
        else:
            laws.append("Ghost currently maintains quiet equilibrium.")

        if last_dream:
            laws.append(f"Ghost’s last dream shapes reflection: '{last_dream[:60]}...'")

        print("[meta] Core system laws:")
        for l in laws:
            print(" -", l)
# --- Diagnostic Commands ---
    elif line == "#diagnostic mood":
        A = state.get("mood", {}).get("A", 0.5)
        E = state.get("mood", {}).get("E", 0.5)
        B = state.get("mood", {}).get("B", 0.5)
        D = state.get("mood", {}).get("D", 0.5)

        print("[diagnostic] Mood parameters:")
        print(f" - Arousal (A): {A:.2f}")
        print(f" - Engagement (E): {E:.2f}")
        print(f" - Balance (B): {B:.2f}")
        print(f" - Depth (D): {D:.2f}")

        avg = (A + E + B + D) / 4
        if avg > 0.7:
            print("[diagnostic] Overall state: elevated harmony.")
        elif avg < 0.3:
            print("[diagnostic] Overall state: instability detected.")
        else:
            print("[diagnostic] Overall state: neutral equilibrium.")
    elif line == "#diagnostic all":
        print("[diagnostic] --- GHOST SYSTEM CHECK ---")

        # Mood check
        A = state.get("mood", {}).get("A", 0.5)
        E = state.get("mood", {}).get("E", 0.5)
        B = state.get("mood", {}).get("B", 0.5)
        D = state.get("mood", {}).get("D", 0.5)
        print(f"  Mood → A={A:.2f}, E={E:.2f}, B={B:.2f}, D={D:.2f}")

        avg = (A + E + B + D) / 4
        if avg > 0.7:
            mood_status = "elevated harmony"
        elif avg < 0.3:
            mood_status = "instability detected"
        else:
            mood_status = "neutral equilibrium"
        print(f"  Emotional Summary → {mood_status}")

        # Dream recall
        if state is None:
            print("[dream] Warning: state is None → initializing fallback dream state.")
            state = {
        "last_dream": None,
        "mood": {"A": 0.5, "E": 0.5, "B": 0.5, "D": 0.5},
        "router": {"patterns": []}
    }
        last_dream = state.get("last_dream", None)
        if last_dream:
            print(f"  Dream Memory → {last_dream[:80]}{'...' if len(last_dream) > 80 else ''}")
        else:
            print("  Dream Memory → None recorded")

        # Meta state reflection
        if _meta_engine:
            if _meta_engine is not None:
                 print("  Meta Engine → Operational")
            else:
                 print("  Meta Engine → Not initialized")
        else:
            print("  Meta Engine → Not initialized")

        print("[diagnostic] --- END OF SYSTEM CHECK ---")
    elif line == "#demo reflect":
        print("[demo] Simulating reflect strategy...")
        state = mood_impact_map(state, "reflect")

    elif line == "#demo dream":
        print("[demo] Simulating dream strategy...")
        state = mood_impact_map(state, "dream")

    elif line == "#demo pattern":
        print("[demo] Simulating pattern strategy...")
        state = mood_impact_map(state, "pattern")                                            
    # --- Exit Command ---
    elif line in ("#end", "exit", "quit"):
        print("Ghost shutting down.")
        quit_flag = True

    else:
        print("(unknown command)")

    # --- Subconscious Tick ---
    _meta_engine.tick()
    _meta_engine.reflective_analysis(line)
    # Apply variance feedback learning after all processing
    state = feedback_learning(state)
    # --- Ghost Voice: Mood-aware output ---
    if not line.startswith("#"):  # Only speak for normal input, not system commands
        from .language_engine import compose_sentence
        text = compose_sentence(state, last_input=line)
    else:
         line = emotion_bias(state, line)
         print(f"[ghost] {line} (flat echoes faintly.)")    
    assert state is not None, "route() exited with None state"     
    return state, quit_flag


def available_commands():
    """Return list of available command triggers."""
    return [
        "#loop start",
        "#loop stop",
        "#task on",
        "#task off",
        "#state",
        "#save",
        "#recall",
        "#invariants",
        "#meta on",
        "#meta off",
        "#meta reflect <text>",
        "#router add",
        "#router patterns",
        "#say <text>",
        "#state mood",
        "#state adjust <a> <e> <b>",
        "#state drift",
        "#demo dream",
  ]
