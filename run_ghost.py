# run_ghost.py

from ghost.runtime.loop import LoopManager

def main():
    loop = LoopManager()
    loop.start()

if __name__ == "__main__":
    main()
