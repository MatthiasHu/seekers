from seekers_types import *

import random
import copy
import utils


def tick(players, goals, animations, world):
  seekers = [s for p in players for s in p.seekers]
  # move and recover seekers
  for s in seekers:
    s.move(world)
    if s.disabled():
      s.disabled_counter -= 1
  # compute magnetic forces and move goals
  for g in goals:
    force = Vector(0,0)
    for s in seekers:
      force += s.magnetic_force(world,g.position)
    g.acceleration = force
    g.move(world)
  # handle seeker collisions
  for i in range(0, len(seekers)):
    s = seekers[i]
    for j in range(i+1, len(seekers)):
      t = seekers[j]
      d = world.torus_distance(t.position,s.position)
      if d < Seeker.radius*2:
        s_copy = copy.deepcopy(s)
        seeker_collided(s, t)
        seeker_collided(t, s_copy)
  # handle collisions of seekers with goals
  for p in utils.shuffled(players):
    for s in utils.shuffled(p.seekers):
      if not s.disabled():
        for i in range(0, len(goals)):
          d = world.torus_distance(goals[i].position,s.position)
          if d < Seeker.radius + Goal.radius:
            goal_scored(p, i, goals, animations, world)
  # advance animations
  for _, animation_list in animations.items():
    for (i, a) in enumerate(animation_list):
      a.age += 1
      if a.age > a.duration:
        animation_list.pop(i)


def seeker_collided(s, t):
  # disable the seeker
  s.disabled_counter = Seeker.disabled_time
  # bounce off the other seeker
  d = t.position - s.position
  if d.norm() != 0:
    dn = d.normalized()
    dv = t.velocity - s.velocity
    dvdn = dv.dot(dn)
    if dvdn < 0:
      s.velocity += dn * dvdn
    ddn = d.dot(dn)
    if ddn < Seeker.radius*2:
      s.position += dn * (ddn - Seeker.radius*2)

def goal_scored(player, goal_index, goals, animations, world):
  player.score += 1
  g = goals[goal_index]
  goals[goal_index] = Goal(random_position(world))
  animations["score"].append(ScoreAnimation(g.position, player.color))

def random_position(world):
  return Vector(random.uniform(0, world.width)
               ,random.uniform(0, world.height))
