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

    def create_point(self, x, y):
        name = "Point1"
        point = Point(name, Coordinates(x, y))
        self._display_file.append(point)
        self._drawer.insert_drawable(point)
        self.redraw()
    
    def redraw(self):
        self._drawer.clear()
        for drawable in self._display_file:
            drawable.draw(self._drawer)