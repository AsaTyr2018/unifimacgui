"""Client helpers for interacting with the UniFi Network controller API."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import requests
import urllib3

LOGGER = logging.getLogger(__name__)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@dataclass
class Site:
    """Lightweight representation of a UniFi site."""

    code: str
    description: str


@dataclass
class WlanProfile:
    """Representation of a WLAN profile and its MAC filter list."""

    name: str
    mac_filter_list: List[str]


class UniFiClient:
    """Simple wrapper around the UniFi controller session."""

    def __init__(self, base_url: str, verify_ssl: bool = False, timeout: int = 10) -> None:
        self.base_url = base_url.rstrip("/")
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self.session = requests.Session()

    def login(self, username: str, password: str) -> None:
        LOGGER.debug("Logging into UniFi controller at %s", self.base_url)
        response = self.session.post(
            f"{self.base_url}/api/login",
            json={"username": username, "password": password},
            timeout=self.timeout,
            verify=self.verify_ssl,
        )
        response.raise_for_status()

    def fetch_sites(self) -> List[Site]:
        LOGGER.debug("Fetching available sites")
        response = self.session.get(
            f"{self.base_url}/api/self/sites",
            timeout=self.timeout,
            verify=self.verify_ssl,
        )
        response.raise_for_status()
        data = response.json().get("data", [])
        sites = [
            Site(code=item.get("name", ""), description=item.get("desc") or item.get("name", ""))
            for item in data
        ]
        sites.sort(key=lambda s: s.description.lower())
        return sites

    def fetch_wlans(self, site_code: str) -> List[WlanProfile]:
        LOGGER.debug("Fetching WLAN profiles for site %s", site_code)
        response = self.session.get(
            f"{self.base_url}/api/s/{site_code}/rest/wlanconf",
            timeout=self.timeout,
            verify=self.verify_ssl,
        )
        response.raise_for_status()
        wlans: List[WlanProfile] = []
        for item in response.json().get("data", []):
            macs = item.get("mac_filter_list") or []
            wlans.append(WlanProfile(name=item.get("name", ""), mac_filter_list=list(macs)))
        wlans.sort(key=lambda w: w.name.lower())
        return wlans

    def fetch_known_devices(self, site_code: str) -> Dict[str, str]:
        """Return a mapping of MAC address to friendly name for known devices."""

        LOGGER.debug("Fetching known devices for site %s", site_code)
        response = self.session.get(
            f"{self.base_url}/api/s/{site_code}/stat/alluser",
            timeout=self.timeout,
            verify=self.verify_ssl,
        )
        response.raise_for_status()
        devices = response.json().get("data", [])
        mapping: Dict[str, str] = {}
        for device in devices:
            mac = (device.get("mac") or "").upper()
            if not mac:
                continue
            name = _pick_name(device)
            if name:
                mapping[mac] = name
        return mapping

    def fetch_mac_filter_details(self, site_code: str, wlan_name: str) -> Tuple[WlanProfile, Dict[str, str]]:
        wlans = self.fetch_wlans(site_code)
        lookup = {wlan.name: wlan for wlan in wlans}
        if wlan_name not in lookup:
            available = ", ".join(sorted(lookup))
            raise ValueError(f"WLAN '{wlan_name}' not found. Available: {available}")
        known_devices = self.fetch_known_devices(site_code)
        return lookup[wlan_name], known_devices


def _pick_name(device: Dict[str, Optional[str]]) -> Optional[str]:
    """Return the best available display name for a device record."""

    for key in ("name", "hostname", "usergroup_name", "oui"):
        value = device.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def label_mac_addresses(macs: List[str], known_devices: Dict[str, str]) -> List[Tuple[str, str]]:
    """Attach friendly labels to MAC addresses, defaulting to 'Unknown'."""

    labelled: List[Tuple[str, str]] = []
    for mac in macs:
        normalised = mac.upper()
        label = known_devices.get(normalised, "Unknown")
        labelled.append((normalised, label))
    return labelled
