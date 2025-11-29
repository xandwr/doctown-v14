"""
NotesPanel widget - displays marginalia content.

The living layer of a docpack: notes, artifacts, sessions, and workflow outputs.
This is where agent-generated summaries, extracted TODOs, and user notes live.

Completes the two-realm model:
- Frozen reality: files, chunks, vectors
- Living marginalia: notes, sessions, artifacts
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.message import Message
from textual.widgets import Button, Label, Static

if TYPE_CHECKING:
    from docpack.storage.marginalia import Artifact, Note, Session


@dataclass
class MarginaliaItem:
    """Unified item for display in the notes list."""

    id: str
    item_type: str  # "note", "artifact", "session"
    title: str
    subtitle: str | None
    date: str
    content: str


class NotesPanel(Static):
    """Display marginalia - notes, artifacts, and sessions."""

    class ItemSelected(Message):
        """Fired when a marginalia item is selected for viewing."""

        def __init__(self, item: MarginaliaItem) -> None:
            super().__init__()
            self.item = item

    DEFAULT_CSS = """
    NotesPanel {
        width: 100%;
        height: 100%;
        background: $surface;
    }

    NotesPanel > VerticalScroll {
        width: 100%;
        height: 100%;
        padding: 1 1;
    }

    NotesPanel .section-title {
        width: 100%;
        text-style: bold;
        color: $primary;
        padding: 0 1;
        padding-bottom: 1;
        border-bottom: solid $primary-darken-2;
        margin-bottom: 1;
    }

    NotesPanel .empty-message {
        width: 100%;
        color: $text-disabled;
        text-style: italic;
        padding: 1;
    }

    NotesPanel .note-item {
        width: 100%;
        height: auto;
        min-height: 3;
        padding: 0 1;
        margin-bottom: 1;
        border: none;
        background: $surface;
        text-align: left;
    }

    NotesPanel .note-item:hover {
        background: $primary-darken-2;
    }

    NotesPanel .note-item:focus {
        background: $primary-darken-1;
    }

    NotesPanel .note-date {
        color: $text-muted;
        text-style: dim;
    }

    NotesPanel .note-title {
        color: $text;
    }

    NotesPanel .note-subtitle {
        color: $text-muted;
        text-style: italic;
    }

    NotesPanel .type-icon {
        color: $primary;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._conn: sqlite3.Connection | None = None
        self._items: list[MarginaliaItem] = []

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield Label("📝 Marginalia", classes="section-title")
            yield Label(
                "No marginalia loaded",
                classes="empty-message",
                id="notes-empty",
            )

    def set_connection(self, conn: sqlite3.Connection) -> None:
        """Set the database connection and load marginalia."""
        self._conn = conn
        self._load_marginalia()

    def _load_marginalia(self) -> None:
        """Load all marginalia items from the database."""
        if not self._conn:
            return

        from docpack.storage.marginalia import (
            get_all_artifacts,
            get_all_notes,
            get_all_sessions,
        )

        self._items = []

        # Load notes
        try:
            notes = get_all_notes(self._conn)
            for note in notes:
                self._items.append(
                    MarginaliaItem(
                        id=f"note:{note.id}",
                        item_type="note",
                        title=note.key,
                        subtitle=f"by {note.author}" if note.author else None,
                        date=self._format_date(note.updated_at),
                        content=note.content,
                    )
                )
        except Exception:
            pass

        # Load artifacts
        try:
            artifacts = get_all_artifacts(self._conn)
            for artifact in artifacts:
                # Determine icon based on content type
                icon = self._get_artifact_icon(artifact.content_type)
                self._items.append(
                    MarginaliaItem(
                        id=f"artifact:{artifact.id}",
                        item_type="artifact",
                        title=f"{icon} {artifact.name}",
                        subtitle=artifact.content_type,
                        date=self._format_date(artifact.created_at),
                        content=artifact.content,
                    )
                )
        except Exception:
            pass

        # Load sessions with tasks
        try:
            sessions = get_all_sessions(self._conn)
            for session in sessions:
                if session.task:  # Only show sessions with tasks
                    self._items.append(
                        MarginaliaItem(
                            id=f"session:{session.id}",
                            item_type="session",
                            title=f"🔍 {session.task[:30]}{'...' if len(session.task) > 30 else ''}",
                            subtitle=f"{session.tool_calls} tool calls",
                            date=self._format_date(session.started_at),
                            content=self._format_session_content(session),
                        )
                    )
        except Exception:
            pass

        # Sort by date (newest first)
        self._items.sort(key=lambda x: x.date, reverse=True)

        # Update the UI
        self._render_items()

    def _format_date(self, iso_date: str) -> str:
        """Format ISO date string for display."""
        try:
            dt = datetime.fromisoformat(iso_date.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d")
        except (ValueError, AttributeError):
            return iso_date[:10] if iso_date else "Unknown"

    def _get_artifact_icon(self, content_type: str | None) -> str:
        """Get an icon for the artifact based on content type."""
        if not content_type:
            return "📄"
        if "json" in content_type:
            return "📋"
        if "markdown" in content_type:
            return "📝"
        if "todo" in content_type.lower():
            return "✅"
        if "summary" in content_type.lower():
            return "📊"
        return "📄"

    def _format_session_content(self, session) -> str:
        """Format session details for display."""
        lines = [
            f"# Session: {session.task or 'Untitled'}",
            "",
            f"**Started:** {session.started_at}",
            f"**Ended:** {session.ended_at or 'In progress'}",
            f"**Tool Calls:** {session.tool_calls}",
            f"**ID:** `{session.id}`",
        ]
        return "\n".join(lines)

    def _render_items(self) -> None:
        """Render the marginalia items list."""
        scroll = self.query_one(VerticalScroll)

        # Remove existing items (except section title)
        for widget in list(scroll.children):
            if not isinstance(widget, Label) or "section-title" not in widget.classes:
                widget.remove()

        if not self._items:
            scroll.mount(
                Label(
                    "No marginalia yet",
                    classes="empty-message",
                    id="notes-empty",
                )
            )
            return

        # Add items as buttons
        for item in self._items:
            # Format the button label
            label = f"[{item.date}] {item.title}"
            btn = Button(
                label,
                id=f"item-{item.id}",
                classes="note-item",
            )
            scroll.mount(btn)

    def refresh_items(self) -> None:
        """Refresh the marginalia list from the database."""
        self._load_marginalia()

    @on(Button.Pressed, ".note-item")
    def on_item_pressed(self, event: Button.Pressed) -> None:
        """Handle item selection."""
        button_id = event.button.id or ""
        if button_id.startswith("item-"):
            item_key = button_id[5:]  # Remove "item-" prefix
            # Find the matching item
            for item in self._items:
                if item.id == item_key:
                    self.post_message(self.ItemSelected(item))
                    break

    def clear(self) -> None:
        """Clear the notes panel."""
        self._conn = None
        self._items = []

        scroll = self.query_one(VerticalScroll)
        for widget in list(scroll.children):
            if not isinstance(widget, Label) or "section-title" not in widget.classes:
                widget.remove()

        scroll.mount(
            Label(
                "No marginalia loaded",
                classes="empty-message",
                id="notes-empty",
            )
        )
