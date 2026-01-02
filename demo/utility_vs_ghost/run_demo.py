from environment import get_environment_signal
from utility_baseline import choose_action as baseline_choose
from utility_with_ghost import choose_action as ghost_choose
from ghost_layer import GhostState
from demo_config import TICKS

ghost = GhostState()
last_action = None

print("tick,system,action,strategy,tension")

for tick in range(TICKS):
    env = get_environment_signal(tick)

    # Baseline
    action_base, _ = baseline_choose(env)
    print(f"{tick},baseline,{action_base},-, -")

    # Ghost-assisted
    ghost.update(env, last_action)
    action_ghost, _ = ghost_choose(env, ghost)
    print(f"{tick},ghost,{action_ghost},{ghost.strategy},{ghost.tension:.2f}")

    last_action = action_ghost
