"""Offline tests: every HTTP call is served by an httpx.MockTransport.

Fixture payloads are small synthetic samples that copy each provider's response
format; the numbers are not real observations. Live checks are in test_live.py.
"""

import httpx
import pytest

from altassets.connectors.base import PoliteClient


@pytest.fixture
def make_client(tmp_path):
    def _make(routes: dict[str, tuple[int, bytes | str]], robots: str = "User-agent: *\nAllow: /\n"):
        seen = []

        def handler(request: httpx.Request):
            seen.append(request)
            if request.url.path == "/robots.txt":
                return httpx.Response(200, text=robots)
            for prefix, (status, body) in routes.items():
                if str(request.url).startswith(prefix):
                    return httpx.Response(status, content=body if isinstance(body, bytes) else body.encode())
            return httpx.Response(404)

        client = PoliteClient(min_interval=0, cache_dir=tmp_path / "cache",
                              transport=httpx.MockTransport(handler))
        client.seen = seen
        return client

    return _make
