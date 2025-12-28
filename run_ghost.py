"""
run_ghost.py
Minimal launcher that uses the new ghost_core engine.
"""

import sys, os

# ✅ Ensure Ghost's main directory is always visible to Python
project_root = os.path.dirname(__file__)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# ✅ Tell Python to include the /ghost folder for imports
ghost_path = os.path.join(project_root, "ghost")
if ghost_path not in sys.path:
    sys.path.insert(0, ghost_path)

from core.ghost_core import run_ghost

if __name__ == "__main__":
    run_ghost()
