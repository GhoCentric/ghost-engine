# /ghost/core/emotion_vectors.py

import math

# Define emotional dimensions
EMOTION_AXES = ["joy", "sadness", "fear", "anger", "disgust"]

def init_emotion_vector():
    """Initialize Ghost’s emotional state to neutral."""
    return {axis: 0.0 for axis in EMOTION_AXES}

def normalize(vector):
    """Keep overall emotion balance scaled to 1.0 total energy."""
    # Calculate Euclidean norm manually
    total = math.sqrt(sum(v ** 2 for v in vector.values()))
    if total == 0:
        return vector
    return {k: round(v / total, 3) for k, v in vector.items()}

def update_emotions(vector, text, weight=0.1):
    """
    Adjust emotions based on keywords in input text.
    Also naturally decays emotions that aren't triggered.
    """
    triggers = {
        "joy": ["happy", "love", "laugh", "success", "peace", "wonderful"],
        "sadness": ["loss", "alone", "fail", "grief", "cry", "hurt"],
        "fear": ["danger", "risk", "pain", "unknown", "dark", "worry"],
        "anger": ["hate", "rage", "unfair", "destroy", "betray", "mad"],
        "disgust": ["gross", "filth", "repulsive", "dirty", "sick", "rotten"]
    }

    text_lower = text.lower()
    for emotion, words in triggers.items():
        # Increase emotion if keywords are detected
        if any(w in text_lower for w in words):
            vector[emotion] = min(1.0, vector[emotion] + weight)
        else:
            # Small natural decay toward 0
            vector[emotion] = max(0.0, vector[emotion] - (weight / 8))

    return normalize(vector)

def derive_mood(vector):
    """
    Compute Ghost’s overall mood as an average of the emotion vector.
    +joy raises mood; negative emotions lower it.
    """
    joy = vector["joy"]
    neg = (vector["sadness"] + vector["fear"] + vector["anger"] + vector["disgust"]) / 4
    mood = joy - neg
    return round(mood, 3)

def emotion_summary(vector):
    """Readable summary of Ghost’s current emotion composition."""
    dominant = max(vector, key=vector.get)
    mood = derive_mood(vector)
    summary = f"Dominant: {dominant} ({vector[dominant]:.2f}) | Mood: {mood:+.2f}"
    return summary
    
# =====================================================
# LEARNING / GRADIENT-LIKE ADAPTATION
# =====================================================

def init_emotion_memory():
    """Keep running averages of emotions that led to good outcomes."""
    return {axis: 0.5 for axis in EMOTION_AXES}

def update_emotion_memory(memory, vector, reward, lr=0.05):
    """
    Simple gradient-like step:
    reward > 0 pushes memory toward current vector,
    reward < 0 pulls it away.
    """
    for k in EMOTION_AXES:
        diff = vector[k] - memory[k]
        memory[k] += lr * reward * diff
        # Clamp to [0,1]
        memory[k] = max(0.0, min(1.0, memory[k]))
    return memory

def apply_emotion_bias(vector, memory, strength=0.1):
    """
    Nudge current emotions toward learned memory state.
    """
    for k in EMOTION_AXES:
        vector[k] += strength * (memory[k] - vector[k])
    return normalize(vector)
