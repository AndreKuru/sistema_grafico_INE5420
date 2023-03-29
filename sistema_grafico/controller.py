from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from model import Coordinates, Point, Line, Wireframe, Drawable, Area2d

if TYPE_CHECKING:
    from view import Graphic_Viewer

@dataclass
class Controller:
    _display_file: list[Drawable] = field(default_factory=list)
    _drawer: Optional["Graphic_Viewer"] = None
    _world_window: Area2d = Area2d(Coordinates(0, 0), Coordinates(1000, 1000))
    _window: Area2d = Area2d(Coordinates(0, 0), Coordinates(1000, 1000))

    def transform_window_to_viewport(self, drawable_in_window: Coordinates):
        x_w_max = self._window.max.x
        x_w_min = self._window.min.x
        x_vp_max = self._drawer._viewport.max.x
        x_vp_min = self._drawer._viewport.min.x

        y_w_max = self._window.max.y
        y_w_min = self._window.min.y
        y_vp_max = self._drawer._viewport.max.y
        y_vp_min = self._drawer._viewport.min.y

        viewport_x = (drawable_in_window.x - x_w_min) / (x_w_max - x_w_min) * (x_vp_max - x_vp_min)
        viewport_y = (1 - ((drawable_in_window.y - y_w_min)/(y_w_max - y_w_min))) * (y_vp_max - y_vp_min)

        viewport_coordinates = Coordinates(int(viewport_x), int(viewport_y))

        return viewport_coordinates

    def transform_viewport_to_window(self, viewport_coordinates: Coordinates):
        x_w_max = self._window.max.x
        x_w_min = self._window.min.x
        x_vp_max = self._drawer._viewport.max.x
        x_vp_min = self._drawer._viewport.min.x

        y_w_max = self._window.max.y
        y_w_min = self._window.min.y
        y_vp_max = self._drawer._viewport.max.y
        y_vp_min = self._drawer._viewport.min.y

        window_x = viewport_coordinates.x * ((x_w_max - x_w_min)/(x_vp_max - x_vp_min)) + x_w_min 
        window_y = (1 - (viewport_coordinates.y/(y_vp_max - y_vp_min))) * (y_w_max - y_w_min) + y_w_min

        window_coordinates = Coordinates(window_x, window_y)

        return window_coordinates

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