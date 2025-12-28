from typing import Dict, List

__all__ = ["list_invariants", "add_invariant", "remove_invariant"]

def list_invariants(state: Dict) -> List[str]:
    return list(state.get("invariants", []))

def add_invariant(state: Dict, text: str) -> None:
    inv = state.setdefault("invariants", [])
    inv.append(text)

def remove_invariant(state: Dict, index: int) -> None:
    inv = state.setdefault("invariants", [])
    if 0 <= index < len(inv):
        inv.pop(index)
