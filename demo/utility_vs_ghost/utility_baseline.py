def compute_utility(action, env):
    if action == "idle":
        return 1.0 - env["threat"]
    if action == "investigate":
        return env["uncertainty"]
    if action == "engage":
        return env["threat"] - env["recent_failure"]
        
def choose_action(env):
    scores = {
        a: compute_utility(a, env)
        for a in ["idle", "investigate", "engage"]
    }
    return max(scores, key=scores.get), scores
