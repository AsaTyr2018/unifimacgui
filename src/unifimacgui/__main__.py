"""Module entry point for `python -m unifimacgui`."""

from .app import run

if __name__ == "__main__":  # pragma: no cover - module execution
    raise SystemExit(run())
