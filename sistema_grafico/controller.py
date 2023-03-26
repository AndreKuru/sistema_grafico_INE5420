from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Iterable, Optional

from .model import WCoords, VPCoords, Vector, Object, Point, Line, Wireframe

if TYPE_CHECKING:
    from view import GraphicalViewer


@dataclass
class Controller:
    _window_position: WCoords = Vector(0,0)
    _window_size: WCoords = Vector(1,1)
    _display_file: list[Object] = field(default_factory=list)
    _graphical_viewer: Optional["GraphicalViewer"] = None

    def _update_view(self) -> None:
        assert self._graphical_viewer is not None
        self._graphical_viewer.redraw(self._display_file)

    def set_graphical_viewer(self, graphical_viewer: "GraphicalViewer") -> None:
        self._graphical_viewer = graphical_viewer
        self._update_view()

    def scale_vpcoords_to_wcoords(self, coords: Vector[int]) -> Vector[float]:
        assert self._graphical_viewer is not None


    def pan_window(self, variation: VPCoords) -> None:
        self._window_position += scale_vpcoords_to_wcoords(variation)
        self._update_view()

    
