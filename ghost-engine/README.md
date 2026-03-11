ghocentric-ghost-engine

A lightweight, deterministic internal state engine for experimenting with persistent state, temporal dynamics, and emergent behavior in interactive systems.

Ghost is NOT a language model and NOT a decision-maker. It is a minimal, stateful core designed to accumulate interaction signals over time and expose them in a clean, predictable, and serialization-safe way.

This project is intentionally focused on architecture and correctness first. Surface features, integrations, and higher-level reasoning systems are expected to be layered on top of the core in later versions.


INSTALLATION

pip install ghocentric-ghost-engine


BASIC USAGE

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

Ghost mutates state only via explicit step() calls.  
All public-facing state is exposed as dictionaries and is safe to serialize.


CORE DESIGN PRINCIPLES

• Deterministic, persistent state core  
• Explicit state transitions via step()  
• No hidden execution or side effects  
• Public API remains dict-based and serialization-safe  
• Internal typed representations may exist but never leak  
• Designed to be expanded around a stable core, not bloated prematurely  


Ghost does NOT:

• Choose actions  
• Generate dialogue  
• Interpret semantics  
• Store memory implicitly  

Those behaviors belong to external systems that consume Ghost’s state.


STABILITY & GUARANTEES (v0.2.1)

Ghost Engine v0.2.1 strengthens the deterministic interaction core with expanded runtime guarantees and formalized behavioral invariants.

The engine now guarantees:

• Deterministic runtime behavior (same inputs → same outputs)
• Explicit, bounded state mutation per step
• Actor state updates across interactions
• Actor-level threat accumulation tracking
• Pairwise relationship mutation with symmetric consistency
• Bounded cascade propagation across interaction networks
• Deterministic nonlinear modulation of global system tension
• Passive decay behavior during idle cycles
• Fully JSON-safe immutable snapshots of engine state

These guarantees hold under repeated execution, long-run simulation, and adversarial input streams.


ARCHITECTURAL EXPANSION (v0.2.0)

Version 0.2.0 introduces the first fully operational multi-agent interaction model on top of Ghost’s deterministic state core.

New capabilities include:

Agent State Mutation  
Agents now maintain evolving internal state (mood, tension, last intent) and react deterministically to interaction signals.

Relationship Graph  
Pairwise relationships now evolve through explicit interaction deltas, supporting long-term system memory without hidden state.

Bounded Cascade Propagation  
Signals propagate deterministically through an agent’s local interaction network with strict bounds to prevent runaway behavior.

Global System Tension  
The engine now tracks a shared global tension signal representing aggregate interaction pressure across the system.

Why This Matters

These changes allow Ghost-based systems to scale toward:

• large multi-agent simulations  
• social interaction modeling  
• emergent behavioral systems  
• game-world simulation engines  

while preserving the deterministic, explicit-state philosophy of the core.

ARCHITECTURAL EXPANSION (v0.2.1)

Version 0.2.1 refines Ghost’s runtime behavior through deterministic nonlinear dynamics and stronger system observability guarantees.

New capabilities include:

Actor Threat Memory
Agents now maintain explicit per-actor threat accumulation history, enabling long-term behavioral analysis and structured system introspection.

Nonlinear System Modulation
Global system tension now evolves through deterministic nonlinear modulation, allowing more realistic emergent dynamics while preserving strict predictability.

Idle-State Decay Dynamics
The engine now exhibits bounded passive decay when idle, improving long-run stability and preventing runaway system pressure.

Immutable JSON-Safe Snapshots
Engine snapshots are now fully serialization-safe, supporting external persistence, logging, and distributed simulation workflows without risk of mutation or type leakage.

Why This Matters

These refinements improve Ghost’s suitability for:

• long-running simulations  
• analytical modeling pipelines  
• reproducible experimental systems  
• persistent world simulation engines  

while maintaining the strict deterministic philosophy of the core.

TESTING PHILOSOPHY

Ghost uses property-based testing and invariant validation rather than relying solely on example-driven tests.

Core validation includes:

• determinism verification  
• clamping and bounded-state guarantees  
• serialization safety validation  

This ensures the engine remains correct and predictable as new systems and features are layered on top in future versions.


PROJECT STRUCTURE

ghost/        core engine modules  
tests/        invariant and runtime tests  
npc_demo.py   experimental sandbox for new ideas  
pyproject.toml build and packaging configuration  

Demos are intentionally minimal and act as experimental sandboxes.  
They are not representative of Ghost’s final scope.


STATUS

Ghost Engine remains in early development.

As of v0.2.0:

• The deterministic interaction core is stable  
• APIs may still evolve  
• Higher-level systems remain intentionally external  

This project is intended as a foundation for experimentation, research, and future system design rather than a finished product.


RELEASE HISTORY

v0.2.1
• Added actor-level threat accumulation tracking
• Introduced deterministic nonlinear modulation of global tension
• Implemented passive idle-cycle decay behavior
• Added fully JSON-safe immutable snapshot support
• Expanded regression, invariant, and integration test coverage

v0.2.0  
• Introduced real agent state mutation  
• Added relationship mutation logic  
• Implemented bounded cascade propagation  
• Achieved deterministic runtime guarantees  
• Achieved JSON-safe serialization baseline  

v0.1.3  
• AgentRegistry and neighbor indexing for scalable interaction graphs  

v0.1.2  
• Formal invariant verification using property-based testing  

v0.1.1  
• Core threat accumulation improvements  

v0.1.0  
• Initial public architecture release
