def get_environment_signal(tick):
    return {
        "threat": 0.6,
        "uncertainty": 0.5,
        "recent_failure": 0.4 if tick % 7 == 0 else 0.1,
    }
