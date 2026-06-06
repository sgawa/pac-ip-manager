from __future__ import annotations

import requests

from fetchers.base import BaseFetcher


class ZoomFetcher(BaseFetcher):
    service = "zoom"
    endpoint = "https://assets.zoom.us/docs/ipranges/Zoom.txt"

    def fetch(self) -> str:
        response = requests.get(self.endpoint, timeout=30)
        response.raise_for_status()
        return response.text

    def normalize(self, raw: str) -> list[dict[str, str]]:
        entries: list[dict[str, str]] = []

        for line in raw.splitlines():
            value = line.strip()
            if not value or value.startswith("#"):
                continue

            entries.append(self.make_entry("ip_range", value))

        return self.dedupe_entries(entries)


if __name__ == "__main__":
    ZoomFetcher.print_cli_output()
