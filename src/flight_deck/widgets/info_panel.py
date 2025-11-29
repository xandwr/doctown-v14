"""
InfoPanel widget - displays docpack metadata and statistics.

Shows version info, file counts, embedding details, and marginalia stats.
"""

from typing import Any

from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.widgets import Label, Static


class InfoPanel(Static):
    """Display docpack information and statistics."""

    DEFAULT_CSS = """
    InfoPanel {
        width: 100%;
        height: 100%;
        background: $surface;
    }

    InfoPanel > VerticalScroll {
        width: 100%;
        height: 100%;
        padding: 1 2;
    }

    InfoPanel .section-title {
        width: 100%;
        text-style: bold;
        color: $primary;
        padding-bottom: 1;
        border-bottom: solid $primary-darken-2;
        margin-bottom: 1;
    }

    InfoPanel .section {
        width: 100%;
        height: auto;
        padding-bottom: 2;
    }

    InfoPanel .stat-row {
        width: 100%;
        height: 1;
    }

    InfoPanel .stat-label {
        color: $text-muted;
    }

    InfoPanel .stat-value {
        color: $text;
        text-style: bold;
    }

    InfoPanel .empty-message {
        color: $text-disabled;
        text-style: italic;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._stats: dict[str, Any] = {}
        self._metadata: dict[str, str] = {}

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            # Version section
            with Vertical(classes="section", id="version-section"):
                yield Label("📋 Version", classes="section-title")
                yield Label("No docpack loaded", classes="empty-message", id="version-content")

            # Stats section
            with Vertical(classes="section", id="stats-section"):
                yield Label("📊 Statistics", classes="section-title")
                yield Label("No docpack loaded", classes="empty-message", id="stats-content")

            # Embedding section
            with Vertical(classes="section", id="embed-section"):
                yield Label("🧠 Embeddings", classes="section-title")
                yield Label("No docpack loaded", classes="empty-message", id="embed-content")

            # Source section
            with Vertical(classes="section", id="source-section"):
                yield Label("📁 Source", classes="section-title")
                yield Label("No docpack loaded", classes="empty-message", id="source-content")

    def load_info(self, stats: dict[str, Any], metadata: dict[str, str]) -> None:
        """Load and display docpack information."""
        self._stats = stats
        self._metadata = metadata

        # Update version section
        version_section = self.query_one("#version-section", Vertical)
        version_content = self.query_one("#version-content")
        version_content.remove()

        format_ver = metadata.get("format_version", "N/A")
        docpack_ver = metadata.get("docpack_version", "N/A")
        created = metadata.get("created_at", "N/A")

        version_section.mount(Label(f"Format: {format_ver}", classes="stat-row"))
        version_section.mount(Label(f"Docpack: {docpack_ver}", classes="stat-row"))
        version_section.mount(Label(f"Created: {created}", classes="stat-row"))

        # Update stats section
        stats_section = self.query_one("#stats-section", Vertical)
        stats_content = self.query_one("#stats-content")
        stats_content.remove()

        total_files = stats.get("total_files", 0)
        total_chunks = stats.get("total_chunks", 0)
        total_vectors = stats.get("total_vectors", 0)
        total_size = stats.get("total_size_bytes", 0)

        stats_section.mount(Label(f"Files: {total_files:,}", classes="stat-row"))
        stats_section.mount(Label(f"Chunks: {total_chunks:,}", classes="stat-row"))
        stats_section.mount(Label(f"Vectors: {total_vectors:,}", classes="stat-row"))
        stats_section.mount(Label(f"Content: {self._format_size(total_size)}", classes="stat-row"))

        # Update embedding section
        embed_section = self.query_one("#embed-section", Vertical)
        embed_content = self.query_one("#embed-content")
        embed_content.remove()

        model = metadata.get("embedding_model", "N/A")
        dims = metadata.get("embedding_dims", "N/A")

        embed_section.mount(Label(f"Model: {model}", classes="stat-row"))
        embed_section.mount(Label(f"Dimensions: {dims}", classes="stat-row"))

        # Update source section
        source_section = self.query_one("#source-section", Vertical)
        source_content = self.query_one("#source-content")
        source_content.remove()

        source = metadata.get("source", "N/A")
        source_section.mount(Label(f"{source}", classes="stat-row"))

    def _format_size(self, size_bytes: int) -> str:
        """Format byte size for display."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

    def clear(self) -> None:
        """Clear the info panel."""
        self._stats = {}
        self._metadata = {}

        # Reset all sections to empty state
        for section_id in ["version", "stats", "embed", "source"]:
            section = self.query_one(f"#{section_id}-section", Vertical)
            content = self.query_one(f"#{section_id}-content")
            if content:
                # Already has placeholder
                pass
            else:
                # Add placeholder back
                section.mount(
                    Label("No docpack loaded", classes="empty-message", id=f"{section_id}-content")
                )
