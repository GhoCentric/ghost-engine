# ghost/core/loop.py
from __future__ import annotations
from typing import Dict

class LoopManager:
    """
    Minimal loop/task manager compatible with your commands.
    Tracks flags/intervals only (no threads).
    """
    def __init__(self):
        self.running = False
        self.tasks: Dict[str, Dict] = {
            "pulse":    {"on": False, "interval": 3.0, "last": 0.0},
            "planner":  {"on": False, "interval": 12.0, "last": 0.0},
            "autosave": {"on": False, "interval": 60.0, "last": 0.0},
        }

    # loop control
    def start(self) -> None:
        self.running = True
        print("loop started.")

    def stop(self) -> None:
        self.running = False
        print("loop stopped.")

    # task control
    def enable(self, name: str, on: bool) -> None:
        if name in self.tasks:
            self.tasks[name]["on"] = on
            print(f"task '{name}' is now {'ON' if on else 'OFF'}.")

    def set_interval(self, name: str, sec: float) -> None:
        if name in self.tasks:
            self.tasks[name]["interval"] = float(sec)
            print(f"task '{name}' interval set to {sec:.1f}s.")
