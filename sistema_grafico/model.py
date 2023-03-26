from dataclasses import dataclass
from typing import Protocol, TypeVar

Number = TypeVar("Number", float, int)

WCoords: TypeAlias = Vector[float]
VPCoords: TypeAlias = Vector[int]

@dataclass(frozen=True)
class Vector(Generic[Number]):
    x: Number
    y: Number

    def __add__(self, vector: "Vector[Number]") -> "Vector[Number]":
        return Vector(self.x + vector.x, self.y + vector.y)
    
    def __sub__(self, vector: "Vector[Number]") -> "Vector[Number]":
        return Vector(self.x - vector.x, self.y - vector.y)

    def __mul__(self, vector: "Vector[Number]") -> "Vector[Number]":
        return Vector(self.x * vector.x, self.y * vector.y)

class Drawer(Protocol):
    def draw_point(self, point: WCoords) -> None:
        ...

    def draw_line(self, endpoint1: WCoords, endpoint2: WCoords) -> None:
        ...

class Object(Protocol):
    name: str

    def draw(self, drawer: Drawer) -> None:
        ...

@dataclass
class Point:
    name: str
    Wcoords: WCoords

    def draw_point(self, drawer: Drawer) -> None:
        drawer.draw_point(self.Wcoords)

@dataclass
class Line:
    name: str
    endpoint1: WCoords
    endpoint2: WCoords

    def draw(self, drawer: Drawer) -> None:
        drawer.draw_line(self.endpoint1, self.endpoint2)

@dataclass
class Wireframe:
    name: str
    vertexes: list[Coord]

    def draw(self, drawer: Drawer) -> None:
        if len(self.vertexes) < 2:
            return
        
        prev_vertex = self.vertexes[-1]
        for vertex in self.vertexes:
            drawer.draw_line(prev_vertex, vertex)
            prev_vertex = vertex
        