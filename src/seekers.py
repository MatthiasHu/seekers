from seekers_types import *
import game_logic
import draw
import sys
import os
import os.path
import glob
import imp
import traceback

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
camps = []
animations = {"score": []}
tournament_mode = False

def start():
  global screen
  global clock
  global quit
  global world
  global goals
  global players
  global camps

  pygame.init()
  screen = pygame.display.set_mode((world.width, world.height))
  clock = pygame.time.Clock()
  random.seed()

  # initialize goals
  goals = [Goal(world.random_position()) for _ in range(0, 3)]

  # find ais and initialize players
  players = []
  load_players()
  reset()

  # set up camps
  camps = world.generate_camps(players)

  # prepare graphics
  draw.init(players)

  quit = False
  main_loop()

def load_players():
  global players
  global tournament_mode

  if len(sys.argv) <= 1:
    for search_path in ("", "./src/ais/"):
      for filename in glob.glob(search_path + "ai*.py"):
        load_player(filename)
  else:
    for filename in sys.argv[1:]:
      load_player(filename)
    tournament_mode = True

def load_player(filename):
  name = filename[:-3]
  p    = Player(name)
  p.ai = load_ai(filename)
  players.append(p)

def load_ai(filename):
  def dummy_decide(mySeekers, goals, otherPlayers, world):
    for s in mySeekers:
      s.target = s.position
    return mySeekers

  def mogrify(code):
    if code.startswith("#bot"):
      lines = code.split("\n")
      lines[0] = "def decide(seekers, goals, otherPlayers, world):"
      for i in range(1,len(lines)):
        lines[i] = " " + lines[i]
      lines.append(" return seekers")
      return "\n".join(lines)
    else:
      return code

  try:
    with open(filename, "r") as f:
      code = mogrify(f.read())
      mod  = imp.new_module(filename[:-3])
      exec(code, mod.__dict__)
      ai = mod.decide
      ai.is_dummy = False
  except Exception:
    print("**********************************************************", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    print("", file=sys.stderr)

    ai = dummy_decide
    ai.is_dummy = True

  ai.filename  = filename
  ai.timestamp = os.path.getctime(filename)

  return ai

def reset():
  global players

  for p in players:
    p.seekers = [Seeker(world.random_position()) for _ in range(0, 3)]

def main_loop():
  global speedup_factor
  global quit
  global players
  global goals
  global world
  global animations
  global screen

  step = 0

  while not quit:
    handle_events()
    for _ in range(speedup_factor):
      call_ais()
      game_logic.tick(players, goals, animations, world)
    draw.draw(players, goals, animations, world, screen)
    clock.tick(50)  # 20ms relative to last tick

    step += 1
    if tournament_mode and step > 1000:
      best_player = sorted(players, key=lambda p: p.score, reverse=True)[0]
      print(best_player.ai.filename)
      quit = True

def handle_events():
  for e in pygame.event.get():
    handle_event(e)

def handle_event(e):
  if e.type == pygame.QUIT:
    global quit
    quit = True

def call_ais():
  global players
  global world

  for p in players:
    if os.path.getctime(p.ai.filename) > p.ai.timestamp:
      p.ai = load_ai(p.ai.filename)
    call_ai(p,copy.deepcopy(world))

def call_ai(player, world):
  def warn_invalid_data():
    print( "The AI of Player "
         + player.name
         + " returned invalid data" )
  own_seekers, goals, other_players = prepare_ai_input(player)
  new_seekers = sandboxed_ai_call( player
          , lambda: player.ai(own_seekers, goals, other_players, world) )
  if isinstance(new_seekers, list):
    for new, original in zip(new_seekers, player.seekers):
      if isinstance(new, Seeker):
        status = Seeker.copy_alterables(new,original)
        if not status: warn_invalid_data()
      else: warn_invalid_data()
  else: warn_invalid_data()

def sandboxed_ai_call(player, ai_call):
# block_stdio()
  try:
    res = ai_call()
  except Exception as e:
    restore_stdio()
    print(  "The AI of Player "
            + player.name
            + " raised an exception:" )
    print(e)
    return []
# restore_stdio()
  return res

class NullDevice():
  def write(self,s): pass

def block_stdio():
  sys.stdout = NullDevice()
  sys.stderr = NullDevice()

def restore_stdio():
  sys.stdout = sys.__stdout__
  sys.stderr = sys.__stderr__

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
