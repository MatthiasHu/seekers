import seekers_types

def ai0(mySeekers, goals, otherPlayers):
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

def ai1(mySeekers, goals, otherPlayers):
  # send every seeker to some goal
  for (i, s) in enumerate(mySeekers):
    s.target = goals[i % len(goals)].position
  return mySeekers

def ai2(mySeekers, goals, otherPlayers):
  # send every seeker to the first goal
  for (i, s) in enumerate(mySeekers):
    s.target = goals[0].position
  return mySeekers
