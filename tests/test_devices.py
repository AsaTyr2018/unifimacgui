"""Unit tests for device labelling utilities."""

from unifimacgui.client import label_mac_addresses


def test_label_mac_addresses_resolves_known_devices() -> None:
    macs = ["aa:bb:cc:dd:ee:ff", "11:22:33:44:55:66", "77:88:99:aa:bb:cc"]
    known = {
        "AA:BB:CC:DD:EE:FF": "Laptop",
        "11:22:33:44:55:66".upper(): "Tablet",
    }

    labelled = label_mac_addresses(macs, known)

    assert labelled == [
        ("AA:BB:CC:DD:EE:FF", "Laptop"),
        ("11:22:33:44:55:66".upper(), "Tablet"),
        ("77:88:99:AA:BB:CC", "Unknown"),
    ]
