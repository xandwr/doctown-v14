"""
GenerateScreen - staged docpack creation wizard.

A multi-step wizard for creating docpacks:
1. Source - Select files/folders to ingest
2. Configure - Tweak settings (chunking, embedding model, etc.)
3. Output - Choose destination path
4. Launch - Execute with rocket progress animation

Designed to feel like a modern web upload flow in the terminal.
"""

from pathlib import Path
from typing import Literal

from textual import on, work
from textual.app import ComposeResult
from textual.containers import Center, Grid, Horizontal, Vertical, VerticalScroll
from textual.message import Message
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import (
    Button,
    Checkbox,
    DirectoryTree,
    Input,
    Label,
    RadioButton,
    RadioSet,
    Rule,
    Static,
)

from flight_deck.widgets import NavBar, RocketProgress


StageType = Literal["source", "configure", "output", "launch"]


class GenerateScreen(Screen):
    """Multi-stage docpack generation wizard."""

    BINDINGS = [
        ("escape", "go_back", "Back"),
    ]

    DEFAULT_CSS = """
    GenerateScreen {
        layout: vertical;
    }

    GenerateScreen .page-content {
        width: 100%;
        height: 1fr;
    }

    GenerateScreen .wizard-container {
        width: 100%;
        max-width: 100;
        height: 100%;
        padding: 1 2;
    }

    /* Stage indicator */
    GenerateScreen .stage-indicator {
        width: 100%;
        height: 3;
        padding: 1 0;
    }

    GenerateScreen .stage-dots {
        width: 100%;
        height: 1;
        content-align: center middle;
    }

    GenerateScreen .stage-dot {
        width: auto;
        padding: 0 2;
        color: $text-disabled;
    }

    GenerateScreen .stage-dot.active {
        color: $primary;
        text-style: bold;
    }

    GenerateScreen .stage-dot.complete {
        color: $success;
    }

    /* Stage content */
    GenerateScreen .stage-content {
        width: 100%;
        height: 1fr;
        padding: 1 0;
    }

    GenerateScreen .stage-title {
        width: 100%;
        text-align: center;
        text-style: bold;
        padding-bottom: 1;
    }

    GenerateScreen .stage-subtitle {
        width: 100%;
        text-align: center;
        color: $text-muted;
        padding-bottom: 2;
    }

    /* Source stage */
    GenerateScreen .source-input-row {
        width: 100%;
        height: 3;
        padding: 0 2;
    }

    GenerateScreen .source-input {
        width: 1fr;
    }

    GenerateScreen .source-browse-btn {
        width: auto;
        margin-left: 1;
    }

    GenerateScreen .source-preview {
        width: 100%;
        height: 1fr;
        border: solid $primary-darken-2;
        background: $surface;
        margin-top: 1;
    }

    GenerateScreen .source-preview-label {
        width: 100%;
        padding: 1;
        color: $text-muted;
        text-style: italic;
    }

    GenerateScreen DirectoryTree {
        width: 100%;
        height: 100%;
    }

    /* Configure stage */
    GenerateScreen .config-section {
        width: 100%;
        height: auto;
        padding: 1 2;
        margin-bottom: 1;
        border: solid $primary-darken-2;
        background: $surface;
    }

    GenerateScreen .config-section-title {
        width: 100%;
        text-style: bold;
        color: $primary;
        padding-bottom: 1;
    }

    GenerateScreen .config-row {
        width: 100%;
        height: auto;
        padding: 0 1;
    }

    GenerateScreen .config-label {
        width: 20;
        color: $text-muted;
    }

    GenerateScreen .config-value {
        width: 1fr;
    }

    /* Output stage */
    GenerateScreen .output-section {
        width: 100%;
        padding: 2;
        border: solid $primary-darken-2;
        background: $surface;
    }

    GenerateScreen .output-preview {
        width: 100%;
        padding: 1;
        margin-top: 1;
        background: $surface;
        border: solid $primary-darken-2;
    }

    GenerateScreen .output-preview-path {
        color: $success;
        text-style: bold;
    }

    /* Navigation buttons */
    GenerateScreen .nav-buttons {
        width: 100%;
        height: 3;
        padding: 1 2;
        align: center middle;
    }

    GenerateScreen .nav-btn {
        margin: 0 1;
        min-width: 15;
    }

    GenerateScreen .nav-btn-primary {
        background: $primary;
    }

    GenerateScreen .nav-btn-launch {
        background: $success;
    }

    /* Launch stage */
    GenerateScreen .launch-container {
        width: 100%;
        height: 1fr;
        padding: 2;
    }
    """

    current_stage: reactive[StageType] = reactive("source")
    source_path: reactive[str] = reactive("")
    output_path: reactive[str] = reactive("")

    # Config options
    skip_chunking: reactive[bool] = reactive(False)
    skip_embedding: reactive[bool] = reactive(False)
    embedding_model: reactive[str] = reactive("google/embeddinggemma-300m")

    def __init__(self, initial_path: Path | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        if initial_path:
            self.source_path = str(initial_path)
            self.output_path = str(initial_path.with_suffix(".docpack"))

    def compose(self) -> ComposeResult:
        yield NavBar(active="generate")

        with Vertical(classes="page-content"):
            with Vertical(classes="wizard-container"):
                # Stage indicator
                with Horizontal(classes="stage-indicator"):
                    with Horizontal(classes="stage-dots"):
                        yield Label("① Source", id="dot-source", classes="stage-dot active")
                        yield Label(" → ", classes="stage-dot")
                        yield Label("② Configure", id="dot-configure", classes="stage-dot")
                        yield Label(" → ", classes="stage-dot")
                        yield Label("③ Output", id="dot-output", classes="stage-dot")
                        yield Label(" → ", classes="stage-dot")
                        yield Label("④ Launch", id="dot-launch", classes="stage-dot")

                # Stage content area
                with VerticalScroll(classes="stage-content", id="stage-content"):
                    yield from self._compose_source_stage()

                # Navigation buttons
                with Horizontal(classes="nav-buttons"):
                    yield Button("← Back", id="btn-back", classes="nav-btn", disabled=True)
                    yield Button("Next →", id="btn-next", classes="nav-btn nav-btn-primary")

    def _compose_source_stage(self) -> list:
        """Compose the source selection stage."""
        return [
            Label("📁 Select Source", classes="stage-title"),
            Label("Choose a folder, zip file, or URL to ingest", classes="stage-subtitle"),
            Horizontal(
                Input(
                    placeholder="Enter path or URL...",
                    value=self.source_path,
                    id="source-input",
                    classes="source-input",
                ),
                Button("Browse", id="browse-btn", classes="source-browse-btn"),
                classes="source-input-row",
            ),
            Vertical(
                Label("Enter a path above to preview contents", classes="source-preview-label"),
                classes="source-preview",
                id="source-preview",
            ),
        ]

    def _compose_configure_stage(self) -> list:
        """Compose the configuration stage."""
        return [
            Label("⚙️ Configure Pipeline", classes="stage-title"),
            Label("Customize how your docpack is created", classes="stage-subtitle"),
            # Processing options
            Vertical(
                Label("Processing", classes="config-section-title"),
                Checkbox("Skip chunking (raw files only)", id="opt-skip-chunk"),
                Checkbox("Skip embedding (no semantic search)", id="opt-skip-embed"),
                classes="config-section",
            ),
            # Model selection
            Vertical(
                Label("Embedding Model", classes="config-section-title"),
                RadioSet(
                    RadioButton(
                        "google/embeddinggemma-300m (default, 1024d)",
                        id="model-gemma",
                        value=True,
                    ),
                    RadioButton(
                        "sentence-transformers/all-MiniLM-L6-v2 (384d, faster)",
                        id="model-minilm",
                    ),
                    RadioButton(
                        "Custom model...",
                        id="model-custom",
                    ),
                    id="model-select",
                ),
                classes="config-section",
            ),
            # Summary
            Vertical(
                Label("Summary", classes="config-section-title"),
                Label(f"Source: {self.source_path}", id="config-summary-source"),
                Label("Chunking: Enabled", id="config-summary-chunk"),
                Label("Embedding: Enabled", id="config-summary-embed"),
                classes="config-section",
            ),
        ]

    def _compose_output_stage(self) -> list:
        """Compose the output path stage."""
        return [
            Label("📦 Output Location", classes="stage-title"),
            Label("Choose where to save your docpack", classes="stage-subtitle"),
            Vertical(
                Label("Output Path:"),
                Input(
                    value=self.output_path,
                    placeholder="/path/to/output.docpack",
                    id="output-input",
                ),
                Vertical(
                    Label("Will create:", classes="config-label"),
                    Label(
                        self.output_path or "(enter path above)",
                        id="output-preview-path",
                        classes="output-preview-path",
                    ),
                    classes="output-preview",
                ),
                classes="output-section",
            ),
        ]

    def _compose_launch_stage(self) -> list:
        """Compose the launch stage."""
        skip_parts = []
        if self.skip_chunking:
            skip_parts.append("chunking")
        if self.skip_embedding:
            skip_parts.append("embedding")
        skip_text = ", ".join(skip_parts) if skip_parts else "none"

        return [
            Label("🚀 Ready for Launch", classes="stage-title"),
            Label("Review and launch your docpack creation", classes="stage-subtitle"),
            # Summary before launch
            Vertical(
                Label("Launch Summary", classes="config-section-title"),
                Label(f"Source: {self.source_path}", id="launch-source"),
                Label(f"Output: {self.output_path}", id="launch-output"),
                Label(f"Skipping: {skip_text}", id="launch-skipping"),
                classes="config-section",
            ),
            Vertical(
                Label(
                    "Click 'Launch' to begin creating your docpack",
                    classes="stage-subtitle",
                ),
                classes="launch-container",
                id="launch-area",
            ),
        ]

    def watch_current_stage(self, stage: StageType) -> None:
        """Update UI when stage changes."""
        # Only update if we're mounted (avoid errors during initial composition)
        if not self.is_mounted:
            return
        self._update_stage_dots()
        self._update_nav_buttons()
        self._render_stage()

    def _update_stage_dots(self) -> None:
        """Update the stage indicator dots."""
        stages = ["source", "configure", "output", "launch"]
        current_idx = stages.index(self.current_stage)

        for i, stage in enumerate(stages):
            dot = self.query_one(f"#dot-{stage}", Label)
            dot.remove_class("active", "complete")

            if i < current_idx:
                dot.add_class("complete")
            elif i == current_idx:
                dot.add_class("active")

    def _update_nav_buttons(self) -> None:
        """Update navigation button states."""
        btn_back = self.query_one("#btn-back", Button)
        btn_next = self.query_one("#btn-next", Button)

        # Back button
        btn_back.disabled = self.current_stage == "source"

        # Next button
        if self.current_stage == "launch":
            btn_next.label = "🚀 Launch"
            btn_next.remove_class("nav-btn-primary")
            btn_next.add_class("nav-btn-launch")
        else:
            btn_next.label = "Next →"
            btn_next.remove_class("nav-btn-launch")
            btn_next.add_class("nav-btn-primary")

    def _render_stage(self) -> None:
        """Render the current stage content."""
        content = self.query_one("#stage-content", VerticalScroll)
        content.remove_children()

        widgets = []
        if self.current_stage == "source":
            widgets = self._compose_source_stage()
        elif self.current_stage == "configure":
            widgets = self._compose_configure_stage()
        elif self.current_stage == "output":
            widgets = self._compose_output_stage()
        elif self.current_stage == "launch":
            widgets = self._compose_launch_stage()

        for widget in widgets:
            content.mount(widget)

    @on(Button.Pressed, "#btn-next")
    def on_next(self, event: Button.Pressed) -> None:
        """Handle next button."""
        stages: list[StageType] = ["source", "configure", "output", "launch"]
        current_idx = stages.index(self.current_stage)

        if self.current_stage == "launch":
            # Execute launch
            self._execute_launch()
        elif current_idx < len(stages) - 1:
            # Validate current stage before advancing
            if self._validate_stage():
                self.current_stage = stages[current_idx + 1]

    @on(Button.Pressed, "#btn-back")
    def on_back(self, event: Button.Pressed) -> None:
        """Handle back button."""
        stages: list[StageType] = ["source", "configure", "output", "launch"]
        current_idx = stages.index(self.current_stage)

        if current_idx > 0:
            self.current_stage = stages[current_idx - 1]

    @on(Input.Changed, "#source-input")
    def on_source_changed(self, event: Input.Changed) -> None:
        """Handle source path changes."""
        self.source_path = event.value
        # Auto-generate output path
        if event.value:
            source = Path(event.value)
            self.output_path = str(source.with_suffix(".docpack"))

    @on(Input.Changed, "#output-input")
    def on_output_changed(self, event: Input.Changed) -> None:
        """Handle output path changes."""
        self.output_path = event.value
        try:
            preview = self.query_one("#output-preview-path", Label)
            preview.update(event.value or "(enter path above)")
        except Exception:
            pass

    @on(Checkbox.Changed, "#opt-skip-chunk")
    def on_skip_chunk_changed(self, event: Checkbox.Changed) -> None:
        """Handle skip chunking toggle."""
        self.skip_chunking = event.value

    @on(Checkbox.Changed, "#opt-skip-embed")
    def on_skip_embed_changed(self, event: Checkbox.Changed) -> None:
        """Handle skip embedding toggle."""
        self.skip_embedding = event.value

    def _validate_stage(self) -> bool:
        """Validate the current stage before advancing."""
        if self.current_stage == "source":
            if not self.source_path:
                self.notify("Please enter a source path", severity="error")
                return False
            source = Path(self.source_path).expanduser()
            if not source.exists():
                self.notify(f"Source not found: {source}", severity="error")
                return False
            return True

        elif self.current_stage == "output":
            if not self.output_path:
                self.notify("Please enter an output path", severity="error")
                return False
            return True

        return True

    def _execute_launch(self) -> None:
        """Execute the docpack creation."""
        # Replace content with rocket progress
        content = self.query_one("#stage-content", VerticalScroll)
        content.remove_children()

        rocket = RocketProgress(id="rocket-progress")
        content.mount(rocket)

        # Hide nav buttons during launch
        self.query_one("#btn-back", Button).disabled = True
        self.query_one("#btn-next", Button).disabled = True

        # Start the freeze operation
        self._run_freeze(rocket)

    @work(thread=True)
    def _run_freeze(self, rocket: RocketProgress) -> None:
        """Run the freeze operation in background."""
        from docpack.ingest import freeze

        source = Path(self.source_path).expanduser()
        output = Path(self.output_path).expanduser()

        try:
            self.call_from_thread(rocket.log, f"Source: {source}")
            self.call_from_thread(rocket.log, f"Output: {output}")
            self.call_from_thread(rocket.log, "")

            # Stage 1: Ingest
            self.call_from_thread(rocket.set_progress, 10, "📥 Ingesting files...")
            self.call_from_thread(rocket.log, "Reading files from source...")

            # Run freeze
            result_path = freeze(
                str(source),
                output=str(output),
                verbose=False,
                skip_chunking=self.skip_chunking,
                skip_embedding=self.skip_embedding,
                embedding_model=self.embedding_model if not self.skip_embedding else None,
            )

            # Stage 2: Chunking (if not skipped)
            if not self.skip_chunking:
                self.call_from_thread(rocket.set_progress, 40, "✂️ Chunking text...")
                self.call_from_thread(rocket.log, "Splitting into semantic chunks...")

            # Stage 3: Embedding (if not skipped)
            if not self.skip_embedding:
                self.call_from_thread(rocket.set_progress, 70, "🧠 Generating embeddings...")
                self.call_from_thread(rocket.log, f"Model: {self.embedding_model}")

            # Complete
            self.call_from_thread(rocket.set_progress, 100, "✅ Complete!")
            self.call_from_thread(rocket.complete, True, str(result_path))

            # Re-enable buttons for exploring result
            def enable_explore():
                btn = self.query_one("#btn-next", Button)
                btn.disabled = False
                btn.label = "🔍 Explore"
                btn.remove_class("nav-btn-launch")
                btn.add_class("nav-btn-primary")

            self.call_from_thread(enable_explore)

        except Exception as e:
            self.call_from_thread(rocket.log, f"Error: {e}", style="red")
            self.call_from_thread(rocket.complete, False, None)

    @on(RocketProgress.LaunchComplete)
    def on_launch_complete(self, event: RocketProgress.LaunchComplete) -> None:
        """Handle launch completion."""
        if event.success and event.output_path:
            # Store for explore button
            self._completed_path = Path(event.output_path)

    def action_go_back(self) -> None:
        """Handle escape - go back or exit."""
        if self.current_stage != "source":
            stages: list[StageType] = ["source", "configure", "output", "launch"]
            current_idx = stages.index(self.current_stage)
            if current_idx > 0:
                self.current_stage = stages[current_idx - 1]
        else:
            self.app.pop_screen()
