# Importing a section

Twelve layouts, each one a single Divi section in the classic portability
format. Import one into any page - you do not need the whole night to use
a piece of it.

## Before the first import

Two things have to be in place, or the section arrives as plain text on a
white page and looks broken when it is not:

1. **Divi** is active (Elegant Themes, commercial, not bundled here).
2. The child theme **»t.o.d. pink - Glitta (Divi Child)«** is the active
   theme - Appearance → Themes. It is the only thing that loads `tod.css`
   and `divi-glue.css`, and those two carry every class these sections
   ride on. Divi alone renders the markup and none of the night.

Build the child theme zip with `sh scripts/build-divi-zip.sh` from the repo
root; the full install walk-through lives in [`divi/README.md`](../../README.md).

Use **0.2.3 or newer**. Older builds miss the geometry fix that keeps Divi's
generated per-module CSS from squashing the sections - the symptom is a
cramped page with no breathing room between blocks.

## Import

1. Open the page with the **Divi Builder**.
2. Click the **portability icon (↑↓)**.
3. **Import** → choose one of the `.json` files here.
4. Look for the option that **replaces** the page's existing content and
   leave it **off** - you want the section added, not the page overwritten.
   With it on, everything already on that page is gone.
5. Import, then save.

The section lands at the end of the page. Drag it where you want it by its
section handle, or use the builder's layers view for longer pages.

## Which file

The seven numbered ones are the page itself, in the order it scrolls:

| file | the block |
|------|-----------|
| `01-hero.json` | name, portrait, equalizer, the spores and laser sweeps |
| `02-story.json` | quote beside the copy, genre pills below |
| `03-sets.json` | two set cards with SoundCloud players |
| `04-dates.json` | the date rows |
| `05-gallery.json` | Divi gallery module in the night frame |
| `06-booking.json` | booking intro and the two buttons |
| `07-finale.json` | »See you at sunrise«, night turning morning |

The five without a number are **not** on the page. They are spares that use
corners of `tod.css` the page leaves unused, so each drops in without a CSS
change and without rebuilding the child theme:

| file | the block |
|------|-----------|
| `press.json` | a pull quote beside its context - a line from a floor, a flyer, a review |
| `rider.json` | two mono-typed fact cards: the booth, and travel plus stay |
| `river.json` | the credit strip for the very bottom of the page |
| `single-set.json` | one set, full width, with room for a sentence about it |
| `statement.json` | one loud line between two quiet sections |

Every text in them is a placeholder - click and write over it. The admin
labels in the builder say which module is which, and the ones that say
»write over this« mean it.

Want the whole page? Import
[`../glitta-the-whole-page.json`](../glitta-the-whole-page.json) instead -
one import rather than seven, and the same result.

## When something looks wrong

| what you see | what it is |
|--------------|-----------|
| Text renders, but grey or serif, no colour, no frames | The child theme is not the active theme. Divi is rendering the markup without `tod.css`. |
| No flicker, no fade-in, no tilt - inside the builder | By design. The child theme keeps the effects JS out of builder mode so inline editing stays smooth. Look at the live page. |
| Sections sit cramped against each other | Child theme older than 0.2.3. Rebuild the zip and re-upload; no re-import needed, the fix is CSS only. |
| Divi's page title above the hero | Give the page the **Blank Page** template in the page's Divi settings. |
| A block of content simply is not there | A row nested inside a column - Divi drops those silently, without an error. Only possible in a hand-edited file. Regenerate. |
| The importer refuses the file | Report the exact message. These are generated and easy to adjust. |

## Do not hand-edit the numbered seven

They are generated from `../glitta-the-whole-page.json`, which stays the
single source of truth. Edit the whole page, then regenerate from the
repo root:

```
python3 scripts/build-divi-sections.py
```

The generator writes nothing unless every check holds - the seven have to
rebuild the source byte for byte, tags have to balance, nesting has to stay
section → row → column → module, every class has to be one `tod.css`
already defines, and the five spares may use no module and no attribute the
whole page does not already use. A failed check exits non-zero and leaves
the files alone.

Editing one of these directly means your change is gone the next time
anyone runs it. The five spares are authored inside the script itself, so
they are no different - change them there.

## Not verified yet

The layouts are written in the classic 4.27.4 portability format and Divi 5
(the site runs 5.11) converts them on import. The whole page has been
through that conversion. **The five spares have not.** They are built from
the same modules and attributes as the page - which is evidence, not proof.

The Divi Library question is answered, and the answer is no. A library
import wants `"context": "et_builder_layouts"`, a WordPress-post-shaped
object per layout whose `post_content` is already Divi 5 block markup
(`<!-- wp:divi/section … -->`), plus a `terms` array for the builder's
library pickers. These files are page-portability exports carrying 4.x
shortcode, so the Library importer is not their door - the builder's
↑↓ on a page is. Source: the community-maintained Divi 5 notes at
16wells.github.io/divi-docs (`internals/library-import-json`), verified
there 2026-03-17. Reverse-engineered, not Elegant Themes official.

If an import goes sideways, the exact importer message is the useful thing
to report.
