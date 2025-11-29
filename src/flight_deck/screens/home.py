"""
HomeScreen - the landing page with DropZone.

This is what users see when they launch Flight Deck without arguments.
"""

from pathlib import Path

from textual import on
from textual.app import ComposeResult
from textual.screen import Screen

from flight_deck.widgets import DropZone, WindowLayout


class HomeScreen(Screen):
    """The home screen with drop zone for docpacks/folders."""

    BINDINGS = [
        ("ctrl+o", "browse", "Browse"),
        ("escape", "quit", "Quit"),
    ]

    def __init__(self, recent_docpacks: list[Path] | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.recent_docpacks = recent_docpacks or []

    def compose(self) -> ComposeResult:
        drop_zone = DropZone(recent_docpacks=self.recent_docpacks)
        yield WindowLayout("Flight Deck", drop_zone)

    @on(DropZone.DocpackSelected)
    def on_docpack_selected(self, event: DropZone.DocpackSelected) -> None:
        """Handle docpack selection - switch to viewer."""
        self.app.open_docpack(event.path)

    @on(DropZone.FolderSelected)
    def on_folder_selected(self, event: DropZone.FolderSelected) -> None:
        """Handle folder selection - switch to freeze screen."""
        self.app.freeze_folder(event.path)

    def action_browse(self) -> None:
        """Open the path input screen."""
        self.app.push_screen("path_input")

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()
