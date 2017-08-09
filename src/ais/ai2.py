from seekers_types import *

def decide(mySeekers, goals, otherPlayers):
  # send every seeker to the first goal
  for i, s in enumerate(mySeekers):
    s.target = goals[0].position
  return mySeekers
