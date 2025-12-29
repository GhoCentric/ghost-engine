# State Model

This document describes the internal state model used by the Ghost engine.

The state model is not a personality simulation, emotional imitation, or agent framework. It is a symbolic bookkeeping system designed to track and regulate internal conditions that influence downstream behavior selection without generating behavior directly.

The purpose of the state model is **consistency, constraint, and interpretability**, not expressiveness.

---

## 1. Purpose of the State Model

The state model exists to solve a specific class of problems common in NPC systems and LLM-based interactions:

- Inconsistent behavior across time
- Personality drift caused by language generation
- Difficulty reasoning about *why* a response occurred
- Lack of durable internal conditions beyond conversational memory

Rather than allowing dialogue or action selection to implicitly define an NPC’s internal condition, Ghost maintains an explicit, persistent internal state that is updated independently of language generation.

This state is used to **constrain** downstream systems, not replace them.

---

## 2. Nature of State Variables

State variables in Ghost are:

- Explicitly defined
- Symbolic (not learned weights)
- Observable and inspectable
- Persistent across interactions
- Subject to deterministic update rules

They are not hidden embeddings, latent vectors, or emergent traits inferred by a model.

If a variable is not defined in state, it is considered nonexistent and cannot influence behavior.

---

## 3. Categories of State Variables
Exact variable names and availability depend on the current implementation.

The state model is organized into broad categories rather than fixed schemas. Exact variable names and counts are implementation-dependent.

Typical categories include:

### Relational State
Represents conditions tied to specific entities or actors.

Examples:
- trust
- suspicion
- familiarity
- tolerance

These variables allow the system to differentiate how the same stimulus affects different relationships.

---

### Affective / Reactivity State
Represents sensitivity and responsiveness, not emotions in a human sense.

Examples:
- baseline reactivity
- variance
- volatility
- dampening factor

These variables modulate *how strongly* stimuli affect other parts of the state.

---

### Memory Persistence State
Controls how long state changes endure.

Examples:
- decay rate
- reinforcement strength
- persistence bias

This allows Ghost to model differences between short-lived reactions and long-term consequences without narrative memory.

---

### Meta-Stability State
Tracks the overall coherence and integrity of the internal state.

Examples:
- stability
- contradiction pressure
- saturation thresholds

These variables exist to prevent runaway feedback, oscillation, or incoherent state combinations.

---

## 4. Update Rules (Conceptual)

State variables are updated through explicit, deterministic rules. These rules are designed to be simple, inspectable, and predictable.

Common rule patterns include:

- **Decay**  
  State values drift toward a baseline over time unless reinforced.

- **Reinforcement**  
  Repeated or consistent stimuli strengthen persistence.

- **Asymmetry**  
  Certain variables are easier to decrease than increase (e.g. trust).

- **Clamping**  
  Upper and lower bounds prevent unbounded growth.

- **Cross-modulation**  
  Some variables influence the sensitivity or decay rate of others.

No variable updates itself through language generation. All updates are driven by external stimuli routed through the state update layer.

---

## 5. What the State Model Does *Not* Do

The Ghost state model is intentionally limited.

It does **not**:

- Generate dialogue
- Select actions
- Form goals or intentions
- Perform planning
- Reason symbolically about the world
- Simulate consciousness or selfhood

State represents **condition**, not **decision**.

---

## 6. Relationship to Dialogue and Actions

State variables are not meant to be expressed directly in dialogue.

Instead, they influence behavior indirectly by constraining downstream systems such as:

- Dialogue trees
- Template selection
- Action availability
- Response tone bands
- Information disclosure thresholds

For example, a high suspicion state may:

- Remove cooperative dialogue options
- Bias toward evasive phrasing
- Suppress information-sharing actions

The resulting dialogue expresses state *implicitly* through behavior, not explicitly through self-description.

---

## 7. Observability and Instrumentation

During development and testing, Ghost can expose or describe its internal state.

This capability exists for:

- Debugging
- Validation
- Consistency testing
- Differentiating literal state from abstraction

This descriptive layer is considered **instrumentation**, not in-world behavior, and can be disabled or routed to logs in production systems.

---

## 8. Design Philosophy

The state model prioritizes:

- Mechanical consistency over narrative richness
- Interpretability over emergence
- Constraint over improvisation
- Explicit limits over implied capability

Ghost assumes that believable behavior emerges from **what is made impossible**, not from what is freely generated.

The state model exists to make that constraint space stable, inspectable, and durable.
