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

    def __add__ (self, other: int|double|float):
        x = self.x + other
        y = self.y + other
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

    def zoom(self, ammount: int):
        self.max = self.max + ammount

class Drawer(Protocol):
    def draw_point(self, coordinates: Coordinates):
        ...

    def draw_line(self, endpoint1: Coordinates, endpoint2: Coordinates):
        ...

class Drawable(Protocol):
    def draw(self, drawer: Drawer):
        ...

@dataclass
class Point:
    coordinates: Coordinates

    def draw(self, drawer: Drawer):
        drawer.draw_point(self.coordinates)

@dataclass
class Line:
    endpoint1: Coordinates
    endpoint2: Coordinates

    def draw(self, drawer: Drawer):
        drawer.draw_line(self.endpoint1, self.endpoint2)

@dataclass
class Wireframe:
    vertexes: list[Coordinates]

    def draw(self, drawer: Drawer):
        if len(self.vertexes) > 2:
            for i in range(len(self.vertexes)-1):
                drawer.draw_line(self.vertexes[i], self.vertexes[i+1])
            drawer.draw_line(self.vertexes[-1], self.vertexes[0])