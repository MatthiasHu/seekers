from seekers_types import *
import game_logic
from game_logic import random_position
import draw
from ais import *

import pygame
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
  # initialize players (and their seekers)
  players = []
  players.append(Player("player0"))
  players.append(Player("player1"))
  players.append(Player("player2"))
  for p in players:
    p.seekers = [Seeker(random_position(world)) for _ in range(0, 3)]
  ais = [ai0, ai1, ai2]
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
  global screen

  while not quit:
    handle_events()
    for _ in range(speedup_factor):
      call_ais()
      game_logic.tick(players, goals, world)
    draw.draw(players, goals, world, screen)
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
  for i in range(0, len(players)):
    call_ai(players[i], ais[i])

def call_ai(player, ai):
  (own_seekers, goals, other_players) = prepare_ai_input(player)
  new_seekers = []
  try:
    new_seekers = ai(own_seekers, goals, other_players)
  except Exception:
    pass
  if (isinstance(new_seekers, list)):
    for (new, original) in zip(new_seekers, player.seekers):
      if (isinstance(new, Seeker)):
        if (isinstance(new.target, Vector)):
          original.target = new.target

def prepare_ai_input(player):
  global players
  global goals
  i = players.index(player)
  other_players = copy.deepcopy(players)
  other_players.pop(i)
  return ( copy.deepcopy(player.seekers)
         , copy.deepcopy(goals)
         , other_players)


start()
