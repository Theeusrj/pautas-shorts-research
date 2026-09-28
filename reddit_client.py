"""Minimal, read-only Reddit research client.

This component is intentionally dormant until the operator has written approval
and official OAuth credentials from Reddit. It never stores credentials, users,
comments, or post bodies. The caller must provide credentials from a local,
uncommitted configuration source.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterable

import requests


ALLOWED_SUBREDDITS = ("volcanoes", "geology", "archaeology", "space")
MAX_POSTS_PER_SUBREDDIT = 25
MAX_SUBREDDITS_PER_RUN = len(ALLOWED_SUBREDDITS)
RECENT_DAYS = 14
USER_AGENT = "windows:PautasShortsResearch:0.1 (official OAuth access)"


class RedditAccessError(RuntimeError):
    """Raised when official Reddit access cannot be used safely."""


@dataclass(frozen=True)
class TrendingPost:
    """Only aggregated metadata needed for editorial trend screening."""

    subreddit: str
    title: str
    permalink: str
    score: int
    comment_count: int
    created_at: str

    def to_dict(self) -> dict[str, str | int]:
        return asdict(self)


def obtain_app_token(client_id: str, client_secret: str) -> str:
    """Request an OAuth token from Reddit using approved app credentials."""
    if not client_id.strip() or not client_secret.strip():
        raise RedditAccessError("Credenciais OAuth do Reddit não configuradas.")
    response = requests.post(
        "https://www.reddit.com/api/v1/access_token",
        auth=(client_id, client_secret),
        data={"grant_type": "client_credentials"},
        headers={"User-Agent": USER_AGENT},
        timeout=20,
    )
    if response.status_code != 200:
        raise RedditAccessError(
            f"OAuth do Reddit não foi aceito (HTTP {response.status_code})."
        )
    token = response.json().get("access_token")
    if not isinstance(token, str) or not token:
        raise RedditAccessError("O Reddit não devolveu um token de acesso.")
    return token


def fetch_trending_posts(
    access_token: str, subreddits: Iterable[str] = ALLOWED_SUBREDDITS
) -> list[TrendingPost]:
    """Read a bounded Top/week listing from approved, public communities.

    The function makes at most one request per allowed community and returns
    titles plus aggregate popularity metadata only. It never fetches comments
    or user profiles.
    """
    requested = tuple(dict.fromkeys(subreddits))
    if not requested:
        return []
    if len(requested) > MAX_SUBREDDITS_PER_RUN:
        raise RedditAccessError("Quantidade de comunidades acima do limite local.")
    if any(name not in ALLOWED_SUBREDDITS for name in requested):
        raise RedditAccessError("Foi solicitada uma comunidade não autorizada.")

    cutoff = datetime.now(timezone.utc) - timedelta(days=RECENT_DAYS)
    headers = {
        "Authorization": f"Bearer {access_token}",
        "User-Agent": USER_AGENT,
    }
    posts: list[TrendingPost] = []

    for subreddit in requested:
        response = requests.get(
            f"https://oauth.reddit.com/r/{subreddit}/top",
            params={"t": "week", "limit": MAX_POSTS_PER_SUBREDDIT, "raw_json": 1},
            headers=headers,
            timeout=20,
        )
        if response.status_code != 200:
            raise RedditAccessError(
                f"Não foi possível consultar r/{subreddit} (HTTP {response.status_code})."
            )
        for child in response.json().get("data", {}).get("children", []):
            data = child.get("data", {})
            created_at = datetime.fromtimestamp(
                float(data.get("created_utc", 0)), tz=timezone.utc
            )
            if data.get("over_18") or created_at < cutoff:
                continue
            title = str(data.get("title", "")).strip()
            permalink = str(data.get("permalink", "")).strip()
            if title and permalink:
                posts.append(
                    TrendingPost(
                        subreddit=subreddit,
                        title=title,
                        permalink=f"https://www.reddit.com{permalink}",
                        score=int(data.get("score", 0)),
                        comment_count=int(data.get("num_comments", 0)),
                        created_at=created_at.isoformat(),
                    )
                )
    return posts

