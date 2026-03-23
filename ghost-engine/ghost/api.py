"""
Public API layer for ghocentric-ghost-engine

This wraps internal systems into a clean, stable interface
for external developers.
"""

from .engine import GhostEngine


# -----------------------------
# DEFAULT EVENT MAP
# -----------------------------
DEFAULT_EVENT_MAP = {
    "insult": {"trust": -0.3},
    "help": {"trust": +0.2},
    "betrayal": {"trust": -0.8, "attachment": -0.5},
}


class GhostAPI:

    # -----------------------------
    # RELATIONSHIP STATE THRESHOLDS
    # -----------------------------
    STATE_THRESHOLDS = {
        "hostile": -0.5,
        "unfriendly": -0.2,
        "neutral": 0.2,
        "friendly": 0.5,
        "loyal": 1.0,
    }

    def __init__(self, config: dict | None = None, event_map: dict | None = None):
        self.engine = GhostEngine(config or {})
        self._transitions = {}  # NEW
        self.event_map = event_map or DEFAULT_EVENT_MAP

    # -----------------------------
    # CORE METHOD (THIS IS YOUR PRODUCT)
    # -----------------------------
    def apply_event(self, source: str, target: str, event: dict):
        if not isinstance(event, dict):
            raise ValueError("Event must be a dict")

        event_type = event.get("type")
        intensity = event.get("intensity", 1.0)
        
        if not isinstance(intensity, (int, float)):
            raise ValueError("Event intensity must be numeric")

        if event_type not in self.event_map:
            raise ValueError(f"Unknown event type: {event_type}")

        base_deltas = self.event_map[event_type]

        scaled_deltas = {
            k: v * intensity for k, v in base_deltas.items()
        }

        self.engine.relationships.apply_delta(source, target, scaled_deltas)
        
    def tick(self):
        """
        Advance time for all relationships (applies decay).
        """
        self.engine.relationships.tick()
    
    def _clamp(self, value, min_v=-1.0, max_v=1.0):
        return max(min(value, max_v), min_v)

    def _get_state(self, trust: float) -> str:
        t = self.STATE_THRESHOLDS

        if trust <= t["hostile"]:
            return "hostile"
        elif trust <= t["unfriendly"]:
            return "unfriendly"
        elif trust <= t["neutral"]:
            return "neutral"
        elif trust <= t["friendly"]:
            return "friendly"
        else:
            return "loyal"

    def _detect_transition(self, a: str, b: str, new_state: str):
        key = f"{a}|{b}"

        prev = self._transitions.get(key)

        transition = None

        if prev is not None and prev != new_state:
            transition = (prev, new_state)

        # update memory
        self._transitions[key] = new_state

        return transition

    def _handle_transition(self, _a: str, _b: str, transition):
        if not transition:
            return None

        prev, new = transition

# -----------------------------
        # BASIC TRIGGERS (clean logic)
        # -----------------------------

        # entering hostile state
        if new == "hostile":
            return {
                "event": "relationship_broken",
                "from": prev,
                "to": new,
            }

        # ANY movement AWAY from hostile = recovery
        if prev == "hostile" and new != "hostile":
            return {
                "event": "deescalation",
                "from": prev,
                "to": new,
            }

        # strong positive shift (optional forgiveness moment)
        if new in ("friendly", "loyal") and prev in ("unfriendly", "neutral"):
            return {
                "event": "forgiveness",
                "from": prev,
                "to": new,
            }

        # default fallback
        return {
            "event": "state_shift",
            "from": prev,
            "to": new,
        }

    # -----------------------------
    # READ STATE
    # -----------------------------
    def get_relationship(self, a: str, b: str) -> dict:
        rel = self.engine.relationships.get(a, b)

        if rel is None:
            return {
                "trust": 0.0,
                "attachment": 0.0,
                "stability": 0.0,
                "state": "neutral",
                "transition": None,
                "trigger": None,
            }

        trust = rel.get("trust", 0.0)
        attachment = rel.get("attachment", 0.0)

        trust = self._clamp(trust)
        attachment = self._clamp(attachment)

        stability = abs(trust)
        state = self._get_state(trust)

        # NEW
        transition = self._detect_transition(a, b, state)
        trigger = self._handle_transition(a, b, transition)

        return {
            "trust": trust,
            "attachment": attachment,
            "stability": stability,
            "state": state,
            "transition": transition,
            "trigger": trigger,
        }

    # -----------------------------
    # OPTIONAL: BULK SNAPSHOT
    # -----------------------------
    def snapshot(self):
        return self.engine.state()
