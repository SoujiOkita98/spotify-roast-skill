# Example: "Life sucks"

A 168-track playlist by user `G`, named **"Life sucks"** — but loaded with explicitly anti-"life sucks" anthems (*Three Little Birds*, *What A Wonderful World*, *All You Need Is Love*, *Mr. Blue Sky*, *Joy to the World*, four Bob Marley tracks). The contradiction is the angle.

Files:
- [`playlist.json`](./playlist.json) — full extraction output
- [`judgment.html`](./judgment.html) — the AI-generated judgment page (bilingual EN/中, exports to PNG)

🌐 **Live:** https://soujiokita98.github.io/spotify-playlist-roast/examples/life-sucks/judgment.html

## How this example was generated

```bash
# 1. Extract
python3 scripts/extract_spotify_playlist.py \
  'https://open.spotify.com/playlist/0r6ZDp6DoLzGcsEyO5Xfy4' \
  --format json > examples/life-sucks/playlist.json

# 2. Roast
# An LLM read playlist.json + recipes/judgment-page.md
# and produced examples/life-sucks/judgment.html.
```

The verdict landed on **8.4 / 10**, with the title-vs-content irony as the central roast and the 14-track 草东没有派对 monolith as the playlist's true emotional center.
