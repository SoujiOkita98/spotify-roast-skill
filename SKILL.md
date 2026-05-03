---
name: spotify-playlist-roast
description: Extract any public Spotify playlist into JSON, CSV, or text without OAuth — then optionally generate a doodle-style "AI judgment" HTML page (bilingual EN/中, screenshot-friendly, exports to PNG via html2canvas). Use when the user gives an open.spotify.com playlist URL and asks to extract / list / export tracks, judge or roast a playlist, build a shareable verdict page, or feed playlist data to an AI for music-taste analysis.
---

# Spotify Playlist Roast

This skill does two things:

1. **Extract** a public Spotify playlist into JSON / CSV / plain text, with no Spotify OAuth required.
2. **Roast** the playlist into a doodle-style HTML page that's screenshot-friendly and exports to PNG.

Both stages are independent — extraction produces a portable JSON the user can use however they want (talk to AI about their music taste, audit duplicates, pick songs for a video, etc.). The roast is one specific recipe on top of it.

---

## 1. Extract

Use the bundled script. No installation beyond `requests`.

```bash
python3 <skill-dir>/scripts/extract_spotify_playlist.py '<spotify-playlist-url-or-id>' --format text
python3 <skill-dir>/scripts/extract_spotify_playlist.py '<spotify-playlist-url-or-id>' --format json > playlist.json
python3 <skill-dir>/scripts/extract_spotify_playlist.py '<spotify-playlist-url-or-id>' --format csv > playlist.csv
```

### Method

1. Parse the playlist id from the URL.
2. Fetch `https://open.spotify.com/embed/playlist/<id>` (the lightweight embed page, not the JS-heavy main playlist page).
3. Parse the Next.js `__NEXT_DATA__` JSON blob.
4. Read:
   - `props.pageProps.state.data.entity` for playlist metadata.
   - `props.pageProps.state.settings.session.accessToken` for the short-lived **anonymous embed bearer token**.
5. Call:

   ```text
   GET https://api.spotify.com/v1/playlists/<id>/tracks?limit=100&offset=0&fields=total,next,items(track(name,artists(name),album(name),duration_ms,external_urls,uri))
   Authorization: Bearer <embed_access_token>
   ```

6. Paginate by `offset += 100` until all tracks are fetched.
7. Respect `429 Retry-After`; do not tight-loop.

### Caveats

- Works only for **public** playlists that Spotify allows in embeds.
- The bearer token is a temporary anonymous embed token, not the user's Spotify OAuth token.
- Private playlists, Liked Songs, and account-specific exports require proper Spotify OAuth.
- **No audio features** (tempo / energy / valence / danceability) — those require OAuth. Mood matching from name + artist alone is good enough for most use cases.
- If the API returns 500, simplify the `fields` selector. In testing, `external_urls(spotify)` caused 500; requesting `external_urls` as a map worked.

### Output guidance

- For chat: return playlist title, total count, then numbered `Song — Artist` lines.
- For spreadsheet review: save CSV and open it with `open <file.csv>` when the user asks to see it on screen.
- For later processing or feeding to an AI: prefer JSON because it preserves album, duration, URL, and URI.

---

## 2. Roast (the judgment page)

If the user wants the playlist judged / roasted / turned into a shareable verdict page, follow the recipe at [`recipes/judgment-page.md`](./recipes/judgment-page.md). It contains:

- The full **design system** (palette, fonts, card rotations, doodle elements)
- All the **content blocks** (verdict, taxonomy, picks, roast paragraphs, energy arc, quote)
- **Tone options** (gentle roast / astrology / deadpan critic / wholesome therapist)
- **Bilingual** EN/中 implementation pattern
- **PNG export** via html2canvas, with html2canvas-specific gotchas pre-handled

Output is a single self-contained `judgment.html` file the user can open in a browser, toggle EN/中, and click **Save as PNG** to share.

The canonical example is at [`examples/life-sucks/`](./examples/life-sucks/).

---

## 3. Other things to do with the JSON

If the user has a playlist JSON and wants to do more than roast it, suggest:

- **Find duplicates** — e.g., the same track appearing twice, or same song from different albums.
- **Genre / decade / language breakdown** — group artists by inferred genre, count tracks by decade or language, generate a profile.
- **Mood matching for video / vlog** — given a clip description, rank tracks by vibe match using name + artist (works surprisingly well for known artists).
- **Cross-playlist comparison** — diff two `playlist.json` files for overlap and unique tracks.
- **AI music-taste profile** — paste the JSON into a chat and ask the AI "what does this say about me?" or "recommend 10 songs that fit this taste."

These are all things the AI can do natively once it has the JSON. Don't write specialized scripts for them unless asked.

---

## When to use this skill

Trigger phrases include:
- "extract this Spotify playlist"
- "list the songs in <playlist URL>"
- "save this playlist as CSV / JSON"
- "roast my playlist" / "judge my music taste"
- "make a shareable page for my playlist"
- "give my AI my music taste"
- "pick songs from my playlist for [video / mood / scene]"
