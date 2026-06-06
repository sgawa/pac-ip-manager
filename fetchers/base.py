from __future__ import annotations

import json
from abc import ABC, abstractmethod
from datetime import date
from typing import Any


class BaseFetcher(ABC):
    service: str = ""

    @abstractmethod
    def fetch(self) -> Any:
        """Return raw service data."""
        raise NotImplementedError

    @abstractmethod
    def normalize(self, raw: Any) -> list[dict[str, str]]:
        """Return normalized entries for the unified PAC list format."""
        raise NotImplementedError

    def build_output(self, entries: list[dict[str, str]]) -> dict[str, Any]:
        return {
            "service": self.service,
            "updated_at": date.today().isoformat(),
            "schema_version": "1",
            "entries": self.dedupe_entries(entries),
        }

    def run(self) -> dict[str, Any]:
        raw = self.fetch()
        return self.build_output(self.normalize(raw))

    @staticmethod
    def make_entry(entry_type: str, value: str, action: str = "DIRECT") -> dict[str, str]:
        return {
            "type": entry_type,
            "value": value.strip(),
            "action": action,
        }

    @staticmethod
    def dedupe_entries(entries: list[dict[str, str]]) -> list[dict[str, str]]:
        seen: set[tuple[str, str, str]] = set()
        deduped: list[dict[str, str]] = []

        for entry in entries:
            value = entry.get("value", "").strip()
            if not value:
                continue

            normalized = {
                "type": entry["type"],
                "value": value,
                "action": entry.get("action", "DIRECT"),
            }
            key = (normalized["type"], normalized["value"], normalized["action"])
            if key in seen:
                continue

            seen.add(key)
            deduped.append(normalized)

        return deduped

    @classmethod
    def print_cli_output(cls) -> None:
        print(json.dumps(cls().run(), ensure_ascii=False, indent=2, sort_keys=True))
