"""
Flight Deck - A windowed terminal UI for exploring docpacks.

The Flight Deck is the unified interface for the docpack ecosystem.
Designed to feel like a website, but entirely in a terminal,
that can also be served as an actual website.

Navigation:
- Commons: Browse public/shared docpacks (coming soon)
- Generate: Create new docpacks with a staged wizard
- Explore: View and search existing docpacks
"""

from pathlib import Path

from textual import on
from textual.app import App
from textual.binding import Binding

from flight_deck.screens import (
    CommonsScreen,
    GenerateScreen,
    PathInputScreen,
    ViewerScreen,
)
from flight_deck.widgets import NavBar


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
        Binding("ctrl+g", "go_generate", "Generate", show=False),
        Binding("ctrl+e", "go_explore", "Explore", show=False),
    ]

    def __init__(self, docpack_path: Path | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self._initial_docpack = docpack_path
        self._recent_docpacks: list[Path] = []
        self._current_docpack: Path | None = None

    def on_mount(self) -> None:
        """Set up the initial screen."""
        if self._initial_docpack and self._initial_docpack.exists():
            # Open directly to viewer if a docpack was provided
            self._current_docpack = self._initial_docpack
            self.push_screen(ViewerScreen(docpack_path=self._initial_docpack))
        else:
            # Default to Generate screen (the main landing page)
            self.push_screen(GenerateScreen())

    @on(NavBar.Navigate)
    def on_nav_navigate(self, event: NavBar.Navigate) -> None:
        """Handle navigation from the NavBar."""
        self._navigate_to(event.destination)

    def _navigate_to(self, destination: str) -> None:
        """Navigate to a destination screen."""
        if destination == "commons":
            self.switch_screen(CommonsScreen())
        elif destination == "generate":
            self.switch_screen(GenerateScreen())
        elif destination == "explore":
            if self._current_docpack and self._current_docpack.exists():
                self.switch_screen(ViewerScreen(docpack_path=self._current_docpack))
            else:
                # No docpack loaded - prompt to open one
                self.action_open_file()

    def open_docpack(self, path: Path) -> None:
        """Open a docpack in the viewer."""
        if not path.exists():
            self.notify(f"File not found: {path}", severity="error")
            return

        if path.suffix != ".docpack":
            self.notify(f"Not a docpack file: {path}", severity="error")
            return

        self._current_docpack = path
        self._add_recent(path)
        self.switch_screen(ViewerScreen(docpack_path=path))

    def freeze_folder(self, path: Path) -> None:
        """Open the generate screen with a pre-filled source path."""
        if not path.exists():
            self.notify(f"Folder not found: {path}", severity="error")
            return

        self.switch_screen(GenerateScreen(initial_path=path))

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

    def action_go_generate(self) -> None:
        """Navigate to Generate screen."""
        self._navigate_to("generate")

    def action_go_explore(self) -> None:
        """Navigate to Explore screen."""
        self._navigate_to("explore")

    def _add_recent(self, path: Path) -> None:
        """Add a path to recent docpacks."""
        self._recent_docpacks = [p for p in self._recent_docpacks if p != path]
        self._recent_docpacks.insert(0, path)
        self._recent_docpacks = self._recent_docpacks[:10]


def main(docpack_path: str | None = None) -> None:
    """Run the Flight Deck application."""
    path = Path(docpack_path) if docpack_path else None
    app = FlightDeck(docpack_path=path)
    app.run()


if __name__ == "__main__":
    main()
