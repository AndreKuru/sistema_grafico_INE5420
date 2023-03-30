from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from model import Coordinates, Point, Line, Wireframe, Drawable, Area2d
from math import sin, cos
from numpy import double, dot

if TYPE_CHECKING:
    from view import Graphic_Viewer

@dataclass
class Controller:
    _display_file: dict[Drawable] = field(default_factory=dict)
    _drawer: Optional["Graphic_Viewer"] = None
    _world_window: Area2d = Area2d(Coordinates(0, 0), Coordinates(1000, 1000))
    _window: Area2d = Area2d(Coordinates(0, 0), Coordinates(200, 200))

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

    def new_name(self, prefix: str):
        index = 1
        while True:
            name = prefix + str(index)
            if name not in self._display_file:
                break
            index += 1

        return name
        

    def create_point(self, x: int, y: int):
        name = self.new_name("Point")
        point = Point(Coordinates(x, y))
        self._display_file[name] = point
        self._drawer.insert_drawable(name)
        self.redraw()

    def create_line(self, x1: int, y1: int, x2: int, y2: int):
        name = self.new_name("Line")
        endpoint1 = Coordinates(x1, y1)
        endpoint2 = Coordinates(x2, y2)
        line = Line(endpoint1, endpoint2)
        self._display_file[name] = line
        self._drawer.insert_drawable(name)
        self.redraw()

    def create_wireframe(self, list_x: list(int), list_y: list(int)):
        name = self.new_name("Wireframe")
        coordinates = list()
        for i in range(len(list_x)):
            coordinate = Coordinates(list_x[i], list_y[i])
            coordinates.append(coordinate)
        wireframe = Wireframe(coordinates)
        self._display_file[name] = wireframe
        self._drawer.insert_drawable(name)
        self.redraw()
            
    def redraw(self):
        self._drawer.clear()
        for drawable in self._display_file.values():
            drawable.draw(self._drawer)

    def pan_window(self, movement: Coordinates):
        self._window.move(movement)
        self.redraw()

    def zoom(self, ammount: int):
        self._window.zoom(ammount)
        self.redraw()

    def translate_object(self, transformation: Coordinates):
        matrix = (
            (1,0,0),
            (0,1,0),
            (transformation.x,transformation.y,1)
            )
        return matrix

    # Not ready yet
    def scale_object(self, transformation: Coordinates):
        matrixes = list()
        drawable = self._display_file[name]
        center = drawable.calculate_center()
        translation_to_origin = Coordinates(0, 0) - center
        matrix = (
            (1,0,0),
            (0,1,0),
            (translation_to_origin.x,translation_to_origin.y,1)
            )
        matrixes.append(matrix)

        matrix = (
            (transformation.x,0,0),
            (0,transformation.y,0),
            (0,0,1)
            )
        matrixes = dot(matrixes, matrix)

        translation_back = center - Coordinates(0, 0)
        drawable.translate_object(translation_back)

    def rotate_object_around_origin(self, angle: float):
        matrix = (
            (cos(angle),-sin(angle),0),
            (sin(angle),cos(angle),0),
            (0,0,1)
            )
        return matrix

    def rotate_object(self, angle: float, center: str, name: str):
        match center:
            case "o":
                self.rotate_object_around_origin(angle)
            case "s":
                self.rotate_object_around_selected_object(angle, name)
            case "a":
                self.rotate_object_around_arbitrary_point(angle, position)

    def transform(self, name: str, transformations: list[tuple[str,int|float,str|int]]):
        drawable = self._display_file[name]
        for operation, op1, op2 in transformations:
            match operation:
                case "t":
                    self.translate_object(Coordinates(op1, op2))
                case "s":
                    self.scale_object(Coordinates(op1, op2))
                case "r":
                    self.rotate_object(op1, op2)