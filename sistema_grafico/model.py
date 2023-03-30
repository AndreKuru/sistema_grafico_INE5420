from dataclasses import dataclass
from typing import Protocol

from numpy import double, dot

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

    def add_scalar (self, other: int|double|float):
        self.x = self.x + other
        self.y = self.y + other

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
        self.max.add_scalar(ammount)

class Drawer(Protocol):
    def draw_point(self, coordinates: Coordinates):
        ...

    def draw_line(self, endpoint1: Coordinates, endpoint2: Coordinates):
        ...

def transform(coordinates: Coordinates, matrix: tuple[tuple[int|float|double]]):
    p = (coordinates.x, coordinates.y, 1)
    new_p = dot(p, matrix)
    return Coordinates(new_p[0], new_p[1])

class Drawable(Protocol):
    def draw(self, drawer: Drawer):
        ...

    def transform(self, matrix: tuple[tuple[int|float|double]]):
        ...

    def calculate_center(self):
        ...

@dataclass
class Point:
    coordinates: Coordinates

    def draw(self, drawer: Drawer):
        drawer.draw_point(self.coordinates)

    def transform(self, matrix: tuple[tuple[int|float|double]]):
        self.coordinates = transform(self.coordinates, matrix)

    def calculate_center(self):
        center = self.coordinates
        return center

@dataclass
class Line:
    endpoint1: Coordinates
    endpoint2: Coordinates

    def draw(self, drawer: Drawer):
        drawer.draw_line(self.endpoint1, self.endpoint2)

    def transform(self, matrix: tuple[tuple[int|float|double]]):
        self.endpoint1 = transform(self.endpoint1, matrix)
        self.endpoint2 = transform(self.endpoint2, matrix)

    def calculate_center(self):
        x_center = (self.endpoint1.x + self.endpoint2.x) / 2
        y_center = (self.endpoint1.y + self.endpoint2.y) / 2
        center = Coordinates(x_center, y_center)
        return center

@dataclass
class Wireframe:
    vertexes: list[Coordinates]

    def draw(self, drawer: Drawer):
        if len(self.vertexes) > 2:
            for i in range(len(self.vertexes)-1):
                drawer.draw_line(self.vertexes[i], self.vertexes[i+1])
            drawer.draw_line(self.vertexes[-1], self.vertexes[0])

    def transform(self, matrix: tuple[tuple[int|float|double]]):
        for vertex in self.vertexes:
            vertex = transform(vertex, matrix)
