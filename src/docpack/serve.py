"""
MCP Server for docpack.

Exposes a frozen docpack to AI agents via the Model Context Protocol.

Tools:
    ls      - List all files in the docpack
    read    - Read file contents by path
    recall  - Semantic search against embedded chunks
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from docpack.recall import recall as do_recall
from docpack.storage import get_all_files, get_file_by_path, init_db


def create_server(docpack_path: str) -> Server:
    """
    Create an MCP server for a docpack.

    Args:
        docpack_path: Path to the .docpack file

    Returns:
        Configured MCP Server instance
    """
    path = Path(docpack_path)
    if not path.exists():
        raise FileNotFoundError(f"Docpack not found: {docpack_path}")

    server = Server("docpack")

    # Keep connection open for the server lifetime
    conn: sqlite3.Connection | None = None

    def get_conn() -> sqlite3.Connection:
        nonlocal conn
        if conn is None:
            conn = init_db(str(path))
        return conn

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="ls",
                description="List all files in the docpack with their paths and sizes",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            ),
            Tool(
                name="read",
                description="Read the contents of a file by its path",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "File path within the docpack",
                        },
                    },
                    "required": ["path"],
                },
            ),
            Tool(
                name="recall",
                description="Semantic search for relevant code chunks using natural language",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Natural language search query",
                        },
                        "k": {
                            "type": "integer",
                            "description": "Number of results to return (default: 5)",
                            "default": 5,
                        },
                    },
                    "required": ["query"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        db = get_conn()

        if name == "ls":
            files = get_all_files(db)
            if not files:
                return [TextContent(type="text", text="No files in docpack")]

            lines = []
            for f in files:
                status = "[bin]" if f["is_binary"] else "[txt]"
                lines.append(f"{status} {f['path']} ({f['size_bytes']} bytes)")

            return [TextContent(type="text", text="\n".join(lines))]

        elif name == "read":
            file_path = arguments.get("path", "")
            if not file_path:
                return [TextContent(type="text", text="Error: path is required")]

            file_record = get_file_by_path(db, file_path)
            if not file_record:
                return [TextContent(type="text", text=f"Error: File not found: {file_path}")]

            if file_record["is_binary"]:
                return [TextContent(type="text", text=f"Error: Cannot read binary file: {file_path}")]

            content = file_record.get("content", "")
            return [TextContent(type="text", text=content or "(empty file)")]

        elif name == "recall":
            query = arguments.get("query", "")
            if not query:
                return [TextContent(type="text", text="Error: query is required")]

            k = arguments.get("k", 5)
            results = do_recall(db, query, k=k)

            if not results:
                return [TextContent(type="text", text="No results found")]

            lines = []
            for i, r in enumerate(results, 1):
                lines.append(f"[{i}] {r.file_path} (chunk {r.chunk_index}) — score: {r.score:.4f}")
                lines.append("-" * 60)
                lines.append(r.text)
                lines.append("")

            return [TextContent(type="text", text="\n".join(lines))]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    return server


async def run_server(docpack_path: str) -> None:
    """
    Run the MCP server over stdio.

    Args:
        docpack_path: Path to the .docpack file
    """
    server = create_server(docpack_path)

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )
