from __future__ import annotations

from fetchers.zoom import ZoomFetcher


class ZoomCloudMeetingsFetcher(ZoomFetcher):
    service = "zoom_cloud_meetings"


if __name__ == "__main__":
    ZoomCloudMeetingsFetcher.print_cli_output()
