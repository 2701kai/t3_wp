#!/usr/bin/env python3
"""Generate divi/tod-pink-global-variables.json from assets/css/tod.css.

Divi 5 keeps its own design tokens - Global Variables - and they are what
the builder offers in its colour and font pickers. Our look does not run
through them: it rides on classes in tod.css, and importing this file
changes how nothing renders. What it changes is what Glitta is offered
when she reaches for a colour. Without it the picker hands her an
arbitrary wheel and every choice is one the night was not designed for.
With it she gets Sun, Ember, UV and Cream by name.

ONE-WAY. tod.css is the single source of truth. Regenerating overwrites
anything edited in Divi's variable UI, so edit the stylesheet and
re-import, never the other way round.

Every token in tod.css's :root must be listed in TOKENS below. A new one
fails the build until somebody classifies it - that is what keeps this a
derived artifact rather than a snapshot that quietly goes stale. Values
are never authored here; they are read from the stylesheet.

Import: wp-admin -> Divi -> Divi Library -> Import & Export, with
"Import Global Variables" checked.

Usage: python3 scripts/build-divi-variables.py
"""

import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOD_CSS = os.path.join(ROOT, "assets", "css", "tod.css")
OUT = os.path.join(ROOT, "divi", "tod-pink-global-variables.json")

# No git, no date: a pinned fallback keeps the build deterministic and
# offline-safe. Divi only reads lastUpdated as metadata.
FALLBACK_DATE = "2026-01-01T00:00:00+00:00"

# Every :root token in tod.css, and what Divi should make of it. "drop"
# carries the reason, which is printed in the report so a later run is
# not tempted to helpfully add it back.
COLOR, FONT, NUMBER = "colors", "fonts", "numbers"
RGB_TRIPLE = ("drop", "bare channel triple - exists so rgb(var(--x) / alpha) "
                      "can vary opacity, meaningless as a Divi number")
GRADIENT = ("drop", "gradient - Divi has no variable type for one "
                    "(colors, numbers, strings, fonts, images, links)")

TOKENS = {
    "--coal":            (COLOR,  "colors"),
    "--coal-2":          (COLOR,  "colors"),
    "--sun":             (COLOR,  "colors"),
    "--ember":           (COLOR,  "colors"),
    "--uvy":             (COLOR,  "colors"),
    "--acid":            (COLOR,  "colors"),
    "--teal":            (COLOR,  "colors"),
    "--wick":            (COLOR,  "colors"),
    "--cream":           (COLOR,  "colors"),
    "--cream-dim":       (COLOR,  "colors"),
    "--line-h":          (COLOR,  "colors"),
    "--bg-glow-a":       (COLOR,  "colors"),
    "--bg-glow-b":       (COLOR,  "colors"),
    "--finale-ink":      (COLOR,  "colors"),
    "--finale-ink-line": (COLOR,  "colors"),
    "--finale-sub":      (COLOR,  "colors"),
    "--river-ink":       (COLOR,  "colors"),

    "--font-display":    (FONT,   "fonts"),
    "--font-body":       (FONT,   "fonts"),
    "--font-mono":       (FONT,   "fonts"),

    "--step-0":          (NUMBER, "type"),
    "--step-1":          (NUMBER, "type"),
    "--step-2":          (NUMBER, "type"),
    "--step-3":          (NUMBER, "type"),
    "--pad":             (NUMBER, "layout"),
    "--measure":         (NUMBER, "layout"),

    "--sun-rgb":         RGB_TRIPLE,
    "--ember-rgb":       RGB_TRIPLE,
    "--uvy-rgb":         RGB_TRIPLE,
    "--acid-rgb":        RGB_TRIPLE,
    "--coal-rgb":        RGB_TRIPLE,
    "--raise-rgb":       RGB_TRIPLE,
    "--finale-grad":     GRADIENT,
    "--river-grad":      GRADIENT,
}

ROOT_KEYS = ["context", "data", "presets", "global_colors",
             "global_variables", "canvases", "images", "thumbnails"]


class Fail(Exception):
    pass


# --------------------------------------------------------------- reading

def read_tokens():
    """(name, value) for every custom property in tod.css's :root, in
    document order. Values come from here and nowhere else."""
    css = open(TOD_CSS, encoding="utf-8").read()
    block = re.search(r":root\s*\{(.*?)\n\}", css, re.S)
    if not block:
        raise Fail("tod.css: no :root block found")
    return [(n, " ".join(v.split()))
            for n, v in re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", block.group(1))]


def stamp():
    """When tod.css last changed, from git - deterministic across runs and
    across checkouts, unlike an mtime."""
    try:
        out = subprocess.run(
            ["git", "-C", ROOT, "log", "-1", "--format=%cI", "--",
             "assets/css/tod.css"],
            capture_output=True, text=True, timeout=10)
        return out.stdout.strip() or FALLBACK_DATE
    except (OSError, subprocess.SubprocessError):
        return FALLBACK_DATE


def slug(name):
    s = re.sub(r"[^a-z0-9]+", "-", name.lstrip("-").lower())
    return re.sub(r"-{2,}", "-", s).strip("-")


def label(name):
    return " ".join(w.capitalize() for w in slug(name).split("-"))


# --------------------------------------------------------------- building

def build(tokens, when):
    unknown = [n for n, _ in tokens if n not in TOKENS]
    if unknown:
        raise Fail("tod.css defines %d token(s) this script has never been "
                   "told about: %s. Add them to TOKENS - as a type or as a "
                   "drop with a reason - so the palette cannot drift."
                   % (len(unknown), ", ".join(unknown)))
    absent = [n for n in TOKENS if n not in {t for t, _ in tokens}]
    if absent:
        raise Fail("TOKENS lists %d token(s) tod.css no longer defines: %s"
                   % (len(absent), ", ".join(absent)))

    colors, variables, dropped = [], [], []
    seen = set()
    for name, value in tokens:
        kind, group = TOKENS[name]
        if kind == "drop":
            dropped.append((name, value, group))
            continue
        # Colours keep one id across both arrays - the picker and any
        # preset referencing them have to agree on it.
        vid = ("gcid-" if kind == COLOR else "gvid-") + slug(name)
        if vid in seen:
            raise Fail("id collision: %s" % vid)
        seen.add(vid)
        if kind == COLOR:
            colors.append([vid, {"color": value, "status": "active",
                                 "label": label(name)}])
        variables.append({
            "id": vid,
            "label": label(name),
            "value": value,
            "order": "",
            "status": "active",
            "lastUpdated": when,
            "variableType": kind,
            "type": kind,
            "groupKey": group,
        })

    payload = {"context": "et_builder", "data": [], "presets": [],
               "global_colors": colors, "global_variables": variables,
               "canvases": [], "images": [], "thumbnails": []}
    return payload, dropped


# ---------------------------------------------------------------- checks

def verify(payload, dropped, tokens):
    if list(payload.keys()) != ROOT_KEYS:
        raise Fail("root shape: keys are %s, Divi expects %s"
                   % (list(payload.keys()), ROOT_KEYS))
    if payload["context"] != "et_builder":
        raise Fail("root shape: context must be et_builder")
    for key in ("data", "presets", "canvases", "images", "thumbnails"):
        if payload[key] != []:
            raise Fail("root shape: %s must be an empty array in a Global "
                       "Variables file (a layout file differs - do not copy "
                       "its data:{} shape)" % key)

    source = dict(tokens)
    # Values are read, never authored: each one must still be byte-equal to
    # the declaration it came from.
    for entry in payload["global_variables"]:
        name = "--" + entry["id"].split("-", 1)[1]
        if name not in source:
            raise Fail("%s does not trace back to a tod.css token" % entry["id"])
        if entry["value"] != source[name]:
            raise Fail("%s is %r but tod.css says %r"
                       % (name, entry["value"], source[name]))

    emitted = {e["id"] for e in payload["global_variables"]}
    if len(emitted) != len(payload["global_variables"]):
        raise Fail("duplicate ids among global_variables")
    for cid, _ in payload["global_colors"]:
        if cid not in emitted:
            raise Fail("%s is in global_colors with no global_variables twin "
                       "- presets referencing it would not resolve" % cid)
        if not cid.startswith("gcid-"):
            raise Fail("%s: colours keep their gcid- id in both arrays" % cid)

    if len(payload["global_variables"]) + len(dropped) != len(tokens):
        raise Fail("accounting: %d emitted + %d dropped != %d tokens in tod.css"
                   % (len(payload["global_variables"]), len(dropped), len(tokens)))


def main():
    tokens = read_tokens()
    when = stamp()
    payload, dropped = build(tokens, when)
    verify(payload, dropped, tokens)

    # Deterministic or the file churns on every run and the diff stops
    # meaning anything.
    again, _ = build(tokens, when)
    if json.dumps(again, ensure_ascii=False) != json.dumps(payload, ensure_ascii=False):
        raise Fail("build is not deterministic")

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False))

    colors = len(payload["global_colors"])
    variables = len(payload["global_variables"])
    print("source     %s" % os.path.relpath(TOD_CSS, ROOT))
    print("written    %s" % os.path.relpath(OUT, ROOT))
    print("stamped    %s (tod.css last changed)" % when)
    print("emitted    %d variables - %d colours, %d fonts, %d numbers"
          % (variables, colors,
             sum(1 for e in payload["global_variables"] if e["type"] == FONT),
             sum(1 for e in payload["global_variables"] if e["type"] == NUMBER)))
    print("dropped    %d, on purpose:" % len(dropped))
    for name, value, reason in dropped:
        print("   %-14s %-34s %s" % (name, value[:34], reason))
    print("checks     every token classified, values byte-equal to tod.css,")
    print("           ids unique, every colour has its twin, root shape and")
    print("           empty-array types correct, build deterministic")
    print("import     Divi > Divi Library > Import & Export, with")
    print("           'Import Global Variables' checked")


if __name__ == "__main__":
    try:
        main()
    except Fail as failure:
        print("FAILED: %s" % failure, file=sys.stderr)
        print("nothing written.", file=sys.stderr)
        sys.exit(1)
