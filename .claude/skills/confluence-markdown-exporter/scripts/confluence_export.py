#!/usr/bin/env python3
"""
Confluence Markdown Exporter wrapper for Claude skills.
Wraps Spenhouet/confluence-markdown-exporter for page/space export to markdown.
"""

import subprocess
import sys
import argparse
import os
from pathlib import Path

DEFAULT_OUTPUT = "/output/"


def run_exporter(args: list[str]) -> int:
    """Run confluence-markdown-exporter command."""
    cmd = ["confluence-markdown-exporter"] + args

    result = subprocess.run(cmd)
    return result.returncode


def export_page(page_id_or_url: str, output_path: str) -> int:
    """Export a single page to markdown."""
    return run_exporter(["pages", page_id_or_url, output_path])


def export_tree(page_id_or_url: str, output_path: str) -> int:
    """Export a page and all its descendants to markdown."""
    return run_exporter(["pages-with-descendants", page_id_or_url, output_path])


def export_space(space_key: str, output_path: str) -> int:
    """Export an entire space to markdown."""
    return run_exporter(["spaces", space_key, output_path])


def run_config() -> int:
    """Run interactive configuration."""
    return run_exporter(["config"])


def ensure_output_dir(path: str) -> str:
    """Ensure output directory exists and return absolute path."""
    abs_path = os.path.abspath(path)
    Path(abs_path).mkdir(parents=True, exist_ok=True)
    return abs_path


def main():
    parser = argparse.ArgumentParser(
        description="Export Confluence pages to markdown"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Page export
    page_parser = subparsers.add_parser("page", help="Export single page")
    page_parser.add_argument("page_id", help="Page ID or URL")
    page_parser.add_argument(
        "output", nargs="?", default=DEFAULT_OUTPUT, help="Output directory"
    )

    # Tree export
    tree_parser = subparsers.add_parser(
        "tree", help="Export page with all descendants"
    )
    tree_parser.add_argument("page_id", help="Page ID or URL")
    tree_parser.add_argument(
        "output", nargs="?", default=DEFAULT_OUTPUT, help="Output directory"
    )

    # Space export
    space_parser = subparsers.add_parser("space", help="Export entire space")
    space_parser.add_argument("space_key", help="Space key")
    space_parser.add_argument(
        "output", nargs="?", default=DEFAULT_OUTPUT, help="Output directory"
    )

    # Config
    subparsers.add_parser("config", help="Configure authentication")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "config":
        sys.exit(run_config())

    # Ensure output directory exists for export commands
    output_path = ensure_output_dir(args.output)

    if args.command == "page":
        sys.exit(export_page(args.page_id, output_path))
    elif args.command == "tree":
        sys.exit(export_tree(args.page_id, output_path))
    elif args.command == "space":
        sys.exit(export_space(args.space_key, output_path))


if __name__ == "__main__":
    main()
