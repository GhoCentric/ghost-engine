## v0.1.2 — Invariant-Verified Core

### Added
- Property-based testing using Hypothesis
- Formal invariants for threat dynamics:
  - Threat level is never negative
  - Threat accumulation is monotonic w.r.t. intensity
  - Threat decays monotonically in absence of new input
- Typed internal step representation (`GhostStep`)
  - Canonical internal format for structured engine input
  - Enables invariant testing without exposing internal types
- Strict separation between internal types and public state
- Actor-specific threat memory invariants

### Fixed
- Internal type leakage from `GhostStep` into public engine state
- Ambiguous input handling between dict-based and typed steps
- Environment contamination caused by parallel package installs

### Guarantees
- Engine state mutates only via explicit `step()` calls
- Public API remains dict-based and serialization-safe
- Internal logic may use typed representations (`GhostStep`) without leaking
- Core engine behavior is invariant under randomized adversarial input
