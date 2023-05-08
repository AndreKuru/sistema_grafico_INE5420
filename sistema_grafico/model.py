from dataclasses import dataclass
from typing import Protocol, Self
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


WINDOW_NDC_MIN_X = -1
WINDOW_NDC_MIN_Y = -1
WINDOW_NDC_MAX_X = 1
WINDOW_NDC_MAX_Y = 1


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
        x = self.x * (other)
        y = self.y * (other)
        return Coordinates(x, y)


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
        self.max = self.max.multiply_scalar(1 + ammount)


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

    def clip_NDC(self, default: bool = True):
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

    def clip_NDC(self, default: bool = True) -> Self | None:
        if (
            self.coordinates.x > WINDOW_NDC_MIN_X
            and self.coordinates.x < WINDOW_NDC_MAX_X
            and self.coordinates.y > WINDOW_NDC_MIN_Y
            and self.coordinates.y < WINDOW_NDC_MAX_Y
        ):
            return deepcopy(self)

        return None


def clip_point_Cohen_Sutherland(
    endpoint: Coordinates, region_code: str, angular_coeficient: int
) -> Coordinates:
    new_endpoint = None

    if region_code[0] == "1":  # Over the top
        new_endpoint = Coordinates(
            endpoint.x + (1 / angular_coeficient) * (WINDOW_NDC_MAX_Y - endpoint.y),
            WINDOW_NDC_MAX_Y,
        )
    elif region_code[1] == "1":  # Over the bottom
        new_endpoint = Coordinates(
            endpoint.x + (1 / angular_coeficient) * (WINDOW_NDC_MIN_Y - endpoint.y),
            WINDOW_NDC_MIN_Y,
        )

    if (
        new_endpoint
        and new_endpoint.x >= WINDOW_NDC_MIN_X
        and new_endpoint.x <= WINDOW_NDC_MAX_X
    ):
        return new_endpoint

    if region_code[2] == "1":  # Over the right
        new_endpoint = Coordinates(
            WINDOW_NDC_MAX_X,
            angular_coeficient * (WINDOW_NDC_MAX_X - endpoint.x) + endpoint.y,
        )
    elif region_code[3] == "1":  # Over the left
        new_endpoint = Coordinates(
            WINDOW_NDC_MIN_X,
            angular_coeficient * (WINDOW_NDC_MIN_X - endpoint.x) + endpoint.y,
        )

    if new_endpoint.y >= WINDOW_NDC_MIN_Y and new_endpoint.y <= WINDOW_NDC_MAX_Y:
        return new_endpoint

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

    def get_region_code(self, endpoint: Coordinates) -> str:  # binary number
        # Over the top
        if endpoint.y > WINDOW_NDC_MAX_Y:
            region_code = "1"
        else:
            region_code = "0"

        # Over the bottom
        if endpoint.y < WINDOW_NDC_MIN_Y:
            region_code = region_code + "1"
        else:
            region_code = region_code + "0"

        # Over the right
        if endpoint.x > WINDOW_NDC_MAX_X:
            region_code = region_code + "1"
        else:
            region_code = region_code + "0"

        # Over the left
        if endpoint.x < WINDOW_NDC_MIN_X:
            region_code = region_code + "1"
        else:
            region_code = region_code + "0"

        return region_code

    def clip_line_Cohen_Sutherland(self) -> Self | None:
        region_code1 = self.get_region_code(self.endpoint1)
        region_code2 = self.get_region_code(self.endpoint2)

        if int(region_code1, 2) + int(region_code2, 2) == 0:
            return deepcopy(self)

        if int(region_code1, 2) & int(region_code2, 2) != 0:
            return None

        angular_coeficient = (self.endpoint2.y - self.endpoint1.y) / (
            self.endpoint2.x - self.endpoint1.x
        )

        if int(region_code1) != 0:
            endpoint1 = clip_point_Cohen_Sutherland(
                self.endpoint1, region_code1, angular_coeficient
            )
        else:
            endpoint1 = deepcopy(self.endpoint1)

        if not endpoint1:
            return None

        if int(region_code2) != 0:
            endpoint2 = clip_point_Cohen_Sutherland(
                self.endpoint2, region_code2, angular_coeficient
            )
        else:
            endpoint2 = deepcopy(self.endpoint2)

        return Line(endpoint1, endpoint2, self.color)

    def clip_line_Liang_Barsky(self) -> Self | None:
        p = list()
        p.append(-(self.endpoint2.x - self.endpoint1.x))
        p.append(self.endpoint2.x - self.endpoint1.x)
        p.append(-(self.endpoint2.y - self.endpoint1.y))
        p.append(self.endpoint2.y - self.endpoint1.y)

        q = list()
        q.append(self.endpoint1.x - WINDOW_NDC_MIN_X)
        q.append(WINDOW_NDC_MAX_X - self.endpoint1.x)
        q.append(self.endpoint1.y - WINDOW_NDC_MIN_Y)
        q.append(WINDOW_NDC_MAX_Y - self.endpoint1.y)

        zeta1 = [0]
        zeta2 = [1]

        p_positive = list()
        p_negative = list()

        for i in range(4):
            if p[i] < 0:
                zeta1.append(q[i] / p[i])
                p_negative.append(p[i])
            elif p[i] > 0:
                zeta2.append(q[i] / p[i])
                p_positive.append(p[i])
            else:
                if q[i] < 0:
                    return None

        zeta1 = max(zeta1)
        zeta2 = min(zeta2)

        if zeta1 > zeta2:
            return None

        if zeta1 > 0:
            x = p[1] * zeta1
            y = p[3] * zeta1
            endpoint1 = self.endpoint1 + Coordinates(x, y)
        else:
            endpoint1 = deepcopy(self.endpoint1)

        if zeta2 < 1:
            x = p[1] * zeta2
            y = p[3] * zeta2
            endpoint2 = self.endpoint1 + Coordinates(x, y)
        else:
            endpoint2 = deepcopy(self.endpoint2)

        return Line(endpoint1, endpoint2, self.color)

    def clip_NDC(self, default: bool = False):
        if default:
            return self.clip_line_Cohen_Sutherland()

        return self.clip_line_Liang_Barsky()


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
