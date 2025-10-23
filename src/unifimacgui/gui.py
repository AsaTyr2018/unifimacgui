"""Tkinter-based GUI for viewing UniFi MAC filter lists."""

from __future__ import annotations

import threading
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Dict, List, Optional

from .client import Site, UniFiClient, WlanProfile, label_mac_addresses


def filter_entries(entries: List[tuple[str, str]], term: str) -> List[tuple[str, str]]:
    """Return entries whose MAC or name contains the search term."""

    if not term:
        return list(entries)

    needle = term.lower()
    filtered: List[tuple[str, str]] = []
    for mac, name in entries:
        if needle in mac.lower() or needle in name.lower():
            filtered.append((mac, name))
    return filtered


class GuiState:
    """Mutable state shared between GUI callbacks."""

    def __init__(self) -> None:
        self.client: Optional[UniFiClient] = None
        self.sites: List[Site] = []
        self.wlans: Dict[str, List[WlanProfile]] = {}
        self.known_devices: Dict[str, Dict[str, str]] = {}


class UnifiGui(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("UniFi MAC Filter Viewer")
        self.geometry("720x520")
        self.resizable(True, True)

        self.state = GuiState()

        self.url_var = tk.StringVar()
        self.user_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Enter credentials and press Connect")

        self.site_var = tk.StringVar()
        self.wlan_var = tk.StringVar()
        self.search_var = tk.StringVar()

        self._build_form()
        self._build_table()

        self._all_entries: List[tuple[str, str]] = []
        self.search_var.trace_add("write", lambda *_: self._refresh_table())

    # ------------------------------------------------------------------ UI setup
    def _build_form(self) -> None:
        container = ttk.Frame(self, padding=16)
        container.pack(fill=tk.X)

        ttk.Label(container, text="Controller URL").grid(row=0, column=0, sticky=tk.W, pady=4)
        ttk.Entry(container, textvariable=self.url_var, width=40).grid(row=0, column=1, sticky=tk.EW, pady=4)

        ttk.Label(container, text="Username").grid(row=1, column=0, sticky=tk.W, pady=4)
        ttk.Entry(container, textvariable=self.user_var, width=30).grid(row=1, column=1, sticky=tk.EW, pady=4)

        ttk.Label(container, text="Password").grid(row=2, column=0, sticky=tk.W, pady=4)
        ttk.Entry(container, textvariable=self.password_var, show="*", width=30).grid(row=2, column=1, sticky=tk.EW, pady=4)

        button = ttk.Button(container, text="Connect", command=self.on_connect)
        button.grid(row=0, column=2, rowspan=3, padx=(12, 0), sticky=tk.NS)

        ttk.Label(container, text="Site").grid(row=3, column=0, sticky=tk.W, pady=4)
        self.site_combo = ttk.Combobox(container, textvariable=self.site_var, state="readonly")
        self.site_combo.grid(row=3, column=1, sticky=tk.EW, pady=4)
        self.site_combo.bind("<<ComboboxSelected>>", self.on_site_selected)

        ttk.Label(container, text="WLAN").grid(row=4, column=0, sticky=tk.W, pady=4)
        self.wlan_combo = ttk.Combobox(container, textvariable=self.wlan_var, state="readonly")
        self.wlan_combo.grid(row=4, column=1, sticky=tk.EW, pady=4)
        self.wlan_combo.bind("<<ComboboxSelected>>", self.on_wlan_selected)

        for col in range(3):
            container.columnconfigure(col, weight=1 if col == 1 else 0)

        status_label = ttk.Label(container, textvariable=self.status_var)
        status_label.grid(row=5, column=0, columnspan=3, sticky=tk.W, pady=(8, 0))

    def _build_table(self) -> None:
        table_frame = ttk.Frame(self, padding=16)
        table_frame.pack(fill=tk.BOTH, expand=True)

        filter_frame = ttk.Frame(table_frame)
        filter_frame.pack(fill=tk.X, side=tk.TOP, pady=(0, 8))
        ttk.Label(filter_frame, text="Filter").pack(side=tk.LEFT)
        ttk.Entry(filter_frame, textvariable=self.search_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0)
        )

        tree_container = ttk.Frame(table_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)

        columns = ("mac", "name")
        self.tree = ttk.Treeview(tree_container, columns=columns, show="headings")
        self.tree.heading("mac", text="MAC")
        self.tree.heading("name", text="Name")
        self.tree.column("mac", width=200, anchor=tk.W)
        self.tree.column("name", width=280, anchor=tk.W)
        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        scrollbar = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(fill=tk.Y, side=tk.RIGHT)

    # ------------------------------------------------------------------ callbacks
    def on_connect(self) -> None:
        url = self.url_var.get().strip()
        username = self.user_var.get().strip()
        password = self.password_var.get().strip()

        if not url or not username or not password:
            messagebox.showwarning("Missing data", "Please fill URL, username, and password.")
            return

        self.status_var.set("Connecting...")
        threading.Thread(target=self._connect_and_fetch_sites, args=(url, username, password), daemon=True).start()

    def _connect_and_fetch_sites(self, url: str, username: str, password: str) -> None:
        try:
            client = UniFiClient(url)
            client.login(username, password)
            sites = client.fetch_sites()
        except Exception as exc:  # pragma: no cover - UI message
            self.after(0, lambda: self._handle_error("Failed to connect", str(exc)))
            return

        def update_ui() -> None:
            self.state.client = client
            self.state.sites = sites
            self.site_combo["values"] = [site.description for site in sites]
            if sites:
                self.site_combo.current(0)
                self.on_site_selected()
            self.status_var.set("Connected. Choose a site and WLAN.")

        self.after(0, update_ui)

    def _handle_error(self, title: str, message: str) -> None:
        self.status_var.set(message)
        messagebox.showerror(title, message)

    def on_site_selected(self, *_args: object) -> None:
        idx = self.site_combo.current()
        if idx < 0:
            return
        site = self.state.sites[idx]
        self.status_var.set(f"Loading WLANs for {site.description}...")
        threading.Thread(target=self._load_site_data, args=(site,), daemon=True).start()

    def _load_site_data(self, site: Site) -> None:
        client = self.state.client
        if client is None:
            return
        try:
            wlans = client.fetch_wlans(site.code)
            known = client.fetch_known_devices(site.code)
        except Exception as exc:  # pragma: no cover - UI message
            self.after(0, lambda: self._handle_error("Failed to load site", str(exc)))
            return

        def update_ui() -> None:
            self.state.wlans[site.code] = wlans
            self.state.known_devices[site.code] = known
            self.wlan_combo["values"] = [wlan.name for wlan in wlans]
            if wlans:
                self.wlan_combo.current(0)
                self.on_wlan_selected()
            else:
                self._populate_table([])
                self.status_var.set("No WLANs found for this site.")

        self.after(0, update_ui)

    def on_wlan_selected(self, *_args: object) -> None:
        site_idx = self.site_combo.current()
        wlan_idx = self.wlan_combo.current()
        if site_idx < 0 or wlan_idx < 0:
            return
        site = self.state.sites[site_idx]
        wlans = self.state.wlans.get(site.code, [])
        if wlan_idx >= len(wlans):
            return
        wlan = wlans[wlan_idx]
        known = self.state.known_devices.get(site.code, {})
        entries = label_mac_addresses(wlan.mac_filter_list, known)
        self._populate_table(entries)
        self.status_var.set(f"Loaded {len(entries)} MAC addresses for {wlan.name}.")

    def _populate_table(self, entries: List[tuple[str, str]]) -> None:
        self._all_entries = list(entries)
        self._refresh_table()

    def _refresh_table(self) -> None:
        entries = filter_entries(self._all_entries, self.search_var.get().strip())
        self.tree.delete(*self.tree.get_children())
        for mac, name in entries:
            self.tree.insert("", tk.END, values=(mac, name))


def run_gui() -> int:
    app = UnifiGui()
    app.mainloop()
    return 0
