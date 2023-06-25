from dataclasses import dataclass
from typing import Protocol, Self
from types import SimpleNamespace
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


const = SimpleNamespace()
const.WINDOW_NDC_MIN_X = -1
const.WINDOW_NDC_MIN_Y = -1
const.WINDOW_NDC_MAX_X = 1
const.WINDOW_NDC_MAX_Y = 1


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

    def __eq__(self, __value: object) -> bool:
        return self.x == __value.x and self.y == __value.y


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

    def clip_NDC(self, default: bool = True) -> list[Self] | None:
        if (
            self.coordinates.x >= const.WINDOW_NDC_MIN_X
            and self.coordinates.x <= const.WINDOW_NDC_MAX_X
            and self.coordinates.y >= const.WINDOW_NDC_MIN_Y
            and self.coordinates.y <= const.WINDOW_NDC_MAX_Y
        ):
            return [deepcopy(self)]

        return None


def clip_point_Cohen_Sutherland(
    endpoint: Coordinates, region_code: str, angular_coeficient: int
) -> Coordinates:
    new_endpoint = None

    if region_code[0] == "1":  # Over the top
        if angular_coeficient == 0:
            new_x = endpoint.x
        else:
            new_x = endpoint.x + (1 / angular_coeficient) * (
                const.WINDOW_NDC_MAX_Y - endpoint.y
            )
        new_endpoint = Coordinates(new_x, const.WINDOW_NDC_MAX_Y)

    elif region_code[1] == "1":  # Over the bottom
        if angular_coeficient == 0:
            new_x = endpoint.x
        else:
            new_x = endpoint.x + (1 / angular_coeficient) * (
                const.WINDOW_NDC_MIN_Y - endpoint.y
            )
        new_endpoint = Coordinates(new_x, const.WINDOW_NDC_MIN_Y)

    if (
        new_endpoint
        and new_endpoint.x >= const.WINDOW_NDC_MIN_X
        and new_endpoint.x <= const.WINDOW_NDC_MAX_X
    ):
        return new_endpoint

    if region_code[2] == "1":  # Over the right
        new_endpoint = Coordinates(
            const.WINDOW_NDC_MAX_X,
            angular_coeficient * (const.WINDOW_NDC_MAX_X - endpoint.x) + endpoint.y,
        )
    elif region_code[3] == "1":  # Over the left
        new_endpoint = Coordinates(
            const.WINDOW_NDC_MIN_X,
            angular_coeficient * (const.WINDOW_NDC_MIN_X - endpoint.x) + endpoint.y,
        )

    if (
        new_endpoint.y >= const.WINDOW_NDC_MIN_Y
        and new_endpoint.y <= const.WINDOW_NDC_MAX_Y
    ):
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
        if endpoint.y > const.WINDOW_NDC_MAX_Y:
            region_code = "1"
        else:
            region_code = "0"

        # Over the bottom
        if endpoint.y < const.WINDOW_NDC_MIN_Y:
            region_code = region_code + "1"
        else:
            region_code = region_code + "0"

        # Over the right
        if endpoint.x > const.WINDOW_NDC_MAX_X:
            region_code = region_code + "1"
        else:
            region_code = region_code + "0"

        # Over the left
        if endpoint.x < const.WINDOW_NDC_MIN_X:
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

        delta_x = self.endpoint2.x - self.endpoint1.x

        if delta_x == 0:
            angular_coeficient = 0
        else:
            angular_coeficient = (self.endpoint2.y - self.endpoint1.y) / delta_x

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

        if not endpoint2:
            return None

        return Line(endpoint1, endpoint2, self.color)

    def clip_line_Liang_Barsky(self) -> Self | None:
        p = list()
        p.append(-(self.endpoint2.x - self.endpoint1.x))
        p.append(self.endpoint2.x - self.endpoint1.x)
        p.append(-(self.endpoint2.y - self.endpoint1.y))
        p.append(self.endpoint2.y - self.endpoint1.y)

        q = list()
        q.append(self.endpoint1.x - const.WINDOW_NDC_MIN_X)
        q.append(const.WINDOW_NDC_MAX_X - self.endpoint1.x)
        q.append(self.endpoint1.y - const.WINDOW_NDC_MIN_Y)
        q.append(const.WINDOW_NDC_MAX_Y - self.endpoint1.y)

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

    def clip_NDC(self, default: bool = True) -> list[Self] | None:
        if default:
            line_clipped = self.clip_line_Cohen_Sutherland()
        else:
            line_clipped = self.clip_line_Liang_Barsky()

        if line_clipped:
            return [line_clipped]

        return None


@dataclass
class Wireframe:
    vertexes: list[Coordinates]
    color: Color = Color.BLACK
    filled: bool = False

    def draw(self, drawer: Drawer):
        if len(self.vertexes) > 2:
            if self.filled:
                drawer.draw_wireframe_filled(self.vertexes, self.color)
            else:
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

    def check_clockwise_and_valid_vertexes(
        self, default: bool
    ) -> tuple[bool, list[tuple[Coordinates, bool, bool]]]:
        clockwise_sum = 0
        if (
            self.vertexes[0].x >= const.WINDOW_NDC_MIN_X
            and self.vertexes[0].x <= const.WINDOW_NDC_MAX_X
            and self.vertexes[0].y >= const.WINDOW_NDC_MIN_Y
            and self.vertexes[0].y <= const.WINDOW_NDC_MAX_Y
        ):
            new_vertexes = [self.vertexes[0]]
            if (
                self.vertexes[0].x == const.WINDOW_NDC_MIN_X
                or self.vertexes[0].x == const.WINDOW_NDC_MAX_X
                or self.vertexes[0].y == const.WINDOW_NDC_MIN_Y
                or self.vertexes[0].y == const.WINDOW_NDC_MAX_Y
            ):
                border_vertexes = [(self.vertexes[0], 0)]
            else:
                border_vertexes = list()
        else:
            new_vertexes = list()
            border_vertexes = list()

        inward_vertexes = set()
        outward_vertexes = set()

        for vertex1, vertex2 in zip(
            self.vertexes, self.vertexes[1:] + [self.vertexes[0]]
        ):
            # clockwise_sum += (vertex2.x - vertex1.x) * (vertex2.y - vertex1.y)
            # top       = +
            # right     = +
            # bottom    = -
            # left      = -

            # top and left      = -
            # top and right     = +
            # bottom and left   = +
            # bottom and right  = -

            clockwise_sum += (vertex2.x - vertex1.x) * (vertex2.y - vertex1.y)
            new_line = Line(vertex1, vertex2, self.color).clip_NDC(default)
            if new_line:
                new_line = new_line[0]

                if vertex1 != new_line.endpoint1:
                    if new_line.endpoint1.x >= 0.998:
                        new_line.endpoint1.x = 1
                    elif new_line.endpoint1.x <= -0.998:
                        new_line.endpoint1.x = -1

                    if new_line.endpoint1.y >= 0.998:
                        new_line.endpoint1.y = 1
                    elif new_line.endpoint1.y <= -0.998:
                        new_line.endpoint1.y = -1

                    new_vertexes.append(new_line.endpoint1)
                    border_vertexes.append((new_line.endpoint1, len(new_vertexes) - 1))
                    inward_vertexes.add(len(new_vertexes) - 1)

                if vertex2 != new_line.endpoint2:
                    if new_line.endpoint2.x >= 0.998:
                        new_line.endpoint2.x = 1
                    elif new_line.endpoint2.x <= -0.998:
                        new_line.endpoint2.x = -1

                    if new_line.endpoint2.y >= 0.998:
                        new_line.endpoint2.y = 1
                    elif new_line.endpoint2.y <= -0.998:
                        new_line.endpoint2.y = -1

                    border_vertexes.append((new_line.endpoint2, len(new_vertexes)))
                    outward_vertexes.add(len(new_vertexes))
                else:
                    if (
                        self.vertexes[0].x == const.WINDOW_NDC_MIN_X
                        or self.vertexes[0].x == const.WINDOW_NDC_MAX_X
                        or self.vertexes[0].y == const.WINDOW_NDC_MIN_Y
                        or self.vertexes[0].y == const.WINDOW_NDC_MAX_Y
                    ):
                        border_vertexes.append((new_line.endpoint2, len(new_vertexes)))
                new_vertexes.append(new_line.endpoint2)

        if clockwise_sum < 0:
            return False, new_vertexes, border_vertexes, inward_vertexes

        return True, new_vertexes, border_vertexes, outward_vertexes

        # TODO: border_vertexes: list[Coordinates, int]
        # TODO: outward_vertexes: outward_vertexes | inward_vertexes

    def follow_border(
        self,
        border_vertexes: list[Coordinates, int],
        outward_vertex: Coordinates,
        outward_index: int,
    ) -> tuple[list[Coordinates], int]:
        border_vertex = None
        corner_borders = list()
        while not border_vertex:
            match outward_vertex:
                # Top border
                case Coordinates(const.WINDOW_NDC_MIN_X, const.WINDOW_NDC_MAX_Y):
                    for vertex, i in border_vertexes:
                        if (
                            i != outward_index
                            and vertex.y == const.WINDOW_NDC_MAX_Y
                            and vertex.x > outward_vertex.x
                            and (not border_vertex or vertex.x < border_vertex.x)
                        ):
                            border_vertex = vertex
                            border_index = i
                    if not border_vertex:
                        corner_vertex = Coordinates(
                            const.WINDOW_NDC_MAX_X, const.WINDOW_NDC_MAX_Y
                        )
                        corner_borders.append(corner_vertex)
                        outward_vertex = corner_vertex

                # Right border
                case Coordinates(const.WINDOW_NDC_MAX_X, const.WINDOW_NDC_MAX_Y):
                    for vertex, i in border_vertexes:
                        if (
                            i != outward_index
                            and vertex.x == const.WINDOW_NDC_MAX_X
                            and vertex.y < outward_vertex.y
                            and (not border_vertex or vertex.y > border_vertex.y)
                        ):
                            border_vertex = vertex
                            border_index = i
                    if not border_vertex:
                        corner_vertex = Coordinates(
                            const.WINDOW_NDC_MAX_X, const.WINDOW_NDC_MIN_Y
                        )
                        corner_borders.append(corner_vertex)
                        outward_vertex = corner_vertex

                # Bottom border
                case Coordinates(const.WINDOW_NDC_MAX_X, const.WINDOW_NDC_MIN_Y):
                    for vertex, i in border_vertexes:
                        if (
                            i != outward_index
                            and vertex.y == const.WINDOW_NDC_MIN_Y
                            and vertex.x < outward_vertex.x
                            and (not border_vertex or vertex.x > border_vertex.x)
                        ):
                            border_vertex = vertex
                            border_index = i
                    if not border_vertex:
                        corner_vertex = Coordinates(
                            const.WINDOW_NDC_MIN_X, const.WINDOW_NDC_MIN_Y
                        )
                        corner_borders.append(corner_vertex)
                        outward_vertex = corner_vertex

                # Left border
                case Coordinates(const.WINDOW_NDC_MIN_X, const.WINDOW_NDC_MIN_Y):
                    for vertex, i in border_vertexes:
                        if (
                            i != outward_index
                            and vertex.x == const.WINDOW_NDC_MIN_X
                            and vertex.y > outward_vertex.y
                            and (not border_vertex or vertex.y < border_vertex.y)
                        ):
                            border_vertex = vertex
                            border_index = i
                    if not border_vertex:
                        corner_vertex = Coordinates(
                            const.WINDOW_NDC_MIN_X, const.WINDOW_NDC_MAX_Y
                        )
                        corner_borders.append(corner_vertex)
                        outward_vertex = corner_vertex

                case Coordinates():
                    match outward_vertex.x:
                        # Left border
                        case const.WINDOW_NDC_MIN_X:
                            for vertex, i in border_vertexes:
                                if (
                                    i != outward_index
                                    and vertex.x == const.WINDOW_NDC_MIN_X
                                    and vertex.y > outward_vertex.y
                                    and (
                                        not border_vertex or vertex.y < border_vertex.y
                                    )
                                ):
                                    border_vertex = vertex
                                    border_index = i
                            if not border_vertex:
                                corner_vertex = Coordinates(
                                    const.WINDOW_NDC_MIN_X, const.WINDOW_NDC_MAX_Y
                                )
                                corner_borders.append(corner_vertex)
                                outward_vertex = corner_vertex

                        # Right border
                        case const.WINDOW_NDC_MAX_X:
                            for vertex, i in border_vertexes:
                                if (
                                    i != outward_index
                                    and vertex.x == const.WINDOW_NDC_MAX_X
                                    and vertex.y < outward_vertex.y
                                    and (
                                        not border_vertex or vertex.y > border_vertex.y
                                    )
                                ):
                                    border_vertex = vertex
                                    border_index = i
                            if not border_vertex:
                                corner_vertex = Coordinates(
                                    const.WINDOW_NDC_MAX_X, const.WINDOW_NDC_MIN_Y
                                )
                                corner_borders.append(corner_vertex)
                                outward_vertex = corner_vertex

                        case _:
                            match outward_vertex.y:
                                # Bottom border
                                case const.WINDOW_NDC_MIN_Y:
                                    for vertex, i in border_vertexes:
                                        if (
                                            i != outward_index
                                            and vertex.y == const.WINDOW_NDC_MIN_Y
                                            and vertex.x < outward_vertex.x
                                            and (
                                                not border_vertex
                                                or vertex.x > border_vertex.x
                                            )
                                        ):
                                            border_vertex = vertex
                                            border_index = i
                                    if not border_vertex:
                                        corner_vertex = Coordinates(
                                            const.WINDOW_NDC_MIN_X,
                                            const.WINDOW_NDC_MIN_Y,
                                        )
                                        corner_borders.append(corner_vertex)
                                        outward_vertex = corner_vertex

                                # Top border
                                case const.WINDOW_NDC_MAX_Y:
                                    for vertex, i in border_vertexes:
                                        if (
                                            i != outward_index
                                            and vertex.y == const.WINDOW_NDC_MAX_Y
                                            and vertex.x > outward_vertex.x
                                            and (
                                                not border_vertex
                                                or vertex.x < border_vertex.x
                                            )
                                        ):
                                            border_vertex = vertex
                                            border_index = i
                                    if not border_vertex:
                                        corner_vertex = Coordinates(
                                            const.WINDOW_NDC_MAX_X,
                                            const.WINDOW_NDC_MAX_Y,
                                        )
                                        corner_borders.append(corner_vertex)
                                        outward_vertex = corner_vertex

        return corner_borders, border_index

    def add_wireframe(
        self, wireframes_list: list[Self], coordinates: list[Coordinates]
    ) -> None:
        # if len(coordinates) < 3:
        #     raise("Wireframe clipped has insuficient vertexes")
        wireframe = Wireframe(deepcopy(coordinates), self.color, self.filled)
        wireframes_list.append(wireframe)
        coordinates.clear()

    def clip_NDC(self, default: bool = True) -> list[list[Self]] | None:
        (
            clockwise,
            new_vertexes,
            border_vertexes,
            outward_vertexes,
        ) = self.check_clockwise_and_valid_vertexes(default)
        if clockwise:
            step = 1
        else:
            step = -1

        new_wireframes = list()
        new_wireframe = list()

        touched_vertexes = set()
        i = 0
        while len(touched_vertexes) < len(new_vertexes):
            if i in touched_vertexes:
                if new_vertexes[i] != new_wireframe[0]:
                    new_wireframe.append(new_vertexes[i])
                i = (i + step) % len(new_vertexes)
                if len(new_wireframe) > 0:
                    self.add_wireframe(new_wireframes, new_wireframe)
            else:
                touched_vertexes.add(i)

                vertex = new_vertexes[i]

                new_wireframe.append(vertex)
                if i in outward_vertexes:
                    corner_vertexes, i = self.follow_border(border_vertexes, vertex, i)

                    new_wireframe = new_wireframe + corner_vertexes
                    if i in touched_vertexes:
                        if new_vertexes[i] != new_wireframe[0]:
                            new_wireframe.append(new_vertexes[i])
                        self.add_wireframe(new_wireframes, new_wireframe)
                    else:
                        touched_vertexes.add(i)
                        vertex = new_vertexes[i]
                        new_wireframe.append(vertex)

                i = (i + step) % len(new_vertexes)

        if len(new_wireframe) > 0:
            self.add_wireframe(new_wireframes, new_wireframe)

        if len(new_wireframes) == 0:
            return None

        return new_wireframes
