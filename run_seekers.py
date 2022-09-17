from seekers import *

import sys

if __name__ == "__main__":
    seekers_game = SeekersGame(ais_locations=sys.argv[1:])

    seekers_game.start()
