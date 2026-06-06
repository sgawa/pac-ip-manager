from __future__ import annotations

from datetime import date

from fetchers.apple import AppleFetcher
from fetchers.box import BoxFetcher
from fetchers.google import GoogleFetcher
from fetchers.google_meet import GoogleMeetFetcher
from fetchers.microsoft365 import Microsoft365Fetcher
from fetchers.microsoft_teams import MicrosoftTeamsFetcher
from fetchers.webex_meetings import WebexMeetingsFetcher
from fetchers.windows_update import WindowsUpdateFetcher
from fetchers.zoom import ZoomFetcher
from fetchers.zoom_cloud_meetings import ZoomCloudMeetingsFetcher


def assert_common_entries(entries: list[dict[str, str]]) -> None:
    assert entries
    for entry in entries:
        assert set(entry) == {"type", "value", "action"}
        assert entry["type"] in {"url", "ip_range", "fqdn"}
        assert entry["value"]
        assert entry["action"] == "DIRECT"


def test_microsoft365_normalize_urls_and_ips() -> None:
    raw = [
        {
            "urls": ["*.office365.com", "*.office365.com", "login.microsoftonline.com"],
            "ips": ["13.107.6.152/31"],
        },
        {
            "urls": ["*.sharepoint.com"],
            "ips": ["40.96.0.0/13"],
        },
    ]

    entries = Microsoft365Fetcher().normalize(raw)

    assert entries == [
        {"type": "url", "value": "*.office365.com", "action": "DIRECT"},
        {"type": "url", "value": "login.microsoftonline.com", "action": "DIRECT"},
        {"type": "ip_range", "value": "13.107.6.152/31", "action": "DIRECT"},
        {"type": "url", "value": "*.sharepoint.com", "action": "DIRECT"},
        {"type": "ip_range", "value": "40.96.0.0/13", "action": "DIRECT"},
    ]
    assert_common_entries(entries)


def test_zoom_normalize_text_lines() -> None:
    raw = """
    # Zoom IP ranges
    3.7.35.0/25

    3.21.137.128/25
    3.7.35.0/25
    """

    entries = ZoomFetcher().normalize(raw)

    assert entries == [
        {"type": "ip_range", "value": "3.7.35.0/25", "action": "DIRECT"},
        {"type": "ip_range", "value": "3.21.137.128/25", "action": "DIRECT"},
    ]
    assert_common_entries(entries)


def test_zoom_cloud_meetings_uses_zoom_ip_ranges() -> None:
    entries = ZoomCloudMeetingsFetcher().normalize("3.7.35.0/25\n")

    assert entries == [
        {"type": "ip_range", "value": "3.7.35.0/25", "action": "DIRECT"},
    ]
    assert_common_entries(entries)


def test_microsoft_teams_normalize_filters_teams_records() -> None:
    raw = [
        {
            "serviceAreaDisplayName": "Microsoft Teams",
            "urls": ["*.teams.microsoft.com", "teams.microsoft.com"],
            "ips": ["52.112.0.0/14"],
        },
        {
            "serviceAreaDisplayName": "Exchange Online",
            "urls": ["outlook.office.com"],
            "ips": ["40.96.0.0/13"],
        },
    ]

    entries = MicrosoftTeamsFetcher().normalize(raw)

    assert entries == [
        {"type": "url", "value": "*.teams.microsoft.com", "action": "DIRECT"},
        {"type": "url", "value": "teams.microsoft.com", "action": "DIRECT"},
        {"type": "ip_range", "value": "52.112.0.0/14", "action": "DIRECT"},
    ]
    assert_common_entries(entries)


def test_webex_meetings_normalize_html() -> None:
    raw = """
    <html><body>
      <ul><li>64.68.96.0/19 (CIDR)</li><li>2402:2500::/32</li></ul>
      <div class="panel">
        <h4>Domains that need to be allowed</h4>
        <table>
          <tr><td>Desktop</td><td>*.webex.com<br>*.wbx2.com</td></tr>
          <tr><td>Certificate</td><td>*.digicert.com</td></tr>
        </table>
      </div>
    </body></html>
    """

    entries = WebexMeetingsFetcher().normalize(raw)

    assert {"type": "ip_range", "value": "64.68.96.0/19", "action": "DIRECT"} in entries
    assert {"type": "ip_range", "value": "2402:2500::/32", "action": "DIRECT"} in entries
    assert {"type": "url", "value": "*.webex.com", "action": "DIRECT"} in entries
    assert {"type": "url", "value": "*.wbx2.com", "action": "DIRECT"} in entries
    assert {"type": "url", "value": "*.digicert.com", "action": "DIRECT"} in entries
    assert_common_entries(entries)


def test_windows_update_normalize_windows_update_section_only() -> None:
    raw = """
    <table>
      <tr><td>Windows Update</td><td></td><td></td><td>Learn more</td></tr>
      <tr><td></td><td>Downloads</td><td>HTTPS</td><td>*.windowsupdate.com</td></tr>
      <tr><td></td><td>API</td><td>HTTPS</td><td>*.api.cdp.microsoft.com</td></tr>
      <tr><td>Xbox Live</td><td></td><td>HTTPS</td><td>da.xboxservices.com</td></tr>
    </table>
    """

    entries = WindowsUpdateFetcher().normalize(raw)

    assert entries == [
        {"type": "url", "value": "*.windowsupdate.com", "action": "DIRECT"},
        {"type": "url", "value": "*.api.cdp.microsoft.com", "action": "DIRECT"},
    ]
    assert_common_entries(entries)


def test_google_meet_normalize_meet_network_section() -> None:
    raw = """
    <html><body>
      <h4>Step 2</h4>
      <p><b>Domains for static resources</b></p>
      <ul><li>meetings.clients6.google.com</li><li>meet.google.com</li></ul>
      <p><b>Domains for user feedback &amp; event log uploads</b></p>
      <ul><li>https://www.google.com/tools/feedback</li></ul>
      <h4>Step 3: Allow access to Google IP address ranges (for audio and video)</h4>
      <ul><li>IPv4: 74.125.250.0/24</li><li>SNI: workspace.turns.goog</li></ul>
      <h4>Step 4: Review bandwidth requirements</h4>
      <p>docs.google.com should not be parsed here.</p>
    </body></html>
    """

    entries = GoogleMeetFetcher().normalize(raw)

    assert {"type": "fqdn", "value": "meetings.clients6.google.com", "action": "DIRECT"} in entries
    assert {"type": "fqdn", "value": "meet.google.com", "action": "DIRECT"} in entries
    assert {"type": "url", "value": "https://www.google.com/tools/feedback", "action": "DIRECT"} in entries
    assert {"type": "ip_range", "value": "74.125.250.0/24", "action": "DIRECT"} in entries
    assert {"type": "fqdn", "value": "workspace.turns.goog", "action": "DIRECT"} in entries
    assert {"type": "fqdn", "value": "docs.google.com", "action": "DIRECT"} not in entries
    assert_common_entries(entries)


def test_box_normalize_firewall_html_and_ips_json() -> None:
    raw = {
        "firewall_html": """
        <pre>
        *.box.com
        api.box.com
        cdn01.boxcdn.net - cdn20.boxcdn.net
        proxy.pac
        17.0.0.0/8
        </pre>
        """,
        "ips": {"ips": {"ingress": {"all": ["216.198.0.0/18"]}}},
    }

    entries = BoxFetcher().normalize(raw)

    assert {"type": "url", "value": "*.box.com", "action": "DIRECT"} in entries
    assert {"type": "fqdn", "value": "api.box.com", "action": "DIRECT"} in entries
    assert {"type": "fqdn", "value": "cdn01.boxcdn.net", "action": "DIRECT"} in entries
    assert {"type": "fqdn", "value": "cdn20.boxcdn.net", "action": "DIRECT"} in entries
    assert {"type": "fqdn", "value": "proxy.pac", "action": "DIRECT"} not in entries
    assert {"type": "ip_range", "value": "17.0.0.0/8", "action": "DIRECT"} in entries
    assert {"type": "ip_range", "value": "216.198.0.0/18", "action": "DIRECT"} in entries
    assert_common_entries(entries)


def test_apple_normalize_hostnames_from_html() -> None:
    raw = """
    <html>
      <body>
        <main>
          <table>
            <tr><td>apple.com</td></tr>
            <tr><td>*.icloud.com</td></tr>
            <tr><td>gdmf.apple.com</td></tr>
          </table>
        </main>
      </body>
    </html>
    """

    entries = AppleFetcher().normalize(raw)

    assert entries == [
        {"type": "fqdn", "value": "apple.com", "action": "DIRECT"},
        {"type": "url", "value": "*.icloud.com", "action": "DIRECT"},
        {"type": "fqdn", "value": "gdmf.apple.com", "action": "DIRECT"},
    ]
    assert_common_entries(entries)


def test_google_normalize_ipv4_prefixes_only() -> None:
    raw = {
        "syncToken": "sample",
        "prefixes": [
            {"ipv4Prefix": "8.8.8.0/24"},
            {"ipv6Prefix": "2001:4860:4860::/48"},
            {"ipv4Prefix": "8.8.4.0/24"},
        ],
    }

    entries = GoogleFetcher().normalize(raw)

    assert entries == [
        {"type": "ip_range", "value": "8.8.8.0/24", "action": "DIRECT"},
        {"type": "ip_range", "value": "8.8.4.0/24", "action": "DIRECT"},
    ]
    assert_common_entries(entries)


def test_build_output_uses_unified_format() -> None:
    fetcher = ZoomFetcher()
    entries = fetcher.normalize("198.51.100.0/24")

    output = fetcher.build_output(entries)

    assert output == {
        "service": "zoom",
        "updated_at": date.today().isoformat(),
        "schema_version": "1",
        "entries": [{"type": "ip_range", "value": "198.51.100.0/24", "action": "DIRECT"}],
    }
