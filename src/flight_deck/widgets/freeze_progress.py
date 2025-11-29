"""
FreezeProgress widget - shows progress during docpack creation.

Displays stages: Ingesting → Chunking → Embedding → Complete
"""

from pathlib import Path
from typing import Callable

from textual import work
from textual.app import ComposeResult
from textual.containers import Center, Vertical
from textual.message import Message
from textual.widgets import Button, Label, ProgressBar, Static


class FreezeProgress(Static):
    """Progress display for freezing a folder into a docpack."""

    class FreezeComplete(Message):
        """Fired when freeze completes successfully."""

        def __init__(self, output_path: Path) -> None:
            super().__init__()
            self.output_path = output_path

    class FreezeFailed(Message):
        """Fired when freeze fails."""

        def __init__(self, error: str) -> None:
            super().__init__()
            self.error = error

    class FreezeCancelled(Message):
        """Fired when freeze is cancelled."""

        pass

    DEFAULT_CSS = """
    FreezeProgress {
        width: 100%;
        height: 100%;
        align: center middle;
    }

    FreezeProgress > Vertical {
        width: 80%;
        max-width: 70;
        height: auto;
        padding: 2 4;
        border: solid $primary;
        background: $surface;
    }

    FreezeProgress .freeze-title {
        width: 100%;
        text-align: center;
        text-style: bold;
        padding-bottom: 1;
    }

    FreezeProgress .freeze-source {
        width: 100%;
        text-align: center;
        color: $text-muted;
        padding-bottom: 2;
    }

    FreezeProgress .stage-container {
        width: 100%;
        height: auto;
        padding: 1 0;
    }

    FreezeProgress .stage-row {
        width: 100%;
        height: 1;
    }

    FreezeProgress .stage-icon {
        width: 3;
    }

    FreezeProgress .stage-name {
        width: 1fr;
    }

    FreezeProgress .stage-status {
        width: auto;
        color: $text-muted;
    }

    FreezeProgress .stage-pending .stage-icon {
        color: $text-disabled;
    }

    FreezeProgress .stage-active .stage-icon {
        color: $warning;
    }

    FreezeProgress .stage-complete .stage-icon {
        color: $success;
    }

    FreezeProgress .stage-error .stage-icon {
        color: $error;
    }

    FreezeProgress .progress-section {
        width: 100%;
        padding: 1 0;
    }

    FreezeProgress ProgressBar {
        width: 100%;
    }

    FreezeProgress .status-message {
        width: 100%;
        text-align: center;
        color: $text-muted;
        padding-top: 1;
    }

    FreezeProgress .error-message {
        width: 100%;
        text-align: center;
        color: $error;
        padding-top: 1;
    }

    FreezeProgress .button-row {
        width: 100%;
        height: auto;
        align: center middle;
        padding-top: 2;
    }
    """

    STAGES = [
        ("ingest", "Ingesting files"),
        ("chunk", "Chunking text"),
        ("embed", "Generating embeddings"),
        ("complete", "Complete"),
    ]

    def __init__(self, source_path: Path, output_path: Path | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.source_path = source_path
        self.output_path = output_path
        self._current_stage = 0
        self._cancelled = False
        self._error: str | None = None

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("📦 Creating Docpack", classes="freeze-title")
            yield Label(f"From: {self.source_path.name}", classes="freeze-source")

            # Stage indicators
            with Vertical(classes="stage-container"):
                for i, (stage_id, stage_name) in enumerate(self.STAGES):
                    state = "pending"
                    icon = "○"
                    yield Label(
                        f"{icon}  {stage_name}",
                        id=f"stage-{stage_id}",
                        classes=f"stage-row stage-{state}",
                    )

            # Progress bar
            with Vertical(classes="progress-section"):
                yield ProgressBar(total=100, show_eta=False, id="progress")
                yield Label("Preparing...", id="status", classes="status-message")

            # Buttons
            with Center(classes="button-row"):
                yield Button("Cancel", id="cancel-btn", variant="error")

    def on_mount(self) -> None:
        """Start the freeze operation when mounted."""
        self._run_freeze()

    @work(thread=True)
    def _run_freeze(self) -> None:
        """Run the freeze operation in a background thread."""
        from docpack.ingest import freeze

        try:
            self.call_from_thread(self._set_stage, 0)  # Ingest
            self.call_from_thread(self._update_status, "Reading files...")

            # Run freeze
            output = freeze(
                str(self.source_path),
                output=str(self.output_path) if self.output_path else None,
                verbose=False,
            )

            if self._cancelled:
                self.call_from_thread(self._on_cancelled)
                return

            # Update stages (freeze does all stages internally)
            self.call_from_thread(self._set_stage, 1)  # Chunk
            self.call_from_thread(self._update_status, "Processing text...")

            self.call_from_thread(self._set_stage, 2)  # Embed
            self.call_from_thread(self._update_status, "Computing embeddings...")

            self.call_from_thread(self._set_stage, 3)  # Complete
            self.call_from_thread(self._update_status, "Done!")
            self.call_from_thread(self._update_progress, 100)

            self.call_from_thread(self._on_complete, output)

        except Exception as e:
            self.call_from_thread(self._on_error, str(e))

    def _set_stage(self, stage_index: int) -> None:
        """Update the current stage display."""
        self._current_stage = stage_index

        for i, (stage_id, stage_name) in enumerate(self.STAGES):
            label = self.query_one(f"#stage-{stage_id}", Label)

            if i < stage_index:
                # Completed
                label.update(f"✓  {stage_name}")
                label.set_classes("stage-row stage-complete")
            elif i == stage_index:
                # Active
                label.update(f"●  {stage_name}")
                label.set_classes("stage-row stage-active")
            else:
                # Pending
                label.update(f"○  {stage_name}")
                label.set_classes("stage-row stage-pending")

        # Update progress bar
        progress_pct = (stage_index / len(self.STAGES)) * 100
        self._update_progress(progress_pct)

    def _update_status(self, message: str) -> None:
        """Update the status message."""
        status = self.query_one("#status", Label)
        status.update(message)
        status.remove_class("error-message")
        status.add_class("status-message")

    def _update_progress(self, percent: float) -> None:
        """Update the progress bar."""
        progress = self.query_one("#progress", ProgressBar)
        progress.progress = percent

    def _on_complete(self, output_path: Path) -> None:
        """Handle successful completion."""
        # Change cancel button to "Open"
        cancel_btn = self.query_one("#cancel-btn", Button)
        cancel_btn.label = "Open Docpack"
        cancel_btn.variant = "success"
        cancel_btn.id = "open-btn"

        self.post_message(self.FreezeComplete(output_path))

    def _on_error(self, error: str) -> None:
        """Handle error."""
        self._error = error

        # Mark current stage as error
        stage_id, stage_name = self.STAGES[self._current_stage]
        label = self.query_one(f"#stage-{stage_id}", Label)
        label.update(f"✗  {stage_name}")
        label.set_classes("stage-row stage-error")

        # Update status
        status = self.query_one("#status", Label)
        status.update(f"Error: {error}")
        status.remove_class("status-message")
        status.add_class("error-message")

        # Change button to "Back"
        cancel_btn = self.query_one("#cancel-btn", Button)
        cancel_btn.label = "Back"
        cancel_btn.variant = "default"

        self.post_message(self.FreezeFailed(error))

    def _on_cancelled(self) -> None:
        """Handle cancellation."""
        self._update_status("Cancelled")
        self.post_message(self.FreezeCancelled())

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "cancel-btn":
            self._cancelled = True
            self.post_message(self.FreezeCancelled())
        elif event.button.id == "open-btn":
            # Signal to open the docpack
            if self.output_path:
                self.post_message(self.FreezeComplete(self.output_path))
