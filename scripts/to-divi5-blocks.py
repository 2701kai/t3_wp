#!/usr/bin/env python3
"""Turn the generated Divi 4 shortcode layout into Divi 5 block markup.

Why this exists: glitta.rocks runs Divi 5.11.0, and page g2 has already been
opened and saved in the Visual Builder, which converted it to the serialized
block format. Re-importing the shortcode layout would push that page back
into Divi's backward-compatibility layer - working, but legacy, and without
the Divi 5 editing experience that is the whole point of converting at all.

So the shortcode tree is the intermediate representation and this is the
real emitter. It only has to understand the vocabulary build-g2-layout.py
emits - section, row, column, text, code - which is machine-generated and
therefore regular.

The format, verified against live content on the install:

  <!-- wp:divi/placeholder -->
    <!-- wp:divi/section {...} -->
      <!-- wp:divi/row {...} -->
        <!-- wp:divi/column {...} -->
          <!-- wp:divi/text {...} /-->
        <!-- /wp:divi/column -->
      <!-- /wp:divi/row -->
    <!-- /wp:divi/section -->
  <!-- /wp:divi/placeholder -->

Every attribute value is breakpoint-keyed: never a bare value, always
{"desktop": {"value": ...}}.

Usage: python3 scripts/to-divi5-blocks.py [out.txt]
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LAYOUT = os.path.join(ROOT, "divi", "layouts", "g2-record.json")
OUT = os.path.join(ROOT, "divi", "layouts", "g2-page.blocks.txt")

BUILDER_VERSION = "5.11.0"

# Content lives in a JSON string that is itself inside an HTML comment, so it
# is escaped twice over. These five are the ones that would break out of one
# or the other. Sentinels keep the substitution away from JSON's own quotes:
# replacing '"' after json.dumps would eat the structural quotes too.
ESCAPES = [
    ("&", "\\u0026"),      # first - later replacements introduce no &
    ("<", "\\u003c"),
    (">", "\\u003e"),
    ('"', "\\u0022"),
    ("--", "\\u002d\\u002d"),   # a bare -- would terminate the comment
]
TAG = re.compile(r"\[(/?)(et_pb_[a-z_]+)([^\]]*)\]")
ATTR = re.compile(r'(\w+)="([^"]*)"')


def dumps(attrs, content):
    """Serialize one block's attributes, escaping the content correctly.

    The sentinels come from the Unicode private use area, and that is
    load-bearing. Control characters look like the obvious choice and are
    wrong: json.dumps escapes them to \\u0001 whatever ensure_ascii says,
    so the substitution afterwards finds nothing and the raw sentinel ships
    inside the content. Private use characters are passed through verbatim.
    """
    sentinels = {}
    if content is not None:
        text = content
        for i, (raw, esc) in enumerate(ESCAPES):
            token = chr(0xE000 + i)
            if token in text:
                raise SystemExit("sentinel U+%04X occurs in the content"
                                 % (0xE000 + i))
            sentinels[token] = esc
            text = text.replace(raw, token)
        attrs = dict(attrs)
        attrs["content"] = {"innerContent": {"desktop": {"value": text}}}
    out = json.dumps(attrs, ensure_ascii=False, separators=(",", ":"))
    for token, esc in sentinels.items():
        out = out.replace(token, esc)
    return out


def responsive(value):
    return {"desktop": {"value": value}}


def module_attrs(sc_attrs, extra_advanced=None):
    """Map the shortcode attributes we emit onto their Divi 5 JSON paths."""
    module = {}
    if sc_attrs.get("admin_label"):
        module.setdefault("meta", {})["adminLabel"] = responsive(
            sc_attrs["admin_label"])

    advanced = dict(extra_advanced or {})
    css_class = sc_attrs.get("module_class", "")
    css_id = sc_attrs.get("module_id", "")
    if css_class or css_id:
        advanced["htmlAttributes"] = responsive(
            {"class": css_class, "id": css_id})
    if advanced:
        module["advanced"] = advanced

    decoration = {}
    if sc_attrs.get("background_enable_color"):
        decoration["background"] = responsive(
            {"enableColor": sc_attrs["background_enable_color"], "color": ""})
    if sc_attrs.get("custom_padding"):
        # "0px||0px||true|false" -> top|right|bottom|left|syncV|syncH
        p = (sc_attrs["custom_padding"].split("|") + [""] * 6)[:6]
        decoration["spacing"] = responsive({"padding": {
            "top": p[0], "right": p[1], "bottom": p[2], "left": p[3],
            "syncVertical": "on" if p[4] == "true" else "off",
            "syncHorizontal": "on" if p[5] == "true" else "off"}})
    if decoration:
        module["decoration"] = decoration

    attrs = {}
    if module:
        attrs["module"] = module
    attrs["builderVersion"] = BUILDER_VERSION
    return attrs


def parse(shortcode):
    """Shortcode string -> nested [{tag, attrs, content, children}]."""
    root, stack, pos = [], [], 0
    for m in TAG.finditer(shortcode):
        text = shortcode[pos:m.start()]
        if text.strip() and stack:
            stack[-1]["content"] = (stack[-1].get("content") or "") + text
        pos = m.end()
        closing, tag, raw = m.group(1), m.group(2), m.group(3)
        if closing:
            node = stack.pop()
            if node["tag"] != tag:
                raise SystemExit("unbalanced: [/%s] closes [%s]" % (tag, node["tag"]))
            continue
        node = {"tag": tag, "attrs": dict(ATTR.findall(raw)),
                "content": None, "children": []}
        (stack[-1]["children"] if stack else root).append(node)
        stack.append(node)
    if stack:
        raise SystemExit("unclosed [%s]" % stack[-1]["tag"])
    return root


NAME = {"et_pb_section": "section", "et_pb_row": "row",
        "et_pb_column": "column", "et_pb_text": "text",
        "et_pb_code": "code"}


def render(node, depth=1):
    block = NAME.get(node["tag"])
    if not block:
        raise SystemExit("no Divi 5 block for [%s]" % node["tag"])
    pad = "  " * depth
    extra = None
    if block == "column":
        extra = {"type": responsive(node["attrs"].get("type", "4_4"))}
    attrs = module_attrs(node["attrs"], extra)

    if node["children"]:
        out = ["%s<!-- wp:divi/%s %s -->" % (pad, block, dumps(attrs, None))]
        for child in node["children"]:
            out.append(render(child, depth + 1))
        out.append("%s<!-- /wp:divi/%s -->" % (pad, block))
        return "\n".join(out)
    return "%s<!-- wp:divi/%s %s /-->" % (
        pad, block, dumps(attrs, node["content"] or ""))


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else OUT
    shortcode = list(json.load(open(LAYOUT, encoding="utf-8"))["data"].values())[0]
    tree = parse(shortcode)

    body = "\n".join(render(n) for n in tree)
    content = "<!-- wp:divi/placeholder -->\n%s\n<!-- /wp:divi/placeholder -->" % body

    # This has to survive a round trip, so check the shape before writing.
    tags = re.findall(r"<!-- (/?)wp:divi/\w+.*?(/?)-->", content)
    closes = sum(1 for c, _ in tags if c)
    selfclosed = sum(1 for c, sc in tags if not c and sc)
    opens = sum(1 for c, sc in tags if not c and not sc)
    if opens != closes:
        raise SystemExit("delimiters unbalanced: %d open against %d close"
                         % (opens, closes))
    # Each delimiter's payload must be valid JSON on its own - \u003c and
    # friends are legal JSON escapes, so no un-escaping is needed to check.
    for raw in re.findall(r"<!-- wp:divi/\w+ (\{.*?\}) /?-->", content):
        json.loads(raw)
    # And nothing may have broken out of its comment: every "-->" in the file
    # should be a delimiter of ours, none of them content that got loose.
    if content.count("-->") != opens + closes + selfclosed:
        raise SystemExit("a '-->' escaped into content - the -- rule failed")

    # Decode every leaf back and require the original HTML, byte for byte.
    # The escaping is the one part of this with no visible failure mode: a
    # leaked sentinel renders as stray digits in the middle of the markup and
    # nothing anywhere reports an error. It shipped once already.
    for name, raw in re.findall(r"<!-- wp:divi/(\w+) (\{.*?\}) /-->", content):
        html = json.loads(raw)["content"]["innerContent"]["desktop"]["value"]
        for token in range(0xE000, 0xE000 + len(ESCAPES)):
            if chr(token) in html:
                raise SystemExit("sentinel U+%04X leaked into a %s block"
                                 % (token, name))
        if html and html not in shortcode:
            raise SystemExit("a %s block does not decode to its source HTML"
                             % name)

    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(content)

    print("layout     %s" % os.path.relpath(LAYOUT, ROOT))
    print("written    %s" % os.path.relpath(out_path, ROOT))
    print("blocks     %d containers, %d leaves" % (closes, selfclosed))
    print("chars      %d" % len(content))
    for b in ("section", "row", "column", "text", "code"):
        print("  divi/%-8s %d" % (b, content.count("wp:divi/%s " % b)))


if __name__ == "__main__":
    main()
