"""
Ghost public API (pip-facing).
This file defines the ONLY supported entry points.
"""

from .engine import GhostEngine

_ENGINE = None


def init():
    """Initialize a new Ghost engine."""
    global _ENGINE
    _ENGINE = GhostEngine()
    return _ENGINE


def step(input_data=None):
    """Advance the engine by one cycle."""
    if _ENGINE is None:
        raise RuntimeError("Ghost not initialized. Call ghost.init() first.")
    return _ENGINE.step(input_data)


def state():
    """Return a mutable view of the current state."""
    if _ENGINE is None:
        raise RuntimeError("Ghost not initialized. Call ghost.init() first.")
    return _ENGINE.state()


def snapshot():
    """Return an immutable snapshot of the current state."""
    if _ENGINE is None:
        raise RuntimeError("Ghost not initialized. Call ghost.init() first.")
    return _ENGINE.snapshot()


def reset():
    """Reset the engine."""
    global _ENGINE
    _ENGINE = GhostEngine()
    return _ENGINE
