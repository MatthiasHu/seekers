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
    draw_goal(g, world, screen)
  # draw jet streams
  for p in players:
    for s in p.seekers:
      a = s.acceleration
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
      draw_halo(s, color, screen)
  # draw animations
  for a in animations["score"]:
    draw_score_animation(a, world, screen)
  # draw player's scores
  draw_scores(players, screen)
  # actually update display
  pygame.display.flip()


def draw_goal(goal, world, screen):
  global font
  color = [205, 0, 250]
  pos = goal.position
  draw_item(color, pos, Goal.radius, world, screen)
  if world.debug_mode:
    screen.blit( font.render( str(goal.uid), False, color )
               , tuple(pos) )

def draw_halo(seeker, color, screen):
  if seeker.disabled():
    return

  mu = abs(math.sin((int(pygame.time.get_ticks() / 30) % 50) / 50 * 2 * math.pi))**2
  pygame.draw.circle(screen, interpolate_color(color, [0,0,0], mu),
      (int(seeker.position.x), int(seeker.position.y)), 3 + Seeker.radius, 3)

  if not seeker.magnet.is_on():
    return

  for offset in 0, 10, 20, 30, 40:
    mu = int(-seeker.magnet.strength * pygame.time.get_ticks() / 50 + offset) % 50
    pygame.draw.circle(screen, interpolate_color(color, [0,0,0], (mu) / 50),
      (int(seeker.position.x), int(seeker.position.y)), mu + Seeker.radius, 2)


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
