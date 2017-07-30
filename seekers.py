import hashlib
import pygame
import math
import copy
import random

h = hashlib.md5(b"hi")
print(h.hexdigest())


screen = None
quit = False
clock = None
width = 768
height = 768
goals = []
seekers = []

class Vector:
  def __init__(self, x=0, y=0):
    self.x = x
    self.y = y

  def __add__(left, right):
    return Vector(left.x+right.x, left.y+right.y)
  def __sub__(left, right):
    return Vector(left.x-right.x, left.y-right.y)
  def __mul__(self, factor):
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

class Goal:
  radius = 15

  def __init__(self, x, y):
    self.position = Vector(x, y)

class Seeker:
  radius = 20
  friction = 0.02
  max_speed = 5
  thrust = max_speed * friction
  disabled_time = 100

  def __init__(self, x, y, vx=0, vy=0):
    self.position = Vector(x, y)
    self.velocity = Vector(vx, vy)
    self.target = self.position
    self.disabled_counter = 0
    self.normalize_position()

  def move(self):
    # friction
    self.velocity.x *= 1-self.friction
    self.velocity.y *= 1-self.friction
    # acceleration
    if (not self.disabled_counter>0):
      a = (self.target - self.position).normalized()
      self.velocity.x += a.x*self.thrust
      self.velocity.y += a.y*self.thrust
    # displacement
    self.position.x += self.velocity.x
    self.position.y += self.velocity.y
    self.normalize_position()

  def normalize_position(self):
    global width
    global height
    self.position.x -= math.floor(self.position.x/width)*width
    self.position.y -= math.floor(self.position.y/height)*height

  def disabled(self):
    return self.disabled_counter > 0


def start():
  global screen
  global clock
  global quit
  global width
  global height
  global goals
  global seekers

  pygame.init()
  screen = pygame.display.set_mode((width, height))
  clock = pygame.time.Clock()

  quit = False
  goals = [random_goal() for _ in range(0, 3)]
  seekers = [Seeker(223.5, 115, 5, 0), Seeker(40, 49, 0, -5), Seeker(-1, 333, 0, 0)]

  main_loop()


def main_loop():
  global quit
  while not quit:
    handle_events()
    call_ais()
    game_logic()
    draw()
    clock.tick(50)  # 20ms relative to last tick

def handle_events():
  for e in pygame.event.get():
    handle_event(e)

def handle_event(e):
  if e.type == pygame.QUIT:
    global quit
    quit = True

def call_ais():
  call_ai(ai0)

def call_ai(ai):
  global seekers
  (own_seekers, goals, other_players) = prepareAIInput(None)
  new_seekers = []
  try:
    new_seekers = ai(own_seekers, goals, other_players)
  except Exception:
    pass
  if (isinstance(new_seekers, list)):
    for i in range(0, min(len(new_seekers), len(seekers))):
      if (isinstance(new_seekers[i], Seeker)):
        if (isinstance(new_seekers[i].target, Vector)):
          seekers[i].target = new_seekers[i].target

def prepareAIInput(player_id):
  global seekers
  global goals
  return (copy.deepcopy(seekers), copy.deepcopy(goals), [])

def game_logic():
  for s in seekers:
    s.move()
    if (s.disabled_counter>0):
      s.disabled_counter -= 1
  for i in range(0, len(seekers)):
    s = seekers[i]
    for j in range(i+1, len(seekers)):
      t = seekers[j]
      if (t.position - s.position).norm() < Seeker.radius*2:
        s_copy = copy.deepcopy(s)
        seeker_collided(s, t)
        seeker_collided(t, s_copy)
  for s in seekers:
    if (not s.disabled()):
      for i in range(0, len(goals)):
        if (goals[i].position - s.position).norm() < Seeker.radius + Goal.radius:
          goal_scored(i)

def seeker_collided(s, t):
  # disable the seeker
  s.disabled_counter = Seeker.disabled_time
  # bounce off the other seeker
  d = t.position - s.position
  if (d.norm() != 0):
    dn = d.normalized()
    dv = t.velocity - s.velocity
    dvdn = dv.dot(dn)
    if (dvdn < 0):
      s.velocity += dn * dvdn
    ddn = d.dot(dn)
    if (ddn < Seeker.radius*2):
      s.position += dn * (ddn - Seeker.radius*2)

def goal_scored(goal_index):
  goals[goal_index] = random_goal()

def random_goal():
  return Goal(random.uniform(0, width), random.uniform(0, height))

def draw():
  global screen
  global goals
  global seekers
  screen.fill((0, 0, 0))
  for g in goals:
    drawItem((255, 200, 0), g.position, Goal.radius)
  for s in seekers:
    color = (20, 200, 0)
    if (s.disabled()):
      color = (10, 100, 0)
    drawItem(color, s.position, Seeker.radius)
  pygame.display.flip()

def drawItem(color, center, radius):
  global screen
  for ix in [-1, 0, 1]:
    for iy in [-1, 0, 1]:
      pygame.draw.circle(screen, color,
        (int(center.x+ix*screen.get_rect().w), int(center.y+iy*screen.get_rect().h)), radius)


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


start()
