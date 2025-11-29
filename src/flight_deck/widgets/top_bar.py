from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button, Label, Static


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
