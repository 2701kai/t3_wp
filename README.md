# t3_wp - »t.o.d. pink - Glitta«

A WordPress **block theme** derived from the [TiTis on Decks](https://github.com/2701kai/t2)
site: the `/pink` night palette (void indigo, neon magenta, UV violet, cyan),
the animations (neon flicker-on titles, drifting spores, laser sweeps, pointer
tilt, the living equalizer) and the layout language - rebuilt without React,
so Glitta edits every text, photo, set and date herself in wp-admin.

The hero follows the `/anja` featured-artist layout (kicker → flickering
name → tilted portrait → intro); the sections below it are the `/pink`
home page: Story, Sets, Dates, Gallery, Booking, Finale. Default content
language is English - every word is editable, so any language works.

## Install

1. Build the zip: `sh scripts/build-zip.sh` → `tod-pink.zip`
   (licensed fonts placed in `assets/fonts/` are packed in automatically).
2. In wp-admin: **Appearance → Themes → Add New → Upload Theme** → `tod-pink.zip` → activate.
3. **Pages → Add New**: WordPress offers the starter layout
   **»Glitta - The Whole Page«** - pick it, title the page »Glitta«, publish.
4. **Settings → Reading**: »A static page« → homepage = »Glitta«.

Requires WordPress 6.5+ (any normal hosting with custom-theme upload;
WordPress.com only on the plan tier that allows theme uploads).

## Fonts - EMOTIQ and its stand-in

The display stack is **`'EMOTIQ', 'Audiowide', 'Monoton', …`**:

- **Audiowide** (OFL, embedded as a data URI) is the built-in default -
  the closest free match to EMOTIQ's wide, rounded techno caps.
- **EMOTIQ** (© Enxyclo Studio) is *not* bundled - t2 only holds its demo
  cut and the license is still pending. The moment a licensed file lands in
  **`assets/fonts/`** as `EMOTIQ.woff2` / `.woff` / `.otf` / `.ttf`,
  `functions.php` detects it and the whole site - front end and editor -
  switches to the real thing. Nothing else to configure.
- Font binaries in `assets/fonts/` stay out of git (public repo); the zip
  build packs them in, so an installed theme carries the licensed font.
- Note: installing EMOTIQ into your *operating system's* fonts only changes
  what **you** see locally - visitors need the webfont via the drop-in above.
- Sora (body) and Space Mono (labels) are embedded too - the site makes no
  external font requests at all (GDPR-clean, works offline in the woods).

## For Glitta - running the page

Everything happens on the »Glitta« page (Pages → Glitta → Edit):

- **Texts**: click, type over, done.
- **Your portrait**: click the empty image in the hero → media library.
- **Photos**: click the gallery in »Moments« and add images from the
  media library - captions get the night look automatically.
- **New set**: in »The Sound«, click a set card → ⋮ → Duplicate → swap the
  SoundCloud link in the embed block. WordPress builds the player itself.
- **New date**: in »Dates«, duplicate a row, swap the texts.
- **Booking address**: the mail button still holds `glitta@example.com` -
  replace it with the real address.
- Sections can also be inserted fresh: block inserter → category **»t.o.d. pink«**.

## What's inside

```
style.css              theme header
theme.json             pink palette + typography as editor tokens
templates/             front-page, page, index (header · content · footer)
parts/                 header (fixed neon nav), footer (credit river)
patterns/              hero · story · sets · dates · gallery · booking ·
                       finale · full-page (starter layout for new pages)
assets/css/fonts.css   Audiowide, Monoton, Sora, Space Mono - data URIs
assets/fonts/          EMOTIQ drop-in slot (see README.txt inside)
assets/css/tod.css     the ported night: tokens, sections, effects
assets/js/tod.js       vanilla ports of t2's Spores, SplitText, Reveal,
                       TiltCard, Waveform - all respect prefers-reduced-motion
screenshot.png         theme card in wp-admin
```

## The Divi edition

The same night also exists as a **Divi child theme + Divi Builder layout**
for sites that run Divi (Elegant Themes, commercial, not bundled) - see
[`divi/README.md`](divi/README.md). Build its zip with
`sh scripts/build-divi-zip.sh`; the layout to import lives in
`divi/layouts/glitta-the-whole-page.json`. Pick one edition per site.

## Derivation notes (t2 → WordPress)

- The pink variation was already a token swap in t2
  (`html[data-theme='pink']` in `styles/home.css`) - those values are now
  simply `:root` in `tod.css`, aliases (`--sun`, `--uvy`, …) kept intact so
  the ported section rules match the source line for line.
- `Spores` and `Waveform` were plain canvas/DOM in t2 and moved over almost
  verbatim; `SplitText`, `Reveal` and `TiltCard` were motion/React and are
  re-implemented with IntersectionObserver + CSS keyframes + `pointermove`.
  Reveal animates the CSS `translate` property, not `transform`, so a card
  can reveal *and* tilt at once.
- Without JavaScript nothing is hidden: effects only arm once `tod.js` adds
  `.tod-js` to `<html>`. With `prefers-reduced-motion` the night stands still.
- Content that lived in JS modules (`sets.js`, `media.js`, `eventsData.js`)
  is now ordinary block content; SoundCloud links auto-embed.

## Inherited watch-outs

- **Photo rights** - t2 is curtained over exactly this. Only imagery with
  cleared rights goes into the media library; the shipped theme contains no photos.
- **EMOTIQ license** - see the fonts section above; buy before going loud.
- **GPL** - the theme is GPL-2.0-or-later, like WordPress.

## Verified

Smoke-tested against a real WordPress (7.0.4, wp-cli + SQLite) with
Playwright: patterns register, the starter layout assembles the full page,
both SoundCloud oEmbeds resolve into players, all reveals/splits fire,
spores + equalizer run, tilt + glare follow the pointer, the EMOTIQ
drop-in switches the display face, no console errors, zero editor warnings.
