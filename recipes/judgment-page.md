# Recipe: Playlist Judgment Page

A brief for any LLM that needs to generate a "playlist judgment" HTML page in the same visual language as `examples/life-sucks/judgment.html`.

The output is a **single self-contained HTML file** the user can open in a browser, screenshot, or export as PNG.

---

## Goal

Given a playlist JSON (the output of `scripts/extract_spotify_playlist.py`), produce a doodle / hand-drawn / tldraw-style page that:

1. Reads the playlist and forms a real opinion (not generic flattery).
2. Renders that opinion as a screenshot-friendly visual page with structured content blocks.
3. Includes EN/中 toggle, PNG export, and predictable visual fidelity in the export.

Tone is playful and pointed — like a friend roasting your taste, not a marketing brand. Specifics over generics. Call out actual track names, actual patterns. Anything generic is a failure.

---

## Step 1: Read the playlist and form a take

Before writing any HTML, read the full JSON and look for **the angle**. Examples of strong angles:

- **Title-vs-content irony** — playlist named "Sad Hours" full of dance pop, etc.
- **Cluster discovery** — a 14-track block by one artist, an unexpected language pocket, a soundtrack obsession.
- **Funniest pairing** — adjacent tracks with comically different energies.
- **Era clash** — pre-1980 nostalgia jammed against TikTok-era pop.
- **Duplicates** — different versions of the same song, or the literal same track twice.

Write your angle in one sentence. Everything else flows from it.

---

## Step 2: Structured content blocks

Every judgment page has these blocks, in order. Adapt content per playlist; keep the structure.

### Header
- A small "pre-line" (e.g., *"A solemn AI verdict on the playlist titled"*).
- The playlist title in a big hand-drawn font, in quote marks.
- Meta: `by <owner> · <N> tracks · ~<duration> of feelings`.
- A "verdict stamp" in the top-right corner — a circular red stamp with a score out of 10.

### Verdict card
- A small label (`⌜ THE VIBE ⌝`).
- A 3–4 line verdict in a big hand-drawn font, with marker-highlighted key phrases (`<em>` tag) and accent-colored phrases (`<span class="pop">`).
- A "why" paragraph that justifies the verdict, naming specific tracks.

### Spectrum (breakdown card)
- 6–8 doodled bar-chart rows showing the playlist's makeup. Categories should be specific to *this* playlist (don't use generic genre names if you can name a cluster).
- Below the bars, a row of "pills" with surprising stats: artist counts (`Beatles ×8`), language count, longest track, etc.

### Taxonomy (cluster card)
- 5–7 named clusters. Each has a fun emoji + name (`📻 The Boomer Dad Canon`) and a short description that names actual artists/tracks.
- Cluster names should be **specific and slightly mean** — "The Reggae Denial Cabana" beats "Reggae section".

### Picks (4 small cards in a 2×2 grid)
- **Most basic pick** — a one-line track + artist + a tiny justification.
- **Most pretentious / most chaotic** — same format.
- **Funniest pairing** — two tracks linked by `→`, with a caption.
- These are the most-shared cards on social. Make the captions land.

### Energy arc (squiggle SVG)
- A hand-drawn SVG curve representing the playlist's emotional shape, with 5–7 labeled inflection points (e.g., `Oasis idle ☕ → AC/DC pivot 🚗 → 草东 spiral 🌧 → ...`). Don't try to match actual track order perfectly; the squiggle is a vibe map, not a chart.

### The roast (4 paragraphs)
- This is the meat. 4 short paragraphs of pointed-but-affectionate judgment. Each paragraph should call out something **specific** in the playlist:
  1. The biggest contradiction or pattern (often the angle from Step 1).
  2. Where the real emotional truth of the playlist lives (which cluster is most honest).
  3. A small audit observation (duplicates, weird filing, version chaos).
  4. The final verdict + score, with a one-line "lose X and the rating goes up" suggestion.

### Quote block
- A pithy two-line quote summarizing the playlist's contradiction or essence, with a date stamp.

### Footer
- "made with ♥ & suspicion · share me 📸" — keep it lightweight.

---

## Step 3: Visual design system

Steal the palette and typography directly from the example. Don't redesign.

### Color tokens
```css
--ink:       #2b2018;   /* main text — warm dark brown, NOT pure black */
--ink-soft:  #5a4a3a;
--paper:     #fef9e7;   /* page background — warm cream */
--y:         #fff39c;   /* yellow card */
--p:         #ffc8de;   /* pink card */
--b:         #bfe2ff;   /* blue card */
--g:         #cdf2c6;   /* green card */
--o:         #ffcc94;   /* orange card */
--l:         #d9caff;   /* lavender card */
--r:         #ffb3b3;   /* red card */
--hi:        #fff176;   /* marker highlight yellow */
```

### Fonts (Google Fonts)
- **Caveat** — headers, big text, hand-drawn feel.
- **Patrick Hand** — body text.
- **Kalam** — captions, callouts.
- **Shadows Into Light** — small scribbled notes.

Load them all from one Google Fonts URL.

### Card pattern
Cards are post-it style:
- Pastel background from the token palette
- Rounded corners (`border-radius: 6px`)
- Slight rotation (`transform: rotate(-1deg)` to `rotate(2deg)`) — every card slightly different so it feels hand-placed, not gridded.
- Soft drop shadow: `box-shadow: 2px 4px 0 rgba(0,0,0,.08), 6px 10px 18px rgba(0,0,0,.08)`.
- Optional washi-tape strip at the top: a small rotated rectangle with semi-transparent color.

### Marker highlight (`em` tag)
**Critical:** use `background-size`, NOT gradient color stops. html2canvas v1.4.1 has known bugs with linear-gradient color stops on inline elements (renders inconsistently per element). Use this:

```css
em {
  font-style: normal;
  background-image: linear-gradient(var(--hi), var(--hi));
  background-repeat: no-repeat;
  background-size: 100% 0.32em;
  background-position: 0 100%;
  padding: 0 3px;
}
```

This produces a yellow band at the bottom of the text, scaled by font size. Renders identically in browser and in the PNG export.

### Doodle SVGs (inline)
Use small inline SVGs for: scribbled vibe lines, stars, hand-drawn arrows, the energy arc curve. Keep stroke-width 2–3px, use `stroke-linecap="round"`, color them with the accent reds (`#c0392b`).

---

## Step 4: Bilingual implementation

The page must support EN ↔ 中 toggling. Default is English.

### CSS pattern
```css
.lang-zh-only { display: none; }
body.lang-zh .lang-en-only { display: none; }
body.lang-zh .lang-zh-only { display: revert; }
```

### Toggle button (top-left, fixed)
```html
<div class="lang-toggle" id="lang-toggle">
  <button class="active" data-lang="en">EN</button>
  <button data-lang="zh">中</button>
</div>
```

JS handler toggles `body.lang-zh` class and sets `document.documentElement.lang`.

### Content pattern
For inline text:
```html
<span class="lang-en-only">English text</span>
<span class="lang-zh-only">中文文本</span>
```

For block-level (paragraphs, divs):
```html
<p class="lang-en-only">English paragraph</p>
<p class="lang-zh-only">中文段落</p>
```

For SVG `<text>` elements: `display: none` works on SVG elements in modern browsers.

For `::before` content (e.g., the "THE ROAST" label):
```css
.roast::before { content: "THE ROAST"; }
body.lang-zh .roast::before { content: "锐评"; }
```

### Tone matching across languages
Don't translate literally. Match the *vibe*. The English roast lands differently than the Chinese one needs to. Translate the joke, not the words.

---

## Step 5: PNG export via html2canvas

Single dependency, loaded from CDN. Place a fixed-position **Save as PNG** button bottom-right.

### Setup
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
```

### Export function pattern
```js
async function exportPNG() {
  // 1. wait for fonts so the screenshot uses the right typefaces
  if (document.fonts && document.fonts.ready) await document.fonts.ready;

  // 2. hide UI chrome (lang toggle, export button) so it isn't captured
  langToggle.style.display = 'none';
  exportBar.style.display = 'none';

  // 3. capture .page (not body — body is viewport-wide)
  const target = document.querySelector('.page');
  const canvas = await html2canvas(target, {
    backgroundColor: '#fef9e7',
    scale: 2,                      // retina sharpness
    useCORS: true,
    logging: false,
    windowWidth: 972,              // 900px page + 36px*2 padding
  });

  // 4. trigger download
  const link = document.createElement('a');
  link.download = 'playlist-verdict.png';
  link.href = canvas.toDataURL('image/png');
  link.click();

  // 5. restore UI
  langToggle.style.display = '';
  exportBar.style.display = '';
}
```

### html2canvas gotchas (already mitigated in the example)
- **`linear-gradient` with color stops renders inconsistently.** Avoid for marker highlights — use `background-size` instead (see Step 3).
- **Web fonts must be loaded before capture.** Always `await document.fonts.ready`.
- **Inline elements with `box-shadow` may render flaky.** Avoid for highlights.
- **SVG `<text>` is supported.** Use it freely.
- **Background gradients on `body` may not capture.** Pass `backgroundColor` option to html2canvas instead of relying on body bg.
- **`windowWidth` and `scale`** matter — set them explicitly. Default `scale: 1` looks pixelated; use `2`.

### CJK character height
For Chinese text, descender-less ideographs make the marker band visually more aggressive. The `0.32em` size in the marker CSS above already accounts for this — don't go bigger.

---

## Step 6: Tone options

Default tone: **gentle roast** — pointed but affectionate, like a friend who knows your weaknesses. Other personas the user can request:

- **Astrology girlie** — "this playlist is so Mercury-in-retrograde-Pisces of you..."
- **Deadpan British critic** — "I see. We're doing... that."
- **Wholesome therapist** — gently reframes every choice as healing.
- **Drill-sergeant fan** — over-the-top hyped about every choice, in caps.

Each persona changes the verdict line, the roast paragraphs, and the cluster names. The visual design stays the same.

---

## Output

A single `judgment.html` file, fully self-contained (Google Fonts and html2canvas via CDN, all other CSS / JS inline). User opens it in a browser, screenshots it, or clicks **Save as PNG** for a 2× retina image.

When done, suggest the user open the file:
```bash
open judgment.html
```
