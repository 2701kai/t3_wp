# t3_wp — a WordPress theme from t.o.d.

Glitta's personal page, derived from the [TiTis on Decks](https://github.com/2701kai/t2)
site (`t2`): same animations, same layout language, the **pink & purple night
palette** (`/pink`) — rebuilt as a WordPress theme she can install once and
then feed herself: texts, photos, sets, dates, all from wp-admin.

## Why this is very doable

The t2 site was built in a way that makes the derivation cheap:

- **The pink variation is ~30 lines of CSS custom properties.**
  `html[data-theme='pink']` in `src/styles/home.css` swaps the tokens
  (void indigo `#08041a`, neon magenta `#ff3ecf`, UV violet `#8a5cff`,
  cyan `#37f5e0`, acid `#b8ff2e`, cream `#f0e9ff`) over the *same* section
  styles. The theme ships only the pink block — no theme switcher needed.
- **Half the animations are already framework-free.**
  `Spores` and `Waveform` are plain canvas (their default colors *are* the
  pink palette), `ShinyText` is pure CSS. They move over almost verbatim.
- **The React-only pieces are tiny.** `SplitText` (neon flicker-on),
  `Reveal` (scroll fade + rise) and `TiltCard` (pointer tilt + glare) are
  ~30–90 lines each and re-implement cleanly in vanilla JS:
  IntersectionObserver + CSS keyframes with per-character delays, and a
  `pointermove` handler for the tilt. No React in the WordPress theme.
- **There is already a blueprint for a personal page.** `/anja` is a
  one-artist page *in the pink theme*: kicker → flicker-on name → tilted
  portrait → caption → intro. Glitta's hero is that page, grown up —
  plus her sets, dates, gallery and contact from the home page sections.

## Architecture: block theme (FSE)

A modern **block theme** — not a classic PHP theme — because the whole
point is that Glitta edits everything herself in the Site Editor:

```
tod-pink/
  style.css              theme header
  theme.json             pink palette + typography as editor tokens
  templates/             index, page, single (minimal HTML templates)
  parts/                 header (nav), footer (finale gradient)
  patterns/              hero, story, sets, dates, gallery, booking — one
                         pattern per t2 section, pre-filled, fully editable
  assets/css/            ported home.css (pink block + section styles)
  assets/css/fonts.css   the embedded data-URI fonts, unchanged
  assets/js/tod.js       spores · waveform · split-text · reveal · tilt
                         (vanilla, respects prefers-reduced-motion)
  functions.php          enqueues, pattern registration
```

Content mapping — what Glitta touches in wp-admin:

| t2 today | WordPress |
|----------|-----------|
| texts in `i18n/translations.jsx` | headings/paragraphs in the editor |
| `media.js` + `public/media/` | Media Library + gallery pattern |
| `sets.js` (SoundCloud links) | paste a SoundCloud URL — WP auto-embeds it |
| `eventsData.js` | an editable dates pattern (v1); an Events CPT in a tiny companion plugin if she wants archive/filtering later (v2) |
| `api/booking.js` (Vercel + Resend) | a form plugin, or a small handler on `wp_mail` |
| DE / PT / EN | v1 ships one language (DE); Polylang later if wanted |

## Build order

1. **Scaffold + tokens** — theme header, `theme.json` with the pink
   palette and type scale, port `fonts.css` and the `data-theme='pink'`
   token block. The site background/glow lands on `body`.
2. **Sections as patterns** — port the section CSS from `home.css`,
   rebuild each section's markup as a block pattern (hero modeled on
   `/anja`, then story, sets, dates, gallery, booking, finale).
3. **The effects file** — vanilla ports of Spores, Waveform, SplitText,
   Reveal, TiltCard behind `prefers-reduced-motion`, wired by class names
   the patterns already carry.
4. **Content wiring** — menu, gallery, SoundCloud embeds, contact form.
5. **Package + hand over** — zip, install on her WordPress, and a
   ten-minute walkthrough: edit a text, swap a photo, add a set, add a date.

## Watch-outs (inherited from t2)

- **EMOTIQ is the demo cut** (© Enxyclo Studio, license pending in t2).
  Before Glitta's page goes public: buy the license, or her theme's
  display font falls back to Monoton/Sora, which are OFL and already
  embedded.
- **Photo rights** — t2 is curtained over exactly this. Her page only
  ships imagery she holds rights to; everything else stays placeholders
  until cleared.
- **Hosting** — she needs a WordPress that accepts custom themes: any
  self-hosted WP, or WordPress.com on the plan tier that allows theme
  uploads. (The Vercel/serverless booking pipeline does not come along —
  WordPress replaces it.)
- **GPL** — if the theme is ever distributed beyond her install, it
  should be GPL-compatible like WordPress itself. Private use: no issue.
