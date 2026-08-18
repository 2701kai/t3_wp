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
  sections/                    the same page cut into one file per section,
                               plus five spares - import them one at a time
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

## Import one section at a time

`divi/layouts/sections/` holds twelve standalone layouts, each one a single
Divi section in the same portability format. Same route as the whole page:
open a page with the builder, **portability icon (↑↓) → Import → choose the
file**. Check the importer's replace-or-append option before you confirm -
appending is what you want when the page already carries something.

The seven numbered ones are the page itself, in the order it scrolls:
`01-hero`, `02-story`, `03-sets`, `04-dates`, `05-gallery`, `06-booking`,
`07-finale`. They are **generated** from `glitta-the-whole-page.json`, which
stays the single source of truth. Edit the whole page, then regenerate -
never the other way around:

```
python3 scripts/build-divi-sections.py
```

The five without a number are not on the page. They are spares that reach
into corners of `tod.css` the page leaves unused, so one can drop into any
night page without touching a stylesheet or rebuilding the child theme:

- **`press.json`** - a pull quote beside its context, for a line from a
  floor, a flyer, a review, a message at 4am.
- **`rider.json`** - two mono-typed fact cards: the booth on the left,
  travel and stay on the right.
- **`river.json`** - the credit strip for the very bottom of the page.
- **`single-set.json`** - one set, full width, with room for a sentence
  about it that the two-up cards in the Sets section have no space for.
- **`statement.json`** - one loud line between two quiet sections.

Every text in them is a placeholder - click and write over it. The admin
labels in the builder say which module is which.

The generator writes nothing unless all of it holds: the seven rebuild the
source byte for byte, every file's tags are balanced and nested the way Divi
needs them (a row inside a column is dropped silently, no error), every
class is one `tod.css` already defines, and the five use no module and no
attribute the whole-page layout does not already use.

**Not verified yet:** the five spares have never been through a real Divi
5.11 importer. The seven carry the whole page's shortcode unchanged, so they
import if it does; the five are built from the same modules and attributes,
which is good evidence and not the same thing as proof. If the importer
complains, report the exact message.

## Which edition should Glitta use?

Both live in this repo and look the same. The block theme (repo root)
needs nothing but WordPress. The Divi edition makes sense if she already
lives in Divi or wants the builder's drag-and-drop everywhere. Pick one
per site - they are separate themes.
