"""
FileViewer widget - displays file contents with syntax highlighting.

Renders markdown natively, shows code with highlighting, and handles binary files.
"""

import uuid
from pathlib import PurePosixPath

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Label, MarkdownViewer, Static, TextArea


class FileViewer(Static):
    """Display file contents with appropriate rendering."""

    DEFAULT_CSS = """
    FileViewer {
        width: 100%;
        height: 100%;
        background: $surface;
    }

    FileViewer > VerticalScroll {
        width: 100%;
        height: 100%;
    }

    FileViewer .file-header {
        width: 100%;
        height: 1;
        background: $primary-darken-1;
        padding: 0 1;
    }

    FileViewer .file-path {
        color: $text;
        text-style: bold;
    }

    FileViewer .file-content {
        width: 100%;
        height: 1fr;
    }

    FileViewer .empty-state {
        width: 100%;
        height: 100%;
        content-align: center middle;
        color: $text-muted;
        text-style: italic;
    }

    FileViewer .binary-warning {
        width: 100%;
        height: 100%;
        content-align: center middle;
        color: $warning;
    }

    FileViewer TextArea {
        width: 100%;
        height: 100%;
    }

    FileViewer MarkdownViewer {
        width: 100%;
        height: 100%;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._current_path: str | None = None
        self._current_content: str | None = None

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield Label("No file selected", classes="file-header file-path", id="file-path")
            with VerticalScroll(classes="file-content", id="content-area"):
                yield Label("Select a file to view its contents", classes="empty-state")

    def show_file(self, path: str, content: str | None, is_binary: bool = False) -> None:
        """Display a file's contents."""
        self._current_path = path
        self._current_content = content

        # Update header
        header = self.query_one("#file-path", Label)
        header.update(f"📄 {path}")

        # Clear content area
        content_area = self.query_one("#content-area", VerticalScroll)
        content_area.remove_children()

        if is_binary:
            content_area.mount(
                Label("🔒 Binary file - cannot display contents", classes="binary-warning")
            )
            return

        if content is None or content == "":
            content_area.mount(Label("(empty file)", classes="empty-state"))
            return

        # Choose renderer based on file type
        ext = PurePosixPath(path).suffix.lower()

        if ext == ".md":
            # Render markdown with TOC navigator
            # Use unique ID to avoid conflicts when switching files
            viewer = MarkdownViewer(
                content,
                show_table_of_contents=True,
                id=f"md-viewer-{uuid.uuid4().hex[:8]}",
            )
            content_area.mount(viewer)
        else:
            # Show as code with TextArea (read-only)
            language = self._get_language(ext)
            text_area = TextArea(
                content,
                language=language,
                theme="monokai",
                read_only=True,
                show_line_numbers=True,
                classes="code-view",
            )
            content_area.mount(text_area)

    def _get_language(self, ext: str) -> str | None:
        """Map file extension to TextArea language."""
        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".tsx": "tsx",
            ".jsx": "javascript",
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".toml": "toml",
            ".html": "html",
            ".css": "css",
            ".sql": "sql",
            ".sh": "bash",
            ".bash": "bash",
            ".zsh": "bash",
            ".rs": "rust",
            ".go": "go",
            ".java": "java",
            ".c": "c",
            ".cpp": "cpp",
            ".h": "c",
            ".rb": "ruby",
            ".xml": "xml",
            ".md": "markdown",
        }
        return language_map.get(ext)

    def scroll_to_chunk(self, start_char: int | None, end_char: int | None) -> None:
        """Scroll to and highlight a specific chunk in the file."""
        if start_char is None or self._current_content is None:
            return

        # Calculate start position (line, column)
        content_before_start = self._current_content[:start_char]
        start_line = content_before_start.count("\n")
        last_newline = content_before_start.rfind("\n")
        start_col = start_char - last_newline - 1 if last_newline >= 0 else start_char

        # Calculate end position if provided
        if end_char is not None:
            content_before_end = self._current_content[:end_char]
            end_line = content_before_end.count("\n")
            last_newline_end = content_before_end.rfind("\n")
            end_col = end_char - last_newline_end - 1 if last_newline_end >= 0 else end_char
        else:
            # Default to selecting to end of line
            end_line = start_line
            line_end = self._current_content.find("\n", start_char)
            end_col = line_end - start_char + start_col if line_end >= 0 else len(self._current_content) - start_char + start_col

        # Try to scroll and select in the TextArea
        try:
            text_area = self.query_one(".code-view", TextArea)
            # Move cursor to start position
            text_area.cursor_location = (start_line, start_col)
            # Select the chunk range
            text_area.selection = ((start_line, start_col), (end_line, end_col))
            text_area.scroll_cursor_visible()
        except Exception:
            pass  # TextArea might not exist (e.g., markdown file)

    def clear(self) -> None:
        """Clear the viewer."""
        self._current_path = None
        self._current_content = None

        header = self.query_one("#file-path", Label)
        header.update("No file selected")

        content_area = self.query_one("#content-area", VerticalScroll)
        content_area.remove_children()
        content_area.mount(Label("Select a file to view its contents", classes="empty-state"))
