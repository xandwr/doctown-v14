"""
PathInputScreen - simple modal for entering a file/folder path.

Used when Browse is clicked or Ctrl+O is pressed.
"""

from pathlib import Path

from textual import on
from textual.app import ComposeResult
from textual.containers import Center, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label


class PathInputScreen(ModalScreen[Path | None]):
    """Modal screen for entering a path."""

    DEFAULT_CSS = """
    PathInputScreen {
        align: center middle;
    }

    PathInputScreen > Vertical {
        width: 60;
        height: auto;
        padding: 2;
        border: solid $primary;
        background: $surface;
    }

    PathInputScreen .title {
        width: 100%;
        text-align: center;
        text-style: bold;
        padding-bottom: 1;
    }

    PathInputScreen .hint {
        width: 100%;
        text-align: center;
        color: $text-muted;
        padding-bottom: 1;
    }

    PathInputScreen Input {
        width: 100%;
        margin-bottom: 1;
    }

    PathInputScreen .button-row {
        width: 100%;
        height: auto;
        align: center middle;
        padding-top: 1;
    }

    PathInputScreen Button {
        margin: 0 1;
    }

    PathInputScreen .error {
        width: 100%;
        text-align: center;
        color: $error;
        padding-top: 1;
    }
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("📂 Open Path", classes="title")
            yield Label("Enter a .docpack file or folder path", classes="hint")
            yield Input(
                placeholder="/path/to/file.docpack or /path/to/folder",
                id="path-input",
            )
            yield Label("", id="error-label", classes="error")
            with Center(classes="button-row"):
                yield Button("Cancel", id="cancel-btn", variant="default")
                yield Button("Open", id="open-btn", variant="primary")

    def on_mount(self) -> None:
        """Focus the input when mounted."""
        self.query_one("#path-input", Input).focus()

    @on(Input.Submitted, "#path-input")
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle enter key in input."""
        self._try_open(event.value)

    @on(Button.Pressed, "#open-btn")
    def on_open_pressed(self, event: Button.Pressed) -> None:
        """Handle open button click."""
        path_input = self.query_one("#path-input", Input)
        self._try_open(path_input.value)

    @on(Button.Pressed, "#cancel-btn")
    def on_cancel_pressed(self, event: Button.Pressed) -> None:
        """Handle cancel button click."""
        self.dismiss(None)

    def action_cancel(self) -> None:
        """Handle escape key."""
        self.dismiss(None)

    def _try_open(self, path_str: str) -> None:
        """Attempt to open the given path."""
        path_str = path_str.strip()
        if not path_str:
            self._show_error("Please enter a path")
            return

        # Expand ~ and resolve path
        path = Path(path_str).expanduser().resolve()

        if not path.exists():
            self._show_error(f"Path not found: {path}")
            return

        if path.is_file():
            if path.suffix != ".docpack":
                self._show_error("File must be a .docpack file")
                return
        elif not path.is_dir():
            self._show_error("Path must be a file or directory")
            return

        self.dismiss(path)

    def _show_error(self, message: str) -> None:
        """Display an error message."""
        error_label = self.query_one("#error-label", Label)
        error_label.update(message)
