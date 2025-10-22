#!/usr/bin/env python3
"""
unifi_mac_export.py
Export the MAC‑filter list of a specific WLAN from a UniFi Network application
to TXT, CSV or Excel (XLSX).

Example:
    python unifi_mac_export.py --url https://[UNIFI_IP]:8443 \
        --user [username] --site [MySite] --wlan [MyWLAN] \
        --out mac_export.xlsx --format xlsx
"""

import argparse
import getpass
import csv
import sys
import os
from typing import List

import requests
import urllib3

# Try pandas for Excel export; fall back gracefully if absent.
try:
    import pandas as pd
except ImportError:  # pragma: no cover
    pd = None

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def login(session: requests.Session, url: str, username: str, password: str) -> None:
    """Authenticate against the UniFi controller."""
    resp = session.post(
        f"{url}/api/login",
        json={"username": username, "password": password},
        verify=False,
        timeout=10,
    )
    resp.raise_for_status()


def resolve_site_code(session: requests.Session, url: str, site_hint: str) -> str:
    """
    Resolve a human‑readable site description (e.g. 'FiWe') or code
    to the internal site code used by the API.
    """
    resp = session.get(f"{url}/api/self/sites", verify=False, timeout=10)
    resp.raise_for_status()
    for site in resp.json()["data"]:
        if site_hint.lower() in {site["desc"].lower(), site["name"].lower()}:
            return site["name"]
    raise ValueError(
        f"Site '{site_hint}' not found. Available: "
        f"{[s['desc'] for s in resp.json()['data']]}"
    )


def export_list(macs: List[str], outfile: str, fmt: str) -> None:
    """Write the MAC list to txt, csv or xlsx."""
    fmt = fmt.lower()
    if fmt == "txt":
        with open(outfile, "w", newline="") as f:
            f.write("\n".join(macs))
    elif fmt == "csv":
        with open(outfile, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["MAC"])
            writer.writerows([[m] for m in macs])
    elif fmt == "xlsx":
        if pd is None:
            raise RuntimeError(
                "pandas (and openpyxl) required for xlsx export. "
                "Install them with 'pip install pandas openpyxl'."
            )
        df = pd.DataFrame({"MAC": macs})
        df.to_excel(outfile, index=False)
    else:
        raise ValueError("Unknown format. Choose txt, csv or xlsx.")


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Export the MAC‑filter list from a UniFi WLAN profile."
    )
    ap.add_argument("--url", required=True, help="Controller base URL, e.g. https://ip:8443")
    ap.add_argument("--user", required=True, help="UniFi username")
    ap.add_argument("--password", help="UniFi password (leave empty to prompt)")
    ap.add_argument("--site", required=True, help="Site name/description, e.g. MySite")
    ap.add_argument("--wlan", required=True, help="WLAN profile name, e.g. MyWifi")
    ap.add_argument(
        "--out", default="mac_export.txt", help="Output filename (defaults to txt)"
    )
    ap.add_argument(
        "--format",
        choices=["txt", "csv", "xlsx"],
        default="txt",
        help="Export format",
    )
    args = ap.parse_args()

    if not args.password:
        args.password = getpass.getpass("UniFi Password: ")

    sess = requests.Session()

    # ---------- Authenticate ----------
    try:
        login(sess, args.url, args.user, args.password)
    except Exception as e:  # pragma: no cover
        print("❌ Login failed:", e)
        sys.exit(1)

    # ---------- Resolve site ----------
    try:
        site_code = resolve_site_code(sess, args.url, args.site)
    except ValueError as e:  # pragma: no cover
        print(e)
        sys.exit(1)

    # ---------- Fetch WLAN configs ----------
    resp = sess.get(f"{args.url}/api/s/{site_code}/rest/wlanconf", verify=False, timeout=10)
    resp.raise_for_status()
    wlans = resp.json()["data"]

    target = next((w for w in wlans if w.get("name") == args.wlan), None)
    if target is None:
        print(f"WLAN '{args.wlan}' not found in site '{args.site}'.")
        sys.exit(1)

    macs = target.get("mac_filter_list", [])
    if not macs:
        print(f"No MAC addresses found for WLAN '{args.wlan}'.")
        sys.exit(0)

    try:
        export_list(macs, args.out, args.format)
    except Exception as e:  # pragma: no cover
        print("Export failed:", e)
        sys.exit(1)

    print(f"✅ Exported {len(macs)} MAC addresses to '{args.out}' as {args.format.upper()}.")


if __name__ == "__main__":
    main()
