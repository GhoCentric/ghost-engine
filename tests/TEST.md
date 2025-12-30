# Ghost Engine – Test Suite Overview

This document describes the purpose, scope, and guarantees of the Ghost Engine test suite.

The tests are designed to validate **deterministic behavior**, **state safety**, and **architectural correctness** across both configuration logic and core engine execution.

Not all tests are equal in dependency level. Some are **repo-safe configuration tests**, while others are **engine-dependent integration tests**. This distinction is intentional and documented below.

---

## Test Categories

### 1. Configuration / Deterministic Logic Tests  
These tests operate **purely on data and deterministic functions**.  
They do **not** require the Ghost engine to be running.

They can be reasoned about statically and validate correctness of configuration files and math logic.

### 2. Engine / Runtime Integration Tests  
These tests require a **fully wired Ghost engine**.  
They validate runtime behavior, state persistence, and resilience.

They are not expected to run in a bare GitHub environment.

---

## Test Index

| Test File | Category | Engine Required |
|---------|---------|----------------|
| `test_state_bounds_enforcement.py` | Configuration | ❌ No |
| `test_routing_weights.py` | Configuration | ❌ No |
| `test_pressure_routing.py` | Configuration | ❌ No |
| `test_stability_recovery.py` | Engine Integration | ✅ Yes |

---

## Test Descriptions

---

## `test_state_bounds_enforcement.py`

### What It Tests
This test verifies that Ghost’s internal state values **cannot exceed configured bounds**, even when subjected to extreme updates.

It intentionally pushes state variables (emotion, awareness, stability) far beyond acceptable limits and confirms that enforcement logic clamps them correctly.

### Guarantees
- State values never exceed defined `min` / `max` bounds
- Clamping behavior is deterministic
- No state variable can drift into unsafe territory

### What It Does NOT Test
- Routing logic
- Pressure modifiers
- Command execution
- Engine persistence

### Why This Test Is Important
State bounds are **hard safety rails**.  
Without strict enforcement, Ghost could accumulate runaway values and lose coherence.

This test guarantees that **state integrity is preserved regardless of input magnitude**.

### Dependency Level
- Configuration only
- No engine required
- Repo-safe

---

## `test_routing_weights.py`

### What It Tests
This test validates the **baseline strategy routing weights** defined in configuration.

It ensures that:
- All strategy weights exist
- Values are numeric
- Weights normalize correctly
- The resulting distribution sums to `1.0`

### Guarantees
- No missing or malformed strategy definitions
- Routing math is deterministic
- Configuration changes cannot silently break routing behavior

### What It Does NOT Test
- Pressure logic
- State mutation
- Engine runtime behavior
- Command execution

### Why This Test Is Important
Routing weights are the **foundation of Ghost’s decision system**.

If base weights are invalid, every higher-level behavior becomes unreliable.  
This test ensures that the starting point is always mathematically sound.

### Dependency Level
- Configuration only
- No engine required
- Repo-safe

---

## `test_pressure_routing.py`

### What It Tests
This test verifies that **pressure modifiers correctly bias routing behavior** relative to a baseline.

Specifically, it checks that:
- Pressure increases intended strategies
- Pressure decreases opposing strategies
- Directional influence behaves as designed
- Output weights remain normalized

### Guarantees
- Pressure modifiers actually influence routing
- Bias directionality is correct
- Scaling behaves predictably
- No unintended strategy amplification occurs

### What It Does NOT Test
- State persistence
- Command handling
- Runtime recovery
- Engine feedback loops

### Why This Test Is Important
Pressure routing is how Ghost adapts under goal-oriented or constrained conditions.

This test ensures that **pressure causes controlled bias**, not chaos or randomness.

It protects against subtle misconfigurations that would otherwise “feel wrong” but be hard to diagnose.

### Dependency Level
- Configuration only
- No engine required
- Repo-safe

---

## `test_stability_recovery.py`

### What It Tests
This is an **engine-level integration test**.

It validates Ghost’s ability to:
- Survive invalid commands
- Maintain internal state integrity
- Persist and reload state safely
- Recover equilibrium after destabilization

This test interacts directly with Ghost’s core runtime.

### Guarantees
- Invalid commands do not corrupt state
- Stability can degrade safely and recover
- State persistence is valid and reloadable
- Equilibrium restoration is deterministic

### What It Does NOT Test
- Routing weight math in isolation
- Pressure scaling alone
- Language generation quality
- External LLM behavior

### Why This Test Is Important
Stability recovery is a **survival property**.

Without it, Ghost would accumulate error, drift, or corruption over time.  
This test proves that Ghost behaves like a **resilient system**, not a fragile script.

### Dependency Level
- Full Ghost engine required
- Runtime execution required
- Not intended for skeleton-only repos

---

## Architectural Notes

- Configuration tests are intentionally isolated and deterministic.
- Engine tests are explicitly marked and documented as runtime-dependent.
- Passing all configuration tests guarantees structural correctness.
- Passing engine tests guarantees behavioral resilience.

This separation allows Ghost to be:
- Auditable
- Extendable
- Testable at multiple abstraction layers

---

## Summary

This test suite ensures that Ghost is:

- **Safe** (bounded state)
- **Deterministic** (routing logic)
- **Adaptive** (pressure handling)
- **Resilient** (runtime recovery)

Each test exists to protect a specific failure mode.

None are redundant.
