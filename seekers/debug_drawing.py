import abc
import dataclasses
import typing
from contextvars import ContextVar
import pygame


@dataclasses.dataclass
class DebugDrawing(abc.ABC):
    @abc.abstractmethod
    def draw(self, surface: pygame.Surface):
        ...


from seekers import Vector


@dataclasses.dataclass
class TextDebugDrawing(DebugDrawing):
    text: str
    position: Vector

    def draw(self, surface: pygame.Surface):
        font = pygame.font.SysFont("monospace", 15)
        label = font.render(self.text, True, (255, 255, 255))
        surface.blit(label, tuple(self.position))


@dataclasses.dataclass
class LineDebugDrawing(DebugDrawing):
    start: Vector
    end: Vector

    def draw(self, surface: pygame.Surface):
        pygame.draw.line(surface, (255, 255, 255), tuple(self.start), tuple(self.end), 2)


@dataclasses.dataclass
class CircleDebugDrawing(DebugDrawing):
    position: Vector
    radius: float

    def draw(self, surface: pygame.Surface):
        pygame.draw.circle(surface, (255, 255, 255), tuple(self.position), self.radius, width=2)


def draw_text(text: str, position: Vector):
    add_debug_drawing_func_ctxtvar.get()(TextDebugDrawing(text, position))


def draw_line(start: Vector, end: Vector):
    add_debug_drawing_func_ctxtvar.get()(LineDebugDrawing(start, end))


def draw_circle(position: Vector, radius: float):
    add_debug_drawing_func_ctxtvar.get()(CircleDebugDrawing(position, radius))


add_debug_drawing_func_ctxtvar: \
    ContextVar[typing.Callable[[DebugDrawing], None]] = ContextVar("add_debug_drawing_func", default=lambda _: None)
