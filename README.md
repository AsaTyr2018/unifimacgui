# UniFi MAC Export GUI

Command-line helper for exporting MAC filter lists from a UniFi Network controller.

## Features
- Logs into a UniFi controller and resolves the target site.
- Exports MAC filter lists to TXT, CSV, or XLSX formats.
- Gracefully prompts for credentials when not provided via flags.

## Quick Start
```bash
python docs/oldscript.py --url https://<controller-ip>:8443 \
  --user <username> --site <SiteName> --wlan <WlanName> \
  --out mac_export.csv --format csv
```

## Documentation
- [Preliminary analysis](docs/preliminary-analysis.md)

## Development
This repository currently ships a single script under `docs/oldscript.py`. Review the
preliminary analysis for refactoring opportunities before expanding the codebase.

## Changelog
See `Changelog/Changelog.md`.

## License
MIT
