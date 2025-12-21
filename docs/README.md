Ghost Engine Documentation
This folder contains supporting documentation for the Ghost internal-state reasoning engine.
Ghost is not a single model, algorithm, or agent.
It is a layered system designed to maintain and regulate a persistent internal state, then expose that state to external systems through constraints rather than direct control.
Ghost does not generate goals, actions, or dialogue on its own.
It evaluates internal conditions and limits what downstream systems are allowed to do.
Core Idea
Most NPC or AI systems conflate three things:
internal state
decision-making
language output
Ghost deliberately separates them.
Ghost maintains internal symbolic state (beliefs, tensions, stability, etc.), updates that state deterministically, and then outputs advisory constraints that bias or restrict behavior elsewhere.
Language, actions, and animation remain external.
High-Level Data Flow
At a high level, Ghost operates like this:
An external system provides a situation or stimulus
Ghost updates its internal symbolic state
Internal state produces constraints and advisory signals
An external system selects dialogue or actions within those constraints
Ghost never directly chooses dialogue or actions.
It only limits and biases what is possible.
Why This Exists
Ghost exists to solve problems that appear when language generation is treated as cognition:
narrative drift
inconsistent personality
prompt exploitation
hallucinated intent or memory
opaque decision-making
By making state explicit and language downstream, Ghost prioritizes:
consistency over novelty
observability over performance
constraint over improvisation
What Ghost Is Not
Ghost is intentionally limited.
It is not:
an autonomous agent
a general intelligence
a dialogue system
a persona generator
Those limits are not shortcomings — they are the architecture.
