"""
FileViewer widget - displays file contents with syntax highlighting.

Renders markdown natively, shows code with highlighting, and handles binary files.
"""

from pathlib import PurePosixPath

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Label, Markdown, Static, TextArea


class FileViewer(Static):
    """Display file contents with appropriate rendering."""

    DEFAULT_CSS = """
    FileViewer {
        width: 100%;
        height: 100%;
        background: $surface;
    }

    FileViewer > Vertical {
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

    FileViewer Markdown {
        width: 100%;
        height: 100%;
        padding: 1 2;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._current_path: str | None = None
        self._current_content: str | None = None

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("No file selected", classes="file-header file-path", id="file-path")
            with Vertical(classes="file-content", id="content-area"):
                yield Label("Select a file to view its contents", classes="empty-state")

    def show_file(self, path: str, content: str | None, is_binary: bool = False) -> None:
        """Display a file's contents."""
        self._current_path = path
        self._current_content = content

        # Update header
        header = self.query_one("#file-path", Label)
        header.update(f"📄 {path}")

        # Clear content area
        content_area = self.query_one("#content-area", Vertical)
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
            # Render markdown
            content_area.mount(Markdown(content))
        else:
            # Show as code with TextArea (read-only)
            language = self._get_language(ext)
            text_area = TextArea(
                content,
                language=language,
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
        """Scroll to highlight a specific chunk in the file."""
        if start_char is None or self._current_content is None:
            return

        # Find the line number for the start position
        content_before = self._current_content[:start_char]
        line_number = content_before.count("\n")

        # Try to scroll the TextArea to that line
        try:
            text_area = self.query_one(".code-view", TextArea)
            # Move cursor to the line
            text_area.cursor_location = (line_number, 0)
            text_area.scroll_cursor_visible()
        except Exception:
            pass  # TextArea might not exist (e.g., markdown file)

    def clear(self) -> None:
        """Clear the viewer."""
        self._current_path = None
        self._current_content = None

        header = self.query_one("#file-path", Label)
        header.update("No file selected")

        content_area = self.query_one("#content-area", Vertical)
        content_area.remove_children()
        content_area.mount(Label("Select a file to view its contents", classes="empty-state"))
