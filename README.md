# Playlist Roast

> Extract any **public** Spotify or NetEase Cloud Music (网易云音乐) playlist into clean JSON, then let an AI judge your taste with a doodle-style page you can screenshot and share. Bilingual EN / 中.

🌐 **Live demo →** [Life Sucks — A Verdict (生活很烂 — 一份裁决)](https://soujiokita98.github.io/spotify-roast-skill/examples/life-sucks/judgment.html)

<p align="center">
  <a href="https://soujiokita98.github.io/spotify-roast-skill/examples/life-sucks/judgment.html">
    <img src="./examples/life-sucks/preview.png" alt="Preview of the Life Sucks playlist judgment page" width="640">
  </a>
</p>

Read this in [中文](./README.zh.md).

---

## Why this exists

I made this while editing a travel vlog. I wanted to ask an AI a simple question: *which songs from my actual playlist fit this scene?* But first I needed a lightweight way to give the AI my playlist as context.

Spotify has official APIs, but they all want OAuth and app setup. For a lightweight "I just want the song names" use case, that's overkill. This skill scrapes the public embed page for an anonymous token and uses it to page through the official API. **No login, no app registration, no client secret.** Works for any public playlist.

Once you have the JSON, the fun starts.

## What you can do with it

1. **🔥 Roast a playlist.** Generate a doodle-style judgment page (verdict, taxonomy, picks, roast paragraphs, emotional arc) that's screenshot-friendly and exports to PNG with one click. Bilingual toggle for EN/中. See the [live demo](https://soujiokita98.github.io/spotify-roast-skill/examples/life-sucks/judgment.html).
2. **🤖 Give your AI your music taste.** Drop the JSON into Claude / ChatGPT / your assistant of choice. Now it actually knows what you listen to and can have real conversations about it instead of guessing from your description.
3. **🎬 Pick songs for a video / vlog.** Describe the vibe ("sunset driving, melancholy") and ask your AI to pull matches from your real library, not from its imagination.
4. **🔍 Audit a playlist.** Find duplicates, count languages, see decade distribution, compare two playlists, find the album outliers — all things your AI can do once it has the JSON.

## Quick start

```bash
git clone https://github.com/SoujiOkita98/spotify-roast-skill.git
cd spotify-roast-skill
pip install requests
```

### Spotify

```bash
python3 scripts/extract_spotify_playlist.py \
  'https://open.spotify.com/playlist/0r6ZDp6DoLzGcsEyO5Xfy4' \
  --format json > my-playlist.json
```

### NetEase Cloud Music (网易云音乐)

```bash
python3 scripts/extract_netease_playlist.py \
  'https://music.163.com/playlist?id=2884035' \
  --format json > my-playlist.json
```

Output formats:

```bash
# Plain text — playlist title and numbered "Song — Artist" list
python3 scripts/extract_spotify_playlist.py '<url>' --format text

# JSON — full track metadata, ideal for feeding to an AI
python3 scripts/extract_spotify_playlist.py '<url>' --format json > playlist.json

# CSV — for spreadsheets
python3 scripts/extract_spotify_playlist.py '<url>' --format csv > playlist.csv
```

## Generating the roast page

The roast is **AI-generated** from the JSON. The recipe lives in [`recipes/judgment-page.md`](./recipes/judgment-page.md) — a design + content brief that any LLM can follow to produce a page in the same visual style as the demo.

The simplest way:

```
> here is my playlist JSON: [paste]
> read recipes/judgment-page.md and make me a judgment page like the demo
```

Or use this skill inside an [OpenClaw](https://github.com/openclaw)-compatible agent — the `SKILL.md` manifest wires extraction + recipe together.

## Feeding your playlist to an AI

The JSON output is the artifact. Once you have `playlist.json`, you can ask your AI things like:

- *"What's the vibe of this playlist? Be honest."*
- *"Find duplicates and tracks I should probably remove."*
- *"Pick 5 songs that fit a melancholy sunset driving scene."*
- *"What kind of person makes a playlist like this?"*
- *"Compare this with [other-playlist.json]. What overlaps? What's unique to each?"*
- *"Group these songs into mood buckets."*

This is the core idea: the JSON is **portable music-taste context**. Drop it into any conversation and your AI is suddenly a meaningful collaborator on anything music-related.

## How extraction works

1. Parse the playlist ID from the URL.
2. Fetch `https://open.spotify.com/embed/playlist/<id>` (the lightweight embed page, not the JS-heavy main page).
3. Parse the Next.js `__NEXT_DATA__` JSON blob.
4. Read `props.pageProps.state.settings.session.accessToken` — a short-lived **anonymous embed bearer token**.
5. Use that token to call `GET https://api.spotify.com/v1/playlists/<id>/tracks` and paginate by `offset += 100`.
6. Respect `429 Retry-After`.

The bearer token is what makes this work without OAuth. It's anonymous, ephemeral, and granted to the embed page for any public playlist Spotify allows in iframes.

### NetEase Cloud Music extraction

1. Parse the playlist ID from the URL (supports short links like `163cn.tv/XXX`).
2. Call `https://music.163.com/api/v6/playlist/detail` to get playlist metadata and all track IDs.
3. Fetch track details in batches of 100 via `https://music.163.com/api/song/detail`. The API silently returns 0 results for batches larger than ~300, so batch size must stay small.
4. No login or API key required — uses public endpoints that the web player itself uses.

## Limitations

- **Public playlists only.** Private playlists, Liked Songs, and account-specific exports require real Spotify OAuth.
- **No audio features.** Tempo / energy / valence / danceability all require OAuth. We only get track-level metadata: name, artists, album, duration, URLs.
- **Embed token can rotate.** Spotify can change the embed page structure or block anonymous access; the script will need maintenance if that happens.
- **Mood matching is name-based.** When asking your AI to pick songs by vibe, it's matching on track + artist names (which works surprisingly well for known artists), not actual audio features.

## Project structure

```
spotify-roast-skill/
├── README.md              # this file
├── README.zh.md           # Chinese version
├── LICENSE                # MIT
├── SKILL.md               # OpenClaw-style skill manifest
├── scripts/
│   ├── extract_spotify_playlist.py
│   └── extract_netease_playlist.py
├── recipes/
│   └── judgment-page.md   # design + content brief for AI to generate the roast page
└── examples/
    └── life-sucks/
        ├── playlist.json
        ├── preview.png    # screenshot preview for the README
        └── judgment.html  # the live demo (bilingual, exports to PNG)
```

## License

MIT — do whatever you want, just don't sue me.

## Credits

Built playfully by [@SoujiOkita98](https://github.com/SoujiOkita98) with a lot of AI co-writing. Inspired by the moment of realizing you've named a playlist "Life Sucks" and then loaded it with *Three Little Birds*.
