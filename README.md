# UniFi MAC Filter Viewer

Cross-platform tool for exploring UniFi controller MAC filter lists via a Windows-friendly
GUI with a Linux-ready CLI fallback.

## Features
- Log in to a UniFi Network controller and discover available sites and WLAN profiles.
- Display MAC filter lists alongside resolved device names pulled from the "Known devices" catalogue.
- Export MAC lists (including friendly names) to TXT, CSV, or XLSX when using the CLI.
- Toggle SSL verification and timeouts for stricter environments.

## Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Launch the GUI (recommended on Windows)
python -m unifimacgui

# Force the CLI (ideal for Linux servers)
python -m unifimacgui --cli --url https://<controller-ip>:8443 \
  --user <username> --site <SiteName> --wlan <WlanName>

# Export the MAC filter list with resolved names
python -m unifimacgui --cli --url https://<controller-ip>:8443 \
  --user <username> --site <SiteName> --wlan <WlanName> \
  --out mac_filter.xlsx --format xlsx
```

## Configuration

| Option | Default | Notes |
| --- | --- | --- |
| `--verify-ssl` | disabled | Enable to enforce certificate validation. |
| `--timeout` | `10` | HTTP timeout in seconds for controller calls. |

## Usage

- Windows users can double-click `python -m unifimacgui` (or create a shortcut) to open the GUI.
- Linux users typically run the CLI variant on headless hosts using the `--cli` flag.
- The GUI automatically maps MAC addresses to device names when known; unknown devices are labelled `Unknown`.

## Development

Source code lives in `src/unifimacgui/`. Run unit tests with `pytest`.
Optional XLSX exports require `pandas` and `openpyxl` (install via `pip install pandas openpyxl`).

## Changelog
See `Changelog/Changelog.md`.

## License
MIT
