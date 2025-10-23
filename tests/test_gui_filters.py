"""Tests for GUI helper utilities."""

from unifimacgui.gui import filter_entries


def test_filter_entries_returns_all_for_empty_term() -> None:
    entries = [("AA:BB", "Living Room"), ("CC:DD", "Office")]

    assert filter_entries(entries, "") == entries


def test_filter_entries_matches_mac_and_name_case_insensitive() -> None:
    entries = [
        ("AA:BB:CC:DD:EE:FF", "Printer"),
        ("11:22:33:44:55:66", "Kitchen Camera"),
    ]

    assert filter_entries(entries, "printer") == [entries[0]]
    assert filter_entries(entries, "22:33") == [entries[1]]
