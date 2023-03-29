from dataclasses import dataclass
from typing import Protocol

from numpy import double

@dataclass
class Coordinates:
    x: int|double
    y: int|double

class Drawer(Protocol):
    def draw_point(self, coordinates: Coordinates):
        ...

    def draw_line(self, endpoint1: Coordinates, endpoint2: Coordinates):
        ...

class Drawable(Protocol):
    name: str

    def draw(self, drawer: Drawer):
        ...

@dataclass
class Point:
    name: str
    coordinates: Coordinates

    def draw(self, drawer: Drawer):
        drawer.draw_point(self.coordinates)

@dataclass
class Line:
    name: str
    endpoint1: Coordinates
    endpoint2: Coordinates

    def draw(self, drawer: Drawer):
        drawer.draw_line(self.endpoint1, self.endpoint2)

@dataclass
class Wireframe:
    name: str
    vertexes: list[Coordinates]
