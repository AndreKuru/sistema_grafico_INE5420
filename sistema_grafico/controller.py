from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from view import Graphic_Viewer


@dataclass
class Controller:
    _display_file: list()