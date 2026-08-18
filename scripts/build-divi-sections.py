#!/usr/bin/env python3
"""Generate divi/layouts/sections/ from divi/layouts/glitta-the-whole-page.json.

Two jobs:

1. Split the whole page into one Divi portability export per section, in
   document order: 01-hero … 07-finale. The whole-page file stays the single
   source of truth - these seven are generated, never hand-edited.

2. Emit five spare sections authored right here (unprefixed filenames, they
   are not part of the page): press, rider, river, single-set, statement.
   They reach into corners of assets/css/tod.css the page does not use yet,
   so importing one needs no CSS change and no theme rebuild.

Every run verifies before it writes a single byte:

  - the seven split shortcodes concatenate back to the source, byte for byte
  - every file's et_pb_* tags are balanced
  - nesting is section > row > column > module. An [et_pb_row] inside an
    [et_pb_column] is invalid: Divi drops it silently, no error, and the
    content simply never appears. That rule is asserted, not remembered.
  - the five authored sections name only classes assets/css/tod.css defines;
    all twelve are checked against tod.css + the Divi glue
  - the five use no module tag and no attribute the whole-page layout does
    not already use - that file is known to import, these inherit the evidence

Any failed check exits non-zero and nothing is written.

Usage: python3 scripts/build-divi-sections.py
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "divi/layouts/glitta-the-whole-page.json"
OUT_DIR = ROOT / "divi/layouts/sections"
TOD_CSS = ROOT / "assets/css/tod.css"
GLUE_CSS = ROOT / "divi/child/assets/css/divi-glue.css"

# The layouts are authored in the classic (4.27.4) portability format; Divi 5
# converts them on import. Keep this in step with the whole-page file.
V = "4.27.4"

PAGE_SECTIONS = [
    ("01-hero", "Hero"),
    ("02-story", "Story"),
    ("03-sets", "Sets"),
    ("04-dates", "Dates"),
    ("05-gallery", "Gallery"),
    ("06-booking", "Booking"),
    ("07-finale", "Finale"),
]

TAG = re.compile(r"\[(/?)(et_pb_[a-z0-9_]+)([^\]]*)\]")
CLASS_ATTR = re.compile(r'(?:module_class|class)="([^"]*)"')
ADMIN_LABEL = re.compile(r'admin_label="([^"]*)"')
ATTR_NAME = re.compile(r'([a-z_0-9]+)="')


# ---------------------------------------------------------------- shortcodes

def _attrs(pairs):
    """Render attributes in the given order, dropping the ones left None."""
    return "".join(' %s="%s"' % (key, value) for key, value in pairs if value is not None)


def section(admin_label, body, module_class=None, module_id=None, wrap_row=True):
    """A top-level [et_pb_section].

    body is a list of module shortcodes and gets wrapped in one full-width
    row with a single 4_4 column - the shape almost every section wants.

    wrap_row=False hands that job to the caller: body is then a list of
    finished rows. Needed whenever a class has to ride on a column rather
    than on a module (.h-set is a column, see single_set below) or when a
    section needs several rows of differing column layouts (press). Wrapping
    those in another row would nest [et_pb_row] inside [et_pb_column], which
    Divi discards without a word.
    """
    inner = "".join(body)
    if wrap_row:
        inner = row([column(inner)])
    open_tag = "[et_pb_section fb_built=\"1\"" + _attrs([
        ("module_class", module_class),
        ("module_id", module_id),
        ("background_enable_color", "off"),
        ("custom_padding", "0px||0px||true|false"),
        ("admin_label", admin_label),
        ("_builder_version", V),
    ]) + "]"
    return open_tag + inner + "[/et_pb_section]"


def row(columns, module_class=None, admin_label=None):
    open_tag = "[et_pb_row" + _attrs([
        ("module_class", module_class),
        ("width", "100%"),
        ("max_width", "none"),
        ("custom_padding", "0px||0px||true|false"),
        ("admin_label", admin_label),
        ("_builder_version", V),
    ]) + "]"
    return open_tag + "".join(columns) + "[/et_pb_row]"


def column(body, type_="4_4", module_class=None):
    open_tag = "[et_pb_column" + _attrs([
        ("type", type_),
        ("module_class", module_class),
        ("_builder_version", V),
    ]) + "]"
    return open_tag + body + "[/et_pb_column]"


def text(html, module_class=None, admin_label=None):
    open_tag = "[et_pb_text" + _attrs([
        ("module_class", module_class),
        ("admin_label", admin_label),
        ("_builder_version", V),
    ]) + "]"
    return open_tag + html + "[/et_pb_text]"


def code(html, admin_label=None):
    open_tag = "[et_pb_code" + _attrs([
        ("admin_label", admin_label),
        ("_builder_version", V),
    ]) + "]"
    return open_tag + html + "[/et_pb_code]"


def heading(kicker, title, admin_label="Heading"):
    return text(
        '<p class="h-kicker">%s</p><h2 class="h-h2">%s</h2>' % (kicker, title),
        module_class="tod-reveal",
        admin_label=admin_label,
    )


def note(copy):
    return text('<p class="h-note">%s</p>' % copy, admin_label="Note")


# ------------------------------------------------------- the five extra ones

def press():
    """.h-quote + .h-copy - the story section's two-column idiom, reused for
    a press voice. Own rows, because the quote/copy pair is a 1_3 + 2_3
    split and the heading above it is full width."""
    return section(
        "Press - voices from the floor",
        module_class="h-section",
        module_id="press",
        wrap_row=False,
        body=[
            row([column(heading("Press", "What the <em>floor</em> says"))]),
            row([
                column(
                    text(
                        '<p class="h-quote">She does not play the night. '
                        '<em>She is the night.</em></p>',
                        module_class="tod-reveal",
                        admin_label="Pull quote - write over this",
                    ),
                    type_="1_3",
                ),
                column(
                    text(
                        '<div class="h-copy">'
                        '<p><strong>Where this came from</strong> - a line from a floor, a '
                        'flyer, a review, a message at 4am. Paste it here and name the '
                        'source in the next paragraph.</p>'
                        '<p>Second paragraph for context: which night, which room, who was '
                        'there. Keep it short - the quote does the work.</p>'
                        '</div>',
                        module_class="tod-reveal",
                        admin_label="Context - write over this",
                    ),
                    type_="2_3",
                ),
            ], admin_label="Quote + context - duplicate this row for another voice"),
            row([column(note(
                "New voice: duplicate the quote row and swap both texts. "
                "Only quote what you are allowed to quote."
            ))]),
        ],
    )


def rider():
    """.h-facts - the mono-typed fact card, twice, side by side."""
    setup = (
        '<div class="h-facts">'
        '<p><strong>Set length</strong>60 to 180 minutes, b2b on request</p>'
        '<p><strong>Booth</strong>2x CDJ-3000 + DJM-900NXS2, or an equivalent Pioneer setup</p>'
        '<p><strong>Monitoring</strong>One wedge on its own send, please</p>'
        '<p><strong>Sound check</strong>30 minutes before doors</p>'
        '</div>'
    )
    around = (
        '<div class="h-facts">'
        '<p><strong>Travel</strong>From the Algarve - flights and ground on the promoter</p>'
        '<p><strong>Stay</strong>One room, late checkout - the night runs long</p>'
        '<p><strong>Guest list</strong>Two names</p>'
        '<p><strong>Contact</strong>booking@glitta.rocks</p>'
        '</div>'
    )
    return section(
        "Rider - the technical facts",
        module_class="h-section",
        module_id="rider",
        wrap_row=False,
        body=[
            row([column(heading("Rider", "What I bring, what I <em>need</em>"))]),
            row([
                column(text(setup, module_class="tod-reveal",
                            admin_label="Facts card - the booth"), type_="1_2"),
                column(text(around, module_class="tod-reveal",
                            admin_label="Facts card - around the set"), type_="1_2"),
            ], admin_label="Fact cards - duplicate a column for a third card"),
            row([column(note(
                "Every line here is a placeholder, not a contract - write over them. "
                "Label in bold, value after it."
            ))]),
        ],
    )


def river():
    """.h-river - the credit strip at the very bottom, same markup as the
    block theme's parts/footer.html.

    Deliberately NOT a classed section: .h-section would inset it, and a
    class on the section loses to Divi's own per-module padding rule, which
    loads after divi-glue.css. Inside a text module the river keeps its own
    padding and gradient and needs nothing from the glue."""
    inner = (
        '<div class="h-river"><div class="h-river-inner">'
        '<p>GLITTA - one of the mothers of '
        '<a href="https://soundcloud.com/titisondecks">TiTis on Decks</a></p>'
        '<p><a href="https://soundcloud.com/glittawicca">SoundCloud</a> '
        '· built on the t.o.d. night</p>'
        '</div></div>'
    )
    return section(
        "Credit river - the very bottom of the page",
        body=[text(inner, admin_label="River - two lines, left and right")],
    )


def single_set():
    """.h-set + .h-set-desc - one set, full width, with room for a sentence
    about it (the page's two-up cards have no description line).

    .h-set rides on the COLUMN (see .et_pb_column.h-set in divi-glue.css),
    so this section brings its own rows: a row cannot live inside a column."""
    card = text(
        '<p class="h-set-meta">154 MIN · GLITTA B2B LUTZI</p>'
        '<h3 class="h-set-title">3 Empresses</h3>'
        '<p class="h-set-desc">Three hours that started as a warm-up and never came '
        'back down. Recorded live, unedited, somewhere past the point where the '
        'floor stops asking what time it is.</p>',
        admin_label="Set - title, meta and the description line",
    ) + code(
        '<iframe title="3 Empresses" width="100%" height="360" scrolling="no" '
        'frameborder="no" allow="autoplay" '
        'src="https://w.soundcloud.com/player/?visual=true&url='
        'https%3A%2F%2Fapi.soundcloud.com%2Ftracks%2F2222797898&show_artwork=true">'
        '</iframe>',
        admin_label="Player - swap the track id in the url",
    )
    return section(
        "Single set - one night, full width",
        module_class="h-section",
        module_id="one-set",
        wrap_row=False,
        body=[
            row([column(heading("One Night", "The set that <em>stayed</em>"))]),
            row(
                [column(card, module_class="h-set tod-reveal")],
                admin_label="Set card - the h-set class lives on the column, keep it",
            ),
            row([column(note(
                "One card, full width - for the set that deserves its own section. "
                "The two-up grid lives in the Sets section."
            ))]),
        ],
    )


def statement():
    """.h-statement - one loud line between two quiet sections."""
    return section(
        "Statement - one line, loud",
        module_class="h-section",
        module_id="statement",
        body=[
            heading("Between sets", "A word before the <em>next</em> one"),
            text(
                '<p class="h-statement">A floor is not an audience. '
                '<em>It is a conversation.</em></p>',
                module_class="tod-reveal",
                admin_label="Statement - write over this",
            ),
            note("Short is the point. One or two lines, the em marks the glowing part."),
        ],
    )


EXTRA_SECTIONS = [
    ("press", press),
    ("rider", rider),
    ("river", river),
    ("single-set", single_set),
    ("statement", statement),
]


# -------------------------------------------------------------------- checks

class CheckFailed(Exception):
    pass


def split_page(shortcode):
    """Slice the page into its top-level sections, in document order."""
    parts, depth, start = [], 0, None
    for match in TAG.finditer(shortcode):
        if match.group(2) != "et_pb_section":
            continue
        if match.group(1):
            depth -= 1
            if depth == 0:
                parts.append(shortcode[start:match.end()])
        else:
            if depth == 0:
                start = match.start()
            depth += 1
    if depth != 0:
        raise CheckFailed("source: unbalanced [et_pb_section] tags")
    return parts


def check_round_trip(parts, shortcode):
    rejoined = "".join(parts)
    if rejoined != shortcode:
        raise CheckFailed(
            "round-trip: the split sections do not rebuild the source "
            "(%d bytes out vs %d in)" % (len(rejoined), len(shortcode))
        )


def check_structure(name, shortcode):
    """Tag balance and Divi's container nesting, in one pass."""
    stack = []
    for match in TAG.finditer(shortcode):
        closing, tag = match.group(1), match.group(2)
        if closing:
            if not stack:
                raise CheckFailed("%s: [/%s] closes nothing" % (name, tag))
            if stack[-1] != tag:
                raise CheckFailed(
                    "%s: [/%s] closes an open [%s]" % (name, tag, stack[-1])
                )
            stack.pop()
            continue

        parent = stack[-1] if stack else None
        if parent is None:
            allowed = tag == "et_pb_section"
            expected = "only [et_pb_section] at the top level"
        elif parent == "et_pb_section":
            allowed = tag == "et_pb_row"
            expected = "a section holds rows"
        elif parent == "et_pb_row":
            allowed = tag == "et_pb_column"
            expected = "a row holds columns"
        elif parent == "et_pb_column":
            allowed = tag not in ("et_pb_section", "et_pb_row", "et_pb_column")
            expected = "a column holds modules - Divi drops a nested row silently"
        else:
            allowed = False
            expected = "a module holds no further et_pb_ tags"
        if not allowed:
            raise CheckFailed(
                "%s: [%s] inside [%s] - %s" % (name, tag, parent or "nothing", expected)
            )
        stack.append(tag)

    if stack:
        raise CheckFailed("%s: never closed [%s]" % (name, stack[-1]))


def css_classes(path):
    """Class names a stylesheet defines - selector text only.

    Declaration blocks are stripped innermost-first so @media survives;
    otherwise every .5rem and url(...js) in a value would look like a class.
    """
    css = re.sub(r"/\*.*?\*/", " ", path.read_text(encoding="utf-8"), flags=re.S)
    while True:
        stripped = re.sub(r"\{[^{}]*\}", " ", css)
        if stripped == css:
            break
        css = stripped
    return set(re.findall(r"\.(-?[_a-zA-Z][_a-zA-Z0-9-]*)", css))


def used_classes(shortcode):
    """Classes a layout asks for: module_class="" on modules, class="" in HTML."""
    found = set()
    for match in CLASS_ATTR.finditer(shortcode):
        found.update(match.group(1).split())
    return found


def check_classes(name, shortcode, defined, where):
    missing = sorted(used_classes(shortcode) - defined)
    if missing:
        raise CheckFailed(
            "%s: %s does not define %s" % (name, where, ", ".join(missing))
        )


def vocabulary(shortcode):
    """Which module tags and which attribute names a layout uses."""
    tags, attrs = set(), set()
    for match in TAG.finditer(shortcode):
        tags.add(match.group(2))
        attrs.update(ATTR_NAME.findall(match.group(3)))
    return tags, attrs


def check_vocabulary(name, shortcode, known_tags, known_attrs):
    """Nothing invented.

    The whole-page layout is known to import into Divi 5.11. A section built
    only from tags and attributes that appear in it inherits that evidence -
    a made-up module or a misspelled attribute would not.
    """
    tags, attrs = vocabulary(shortcode)
    new_tags = sorted(tags - known_tags)
    new_attrs = sorted(attrs - known_attrs)
    if new_tags or new_attrs:
        raise CheckFailed(
            "%s: uses %s the whole-page layout does not - untested against Divi"
            % (name, " and ".join(
                ["tag(s) " + ", ".join(new_tags)] * bool(new_tags)
                + ["attribute(s) " + ", ".join(new_attrs)] * bool(new_attrs)
            ))
        )


def check_labels(parts):
    if len(parts) != len(PAGE_SECTIONS):
        raise CheckFailed(
            "source: expected %d sections, found %d"
            % (len(PAGE_SECTIONS), len(parts))
        )
    for part, (filename, expected) in zip(parts, PAGE_SECTIONS):
        match = ADMIN_LABEL.search(part)
        label = match.group(1) if match else ""
        if not label.startswith(expected):
            raise CheckFailed(
                "source: section for %s.json is labelled %r, expected it to start "
                "with %r - has the page been reordered?" % (filename, label, expected)
            )


# --------------------------------------------------------------------- build

def export(shortcode):
    """A standalone Divi portability export holding one section."""
    return {
        "context": "et_builder",
        "data": {"1": shortcode},
        "presets": {},
        "images": {},
        "thumbnails": [],
    }


def main():
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    page = source["data"]["1"]

    check_structure(SOURCE.name, page)
    parts = split_page(page)
    check_round_trip(parts, page)
    check_labels(parts)

    files = [(name, part) for (name, _), part in zip(PAGE_SECTIONS, parts)]
    files += [(name, build()) for name, build in EXTRA_SECTIONS]

    tod = css_classes(TOD_CSS)
    glue = css_classes(GLUE_CSS)
    known_tags, known_attrs = vocabulary(page)
    extra_names = {name for name, _ in EXTRA_SECTIONS}

    for name, shortcode in files:
        check_structure(name + ".json", shortcode)
        # The five authored ones must live entirely off tod.css: import one
        # into any night page, no CSS change, no rebuild.
        if name in extra_names:
            check_classes(name + ".json", shortcode, tod, "assets/css/tod.css")
            check_vocabulary(name + ".json", shortcode, known_tags, known_attrs)
        # The split ones may also use the Divi glue - .h-gallery-divi does.
        check_classes(name + ".json", shortcode, tod | glue,
                      "tod.css + divi-glue.css")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = set()
    for name, shortcode in files:
        path = OUT_DIR / (name + ".json")
        path.write_text(json.dumps(export(shortcode), ensure_ascii=False),
                        encoding="utf-8")
        written.add(path.name)
        kind = "spare " if name in extra_names else "page  "
        print("  %s %-18s %6d bytes" % (kind, path.name, len(shortcode)))

    stale = sorted(p.name for p in OUT_DIR.glob("*.json") if p.name not in written)
    if stale:
        print("\n  not generated by this script, delete if left over: %s"
              % ", ".join(stale))

    print("\n%d sections written to %s"
          % (len(files), OUT_DIR.relative_to(ROOT)))
    print("checks passed: round-trip byte for byte, tags balanced, "
          "nesting section > row > column > module, classes defined,\n"
          "               no module or attribute the whole-page layout does not use")


if __name__ == "__main__":
    try:
        main()
    except CheckFailed as failure:
        print("FAILED: %s" % failure, file=sys.stderr)
        print("nothing written.", file=sys.stderr)
        sys.exit(1)
