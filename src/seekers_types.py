from hash_color import *

import random
import utils

class Vector:
  def __init__(self, x=0, y=0):
    self.x = x
    self.y = y

  def is_vector(obj):
    return isinstance(obj,Vector)

  def __add__(left, right):
    return Vector(left.x+right.x, left.y+right.y)
  def __sub__(left, right):
    return Vector(left.x-right.x, left.y-right.y)
  def __neg__(self):
    return self*(-1)
  def __mul__(self, factor):
    return Vector(self.x*factor, self.y*factor)
  def __rmul__(self, factor):
    return Vector(self.x*factor, self.y*factor)
  def __truediv__(self, divisor):
    return self * (1/divisor)
  def dot(self, other):
    return (self.x*other.x + self.y*other.y)

  def norm(self):
    return math.sqrt(self.x*self.x + self.y*self.y)
  
  def normalized(self):
    norm = self.norm()
    if (norm == 0):
      return Vector(0, 0)
    else:
      return Vector(self.x/norm, self.y/norm)

  def rotated(self):
    return Vector(-self.y, self.x)
      
  def fmap(self, f):
    return Vector(f(self.x),f(self.y))

class Physical:
  friction = 0.02
  max_speed = 5
  base_thrust = max_speed * friction
  
  def __init__(self, position, velocity=Vector(0, 0)):
    self.position = Vector(position.x, position.y)
    self.velocity = Vector(velocity.x, velocity.y)
  
  def move(self,world):
    # friction
    self.velocity.x *= 1-Seeker.friction
    self.velocity.y *= 1-Seeker.friction
    # acceleration
    a = self.compute_acceleration()
    self.velocity.x += a.x * self.thrust()
    self.velocity.y += a.y * self.thrust()
    # displacement
    self.position.x += self.velocity.x
    self.position.y += self.velocity.y
    world.normalize_position(self.position)
  
  def compute_acceleration(self):
    return Vector(0,0)
  
  def thrust(self):
    return self.base_thrust


class Goal(Physical):
  radius = 15

  def __init__(self, position, velocity=Vector(0, 0)):
    Physical.__init__(self,position,velocity)
    self.position = Vector(position.x, position.y)
    self.velocity = Vector(velocity.x, velocity.y)
    self.acceleration = Vector(0,0)

  def compute_acceleration(self):
    return self.acceleration


class Magnet():
  def __init__(self, strength = 0):
    self.strength = strength

  def is_magnet(obj):
    typ = isinstance(obj,Magnet) and isinstance(obj.strength,int)
    val = 1 >= obj.strength >= -1
    return typ and val

  def is_on(self):
    return not self.strength == 0
  
  def set_repulsive(self):
    self.strength = -1

  def set_attractive(self):
    self.strength = 1

  def disable(self):
    self.strength = 0




class Seeker(Physical):
  radius = 20
  magnet_slowdown = 0.2
  disabled_time = 1000
  alterables = [ ('target',Vector.is_vector)
                ,('magnet',Magnet.is_magnet) ]

  def __init__(self, position, velocity=Vector(0, 0)):
    Physical.__init__(self,position,velocity)
    self.target = self.position
    self.disabled_counter = 0
    self.magnet = Magnet()

  def disabled(self):
    return self.disabled_counter > 0

  def compute_acceleration(self):
    a = (self.target - self.position).normalized()
    return Vector(0,0) if self.disabled_counter>0 else a

  def thrust(self):
    b = self.magnet_slowdown if self.magnet.is_on() else 1
    return Physical.thrust(self) * b

  def set_magnet_repulsive(self):
    self.magnet.set_respulsive()

  def set_magnet_attractive(self):
    self.magnet.set_attractive()

  def disable_magnet(self):
    self.magnet.disable()

  def magnetic_force(self,world,pos):
    r = world.torus_distance(self.position,pos) / world.diameter()
    d = world.torus_direction(self.position,pos)
    return d * (self.magnet.strength * utils.bump(r*10))


class ScoreAnimation:
  duration = 20

  def __init__(self, position, color):
    self.position = position
    self.age = 0
    self.color = color

class Player:
  win_score = 100

  def __init__(self, name):
    self.name = name
    self.color = string_hash_color(name)
    self.score = 0
    self.seekers = []

class World:
  def __init__(self, width, height):
    self.width = width
    self.height = height

  def normalize_position(self, pos):
    pos.x -= math.floor(pos.x/self.width)*self.width
    pos.y -= math.floor(pos.y/self.height)*self.height

  def size_vector(self):
    return Vector(self.width,self.height)

  def diameter(self):
    return self.size_vector().norm()

  def torus_distance(self,left,right):
    def dist1d(l,a,b):
      delta = abs(a-b)
      return min(delta,l-delta)
    return Vector( dist1d(self.width,right.x,left.x)
                 , dist1d(self.height,right.y,left.y) ).norm()

  def torus_direction(self,left,right):
    def dir1d(l,a,b):
      delta = abs(a-b)
      return b-a if delta < l-delta else a-b
    return Vector( dir1d(self.width,right.x,left.x)
                 , dir1d(self.height,right.y,left.y) ).normalized()


