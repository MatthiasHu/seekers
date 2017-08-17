from seekers_types import *
import math

def decide(mySeekers, goals, otherPlayers,world):
  # gradient descend
  f = lambda i: force( list(flatten(p.seekers for p in otherPlayers)), mySeekers, goals, world, i )
  for s in mySeekers:
    i = closest(goals,s)
    s.target = s.position + f(i)(s.position)
  return mySeekers


def closest(goals,s):
  dist = 10000
  index = 0
  for g,i in zip(goals,range(len(goals))):
    if (g.position - s.position).norm() < dist:
      dist = (g.position - s.position).norm()
      index = i
  return index

def force(otherSeekers, mySeekers, goals, world, i):
  diamA = 500
  diamR = 100
  diamO = 250
  # diamM = 800
  scaleA = 100
  scaleR = 300
  scaleO = 400
  # scaleM = 100
  def at(x):
    g = goals[i]
    # main = world.torus_direction(g.position,x) * scaleM * wedge(diamA,x,g.position)
    attractive = [world.torus_direction(g.position,x) * scaleA * void(world,diamA,x,g.position) for g in goals]
    repulsiveOther = [world.torus_direction(s.position,x) * scaleR * void(world,diamR,x,s.position) for s in otherSeekers]
    repulsiveOwn = [world.torus_direction(s.position,x) * scaleO * void(world,diamO,x,s.position) for s in otherSeekers]
    a = genSum(attractive)
    r = genSum(repulsiveOwn) + genSum(repulsiveOther)
    # raise Exception(((a-r).x,(a-r).y))
    return a - r
  return at


def void(world,diam,a,b):
  d = world.torus_distance(a,b) / diam
  return 1/(d**2) if d < 1 else 0

def wedge(world,diam,a,b):
  d = world.torus_distance(a,b) / diam
  return d if d < 1 else 0

def bump(world,diam,a,b):
  d = world.torus_distance(a,b) / diam
  return math.exp(1 / (d**2 - 1)) if d < 1 else 0

def genSum(xs):
  r = xs[0]
  for x in xs[1:]:
    r += x
  return r

def flatten(nested):
  for xs in nested:
    for x in xs:
      yield x

