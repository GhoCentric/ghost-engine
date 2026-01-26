from dataclasses import dataclass


@dataclass
class GhostStep:
    source: str
    intent: str | None = None
    actor: str = "unknown"     # ← DEFAULT
    intensity: float = 0.0
