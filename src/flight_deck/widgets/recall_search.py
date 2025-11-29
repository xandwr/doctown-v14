"""
RecallSearch widget - semantic search interface.

Provides a search input and displays recall results from the docpack.
"""

from dataclasses import dataclass
from typing import Any

from textual import on, work
from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.message import Message
from textual.widgets import Input, Label, ListItem, ListView, Static


@dataclass
class SearchResult:
    """A search result from recall."""

    chunk_id: int
    file_id: int
    file_path: str
    chunk_index: int
    text: str
    score: float


class RecallSearch(Static):
    """Semantic search widget for docpacks."""

    class ResultSelected(Message):
        """Fired when a search result is selected."""

        def __init__(self, result: SearchResult) -> None:
            super().__init__()
            self.result = result

    DEFAULT_CSS = """
    RecallSearch {
        width: 100%;
        height: 100%;
        background: $surface;
    }

    RecallSearch > Vertical {
        width: 100%;
        height: 100%;
    }

    RecallSearch .search-header {
        width: 100%;
        height: auto;
        padding: 1;
        border-bottom: solid $primary-darken-2;
    }

    RecallSearch .search-title {
        width: 100%;
        text-style: bold;
        padding-bottom: 1;
    }

    RecallSearch #search-input {
        width: 100%;
    }

    RecallSearch .search-status {
        width: 100%;
        color: $text-muted;
        text-style: italic;
        padding-top: 1;
    }

    RecallSearch .results-container {
        width: 100%;
        height: 1fr;
    }

    RecallSearch .result-item {
        width: 100%;
        height: auto;
        padding: 1;
        border-bottom: solid $primary-darken-3;
    }

    RecallSearch .result-item:hover {
        background: $primary-darken-2;
    }

    RecallSearch .result-header {
        width: 100%;
        color: $primary;
        text-style: bold;
    }

    RecallSearch .result-score {
        color: $success;
    }

    RecallSearch .result-text {
        width: 100%;
        color: $text-muted;
        padding-top: 1;
    }

    RecallSearch .no-results {
        width: 100%;
        text-align: center;
        color: $text-disabled;
        padding: 2;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._db_path: str | None = None  # Database path for thread-safe access
        self._results: list[SearchResult] = []
        self._searching = False

    def set_connection(self, conn) -> None:
        """Set the database connection for searches.

        We extract the path from the connection to allow opening
        fresh connections in worker threads (SQLite requirement).
        """
        # Get the database path from the connection
        cursor = conn.execute("PRAGMA database_list")
        row = cursor.fetchone()
        if row:
            self._db_path = row[2]  # Third column is the file path

    def compose(self) -> ComposeResult:
        with Vertical():
            with Vertical(classes="search-header"):
                yield Label("🔍 Semantic Search", classes="search-title")
                yield Input(
                    placeholder="Search with natural language...",
                    id="search-input",
                )
                yield Label("", id="search-status", classes="search-status")

            with VerticalScroll(classes="results-container", id="results"):
                yield Label("Enter a query to search", classes="no-results")

    @on(Input.Submitted, "#search-input")
    def on_search_submitted(self, event: Input.Submitted) -> None:
        """Handle search submission."""
        query = event.value.strip()
        if query and self._db_path:
            self._do_search(query)

    @work(thread=True)
    def _do_search(self, query: str) -> None:
        """Perform the search in a background thread."""
        from docpack.recall import recall
        from docpack.storage import init_db

        self._searching = True
        self.app.call_from_thread(self._update_status, f"Searching for: {query}...")

        try:
            # Open a fresh connection in this thread (SQLite requirement)
            conn = init_db(self._db_path)
            try:
                results = recall(conn, query, k=10)
                search_results = [
                    SearchResult(
                        chunk_id=r.chunk_id,
                        file_id=r.file_id,
                        file_path=r.file_path,
                        chunk_index=r.chunk_index,
                        text=r.text,
                        score=r.score,
                    )
                    for r in results
                ]
                self.app.call_from_thread(self._show_results, search_results, query)
            finally:
                conn.close()
        except Exception as e:
            self.app.call_from_thread(self._show_error, str(e))
        finally:
            self._searching = False

    def _update_status(self, message: str) -> None:
        """Update the status label."""
        status = self.query_one("#search-status", Label)
        status.update(message)

    def _show_results(self, results: list[SearchResult], query: str) -> None:
        """Display search results."""
        self._results = results
        container = self.query_one("#results", VerticalScroll)

        # Clear existing results
        container.remove_children()

        if not results:
            container.mount(Label("No results found", classes="no-results"))
            self._update_status(f"0 results for: {query}")
            return

        self._update_status(f"{len(results)} results for: {query}")

        for i, result in enumerate(results):
            # Truncate text for display
            text = result.text
            if len(text) > 150:
                text = text[:150] + "..."

            item = ResultItem(result, index=i + 1)
            container.mount(item)

    def _show_error(self, error: str) -> None:
        """Display an error message."""
        self._update_status(f"Error: {error}")
        container = self.query_one("#results", VerticalScroll)
        container.remove_children()
        container.mount(Label(f"Search failed: {error}", classes="no-results"))


class ResultItem(Static):
    """A single search result item."""

    DEFAULT_CSS = """
    ResultItem {
        width: 100%;
        height: auto;
        padding: 1;
        border-bottom: solid $primary-darken-3;
    }

    ResultItem:hover {
        background: $primary-darken-2;
    }

    ResultItem:focus {
        background: $primary;
    }

    ResultItem .result-header {
        width: 100%;
    }

    ResultItem .result-path {
        color: $primary;
        text-style: bold;
    }

    ResultItem .result-score {
        color: $success;
    }

    ResultItem .result-text {
        width: 100%;
        color: $text-muted;
        padding-top: 1;
    }
    """

    can_focus = True

    def __init__(self, result: SearchResult, index: int, **kwargs) -> None:
        super().__init__(**kwargs)
        self.result = result
        self.index = index

    def compose(self) -> ComposeResult:
        text = self.result.text
        if len(text) > 150:
            text = text[:150] + "..."

        with Vertical():
            yield Label(
                f"[{self.index}] {self.result.file_path} "
                f"(chunk {self.result.chunk_index}) — "
                f"[green]{self.result.score:.2%}[/green]",
                classes="result-header",
            )
            yield Label(text, classes="result-text")

    def on_click(self) -> None:
        """Handle click on result."""
        self.post_message(RecallSearch.ResultSelected(self.result))

    def on_key(self, event) -> None:
        """Handle key press."""
        if event.key == "enter":
            self.post_message(RecallSearch.ResultSelected(self.result))
