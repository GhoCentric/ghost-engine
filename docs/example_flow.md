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
