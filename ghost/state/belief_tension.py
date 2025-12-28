# belief_tension.py
# --------------------------------------------------------
# Step 4B — Micro Belief-Tension Engine
# --------------------------------------------------------
import re

TENSION_DEFAULT = 0.0
TENSION_MAX = 1.0
TENSION_MIN = 0.0

# How fast tension rises when triggered
TENSION_SPIKE = 0.18

# How fast tension cools back toward zero
TENSION_DECAY = 0.04


# Simple contradiction keyword sets
CONFLICT_PATTERNS = [
    ("yes", "no"),
    ("want", "don't"),
    ("want", "not want"),
    ("must", "can't"),
    ("good", "bad"),
]


CONTRA_BRIDGES = {"but", "however", "though", "yet", "although", "still"}
POS_MARKERS    = {"yes", "want", "like", "love", "hope", "good", "okay", "ok", "sure"}
NEG_MARKERS    = {"no", "not", "never", "can't", "cannot", "wont", "won't", "hate", "bad", "afraid", "doubt"}


def detect_contradiction(text: str) -> bool:
    """
    Very simple contradiction detector.

    Flags things like:
      - "yes but also no"
      - "I want to stop but I can't"
      - mixed positive/negative sentiment bridged by 'but/however/though/…'
    """
    if not text:
        return False

    lower = text.lower()
    tokens = re.findall(r"[a-z']+", lower)

    has_bridge = any(t in CONTRA_BRIDGES for t in tokens)
    has_pos    = any(t in POS_MARKERS    for t in tokens)
    has_neg    = any(t in NEG_MARKERS    for t in tokens)

    # Core pattern: positive + negative joined by contrast word
    if has_bridge and has_pos and has_neg:
        return True

    # Explicit hardcoded patterns that *must* hit
    if "yes but" in lower and "no" in lower:
        return True
    if "but also no" in lower:
        return True
    if "i want" in lower and ("can't" in lower or "cannot" in lower):
        return True

    return False


def run_belief_tension_pass(ctx: dict) -> None:
    """
    Updates:
      - ctx['belief_tension']  : float in [TENSION_MIN, TENSION_MAX]
      - ctx['contradictions']  : running count of detected contradictions
    based on the current input text.
    """

    # 1. Grab input and previous values
    text = ctx.get("input", "") or ""

    prev_tension = ctx.get("belief_tension", TENSION_DEFAULT)
    prev_contras = ctx.get("contradictions", 0)

    # 2. Ask the detector if this line is contradictory
    contradiction = detect_contradiction(text)

    # 3. Update tension + contradiction count
    if contradiction:
        # spike up when we see a contradiction
        new_tension = min(TENSION_MAX, prev_tension + TENSION_SPIKE)
        new_contras = prev_contras + 1
    else:
        # decay toward zero if no contradiction
        if prev_tension > 0:
            new_tension = max(TENSION_MIN, prev_tension - TENSION_DECAY)
        else:
            new_tension = prev_tension
        new_contras = prev_contras

    # 4. Write back into ctx
    ctx["belief_tension"] = round(new_tension, 3)
    ctx["contradictions"] = int(new_contras)

    # 5. Optional debug
    # print(f"[belief] text={text!r} contradiction={contradiction} "
    #       f"tension={ctx['belief_tension']} contradictions={ctx['contradictions']}")
