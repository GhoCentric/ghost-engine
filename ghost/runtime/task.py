# ghost/core/tasks.py
from __future__ import annotations
from .state import save_state

def do_pulse(state: dict):
    # visible heartbeat marker in state (no spammy prints)
    #state["last_pulse"] = now_ts()
    pass

def do_planner(state: dict):
    # trivial planner: promote first inbox item to plans if any
    if state["inbox"]:
        item = state["inbox"].pop(0)
        state["plans"].append(item)

def do_autosave(state: dict):
    save_state(state)

TASK_IMPLS = {
    "pulse": do_pulse,
    "planner": do_planner,
    "autosave": do_autosave,
}

# -------------------------------
# ghost_core integration hook
# -------------------------------

def run_task_pass(ctx):
    """
    Decide what Ghost *does* this cycle.
    TEMP VERSION: just echoes input as a 'say' task.
    """
    tasks = ctx.get("tasks") or {}
    text = ctx.get("input") or ""

    if not isinstance(tasks, dict):
        tasks = {}

    if text:
        tasks["say"] = text

    ctx["tasks"] = tasks
