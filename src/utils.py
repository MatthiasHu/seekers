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

import math
import random
import copy

def foldr(f,a,xs):
  for x in xs:
    a = f(a,x)
  return a

def foldr1(f,xs):
  return foldr(f,xs[0],xs[1:])

def fmap(f,xs):
  return [f(x) for x in xs]


def flatten(nested):
  for xs in nested:
    for x in xs:
      yield x

def shuffled(xs):
  ys = copy.copy(xs)
  random.shuffle(ys)
  return ys

def bump(r):
  return math.exp(1 / (r**2 - 1)) if r < 1 else 0

def pop_split(xs,i):
  x = xs.pop(i)
  return (x,xs)

