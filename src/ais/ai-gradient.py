from seekers_types import *
import math
import utils
import operator as op


def decide(mySeekers, goals, otherPlayers,world):
  # gradient descend
  f = force( list(utils.flatten(p.seekers for p in otherPlayers)), mySeekers, goals, world )
  for s in mySeekers:
    s.target = s.position + f(s.position)
  return mySeekers


def force(otherSeekers, mySeekers, goals, world):
  diamA = 500
  diamR = 100
  diamO = 250
  # diamM = 800
  scaleA = 100
  scaleR = 300
  scaleO = 400
  # scaleM = 100
  def at(x):
    attractive = [world.torus_direction(x,g.position) * scaleA * void(world,diamA,x,g.position) for g in goals]
    repulsiveOther = [world.torus_direction(x,s.position) * scaleR * void(world,diamR,x,s.position) for s in otherSeekers]
    repulsiveOwn = [world.torus_direction(x,s.position) * scaleO * void(world,diamO,x,s.position) for s in otherSeekers]
    a = genSum(attractive)
    r = genSum(repulsiveOwn) + genSum(repulsiveOther)
    return a - r
  return at

genSum = lambda xs: utils.foldr1(op.add,xs)


def void(world,diam,a,b):
  d = world.torus_distance(a,b) / diam
  return 1/(d**2) if d < 1 else 0




