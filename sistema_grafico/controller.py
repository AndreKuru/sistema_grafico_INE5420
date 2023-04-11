from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from model import Coordinates, Point, Line, Wireframe, Drawable, Area2d, Color
from math import sin, cos, radians
from numpy import double, dot

if TYPE_CHECKING:
    from view import Graphic_Viewer

@dataclass
class Controller:
    _drawer: Optional["Graphic_Viewer"] = None
    _window: Area2d = Area2d(Coordinates(0, 0), Coordinates(200, 200))
    _display_file: dict[Drawable] = field(default_factory=dict)
    _display_file_NDC: dict[Drawable] = field(default_factory=dict)
    _transformation_NDC: list[list[int|double|float]] = field(default_factory=lambda:[[1,0,0],[0,1,0],[0,0,1]])

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

        viewport_x = viewport_x - self._window.max.x/2
        viewport_y = viewport_y - self._window.max.y/2

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
        

    def create_point(self, x: int, y: int, color: Color):
        name = self.new_name("Point")
        point = Point(Coordinates(x, y), color)
        self._display_file[name] = point
        self._drawer.insert_drawable(name)
        self.redraw()

    def create_line(self, x1: int, y1: int, x2: int, y2: int, color: Color):
        name = self.new_name("Line")
        endpoint1 = Coordinates(x1, y1)
        endpoint2 = Coordinates(x2, y2)
        line = Line(endpoint1, endpoint2, color)
        self._display_file[name] = line
        self._drawer.insert_drawable(name)
        self.redraw()

    def create_wireframe(self, list_x: list(int), list_y: list(int), color: Color):
        name = self.new_name("Wireframe")
        coordinates = list()
        for i in range(len(list_x)):
            coordinate = Coordinates(list_x[i], list_y[i])
            coordinates.append(coordinate)
        wireframe = Wireframe(coordinates, color)
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

    def zoom(self, ammount: float):
        self._window.zoom(ammount)
        self.redraw()

    def translate(self, transformation: Coordinates):
        matrix = (
            (1,0,0),
            (0,1,0),
            (transformation.x,transformation.y,1)
            )
        return matrix

    def scale(self, transformation: Coordinates, center: Coordinates):
        translation_to_origin = Coordinates(0, 0) - center
        resulting_matrix = self.translate(translation_to_origin)

        matrix = (
            (transformation.x,0,0),
            (0,transformation.y,0),
            (0,0,1)
            )
        resulting_matrix = dot(resulting_matrix, matrix)

        matrix = self.translate(center)
        resulting_matrix = dot(resulting_matrix, matrix)

        return resulting_matrix

    def rotate_around_origin(self, angle: float):
        matrix = (
            (cos(angle),-sin(angle),0),
            (sin(angle),cos(angle),0),
            (0,0,1)
            )
        return matrix

    def rotate_around_arbitrary_point(self, angle: float, position: Coordinates):
        translation_to_origin = Coordinates(0, 0) - position
        resulting_matrix = self.translate(translation_to_origin)

        matrix = self.rotate_around_origin(angle)
        resulting_matrix = dot(resulting_matrix, matrix)

        matrix = self.translate(position)
        resulting_matrix = dot(resulting_matrix, matrix)

        return resulting_matrix

    def rotate(self, angle: float, around: str, position: Coordinates):
        angle = radians(angle)

        match around:
            case "o":
                return self.rotate_around_origin(angle)
            case _:
                return self.rotate_around_arbitrary_point(angle, position)

    def transform(self, transformations: list[tuple[str,int|float,str|int],int|None,int|None], name: str):
        resulting_matrix = (
            (1,0,0),
            (0,1,0),
            (0,0,1)
            )
        drawable = self._display_file[name]

        center = drawable.calculate_center()
        center = Point(center)

        for i in range(len(transformations)):
            operation = transformations[i][0]
            op1 = transformations[i][1]
            op2 = transformations[i][2]
            match operation:
                case "t":
                    matrix = self.translate(Coordinates(op1, op2))
                case "s":
                    matrix = self.scale(Coordinates(op1, op2), center.coordinates)
                case "r":
                    if op2 == "a":
                        x = float(transformations[i][3])
                        y = float(transformations[i][4])
                        position = Coordinates(x, y)
                    else:
                        position = center.coordinates
                    matrix = self.rotate(float(op1), op2, position)

            center.transform(matrix)
            resulting_matrix = dot(resulting_matrix, matrix)
        drawable.transform(resulting_matrix)
        self.redraw()

    def transform_window(self, transformations: list[tuple[str,int|float,str|int],int|None,int|None]):
        ...