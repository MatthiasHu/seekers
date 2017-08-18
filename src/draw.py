from seekers_types import *

import pygame
import random


player_name_images = {}
font = None


def init(players):
  global font
  global name_images

  font = pygame.font.SysFont("monospace", 20, bold=True)

  for p in players:
    player_name_images[p.name] = font.render(p.name, True, p.color)
    

def draw(players, camps, goals, animations, world, screen):
  # clear screen
  screen.fill([0, 0, 30])
  # draw camps
  draw_camps(camps, screen)
  # draw goals
  for g in goals:
    draw_item([255, 200, 0], g.position, Goal.radius, world, screen)
  # draw jet streams
  for p in players:
    for s in p.seekers:
      a = world.torus_direction(s.position, s.target)
      if (not s.disabled() and a.norm()>0):
        draw_jet_stream(s.position, -a, world, screen)
  # draw seekers
  for p in players:
    for s in p.seekers:
      color = p.color
      if s.disabled():
        color = interpolate_color(color, [0, 0, 0], 0.5)
      if p.ai.is_dummy:
        color = interpolate_color(color, [1, 1, 1], 0.5)
      draw_item(color, s.position, Seeker.radius, world, screen)
  # draw animations
  for a in animations["score"]:
    draw_score_animation(a, world, screen)
  # draw player's scores
  draw_scores(players, screen)
  # actually update display
  pygame.display.flip()


def draw_camps(camps, screen):
  for camp in camps:
    x,y = camp.position.x, camp.position.y
    w = camp.width
    h = camp.height
    dx = w / 2
    dy = h / 2
    r = pygame.Rect( (x-dx,y-dy)
                   , (w, h) )
    color = camp.owner.color
    pygame.draw.rect(screen, color, r, 5)


def draw_item(color, center, radius, world, screen):
  for (dx, dy) in repetition_offsets(world):
    pygame.draw.circle(screen, color,
      (int(center.x+dx), int(center.y+dy)), radius)

def draw_jet_stream(origin, direction, world, screen):
  def line(a, b):
    for dx, dy in repetition_offsets(world):
      pygame.draw.line(screen, [255, 255, 255],
          (int(a.x+dx), int(a.y+dy))
        , (int(b.x+dx), int(b.y+dy)))

  for _ in range(0, 2):
    t = direction.rotated() * (random.uniform(-1, 1)
          * Seeker.radius * 0.3)
    l = Seeker.radius * (1 + math.exp(random.normalvariate(0.5, 0.2)))
    line(origin + t, origin + direction*l + t)

def draw_score_animation(a, world, screen):
  t = a.age / a.duration
  r = Goal.radius + 100*t
  for dx, dy in repetition_offsets(world):
    pygame.draw.circle(screen, a.color,
      (int(a.position.x+dx), int(a.position.y+dy)), int(r), 1)

def repetition_offsets(world):
  l = []
  for ix in [-1, 0, 1]:
    for iy in [-1, 0, 1]:
      l.append((ix*world.width, iy*world.height))
  return l

def draw_scores(players, screen):
  global name_images
  global font

  y = 10
  for p in players:
    screen.blit(font.render(str(p.score), False, p.color), (10, y))
    screen.blit(player_name_images[p.name], (50, y))
    y += 30
