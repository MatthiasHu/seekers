from seekers import *


def main():
    import sys

    seekers_game = SeekersGame(local_ai_locations=sys.argv[1:], config=Config.from_filepath("default_config.ini"))

    seekers_game.start()


if __name__ == "__main__":
    main()
