# Copyright 2018 Matthias Hutzler
#
# This file is part of Seekers.
#
# Seekers is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Seekers is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Seekers.  If not, see <http://www.gnu.org/licenses/>.

from seekers_types import *

import random
import copy
import utils


def tick(players, camps, goals, animations, world):
  """

  :param players:
  :param camps:
  :param goals:
  :param animations:
  :param world:
  :return:
  """
  seekers = [s for p in players for s in p.seekers]
  # move and recover seekers
  for s in seekers:
    s.move(world)
    if s.disabled():
      s.disabled_counter -= 1
  # compute magnetic forces and move goals
  for g in goals:
    force = Vector(0,0)
    for s in seekers:
      force += s.magnetic_force(world,g.position)
    g.acceleration = force
    g.move(world)
  # handle collisions
  physicals = seekers + goals
  for i in range(0, len(physicals)):
    s = physicals[i]
    for j in range(i+1, len(physicals)):
      t = physicals[j]
      d = world.torus_distance(t.position,s.position)
      min_dist = s.radius + t.radius
      # ^ bit of a hack; will only work with seekers and goals
      if d < min_dist:
        if isinstance(s,Seeker) and isinstance(t,Seeker):
          Seeker.collision(s, t, world, min_dist)
        else:
          Physical.collision(s, t, world, min_dist)
  # handle goals and scoring
  for i,g in enumerate(goals):
    for camp in camps:
      if g.camp_tick(camp):
        goal_scored(g.owner, i, goals, animations, world)
        break
  # advance animations
  for _, animation_list in animations.items():
    for (i, a) in enumerate(animation_list):
      a.age += 1
      if a.age > a.duration:
        animation_list.pop(i)


def goal_scored(player, goal_index, goals, animations, world):
  player.score += 1
  g = goals[goal_index]
  goals[goal_index] = Goal(world.random_position())
  animations["score"].append(ScoreAnimation(g.position, player.color))



