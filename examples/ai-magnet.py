#bot

s = seekers[0]
dist = 10000
neargoal = None
for g in goals:
  if (g.position - s.position).norm() < dist:
    dist = (g.position - s.position).norm()
    neargoal = g

if dist < 100:
    print("** AN")
    s.set_magnet_attractive()
    s.target = own_camp.position # goals[0].position
else:
    print("** AUS")
    s.disable_magnet()
    s.target = goals[2].position
