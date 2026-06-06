from __future__ import annotations

import requests

from fetchers.base import BaseFetcher
from fetchers.utils import domain_entry_type, extract_cidrs, extract_hostnames, extract_urls, html_to_text


class GoogleMeetFetcher(BaseFetcher):
    service = "google_meet"
    endpoint = "https://support.google.com/a/answer/1279090?hl=en-GB"

    def fetch(self) -> str:
        response = requests.get(
            self.endpoint,
            timeout=30,
            headers={"User-Agent": "pac-ip-manager/1.0"},
        )
        response.raise_for_status()
        return response.text

    def normalize(self, raw: str) -> list[dict[str, str]]:
        text = html_to_text(raw)
        section = self._meet_network_section(text)
        entries: list[dict[str, str]] = []

        urls = extract_urls(section)
        hostname_source = section
        for url in urls:
            entries.append(self.make_entry("url", url))
            hostname_source = hostname_source.replace(url, "")

        for ip_range in extract_cidrs(section):
            entries.append(self.make_entry("ip_range", ip_range))

        for hostname in extract_hostnames(hostname_source):
            entries.append(self.make_entry(domain_entry_type(hostname), hostname))

        return self.dedupe_entries(entries)

    @staticmethod
    def _meet_network_section(text: str) -> str:
        start = text.find("Domains for static resources")
        if start == -1:
            start = text.find("Step 3: Allow access to Google IP address ranges")
        end = text.find("Step 4: Review bandwidth requirements", start)

        if start == -1:
            return text
        if end == -1:
            return text[start:]
        return text[start:end]


if __name__ == "__main__":
    GoogleMeetFetcher.print_cli_output()
