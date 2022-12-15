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
    color: tuple[int, int, int] = (255, 255, 255)

    def draw(self, surface: pygame.Surface):
        font = pygame.font.SysFont("monospace", 15)
        label = font.render(self.text, True, self.color)
        surface.blit(label, tuple(self.position))


@dataclasses.dataclass
class LineDebugDrawing(DebugDrawing):
    start: Vector
    end: Vector
    color: tuple[int, int, int] = (255, 255, 255)
    width: int = 2

    def draw(self, surface: pygame.Surface):
        pygame.draw.line(surface, self.color, tuple(self.start), tuple(self.end), self.width)


@dataclasses.dataclass
class CircleDebugDrawing(DebugDrawing):
    position: Vector
    radius: float
    color: tuple[int, int, int] = (255, 255, 255)
    width: int = 2

    def draw(self, surface: pygame.Surface):
        pygame.draw.circle(surface, self.color, tuple(self.position), self.radius, self.width)


def draw_text(text: str, position: Vector, color: tuple[int, int, int] = (255, 255, 255)):
    add_debug_drawing_func_ctxtvar.get()(TextDebugDrawing(text, position, color))


def draw_line(start: Vector, end: Vector, color: tuple[int, int, int] = (255, 255, 255), width: int = 2):
    add_debug_drawing_func_ctxtvar.get()(LineDebugDrawing(start, end, color, width))


def draw_circle(position: Vector, radius: float, color: tuple[int, int, int] = (255, 255, 255), width: int = 2):
    add_debug_drawing_func_ctxtvar.get()(CircleDebugDrawing(position, radius, color, width))


add_debug_drawing_func_ctxtvar: \
    ContextVar[typing.Callable[[DebugDrawing], None]] = ContextVar("add_debug_drawing_func", default=lambda _: None)
