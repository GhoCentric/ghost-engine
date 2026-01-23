class GhostEngine:
    def __init__(self, context: dict | None = None):
        """
        Core Ghost engine.
        Monolithic, self-contained v0.1 implementation.
        """

        # Initialize context if not provided
        if context is None:
            context = {}

        self._ctx = context

        # Required baseline state
        self._ctx.setdefault("cycles", 0)
        self._ctx.setdefault("input", None)
        self._ctx.setdefault("last_step", None)

    def step(self, input_data=None):
        """
        Advance the Ghost engine by one cycle.
        """

        ctx = self._ctx
        ctx["cycles"] += 1

        # Ensure npc bucket exists
        npc = ctx.setdefault("npc", {})
        npc.setdefault("threat_level", 0.0)
        npc.setdefault("last_intent", None)
        npc.setdefault("actors", {})

        # --- PROCESS INPUT FIRST ---
        received_threat = False

        if input_data:
            ctx["raw_input"] = input_data
            ctx["input"] = input_data

            if input_data.get("source") == "npc_engine":
                intent = input_data.get("intent")
                intensity = float(input_data.get("intensity", 0.0))
                actor = input_data.get("actor", "unknown")

                if intent == "threat":
                    received_threat = True

                    # Actor memory
                    actor_bucket = npc["actors"].setdefault(
                        actor,
                        {"threat_count": 0}
                    )
                    actor_bucket["threat_count"] += 1

                    # Mood modulation
                    mood = ctx.get("state", {}).get("mood", 0.5)
                    mood_multiplier = 0.5 + mood  # 0.5 → 1.5

                    threat_gain = intensity * mood_multiplier
                    npc["threat_level"] += threat_gain
                    npc["last_intent"] = "threat"

        # --- DECAY ONLY IF NO NEW THREAT ---
        if not received_threat:
            DECAY_RATE = 0.15
            npc["threat_level"] = max(0.0, npc["threat_level"] - DECAY_RATE)

        return ctx
    
    def state(self):
        """Return the live engine state (mutable)."""
        return self._ctx

    def snapshot(self):
        """Return an immutable snapshot of engine state."""
        import copy
        return copy.deepcopy(self._ctx)
