from __future__ import annotations

import re

import requests
from bs4 import BeautifulSoup, Tag

from fetchers.base import BaseFetcher
from fetchers.utils import domain_entry_type


ANNOTATION_PATTERN = re.compile(r"\s*\([^)]*\)\s*$")


class AdobeUpdatesFetcher(BaseFetcher):
    service = "adobe_updates"
    endpoint = "https://helpx.adobe.com/enterprise/kb/network-endpoints.html"
    section_headings = (
        "Deployment and fulfillment services:",
        "Updater:",
    )
    fallback_endpoints = (
        "acrs.adobe.com",
        "adobecloudpackager.adobe.io",
        "adminconsole.adobe.com",
        "cc-ext-prod-pkgs.s3.amazonaws.com",
        "ccmdls.adobe.com",
        "ccmdl.adobe.com",
        "ans.oobesaas.adobe.com",
        "ars.oobesaas.adobe.com",
        "cdn-ffc.oobesaas.adobe.com",
        "ffc-icons.oobesaas.adobe.com",
        "ffc-static-cdn.oobesaas.adobe.com",
        "prod-rel-ffc-ccm.oobesaas.adobe.com",
        "acc.adobeoobe.com",
        "prod.acp.adobeoobe.com",
        "mir-s3-cdn-cf.behance.net",
        "swupmf.adobe.com",
        "swupdl.adobe.com",
        "oobe.adobe.com",
        "productrouter.adobe.com",
        "s3.amazonaws.com",
        "s3.amazonaws.com/tron-ffc-icons-prod/",
        "tron-prod-customized-user-packages.s3.amazonaws.com",
        "armmf.adobe.com",
        "ardownload.adobe.com",
        "ardownload2.adobe.com",
        "agsupdate.adobe.com",
        "http://armdl.adobe.com/",
    )

    def fetch(self) -> str:
        try:
            response = requests.get(
                self.endpoint,
                timeout=30,
                headers={"User-Agent": "Mozilla/5.0 pac-ip-manager/1.0"},
            )
            response.raise_for_status()
            return response.text
        except requests.RequestException:
            return self._fallback_html()

    def normalize(self, raw: str) -> list[dict[str, str]]:
        entries: list[dict[str, str]] = []
        endpoints = self._section_endpoints(raw) or list(self.fallback_endpoints)

        for endpoint in endpoints:
            entries.append(self.make_entry(domain_entry_type(endpoint), endpoint))

        return self.dedupe_entries(entries)

    def _section_endpoints(self, html: str) -> list[str]:
        endpoints: list[str] = []
        soup = BeautifulSoup(html, "html.parser")

        for heading in self.section_headings:
            for item in self._items_after_heading(soup, heading):
                endpoint = self._clean_endpoint(item)
                if endpoint:
                    endpoints.append(endpoint)

        return endpoints

    @staticmethod
    def _items_after_heading(soup: BeautifulSoup, heading: str) -> list[str]:
        node = soup.find(string=lambda value: bool(value and value.strip() == heading))
        if not node:
            return []

        parent = node.parent
        if not isinstance(parent, Tag):
            return []

        current = parent
        while current:
            current = current.find_next_sibling()
            if not isinstance(current, Tag):
                continue

            if current.name == "ul":
                return [item.get_text(" ", strip=True) for item in current.find_all("li")]

            if current.name and current.get_text(" ", strip=True).endswith(":"):
                return []

        return []

    @staticmethod
    def _clean_endpoint(value: str) -> str:
        cleaned = value.replace("\xa0", " ").strip()
        cleaned = ANNOTATION_PATTERN.sub("", cleaned).strip()
        return cleaned.strip(".,;")

    @classmethod
    def _fallback_html(cls) -> str:
        items = "\n".join(f"<li>{endpoint}</li>" for endpoint in cls.fallback_endpoints)
        return f"<html><body><p>{cls.section_headings[0]}</p><ul>{items}</ul></body></html>"


if __name__ == "__main__":
    AdobeUpdatesFetcher.print_cli_output()
