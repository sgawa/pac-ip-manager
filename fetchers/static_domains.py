from __future__ import annotations

from fetchers.base import BaseFetcher
from fetchers.utils import domain_entry_type


class StaticDomainFetcher(BaseFetcher):
    domains: tuple[str, ...] = ()

    def fetch(self) -> list[str]:
        return list(self.domains)

    def normalize(self, raw: list[str]) -> list[dict[str, str]]:
        entries = [self.make_entry(domain_entry_type(domain), domain) for domain in raw]
        return self.dedupe_entries(entries)


class NetflixFetcher(StaticDomainFetcher):
    service = "netflix"
    domains = (
        "netflix.com",
        "*.netflix.com",
        "netflix.net",
        "*.netflix.net",
        "nflxvideo.net",
        "*.nflxvideo.net",
        "nflximg.net",
        "*.nflximg.net",
        "nflximg.com",
        "*.nflximg.com",
        "nflxso.net",
        "*.nflxso.net",
        "nflxext.com",
        "*.nflxext.com",
        "nflxsearch.net",
        "*.nflxsearch.net",
        "fast.com",
        "*.fast.com",
    )


class PrimeVideoFetcher(StaticDomainFetcher):
    service = "prime_video"
    domains = (
        "primevideo.com",
        "*.primevideo.com",
        "amazonvideo.com",
        "*.amazonvideo.com",
        "aiv-cdn.net",
        "*.aiv-cdn.net",
        "aiv-delivery.net",
        "*.aiv-delivery.net",
        "pv-cdn.net",
        "*.pv-cdn.net",
        "prime-video.amazon.dev",
        "*.prime-video.amazon.dev",
        "video.a2z.com",
        "*.video.a2z.com",
        "atv-ext.amazon.com",
        "atv-ps.amazon.com",
        "media-amazon.com",
        "*.media-amazon.com",
    )


class YouTubeFetcher(StaticDomainFetcher):
    service = "youtube"
    domains = (
        "youtube.com",
        "*.youtube.com",
        "youtu.be",
        "*.youtu.be",
        "youtube-nocookie.com",
        "*.youtube-nocookie.com",
        "youtubeeducation.com",
        "www.youtubeeducation.com",
        "googlevideo.com",
        "*.googlevideo.com",
        "ytimg.com",
        "*.ytimg.com",
        "i.ytimg.com",
        "s.ytimg.com",
        "yt3.ggpht.com",
        "youtubei.googleapis.com",
        "youtube.googleapis.com",
        "youtube-ui.l.google.com",
    )


class InstagramFetcher(StaticDomainFetcher):
    service = "instagram"
    domains = (
        "instagram.com",
        "*.instagram.com",
        "cdninstagram.com",
        "*.cdninstagram.com",
        "ig.me",
        "*.ig.me",
        "instagr.am",
        "*.instagr.am",
        "igsonar.com",
        "*.igsonar.com",
        "z-p42-chat-e2ee-ig.facebook.com",
        "z-p42-chat-e2ee-ig-fallback.facebook.com",
        "mqtt-ig-p4.facebook.com",
        "z-p3-instagram-portal.fb.com",
        "z-p42-instagram-portal.fb.com",
    )


class TikTokFetcher(StaticDomainFetcher):
    service = "tiktok"
    domains = (
        "tiktok.com",
        "*.tiktok.com",
        "tiktokv.com",
        "*.tiktokv.com",
        "tiktokv.us",
        "*.tiktokv.us",
        "tiktokcdn.com",
        "*.tiktokcdn.com",
        "tiktokcdn-us.com",
        "*.tiktokcdn-us.com",
        "tiktokcdn-eu.com",
        "*.tiktokcdn-eu.com",
        "tiktokw.us",
        "*.tiktokw.us",
        "ttdns2.com",
        "*.ttdns2.com",
        "byteoversea.com",
        "*.byteoversea.com",
        "bytefcdn-oversea.com",
        "*.bytefcdn-oversea.com",
        "ibytedtos.com",
        "*.ibytedtos.com",
        "ibyteimg.com",
        "*.ibyteimg.com",
        "muscdn.com",
        "*.muscdn.com",
        "musical.ly",
        "*.musical.ly",
        "snssdk.com",
        "*.snssdk.com",
        "ttwstatic.com",
        "*.ttwstatic.com",
    )
