"""
DropZone widget - the landing page for Flight Deck.

Handles:
- Visual drop target for files/folders
- File browser dialog
- Recent docpacks list
- Routing to viewer or freeze workflow
"""

from pathlib import Path
from typing import Callable

from textual import on
from textual.app import ComposeResult
from textual.containers import Center, Vertical
from textual.message import Message
from textual.widgets import Button, Label, Static


class DropZone(Static):
    """A drop zone for docpacks and folders."""

    class DocpackSelected(Message):
        """Fired when a docpack is selected for viewing."""

        def __init__(self, path: Path) -> None:
            super().__init__()
            self.path = path

    class FolderSelected(Message):
        """Fired when a folder is selected for freezing."""

        def __init__(self, path: Path) -> None:
            super().__init__()
            self.path = path

    DEFAULT_CSS = """
    DropZone {
        width: 100%;
        height: 100%;
        align: center middle;
    }

    DropZone > Vertical {
        width: 80%;
        max-width: 60;
        height: auto;
        padding: 2 4;
        border: dashed $primary;
        background: $surface;
    }

    DropZone .drop-icon {
        width: 100%;
        text-align: center;
        text-style: bold;
        color: $primary;
        padding-bottom: 1;
    }

    DropZone .drop-title {
        width: 100%;
        text-align: center;
        text-style: bold;
        padding-bottom: 1;
    }

    DropZone .drop-hint {
        width: 100%;
        text-align: center;
        color: $text-muted;
        padding-bottom: 1;
    }

    DropZone .button-row {
        width: 100%;
        height: auto;
        align: center middle;
        padding-top: 1;
    }

    DropZone #browse-btn {
        margin: 0 1;
    }

    DropZone .recent-section {
        width: 100%;
        height: auto;
        padding-top: 2;
        border-top: solid $primary-darken-2;
        margin-top: 1;
    }

    DropZone .recent-title {
        width: 100%;
        text-align: center;
        color: $text-muted;
        text-style: italic;
        padding-bottom: 1;
    }

    DropZone .recent-item {
        width: 100%;
        text-align: center;
        padding: 0 1;
    }

    DropZone .recent-item:hover {
        background: $primary-darken-2;
        color: $text;
    }

    DropZone .empty-recent {
        width: 100%;
        text-align: center;
        color: $text-disabled;
        text-style: italic;
    }
    """

    def __init__(
        self,
        recent_docpacks: list[Path] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.recent_docpacks = recent_docpacks or []

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("📦", classes="drop-icon")
            yield Label("Flight Deck", classes="drop-title")
            yield Label("Drop a .docpack to explore", classes="drop-hint")
            yield Label("Drop a folder to create one", classes="drop-hint")

            with Center(classes="button-row"):
                yield Button("Browse", id="browse-btn", variant="primary")

            # Recent docpacks section
            if self.recent_docpacks:
                with Vertical(classes="recent-section"):
                    yield Label("Recent", classes="recent-title")
                    for docpack in self.recent_docpacks[:5]:
                        yield Button(
                            docpack.name,
                            id=f"recent-{docpack.name}",
                            classes="recent-item",
                            variant="default",
                        )
            else:
                with Vertical(classes="recent-section"):
                    yield Label("Recent", classes="recent-title")
                    yield Label("No recent docpacks", classes="empty-recent")

    @on(Button.Pressed, "#browse-btn")
    def on_browse(self, event: Button.Pressed) -> None:
        """Open file browser dialog."""
        # For now, we'll use a simple path input
        # In a full implementation, this would open a native file dialog
        self.app.push_screen("path_input")

    @on(Button.Pressed, ".recent-item")
    def on_recent_selected(self, event: Button.Pressed) -> None:
        """Handle recent docpack selection."""
        button_id = event.button.id or ""
        if button_id.startswith("recent-"):
            name = button_id[7:]  # Remove "recent-" prefix
            # Find the matching path
            for docpack in self.recent_docpacks:
                if docpack.name == name:
                    self.post_message(self.DocpackSelected(docpack))
                    break

    def handle_path(self, path: Path) -> None:
        """Process a path - either a docpack or folder."""
        if not path.exists():
            self.notify(f"Path not found: {path}", severity="error")
            return

        if path.is_file() and path.suffix == ".docpack":
            self.post_message(self.DocpackSelected(path))
        elif path.is_dir():
            self.post_message(self.FolderSelected(path))
        else:
            self.notify(
                f"Expected .docpack file or folder, got: {path.name}",
                severity="warning",
            )
