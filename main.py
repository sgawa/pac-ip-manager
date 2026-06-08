from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from fetchers.adobe_updates import AdobeUpdatesFetcher
from fetchers.apple import AppleFetcher
from fetchers.box import BoxFetcher
from fetchers.google import GoogleFetcher
from fetchers.google_meet import GoogleMeetFetcher
from fetchers.microsoft365 import Microsoft365Fetcher
from fetchers.microsoft_teams import MicrosoftTeamsFetcher
from fetchers.static_domains import (
    InstagramFetcher,
    NetflixFetcher,
    PrimeVideoFetcher,
    TikTokFetcher,
    YouTubeFetcher,
)
from fetchers.webex_meetings import WebexMeetingsFetcher
from fetchers.windows_update import WindowsUpdateFetcher
from fetchers.zoom import ZoomFetcher


ROOT_DIR = Path(__file__).resolve().parent
LATEST_DIR = ROOT_DIR / "ip-lists" / "latest"
HISTORY_DIR = ROOT_DIR / "ip-lists" / "history"
SCHEMA_PATH = ROOT_DIR / "schema" / "ip-list.schema.json"

FETCHER_CLASSES = {
    Microsoft365Fetcher.service: Microsoft365Fetcher,
    MicrosoftTeamsFetcher.service: MicrosoftTeamsFetcher,
    ZoomFetcher.service: ZoomFetcher,
    WebexMeetingsFetcher.service: WebexMeetingsFetcher,
    WindowsUpdateFetcher.service: WindowsUpdateFetcher,
    AppleFetcher.service: AppleFetcher,
    GoogleFetcher.service: GoogleFetcher,
    GoogleMeetFetcher.service: GoogleMeetFetcher,
    BoxFetcher.service: BoxFetcher,
    NetflixFetcher.service: NetflixFetcher,
    PrimeVideoFetcher.service: PrimeVideoFetcher,
    YouTubeFetcher.service: YouTubeFetcher,
    InstagramFetcher.service: InstagramFetcher,
    TikTokFetcher.service: TikTokFetcher,
    AdobeUpdatesFetcher.service: AdobeUpdatesFetcher,
}


@dataclass
class ServiceResult:
    service: str
    status: str
    entries: int = 0
    error: str | None = None


def configure_logging(log_dir: Path) -> Path:
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"fetch-{date.today().isoformat()}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file, encoding="utf-8"),
        ],
        force=True,
    )
    return log_file


def load_schema() -> dict[str, Any]:
    with SCHEMA_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")


def comparable(data: dict[str, Any] | None) -> dict[str, Any] | None:
    if data is None:
        return None

    normalized = dict(data)
    normalized.pop("updated_at", None)
    normalized["entries"] = sorted(
        normalized.get("entries", []),
        key=lambda entry: (entry.get("type", ""), entry.get("value", ""), entry.get("action", "")),
    )
    return normalized


def has_changed(current: dict[str, Any], previous: dict[str, Any] | None) -> bool:
    return comparable(current) != comparable(previous)


def run_service(service: str, validator: Draft202012Validator) -> ServiceResult:
    logger = logging.getLogger(__name__)
    fetcher = FETCHER_CLASSES[service]()

    try:
        logger.info("[%s] fetching", service)
        output = fetcher.run()
        validator.validate(output)

        latest_path = LATEST_DIR / f"{service}.json"
        previous = load_json(latest_path)

        if not has_changed(output, previous):
            logger.info("[%s] no changes (%s entries)", service, len(output["entries"]))
            return ServiceResult(service=service, status="no_change", entries=len(output["entries"]))

        history_path = HISTORY_DIR / service / f"{service}-{date.today().isoformat()}.json"
        save_json(latest_path, output)
        save_json(history_path, output)
        logger.info(
            "[%s] updated (%s entries): %s, %s",
            service,
            len(output["entries"]),
            latest_path.relative_to(ROOT_DIR),
            history_path.relative_to(ROOT_DIR),
        )
        return ServiceResult(service=service, status="updated", entries=len(output["entries"]))
    except Exception as exc:
        logger.exception("[%s] failed and skipped", service)
        return ServiceResult(service=service, status="error", error=str(exc))


def print_summary(results: list[ServiceResult]) -> None:
    logger = logging.getLogger(__name__)
    updated = [result.service for result in results if result.status == "updated"]
    unchanged = [result.service for result in results if result.status == "no_change"]
    errors = [result for result in results if result.status == "error"]

    logger.info("summary: updated=%s no_change=%s errors=%s", len(updated), len(unchanged), len(errors))

    if updated:
        logger.info("updated services: %s", ", ".join(updated))
    if unchanged:
        logger.info("unchanged services: %s", ", ".join(unchanged))
    if errors:
        logger.info("failed services: %s", ", ".join(result.service for result in errors))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch and normalize PAC IP lists.")
    parser.add_argument(
        "--service",
        action="append",
        choices=sorted(FETCHER_CLASSES),
        help="Run only the selected service. Can be specified multiple times.",
    )
    parser.add_argument(
        "--log-dir",
        default=os.environ.get("PAC_IP_MANAGER_LOG_DIR", str(ROOT_DIR / "logs")),
        help="Directory for daily log files.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    log_file = configure_logging(Path(args.log_dir))
    logger = logging.getLogger(__name__)
    logger.info("log file: %s", log_file)

    services = args.service or list(FETCHER_CLASSES)
    schema = load_schema()
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    results = [run_service(service, validator) for service in services]
    print_summary(results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
