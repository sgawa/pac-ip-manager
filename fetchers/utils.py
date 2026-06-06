from __future__ import annotations

import ipaddress
import re
from typing import Any

from bs4 import BeautifulSoup


CIDR_CANDIDATE_PATTERN = re.compile(r"(?<![A-Za-z0-9_.:-])(?:[0-9A-Fa-f:.]+/[0-9]{1,3})(?![A-Za-z0-9_.:-])")
HOSTNAME_PATTERN = re.compile(
    r"(?<![A-Za-z0-9_.-])(?:\*\.)?(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z]{2,63}(?![A-Za-z0-9_.-])"
)
URL_PATTERN = re.compile(r"https?://[^\s<>()\"']+")


def html_to_text(html: str, selector: str | None = None) -> str:
    soup = BeautifulSoup(html, "html.parser")
    content = soup.select_one(selector) if selector else None
    content = content or soup.select_one("main") or soup.select_one("article") or soup.body or soup
    return content.get_text("\n", strip=True)


def extract_cidrs(text: str) -> list[str]:
    cidrs: list[str] = []
    seen: set[str] = set()

    for match in CIDR_CANDIDATE_PATTERN.finditer(text):
        value = match.group(0).strip(".,;:()[]{}'\"")
        try:
            ipaddress.ip_network(value, strict=False)
        except ValueError:
            continue

        if value not in seen:
            seen.add(value)
            cidrs.append(value)

    return cidrs


def extract_hostnames(text: str) -> list[str]:
    hostnames: list[str] = []
    seen: set[str] = set()

    for match in HOSTNAME_PATTERN.finditer(text):
        hostname = clean_hostname(match.group(0))
        if not hostname or hostname in seen:
            continue

        seen.add(hostname)
        hostnames.append(hostname)

    return hostnames


def extract_urls(text: str) -> list[str]:
    urls: list[str] = []
    seen: set[str] = set()

    for match in URL_PATTERN.finditer(text):
        url = match.group(0).strip(".,;:()[]{}'\"")
        if url not in seen:
            seen.add(url)
            urls.append(url)

    return urls


def domain_entry_type(value: str) -> str:
    return "url" if value.startswith(("http://", "https://")) or "*" in value or "/" in value else "fqdn"


def clean_hostname(hostname: str) -> str:
    return hostname.strip(".,;:()[]{}'\"").lower()


def flatten_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        strings: list[str] = []
        for item in value:
            strings.extend(flatten_strings(item))
        return strings
    if isinstance(value, dict):
        strings = []
        for item in value.values():
            strings.extend(flatten_strings(item))
        return strings
    return []
