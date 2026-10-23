"""Polite HTTP base for every connector.

Every request goes through `PoliteClient`, which:
  * identifies us with a User-Agent that carries a contact address (ALTASSETS_CONTACT),
  * checks robots.txt for the host before fetching and refuses disallowed paths,
  * enforces a per-host minimum interval between requests,
  * caches raw responses under data/raw so re-runs do not re-hit the source.

Robots.txt is a floor, not a licence: each source's terms of use are recorded in
sources/sources.yaml and a connector should only be written for sources whose terms
allow automated access.
"""

from __future__ import annotations

import hashlib
import os
import time
import urllib.robotparser
from abc import ABC, abstractmethod
from pathlib import Path
from urllib.parse import urlsplit

import httpx
import pandas as pd

from altassets.data.schema import SeriesMeta

DEFAULT_CONTACT = "set-ALTASSETS_CONTACT@example.invalid"


class RobotsDisallowed(RuntimeError):
    pass


class PoliteClient:
    def __init__(
        self,
        min_interval: float = 1.0,
        cache_dir: str | Path | None = "data/raw/http",
        respect_robots: bool = True,
        transport: httpx.BaseTransport | None = None,
        timeout: float = 30.0,
    ):
        contact = os.environ.get("ALTASSETS_CONTACT", DEFAULT_CONTACT)
        self.user_agent = f"altassets-research/0.1 (+{contact})"
        self.min_interval = min_interval
        self.cache_dir = Path(cache_dir) if cache_dir else None
        self.respect_robots = respect_robots
        self._robots: dict[str, urllib.robotparser.RobotFileParser] = {}
        self._last: dict[str, float] = {}
        self._http = httpx.Client(
            headers={"User-Agent": self.user_agent},
            timeout=timeout,
            follow_redirects=True,
            transport=transport,
        )

    def _throttle(self, host: str) -> None:
        wait = self.min_interval - (time.monotonic() - self._last.get(host, 0.0))
        if wait > 0:
            time.sleep(wait)
        self._last[host] = time.monotonic()

    def allowed(self, url: str) -> bool:
        parts = urlsplit(url)
        base = f"{parts.scheme}://{parts.netloc}"
        rp = self._robots.get(base)
        if rp is None:
            rp = urllib.robotparser.RobotFileParser()
            r = self._http.get(f"{base}/robots.txt")
            if r.status_code == 200:
                rp.parse(r.text.splitlines())
            elif r.status_code in (401, 403):
                rp.disallow_all = True
            else:  # 404 or similar: no robots policy published
                rp.allow_all = True
            self._robots[base] = rp
        return rp.can_fetch(self.user_agent, url)

    def get(self, url: str, params: dict | None = None, use_cache: bool = True) -> bytes:
        full = str(httpx.URL(url, params=params))
        key = hashlib.sha256(full.encode()).hexdigest()[:32]
        cached = self.cache_dir / key if self.cache_dir else None
        if use_cache and cached and cached.exists():
            return cached.read_bytes()
        if self.respect_robots and not self.allowed(full):
            raise RobotsDisallowed(full)
        self._throttle(urlsplit(full).netloc)
        r = self._http.get(full)
        r.raise_for_status()
        if cached:
            cached.parent.mkdir(parents=True, exist_ok=True)
            cached.write_bytes(r.content)
        return r.content


class Connector(ABC):
    """A source of time series. Subclasses implement `fetch` returning canonical rows."""

    source: str = ""
    min_interval: float = 1.0

    def __init__(self, client: PoliteClient | None = None):
        self.client = client or PoliteClient(min_interval=self.min_interval)

    @abstractmethod
    def fetch(
        self, series_id: str, start: str | None = None, end: str | None = None
    ) -> tuple[pd.DataFrame, SeriesMeta]:
        """Return (frame in canonical schema, metadata)."""
