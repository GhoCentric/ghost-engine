# ghocentric-ghost-engine

A lightweight, deterministic internal state engine for experimenting with
persistent state, temporal dynamics, and emergent behavior in interactive systems.

Ghost is NOT a language model and NOT a decision-maker.
It is a minimal, stateful core designed to accumulate interaction signals over time
and expose them in a clean, predictable, and serialization-safe way.

This project is intentionally focused on architecture and correctness first.
Surface features, integrations, and higher-level reasoning systems are expected
to be layered on top of the core in later versions.

---

INSTALLATION

pip install ghocentric-ghost-engine

---

BASIC USAGE

from ghost.engine import GhostEngine

engine = GhostEngine()

engine.step({
    "source": "npc_engine",
    "intent": "threat",
    "actor": "player",
    "intensity": 0.5,
})

state = engine.state()
print(state["npc"]["threat_level"])

Ghost mutates state only via explicit step() calls.
All public-facing state is exposed as dictionaries and is safe to serialize.

---

CORE DESIGN PRINCIPLES

- Deterministic, persistent state core
- Explicit state transitions via step()
- No hidden execution or side effects
- Public API remains dict-based and serialization-safe
- Internal typed representations may exist but never leak
- Designed to be expanded around a stable core, not bloated prematurely

Ghost does NOT:
- Choose actions
- Generate dialogue
- Interpret semantics
- Store memory implicitly

Those behaviors belong to external systems that consume Ghost’s state.

---

STABILITY & GUARANTEES (v0.1.2)

Ghost Engine v0.1.2 establishes a formally verified core protected by
property-based testing using Hypothesis.

Verified invariants include:
- Threat level is never negative
- Threat accumulation is monotonic with respect to input intensity
- Threat decays monotonically in the absence of new input
- Actor-specific threat memory remains consistent
- Internal step types never leak into public engine state
- Engine state mutates only through explicit step() calls

These guarantees hold under randomized and adversarial input.

---

TESTING PHILOSOPHY

Ghost uses property-based testing to validate behavioral invariants rather than
relying solely on example-driven tests.

This ensures the engine remains correct and predictable as new systems and features
are layered on top in future versions.

---

PROJECT STRUCTURE

ghost/           core engine modules
tests/           invariant and property-based tests
npc_demo.py      experimental sandbox for new ideas
pyproject.toml   build and packaging configuration

Demos are intentionally minimal and act as experimental sandboxes.
They are not representative of Ghost’s final scope.

---

STATUS

Ghost Engine is in early development.
The core architecture is stable as of v0.1.2, but APIs may evolve as new layers are added.

This project is intended as a foundation for experimentation, research, and
future system design rather than a finished product.
