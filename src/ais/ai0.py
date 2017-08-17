from seekers_types import *

def decide(mySeekers, goals, otherPlayers, camps, world):
  # send every seeker to the nearest goal
  for s in mySeekers:
    dist = 10000
    neargoal = None
    for g in goals:
      if (g.position - s.position).norm() < dist:
        dist = (g.position - s.position).norm()
        neargoal = g
    s.target = neargoal.position
  return mySeekers

