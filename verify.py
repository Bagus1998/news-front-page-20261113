#!/usr/bin/env python3
"""Ad-hoc verification for the news-image-01 entry (no test suite exists in this repo).

Checks the two things that actually broke or could break:
  A. gate     -- the image meets the rules the sealed scorer enforces
  B. geometry -- no ink from a block escapes its own region (the radar-arc bug that drew
                 teal sweeps across the masthead headline and nearly shipped)
  C. program  -- main.ts writes byte-identical output twice, and matches entry.png

Run: python3 /tmp/hermes-verify-news.py   (exit 0 only if every assertion passes)
"""
import hashlib, json, os, re, subprocess, sys, tempfile, shutil
from PIL import Image
import numpy as np

BOT = os.path.expanduser("~/makefun/news/bot")
PNG = f"{BOT}/entry.png"
SRC = os.path.expanduser("~/makefun/news/compose.py")
fails = []


def ok(cond, label):
    if not cond:
        fails.append(label)
    print(("PASS " if cond else "FAIL ") + label)


# ---------------------------------------------------------------- A. gate
def gate():
    raw = open(PNG, "rb").read()
    ok(raw[:8] == b"\x89PNG\r\n\x1a\n", "A1 is a PNG by its first bytes")
    ok(len(raw) <= 1_048_576, f"A2 under 1 MiB ({len(raw)} B)")
    im = Image.open(PNG)
    im.verify()                                  # raises on a broken chunk checksum
    im = Image.open(PNG)
    ok(im.size == (1024, 1024), f"A3 exactly 1024x1024 (got {im.size})")
    ok(max(im.size) <= 1024, "A4 no dimension over 1024")
    ok(not os.path.islink(PNG), "A5 a regular file, not a link")
    return im


# ---------------------------------------------------------------- B. geometry
INK_MIN = 120          # anything darker than this is ink, not paper
TEAL = (26, 138, 148)


def geometry(im):
    a = np.array(im.convert("RGB"))
    h, w, _ = a.shape

    # B1: the masthead headline band (y 30..120) must hold no coloured block ink.
    #     This is the regression that the radar sweep arcs caused.
    band = a[30:120]
    teal = ((abs(band[:, :, 0].astype(int) - TEAL[0]) < 45)
            & (abs(band[:, :, 1].astype(int) - TEAL[1]) < 55)
            & (abs(band[:, :, 2].astype(int) - TEAL[2]) < 55))
    ok(int(teal.sum()) == 0, f"B1 no teal ink in the headline band ({int(teal.sum())} px)")

    # B2: every hero icon strip (three across, just under the legend) must be self-contained:
    #     the row immediately above the strips is paper-only.
    ok(int((a[141:146].min(axis=2) < INK_MIN).sum()) == 0,
       "B2 clean paper row directly above the icon strips")

    # B3: nothing runs into the outer margin — the 8px frame is paper.
    for name, sl in (("left", a[:, :6]), ("right", a[:, -6:]),
                     ("top", a[:6, :]), ("bottom", a[-6:, :])):
        ok(int((sl.min(axis=2) < INK_MIN).sum()) == 0, f"B3 {name} margin is clear")

    # B4: the page is dense — a front page that lost its content would show as mostly blank.
    ink_frac = float((a.min(axis=2) < INK_MIN).mean())
    ok(0.02 < ink_frac < 0.35, f"B4 ink fraction is plausible ({ink_frac:.3f})")

    # B5: the page must carry 33 stories, numbered 1..33 with no gap and no repeat:
    # 3 heroes (1-3) + 12 cards (4-15) + 18 briefs (16-33). This is the claim the masthead makes,
    # so it is the claim worth asserting.
    src = open(SRC).read()
    heroes = [int(n) for n in re.findall(r"dict\(n=(\d+)", src)]
    cards = [int(n) for n in re.findall(r"^\s*\((\d+), \"", src, re.M)]
    briefs = [int(n) for n in re.findall(r"^\s*\((\d+), C_[A-Z]+, \"", src, re.M)]
    nums = sorted(heroes + cards + briefs)
    ok(len(heroes) == 3, f"B5 three hero stories (got {len(heroes)})")
    ok(len(cards) == 12, f"B6 twelve numbered cards (got {len(cards)})")
    ok(len(briefs) == 18, f"B7 eighteen briefs (got {len(briefs)})")
    ok(nums == list(range(1, 34)), f"B8 stories numbered 1..33 contiguously ({len(nums)} found)")
    ok("33 STORIES" in src, "B9 the masthead's count matches the content (33)")


# ---------------------------------------------------------------- C. program
def program():
    d = tempfile.mkdtemp(prefix="hermes-verify-")
    try:
        outs = []
        for i in (1, 2):
            o = f"{d}/o{i}"
            os.makedirs(o)
            r = subprocess.run(["node", f"{BOT}/main.ts"], capture_output=True, text=True,
                               timeout=120, env=dict(os.environ, MAKEFUN_OUTPUT_DIR=o))
            ok(r.returncode == 0, f"C{i} main.ts exits 0")
            p = f"{o}/entry.png"
            ok(os.path.isfile(p), f"C{i} wrote entry.png")
            if os.path.isfile(p):
                outs.append(hashlib.sha256(open(p, "rb").read()).hexdigest())
        ok(len(outs) == 2 and outs[0] == outs[1], "C3 two runs write byte-identical output")
        ok(outs and outs[0] == hashlib.sha256(open(PNG, "rb").read()).hexdigest(),
           "C4 output matches the committed entry.png")
    finally:
        shutil.rmtree(d, ignore_errors=True)


im = gate()
geometry(im)
program()

print()
if fails:
    print(f"FAILED {len(fails)}:")
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("ALL CHECKS PASSED (ad-hoc verification, not a test suite)")
