from seekers_types import *

def decide(mySeekers, goals, otherPlayers, camps, world):
  # send every seeker to some goal
  for i, s in enumerate(mySeekers):
    s.target = goals[i % len(goals)].position
    s.set_magnet_attractive()
  return mySeekers

