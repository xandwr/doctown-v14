"""
Docpack storage layer.

All SQL operations are encapsulated here. No other module should
contain SQL strings or direct database operations.

Usage:
    from docpack.storage import init_db, insert_file, insert_chunk, insert_vector

    conn = init_db("project.docpack")
    file_id = insert_file(conn, "src/main.py", 1234, "abc123...")
    chunk_id = insert_chunk(conn, file_id, 0, "def main():", 5)
    insert_vector(conn, chunk_id, 384, embedding)
"""

from .chunks import get_chunks, insert_chunk
from .connection import init_db
from .files import get_all_files, get_file, get_file_by_path, insert_file
from .metadata import get_all_metadata, get_metadata, get_stats, set_metadata
from .schema import IntegrityError, NotFoundError, StorageError
from .vectors import get_vectors, insert_vector

__all__ = [
    # Connection
    "init_db",
    # Files
    "insert_file",
    "get_file",
    "get_file_by_path",
    "get_all_files",
    # Chunks
    "insert_chunk",
    "get_chunks",
    # Vectors
    "insert_vector",
    "get_vectors",
    # Metadata
    "set_metadata",
    "get_metadata",
    "get_all_metadata",
    "get_stats",
    # Exceptions
    "StorageError",
    "IntegrityError",
    "NotFoundError",
]
