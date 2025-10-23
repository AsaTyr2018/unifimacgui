## [2025-10-22 14:01] Document preliminary analysis
**Change Type:** Standard Change
**Why:** Provide an initial assessment of the legacy export script.
**What changed:** Added a preliminary analysis document, refreshed README links, and established the changelog structure.
**Impact:** Documentation only; no runtime impact.
**Testing:** Not applicable.
**Docs:** README and docs updated.
**Rollback Plan:** Delete `docs/preliminary-analysis.md`, revert README, and remove the changelog entry.
**Refs:** N/A

## [2025-10-22 14:19] Replace legacy script with GUI + CLI app
**Change Type:** Normal Change  
**Why:** Deliver a more user-friendly UniFi MAC filter viewer while keeping Linux CLI support.  
**What changed:** Introduced a Tkinter GUI and refreshed CLI under `src/unifimacgui`, added unit tests, updated README guidance, and wired a shared entry point.  
**Impact:** Users can launch a GUI by default (`python -m unifimacgui`) or continue using the CLI with exports; MAC names resolve via known devices.  
**Testing:** `pytest` (unit coverage for MAC/name mapping).  
**Docs:** README updated.  
**Rollback Plan:** Remove the new `src/unifimacgui` package, delete tests, and restore the previous README instructions.  
**Refs:** N/A

## [2025-10-22 15:05] Add live filter to MAC table
**Change Type:** Normal Change
**Why:** Allow users to quickly search MAC entries in the GUI.
**What changed:** Added a search box above the MAC table, introduced reusable filtering logic, and covered it with unit tests.
**Impact:** GUI users can filter MACs without exporting; CLI behaviour unchanged.
**Testing:** `pytest` (GUI filtering helper tests).
**Docs:** README feature list updated.
**Rollback Plan:** Revert the GUI search commit and delete the new unit test.
**Refs:** N/A
