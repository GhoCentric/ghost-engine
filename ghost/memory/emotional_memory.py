"""
emotional_memory.py
Linear emotional memory engine (Option A)

Tracks:
    - last_mood
    - mood_delta
    - emotional_spike (boolean)
    - rolling_avg (simple smoothing)

No drift, no band analysis, no stability metrics.
This is the cleanest possible emotional signal layer.
"""

DEFAULT_EMOTION = 0.50      # baseline neutral
SMOOTHING = 0.10            # how quickly rolling_avg adapts
SPIKE_THRESHOLD = 0.12      # mood jump needed to count as spike


def run_emotional_memory(ctx: dict) -> None:
    """
    Updates ctx with emotional memory fields:

        ctx["emotion_last"]
        ctx["emotion_delta"]
        ctx["emotion_spike"]
        ctx["emotion_avg"]

    Input:
        ctx["mood"] : float 0.0–1.0 (current mood)

    Writes:
        new emotional memory values back into ctx
    """

    mood = ctx.get("mood", DEFAULT_EMOTION)

    # ----------------------------------------------------
    # Retrieve prior values (or defaults)
    # ----------------------------------------------------
    prev = ctx.get("emotion_last", DEFAULT_EMOTION)
    avg = ctx.get("emotion_avg", DEFAULT_EMOTION)

    # ----------------------------------------------------
    # Compute delta and spike
    # ----------------------------------------------------
    delta = mood - prev
    spike = abs(delta) >= SPIKE_THRESHOLD

    # ----------------------------------------------------
    # Update rolling average (simple smoothing)
    # ----------------------------------------------------
    new_avg = avg + SMOOTHING * (mood - avg)

    # ----------------------------------------------------
    # Save back into ctx
    # ----------------------------------------------------
    ctx["emotion_last"] = round(mood, 4)
    ctx["emotion_delta"] = round(delta, 4)
    ctx["emotion_spike"] = spike
    ctx["emotion_avg"] = round(new_avg, 4)
