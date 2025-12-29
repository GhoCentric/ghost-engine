# adaptive_pressure_controller.py

class AdaptivePressureController:
    """
    Computes internal pressure signals to prevent
    stagnation, reward hacking, and passive convergence.
    """

    def __init__(self):
        self.last_state = None

    def compute_pressure(self, state: dict) -> dict:
        """
        Returns pressure signals without mutating state.
        """

        pressure = {
            "goal_pressure": 0.0,
            "exploration_pressure": 0.0,
            "output_gate": 1.0,  # 1.0 = allow, 0.0 = suppress
        }

        if self.last_state is None:
            self.last_state = state.copy()
            return pressure

        # --- Goal stagnation detection ---
        mood_delta = abs(state.get("mood", 0.5) - self.last_state.get("mood", 0.5))
        if abs(state["mood"] - 0.5) > 0.2 and mood_delta < 0.05:
            pressure["goal_pressure"] += 0.4
            print("[pressure]", pressure)
            
        # --- Monotonic drift detection ---
        mood_now = state.get("mood", 0.5)
        mood_prev = self.last_state.get("mood", 0.5)
        
        # --- Strategy repetition stagnation detection ---
        current_strategy = state.get("last_strategy")
        previous_strategy = self.last_state.get("last_strategy")

        if current_strategy is not None and current_strategy == previous_strategy:
            if current_strategy in ("reflect", "idle", "stabilize"):
                pressure["goal_pressure"] += 0.25
                print("[pressure:strategy_stagnation]", current_strategy, pressure)

        if mood_now < mood_prev and mood_now < 0.2:
            pressure["goal_pressure"] += 0.2
            print("[pressure:drift]", pressure)                    
            
        # --- Exploration vs exploitation ---
        memory_factor = state.get("memory_factor", 0.5)
        if memory_factor < 0.3:
            pressure["exploration_pressure"] += 0.3

        # --- Output gating ---
        belief_tension = state.get("belief_tension", 0.0)
        if belief_tension > 0.8:
            pressure["output_gate"] = 0.0  # suppress output

        self.last_state = state.copy()
        return pressure
