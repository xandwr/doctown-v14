"""
Flight Deck - A windowed terminal UI for exploring docpacks.

The Flight Deck is the unified interface for the docpack ecosystem.
Drop a .docpack to explore, drop a folder to create one.

Supports both CLI power users and casual users who want a simple
drag-and-drop experience.
"""

from pathlib import Path
from typing import Any

from textual.app import App, ComposeResult
from textual.binding import Binding

from flight_deck.screens import FreezeScreen, HomeScreen, PathInputScreen, ViewerScreen


class FlightDeck(App):
    """The main Flight Deck application."""

    TITLE = "Flight Deck"
    SUB_TITLE = "Docpack Explorer"

    CSS = """
    Screen {
        background: $background;
    }
    """

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", show=True, priority=True),
        Binding("ctrl+o", "open_file", "Open", show=True),
    ]

    SCREENS = {
        "path_input": PathInputScreen,
    }

    def __init__(self, docpack_path: Path | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self._initial_docpack = docpack_path
        self._recent_docpacks: list[Path] = []
        self._load_recent()

    def on_mount(self) -> None:
        """Set up the initial screen."""
        if self._initial_docpack and self._initial_docpack.exists():
            # Open directly to viewer if a docpack was provided
            self.push_screen(ViewerScreen(docpack_path=self._initial_docpack))
        else:
            # Show home screen
            self.push_screen(HomeScreen(recent_docpacks=self._recent_docpacks))

    def open_docpack(self, path: Path) -> None:
        """Open a docpack in the viewer."""
        if not path.exists():
            self.notify(f"File not found: {path}", severity="error")
            return

        if path.suffix != ".docpack":
            self.notify(f"Not a docpack file: {path}", severity="error")
            return

        # Add to recent
        self._add_recent(path)

        # Switch to viewer
        self.switch_screen(ViewerScreen(docpack_path=path))

    def freeze_folder(self, path: Path) -> None:
        """Start freezing a folder into a docpack."""
        if not path.exists():
            self.notify(f"Folder not found: {path}", severity="error")
            return

        if not path.is_dir():
            self.notify(f"Not a folder: {path}", severity="error")
            return

        # Determine output path
        output_path = path.with_suffix(".docpack")

        # Switch to freeze screen
        self.push_screen(FreezeScreen(source_path=path, output_path=output_path))

    def action_open_file(self) -> None:
        """Open the path input dialog."""

        def handle_result(path: Path | None) -> None:
            if path is None:
                return

            if path.is_file() and path.suffix == ".docpack":
                self.open_docpack(path)
            elif path.is_dir():
                self.freeze_folder(path)

        self.push_screen(PathInputScreen(), handle_result)

    def _load_recent(self) -> None:
        """Load recent docpacks from config."""
        # For now, just use an empty list
        # Could persist to ~/.config/docpack/recent.json
        self._recent_docpacks = []

    def _add_recent(self, path: Path) -> None:
        """Add a path to recent docpacks."""
        # Remove if already present
        self._recent_docpacks = [p for p in self._recent_docpacks if p != path]

        # Add to front
        self._recent_docpacks.insert(0, path)

        # Keep only last 10
        self._recent_docpacks = self._recent_docpacks[:10]

        # Could persist here
        self._save_recent()

    def _save_recent(self) -> None:
        """Save recent docpacks to config."""
        # Could persist to ~/.config/docpack/recent.json
        pass


def main(docpack_path: str | None = None) -> None:
    """Run the Flight Deck application."""
    path = Path(docpack_path) if docpack_path else None
    app = FlightDeck(docpack_path=path)
    app.run()


if __name__ == "__main__":
    main()
