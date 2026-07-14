"""Optional MuseHub read adapter (§HGD.4.1) — never sole baseline (K7)."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import quote

from tools.hosted_dashboard.http_client import UpstreamClient, UpstreamError


@dataclass(frozen=True)
class MuseFileContent:
    """MuseHub-fetched file bytes."""

    path: str
    text: str
    raw: bytes
    sha256: str
    ref: str
    source_id: str = "musehub_read"


class MuseHubReadAdapter:
    """Optional deepen — requires configured finite host allowlist entries."""

    def __init__(self, client: UpstreamClient, *, base_url: str) -> None:
        self._client = client
        self._base = base_url.rstrip("/")

    def fetch_file(self, owner: str, repo: str, path: str, *, ref: str) -> MuseFileContent:
        url = f"{self._base}/repos/{quote(owner)}/{quote(repo)}/contents/{quote(path, safe='/')}?ref={quote(ref)}"
        raw = self._client.get_bytes(url, accept="application/octet-stream")
        from tools.hosted_dashboard.cache import EphemeralByteCache

        digest = EphemeralByteCache.digest(raw)
        return MuseFileContent(
            path=path,
            text=raw.decode("utf-8", errors="replace"),
            raw=raw,
            sha256=digest,
            ref=ref,
        )


def musehub_baseline_impossible(*, github_contents_enabled: bool) -> bool:
    """K7: MuseHub-only baseline is impossible — github_contents must remain enabled."""
    return not github_contents_enabled
