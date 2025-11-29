"""
FileTree widget - displays docpack files in a tree structure.

Shows the file hierarchy with icons and allows selection.
"""

from pathlib import PurePosixPath
from typing import Any

from textual.app import ComposeResult
from textual.message import Message
from textual.widgets import Tree
from textual.widgets.tree import TreeNode


class FileTree(Tree):
    """A tree view of files in a docpack."""

    class FileSelected(Message):
        """Fired when a file is selected."""

        def __init__(self, path: str, file_id: int) -> None:
            super().__init__()
            self.path = path
            self.file_id = file_id

    DEFAULT_CSS = """
    FileTree {
        width: 100%;
        height: 100%;
        background: $surface;
        scrollbar-size: 1 1;
    }

    FileTree > .tree--label {
        padding: 0 1;
    }

    FileTree > .tree--cursor {
        background: $primary;
        color: $text;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__("📦 Files", **kwargs)
        self.show_root = True
        self._files: list[dict[str, Any]] = []
        self._path_to_node: dict[str, TreeNode] = {}

    def on_mount(self) -> None:
        """Expand root when mounted."""
        self.root.expand()

    def load_files(self, files: list[dict[str, Any]]) -> None:
        """Load files from docpack storage into the tree."""
        self._files = files
        self.clear()  # Note: clear() creates a new root node
        self._path_to_node.clear()

        # Build tree structure - must access self.root AFTER clear()
        # because clear() replaces the root node
        self.root.expand()

        # Sort files by path for consistent ordering
        sorted_files = sorted(files, key=lambda f: f["path"])

        for file_info in sorted_files:
            path = file_info["path"]
            parts = PurePosixPath(path).parts
            current_node = self.root

            # Create/traverse directory nodes
            for i, part in enumerate(parts[:-1]):
                dir_path = "/".join(parts[: i + 1])
                if dir_path not in self._path_to_node:
                    # Create directory node
                    node = current_node.add(f"📁 {part}", data={"type": "dir", "path": dir_path})
                    self._path_to_node[dir_path] = node
                    node.expand()
                current_node = self._path_to_node[dir_path]

            # Add file node
            filename = parts[-1]
            icon = self._get_file_icon(filename, file_info.get("is_binary", False))
            file_node = current_node.add(
                f"{icon} {filename}",
                data={
                    "type": "file",
                    "path": path,
                    "file_id": file_info["id"],
                    "is_binary": file_info.get("is_binary", False),
                },
            )
            self._path_to_node[path] = file_node

        # Force a refresh to ensure the tree is rendered
        self.refresh()

    def _get_file_icon(self, filename: str, is_binary: bool) -> str:
        """Get an appropriate icon for the file type."""
        if is_binary:
            return "📄"

        ext = PurePosixPath(filename).suffix.lower()
        icons = {
            ".py": "🐍",
            ".js": "📜",
            ".ts": "📘",
            ".tsx": "⚛️",
            ".jsx": "⚛️",
            ".json": "📋",
            ".yaml": "📋",
            ".yml": "📋",
            ".toml": "📋",
            ".md": "📝",
            ".txt": "📝",
            ".html": "🌐",
            ".css": "🎨",
            ".sql": "🗄️",
            ".sh": "⚙️",
            ".bash": "⚙️",
            ".zsh": "⚙️",
            ".rs": "🦀",
            ".go": "🐹",
            ".java": "☕",
            ".c": "⚡",
            ".cpp": "⚡",
            ".h": "⚡",
            ".rb": "💎",
            ".pdf": "📕",
            ".png": "🖼️",
            ".jpg": "🖼️",
            ".jpeg": "🖼️",
            ".gif": "🖼️",
            ".svg": "🖼️",
        }
        return icons.get(ext, "📄")

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Handle node selection."""
        node = event.node
        data = node.data

        if data and data.get("type") == "file":
            self.post_message(
                self.FileSelected(
                    path=data["path"],
                    file_id=data["file_id"],
                )
            )

    def select_path(self, path: str) -> None:
        """Programmatically select a file by path."""
        if path in self._path_to_node:
            node = self._path_to_node[path]
            self.select_node(node)
            # Expand parent directories
            parent = node.parent
            while parent:
                parent.expand()
                parent = parent.parent
