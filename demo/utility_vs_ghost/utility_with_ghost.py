from utility_baseline import compute_utility

def choose_action(env, ghost):
    bias = ghost.bias()

    scores = {}
    for action in bias:
        scores[action] = compute_utility(action, env) * bias[action]

    return max(scores, key=scores.get), scores
