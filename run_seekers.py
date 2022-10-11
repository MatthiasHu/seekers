from seekers import *


def main():
    import sys

    seekers_game = SeekersGame(ai_locations=sys.argv[1:])

    seekers_game.start()


if __name__ == "__main__":
    main()
