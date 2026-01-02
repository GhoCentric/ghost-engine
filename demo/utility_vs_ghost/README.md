Ghost Engine — Utility Bias Demo
================================

Why this demo exists
--------------------
This demo exists to answer a specific criticism:

“Isn’t this just a utility system?”

The goal is not to replace utility systems or behavior trees.
The goal is to show how an explicit internal-state layer can run
alongside a utility system and influence its behavior in a stable,
inspectable way.

This demo intentionally avoids the full Ghost engine.
It isolates the core idea so it can be reasoned about without
terminology, abstraction, or LLM involvement.


What is being compared
----------------------
Each tick runs two decision paths under the same environment signal:

1) baseline
   A simple utility chooser that reacts directly to the environment.

2) ghost
   The same utility chooser, but with a lightweight Ghost-style layer
   that:
   - tracks internal state (tension)
   - selects a strategy mode
   - biases the utility choice without choosing actions itself


What Ghost is doing here
------------------------
Ghost does NOT choose actions.

It:
- updates internal state over time
- accumulates tension instead of resetting every tick
- selects a high-level strategy mode
- biases how the utility system behaves under identical inputs

Think of it as state governance, not decision logic.


What to look for in the output
------------------------------
Each tick prints two rows:

tick, system, action, strategy, tension

baseline:
- utility reacts immediately
- no memory
- no accumulated state

ghost:
- utility behavior drifts over time
- tension accumulates
- strategy selection influences future choices

Pay attention to:
- how actions diverge under similar conditions
- how tension grows instead of snapping back
- how strategy affects future behavior
- how every shift is traceable to printed state

How to read the output:
-----------------------
The CSV logs two rows per tick: a baseline row and a ghost row. Both systems see the same environment and use the same utility logic. The baseline system has no internal state governance, so its behavior remains static under similar conditions. The ghost-assisted system runs an additional internal-state layer that accumulates tension and selects a high-level strategy mode. Over time, this causes the ghost system’s action choices to diverge gradually from baseline, despite identical inputs. The key thing to observe is not that Ghost “chooses actions,” but that it changes when and why certain actions become preferable, with every shift traceable to explicit state variables printed alongside the decision.

Running diff_actions.py identifies 42 divergent ticks where Ghost’s action differs from the baseline.

What this demo proves (and what it doesn’t)
-------------------------------------------
This demo proves:
- Ghost-style biasing can be separated from decision logic
- Internal state can be explicit, inspectable, and stable
- Utility systems can be influenced without being replaced

This demo does NOT claim:
- novelty over all utility systems
- superiority to existing architectures
- that this cannot collapse into “floats + logging”

If it does collapse there, that’s still a valid and useful result.


Why this matters
----------------
In many systems, internal bias emerges implicitly and is hard to debug.

Ghost’s value is making that layer:
- explicit
- inspectable
- governable

instead of implicit and emergent.
