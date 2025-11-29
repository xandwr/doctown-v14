# .docpack spec FINAL FORM (hopefully)

The pitch:
> A .docpack is a self-contained, immutable SQLite knowledge capsule containing raw files, semantic chunks, vector embeddings, and all metadata needed for deterministic offline search.

## Design

1. Filesystem Layer

All raw input material preserved exactly as it existed.
`files` table:
- path
- extension
- size_bytes
- is_binary
- (text) content or (binary) NULL + metadata
- SHA256 hash (optional, recommended)

This is the ground truth.
It’s the “archive” part of the freezer.

2. Chunk Layer

The human-readable slices that embeddings operate on.
`chunks` table:
- id
- file_path
- chunk_index
- text
- start_char
- end_char

These represent the semantic atoms of the universe.

3. Embedding Layer

Machine-understandable meaning for every chunk.
`vectors` table:
- chunk_id
- vector (BLOB of 384 floats, or compressed bytes)

This is the “meaning map,” pinned in offline space.

4. Semantic Index

The data structure that makes recall fast and deterministic.
This can be stored as:
a normalized vectors table + SQLite index
OR a side-table for centroid caches / L2-normalized copies
OR nothing extra (MiniLM search is cheap)

The point:
Everything needed for recall lives inside the docpack.

5. Metadata

The manifest for reproducibility and provenance.
`metadata` table (key/value):
- version ("1.0.0")
- created_at
- embedding_model ("all-MiniLM-L6-v2")
- text_split_strategy ("paragraph")
- total_files
- total_chunks
- total_embeddings
- tool_version ("docpack v14")
- freeze_source_path
etc.

This makes the docpack a scientific artifact, not just a blob.

6. Optional: Attachments or Sidecar Data

You may eventually add:
- OCR text for PDFs
- cluster labels from reranker
- index of top-K neighbors per chunk
- source commit hash (if freezing git repos)

But these are optional enhancements, not part of the core.

## Conceptual view
A .docpack is a frozen universe with four layers:

- Raw reality (the files)
- Readable slices (chunks)
- Semantic meaning (embeddings)
- Queryable index (recall)

It is:
- offline
- deterministic
- portable
- inspectable
- immutable after creation
- safe for agents to explore

And you can mount it from:
- CLI
- Flight Deck
- MCP agents
- custom scripts
- cloud runners

Without internet.
Without hallucinations.
Without any external database.

