# Doctown v14

## Scripts
- [`run_fd_local.sh`](run_fd_local.sh): Starts the flight deck in the terminal directly.
- [`run_fd_web.sh`](run_fd_web.sh): Serves the flight deck to local port 8000 to be used as a website.

---

**The Universal Semantic Container**

*Ingest Chaos. Freeze State. Query Everything.*

---

## What is a `.docpack`?

A `.docpack` is a standard SQLite database—a single, portable file that works anywhere.

It contains:

- **The Filesystem**: Raw data preserved exactly as it was (text, code, logs)
- **The Vector Map**: Mathematical index linking concepts together (e.g., "flour" → "baking", `auth_token` → `login.rs`)

No internet connection. No vector database server. Just the file.

## Philosophy

Traditional AI systems try to "read" and "summarize" your data during import. This is slow, expensive, and prone to hallucinations.

DocPack takes a different approach:

| Phase | What Happens |
|-------|--------------|
| **Ingest (Freezing)** | Map the territory. Don't write the travel guide. Fast, deterministic, offline. |
| **Query (Thawing)** | Understanding happens only when you ask. An AI Agent enters the frozen snapshot and explores data exactly as it exists. |

---

## Installation

**Prerequisites:** Python 3.12+

```bash
# Using uv (recommended)
uv sync

# Or pip
pip install -e .
```

## Quick Start

```bash
# Freeze a folder or zip into a queryable docpack
docpack freeze ./my-project -o project.docpack

# Start MCP server for AI agents
docpack serve project.docpack

# One-shot: freeze + serve (uses temp file)
docpack run ./my-project

# Interactive TUI for testing
docpack deck

# Inspect a docpack
docpack info project.docpack
```

---

### Processing Pipeline

1. **Ingest** — Walk directories or extract zips, detect binary vs text
2. **Chunk** — Split text on paragraph boundaries, merge small fragments
3. **Embed** — Generate 384-dim vectors via `all-MiniLM-L6-v2` - fast, runs locally and on-device
4. **Store** — Write to SQLite with indexed tables

### MCP Server Tools

When serving a docpack, AI agents get three tools:

| Tool | Description |
|------|-------------|
| `ls(path)` | List directory contents with file sizes |
| `read(path)` | Read file content (text) or metadata (binary) |
| `recall(query, limit)` | Semantic search via embedding similarity |

### Database Schema

```sql
files (path, content, size_bytes, extension, is_binary)
chunks (id, file_path, chunk_index, text, start_char, end_char)
vectors (chunk_id, embedding)
metadata (key, value)
```

---

## Examples

### Exploring a codebase:

```bash
# Freeze a project
$ docpack freeze ~/projects/my-api -o api.docpack

Freezing ~/projects/my-api...
  ├── 847 files discovered
  ├── 312 text files processed
  ├── 2,847 chunks created
  └── Done in 1.8s

Saved to api.docpack (4.2 MB)
```

```bash
# Start the flight deck
$ docpack deck api.docpack
```

```txt
╭─────────────────────────────────────────────────────────────╮
│  DOCPACK FLIGHT DECK                        api.docpack     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  > where do we handle JWT validation?                       │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  Found 3 relevant locations:                                │
│                                                             │
│  1. src/middleware/auth.py (lines 34-67)                    │
│     validate_token() checks signature and expiry            │
│                                                             │
│  2. src/utils/jwt.py (lines 12-29)                          │
│     decode_jwt() handles parsing and verification           │
│                                                             │
│  3. tests/test_auth.py (lines 89-124)                       │
│     Test cases for expired and malformed tokens             │
│                                                             │
│  ───────────────────────────────────────────────────────    │
│  [Enter] follow-up  [Tab] browse files  [Esc] clear         │
╰─────────────────────────────────────────────────────────────╯

╭─────────────────────────────────────────────────────────────╮
│  > show me auth.py around line 34                           │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  src/middleware/auth.py                                     │
│  ──────────────────────                                     │
│  32   │                                                     │
│  33   │ def validate_token(token: str) -> Claims:           │
│  34 → │     """Validate JWT and return claims."""           │
│  35   │     try:                                            │
│  36   │         payload = decode_jwt(token)                 │
│  37   │         if payload["exp"] < time.time():            │
│  38   │             raise TokenExpiredError()               │
│  39   │         return Claims(**payload)                    │
│  40   │     except JWTError as e:                           │
│  41   │         raise InvalidTokenError(str(e))             │
│  42   │                                                     │
│                                                             │
╰─────────────────────────────────────────────────────────────╯
```

### Grandma's recipe collection:

```bash
# Freeze decades of recipes from a folder of scans, PDFs, and text files
$ docpack freeze ~/Recipes -o recipes.docpack

Freezing ~/Recipes...
  ├── 156 files discovered
  ├── 143 text files processed (including 47 PDFs)
  ├── 891 chunks created
  └── Done in 3.2s

Saved to recipes.docpack (2.1 MB)
```

```bash
# Open the flight deck
$ docpack deck recipes.docpack
```

```txt
╭─────────────────────────────────────────────────────────────╮
│  DOCPACK FLIGHT DECK                     recipes.docpack    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  > the cookie recipe from Margaret with walnuts             │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  Found it:                                                  │
│                                                             │
│  Margaret's Walnut Chocolate Chip Cookies                   │
│  from: church_potluck_recipes_1987.pdf (page 3)             │
│                                                             │
│  "This is the one everyone asks about! Make sure            │
│   the butter is room temperature." - M.                     │
│                                                             │
│  Ingredients: butter, brown sugar, flour, walnuts,          │
│  chocolate chips, vanilla, eggs, baking soda, salt          │
│                                                             │
│  [Enter] see full recipe  [Tab] browse files  [Esc] clear   │
╰─────────────────────────────────────────────────────────────╯

╭─────────────────────────────────────────────────────────────╮
│  > what can I make if I have chicken and lemon?             │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  5 recipes use both chicken and lemon:                      │
│                                                             │
│  1. Greek Lemon Chicken (mom_favorites.txt)                 │
│     Roasted with oregano and potatoes                       │
│                                                             │
│  2. Lemon Herb Grilled Chicken (summer_bbq.pdf)             │
│     Marinade requires 2 hours                               │
│                                                             │
│  3. Grandma Ruth's Chicken Soup (handwritten_cards.pdf)     │
│     "Add lemon at the end for brightness"                   │
│                                                             │
│  4. Chicken Piccata (italian_night.txt)                     │
│     Capers, butter, white wine                              │
│                                                             │
│  5. Chinese Lemon Chicken (takeout_copycats.pdf)            │
│     The crispy fried version                                │
│                                                             │
╰─────────────────────────────────────────────────────────────╯

╭─────────────────────────────────────────────────────────────╮
│  > which recipes are from Ruth?                             │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  12 recipes attributed to Ruth:                             │
│                                                             │
│  Soups         Chicken Soup, Beef Barley, Mushroom Bisque   │
│  Baking        Challah, Apple Cake, Mandelbrot              │
│  Holidays      Brisket, Potato Kugel, Charoset              │
│  Everyday      Meatloaf, Tuna Casserole, Stuffed Cabbage    │
│                                                             │
│  Source: mostly handwritten_cards.pdf (scanned index cards) │
│                                                             │
╰─────────────────────────────────────────────────────────────╯
```

### Drowning in project documents:

```bash
# Freeze everything from the Henderson account
$ docpack freeze ~/Work/Henderson_Project -o henderson.docpack

Freezing ~/Work/Henderson_Project...
  ├── 2,341 files discovered
  ├── 1,847 text files processed
  ├── 12,453 chunks created
  └── Done in 8.7s

Saved to henderson.docpack (31.4 MB)
```

```bash
# Open the flight deck
$ docpack deck henderson.docpack
```

```txt
╭─────────────────────────────────────────────────────────────╮
│  DOCPACK FLIGHT DECK                   henderson.docpack    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  > did we already send them the revised quote?              │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  Yes. Found 2 versions:                                     │
│                                                             │
│  1. Henderson_Quote_v2_FINAL.pdf (sent Oct 14)              │
│     Total: $47,200 — includes the extra signage             │
│                                                             │
│  2. Henderson_Quote_v1.pdf (Oct 3)                          │
│     Total: $41,800 — original scope                         │
│                                                             │
│  Related email: emails/oct_14_linda_RE_quote.eml            │
│  "Attached is the revised quote per our call Thursday"      │
│                                                             │
╰─────────────────────────────────────────────────────────────╯

╭─────────────────────────────────────────────────────────────╮
│  > what did we promise about the delivery timeline?         │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  3 documents mention delivery commitments:                  │
│                                                             │
│  1. contracts/Henderson_SOW_signed.pdf (page 4)             │
│     "Delivery within 6 weeks of signed approval"            │
│                                                             │
│  2. emails/oct_22_RE_timeline.eml                           │
│     "We're targeting Nov 29 but will confirm Monday"        │
│                                                             │
│  3. meeting_notes/kickoff_oct_16.docx                       │
│     "Client wants everything before Thanksgiving if         │
│      possible — hard deadline is Dec 5"                     │
│                                                             │
│  ⚠ Note: Nov 29 is 2 days before Thanksgiving               │
│                                                             │
╰─────────────────────────────────────────────────────────────╯

╭─────────────────────────────────────────────────────────────╮
│  > who's the contact for their facilities team?             │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  Mike Reeves — Facilities Manager                           │
│                                                             │
│  Phone: (555) 234-8821                                      │
│  Email: mreeves@hendersoninc.com                            │
│                                                             │
│  Source: contacts/henderson_team.xlsx                       │
│                                                             │
│  Also mentioned in:                                         │
│  · meeting_notes/site_visit_oct_9.docx                      │
│    "Mike will handle loading dock access"                   │
│  · emails/oct_11_RE_install.eml                             │
│    "Loop in Mike for anything on-site"                      │
│                                                             │
╰─────────────────────────────────────────────────────────────╯

╭─────────────────────────────────────────────────────────────╮
│  > what's still outstanding with this client?               │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  Based on emails and notes, unresolved items:               │
│                                                             │
│  1. Final sign-off on color samples                         │
│     (emails/oct_25_color_options.eml — no reply found)      │
│                                                             │
│  2. Insurance certificate request                           │
│     (emails/oct_19_RE_COI.eml — "send by Friday")           │
│     No matching outbound found in this folder               │
│                                                             │
│  3. Parking coordination for install crew                   │
│     (meeting_notes/kickoff_oct_16.docx — marked "TBD")      │
│                                                             │
╰─────────────────────────────────────────────────────────────╯
```

### Making sense of medical records:

```bash
# Freeze years of health documents before a specialist appointment
$ docpack freeze ~/Medical -o health.docpack

Freezing ~/Medical...
  ├── 89 files discovered
  ├── 76 text files processed (including 52 PDFs)
  ├── 634 chunks created
  └── Done in 2.1s

Saved to health.docpack (8.3 MB)
```

```bash
# Open the flight deck
$ docpack deck health.docpack
```

```txt
╭─────────────────────────────────────────────────────────────╮
│  DOCPACK FLIGHT DECK                      health.docpack    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  > when was my last tetanus shot?                           │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  August 12, 2019                                            │
│                                                             │
│  Source: immunization_record_2019.pdf                       │
│  Provider: Dr. Patel, Riverside Family Medicine             │
│  Note: Tdap (tetanus, diphtheria, pertussis)                │
│                                                             │
│  ⚠ Tetanus boosters typically recommended every 10 years    │
│                                                             │
╰─────────────────────────────────────────────────────────────╯

╭─────────────────────────────────────────────────────────────╮
│  > what medications have I been prescribed?                 │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  Found 7 prescriptions across your records:                 │
│                                                             │
│  Current                                                    │
│  · Lisinopril 10mg (blood pressure) — since March 2023      │
│  · Vitamin D 2000IU — since Jan 2022                        │
│                                                             │
│  Past                                                       │
│  · Amoxicillin 500mg — Feb 2024 (sinus infection)           │
│  · Prednisone 10mg — Oct 2023 (back inflammation)           │
│  · Cyclobenzaprine 5mg — Oct 2023 (muscle relaxant)         │
│  · Omeprazole 20mg — 2021-2022 (discontinued)               │
│  · Fluoxetine 20mg — 2018-2020 (discontinued)               │
│                                                             │
│  Sources: pharmacy_history.pdf, visit summaries (various)   │
│                                                             │
╰─────────────────────────────────────────────────────────────╯

╭─────────────────────────────────────────────────────────────╮
│  > summarize my back issues for the new doctor              │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  Timeline of lower back issues:                             │
│                                                             │
│  Oct 2023    Initial injury (visit_notes_oct_2023.pdf)      │
│              "Patient reports lifting injury at work"       │
│              Prescribed muscle relaxant + steroid pack      │
│                                                             │
│  Nov 2023    Follow-up, still symptomatic                   │
│              Referred to physical therapy                   │
│                                                             │
│  Dec 2023    MRI performed (mri_lumbar_dec2023.pdf)         │
│              "Mild disc bulge L4-L5, no herniation"         │
│                                                             │
│  Jan-Mar     PT notes show gradual improvement              │
│  2024        8 sessions completed                           │
│                                                             │
│  Jun 2024    "Occasional stiffness, manageable"             │
│              (annual_physical_2024.pdf)                     │
│                                                             │
│  Copy-friendly summary available: [Enter] to export         │
│                                                             │
╰─────────────────────────────────────────────────────────────╯

╭─────────────────────────────────────────────────────────────╮
│  > anything I should mention about family history?          │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  Family history noted in your records:                      │
│                                                             │
│  · Father: Type 2 diabetes, high blood pressure             │
│    (intake_form_2021.pdf)                                   │
│                                                             │
│  · Mother: Breast cancer (survivor), osteoporosis           │
│    (intake_form_2021.pdf, annual_physical_2024.pdf)         │
│                                                             │
│  · Maternal grandmother: Heart disease                      │
│    (intake_form_2021.pdf)                                   │
│                                                             │
│  Note: Your 2024 physical mentions "discussed increased     │
│  screening given family history" — no follow-up documented  │
│                                                             │
╰─────────────────────────────────────────────────────────────╯
```

## Tech Stack

| Layer | Technologies |
|-------|--------------|
| **Python** | sentence-transformers, mcp, numpy, textual |

## Design Principles

- **Protocol-based extensibility** — Swap chunkers, embedders, ingesters without inheritance
- **Deterministic processing** — No network calls during freeze, reproducible embeddings
- **One process = one docpack** — Prevents context pollution between document universes
- **Lazy loading** — Models loaded on first use, not at import