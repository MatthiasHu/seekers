#bot

dist = 10000
for i,s in enumerate(seekers):
  g = goals[i]
  dist = world.torus_distance(g.position,s.position)
  if dist < 90:
    print("** AN")
    s.set_magnet_attractive()
    s.target = own_camp.position
  else:
    print("** AUS")
    s.disable_magnet()
    s.target = goals[2].position


