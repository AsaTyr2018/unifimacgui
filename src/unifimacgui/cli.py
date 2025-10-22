"""Command-line interface for UniFi MAC filter lookups."""

from __future__ import annotations

import argparse
import getpass
import logging
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

from .client import UniFiClient, label_mac_addresses

LOGGER = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fetch UniFi MAC filter lists (CLI mode).",
        add_help=False,
    )
    parser.add_argument("--url", help="Controller base URL, e.g. https://ip:8443")
    parser.add_argument("--user", help="UniFi username")
    parser.add_argument("--password", help="UniFi password (leave empty to prompt)")
    parser.add_argument("--site", help="Site name or description")
    parser.add_argument("--wlan", help="WLAN profile name")
    parser.add_argument(
        "--out",
        help="Optional output filename. If omitted, results are printed to stdout.",
    )
    parser.add_argument(
        "--format",
        choices=["txt", "csv", "xlsx"],
        default="txt",
        help="Export format when --out is supplied.",
    )
    parser.add_argument(
        "--verify-ssl",
        action="store_true",
        help="Enable SSL certificate verification (disabled by default for compatibility).",
    )
    parser.add_argument("--timeout", type=int, default=10, help="HTTP timeout in seconds (default: 10)")
    parser.add_argument("-h", "--help", action="help", help="Show this help message and exit")
    return parser


def ensure_cli_args(args: argparse.Namespace) -> None:
    missing = [flag for flag in ("url", "user", "site", "wlan") if not getattr(args, flag)]
    if missing:
        msg = ", ".join(f"--{flag}" for flag in missing)
        raise SystemExit(f"Missing required arguments: {msg}")


def prompt_password(args: argparse.Namespace) -> None:
    if not args.password:
        args.password = getpass.getpass("UniFi Password: ")


def run_cli(argv: Sequence[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    ensure_cli_args(args)
    prompt_password(args)

    client = UniFiClient(args.url, verify_ssl=args.verify_ssl, timeout=args.timeout)

    try:
        client.login(args.user, args.password)
        wlan, known_devices = client.fetch_mac_filter_details(args.site, args.wlan)
    except Exception as exc:  # pragma: no cover - surface actual error to user
        print(f"Error: {exc}")
        LOGGER.exception("CLI execution failed")
        return 1

    labelled = label_mac_addresses(wlan.mac_filter_list, known_devices)

    if args.out:
        export_results(labelled, args.out, args.format)
        print(f"Exported {len(labelled)} entries to {args.out} ({args.format}).")
    else:
        print_table(labelled)
    return 0


def export_results(entries: Iterable[Tuple[str, str]], outfile: str, fmt: str) -> None:
    fmt = fmt.lower()
    entries = list(entries)
    if fmt == "txt":
        lines = [f"{mac}\t{name}" for mac, name in entries]
        Path(outfile).write_text("\n".join(lines), encoding="utf-8")
    elif fmt == "csv":
        import csv

        with open(outfile, "w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["MAC", "Name"])
            writer.writerows(entries)
    elif fmt == "xlsx":
        try:
            import pandas as pd
        except ImportError as exc:  # pragma: no cover - depends on optional dependency
            raise RuntimeError(
                "pandas and openpyxl are required for XLSX export. Install them via 'pip install pandas openpyxl'."
            ) from exc
        data = {"MAC": [mac for mac, _ in entries], "Name": [name for _, name in entries]}
        df = pd.DataFrame(data)
        df.to_excel(outfile, index=False)
    else:  # pragma: no cover - defensive programming
        raise ValueError(f"Unsupported export format: {fmt}")


def print_table(entries: List[Tuple[str, str]]) -> None:
    if not entries:
        print("No MAC addresses found.")
        return

    mac_width = max(len(mac) for mac, _ in entries)
    name_width = max(len(name) for _, name in entries)
    header = f"{'MAC'.ljust(mac_width)}  {'Name'.ljust(name_width)}"
    divider = f"{'-' * mac_width}  {'-' * name_width}"
    print(header)
    print(divider)
    for mac, name in entries:
        print(f"{mac.ljust(mac_width)}  {name.ljust(name_width)}")
