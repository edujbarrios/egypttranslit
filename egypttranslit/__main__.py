"""Command-line interface for egypttranslit."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable, Sequence

from . import __version__, normalize_unicode, parse, parse_mdc

_CONVERTERS: dict[str, Callable[[str], str]] = {
    "auto": parse,
    "mdc": parse_mdc,
    "unicode": normalize_unicode,
}


def _configure_utf8_stdio() -> None:
    """Use deterministic UTF-8 for redirected and interactive standard streams."""
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="strict")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="egypttranslit",
        description="Convert Egyptological transliteration to canonical Unicode.",
    )
    parser.add_argument(
        "text",
        nargs="*",
        help="text to convert; when omitted, read exactly from standard input",
    )
    parser.add_argument(
        "-m",
        "--mode",
        choices=tuple(_CONVERTERS),
        default="auto",
        help="conversion mode (default: auto)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command-line interface and return a process exit code."""
    _configure_utf8_stdio()
    args = _build_parser().parse_args(argv)
    source = " ".join(args.text) if args.text else sys.stdin.read()
    sys.stdout.write(_CONVERTERS[args.mode](source))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
