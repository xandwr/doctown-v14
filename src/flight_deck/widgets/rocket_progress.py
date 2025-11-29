"""
RocketProgress widget - animated launch progress.

Shows a rocket flying from left (0%) to right (100%) with
a log panel below for verbose output.

The ultimate post-modern terminal-web-hybrid progress indicator.
"""

from textual import work
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Label, RichLog, Static


# Rocket ASCII art frames for animation
ROCKET = "🚀"
ROCKET_TRAIL = "═"
LAUNCH_PAD = "▓"
SKY = "░"


class RocketProgress(Static):
    """Animated rocket progress indicator."""

    class LaunchComplete(Message):
        """Fired when launch completes."""

        def __init__(self, success: bool, output_path: str | None = None) -> None:
            super().__init__()
            self.success = success
            self.output_path = output_path

    DEFAULT_CSS = """
    RocketProgress {
        width: 100%;
        height: auto;
        padding: 1 2;
    }

    RocketProgress > Vertical {
        width: 100%;
        height: auto;
    }

    RocketProgress .launch-title {
        width: 100%;
        text-align: center;
        text-style: bold;
        padding-bottom: 1;
    }

    RocketProgress .sky-container {
        width: 100%;
        height: 3;
        background: $surface;
        border: solid $primary-darken-2;
    }

    RocketProgress .rocket-track {
        width: 100%;
        height: 1;
        padding: 0 1;
    }

    RocketProgress .progress-label {
        width: 100%;
        text-align: center;
        color: $text-muted;
        padding: 1 0;
    }

    RocketProgress .stage-label {
        width: 100%;
        text-align: center;
        color: $primary;
        text-style: bold;
    }

    RocketProgress .log-container {
        width: 100%;
        height: 10;
        border: solid $primary-darken-2;
        background: $surface-darken-1;
        margin-top: 1;
    }

    RocketProgress RichLog {
        width: 100%;
        height: 100%;
        padding: 0 1;
    }
    """

    progress = reactive(0.0)
    stage = reactive("Preparing for launch...")

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._track_width = 50

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("🚀 Launching Docpack", classes="launch-title")

            # Sky/track area
            with Vertical(classes="sky-container"):
                yield Label("", classes="rocket-track", id="track")

            yield Label("0%", classes="progress-label", id="progress-pct")
            yield Label("Preparing for launch...", classes="stage-label", id="stage-label")

            # Log output
            with Vertical(classes="log-container"):
                yield RichLog(id="launch-log", highlight=True, markup=True)

    def on_mount(self) -> None:
        """Initial render."""
        self._update_rocket()

    def watch_progress(self, value: float) -> None:
        """React to progress changes."""
        self._update_rocket()
        pct_label = self.query_one("#progress-pct", Label)
        pct_label.update(f"{int(value)}%")

    def watch_stage(self, value: str) -> None:
        """React to stage changes."""
        stage_label = self.query_one("#stage-label", Label)
        stage_label.update(value)

    def _update_rocket(self) -> None:
        """Render the rocket at current position."""
        track = self.query_one("#track", Label)

        # Calculate rocket position
        track_width = self._track_width
        rocket_pos = int((self.progress / 100) * (track_width - 1))

        # Build the track string
        trail = ROCKET_TRAIL * rocket_pos
        space_after = " " * (track_width - rocket_pos - 1)

        # Colorize with Rich markup
        track_str = f"[dim]{trail}[/dim]{ROCKET}[dim]{space_after}[/dim]"
        track.update(track_str)

    def log(self, message: str, style: str = "") -> None:
        """Add a message to the log."""
        log_widget = self.query_one("#launch-log", RichLog)
        if style:
            log_widget.write(f"[{style}]{message}[/{style}]")
        else:
            log_widget.write(message)

    def set_progress(self, pct: float, stage: str | None = None) -> None:
        """Update progress and optionally the stage."""
        self.progress = min(100, max(0, pct))
        if stage:
            self.stage = stage

    def complete(self, success: bool = True, output_path: str | None = None) -> None:
        """Mark launch as complete."""
        if success:
            self.progress = 100
            self.stage = "🎉 Launch successful!"
            self.log("✓ Docpack created successfully!", style="green bold")
            if output_path:
                self.log(f"  Output: {output_path}", style="green")
        else:
            self.stage = "💥 Launch failed!"
            self.log("✗ Launch failed", style="red bold")

        self.post_message(self.LaunchComplete(success, output_path))
