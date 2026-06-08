from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import ValidationError


ROOT_DIR = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT_DIR / "schema" / "ip-list.schema.json"


@pytest.fixture
def validator() -> Draft202012Validator:
    with SCHEMA_PATH.open("r", encoding="utf-8") as file:
        schema = json.load(file)
    return Draft202012Validator(schema, format_checker=FormatChecker())


@pytest.mark.parametrize(
    "sample",
    [
        {
            "service": "microsoft365",
            "updated_at": "2026-06-06",
            "schema_version": "1",
            "entries": [
                {"type": "url", "value": "*.office365.com", "action": "DIRECT"},
                {"type": "ip_range", "value": "13.107.6.152/31", "action": "DIRECT"},
            ],
        },
        {
            "service": "zoom",
            "updated_at": "2026-06-06",
            "schema_version": "1",
            "entries": [
                {"type": "ip_range", "value": "3.7.35.0/25", "action": "DIRECT"},
            ],
        },
        {
            "service": "microsoft_teams",
            "updated_at": "2026-06-06",
            "schema_version": "1",
            "entries": [
                {"type": "url", "value": "*.teams.microsoft.com", "action": "DIRECT"},
                {"type": "ip_range", "value": "52.112.0.0/14", "action": "DIRECT"},
            ],
        },
        {
            "service": "webex_meetings",
            "updated_at": "2026-06-06",
            "schema_version": "1",
            "entries": [
                {"type": "url", "value": "*.webex.com", "action": "DIRECT"},
                {"type": "ip_range", "value": "64.68.96.0/19", "action": "DIRECT"},
            ],
        },
        {
            "service": "windows_update",
            "updated_at": "2026-06-06",
            "schema_version": "1",
            "entries": [
                {"type": "url", "value": "*.windowsupdate.com", "action": "DIRECT"},
                {"type": "fqdn", "value": "adl.windows.com", "action": "DIRECT"},
            ],
        },
        {
            "service": "apple",
            "updated_at": "2026-06-06",
            "schema_version": "1",
            "entries": [
                {"type": "fqdn", "value": "apple.com", "action": "DIRECT"},
                {"type": "url", "value": "*.icloud.com", "action": "DIRECT"},
            ],
        },
        {
            "service": "google",
            "updated_at": "2026-06-06",
            "schema_version": "1",
            "entries": [
                {"type": "ip_range", "value": "8.8.8.0/24", "action": "DIRECT"},
            ],
        },
        {
            "service": "google_meet",
            "updated_at": "2026-06-06",
            "schema_version": "1",
            "entries": [
                {"type": "fqdn", "value": "meet.google.com", "action": "DIRECT"},
                {"type": "ip_range", "value": "74.125.250.0/24", "action": "DIRECT"},
            ],
        },
        {
            "service": "box",
            "updated_at": "2026-06-06",
            "schema_version": "1",
            "entries": [
                {"type": "url", "value": "*.box.com", "action": "DIRECT"},
                {"type": "ip_range", "value": "216.198.0.0/18", "action": "DIRECT"},
            ],
        },
        {
            "service": "netflix",
            "updated_at": "2026-06-06",
            "schema_version": "1",
            "entries": [
                {"type": "fqdn", "value": "netflix.com", "action": "DIRECT"},
                {"type": "url", "value": "*.nflxvideo.net", "action": "DIRECT"},
            ],
        },
        {
            "service": "prime_video",
            "updated_at": "2026-06-06",
            "schema_version": "1",
            "entries": [
                {"type": "fqdn", "value": "primevideo.com", "action": "DIRECT"},
                {"type": "url", "value": "*.aiv-cdn.net", "action": "DIRECT"},
            ],
        },
        {
            "service": "youtube",
            "updated_at": "2026-06-06",
            "schema_version": "1",
            "entries": [
                {"type": "fqdn", "value": "youtube.com", "action": "DIRECT"},
                {"type": "url", "value": "*.googlevideo.com", "action": "DIRECT"},
            ],
        },
        {
            "service": "instagram",
            "updated_at": "2026-06-06",
            "schema_version": "1",
            "entries": [
                {"type": "fqdn", "value": "instagram.com", "action": "DIRECT"},
                {"type": "url", "value": "*.cdninstagram.com", "action": "DIRECT"},
            ],
        },
        {
            "service": "tiktok",
            "updated_at": "2026-06-06",
            "schema_version": "1",
            "entries": [
                {"type": "fqdn", "value": "tiktok.com", "action": "DIRECT"},
                {"type": "url", "value": "*.tiktokcdn.com", "action": "DIRECT"},
            ],
        },
        {
            "service": "adobe_updates",
            "updated_at": "2026-06-06",
            "schema_version": "1",
            "entries": [
                {"type": "fqdn", "value": "ccmdl.adobe.com", "action": "DIRECT"},
                {"type": "url", "value": "http://armdl.adobe.com/", "action": "DIRECT"},
            ],
        },
    ],
)
def test_samples_validate_against_schema(
    validator: Draft202012Validator,
    sample: dict[str, object],
) -> None:
    validator.validate(sample)


def test_schema_rejects_non_direct_action(validator: Draft202012Validator) -> None:
    sample = {
        "service": "zoom",
        "updated_at": "2026-06-06",
        "schema_version": "1",
        "entries": [
            {"type": "ip_range", "value": "3.7.35.0/25", "action": "PROXY"},
        ],
    }

    with pytest.raises(ValidationError):
        validator.validate(sample)
