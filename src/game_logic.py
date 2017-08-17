from seekers_types import *

import random
import copy


def tick(players, goals, animations, world):
  seekers = [s for p in players for s in p.seekers]
  # move and recover seekers
  for s in seekers:
    move_seeker(s, world)
    if s.disabled():
      s.disabled_counter -= 1
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
  for p in shuffled(players):
    for s in shuffled(p.seekers):
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


def shuffled(xs):
  ys = copy.copy(xs)
  random.shuffle(ys)
  return ys


def move_seeker(s, world):
  # friction
  s.velocity.x *= 1-Seeker.friction
  s.velocity.y *= 1-Seeker.friction
  # acceleration
  if not s.disabled_counter>0:
    a = (s.target - s.position).normalized()
    s.velocity.x += a.x*Seeker.thrust
    s.velocity.y += a.y*Seeker.thrust
  # displacement
  s.position.x += s.velocity.x
  s.position.y += s.velocity.y
  world.normalize_position(s.position)

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
