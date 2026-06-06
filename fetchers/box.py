from __future__ import annotations

from typing import Any

import requests
from bs4 import BeautifulSoup

from fetchers.base import BaseFetcher
from fetchers.utils import domain_entry_type, extract_cidrs, extract_hostnames, flatten_strings


class BoxFetcher(BaseFetcher):
    service = "box"
    ignored_hostnames = {
        "network.http.accept-encoding.secure",
        "proxy.pac",
    }
    firewall_endpoint = (
        "https://support.box.com/hc/en-us/articles/360043696434-"
        "Configuring-A-Firewall-For-Box-Applications"
    )
    ips_endpoint = "https://support.box.com/ips"

    def fetch(self) -> dict[str, Any]:
        headers = {"User-Agent": "pac-ip-manager/1.0"}

        firewall_response = requests.get(self.firewall_endpoint, timeout=30, headers=headers)
        firewall_response.raise_for_status()

        ips_response = requests.get(self.ips_endpoint, timeout=30, headers=headers)
        ips_response.raise_for_status()

        return {
            "firewall_html": firewall_response.text,
            "ips": ips_response.json(),
        }

    def normalize(self, raw: dict[str, Any]) -> list[dict[str, str]]:
        entries: list[dict[str, str]] = []
        firewall_text = self._firewall_code_text(raw.get("firewall_html", ""))

        for ip_range in extract_cidrs(firewall_text):
            entries.append(self.make_entry("ip_range", ip_range))

        for value in flatten_strings(raw.get("ips", {})):
            for ip_range in extract_cidrs(value):
                entries.append(self.make_entry("ip_range", ip_range))

        for hostname in extract_hostnames(firewall_text):
            if hostname in self.ignored_hostnames:
                continue
            entries.append(self.make_entry(domain_entry_type(hostname), hostname))

        return self.dedupe_entries(entries)

    @staticmethod
    def _firewall_code_text(html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        code_blocks = soup.select("pre, code")
        if not code_blocks:
            return soup.get_text("\n", strip=True)

        return "\n".join(block.get_text("\n", strip=True) for block in code_blocks)


if __name__ == "__main__":
    BoxFetcher.print_cli_output()
