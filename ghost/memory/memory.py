# ghost/core/memory.py
from __future__ import annotations
from pathlib import Path
import json, time
from typing import Dict, Any, List, Tuple

MEMORY_FILE = "memory.json"

# ==========================================================
# Memory Initialization Patch
# Adds: init_memory()
# ==========================================================

def init_memory():
    """
    Initialize Ghost's memory container.
    This runs once when ghost_core.init_context() is called.
    """
    return {
        "short_term": [],
        "long_term": [],
        "topics": {},
        "last_reflection": None,
    }

def _paths(data_dir: Path) -> Path:
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / MEMORY_FILE

# ---------- state helpers ----------
def _blank_state() -> Dict[str, Any]:
    return {
        "inbox": [],
        "plans": [],
        "tasks": {
            "pulse":    {"on": False, "interval": 3.0},
            "planner":  {"on": False, "interval": 12.0},
            "autosave": {"on": False, "interval": 60.0},
        },
        "invariants": [],
        "meta": {"enabled": True, "events": []},  # metacognition store
        "router": {"patterns": []},               # list of {"pattern","reply"}
    }

def _ensure_keys(state: Dict[str, Any]) -> None:
    base = _blank_state()
    # fill only missing top-level keys
    for k, v in base.items():
        if k not in state:
            state[k] = v
    # migrate old task shapes if needed
    for name, task in state.get("tasks", {}).items():
        if "enabled" in task and "on" not in task:
            task["on"] = bool(task.pop("enabled"))

# ---------- i/o ----------
def load_state(data_dir: Path) -> Dict[str, Any]:
    p = _paths(data_dir)
    if not p.exists():
        return _blank_state()
    try:
        state = json.loads(p.read_text(encoding="utf-8"))
        _ensure_keys(state)
        return state
    except Exception:
        return _blank_state()

def save_state(data_dir: Path, state: Dict[str, Any]) -> None:
    p = _paths(data_dir)
    p.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

# ---------- meta ----------
def meta_log(state: Dict[str, Any], event: str) -> None:
    if state["meta"].get("enabled", True):
        state["meta"]["events"].append({"ts": time.time(), "event": event})

def get_meta(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    return state["meta"]["events"]

def set_meta_enabled(state: Dict[str, Any], on: bool) -> None:
    state["meta"]["enabled"] = bool(on)

# ---------- memory ops ----------
def add_memory(state: Dict[str, Any], text: str) -> None:
    state["inbox"].append(text)

def recall(state: Dict[str, Any], q: str) -> List[str]:
    ql = q.lower()
    hits = [t for t in state.get("inbox", []) if ql in t.lower()]
    return hits

def add_invariant(state: Dict[str, Any], text: str) -> None:
    state["invariants"].append(text)

def remove_invariant(state: Dict[str, Any], idx: int) -> bool:
    try:
        state["invariants"].pop(idx)
        return True
    except Exception:
        return False

def list_invariants(state: Dict[str, Any]) -> List[str]:
    return state.get("invariants", [])

# ---------- router ----------
def add_pattern(state: Dict[str, Any], pattern: str, reply: str) -> None:
    patterns = state.setdefault("router", {}).setdefault("patterns", [])
    if not isinstance(patterns, list):
        # migrate if someone accidentally stored a dict
        state["router"]["patterns"] = patterns = []
    patterns.append({"pattern": pattern.lower().strip(), "reply": reply})

def list_patterns(state: Dict[str, Any]) -> List[Dict[str, str]]:
    return state.get("router", {}).get("patterns", [])

def route_text(state: Dict[str, Any], text: str) -> str | None:
    tl = text.lower().strip()
    for pr in list_patterns(state):
        if tl.startswith(pr["pattern"]):
            return pr["reply"]
    return None
    
# ==========================================================
# Memory Cycle Patch
# Adds: run_memory_pass(ctx)
# ==========================================================

def run_memory_pass(ctx):
    """
    MUST RUN *AFTER* LLM output.
    This version only records final output and meta AFTER Ghost finishes speaking.
    """
    if ctx is None:
        return

    # Must capture memory container
    memory = ctx.setdefault("memory", {})
    short_term = memory.setdefault("short_term", [])
    long_term = memory.setdefault("long_term", [])

    # --- SAFETY: If no output yet, skip memory entirely ---
    # This prevents the LLM from being blocked.
    if ctx.get("output") is None:
        return

    # Raw emotion/meta snapshots (optional, not used in routing)
    raw_meta = ctx.get("meta", {})
    raw_emotion = ctx.get("emotion", {})
    flags = ctx.get("flags", {})

    # Build a final memory entry AFTER output exists
    entry = {
        "input": ctx.get("input", ""),
        "output": ctx.get("output", ""),  # <-- Now safe to store
        "emotion": raw_emotion,
        "meta": {
            "belief_tension": float(raw_meta.get("belief_tension", 0.0)),
            "contradictions": raw_meta.get("contradictions", 0),
            "global_tension": float(raw_meta.get("global_tension", 0.0)),
            "__raw__": raw_meta,
        },
        "flags": flags,
        "timestamp": time.time(),
    }

    # Store memory
    short_term.append(entry)
    if len(short_term) > 50:
        short_term[:] = short_term[-50:]

    # Short -> long transfer
    if len(short_term) > 20:
        long_term.append(short_term.pop(0))

    # Logging
    bt = entry["meta"].get("belief_tension")
    gt = entry["meta"].get("global_tension")
    ctx.setdefault("log", []).append(
        f"[memory] short={len(short_term)}, long={len(long_term)}, bt={bt}, gt={gt}"
               )
