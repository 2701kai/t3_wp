#!/usr/bin/env python3
"""Convert g2.html into a Divi layout: divi/layouts/g2-record.json.

The point of this build is that Glitta can edit her own words, so the file
is cut in two:

  PROSE  -> plain Divi text modules. Hero copy, the five tracks, archive,
            CTA, footer. She clicks and types, like any other module.
  DECK   -> one [et_pb_code] module holding the SVG turntable, the
            transport button, the scoped CSS and the tonearm JS. That part
            is geometry and genuinely has to stay code.

The tonearm still drives the whole page because it finds its chapters with
a document-wide query. The chapters can therefore live in separate Divi
modules and the needle still follows them.

Transforms applied on the way, each one fixing a silent failure:

  1. English is baked into the markup. STRINGS, applyLang() and the
     language buttons are dropped. That is what makes the prose editable
     at all - previously every visible string was overwritten on load.
  2. CSS is scoped under .g2. The source has bare html/body/* rules that
     would otherwise escape into the whole WordPress document and fight
     tod.css and Divi's chrome.
  3. :root and [data-theme="pink"] both become .g2. Neither selector can
     match inside a code module - there is no <html> down there - so the
     tokens have to move to the scope root or every var() resolves to
     nothing.
  4. The script carries the same et_fb check functions.php applies to
     tod.js, widened past the query string. Without it the JS runs inside
     the Visual Builder and rewrites text while it is being edited.
  5. The tonearm anchors its chapter list to a class on the Divi MODULE
     (.g2-chapter), not to markup inside it. Glitta edits that markup;
     anything the editor reformats there must not be able to break the
     needle. Styling still hangs off the inner .track, so a mangled
     wrapper costs looks, never function.

Nothing is written unless verify() passes - see the checks there.

Usage: python3 scripts/build-g2-layout.py [path-or-url-to-g2.html]
"""

import json
import os
import re
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(HERE)
OUT = os.path.join(ROOT_DIR, "divi", "layouts", "g2-record.json")
DEFAULT_SRC = "https://glitta.rocks/g2.html"

BV = "4.27.4"
SCOPE = "g2"
CHAPTER = "g2-chapter"          # the JS hook, on the module, not in the prose

# Selectors that must become the scope root itself rather than a descendant
# of it. Everything else gets ".g2 " prefixed.
# NB: "*" is deliberately absent. It has its own branch in
# _scope_selector that expands it to ".g2, .g2 *"; listing it here would
# shadow that branch and collapse the universal reset onto the section
# alone, quietly leaving every descendant on content-box.
ROOT_SELECTORS = {":root", "html", "body", '[data-theme="pink"]',
                  'html[data-theme="pink"]', ":root, html"}

TAG = re.compile(r"\[(/?)(et_pb_[a-z0-9_]+)([^\]]*)\]")


class Fail(Exception):
    pass


def sub_once(text, old, new, what):
    """Replace, and refuse to continue if the source shape has moved.

    A replacement that silently matches nothing looks exactly like a
    replacement that worked.
    """
    if old not in text:
        raise Fail("could not apply %s - g2.html has changed shape" % what)
    return text.replace(old, new)


# ---------------------------------------------------------------- helpers

def load(src):
    if re.match(r"^https?://", src):
        with urllib.request.urlopen(src) as fh:
            return fh.read().decode("utf-8")
    with open(src, encoding="utf-8") as fh:
        return fh.read()


def strings_en(js):
    """Pull the en: {...} block out of the STRINGS object."""
    i = js.find("STRINGS")
    blk = js[i:]
    m = re.search(r"\ben\s*:\s*\{", blk)
    start = m.end() - 1
    depth = 0
    for j, ch in enumerate(blk[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                body = blk[start:j + 1]
                break
    out = {}
    for k, v in re.findall(r'(\w+)\s*:\s*"((?:[^"\\]|\\.)*)"', body):
        out[k] = v.replace('\\"', '"').replace("\\'", "'")
    return out


def scope_css(css, scope):
    """Prefix every rule with .scope, promoting root-level selectors.

    at-rules keep their prelude; only the selectors inside are rewritten.
    @keyframes bodies are left alone - their keys are percentages, not
    selectors.
    """
    out = []
    i = 0
    while i < len(css):
        # Whitespace first. Without this the loop only ever sees a comment
        # when one starts at the exact cursor, so every comment that
        # follows a rule gets swallowed into the NEXT selector - which
        # turned ":root{" into ".g2 /*...*/ :root{", a selector that can
        # never match, leaving every token undefined.
        m = re.match(r"\s+", css[i:])
        if m:
            out.append(m.group(0))
            i += m.end()
            continue
        # comment
        if css.startswith("/*", i):
            j = css.find("*/", i + 2)
            j = len(css) if j == -1 else j + 2
            out.append(css[i:j])
            i = j
            continue
        # at-rule
        m = re.match(r"@([a-zA-Z-]+)[^{;]*", css[i:])
        if m:
            name = m.group(1).lower()
            prelude = css[i:i + m.end()]
            k = i + m.end()
            if k < len(css) and css[k] == ";":       # @import, @charset
                out.append(prelude + ";")
                i = k + 1
                continue
            body, end = _block(css, k)
            if name in ("keyframes", "-webkit-keyframes", "font-face",
                        "property", "counter-style"):
                out.append(prelude + "{" + body + "}")
            else:                                     # @media, @supports
                out.append(prelude + "{" + scope_css(body, scope) + "}")
            i = end
            continue
        # ordinary rule
        brace = css.find("{", i)
        if brace == -1:
            out.append(css[i:])
            break
        sel = css[i:brace].strip()
        body, end = _block(css, brace)
        if sel:
            out.append(_scope_selector(sel, scope) + "{" + body + "}")
        i = end
    return "".join(out)


def _block(css, brace):
    """Return (inner_text, index_after_closing_brace)."""
    depth = 0
    for j in range(brace, len(css)):
        if css[j] == "{":
            depth += 1
        elif css[j] == "}":
            depth -= 1
            if depth == 0:
                return css[brace + 1:j], j + 1
    return css[brace + 1:], len(css)


def _scope_selector(sel, scope):
    parts = []
    for one in sel.split(","):
        one = one.strip()
        if not one:
            continue
        low = one.lower()
        if low in ROOT_SELECTORS:
            parts.append("." + scope)
        elif low == "*":
            parts.append(".%s, .%s *" % (scope, scope))
        # body.playing .platter -> .g2.playing .platter
        elif re.match(r"^(html|body)([.:\[#][^ >+~]*)?", low):
            m = re.match(r"^(html|body)([.:\[][^ >+~]*)?(.*)$", one, re.I)
            attach = m.group(2) or ""
            rest = m.group(3) or ""
            parts.append(("." + scope + attach + rest).rstrip())
        else:
            parts.append(".%s %s" % (scope, one))
    return ", ".join(parts)


def esc(s):
    """Divi stores module content inside shortcodes; a literal ] in text
    would close the tag early."""
    return s.replace("[", "&#91;").replace("]", "&#93;")


# ---------------------------------------------------------------- builders

def extract_element(html, needle):
    """Return the full element whose opening tag contains `needle`, matched
    by tag depth. A non-greedy regex cannot do this: the deck nests four
    divs and .*?</div></div> stops inside .label."""
    m = re.search(r"<(\w+)[^>]*%s[^>]*>" % re.escape(needle), html)
    if not m:
        raise Fail("could not find element containing %r" % needle)
    tag = m.group(1)
    depth = 0
    pos = m.start()
    for t in re.finditer(r"<(/?)%s\b[^>]*?(/?)>" % tag, html[m.start():], re.I):
        if t.group(2) == "/":                 # self-closing
            continue
        depth += -1 if t.group(1) else 1
        if depth == 0:
            return html[pos:pos + t.end()]
    raise Fail("unbalanced <%s> around %r" % (tag, needle))


def text(label, html, cls="tod-reveal"):
    c = ' module_class="%s"' % cls if cls else ""
    return '[et_pb_text%s admin_label="%s" _builder_version="%s"]%s[/et_pb_text]' % (
        c, label, BV, html)


def code(label, html):
    return '[et_pb_code admin_label="%s" _builder_version="%s"]%s[/et_pb_code]' % (
        label, BV, html)


def col(body, type_="4_4"):
    return ('[et_pb_column type="%s" _builder_version="%s"]%s[/et_pb_column]'
            % (type_, BV, body))


def row_cols(cols, label="", module_class=None):
    mc = ' module_class="%s"' % module_class if module_class else ""
    lbl = ' admin_label="%s"' % label if label else ""
    return ('[et_pb_row%s width="100%%" max_width="none"'
            ' custom_padding="0px||0px||true|false"%s _builder_version="%s"]%s'
            "[/et_pb_row]") % (mc, lbl, BV, "".join(cols))


def row(body, label=""):
    return row_cols([col(body)], label)


def tonearm_js(js, strings):
    """The geometry, with the i18n layer removed and the DOM contract
    moved onto things Glitta cannot edit away."""
    i = js.find("const PIVOT")
    arm = js[i:]
    arm = arm.split("window.setTimeout(function()")[0]   # LiteSpeed cookie line
    arm = arm.replace('applyLang("de");', "")
    arm = sub_once(
        arm,
        'playBtn.querySelector("[data-i18n]").textContent = playing ? '
        'STRINGS[lang].pause : STRINGS[lang].play;',
        'playBtn.querySelector(".label").textContent = playing ? %s : %s;'
        % (json.dumps(strings["pause"]), json.dumps(strings["play"])),
        "play-button label")
    # the playing class drives CSS that is now scoped under .g2
    arm = arm.replace("document.body.classList.add", "ROOT.classList.add")
    arm = arm.replace("document.body.classList.toggle", "ROOT.classList.toggle")

    # Chapters are found by the class on the Divi module. The inner .track
    # is only resolved for styling, and falls back to the module if the
    # editor ever eats it - a mangled wrapper must cost looks, not function.
    arm = sub_once(
        arm,
        'const tracks = [...document.querySelectorAll(".track")];',
        'const tracks = [...ROOT.querySelectorAll(".%s")]\n'
        '  .map(function(el){ return el.querySelector(".track") || el; });\n'
        'if (!tracks.length || !armGroup) return;' % CHAPTER,
        "chapter lookup")
    # everything else the deck owns lives inside the section: scope it there
    arm = sub_once(arm, 'const RINGS = [...document.querySelectorAll(".ring")]',
                   'const RINGS = [...ROOT.querySelectorAll(".ring")]',
                   "ring lookup")
    arm = sub_once(arm, 'const armGroup = document.getElementById("armGroup");',
                   'const armGroup = ROOT.querySelector("#armGroup");',
                   "arm group lookup")
    arm = arm.replace('document.querySelectorAll(".ring")',
                      'ROOT.querySelectorAll(".ring")')

    return (
        "(function(){\n"
        "/* Same rule functions.php applies to tod.js: stay out of the\n"
        "   Visual Builder, or this rewrites text while it is being edited.\n"
        "   functions.php tests two things, so this tests more than the\n"
        "   query string alone. */\n"
        "if (window.location.search.indexOf('et_fb=') !== -1) return;\n"
        "if (window.ET_Builder || window.ET_FB || window.et_fb_options) return;\n"
        "if (document.body && (document.body.classList.contains('et-fb')\n"
        "    || document.body.classList.contains('et-fb-iframe'))) return;\n"
        "var ROOT = document.querySelector('.%s');\n"
        "if (!ROOT) return;\n"
        "var playBtn = ROOT.querySelector('.play');\n"
        "if (!playBtn) return;\n"
        "%s\n})();" % (SCOPE, arm))


STAGE_ROW = "g2-stage-row"

# Transform 6. The source lays hero / list / deck out as ONE grid with named
# areas ("hero deck" / "list deck" at >=900px, deck sticky down the right).
# Divi wraps every module in row > column > module, so those three can never
# be siblings again and the grid loses its occupants - which is exactly how
# the first import rendered: a flat vertical stack. The two-column split is
# therefore Divi's (a 2_3 and a 1_3 column) and this block retires the grid
# and gives the deck the height chain position:sticky needs to travel in.
# Appended, never merged into the scoped source, same as the other five.
STAGE_OVERRIDE = """
/* ---------- transform 6: the stage, rebuilt on Divi's columns ---------- */
.SCOPE .stage{ display:block; }
.SCOPE .hero-copy, .SCOPE .stage-deck{ align-self:auto; }

/* Divi stacks its own columns at 980px; the source grid switched at 900.
   Those 80px were a band where our CSS thought "two columns" and Divi had
   already stacked them. The split now uses Divi's breakpoint, and the
   stacking below it is stated here rather than borrowed. */
@media(max-width:980px){
  .SCOPE .ROW > .et_pb_column{
    float:none !important;
    width:100% !important;
    margin:0 0 clamp(2rem,6vw,3rem) !important;
  }
}

@media(min-width:981px){
  .SCOPE .ROW{
    display:flex !important;
    align-items:stretch !important;
    gap:clamp(2rem,5vw,4.5rem);
  }
  .SCOPE .ROW > .et_pb_column{
    float:none !important;
    width:auto !important;
    margin:0 !important;
  }
  .SCOPE .ROW > .et_pb_column_2_3{ flex:1 1 0; min-width:0; }
  .SCOPE .ROW > .et_pb_column_1_3{ flex:0 0 clamp(300px,30%,420px); }
  /* Sticky needs every ancestor between the column and .deck-inner to
     carry height, or the needle has nowhere to travel. The column itself
     is deliberately NOT in this list: an explicit height on a flex item
     beats align-items:stretch, and the column then collapses to its own
     content - measured 599px against the prose column's 1619px, which is
     exactly no travel at all. Let flex stretch it, size the rest. */
  .SCOPE .ROW .et_pb_code,
  .SCOPE .ROW .et_pb_code_inner,
  .SCOPE .ROW .stage,
  .SCOPE .ROW .stage-deck{ height:100%; }
}
"""


# Transform 8. The source wraps every region in <div class="wrap"> - the
# 1180px measure, the centring margin and the rail padding - and each half
# of the tracklist in <section class="side">, whose top padding is the air
# above the heading. Divi builds row > column > module itself, so neither
# element is ever emitted and those declarations go looking for markup that
# does not exist. The rows are explicitly full-bleed (the module settings
# emit width:100% !important and max-width:none !important), so without this
# the prose runs the whole width of the viewport and touches both edges.
# Re-aim the two containers at the wrappers Divi does build.
CONTAINER_OVERRIDE = """
/* ---------- transform 8: .wrap and .side lost their elements ---------- */
.SCOPE .et_pb_row{
  max-width:1180px !important;
  margin-inline:auto !important;
  padding-inline:var(--rail);
}
.SCOPE .side-head-wrap{ padding-block:clamp(1.6rem,4vw,2.6rem) 0; }
"""

# Classes the layout deliberately does not carry. Each is a decision, and
# the orphan check below has to be able to tell a decision from an oversight.
DROPPED = {
    "back", "langs", "topbar",   # the language bar went with the i18n layer
    "strip", "tile",             # the archive ships as a heading, no tiles yet
    "list",                      # only ever carried grid-area; grid retired
    "button",                    # the CTA uses the theme's .h-btn instead
}
# Added by the tonearm at runtime, so never present in the emitted markup.
RUNTIME = {"playing", "live", "on"}
# Re-homed onto Divi's own wrappers by transform 8 above.
REAIMED = {"wrap", "side"}
# Wrappers Divi itself builds around every module.
DIVI_BUILT = {"et_pb_row", "et_pb_column", "et_pb_column_2_3",
              "et_pb_column_1_3", "et_pb_code", "et_pb_code_inner",
              "et_pb_text"}


def build(html):
    js = "\n".join(re.findall(r"<script[^>]*>(.*?)</script>", html, re.S))
    css = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", html, re.S))
    body = re.search(r"<body[^>]*>(.*?)</body>", html, re.S).group(1)
    S = strings_en(js)

    deck_html = extract_element(body, 'class="stage-deck"')
    guard = tonearm_js(js, S)

    # Transform 7. The source loads Unbounded / Work Sans / Space Mono from
    # Google Fonts with <link> tags in <head>. Only <style> and <script> were
    # being lifted, so every font fell through to system-ui - the first
    # import rendered the whole page in the wrong typeface. @import rides
    # inside the style block, which the importer is now proven to preserve,
    # and must precede every other rule.
    m = re.search(r'<link[^>]+href="(https://fonts\.googleapis\.com/css2\?[^"]+)"', html)
    if not m:
        raise Fail("could not find the Google Fonts link - g2.html has changed shape")
    font_url = m.group(1).replace("&amp;", "&")

    override = ((STAGE_OVERRIDE + CONTAINER_OVERRIDE)
                .replace(".SCOPE", "." + SCOPE)
                .replace(".ROW", "." + STAGE_ROW))
    style = ('<style>\n@import url("%s");\n%s\n%s</style>'
             % (font_url, scope_css(css, SCOPE), override))

    transport = (
        '<div class="transport">'
        '<button class="play" type="button" aria-pressed="true">'
        '<span class="icon"></span><span class="label">%s</span></button>'
        '<span class="rpm">%s</span></div>' % (esc(S["pause"]), esc(S["rpm"])))

    hero = text("Hero copy - click and write over it",
                '<header class="hero-copy">'
                '<p class="eyebrow">%s</p><h1>Gitta</h1>'
                '<p class="tagline">%s</p><p class="intro">%s</p></header>'
                % (esc(S["eyebrow"]), esc(S["tagline"]), esc(S["intro"])))

    deck_module = code(
        "Turntable + tonearm - leave as is (geometry, not content)",
        style + '<div class="stage">' + transport + deck_html + "</div>"
        + "<script>" + guard + "</script>")

    def side(letter, note, indices):
        head = ('<div class="side-head"><h2>%s</h2>'
                '<span class="note">%s</span></div>'
                % (esc(S["side" + letter]), esc(note)))
        mods = [text("Side %s heading" % letter,
                     '<div class="side-head-wrap">%s</div>' % head)]
        for n in indices:
            mods.append(text(
                "Track %d - %s (keep the %s class)" % (n, S["t%dtitle" % n], CHAPTER),
                '<article class="track" data-track="%d">'
                '<span class="no">%02d</span><h3>%s</h3>'
                '<p class="where">%s</p><p class="body">%s</p></article>'
                % (n, n + 1, esc(S["t%dtitle" % n]),
                   esc(S["t%dwhere" % n]), esc(S["t%dbody" % n])),
                cls="tod-reveal " + CHAPTER))
        return "".join(mods)

    archive = text("Archive",
                   '<section class="archive"><p class="eyebrow">%s</p>'
                   '<div class="archive-head"><h2>%s</h2><p>%s</p></div>'
                   "</section>"
                   % (esc(S["archiveEyebrow"]), esc(S["archiveTitle"]),
                      esc(S["archiveNote"])))

    cta = text("Booking CTA",
               '<section class="cta"><p class="eyebrow">%s</p><h2>%s</h2>'
               '<p>%s</p><p><a class="h-btn" href="mailto:booking@glitta.rocks">'
               "%s</a></p></section>"
               % (esc(S["ctaEyebrow"]), esc(S["ctaTitle"]),
                  esc(S["ctaText"]), esc(S["ctaButton"])))

    footer = text("Footer note",
                  '<footer><span class="note">%s</span></footer>'
                  % esc(S["footerNote"]))

    # One row, two columns: the prose column and the deck column. This is
    # the grid the source drew, expressed in the only vocabulary that
    # survives Divi's wrappers.
    prose = (hero
             + side("A", S["sideANote"], [0, 1, 2])
             + side("B", S["sideBNote"], [3, 4]))
    inner = (row_cols([col(prose, "2_3"), col(deck_module, "1_3")],
                      "The record - prose left, deck right",
                      module_class=STAGE_ROW)
             + row(archive + cta + footer, "Archive, booking, footer"))

    return ('[et_pb_section fb_built="1" module_class="%s" module_id="g2"'
            ' background_enable_color="off"'
            ' custom_padding="0px||0px||true|false"'
            ' admin_label="Gitta - the record" _builder_version="%s"]'
            "%s[/et_pb_section]") % (SCOPE, BV, inner)


# ----------------------------------------------------------------- checks

def css_rules(css):
    """(selector, body) for every rule, brace-depth aware.

    Comments are stripped from the selector text - a naive walker hands
    back the comment sitting in front of a rule as part of its selector,
    and a comma inside that comment then looks like a second selector.
    Recurses into @media/@supports so rules inside a breakpoint are
    checked too; @keyframes keys are not selectors and are skipped.
    """
    # Comments go first, for the whole stylesheet. Leaving them in means a
    # semicolon inside prose reads as the end of an @import, and a comma
    # inside prose reads as a second selector - both have now cost a build.
    css = re.sub(r"/\*.*?\*/", " ", css, flags=re.S)
    out, i = [], 0
    while True:
        b = css.find("{", i)
        if b == -1:
            return out
        # A statement at-rule (@import, @charset) ends at ';' with no block.
        # Without consuming it here it merges into the next selector, the
        # same way a comment used to - and the rule it swallows stops
        # counting, which reads as "every token undefined".
        semi = css.find(";", i)
        if semi != -1 and semi < b:
            i = semi + 1
            continue
        sel = css[i:b].strip()
        depth, j = 0, b
        while j < len(css):
            if css[j] == "{":
                depth += 1
            elif css[j] == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        body = css[b + 1:j]
        if sel.startswith("@"):
            if sel[1:].split(" ")[0].split("(")[0].lower() in (
                    "media", "supports", "layer", "container"):
                out.extend(css_rules(body))
        elif sel:
            out.append((sel, body))
        i = j + 1


def verify(shortcode, expect):
    css = re.search(r"<style>(.*?)</style>", shortcode, re.S).group(1)
    js = re.search(r"<script>(.*?)</script>", shortcode, re.S).group(1)

    # --- tags balanced, and nested the way Divi needs -------------------
    stack = []
    for m in TAG.finditer(shortcode):
        closing, tag = m.group(1), m.group(2)
        if closing:
            if not stack or stack[-1] != tag:
                raise Fail("tags: [/%s] does not close the open tag" % tag)
            stack.pop()
            continue
        parent = stack[-1] if stack else None
        ok = {None: tag == "et_pb_section",
              "et_pb_section": tag == "et_pb_row",
              "et_pb_row": tag == "et_pb_column",
              "et_pb_column": tag not in ("et_pb_section", "et_pb_row",
                                          "et_pb_column")}.get(parent, False)
        if not ok:
            raise Fail("nesting: [%s] inside [%s] - a row inside a column is "
                       "dropped by Divi silently" % (tag, parent or "nothing"))
        stack.append(tag)
    if stack:
        raise Fail("tags: never closed [%s]" % stack[-1])

    # --- every selector is inside the scope, and can actually match ----
    parts, defined = [], set()
    for sel, body in css_rules(css):
        for one in sel.split(","):
            one = " ".join(one.split())
            if not one:
                continue
            parts.append(one)
            if not re.match(r"^\.%s(?![\w-])" % SCOPE, one):
                raise Fail("css: %r escapes the .%s scope and would style the "
                           "whole WordPress document" % (one[:70], SCOPE))
            # Inside a code module there is no <html>, so neither of these
            # can ever match. A rule that cannot match defines nothing.
            if ":root" in one or re.search(r"(?<![\w.-])html(?![\w-])", one):
                raise Fail("css: %r can never match inside a code module - "
                           "promote it to .%s" % (one[:70], SCOPE))
        defined |= set(re.findall(r"(--[\w-]+)\s*:", body))

    if expect["universal"] and ".%s *" % SCOPE not in parts:
        raise Fail("css: the universal reset did not survive scoping - "
                   "without a plain '.%s *' every descendant drops back to "
                   "content-box" % SCOPE)

    missing = sorted(set(re.findall(r"var\((--[\w-]+)", css)) - defined)
    if missing:
        raise Fail("css: %d token(s) referenced but never defined: %s"
                   % (len(missing), ", ".join(missing)))

    # --- the i18n layer is gone, or the prose is not editable ----------
    for needle in ("STRINGS", "applyLang", "data-i18n"):
        if needle in shortcode:
            raise Fail("i18n: %r survived - text modules would be overwritten "
                       "on load" % needle)
    if "_lcp3" in shortcode:
        raise Fail("a cache-plugin cookie line survived into the layout")

    # --- the builder guard --------------------------------------------
    if "et_fb=" not in js or "ET_Builder" not in js:
        raise Fail("guard: the et_fb check is missing or narrower than the "
                   "one functions.php applies to tod.js")

    # --- the fonts come with the page ----------------------------------
    first = re.sub(r"^\s+", "", css)
    if not first.startswith("@import"):
        raise Fail("css: @import for the webfonts must be the first rule, or "
                   "the browser drops it and every font falls back")
    if "fonts.googleapis.com" not in css:
        raise Fail("css: the Google Fonts import is missing - the page would "
                   "render in system-ui")

    # --- the stage is two columns, deck in the narrow one ----------------
    stage = re.search(r'\[et_pb_row[^\]]*module_class="[^"]*\b%s\b[^\]]*\](.*?)\[/et_pb_row\]'
                      % STAGE_ROW, shortcode, re.S)
    if not stage:
        raise Fail("layout: no row carries %s - the two-column stage is gone "
                   "and the page would stack flat, as the first import did"
                   % STAGE_ROW)
    types = re.findall(r'\[et_pb_column type="([^"]+)"', stage.group(1))
    if types != ["2_3", "1_3"]:
        raise Fail("layout: stage row columns are %s, expected ['2_3', '1_3']"
                   % types)
    deck_col = stage.group(1).split('[et_pb_column type="1_3"')[1]
    if "[et_pb_code" not in deck_col:
        raise Fail("layout: the deck module is not in the 1_3 column")
    if "transform 6" not in css:
        raise Fail("css: the stage override block is missing - Divi's floated "
                   "columns would win and sticky would have no height chain")
    if "transform 8" not in css:
        raise Fail("css: the container override is missing - the rows are "
                   "full-bleed, so the prose would span the whole viewport")

    # --- every scoped rule still has markup to land on -----------------
    # Splitting one page across Divi modules silently orphans any rule whose
    # element was a container the source drew and Divi does not. Nothing
    # errors: the rule ships, matches nothing, and the layout is quietly
    # wrong. That is how .wrap took the page's measure and rail padding with
    # it. Every class a rule targets must therefore be accounted for - in the
    # markup, built by Divi, added at runtime, or listed above as a decision.
    markup = re.sub(r"<style>.*?</style>|<script>.*?</script>", "",
                    shortcode, flags=re.S)
    present = set()
    for group in re.findall(r'(?:module_)?class="([^"]+)"', markup):
        present |= set(group.split())
    known = present | DIVI_BUILT | RUNTIME | REAIMED | DROPPED
    orphans = set()
    for sel, _ in css_rules(css):
        for one in sel.split(","):
            orphans |= {c for c in re.findall(r"\.([A-Za-z][\w-]*)", one)
                        if c not in known}
    if orphans:
        raise Fail("css: %d rule target(s) match no element in the layout: %s"
                   " - either the markup that carried them was dropped, or a "
                   "container the source drew is one Divi does not build. Give"
                   " each one a home or list it as a decision."
                   % (len(orphans), ", ".join(sorted(orphans))))

    # --- the JS contract holds ----------------------------------------
    chapters = len(re.findall(r'module_class="[^"]*\b%s\b' % CHAPTER, shortcode))
    rings = len(re.findall(r"data-ring", shortcode))
    if chapters != 5 or rings != 5:
        raise Fail("deck: %d chapter modules against %d rings - the tonearm "
                   "maps one ring per chapter" % (chapters, rings))
    if ".%s" % CHAPTER not in js:
        raise Fail("deck: the JS does not look for .%s, so the chapter list "
                   "would depend on markup Glitta edits" % CHAPTER)
    for stray in ('document.querySelectorAll(".track")',
                  'document.querySelectorAll(".ring")',
                  'document.getElementById("armGroup")'):
        if stray in js:
            raise Fail("deck: %s is unscoped - it should query inside ROOT" % stray)
    return {"chapters": chapters, "rings": rings, "css": len(css), "js": len(js)}


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SRC
    html = load(src)
    shortcode = build(html)
    src_css = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", html, re.S))
    stats = verify(shortcode, {
        "universal": bool(re.search(r"(?:^|\})\s*\*[,{]", src_css, re.M)),
    })

    payload = {"context": "et_builder", "data": {"1": shortcode},
               "presets": {}, "images": {}, "thumbnails": []}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False))

    print("source     %s" % src)
    print("written    %s" % os.path.relpath(OUT, ROOT_DIR))
    print("shortcode  %d chars (css %d, js %d)"
          % (len(shortcode), stats["css"], stats["js"]))
    print("text mods  %d  (%d of them chapters)"
          % (shortcode.count("[et_pb_text"), stats["chapters"]))
    print("code mods  %d" % shortcode.count("[et_pb_code"))
    print("checks     scope clean (incl. @media), every token defined,")
    print("           universal reset intact, tags balanced,")
    print("           nesting section > row > column > module, i18n gone,")
    print("           builder guard present, chapter list off the module class,")
    print("           every scoped rule still has an element to match")


if __name__ == "__main__":
    try:
        main()
    except Fail as failure:
        print("FAILED: %s" % failure, file=sys.stderr)
        print("nothing written.", file=sys.stderr)
        sys.exit(1)
