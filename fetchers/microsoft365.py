from __future__ import annotations

from typing import Any

import requests

from fetchers.base import BaseFetcher


class Microsoft365Fetcher(BaseFetcher):
    service = "microsoft365"
    endpoint = (
        "https://endpoints.office.com/endpoints/worldwide"
        "?clientrequestid=b10c5ed1-bad1-445f-b386-b919946339a7"
    )

    def fetch(self) -> list[dict[str, Any]]:
        response = requests.get(self.endpoint, timeout=30)
        response.raise_for_status()
        return response.json()

    def normalize(self, raw: list[dict[str, Any]]) -> list[dict[str, str]]:
        entries: list[dict[str, str]] = []

        for endpoint in raw:
            for url in endpoint.get("urls", []) or []:
                entries.append(self.make_entry("url", url))

            for ip_range in endpoint.get("ips", []) or []:
                entries.append(self.make_entry("ip_range", ip_range))

        return self.dedupe_entries(entries)


if __name__ == "__main__":
    Microsoft365Fetcher.print_cli_output()
