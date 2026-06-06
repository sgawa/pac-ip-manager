from __future__ import annotations

import requests
from bs4 import BeautifulSoup

from fetchers.base import BaseFetcher
from fetchers.utils import domain_entry_type, extract_cidrs, extract_hostnames, html_to_text


class WebexMeetingsFetcher(BaseFetcher):
    service = "webex_meetings"
    endpoint = "https://help.webex.com/en-us/article/WBX264/Network-Requirements-for-Webex-Services"

    def fetch(self) -> str:
        response = requests.get(
            self.endpoint,
            timeout=30,
            headers={"User-Agent": "pac-ip-manager/1.0"},
        )
        response.raise_for_status()
        return response.text

    def normalize(self, raw: str) -> list[dict[str, str]]:
        article_text = html_to_text(raw)
        domain_text = self._domain_section_text(raw) or article_text
        entries: list[dict[str, str]] = []

        for ip_range in extract_cidrs(article_text):
            entries.append(self.make_entry("ip_range", ip_range))

        for hostname in extract_hostnames(domain_text):
            if hostname == "help.webex.com":
                continue
            entries.append(self.make_entry(domain_entry_type(hostname), hostname))

        return self.dedupe_entries(entries)

    @staticmethod
    def _domain_section_text(html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        link = soup.find(string=lambda value: bool(value and "Domains that need to be allowed" in value))
        if not link:
            return ""

        panel = link.find_parent("div", class_="panel")
        if not panel:
            return ""

        return panel.get_text("\n", strip=True)


if __name__ == "__main__":
    WebexMeetingsFetcher.print_cli_output()
