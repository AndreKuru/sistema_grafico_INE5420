from dataclasses import dataclass
from typing import Protocol

from numpy import double

@dataclass
class Coordinates:
    x: int|double|float
    y: int|double|float

    def __add__ (self, other: "Coordinates"):
        x = self.x + other.x
        y = self.y + other.y
        return Coordinates(x, y)

    def __sub__ (self, other: "Coordinates"):
        x = self.x - other.x
        y = self.y - other.y
        return Coordinates(x, y)

@dataclass
class Area2d:
    min: Coordinates
    max: Coordinates

    def size():
        return max - min

    def move(self, movement: Coordinates):
        self.min = self.min + movement
        self.max = self.max + movement

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

    def draw(self, drawer: Drawer):
        if len(self.vertexes) > 2:
            for i in range(len(self.vertexes)-1):
                drawer.draw_line(self.vertexes[i], self.vertexes[i+1])
            drawer.draw_line(self.vertexes[-1], self.vertexes[0])