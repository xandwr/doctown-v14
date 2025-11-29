"""
ViewerScreen - the main docpack exploration interface.

Combines FileTree, FileViewer, RecallSearch, and InfoPanel into a
cohesive exploration experience.
"""

import sqlite3
from pathlib import Path

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import ContentSwitcher, Footer, Label, TabbedContent, TabPane

from flight_deck.widgets import (
    FileTree,
    FileViewer,
    InfoPanel,
    NavBar,
    RecallSearch,
    SearchResult,
)


class ViewerScreen(Screen):
    """Main docpack viewer/explorer screen."""

    BINDINGS = [
        Binding("ctrl+o", "open_new", "Open"),
        Binding("ctrl+f", "focus_search", "Search"),
        Binding("ctrl+t", "toggle_sidebar", "Toggle Sidebar"),
        Binding("escape", "go_home", "Home"),
        Binding("f1", "show_info", "Info"),
        Binding("f2", "show_files", "Files"),
        Binding("f3", "show_search", "Search"),
    ]

    DEFAULT_CSS = """
    ViewerScreen {
        layout: vertical;
    }

    ViewerScreen > Vertical {
        width: 100%;
        height: 1fr;
    }

    ViewerScreen .docpack-header {
        width: 100%;
        height: 1;
        background: $primary-darken-1;
        padding: 0 2;
        text-style: bold;
    }

    ViewerScreen .main-container {
        width: 100%;
        height: 1fr;
    }

    ViewerScreen .sidebar {
        width: 35;
        height: 100%;
        border-right: solid $primary-darken-2;
    }

    ViewerScreen .sidebar-hidden {
        display: none;
    }

    ViewerScreen .content-area {
        width: 1fr;
        height: 100%;
    }

    ViewerScreen TabbedContent {
        height: 100%;
    }

    ViewerScreen TabPane {
        padding: 0;
        height: 100%;
    }

    ViewerScreen FileTree {
        height: 100%;
    }

    ViewerScreen RecallSearch {
        height: 100%;
    }

    ViewerScreen InfoPanel {
        height: 100%;
    }

    ViewerScreen .status-bar {
        width: 100%;
        height: 1;
        background: $primary-darken-1;
        padding: 0 1;
        color: $text-muted;
    }
    """

    def __init__(self, docpack_path: Path, **kwargs) -> None:
        super().__init__(**kwargs)
        self.docpack_path = docpack_path
        self._conn: sqlite3.Connection | None = None
        self._sidebar_visible = True

    def compose(self) -> ComposeResult:
        yield NavBar(active="explore")

        with Vertical():
            # Docpack name header
            yield Label(
                f"📦 {self.docpack_path.name}",
                classes="docpack-header",
            )

            with Horizontal(classes="main-container"):
                # Sidebar with tabs
                with Vertical(classes="sidebar", id="sidebar"):
                    with TabbedContent(id="sidebar-tabs"):
                        with TabPane("Files", id="files-tab"):
                            yield FileTree(id="file-tree")
                        with TabPane("Search", id="search-tab"):
                            yield RecallSearch(id="recall-search")
                        with TabPane("Info", id="info-tab"):
                            yield InfoPanel(id="info-panel")

                # Main content area
                with Vertical(classes="content-area"):
                    yield FileViewer(id="file-viewer")

            # Status bar
            yield Label(
                f"📦 {self.docpack_path} | Ctrl+O: Open | Ctrl+F: Search | Ctrl+T: Toggle sidebar",
                classes="status-bar",
            )

    def on_mount(self) -> None:
        """Load the docpack when the screen mounts."""
        self._load_docpack()

    def _load_docpack(self) -> None:
        """Load the docpack and populate widgets."""
        from docpack.storage import get_all_files, get_all_metadata, get_stats, init_db

        try:
            self._conn = init_db(str(self.docpack_path))

            # Load files into tree
            files = get_all_files(self._conn)
            file_tree = self.query_one("#file-tree", FileTree)
            file_tree.load_files(files)

            # Set connection for recall search
            recall_search = self.query_one("#recall-search", RecallSearch)
            recall_search.set_connection(self._conn)

            # Load info panel
            stats = get_stats(self._conn)
            metadata = get_all_metadata(self._conn)
            info_panel = self.query_one("#info-panel", InfoPanel)
            info_panel.load_info(stats, metadata)

            self.notify(f"Loaded: {self.docpack_path.name}")

        except Exception as e:
            self.notify(f"Error loading docpack: {e}", severity="error")

    @on(FileTree.FileSelected)
    def on_file_selected(self, event: FileTree.FileSelected) -> None:
        """Handle file selection from tree."""
        if not self._conn:
            return

        from docpack.storage import get_file_by_path

        file_record = get_file_by_path(self._conn, event.path)
        if file_record:
            viewer = self.query_one("#file-viewer", FileViewer)
            viewer.show_file(
                path=event.path,
                content=file_record.get("content"),
                is_binary=file_record.get("is_binary", False),
            )

    @on(RecallSearch.ResultSelected)
    def on_search_result_selected(self, event: RecallSearch.ResultSelected) -> None:
        """Handle search result selection - show file and scroll to chunk."""
        if not self._conn:
            return

        from docpack.storage import get_file_by_path

        result = event.result
        file_record = get_file_by_path(self._conn, result.file_path)

        if file_record:
            viewer = self.query_one("#file-viewer", FileViewer)
            viewer.show_file(
                path=result.file_path,
                content=file_record.get("content"),
                is_binary=file_record.get("is_binary", False),
            )

            # Also select in tree
            file_tree = self.query_one("#file-tree", FileTree)
            file_tree.select_path(result.file_path)

    def action_open_new(self) -> None:
        """Open a new docpack."""
        self.app.push_screen("path_input")

    def action_focus_search(self) -> None:
        """Focus the search input."""
        # Switch to search tab
        tabs = self.query_one("#sidebar-tabs", TabbedContent)
        tabs.active = "search-tab"

        # Focus the input
        search = self.query_one("#recall-search", RecallSearch)
        search_input = search.query_one("#search-input")
        search_input.focus()

    def action_toggle_sidebar(self) -> None:
        """Toggle sidebar visibility."""
        sidebar = self.query_one("#sidebar", Vertical)
        self._sidebar_visible = not self._sidebar_visible

        if self._sidebar_visible:
            sidebar.remove_class("sidebar-hidden")
        else:
            sidebar.add_class("sidebar-hidden")

    def action_go_home(self) -> None:
        """Return to home screen."""
        if self._conn:
            self._conn.close()
            self._conn = None
        self.app.pop_screen()

    def action_show_info(self) -> None:
        """Switch to info tab."""
        tabs = self.query_one("#sidebar-tabs", TabbedContent)
        tabs.active = "info-tab"

    def action_show_files(self) -> None:
        """Switch to files tab."""
        tabs = self.query_one("#sidebar-tabs", TabbedContent)
        tabs.active = "files-tab"

    def action_show_search(self) -> None:
        """Switch to search tab."""
        tabs = self.query_one("#sidebar-tabs", TabbedContent)
        tabs.active = "search-tab"

    def on_unmount(self) -> None:
        """Clean up when screen is removed."""
        if self._conn:
            self._conn.close()
            self._conn = None
