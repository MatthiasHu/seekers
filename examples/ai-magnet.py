#bot

s = seekers[0]
dist = 10000
neargoal = None
for g in goals:
  if world.torus_distance(g.position,s.position) < dist:
    dist = world.torus_distance(g.position,s.position)
    neargoal = g

if dist < 90:
    print("** AN")
    s.set_magnet_attractive()
    s.target = own_camp.position
else:
    print("** AUS")
    s.disable_magnet()
    s.target = goals[2].position
