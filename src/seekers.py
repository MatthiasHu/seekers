from seekers_types import *
import game_logic
from game_logic import random_position
import draw
from ais import *

import pygame
import sys
import copy
import random


speedup_factor = 1
screen = None
quit = False
clock = None
font = None
world = World(768, 768)
goals = []
players = []
ais = []
animations = {"score": []}


def start():
  global screen
  global clock
  global quit
  global world
  global goals
  global players
  global ais

  pygame.init()
  screen = pygame.display.set_mode((world.width, world.height))
  clock = pygame.time.Clock()
  random.seed()

  # initialize goals
  goals = [Goal(random_position(world)) for _ in range(0, 3)]

  # find ais and initialize players
  players = []
  ais = []
  ai_prefix = "ais."
  for m in sys.modules:
    if ( m[:len(ai_prefix)] == ai_prefix
         and hasattr(sys.modules[m], "decide") ):
      name = m[len(ai_prefix):]
      p = Player(name)
      p.seekers = [Seeker(random_position(world)) for _ in range(0, 3)]
      players.append(p)
      ais.append(sys.modules[m].decide)

  # prepare graphics
  draw.init(players)

  quit = False
  main_loop()

def main_loop():
  global speedup_factor
  global quit
  global players
  global goals
  global world
  global animations
  global screen

  while not quit:
    handle_events()
    for _ in range(speedup_factor):
      call_ais()
      game_logic.tick(players, goals, animations, world)
    draw.draw(players, goals, animations, world, screen)
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
  global ais
  for player,ai in zip(players,ais):
    call_ai(player,ai)

def call_ai(player, ai):
  own_seekers, goals, other_players = prepare_ai_input(player)
  new_seekers = []
  try:
    new_seekers = ai(own_seekers, goals, other_players)
  except Exception as e:
      print(  "The AI of Player "
            + player.name
            + " raised an exception." )
  if isinstance(new_seekers, list):
    for new, original in zip(new_seekers, player.seekers):
      if isinstance(new, Seeker):
        if isinstance(new.target, Vector):
          original.target = new.target

def prepare_ai_input(player):
  global players
  global goals
  i = players.index(player)
  other_players = copy.deepcopy(players)
  other_players.pop(i)
  return ( copy.deepcopy(player.seekers)
         , copy.deepcopy(goals)
         , other_players )


start()
