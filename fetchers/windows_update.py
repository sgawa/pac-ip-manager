from __future__ import annotations

import requests
from bs4 import BeautifulSoup

from fetchers.base import BaseFetcher
from fetchers.utils import domain_entry_type, extract_hostnames, extract_urls


class WindowsUpdateFetcher(BaseFetcher):
    service = "windows_update"
    endpoint = "https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints"

    def fetch(self) -> str:
        response = requests.get(
            self.endpoint,
            timeout=30,
            headers={"User-Agent": "pac-ip-manager/1.0"},
        )
        response.raise_for_status()
        return response.text

    def normalize(self, raw: str) -> list[dict[str, str]]:
        entries: list[dict[str, str]] = []

        for destination in self._windows_update_destinations(raw):
            for url in extract_urls(destination):
                entries.append(self.make_entry("url", url))

            for hostname in extract_hostnames(destination):
                value = self._restore_trailing_wildcard(destination, hostname)
                entries.append(self.make_entry(domain_entry_type(value), value))

        return self.dedupe_entries(entries)

    @staticmethod
    def _windows_update_destinations(html: str) -> list[str]:
        soup = BeautifulSoup(html, "html.parser")
        destinations: list[str] = []
        in_windows_update = False

        for row in soup.select("tr"):
            cells = [cell.get_text(" ", strip=True) for cell in row.find_all(["td", "th"])]
            if not cells:
                continue

            section_name = cells[0].strip()
            if section_name == "Windows Update":
                in_windows_update = True
                continue

            if in_windows_update and section_name:
                break

            if in_windows_update and len(cells) >= 4:
                destination = cells[-1].strip()
                if destination:
                    destinations.append(destination)

        return destinations

    @staticmethod
    def _restore_trailing_wildcard(source: str, hostname: str) -> str:
        return f"{hostname}*" if f"{hostname}*" in source.lower() else hostname


if __name__ == "__main__":
    WindowsUpdateFetcher.print_cli_output()
