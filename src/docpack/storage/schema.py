"""Schema definition and exceptions for docpack storage."""

from __future__ import annotations


# -----------------------------------------------------------------------------
# Exceptions
# -----------------------------------------------------------------------------


class StorageError(Exception):
    """Base exception for storage operations."""

    pass


class IntegrityError(StorageError):
    """Raised when a database constraint is violated."""

    pass


class NotFoundError(StorageError):
    """Raised when a requested record doesn't exist."""

    pass


# -----------------------------------------------------------------------------
# Schema
# -----------------------------------------------------------------------------

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT UNIQUE NOT NULL,
    extension TEXT,
    size_bytes INTEGER NOT NULL,
    is_binary INTEGER NOT NULL DEFAULT 0,
    content TEXT,
    sha256_hash TEXT
);

CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER NOT NULL,
    chunk_index INTEGER NOT NULL,
    text TEXT NOT NULL,
    token_count INTEGER,
    start_char INTEGER,
    end_char INTEGER,
    FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE,
    UNIQUE(file_id, chunk_index)
);

CREATE TABLE IF NOT EXISTS vectors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chunk_id INTEGER NOT NULL,
    dims INTEGER NOT NULL,
    vector BLOB NOT NULL,
    FOREIGN KEY (chunk_id) REFERENCES chunks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS metadata (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE INDEX IF NOT EXISTS idx_chunks_file_id ON chunks(file_id);
CREATE INDEX IF NOT EXISTS idx_vectors_chunk_id ON vectors(chunk_id);
CREATE INDEX IF NOT EXISTS idx_files_path ON files(path);
"""
