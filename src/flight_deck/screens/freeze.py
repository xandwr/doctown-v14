"""
FreezeScreen - shows progress while creating a docpack.

Displays the freeze progress widget and handles completion/errors.
"""

from pathlib import Path

from textual import on
from textual.app import ComposeResult
from textual.screen import Screen

from flight_deck.widgets import FreezeProgress, WindowLayout


class FreezeScreen(Screen):
    """Screen for freezing a folder into a docpack."""

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(self, source_path: Path, output_path: Path | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.source_path = source_path
        self.output_path = output_path or source_path.with_suffix(".docpack")

    def compose(self) -> ComposeResult:
        progress = FreezeProgress(
            source_path=self.source_path,
            output_path=self.output_path,
        )
        yield WindowLayout(f"Creating: {self.output_path.name}", progress)

    @on(FreezeProgress.FreezeComplete)
    def on_freeze_complete(self, event: FreezeProgress.FreezeComplete) -> None:
        """Handle successful freeze - open the new docpack."""
        self.app.open_docpack(event.output_path)

    @on(FreezeProgress.FreezeFailed)
    def on_freeze_failed(self, event: FreezeProgress.FreezeFailed) -> None:
        """Handle freeze failure - show error and allow retry."""
        self.notify(f"Freeze failed: {event.error}", severity="error")

    @on(FreezeProgress.FreezeCancelled)
    def on_freeze_cancelled(self, event: FreezeProgress.FreezeCancelled) -> None:
        """Handle cancellation - return to home."""
        self.app.pop_screen()

    def action_cancel(self) -> None:
        """Handle escape - return to home."""
        self.app.pop_screen()
