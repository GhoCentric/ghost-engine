class GhostState:
    def __init__(self):
        self.tension = 0.0
        self.strategy = "pattern"

    def update(self, env, last_action):
        self.tension += abs(env["threat"] - env["uncertainty"]) * 0.1
        self.tension = min(self.tension, 1.0)

        if self.tension > 0.6:
            self.strategy = "cautious"
        elif self.tension < 0.3:
            self.strategy = "pattern"

    def bias(self):
        if self.strategy == "cautious":
            return {"engage": 0.6, "investigate": 1.2, "idle": 1.0}
        return {"engage": 1.0, "investigate": 1.0, "idle": 1.0}
