# Example Flow — How Ghost Influences Behavior (Non-Agentic)

This document provides a concrete example of how the Ghost engine processes input, updates internal state, and constrains downstream behavior **without generating dialogue, actions, or plans**.

Ghost does not act.  
Ghost does not decide outcomes.  
Ghost restricts what outcomes are allowed.

---

## Scenario

A player approaches an NPC shortly after stealing from a nearby shop.

The game engine reports this event to Ghost as contextual input.

Ghost receives **signals**, not intent:
- proximity event
- recent theft flag
- NPC–player interaction request

---

## Step 1 — Input Normalization

Ghost routes and interprets input through deterministic parsing and pattern detection logic:

- event_type = `player_interaction`
- context_flag = `recent_theft`
- target = `npc_merchant`

No interpretation, dialogue, or emotion occurs at this stage.

---

## Step 2 — Memory Recall

Ghost queries persistent symbolic memory:

- Prior encounters with the player
- Existing trust or suspicion levels
- Recent contradiction or tension history

Memory recall may strengthen or decay prior signals based on time and reinforcement rules.

Memory recall is implemented via distributed symbolic memory modules rather than a single retrieval stage.

---

## Step 3 — Internal State Update (Deterministic)

Ghost updates internal symbolic state using deterministic rules:

- trust → decreases
- suspicion → increases
- tolerance → decreases
- belief tension → increases
- stability → checked and clamped if needed

All updates are:
- rule-based
- bounded
- observable
- repeatable

No language is generated.

---

## Step 4 — Meta-Regulatory Enforcement

Meta-regulatory controls evaluate system health:

- Prevent runaway escalation
- Prevent collapse into passivity
- Enforce stability thresholds

If instability or stagnation is detected, corrective pressure is applied **before any output is allowed**.

---

## Step 5 — Strategy Routing

Based on internal state, Ghost selects an selects a response strategy via deterministic weighting and pressure overrides:

Examples:
- `dismissive`
- `guarded`
- `restricted`
- `neutral`

This is **not** dialogue selection.  
It is a **routing decision** that limits downstream options.

---

## Step 6 — Constraint Snapshot Generation

Ghost produces an authoritative state snapshot derived from current internal variables, including:

- allowed response modes
- suppressed behaviors
- bias weights
- output gating flags

This snapshot is authoritative for the remainder of the interaction.

---

## Step 7 — Downstream Selection (External System)

An external system (dialogue tree, template engine, or optional LLM):

- selects dialogue or actions **within Ghost’s constraints**
- cannot access or modify Ghost’s internal state
- cannot override forbidden modes

Example result:

> “We’re closed. Take your business elsewhere.”

This line was not *chosen* by Ghost.  
Other lines were made **invalid**.

---

## Key Outcome

Ghost did **not**:
- write dialogue
- choose actions
- simulate emotions
- pursue goals

Ghost **did**:
- enforce internal consistency
- restrict invalid behavior
- preserve causal continuity

---

## Why This Matters

This approach enables:

- believable consistency without scripted emotions
- debuggable causality instead of opaque generation
- stateful behavior without agentic autonomy
- NPCs that react coherently without “thinking”

Ghost turns **state into constraint**, not language into cognition.

---

## Summary

Ghost operates as a **deterministic internal-state authority** that constrains downstream systems.

Language and action selection remain external.

Behavior emerges from **what is no longer allowed**, not from simulated intent.
