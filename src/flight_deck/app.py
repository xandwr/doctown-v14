"""
Flight Deck - A windowed terminal UI application.
"""

from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import MarkdownViewer

from flight_deck.widgets.window import WindowLayout


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