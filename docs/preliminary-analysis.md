# Preliminary Code Analysis

## Scope
This analysis covers the legacy export script located at `docs/oldscript.py`. The tool logs in to a UniFi Network controller and exports MAC filter lists from a chosen WLAN profile.

## High-Level Structure
| Component | Responsibility |
| --- | --- |
| `login` | Authenticates against the UniFi controller using the legacy `/api/login` endpoint. |
| `resolve_site_code` | Converts a human-readable site descriptor to its internal site code. |
| `export_list` | Serialises MAC addresses into TXT, CSV, or XLSX outputs. |
| `main` | Parses CLI arguments, orchestrates authentication, site lookup, WLAN fetch, and export. |

## Data Flow
1. Parse CLI arguments and prompt for a password when not provided.
2. Authenticate and retrieve session cookies via `/api/login`.
3. Resolve the site code using `/api/self/sites`.
4. Download WLAN configurations via `/api/s/<site>/rest/wlanconf`.
5. Locate the requested WLAN and export its `mac_filter_list`.

## Dependencies and Requirements
- **Runtime:** Python 3. Requests and urllib3 are required; pandas is optional for XLSX export.
- **Security:** TLS verification is disabled by default (`verify=False`), which avoids certificate errors but exposes users to MITM risks.
- **Controller Compatibility:** Relies on legacy UniFi API routes (`/api/login`). Modern UniFi OS versions may require token-based authentication or different endpoints.

## Notable Observations
- Password prompting happens in plain text; no support for environment variables or keyring storage.
- No retry logic or timeout customization beyond the hard-coded 10-second timeout per request.
- Lack of structured logging; output is limited to `print` statements with basic success/failure messages.
- Error handling exits the process immediately; no partial recovery or detailed diagnostics.
- Script lives under `docs/`, indicating it is legacy or awaiting relocation to a proper package layout.

## Potential Risks
- **Authentication Changes:** If the controller deprecates `/api/login`, the script will fail to authenticate.
- **Certificate Handling:** Disabling TLS verification may violate security policies.
- **Scalability:** Export is entirely in-memory; very large MAC lists may stress memory.
- **Maintainability:** Monolithic script structure makes testing and reuse difficult.

## Recommended Next Steps
1. **Rehome the Script:** Move logic into a `src/` package with unit tests, leaving a thin CLI wrapper.
2. **Improve Security:** Allow enabling TLS verification and support token-based authentication flows.
3. **Add Logging:** Use the `logging` module to emit structured logs and levels.
4. **Extend Configuration:** Provide configuration via environment variables or config files in addition to CLI flags.
5. **Document Dependencies:** Publish a `requirements.txt` and installation instructions.

## Suggested Metrics for Future Review
- Number of supported output formats and export success rate.
- Test coverage once unit tests are introduced.
- Average time to export for common list sizes.

