## Quickstart:

The project deps are managed with `uv` which is fucking awesome.

`uv run docpack [abc]`

---

1. **Storage Layer** (SQLite schema + wrapper) — the foundation (🮱 DONE)

    You build:
    - storage.py
    - tables: files, chunks, vectors, metadata
    - minimal helper functions:
        - init_db(path)
        - insert_file(...)
        - insert_chunk(...)
        - insert_vector(...)
        - get_chunks()

    Make it solid now, then everything else becomes a pipe.

---

2. **Ingest** (filesystem walker + zip extractor) — the raw material

    Once storage exists, you implement:
    - ingest.py
    - walk_dir(path)
    - handle_zip(path)
    - detect text vs binary
    - read file contents
    - store rows into files

    Your first milestone:

    `docpack freeze ./folder`

    …creates a .docpack with only the files table filled.
    No chunking. No embeddings.
    Just raw ingestion.

---

3. **Chunking** (paragraph splitter) — structure and granularity

    Now you can read the file contents from the DB and produce chunks.
    - chunk.py
    - split_into_chunks(text)
    - add chunk_index, start/end_char
    - write to chunks

    At this point you can run:

    `docpack info file.docpack`

    …and see file count and chunk count.

---

4. **Embedding Engine** — meaning gets attached

    Now that you have chunks, you can embed them.
    - embed.py
    - lazy-load MiniLM model
    - batch inference
    - store 384-dim vectors into vectors

    This unlocks:
    docpack recall "search text"
    (but recall isn’t implemented yet — vector search is next)

---

5. **Vector Search** — semantic recall

    This is where the system becomes “alive.”
    - recall.py
    - cosine similarity
    - k-nearest neighbors
    - pull chunk text + file path + metadata

    Boom. The semantic engine works:

    `docpack recall docpack.docpack "jwt token"`

    Now the CLI is officially a tool, not a pipeline.

---

6. **Metadata + Model Tracking** — polish pass

    Add:
    - model name
    - created_at
    - version
    - file size
    - counts
    - config flags

    This powers:

    `docpack info docpack.docpack`

---

7. **CLI commands** — the interface for humans

    Now wire the pieces:
    - freeze → ingest → chunk → embed → store
    - recall → vector search
    - info → metadata
    - run → freeze + serve
    - serve → MCP server
    - deck → TUI / web UI wrapper

    Building the pipeline first makes CLI trivial.

---

8. **MCP Server** — the interface for AI agents

    After recall is stable, implement:
    - serve
    - tools:
        - ls()
        - read()
        - recall()

    This completes the Freeze → Query lifecycle.

---

9. **Flight Deck** (Textual TUI + web) — the interface for humans

    By doing it last, I avoid rewriting UI because the backend changed shape.
    Textual becomes a consumer of the core — not fused with it.

---