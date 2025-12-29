# Ghost Engine Documentation

This folder contains supporting technical documentation for the Ghost internal-state reasoning engine.

Ghost is not a single model, algorithm, or agent. It is a layered system designed to maintain, regulate, and expose a persistent internal symbolic state. That state is used to produce advisory signals and constraints that bias downstream systems — not to directly control dialogue, actions, or planning.

Ghost does not generate goals, actions, or dialogue on its own. It evaluates internal conditions and shapes what downstream systems are likely or permitted to produce through constraint-first routing and gating.

---

## Core Idea

Most AI and NPC systems conflate three distinct concerns:

- Internal state and reasoning  
- Decision-making  
- Language or action output  

Ghost deliberately separates these layers.

Ghost maintains an explicit internal symbolic state (belief tension, emotional vectors, stability metrics, contradiction tracking), updates that state deterministically, and then emits advisory signals that bias or constrain downstream behavior.

Language generation, animation, and action selection remain external.

---

## High-Level Data Flow

At a high level, Ghost operates as follows:

1. An external system provides a situation, stimulus, or query  
2. Ghost updates its internal symbolic state deterministically  
3. Internal state produces advisory signals, routing preferences, or output gates  
4. An external system selects dialogue or actions within those constraints  

Ghost never directly selects dialogue or actions. It selects internal strategies and constraints that shape downstream behavior without exercising agency or control.

---

## Why This Exists

Ghost exists to address failure modes common in language-driven systems where language generation is treated as cognition:

- Narrative drift
- Inconsistent personality
- Prompt exploitation
- Hallucinated intent or memory
- Opaque or irreproducible reasoning

By making internal state explicit and language downstream, Ghost prioritizes:

- Consistency over novelty  
- Observability over performance  
- Constraint over improvisation  

---

## What Ghost Is Not

Ghost is intentionally limited. It is not:

- An autonomous agent  
- A general intelligence  
- A dialogue system  
- A persona generator  

These limits are not shortcomings — they define the architecture.
