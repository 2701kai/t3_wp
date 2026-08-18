# t.o.d. pink - the Divi edition

The same night, editable with the **Divi Builder**. Two pieces, both need
your own Divi license (Divi is commercial and is not bundled here):

```
divi/child/                    Divi child theme: the pink tokens, embedded
                               fonts, effects JS, EMOTIQ drop-in, plus
                               divi-glue.css taming Divi's wrappers
divi/layouts/
  glitta-the-whole-page.json   the full page as native Divi sections/rows/
                               modules, our CSS classes riding on them
```

## Install

1. Install and activate **Divi** (Elegant Themes) as usual.
2. Build the child theme zip: `sh scripts/build-divi-zip.sh` →
   `tod-pink-divi-child.zip` (a licensed EMOTIQ file placed in
   `assets/fonts/` of the repo is packed in automatically).
3. wp-admin → **Appearance → Themes → Add New → Upload Theme** →
   `tod-pink-divi-child.zip` → activate. Divi stays installed as the parent.
4. Create a page »Glitta«, open it with the Divi Builder, then import the
   layout: **portability icon (↑↓) → Import → choose
   `glitta-the-whole-page.json`**. Save.
5. **Settings → Reading** → static homepage = »Glitta«.
6. Recommended: in the page's Divi settings choose the **Blank Page**
   template, so Divi's own header does not sit on top of the night. Or
   keep Divi's header and style it dark in the Customizer - your call.

Authored in the classic Divi portability format; Divi 5 (you are on
5.11) converts it on import. If the importer complains, report the exact
message - the layout is generated and easy to adjust.

## How editing works in the builder

- Texts, headings, links: normal Divi text modules - click and type.
- The magic (flicker, reveal, tilt, night frames) rides on **CSS classes**
  in each module's Advanced tab: `tod-split`, `tod-reveal`, `tod-tilt`,
  `h-section`, `h-set`, `tod-date`, `h-finale`, … Keep the classes when
  duplicating modules and everything keeps glowing.
- The two Code modules labeled »leave as is« hold the spores/laser
  canvas mounts and the equalizer.
- New set: duplicate a set card column, swap the title and the track id
  in the player url. New date: duplicate a date row module.
- Effects render on the live page, not inside the Visual Builder - the
  child theme deliberately keeps the effects JS out of builder mode so
  inline editing stays smooth.

## Which edition should Glitta use?

Both live in this repo and look the same. The block theme (repo root)
needs nothing but WordPress. The Divi edition makes sense if she already
lives in Divi or wants the builder's drag-and-drop everywhere. Pick one
per site - they are separate themes.
