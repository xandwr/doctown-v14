"""
Freeze command implementation.

Ingests files from various sources and stores them in a .docpack file.
This is the first stage of the pipeline - raw file ingestion without
chunking or embedding.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

from docpack.storage import init_db, insert_file, set_metadata

from .sources import DirectorySource, URLSource, ZipSource
from .vfs import VirtualFS

if TYPE_CHECKING:
    import sqlite3


# -----------------------------------------------------------------------------
# Source detection
# -----------------------------------------------------------------------------


def detect_source(target: str) -> VirtualFS:
    """
    Detect and create appropriate source for target.

    Handles:
    - Local directories
    - Local zip files
    - URLs (http://, https://)

    Args:
        target: Path or URL to ingest

    Returns:
        Appropriate VirtualFS implementation

    Raises:
        ValueError: If target type cannot be determined
        FileNotFoundError: If local path doesn't exist
    """
    # URL
    if target.startswith(("http://", "https://")):
        return URLSource(target)

    # Local path
    path = Path(target)

    if not path.exists():
        raise FileNotFoundError(f"Path not found: {target}")

    if path.is_dir():
        return DirectorySource(path)

    if path.is_file():
        # Check if zip
        if path.suffix.lower() == ".zip":
            return ZipSource(path)

        # Try to detect zip by magic bytes
        try:
            with open(path, "rb") as f:
                if f.read(2) == b"PK":
                    return ZipSource(path)
        except OSError:
            pass

        raise ValueError(f"Unsupported file type: {target}")

    raise ValueError(f"Cannot determine source type: {target}")


# -----------------------------------------------------------------------------
# Freeze
# -----------------------------------------------------------------------------


def freeze(
    target: str,
    output: str | None = None,
    *,
    use_temp: bool = False,
    verbose: bool = False,
) -> Path:
    """
    Freeze a target into a .docpack file.

    Ingests all files from the target source (directory, zip, URL)
    and stores them in a SQLite database. This is raw ingestion -
    no chunking or embedding is performed.

    Args:
        target: Path or URL to ingest
        output: Output .docpack path (default: derived from target)
        use_temp: If True, create in system temp dir (auto-cleanup)
        verbose: Print progress information

    Returns:
        Path to created .docpack file

    Example:
        # Freeze a directory
        path = freeze("./my-project", "project.docpack")

        # Freeze to temp (for one-shot operations)
        path = freeze("./my-project", use_temp=True)

        # Freeze a URL
        path = freeze("https://github.com/user/repo/archive/main.zip")
    """
    # Determine output path
    if output:
        output_path = Path(output)
    elif use_temp:
        # Create in temp directory
        fd, temp_path = tempfile.mkstemp(suffix=".docpack")
        import os

        os.close(fd)
        output_path = Path(temp_path)
    else:
        # Derive from target name
        if target.startswith(("http://", "https://")):
            from urllib.parse import urlparse

            parsed = urlparse(target)
            name = parsed.path.rsplit("/", 1)[-1] or "download"
            name = name.rsplit(".", 1)[0]  # Remove extension
        else:
            name = Path(target).stem

        output_path = Path(f"{name}.docpack")

    # Initialize database
    conn = init_db(str(output_path))

    try:
        # Get source and ingest
        source = detect_source(target)

        with source:
            file_count = 0
            total_bytes = 0

            for vfile in source.walk():
                # Read content
                content_bytes = vfile.read_bytes()
                is_binary = vfile.is_binary()

                # Decode text content
                text_content: str | None = None
                if not is_binary:
                    text_content = content_bytes.decode("utf-8", errors="replace")

                # Insert into database
                insert_file(
                    conn,
                    path=vfile.path,
                    size_bytes=vfile.size,
                    sha256_hash=vfile.sha256(),
                    content=text_content,
                    is_binary=is_binary,
                    extension=vfile.extension,
                )

                file_count += 1
                total_bytes += vfile.size

                if verbose:
                    status = "binary" if is_binary else "text"
                    print(f"  [{status}] {vfile.path} ({vfile.size} bytes)")

            # Store metadata
            set_metadata(conn, "source", target)
            set_metadata(conn, "file_count", str(file_count))
            set_metadata(conn, "total_bytes", str(total_bytes))
            set_metadata(conn, "stage", "frozen")  # No chunks/embeddings yet

            if verbose:
                print(f"\nFroze {file_count} files ({total_bytes:,} bytes)")
                print(f"Output: {output_path}")

    finally:
        conn.close()

    return output_path


def freeze_to_connection(
    target: str,
    conn: "sqlite3.Connection",
    *,
    verbose: bool = False,
) -> int:
    """
    Freeze a target into an existing database connection.

    Useful for programmatic use where you want control over the connection.

    Args:
        target: Path or URL to ingest
        conn: Open database connection
        verbose: Print progress information

    Returns:
        Number of files ingested
    """
    source = detect_source(target)

    with source:
        file_count = 0
        total_bytes = 0

        for vfile in source.walk():
            content_bytes = vfile.read_bytes()
            is_binary = vfile.is_binary()

            text_content: str | None = None
            if not is_binary:
                text_content = content_bytes.decode("utf-8", errors="replace")

            insert_file(
                conn,
                path=vfile.path,
                size_bytes=vfile.size,
                sha256_hash=vfile.sha256(),
                content=text_content,
                is_binary=is_binary,
                extension=vfile.extension,
            )

            file_count += 1
            total_bytes += vfile.size

            if verbose:
                status = "binary" if is_binary else "text"
                print(f"  [{status}] {vfile.path} ({vfile.size} bytes)")

        set_metadata(conn, "source", target)
        set_metadata(conn, "file_count", str(file_count))
        set_metadata(conn, "total_bytes", str(total_bytes))
        set_metadata(conn, "stage", "frozen")

    return file_count
