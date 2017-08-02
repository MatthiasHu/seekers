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
    

def draw(players, goals, world, screen):
  # clear screen
  screen.fill([0, 0, 30])
  # draw goals
  for g in goals:
    draw_item([255, 200, 0], g.position, Goal.radius, world, screen)
  # draw jet streams
  for p in players:
    for s in p.seekers:
      a = (s.target - s.position).normalized()
      if (not s.disabled() and a.norm()>0):
        draw_jet_stream(s.position, -a, world, screen)
  # draw seekers
  for p in players:
    for s in p.seekers:
      color = p.color
      if (s.disabled()):
        color = interpolate_color(color, [0, 0, 0], 0.5)
      draw_item(color, s.position, Seeker.radius, world, screen)
  # draw player's scores
  draw_scores(players, screen)
  # actually update display
  pygame.display.flip()

def draw_item(color, center, radius, world, screen):
  for ix in [-1, 0, 1]:
    for iy in [-1, 0, 1]:
      pygame.draw.circle(screen, color,
        ( int(center.x+ix*world.width)
        , int(center.y+iy*world.height) ), radius)

def draw_jet_stream(origin, direction, world, screen):
  def line(a, b):
    for ix in [-1, 0, 1]:
      for iy in [-1, 0, 1]:
        pygame.draw.line(screen, [255, 255, 255],
            (int(a.x+ix*world.width), int(a.y+iy*world.height))
          , (int(b.x+ix*world.width), int(b.y+iy*world.height)))

  for _ in range(0, 2):
    t = direction.rotated() * (random.uniform(-1, 1)
          * Seeker.radius * 0.3)
    l = Seeker.radius * (1 + math.exp(random.normalvariate(0.5, 0.2)))
    line(origin + t, origin + direction*l + t)

def draw_scores(players, screen):
  global name_images
  global font

  y = 10
  for p in players:
    screen.blit(font.render(str(p.score), False, p.color), (10, y))
    screen.blit(player_name_images[p.name], (50, y))
    y += 30
