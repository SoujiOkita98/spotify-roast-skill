#!/usr/bin/env python3
"""Extract tracks from a public Spotify playlist URL without user OAuth.

Method:
1. Fetch https://open.spotify.com/embed/playlist/<id>
2. Parse Next.js __NEXT_DATA__ JSON.
3. Use embedded anonymous session.accessToken to call Spotify Web API pages.
4. Respect 429 Retry-After.

This works for public playlists when Spotify exposes an embed token. It is not a
private-playlist or account-auth exporter.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
from html import unescape
from typing import Any

import requests

PLAYLIST_RE = re.compile(r"(?:playlist/|spotify:playlist:)([A-Za-z0-9]+)")


def playlist_id(value: str) -> str:
    m = PLAYLIST_RE.search(value)
    if m:
        return m.group(1)
    if re.fullmatch(r"[A-Za-z0-9]+", value):
        return value
    raise SystemExit(f"Could not parse Spotify playlist id from: {value}")


def fetch_embed(pid: str) -> dict[str, Any]:
    url = f"https://open.spotify.com/embed/playlist/{pid}"
    headers = {"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US,en;q=0.9"}
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', r.text)
    if not m:
        raise RuntimeError("Could not find __NEXT_DATA__ in Spotify embed page")
    return json.loads(unescape(m.group(1)))


def get_nested(obj: dict[str, Any], path: list[str]) -> Any:
    cur: Any = obj
    for key in path:
        cur = cur[key]
    return cur


def api_get(url: str, token: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    headers = {"Authorization": f"Bearer {token}", "User-Agent": "Mozilla/5.0", "Accept": "application/json"}
    for _ in range(6):
        r = requests.get(url, headers=headers, params=params, timeout=30)
        if r.status_code == 429:
            time.sleep(int(r.headers.get("retry-after", "5")) + 1)
            continue
        r.raise_for_status()
        return r.json()
    raise RuntimeError("Spotify API kept returning 429 after retries")


def extract(pid: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    next_data = fetch_embed(pid)
    state = get_nested(next_data, ["props", "pageProps", "state"])
    entity = get_nested(state, ["data", "entity"])
    token = get_nested(state, ["settings", "session", "accessToken"])

    # The embed usually contains only the first 100. Use the anonymous embed token
    # to page through the playlist API and get the true total.
    base = f"https://api.spotify.com/v1/playlists/{pid}/tracks"
    # Keep fields conservative: Spotify can return 500 on some malformed/deep
    # field selectors (e.g. external_urls(spotify)); fetch external_urls as a map.
    fields = "total,next,items(track(name,artists(name),album(name),duration_ms,external_urls,uri))"
    tracks: list[dict[str, Any]] = []
    offset = 0
    total = None
    while total is None or offset < total:
        page = api_get(base, token, {"limit": 100, "offset": offset, "fields": fields})
        total = page.get("total", 0)
        for item in page.get("items", []):
            track = item.get("track") or {}
            if not track.get("name"):
                continue
            tracks.append(
                {
                    "name": track.get("name", ""),
                    "artists": ", ".join(a.get("name", "") for a in track.get("artists", [])),
                    "album": (track.get("album") or {}).get("name", ""),
                    "duration_ms": track.get("duration_ms"),
                    "url": (track.get("external_urls") or {}).get("spotify", ""),
                    "uri": track.get("uri", ""),
                }
            )
        offset += 100
    meta = {"id": pid, "title": entity.get("title") or entity.get("name"), "owner": entity.get("subtitle"), "total": total}
    return meta, tracks


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("playlist")
    ap.add_argument("--format", choices=["text", "json", "csv"], default="text")
    args = ap.parse_args()
    meta, tracks = extract(playlist_id(args.playlist))

    if args.format == "json":
        print(json.dumps({"playlist": meta, "tracks": tracks}, ensure_ascii=False, indent=2))
    elif args.format == "csv":
        w = csv.DictWriter(sys.stdout, fieldnames=["index", "name", "artists", "album", "duration_ms", "url", "uri"])
        w.writeheader()
        for i, t in enumerate(tracks, 1):
            w.writerow({"index": i, **t})
    else:
        print(f"{meta['title']} — Spotify playlist tracks ({len(tracks)})")
        print(f"https://open.spotify.com/playlist/{meta['id']}")
        print()
        for i, t in enumerate(tracks, 1):
            print(f"{i}. {t['name']} — {t['artists']}")


if __name__ == "__main__":
    main()
