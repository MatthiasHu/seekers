import hashlib
import pygame
import math
import copy
import random


screen = None
quit = False
clock = None
width = 768
height = 768
goals = []
players = []

class Vector:
  def __init__(self, x=0, y=0):
    self.x = x
    self.y = y

  def __add__(left, right):
    return Vector(left.x+right.x, left.y+right.y)
  def __sub__(left, right):
    return Vector(left.x-right.x, left.y-right.y)
  def __neg__(self):
    return self*(-1)
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

  def rotated(self):
    return Vector(-self.y, self.x)

class Goal:
  radius = 15

  def __init__(self, position):
    self.position = Vector(position.x, position.y)

class Seeker:
  radius = 20
  friction = 0.02
  max_speed = 5
  thrust = max_speed * friction
  disabled_time = 100

  def __init__(self, position, velocity=Vector(0, 0)):
    self.position = Vector(position.x, position.y)
    self.velocity = Vector(velocity.x, velocity.y)
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

class Player:
  win_score = 100

  def __init__(self, name, ai):
    self.name = name
    self.color = string_hash_color(name)
    self.score = 0
    self.seekers = []
    self.ai = ai

def all_seekers():
  global players
  seekers = []
  for p in players:
    for s in p.seekers:
      seekers.append((p, s))
  return seekers

def string_hash_color(string):
  original_state = random.getstate()
  random.seed(string.encode())
  hue = random.uniform(0, 1)
  random.setstate(original_state)
  return hue_color(hue)

# make a nice color from a hue given as a number between 0 and 1
def hue_color(hue):
  colors = [
      [255, 0, 0]
    , [255, 255, 0]
    , [0, 255, 0]
    , [0, 255, 255]
    , [0, 0, 255]
    , [255, 0, 255]
    , [255, 0, 0] ]
  n = len(colors)-1
  i = math.floor(hue*n)
  i = min(i, n-1)
  return interpolate_color(colors[i], colors[i+1], hue*n-i)

def interpolate_color(c1, c2, t):
  return [(1-t)*a + t*b for (a, b) in zip(c1, c2)]


def start():
  global screen
  global clock
  global quit
  global width
  global height
  global goals
  global players

  pygame.init()
  screen = pygame.display.set_mode((width, height))
  clock = pygame.time.Clock()
  random.seed()

  quit = False
  # initialize goals
  goals = [Goal(random_position()) for _ in range(0, 3)]
  # initialize players (and their seekers)
  players = []
  players.append(Player("player0", ai0))
  players.append(Player("player1", ai1))
  players.append(Player("player2", ai2))
  for p in players:
    p.seekers = [Seeker(random_position()) for _ in range(0, 3)]

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
  global players
  for p in players:
    call_ai(p)

def call_ai(player):
  (own_seekers, goals, other_players) = prepareAIInput(player)
  new_seekers = []
  try:
    new_seekers = player.ai(own_seekers, goals, other_players)
  except Exception:
    pass
  if (isinstance(new_seekers, list)):
    for (new, original) in zip(new_seekers, player.seekers):
      if (isinstance(new, Seeker)):
        if (isinstance(new.target, Vector)):
          original.target = new.target

def prepareAIInput(player):
  global players
  global goals
  i = players.index(player)
  other_players = copy.deepcopy(players)
  other_players.pop(i)
  return (copy.deepcopy(player.seekers), copy.deepcopy(goals), other_players)

def game_logic():
  seekers = [s for (_, s) in all_seekers()]
  # move and recover seekers
  for s in seekers:
    s.move()
    if (s.disabled()):
      s.disabled_counter -= 1
  # handle seeker collisions
  for i in range(0, len(seekers)):
    s = seekers[i]
    for j in range(i+1, len(seekers)):
      t = seekers[j]
      if (t.position - s.position).norm() < Seeker.radius*2:
        s_copy = copy.deepcopy(s)
        seeker_collided(s, t)
        seeker_collided(t, s_copy)
  # handle collisions of seekers with goals
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
  goals[goal_index] = Goal(random_position())

def random_position():
  return Vector(random.uniform(0, width), random.uniform(0, height))

def draw():
  global screen
  global goals
  # clear screen
  screen.fill([0, 0, 50])
  # draw goals
  for g in goals:
    drawItem((255, 200, 0), g.position, Goal.radius)
  # draw jet streams
  for (_, s) in all_seekers():
    a = (s.target - s.position).normalized()
    if (not s.disabled() and a.norm()>0):
      draw_jet_stream(s.position, -a)
  # draw seekers
  for (p, s) in all_seekers():
    color = p.color
    if (s.disabled()):
      color = interpolate_color(color, [0, 0, 0], 0.5)
    drawItem(color, s.position, Seeker.radius)
  # actually update display
  pygame.display.flip()

def drawItem(color, center, radius):
  global screen
  global width
  global height
  for ix in [-1, 0, 1]:
    for iy in [-1, 0, 1]:
      pygame.draw.circle(screen, color,
        ( int(center.x+ix*width)
        , int(center.y+iy*height) ), radius)

def draw_jet_stream(origin, direction):
  global screen
  global width
  global height

  def line(a, b):
    for ix in [-1, 0, 1]:
      for iy in [-1, 0, 1]:
        pygame.draw.line(screen, [255, 255, 255],
            (int(a.x+ix*width), int(a.y+iy*height))
          , (int(b.x+ix*width), int(b.y+iy*height)))

  for _ in range(0, 2):
    t = direction.rotated() * (random.uniform(-1, 1)
          * Seeker.radius * 0.3)
    l = Seeker.radius * (1 + math.exp(random.normalvariate(0.5, 0.2)))
    line(origin + t, origin + direction*l + t)


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

start()
