# Ghost Engine — Deterministic Demo Mode (Illustrative)

This directory contains a **deterministic demo runner** for the Ghost Engine.

This demo is designed to **demonstrate behavior, not distribute the engine**.

---

## Important Note (Read This First)

This demo **cannot be executed standalone**.

It depends on the Ghost Engine core (`ghost/core/ghost_core.py`), which is **intentionally not included in this public repository**.

This demo exists for:

- Structural transparency  
- Behavioral explanation  
- Code-level inspection  

—not for independent execution.

If you are looking for something you can immediately `pip install && run`, this is **not that**.

---

## What This Demo Demonstrates

Even without execution, this file shows **exactly** how Ghost operates at runtime:

- How a **true cold start** is enforced
- How **state emergence** happens without memory
- How **strategy weights** are computed
- How a **single behavioral decision** is selected
- How **pre-state and post-state** are captured via trace

All without:
- An LLM
- Prompt engineering
- Persistent memory
- Training loops

---

## What This Demo Is

- A **controlled entry point** into the engine
- A **diagnostic harness** used during development
- A **behavioral proof**, not a product demo

The code is real.
The execution path is real.
The outputs shown in screenshots are real.

The core engine is simply not public.

---

## What This Demo Is Not

- ❌ A chatbot demo  
- ❌ A prompt-based system  
- ❌ A runnable toy example  
- ❌ A full release  

This is **engine-level work**, not UX.

---

## File Overview

```
demo/
└── demo_mode.py
```

### `demo_mode.py`

This file:

- Forces a **true cold start**:
  - `state = None`
  - `memory = None`
- Disables all external systems
- Executes **exactly one engine cycle**
- Records:
  - Pre-state snapshot
  - Strategy weights
  - Chosen strategy
  - Post-state snapshot

Everything is explicit.
Nothing is hidden in prompts.
Nothing is mocked.

---

## Why You Can’t Run It

The Ghost Engine core is not included because:

- It is still evolving
- It represents the primary intellectual work
- This repository is focused on **demonstration**, not distribution

The purpose here is to answer:

> “What does this system actually *do*?”

—not to ship a runnable binary.

---

## How to Verify This Demo Anyway

Even without execution, you can verify:

- There is **no LLM call**
- There is **no prompt injection**
- There is **no memory carryover**
- Strategy selection is **state-driven**
- Behavior emerges from **internal mechanics**

If you understand Python, you can follow the execution path line by line.

That is the point.

---

## Why This Exists

This demo exists because explaining Ghost abstractly caused confusion.

So instead of describing it, this file **shows**:

- Inputs
- Constraints
- Decision logic
- State transitions

With nothing hidden behind AI
