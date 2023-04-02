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

def transform(coordinates: Coordinates, matrix: list[list[int|double|float]]):
    p = (coordinates.x, coordinates.y, 1)
    new_p = dot(p, matrix)
    return Coordinates(new_p[0], new_p[1])

class Drawable(Protocol):
    def draw(self, drawer: Drawer):
        ...

    def transform(self, matrix: list[list[int|double|float]]):
        ...

    def calculate_center(self):
        ...

@dataclass
class Point:
    coordinates: Coordinates

    def draw(self, drawer: Drawer):
        drawer.draw_point(self.coordinates)

    def transform(self, matrix: list[list[int|double|float]]):
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

    def transform(self, matrix: list[list[int|double|float]]):
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

    def transform(self, matrix: list[list[int|double|float]]):
        new_vertexes = list()
        for vertex in self.vertexes:
            new_vertexes.append(transform(vertex, matrix))
        self.vertexes = new_vertexes

    # All functions below implement the centroid calculus

    def calculate_common_elements(self, i: int):
        actual_vertex = self.vertexes[i]
        next_vertex = self.vertexes[i+1]
        common_expression = (
            (actual_vertex.x * next_vertex.y) - (next_vertex.x * actual_vertex.y))

        return actual_vertex, next_vertex, common_expression

    def calculate_wireframe_signed_area(self):
        shoelace_sum = 0
    
        for i in range(len(self.vertexes) - 1):
            actual_vertex, next_vertex, common_expression = self.calculate_common_elements(i)
            shoelace_sum += common_expression
        
        wireframe_signed_area = shoelace_sum * 0.5

        return wireframe_signed_area

    def calculate_center(self):
        center_x = 0
        center_y = 0
        
        for i in range(len(self.vertexes) - 1):
            actual_vertex, next_vertex, common_expression = self.calculate_common_elements(i)

            center_x += (actual_vertex.x + next_vertex.x) * common_expression
            center_y += (actual_vertex.y + next_vertex.y) * common_expression

        center_x = center_x / (6 * self.calculate_wireframe_signed_area())
        center_y = center_y / (6 * self.calculate_wireframe_signed_area())

        return Coordinates(center_x, center_y)
