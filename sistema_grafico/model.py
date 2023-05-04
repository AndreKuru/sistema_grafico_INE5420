from dataclasses import dataclass
from typing import Protocol
from copy import deepcopy

from numpy import double, dot
from enum import Enum


class Color(Enum):
    BLACK = "Black"
    RED = "Red"
    GREEN = "Green"
    BLUE = "Blue"
    CYAN = "Cyan"
    YELLOW = "Yellow"
    MAGENTA = "Magenta"

WINDOW_NDC_MIN = -1
WINDOW_NDC_MAX = 1


@dataclass
class Coordinates:
    x: int | double | float
    y: int | double | float

    def __add__(self, other: "Coordinates"):
        x = self.x + other.x
        y = self.y + other.y
        return Coordinates(x, y)

    def __sub__(self, other: "Coordinates"):
        x = self.x - other.x
        y = self.y - other.y
        return Coordinates(x, y)

    def multiply_scalar(self, other: int | double | float):
        self.x = self.x * (other)
        self.y = self.y * (other)


@dataclass
class Area2d:
    min: Coordinates
    max: Coordinates

    def size(self):
        return self.max - self.min

    def move(self, movement: Coordinates):
        self.min = self.min + movement
        self.max = self.max + movement

    def zoom(self, ammount: float):
        self.max.multiply_scalar(1 + ammount)


class Drawer(Protocol):
    def draw_point(self, coordinates: Coordinates):
        ...

    def draw_line(self, endpoint1: Coordinates, endpoint2: Coordinates):
        ...


def transform(coordinates: Coordinates, matrix: list[list[int | double | float]]):
    p = (coordinates.x, coordinates.y, 1)
    new_p = dot(p, matrix)
    return Coordinates(new_p[0], new_p[1])


class Drawable(Protocol):
    color: Color

    def draw(self, drawer: Drawer):
        ...

    def transform(self, matrix: list[list[int | double | float]]):
        ...

    def calculate_center(self):
        ...
    
    def clip_NDC(self):
        ...

@dataclass
class Point:
    coordinates: Coordinates
    color: Color = Color.BLACK

    def draw(self, drawer: Drawer):
        drawer.draw_point(self.coordinates, self.color)

    def transform(self, matrix: list[list[int | double | float]]):
        self.coordinates = transform(self.coordinates, matrix)

    def calculate_center(self):
        center = self.coordinates
        return center
    
    def clip_NDC(self): #-> Point | None:
        if (
            self.coordinates.x > WINDOW_NDC_MIN
            and self.coordinates.x < WINDOW_NDC_MAX
            and self.coordinates.y > WINDOW_NDC_MIN
            and self.coordinates.y < WINDOW_NDC_MAX
        ):
            return deepcopy(self)

        return None


@dataclass
class Line:
    endpoint1: Coordinates
    endpoint2: Coordinates
    color: Color = Color.BLACK

    def draw(self, drawer: Drawer):
        drawer.draw_line(self.endpoint1, self.endpoint2, self.color)

    def transform(self, matrix: list[list[int | double | float]]):
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
    color: Color = Color.BLACK

    def draw(self, drawer: Drawer):
        if len(self.vertexes) > 2:
            for i in range(len(self.vertexes) - 1):
                drawer.draw_line(self.vertexes[i], self.vertexes[i + 1], self.color)
            drawer.draw_line(self.vertexes[-1], self.vertexes[0], self.color)

    def transform(self, matrix: list[list[int | double | float]]):
        new_vertexes = list()
        for vertex in self.vertexes:
            new_vertexes.append(transform(vertex, matrix))
        self.vertexes = new_vertexes

    def calculate_center(self):
        center_x = 0
        center_y = 0
        for vertex in self.vertexes:
            center_x += vertex.x
            center_y += vertex.y
        center_x = center_x / len(self.vertexes)
        center_y = center_y / len(self.vertexes)
        center = Coordinates(center_x, center_y)
        return center
