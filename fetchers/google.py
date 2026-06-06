from __future__ import annotations

from typing import Any

import requests

from fetchers.base import BaseFetcher


class GoogleFetcher(BaseFetcher):
    service = "google"
    endpoint = "https://www.gstatic.com/ipranges/goog.json"

    def fetch(self) -> dict[str, Any]:
        response = requests.get(self.endpoint, timeout=30)
        response.raise_for_status()
        return response.json()

    def normalize(self, raw: dict[str, Any]) -> list[dict[str, str]]:
        entries: list[dict[str, str]] = []

        for prefix in raw.get("prefixes", []) or []:
            ipv4_prefix = prefix.get("ipv4Prefix")
            if ipv4_prefix:
                entries.append(self.make_entry("ip_range", ipv4_prefix))

        return self.dedupe_entries(entries)


if __name__ == "__main__":
    GoogleFetcher.print_cli_output()
