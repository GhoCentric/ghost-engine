## Ghost Engine – High-Level Architecture
┌──────────────────────────────────────────────┐ │                EXTERNAL INPUT                │ │        (User, World Events, Systems)         │ └───────────────────────────┬──────────────────┘ │ ▼ ┌──────────────────────────────────────────────┐ │              INPUT PROCESSING                │ │  - Signal parsing                            │ │  - Memory recall triggers                   │ │  - Sanitization / normalization             │ └───────────────────────────┬──────────────────┘ │ ▼ ┌──────────────────────────────────────────────┐ │          PERSISTENT MEMORY SYSTEM             │ │  - Long-term symbolic memory                 │ │  - Recall weighting & decay                  │ │  - Historical state snapshots                │ └───────────────────────────┬──────────────────┘ │ ▼ ┌────────────────────────────────────────────────────────────┐ │          INTERNAL STATE KERNEL (DETERMINISTIC CORE)         │ │                                                            │ │  Emotional Vectors        Belief Tension                   │ │  Mood & Band              Contradiction Tracking           │ │  Stability Metrics        Reaction Strength                │ │  Awareness / Depth Axis   Clamp Tolerance & Sensitivity    │ │  Global Tension           Personality Profile (optional)   │ │                                                            │ │  ↺  Meta-Regulatory Feedback Loop (Stability Control)      │ └───────────────────────────┬────────────────────────────────┘ │ ▼ ┌──────────────────────────────────────────────┐ │         STATE UPDATE & ENFORCEMENT            │ │  - Deterministic rule application             │ │  - Constraint enforcement                    │ │  - Hallucination prevention                  │ └───────────────────────────┬──────────────────┘ │ ▼ ┌──────────────────────────────────────────────┐ │     CONTEXT CONSTRAINT VECTOR (C.C.V.)        │ │  - State-derived bias weights                │ │  - Action / response suppression             │ │  - Output shaping parameters                 │ └───────────────────────────┬──────────────────┘ ┌─────────┴─────────┐ │                   │ ▼                   ▼
┌────────────────────────────┐   ┌──────────────────────────────┐ │ DETERMINISTIC OUTPUT PATH  │   │  OPTIONAL LLM RENDERING LAYER │ │  (NO LLM REQUIRED)         │   │  (PLR – Probabilistic Only)   │ │                            │   │                              │ │ - Symbolic templates       │   │ - Prompt constrained by CCV  │ │ - Rule-based language      │   │ - No state authority          │ │ - Guaranteed consistency  │   │ - No memory or agency         │ └───────────────┬────────────┘   └───────────────┬──────────────┘ │                                │ ▼                                ▼ ┌──────────────────────────────────────────────┐ │            OUTPUT VALIDATION LAYER            │ │  - State consistency check                   │ │  - Constraint compliance                    │ │  - Hallucination rejection                  │ └───────────────────────────┬──────────────────┘ │ ┌─────────┴─────────┐ ▼                   ▼ ┌──────────────┐     ┌──────────────┐ │ ACCEPTED     │     │ DISCARDED     │ │ OUTPUT       │     │ OUTPUT        │ └──────────────┘     └──────────────┘
### Design Notes
- Ghost is not an autonomous agent.
- Ghost does not select actions or goals.
- All behavior emerges from persistent symbolic state.
- Language models are optional and strictly subordinated.
- No output can directly mutate internal state.

Example: Internal State Influencing NPC Behavior
This example shows how Ghost influences NPC behavior without generating dialogue or actions directly.
Scenario
A player approaches an NPC shortly after stealing from a nearby shop.
The game engine reports this event to Ghost as contextual input.
Internal State Update
Ghost updates internal symbolic variables such as:
trust: decreases
suspicion: increases
tolerance: decreases
memory persistence: reinforced
These updates follow explicit rules (decay, reinforcement, clamping), not learned weights.
No dialogue is generated at this stage.
Constraint Output
From the updated state, Ghost produces advisory constraints such as:
reduce friendliness range
restrict cooperative responses
suppress information sharing
bias toward evasive or dismissive phrasing
These constraints describe what should not be allowed, not what must happen.
Dialogue / Action Selection
An external system (dialogue tree, template system, or LLM) selects from its existing options within those constraints.
For example, a valid result might be:
“We’re closed. Take your business elsewhere.”
This line was not chosen because the NPC “felt” anything.
It was chosen because other options were no longer permitted.
Key Point
Ghost did not write the dialogue.
Ghost made certain dialogue impossible.
This preserves:
mechanical consistency
believable behavior
debuggable causality
without requiring agentic language generation.
