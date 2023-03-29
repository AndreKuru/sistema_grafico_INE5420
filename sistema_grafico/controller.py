from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from model import Coordinates, Point, Line, Wireframe, Drawable

if TYPE_CHECKING:
    from view import Graphic_Viewer

@dataclass
class Controller:
    _display_file: list[Drawable] = field(default_factory=list)
    _drawer: Optional["Graphic_Viewer"] = None

    def set_drawer(self, drawer: Graphic_Viewer):
        self._drawer = drawer

    def create_point(self, x: int, y: int):
        name = "Point1"
        point = Point(name, Coordinates(x, y))
        self._display_file.append(point)
        self._drawer.insert_drawable(point)
        self.redraw()

    def create_line(self, x1: int, y1: int, x2: int, y2: int):
        name = "Line1"
        endpoint1 = Coordinates(x1, y1)
        endpoint2 = Coordinates(x2, y2)
        line = Line(name, endpoint1, endpoint2)
        self._display_file.append(line)
        self._drawer.insert_drawable(line)
        self.redraw()

    def create_wireframe(self, list_x: list(int), list_y: list(int)):
        name = "Wireframe1"
        coordinates = list()
        for i in range(len(list_x)):
            coordinate = Coordinates(list_x[i], list_y[i])
            coordinates.append(coordinate)
        wireframe = Wireframe(name, coordinates)
        self._display_file.append(wireframe)
        self._drawer.insert_drawable(wireframe)
        self.redraw()
            
    def redraw(self):
        self._drawer.clear()
        for drawable in self._display_file:
            drawable.draw(self._drawer)