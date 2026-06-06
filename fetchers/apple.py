from __future__ import annotations

import re

import requests
from bs4 import BeautifulSoup

from fetchers.base import BaseFetcher


HOSTNAME_PATTERN = re.compile(
    r"(?<![A-Za-z0-9_.-])(?:\*\.)?(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z]{2,63}(?![A-Za-z0-9_.-])"
)


class AppleFetcher(BaseFetcher):
    service = "apple"
    endpoint = "https://support.apple.com/en-us/101555"

    def fetch(self) -> str:
        response = requests.get(
            self.endpoint,
            timeout=30,
            headers={"User-Agent": "pac-ip-manager/1.0"},
        )
        response.raise_for_status()
        return response.text

    def normalize(self, raw: str) -> list[dict[str, str]]:
        hostnames = self._extract_hostnames_from_html(raw)
        entries = [
            self.make_entry("url" if "*" in hostname else "fqdn", hostname)
            for hostname in hostnames
        ]
        return self.dedupe_entries(entries)

    def _extract_hostnames_from_html(self, html: str) -> list[str]:
        try:
            soup = BeautifulSoup(html, "html.parser")
            content = soup.select_one("main") or soup.select_one("article") or soup.body or soup
            candidate_text = "\n".join(
                element.get_text(" ", strip=True)
                for element in content.select("table, ul, ol, pre, code")
            )
        except Exception:
            candidate_text = ""

        if not candidate_text.strip():
            candidate_text = BeautifulSoup(html, "html.parser").get_text(" ", strip=True)

        return self._extract_hostnames(candidate_text)

    @staticmethod
    def _extract_hostnames(text: str) -> list[str]:
        hostnames: list[str] = []
        seen: set[str] = set()

        for match in HOSTNAME_PATTERN.finditer(text):
            hostname = match.group(0).strip(".,;:()[]{}'\"").lower()
            if hostname not in seen:
                seen.add(hostname)
                hostnames.append(hostname)

        return hostnames


if __name__ == "__main__":
    AppleFetcher.print_cli_output()
