"""
Flight Deck - A windowed terminal UI application.
"""

from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Button, Label, MarkdownViewer, Static
from textual.widget import Widget


class TopBar(Static):
    """A window topbar with title and close button."""

    DEFAULT_CSS = """
    TopBar {
        dock: top;
        height: 1;
        background: $primary;
        color: $text;
    }

    TopBar > Horizontal {
        width: 100%;
        height: 100%;
    }

    TopBar .topbar-title {
        width: 1fr;
        content-align: left middle;
        padding-left: 1;
    }

    TopBar #close-btn {
        width: 3;
        min-width: 3;
        height: 1;
        background: red;
        color: white;
        border: none;
        padding: 0;
        text-style: bold;
    }

    TopBar #close-btn:hover {
        background: darkred;
    }

    TopBar #close-btn:focus {
        background: red;
        text-style: bold;
    }
    """

    def __init__(self, title: str = "Flight Deck", **kwargs) -> None:
        super().__init__(**kwargs)
        self.title_text = title

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Label(self.title_text, classes="topbar-title")
            yield Button("✕", id="close-btn")

    def on_mount(self) -> None:
        """Hide close button when running in web mode."""
        if self.app.is_web:
            self.query_one("#close-btn").display = False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close-btn":
            self.app.exit()


class WindowLayout(Container):
    """A window container with topbar and content area - like BaseLayout.astro."""

    DEFAULT_CSS = """
    WindowLayout {
        width: 100%;
        height: 100%;
        border: solid $primary;
    }

    WindowLayout > .window-body {
        width: 100%;
        height: 1fr;
    }
    """

    def __init__(self, title: str = "Flight Deck", *children: Widget, **kwargs) -> None:
        super().__init__(**kwargs)
        self.title_text = title
        self._child_widgets = children

    def compose(self) -> ComposeResult:
        yield TopBar(self.title_text)
        with Container(classes="window-body"):
            for child in self._child_widgets:
                yield child


class FlightDeck(App):
    """The main Flight Deck application."""

    CSS = """
    Screen {
        background: $background;
        padding: 1 2;
    }

    WindowLayout {
        width: 100%;
        height: 100%;
    }
    """

    BINDINGS = [
        ("ctrl+q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        markdown_text = Path("README.md").read_text()
        markdown_viewer = MarkdownViewer(markdown_text, show_table_of_contents=True)
        yield WindowLayout("Flight Deck", markdown_viewer)


def main():
    app = FlightDeck()
    app.run()


if __name__ == "__main__":
    main()
