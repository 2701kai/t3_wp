# t3_wp — »t.o.d. pink — Glitta«

A WordPress **block theme** derived from the [TiTis on Decks](https://github.com/2701kai/t2)
site: the `/pink` night palette (void indigo, neon magenta, UV violet, cyan),
the animations (neon flicker-on titles, drifting spores, laser sweeps, pointer
tilt, the living equalizer) and the layout language — rebuilt without React,
so Glitta edits every text, photo, set and date herself in wp-admin.

The hero follows the `/anja` featured-artist layout (kicker → flickering
name → tilted portrait → intro); the sections below it are the `/pink`
home page: Story, Sets, Termine, Galerie, Booking, Finale.

## Install

1. Build the zip: `sh scripts/build-zip.sh` → `tod-pink.zip`
   (or download the repo zip from GitHub and rename the inner folder to `tod-pink`).
2. In wp-admin: **Design → Themes → Hinzufügen → Theme hochladen** → `tod-pink.zip` → aktivieren.
3. **Seiten → Erstellen**: WordPress offers the starter layout
   **»Glitta — die ganze Seite«** — pick it, title the page »Glitta«, publish.
4. **Einstellungen → Lesen**: »Eine statische Seite« → homepage = »Glitta«.

Requires WordPress 6.5+ (any normal hosting with custom-theme upload;
WordPress.com only on the plan tier that allows theme uploads).

## Für Glitta — so pflegst du die Seite

Alles passiert auf deiner Seite »Glitta« (Seiten → Glitta → Bearbeiten):

- **Texte**: anklicken, drüberschreiben. Fertig.
- **Dein Porträt**: das leere Bild im Hero anklicken → Mediathek → Foto wählen.
- **Fotos**: im Abschnitt »Momente« auf die Galerie klicken und Bilder aus
  der Mediathek hinzufügen — Captions erscheinen automatisch im Nacht-Look.
- **Neues Set**: im Abschnitt »Der Sound« eine Set-Karte anklicken →
  ⋮ → Duplizieren → SoundCloud-Link im Einbettungsblock tauschen.
  Den Player baut WordPress von selbst.
- **Neues Date**: im Abschnitt »Termine« eine Zeile duplizieren, Texte tauschen.
- **Booking-Adresse**: im Kontakt-Abschnitt steckt noch `glitta@example.com`
  im Mail-Button — durch die echte Adresse ersetzen.
- Einzelne Abschnitte lassen sich auch neu einfügen: Block-Inserter →
  Kategorie **»t.o.d. pink«**.

## What's inside

```
style.css              theme header
theme.json             pink palette + typography as editor tokens
templates/             front-page, page, index (header · content · footer)
parts/                 header (fixed neon nav), footer (credit river)
patterns/              hero · story · sets · dates · gallery · booking ·
                       finale · full-page (starter layout for new pages)
assets/css/fonts.css   Monoton, Sora, Space Mono — embedded as data URIs,
                       no external requests (GDPR-clean, works offline)
assets/css/tod.css     the ported night: tokens, sections, effects
assets/js/tod.js       vanilla ports of t2's Spores, SplitText, Reveal,
                       TiltCard, Waveform — all respect prefers-reduced-motion
screenshot.png         theme card in wp-admin
```

## Derivation notes (t2 → WordPress)

- The pink variation was already a token swap in t2
  (`html[data-theme='pink']` in `styles/home.css`) — those values are now
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

- **EMOTIQ is not bundled.** t2 ships only the demo cut (© Enxyclo Studio,
  license pending), so this theme's display face is Monoton — draft1's
  original neon, fitting for the pink/purple night. Once EMOTIQ is licensed:
  add its `@font-face` to `assets/css/fonts.css` and put `'EMOTIQ'` first in
  `--font-display` in `assets/css/tod.css`.
- **Photo rights** — t2 is curtained over exactly this. Only imagery with
  cleared rights goes into the Mediathek; the shipped theme contains no photos.
- **GPL** — the theme is GPL-2.0-or-later, like WordPress.

## Verified

Smoke-tested against a real WordPress (6.x, wp-cli + SQLite) with
Playwright: patterns register, the starter layout assembles the full page,
both SoundCloud oEmbeds resolve into players, all reveals/splits fire,
spores + equalizer run, tilt + glare follow the pointer, no console errors.
