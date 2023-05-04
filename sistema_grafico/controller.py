from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from model import Coordinates, Point, Line, Wireframe, Drawable, Area2d, Color
from math import sin, cos, radians
from numpy import double, dot
from copy import deepcopy
from pathlib import Path
import re

if TYPE_CHECKING:
    from view import Graphic_Viewer


@dataclass
class Controller:
    _drawer: Optional["Graphic_Viewer"] = None
    _window: Area2d = field(default=lambda: Area2d(Coordinates(0, 0), Coordinates(200, 200)))
    _display_file: dict[Drawable] = field(default_factory=dict)
    _display_file_NDC: dict[Drawable] = field(default_factory=dict)
    _transformation_NDC: list[list[int | double | float]] = field(
        default_factory=lambda: [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    )

    def transform_window_to_viewport(self, drawable_in_window: Coordinates):
        x_w_max = 1
        x_w_min = -1
        x_vp_max = self._drawer._viewport.max.x
        x_vp_min = self._drawer._viewport.min.x

        y_w_max = 1
        y_w_min = -1
        y_vp_max = self._drawer._viewport.max.y
        y_vp_min = self._drawer._viewport.min.y

        viewport_x = (
            (drawable_in_window.x - x_w_min)
            / (x_w_max - x_w_min)
            * (x_vp_max - x_vp_min)
        )
        viewport_y = (1 - ((drawable_in_window.y - y_w_min) / (y_w_max - y_w_min))) * (
            y_vp_max - y_vp_min
        )

        viewport_coordinates = Coordinates(
            viewport_x + self._drawer._viewport.min.x, 
            viewport_y + self._drawer._viewport.min.y
            )

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

        window_x = (
            viewport_coordinates.x * ((x_w_max - x_w_min) / (x_vp_max - x_vp_min))
            + x_w_min
        )
        window_y = (1 - (viewport_coordinates.y / (y_vp_max - y_vp_min))) * (
            y_w_max - y_w_min
        ) + y_w_min

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

    def create_point_w_coordinates(
        self, coordinate: Coordinates, color: Color, name: str = None
    ):
        if name is None:
            name = self.new_name("Point")
        point = Point(coordinate, color)
        self._display_file[name] = point
        self._drawer.insert_drawable(name)
        point_NDC = deepcopy(point)
        point_NDC.transform(self._transformation_NDC)
        self._display_file_NDC[name] = point_NDC
        self.redraw()

    def create_point(self, x: int, y: int, color: Color):
        self.create_point_w_coordinates(Coordinates(x, y), color)

    def create_line_w_coordinates(
        self,
        endpoint1: Coordinates,
        endpoint2: Coordinates,
        color: Color,
        name: str = None,
    ):
        if name is None:
            name = self.new_name("Line")
        line = Line(endpoint1, endpoint2, color)
        self._display_file[name] = line
        self._drawer.insert_drawable(name)
        line_NDC = deepcopy(line)
        line_NDC.transform(self._transformation_NDC)
        self._display_file_NDC[name] = line_NDC
        self.redraw()

    def create_line(self, x1: int, y1: int, x2: int, y2: int, color: Color):
        endpoint1 = Coordinates(x1, y1)
        endpoint2 = Coordinates(x2, y2)

        self.create_line_w_coordinates(endpoint1, endpoint2, color)

    def create_wireframe_w_coordinates(
        self, coordinates: list[Coordinates], color: Color, name: str = None
    ):
        if name is None:
            name = self.new_name("Wireframe")
        wireframe = Wireframe(coordinates, color)
        self._display_file[name] = wireframe
        self._drawer.insert_drawable(name)
        wireframe_NDC = deepcopy(wireframe)
        wireframe_NDC.transform(self._transformation_NDC)
        self._display_file_NDC[name] = wireframe_NDC
        self.redraw()

    def create_wireframe(self, list_x: list(int), list_y: list(int), color: Color):
        coordinates = list()
        for i in range(len(list_x)):
            coordinate = Coordinates(list_x[i], list_y[i])
            coordinates.append(coordinate)

        self.create_wireframe_w_coordinates(coordinates, color)

    def redraw(self):
        self._drawer.clear()
        for drawable in self._display_file_NDC.values():
            drawable_clipped = drawable.clip_NDC()
            if drawable_clipped:
                drawable_clipped.draw(self._drawer)
        self._drawer.draw_viewport_border()

    def size_window(self) -> Coordinates:
        return Coordinates(
            self._transformation_NDC[0][0], self._transformation_NDC[1][1]
        )

    def pan_window(self, movement: Coordinates, step: float):
        translate = ("t", movement.x * step, movement.y * step)
        self.transform_window([translate])
        self.redraw()

    def zoom(self, ammount: Coordinates):
        scalling = ("s", ammount.x, ammount.y)
        self.transform_window([scalling])
        self.redraw()

    def translate(self, transformation: Coordinates):
        matrix = ((1, 0, 0), (0, 1, 0), (transformation.x, transformation.y, 1))
        return matrix

    def scale(self, transformation: Coordinates, center: Coordinates):
        translation_to_origin = Coordinates(0, 0) - center
        resulting_matrix = self.translate(translation_to_origin)

        matrix = ((transformation.x, 0, 0), (0, transformation.y, 0), (0, 0, 1))
        resulting_matrix = dot(resulting_matrix, matrix)

        matrix = self.translate(center)
        resulting_matrix = dot(resulting_matrix, matrix)

        return resulting_matrix

    def rotate_around_origin(self, angle: float):
        matrix = ((cos(angle), -sin(angle), 0), (sin(angle), cos(angle), 0), (0, 0, 1))
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

    def transform_drawable(
        self,
        transformations: list[
            tuple[str, int | float, str | int, int | None, int | None]
        ],
        name: str,
    ):
        drawable = self._display_file[name]
        initial_matrix = ((1, 0, 0), (0, 1, 0), (0, 0, 1))

        center = Point(drawable.calculate_center())
        transformations_matrix = self.transform(transformations, center, initial_matrix)

        drawable.transform(transformations_matrix)

        drawable_NDC = deepcopy(drawable)
        drawable_NDC.transform(self._transformation_NDC)
        self._display_file_NDC[name] = drawable_NDC
        self.redraw()

    def transform(
        self,
        transformations: list[
            tuple[str, int | float, str | int | float, int | None, int | None]
        ],
        center: Point,
        transformation_matrix: tuple[
            tuple[float, float, float],
            tuple[float, float, float],
            tuple[float, float, float],
        ],
    ):
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
            transformation_matrix = dot(transformation_matrix, matrix)

        return transformation_matrix

    def transform_display_file_NDC(self):
        self._display_file_NDC = deepcopy(self._display_file)
        for drawable in self._display_file_NDC.values():
            drawable.transform(self._transformation_NDC)
        self.redraw()

    def transform_window(
        self,
        transformations: list[
            tuple[str, int | float, str | int | float, int | None, int | None]
        ],
    ):
        self._transformation_NDC = self.transform(
            transformations, Point(Coordinates(0, 0)), self._transformation_NDC
        )
        self.transform_display_file_NDC()

    def export_obj(self, name: str) -> str:
        drawable = self._display_file[name]

        match drawable:
            case Point():
                vertexes = [drawable.coordinates]

            case Line():
                vertexes = [drawable.endpoint1, drawable.endpoint2]

            case Wireframe():
                vertexes = drawable.vertexes

        output_content = f"o {name}\n"
        for vertex in vertexes:
            output_content = (
                output_content + f"\nv {float(vertex.x)} {float(vertex.y)} 0"
            )

        output_content = output_content + "\n\nf"

        # Relative
        #  for i in range(-len(vertexes), 0):
        #      output_content = output_content + f" {i}"

        # Absolute
        for i in range(1, len(vertexes) + 1):
            output_content = output_content + f" {i}"

        return output_content

    def import_obj(self, lines: list[str]) -> None:
        if re.search("o\s", lines[0]):
            name = re.sub("o\s", "", lines[0])
        else:
            print("Missing name. It will be used a generic name.")
            name = None

        vertexes = list()
        coordinates = list()  # 2D
        for line in lines:
            if re.search("v\s-?\d+.?\d*\s-?\d+.?\d*\s-?\d+.?\d*", line):
                numbers = re.sub("v\s", "", line)
                numbers = numbers.split(" ")
                numbers = [float(number) for number in numbers]
                x, y, z = numbers  # z will be used in 3D only
                vertexes.append(Coordinates(x, y))

            if re.search("f\s-?\d+", line):
                face = re.sub("f\s", "", line)
                face = face.split(" ")
                face = [int(f) for f in face]
                for index in face:
                    if index > 0:
                        coordinates.append(vertexes[index - 1])
                    if index < 0:
                        coordinates.append(vertexes[index])

        match len(coordinates):
            case 0:
                raise ("Invalid .obj: No vertexes found")

            case 1:
                self.create_point_w_coordinates(coordinates[0], Color.BLACK, name)

            case 2:
                self.create_line_w_coordinates(
                    coordinates[0], coordinates[1], Color.BLACK, name
                )

            case _:
                self.create_wireframe_w_coordinates(coordinates, Color.BLACK, name)
    