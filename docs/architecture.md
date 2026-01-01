# Ghost Engine — High-Level Architecture

Ghost is an internal-state reasoning engine designed around explicit symbolic state, deterministic control, and constrained output shaping. Ghost does not attempt to model cognition or intelligence; it enforces consistency and constraint over downstream systems.

This document describes the intended architecture and how the implemented components relate to that design. Some layers are conceptual abstractions that are partially implemented or distributed across modules rather than existing as single subsystems.

---

## High-Level Flow (Conceptual)
┌──────────────────────────────────────────────┐
│               EXTERNAL INPUT                 │
│        (User, World Events, Systems)          │
└───────────────────────────┬──────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────┐
│              INPUT NORMALIZATION              │
│  - Signal parsing                             │
│  - Sanitization                               │
│  - Recall triggers                            │
└───────────────────────────┬──────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────┐
│          PERSISTENT MEMORY LAYER              │
│  - Symbolic memory                            │
│  - Recall weighting & decay                   │
│  - Historical snapshots                      │
└───────────────────────────┬──────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────┐
│      INTERNAL STATE KERNEL (DETERMINISTIC)    │
│                                              │
│  • Emotional vectors                          │
│  • Belief tension                             │
│  • Contradiction tracking                     │
│  • Stability & pressure metrics               │
│  • Awareness / depth bounds                   │
│                                              │
│  ↺ Meta-regulatory control loop               │
│    (prevents drift & collapse)                │
└───────────────────────────┬──────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────┐
│        STATE ENFORCEMENT & ROUTING             │
│  - Deterministic rule application              │
│  - Strategy selection                          │
│  - Output gating / suppression                 │
│  - Hallucination prevention                   │
└───────────────────────────┬──────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────┐
│      CONTEXT CONSTRAINT SNAPSHOT (CCS)        │
│  - Immutable state snapshot                   │
│  - Bias weights                               │
│  - Allowed / forbidden modes                  │
└───────────────────────────┬──────────────────┘
              ┌─────────────┴─────────────┐
              │                           │
              ▼                           ▼
┌──────────────────────────────┐   ┌──────────────────────────────┐
│ DETERMINISTIC OUTPUT PATH     │   │ OPTIONAL LANGUAGE RENDERER   │
│ (No LLM required)             │   │ (LLM as surface only)        │
│                                │   │                              │
│ - Symbolic templates           │   │ - Prompt constrained by CCS  │
│ - Rule-based output            │   │ - No state authority         │
│ - Guaranteed consistency      │   │ - No memory or agency        │
└───────────────┬──────────────┘   └───────────────┬──────────────┘
                │                                  │
                ▼                                  ▼
┌──────────────────────────────────────────────┐
│            OUTPUT VALIDATION LAYER            │
│  - State consistency check                   │
│  - Constraint compliance                    │
│  - Hallucination rejection                  │
└───────────────────────────┬──────────────────┘
                            │
                ┌───────────┴───────────┐
                ▼                       ▼
        ┌──────────────┐       ┌──────────────┐
        │ ACCEPTED     │       │ DISCARDED     │
        │ OUTPUT       │       │ OUTPUT        │
        └──────────────┘       └──────────────┘

---

## Design Notes

- Ghost is not an autonomous agent.
- Ghost does not select actions, goals, or plans.
- All behavior emerges from persistent symbolic state.
- Language models are optional and strictly subordinated.
- No output can directly mutate internal state.

---

## Core Design Principle

**Language is not the cognitive core.**

All reasoning occurs outside the language model. The LLM, when enabled, functions only as a controlled rendering surface after state evaluation and constraint enforcement.

---

## Internal State Variables

Ghost maintains explicit, bounded, and observable internal variables, including:

- Emotional vectors
- Belief tension metrics
- Contradiction counts
- Stability thresholds
- Memory persistence factors

These variables are mechanically enforced and persist across interactions.

---

## Hallucination Resistance (Architectural)

Ghost does not rely on temperature tuning, prompt complexity, or sampling tricks to reduce hallucination.

Instead, hallucination resistance is achieved through:

- Deterministic routing
- State-grounded output constraints
- Prohibition of undefined variables
- Separation of reasoning state from language generation

If information is not present in state, it cannot be asserted.

---

## Non-Agentic Constraint

Ghost is intentionally non-agentic.

It does not:

- Initiate actions
- Pursue goals
- Generate plans
- Simulate identity or selfhood

These constraints are foundational, not optional.

---

## Proof-of-Architecture Status

Ghost is an exploratory system demonstrating how symbolic state, deterministic control, and constrained probabilistic language can interact to produce stable, coherent behavior.

It is not a finished product.
It is an architectural thesis implemented in working code.

## Phase A — Deterministic Core Validation (Ablation Proof)

Phase A validates that Ghost’s behavior is not an artifact of language model output, stylistic variance, or token sampling.

To test this, the system was explicitly split into two layers:

- Deterministic Core
  - Internal symbolic state
  - Strategy selection
  - Pressure and stability modulation
  - Memory influence
  - Trace logging and invariants

- Optional Language Surface
  - Purely expressive
  - No authority over state
  - No memory mutation
  - Fully removable

### LLM Ablation Test

The optional language renderer was fully disabled.

The system was then run under the following conditions:

- Cold start
- No memory carryover
- Identical initial state
- Identical code path
- Identical strategy logic
- No token sampling
- No probabilistic text generation

### Observed Results (With LLM Disabled)

The following behaviors remained intact:

- Strategy weights were normalized and enforced
- Full pre_state → decision → post_state snapshots were recorded
- Strategy selection changed in response to internal state
- Output content aligned with selected strategy (e.g., “dream” vs “reflect”)
- All transitions were traceable, inspectable, and replayable
- No hidden state mutation occurred outside logged paths

The following behaviors disappeared as expected:

- Token-level variability
- Stylistic richness
- Sampling-based randomness
- Model-driven phrasing diversity

### Architectural Implication

If Ghost were a purely performative or decorative system, removing the language model would collapse its behavior into static or repetitive output.

This did not occur.

Instead:

Different inputs
→ different internal states
→ different strategy selection
→ different constrained outputs

This chain executed entirely without a language model.

### Determinism Boundary

Ghost is deterministic up to the strategy selection boundary.

Any nondeterminism exists only in:
- Optional language rendering
- Explicitly gated, post-decision expression

All internal reasoning, state transitions, and control logic are deterministic, logged, and auditable.

### Conclusion

Phase A demonstrates that Ghost is not a prompt artifact, Rube Goldberg machine, or stylistic illusion.

It is a deterministic state machine whose behavior survives ablation.

The language model, when enabled, does not create behavior — it renders it.
