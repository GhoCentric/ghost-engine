# ghocentric-ghost-engine

A lightweight, deterministic internal state engine for experimenting with persistent state, temporal dynamics, and emergent behavior in interactive systems.

Ghost is **NOT** a language model and **NOT** a decision-maker.  
It is a minimal, stateful core designed to accumulate interaction signals over time and expose them in a clean, predictable, and serialization-safe way.

This project is intentionally focused on architecture and correctness first. Surface features, integrations, and higher-level reasoning systems are expected to be layered on top of the core.

---

## Installation

```bash
pip install ghocentric-ghost-engine
```

---

## Basic Usage

```python
from ghost.engine import GhostEngine

engine = GhostEngine()

engine.step({
    "source": "npc_engine",
    "intent": "threat",
    "actor": "player",
    "target": "guard",
    "intensity": 0.5,
})

state = engine.state()
print(state["npc"]["threat_level"])
```

Ghost mutates state only through explicit `step()` calls.  
All public-facing state is exposed as dictionaries and is safe to serialize.

---

## Core Design Principles

- Deterministic, persistent state core  
- Explicit state transitions via `step()`  
- No hidden execution or side effects  
- Public API remains dict-based and serialization-safe  
- Internal typed representations may exist but never leak  
- Designed to be expanded around a stable core  

### Ghost does NOT:

- Choose actions  
- Generate dialogue  
- Interpret semantics  
- Store memory implicitly  

These responsibilities belong to external systems that consume Ghost’s state.

---

## Stability & Guarantees (v0.2.2)

Ghost Engine v0.2.2 strengthens runtime correctness and serialization guarantees across public engine state.

The engine guarantees:

- Deterministic runtime behavior (same inputs → same outputs)  
- Explicit, bounded state mutation per step  
- Actor state updates across interactions  
- Actor-level threat accumulation tracking  
- Pairwise relationship mutation with symmetric consistency  
- Bounded cascade propagation across interaction networks  
- Deterministic nonlinear modulation of global system tension  
- Passive decay behavior during idle cycles  
- Fully JSON-safe public state and immutable snapshots  

These guarantees hold under repeated execution, long-run simulation, and adversarial input streams.

---

## Architectural Expansion (v0.2.x)

Recent releases introduce the first fully operational multi-agent interaction model on top of Ghost’s deterministic state core.

### Key Capabilities

**Agent State Mutation**  
Agents maintain evolving internal state (mood, tension, last intent) and react deterministically to interaction signals.

**Relationship Graph**  
Pairwise relationships evolve through explicit interaction deltas, supporting long-term system memory without hidden state.

**Bounded Cascade Propagation**  
Signals propagate deterministically through local interaction networks with strict bounds to prevent runaway behavior.

**Global System Tension**  
The engine tracks shared system pressure across interactions using deterministic nonlinear modulation.

**Actor Threat Memory**  
Agents maintain explicit per-actor threat accumulation history for structured introspection.

**Idle-State Decay Dynamics**  
Bounded passive decay improves long-run stability and prevents runaway system pressure.

---

## Testing Philosophy

Ghost uses property-based testing and invariant validation rather than relying solely on example-driven tests.

Core validation includes:

- determinism verification  
- bounded-state guarantees  
- serialization safety validation  

This ensures the engine remains correct and predictable as new systems are layered on top.

---

## Project Structure

```
ghost/        core engine modules  
tests/        invariant and runtime tests  
npc_demo.py   experimental sandbox  
pyproject.toml build configuration  
```

Demos are intentionally minimal and act as experimental sandboxes.  
They are not representative of Ghost’s final scope.

---

## Status

Ghost Engine remains in early development.

As of v0.2.x:

- The deterministic interaction core is stable  
- APIs may still evolve  
- Higher-level systems remain intentionally external  

This project is intended as a foundation for experimentation, research, and future system design rather than a finished product.

---

## Release History

**v0.2.2**
- Fixed public state serialization issue in relationship subsystem  
- Replaced set-based storage with JSON-safe structures  
- Strengthened invariant coverage across runtime state  

**v0.2.1**
- Added actor-level threat accumulation tracking  
- Introduced deterministic nonlinear system modulation  
- Implemented passive idle-cycle decay  
- Added immutable JSON-safe snapshots  

**v0.2.0**
- Introduced multi-agent state mutation  
- Added relationship mutation logic  
- Implemented bounded cascade propagation  
- Achieved deterministic runtime guarantees  

**v0.1.x**
- Foundational architecture releases
