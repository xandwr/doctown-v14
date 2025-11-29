"""
Flight Deck screens.

Each screen represents a major mode of the application.
"""

from .commons import CommonsScreen
from .freeze import FreezeScreen
from .generate import GenerateScreen
from .home import HomeScreen
from .path_input import PathInputScreen
from .viewer import ViewerScreen

__all__ = [
    "CommonsScreen",
    "FreezeScreen",
    "GenerateScreen",
    "HomeScreen",
    "PathInputScreen",
    "ViewerScreen",
]
