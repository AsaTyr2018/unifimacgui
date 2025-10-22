"""Entry points for launching the UniFi MAC viewer via GUI or CLI."""

from __future__ import annotations

import argparse
import logging
import platform
import sys
from typing import List

from .cli import run_cli
from .gui import run_gui

LOGGER = logging.getLogger(__name__)


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="UniFi MAC filter viewer (GUI + CLI)",
        add_help=False,
    )
    parser.add_argument("--cli", action="store_true", help="Force CLI mode (skip the GUI)")
    parser.add_argument("--debug", action="store_true", help="Enable verbose logging")
    parser.add_argument("-h", "--help", action="help", help="Show this help message and exit")
    return parser.parse_known_args(argv)


def run(argv: List[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    basic_config = {
        "level": logging.INFO,
        "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    }
    logging.basicConfig(**basic_config)

    args, remainder = parse_args(argv)
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.cli or remainder:
        LOGGER.debug("Starting CLI mode with args: %s", remainder)
        return run_cli(remainder)

    # Default: launch GUI. Windows users get GUI by default; Linux users can request CLI explicitly.
    if platform.system() == "Linux":
        LOGGER.info("No CLI arguments supplied; launch GUI manually with --cli if desired.")
    return run_gui()


if __name__ == "__main__":  # pragma: no cover - manual execution
    sys.exit(run())
