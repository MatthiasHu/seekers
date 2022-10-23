import abc
from collections import defaultdict

from .hash_color import *

import dataclasses
from typing import Callable
import math
import random

_IDS = defaultdict(list)


def get_id(obj: str):
    while (id_ := random.randint(0, 2 ** 32)) in _IDS[obj]:
        ...

    _IDS[obj].append(id_)

    return f"py-seekers.{obj}@{id_}"


class Vector:
    def __init__(self, x: float = 0, y: float = 0):
        self.x = x
        self.y = y

    @staticmethod
    def from_polar(angle: float, radius: float = 1) -> "Vector":
        return Vector(math.cos(angle) * radius, math.sin(angle) * radius)

    def rotated(self, angle: float) -> "Vector":
        return Vector(
            math.cos(angle) * self.x - math.sin(angle) * self.y,
            math.sin(angle) * self.x + math.cos(angle) * self.y,
        )

    def is_vector(obj) -> bool:
        return isinstance(obj, Vector)

    def __iter__(self):
        return iter((self.x, self.y))

    def __getitem__(self, i: int):
        if i == 0:
            return self.x
        elif i == 1:
            return self.y
        else:
            raise IndexError

    def __add__(self, other: "Vector"):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vector"):
        return Vector(self.x - other.x, self.y - other.y)

    def __neg__(self):
        return self * (-1)

    def __mul__(self, factor):
        return Vector(self.x * factor, self.y * factor)

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, divisor):
        return self * (1 / divisor)

    def __rtruediv__(self, other):
        if other == 1:
            return Vector(1 / self.x, 1 / self.y)

        return 1 / self * other

    def __bool__(self):
        return self.x or self.y

    def dot(self, other: "Vector") -> float:
        return self.x * other.x + self.y * other.y

    def squared_length(self) -> float:
        return self.x * self.x + self.y * self.y

    def length(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y)

    def normalized(self):
        norm = self.length()
        if norm == 0:
            return Vector(0, 0)
        else:
            return Vector(self.x / norm, self.y / norm)

    def map(self, func: Callable[[float], float]) -> "Vector":
        return Vector(func(self.x), func(self.y))

    def __repr__(self):
        return f"Vector({self.x}, {self.y})"

    def __format__(self, format_spec):
        return f"Vector({self.x:{format_spec}}, {self.y:{format_spec}})"


class Physical:
    mass = 1
    friction = 0.02
    max_speed = 5
    base_thrust = max_speed * friction

    def __init__(self, id_: str, position: Vector, velocity: Vector):
        self.id = id_
        self.position = position
        self.velocity = velocity
        self.acceleration = Vector(0, 0)

    def update_acceleration(self, world: "World") -> Vector:
        ...

    def move(self, world: "World"):
        # friction
        self.velocity *= 1 - self.friction

        # acceleration
        self.update_acceleration(world)
        self.velocity += self.acceleration * self.thrust()

        # displacement
        self.position += self.velocity

        world.normalize_position(self.position)

    def thrust(self):
        return self.base_thrust

    def collision(self, other: "Physical", world: "World", min_dist: float):
        # elastic collision
        d = world.torus_difference(self.position, other.position)
        if d.length() != 0:
            dn = d.normalized()
            dv = other.velocity - self.velocity
            m = 2 / (self.mass + other.mass)

            dvdn = dv.dot(dn)
            if dvdn < 0:
                self.velocity += dn * (m * other.mass * dvdn)
                other.velocity -= dn * (m * self.mass * dvdn)

            ddn = d.dot(dn)
            if ddn < min_dist:
                self.position += dn * (ddn - min_dist)
                other.position -= dn * (ddn - min_dist)


class Goal(Physical):
    mass = 0.5
    radius = 6
    scoring_time = 150

    def __init__(self, id_: str, position, velocity=Vector(0, 0)):
        super().__init__(id_, position, velocity)
        self.position = Vector(position.x, position.y)
        self.velocity = Vector(velocity.x, velocity.y)
        self.acceleration = Vector(0, 0)
        self.owner = None
        self.owned_for = 0

    def camp_tick(self, camp):
        if camp.contains(self.position):
            if self.owner == camp.owner:
                self.owned_for += 1
            else:
                self.owned_for = 0
                self.owner = camp.owner
            return self.owned_for >= self.scoring_time
        else:
            return False


class Magnet:
    def __init__(self, strength=0):
        self.strength = strength

    def is_magnet(obj):
        typ = isinstance(obj, Magnet) and isinstance(obj.strength, int)
        val = 1 >= obj.strength >= -8
        return typ and val

    def is_on(self):
        # TODO: to property
        return not self.strength == 0

    def set_repulsive(self):
        self.strength = -8

    def set_attractive(self):
        self.strength = 1

    def disable(self):
        self.strength = 0


class Seeker(Physical):
    radius = 10
    magnet_slowdown = 0.2
    disabled_time = 250
    alterables = (('target', Vector.is_vector),
                  ('magnet', Magnet.is_magnet))

    def __init__(self, id_: str, position, velocity=Vector(0, 0)):
        super().__init__(id_, position, velocity)
        self.target = self.position
        self.disabled_counter = 0
        self.magnet = Magnet()

    @property
    def is_disabled(self):
        return self.disabled_counter > 0

    def disable(self):
        self.disabled_counter = Seeker.disabled_time

    def update_acceleration(self, world):
        if self.disabled_counter == 0:
            a = world.torus_direction(self.position, self.target)
            self.acceleration = a
        else:
            self.acceleration = Vector(0, 0)

    def thrust(self):
        b = self.magnet_slowdown if self.magnet.is_on() else 1
        return Physical.thrust(self) * b

    def collision(self, other: "Seeker", world, min_dist):
        if self.magnet.is_on():
            self.disable()
        if other.magnet.is_on():
            other.disable()

        if not (self.magnet.is_on() or other.magnet.is_on()):
            self.disable()
            other.disable()

        Physical.collision(self, other, world, min_dist)

    def copy_alterables(src, dest) -> bool:
        for attr, is_valid in Seeker.alterables:
            fallback = getattr(dest, attr)
            val = getattr(src, attr, fallback)
            if is_valid(val):
                setattr(dest, attr, val)
            else:
                return False
        return True

    def set_magnet_repulsive(self):
        self.magnet.set_repulsive()

    def set_magnet_attractive(self):
        self.magnet.set_attractive()

    def disable_magnet(self):
        self.magnet.disable()

    def set_magnet_disabled(self):
        self.magnet.disable()

    def magnetic_force(self, world, pos: Vector) -> Vector:
        def bump(r) -> float:
            return math.exp(1 / (r ** 2 - 1)) if r < 1 else 0

        r = world.torus_distance(self.position, pos) / world.diameter()
        d = world.torus_direction(self.position, pos)

        return Vector(0, 0) if self.is_disabled else - d * (self.magnet.strength * bump(r * 10))


class ScoreAnimation:
    duration = 20

    def __init__(self, position, color):
        self.position = position
        self.age = 0
        self.color = color


DecideCallable = Callable[
    [list[Seeker], list[Seeker], list[Seeker], list[Goal], list["Player"], "Camp", list["Camp"], "World"],
    list[Seeker]
]


@dataclasses.dataclass
class PlayerAI(abc.ABC):
    filepath: str
    timestamp: float
    decide_function: DecideCallable


@dataclasses.dataclass
class Player:
    id: str
    name: str
    ai: PlayerAI
    score: int = dataclasses.field(default=0)
    seekers: list[Seeker] = dataclasses.field(default_factory=list)

    @property
    def color(self):
        return string_hash_color(self.name)


class World:
    def __init__(self, width, height, debug_mode=True):
        self.width = width
        self.height = height
        self.debug_mode = debug_mode

    def normalize_position(self, pos: Vector):
        pos.x -= math.floor(pos.x / self.width) * self.width
        pos.y -= math.floor(pos.y / self.height) * self.height

    @property
    def geometry(self) -> Vector:
        return Vector(self.width, self.height)

    def diameter(self):
        return self.geometry.length()

    def middle(self) -> Vector:
        return self.geometry / 2

    def torus_distance(self, left: Vector, right: Vector, /) -> float:
        def dist1d(l, a, b):
            delta = abs(a - b)
            return min(delta, l - delta)

        return Vector(dist1d(self.width, right.x, left.x),
                      dist1d(self.height, right.y, left.y)).length()

    def torus_difference(self, left: Vector, right: Vector, /) -> Vector:
        def diff1d(l, a, b):
            delta = abs(a - b)
            return b - a if delta < l - delta else a - b

        return Vector(diff1d(self.width, left.x, right.x)
                      , diff1d(self.height, left.y, right.y))

    def torus_direction(self, left: Vector, right: Vector, /) -> Vector:
        return self.torus_difference(left, right).normalized()

    def index_of_nearest(self, pos: Vector, positions: list) -> int:
        d = self.torus_distance(pos, positions[0])
        j = 0
        for i, p in enumerate(positions[1:]):
            dn = self.torus_distance(pos, p)
            if dn < d:
                d = dn
                j = i + 1
        return j

    def nearest_goal(self, pos: Vector, goals: list) -> Goal:
        i = self.index_of_nearest(pos, [g.position for g in goals])
        return goals[i]

    def nearest_seeker(self, pos: Vector, seekers: list) -> Seeker:
        i = self.index_of_nearest(pos, [s.position for s in seekers])
        return seekers[i]

    def random_position(self) -> Vector:
        return Vector(random.uniform(0, self.width),
                      random.uniform(0, self.height))

    def gen_camp(self, n, i, player: Player):
        r = self.diameter() / 4
        width = height = r / 5

        pos = self.middle() + Vector.from_polar(2 * math.pi * i / n) * r
        return Camp(get_id("Camp"), player, pos, width, height)

    def generate_camps(self, players) -> list:
        n = len(players)
        return [self.gen_camp(n, i, p) for i, p in enumerate(players)]


@dataclasses.dataclass
class Camp:
    id: str
    owner: Player
    position: Vector
    width: float
    height: float

    def contains(self, pos: Vector) -> bool:
        delta = self.position - pos
        return 2 * abs(delta.x) < self.width and 2 * abs(delta.y) < self.height
