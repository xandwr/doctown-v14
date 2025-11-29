"""
Docpack CLI.

Commands:
    freeze     Turn folders/zips/URLs into a .docpack
    deck       Launch the Flight Deck (TUI / web cockpit)
    recall     Semantic search against a docpack
    serve      Expose docpack via MCP for AI agents
    info       Inspect metadata, stats, counts
    run        Freeze + serve a temp docpack (one-shot)

Examples:
    docpack freeze ./my-project -o project.docpack
    docpack freeze https://github.com/user/repo/archive/main.zip
    docpack info project.docpack
    docpack recall project.docpack "where is jwt validation?"
"""

from __future__ import annotations

import argparse
import sys


def cmd_freeze(args: argparse.Namespace) -> int:
    """Handle freeze command."""
    from docpack.ingest import freeze

    try:
        output_path = freeze(
            args.target,
            output=args.output,
            use_temp=args.temp,
            verbose=args.verbose,
            skip_chunking=args.no_chunk,
            skip_embedding=args.no_embed,
            embedding_model=args.model,
        )
        if not args.verbose:
            print(f"Created: {output_path}")
        return 0
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_info(args: argparse.Namespace) -> int:
    """Handle info command."""
    from pathlib import Path

    from docpack.storage import get_all_metadata, get_stats, init_db

    docpack_path = Path(args.docpack)
    if not docpack_path.exists():
        print(f"Error: File not found: {docpack_path}", file=sys.stderr)
        return 1

    conn = init_db(str(docpack_path))
    try:
        stats = get_stats(conn)
        metadata = get_all_metadata(conn)

        print(f"Docpack: {docpack_path}")
        print(f"Size: {docpack_path.stat().st_size:,} bytes")
        print()
        print("Stats:")
        print(f"  Files: {stats.get('total_files', 0)}")
        print(f"  Chunks: {stats.get('total_chunks', 0)}")
        print(f"  Vectors: {stats.get('total_vectors', 0)}")
        print(f"  Total size: {stats.get('total_size_bytes', 0):,} bytes")

        if metadata:
            print()
            print("Metadata:")
            for key, value in sorted(metadata.items()):
                print(f"  {key}: {value}")

        return 0
    finally:
        conn.close()


def cmd_not_implemented(name: str) -> int:
    """Placeholder for unimplemented commands."""
    print(f"Command '{name}' not yet implemented.", file=sys.stderr)
    return 1


def main() -> int:
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        prog="docpack",
        description="Freeze codebases for semantic search and AI consumption.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # freeze
    freeze_parser = subparsers.add_parser(
        "freeze",
        help="Turn folders/zips/URLs into a .docpack",
    )
    freeze_parser.add_argument(
        "target",
        help="Path or URL to ingest",
    )
    freeze_parser.add_argument(
        "-o",
        "--output",
        help="Output .docpack path",
    )
    freeze_parser.add_argument(
        "-t",
        "--temp",
        action="store_true",
        help="Create in temp directory (auto-cleanup)",
    )
    freeze_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print progress information",
    )
    freeze_parser.add_argument(
        "--no-chunk",
        action="store_true",
        help="Skip chunking (raw ingestion only)",
    )
    freeze_parser.add_argument(
        "--no-embed",
        action="store_true",
        help="Skip embedding (chunking only)",
    )
    freeze_parser.add_argument(
        "-m",
        "--model",
        default=None,
        help="Embedding model (default: google/embeddinggemma-300m)",
    )

    # info
    info_parser = subparsers.add_parser(
        "info",
        help="Inspect metadata, stats, counts",
    )
    info_parser.add_argument(
        "docpack",
        help="Path to .docpack file",
    )

    # Placeholders for future commands
    subparsers.add_parser("deck", help="Launch the Flight Deck (TUI)")
    subparsers.add_parser("recall", help="Semantic search against a docpack")
    subparsers.add_parser("serve", help="Expose docpack via MCP")
    subparsers.add_parser("run", help="Freeze + serve (one-shot)")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "freeze":
        return cmd_freeze(args)
    elif args.command == "info":
        return cmd_info(args)
    else:
        return cmd_not_implemented(args.command)


if __name__ == "__main__":
    sys.exit(main())