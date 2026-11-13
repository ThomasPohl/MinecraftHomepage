#!/usr/bin/env python3
"""Erzeugt die eigenen Grafiken und die eigene Pixel-Schrift der Seite.

Alles hier ist selbst gezeichnet (keine Mojang-Assets, keine fremden Fonts).
Aufruf:  python3 tools/make_assets.py   (benötigt fontTools)
Ausgabe: site/fonts/blockschrift.woff, site/img/*.svg
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "site"

# --------------------------------------------------------------------------
# 1) Pixel-Schrift "Blockschrift" (5x7 Raster, nur Grossbuchstaben)
# --------------------------------------------------------------------------
GLYPHS = {
    "A": ".###. #...# #...# ##### #...# #...# #...#",
    "B": "####. #...# #...# ####. #...# #...# ####.",
    "C": ".###. #...# #.... #.... #.... #...# .###.",
    "D": "####. #...# #...# #...# #...# #...# ####.",
    "E": "##### #.... #.... ####. #.... #.... #####",
    "F": "##### #.... #.... ####. #.... #.... #....",
    "G": ".###. #...# #.... #.### #...# #...# .###.",
    "H": "#...# #...# #...# ##### #...# #...# #...#",
    "I": ".###. ..#.. ..#.. ..#.. ..#.. ..#.. .###.",
    "J": "..### ...#. ...#. ...#. ...#. #..#. .##..",
    "K": "#...# #..#. #.#.. ##... #.#.. #..#. #...#",
    "L": "#.... #.... #.... #.... #.... #.... #####",
    "M": "#...# ##.## #.#.# #.#.# #...# #...# #...#",
    "N": "#...# ##..# #.#.# #..## #...# #...# #...#",
    "O": ".###. #...# #...# #...# #...# #...# .###.",
    "P": "####. #...# #...# ####. #.... #.... #....",
    "Q": ".###. #...# #...# #...# #.#.# #..#. .##.#",
    "R": "####. #...# #...# ####. #.#.. #..#. #...#",
    "S": ".#### #.... #.... .###. ....# ....# ####.",
    "T": "##### ..#.. ..#.. ..#.. ..#.. ..#.. ..#..",
    "U": "#...# #...# #...# #...# #...# #...# .###.",
    "V": "#...# #...# #...# #...# #...# .#.#. ..#..",
    "W": "#...# #...# #...# #.#.# #.#.# ##.## #...#",
    "X": "#...# #...# .#.#. ..#.. .#.#. #...# #...#",
    "Y": "#...# #...# .#.#. ..#.. ..#.. ..#.. ..#..",
    "Z": "##### ....# ...#. ..#.. .#... #.... #####",
    "Ä": "#...# ..... .###. #...# ##### #...# #...#",
    "Ö": "#...# ..... .###. #...# #...# #...# .###.",
    "Ü": "#...# ..... #...# #...# #...# #...# .###.",
    "0": ".###. #...# #..## #.#.# ##..# #...# .###.",
    "1": "..#.. .##.. ..#.. ..#.. ..#.. ..#.. .###.",
    "2": ".###. #...# ....# ...#. ..#.. .#... #####",
    "3": "####. ....# ....# .###. ....# ....# ####.",
    "4": "...#. ..##. .#.#. #..#. ##### ...#. ...#.",
    "5": "##### #.... ####. ....# ....# #...# .###.",
    "6": ".###. #.... #.... ####. #...# #...# .###.",
    "7": "##### ....# ...#. ..#.. ..#.. ..#.. ..#..",
    "8": ".###. #...# #...# .###. #...# #...# .###.",
    "9": ".###. #...# #...# .#### ....# ....# .###.",
    " ": "..... ..... ..... ..... ..... ..... .....",
    ".": "..... ..... ..... ..... ..... .##.. .##..",
    ",": "..... ..... ..... ..... .##.. .##.. .#...",
    ":": "..... .##.. .##.. ..... .##.. .##.. .....",
    "!": "..#.. ..#.. ..#.. ..#.. ..#.. ..... ..#..",
    "?": ".###. #...# ....# ...#. ..#.. ..... ..#..",
    "-": "..... ..... ..... ####. ..... ..... .....",
    "+": "..... ..#.. ..#.. ##### ..#.. ..#.. .....",
    "/": "....# ....# ...#. ..#.. .#... #.... #....",
    "'": "..#.. ..#.. .#... ..... ..... ..... .....",
    "(": "...#. ..#.. .#... .#... .#... ..#.. ...#.",
    ")": ".#... ..#.. ...#. ...#. ...#. ..#.. .#...",
    "&": ".##.. #..#. #.#.. .#... #.#.# #..#. .##.#",
    "<": "...#. ..#.. .#... #.... .#... ..#.. ...#.",
    ">": ".#... ..#.. ...#. ....# ...#. ..#.. .#...",
    "_": "..... ..... ..... ..... ..... ..... #####",
    "*": "..... #.#.# .###. ##### .###. #.#.# .....",
    "@": ".###. #...# #.### #.#.# #.### #.... .###.",
}
ALIASES = {"’": "'", "–": "-", "—": "-", "ẞ": "S"}

PX = 100          # Einheiten pro Pixel
ADV = 6 * PX      # 5 Pixel + 1 Abstand


def build_font():
    from fontTools.fontBuilder import FontBuilder
    from fontTools.pens.ttGlyphPen import TTGlyphPen

    def draw(rows):
        pen = TTGlyphPen(None)
        for r, row in enumerate(rows):
            c = 0
            while c < 5:
                if row[c] != "#":
                    c += 1
                    continue
                start = c
                while c < 5 and row[c] == "#":
                    c += 1
                x0, x1 = start * PX, c * PX
                y1 = (7 - r) * PX
                y0 = y1 - PX
                # leicht nach unten ueberlappen -> keine Haarlinien zwischen Zeilen
                below = r + 1 < 7 and any(rows[r + 1][i] == "#" for i in range(start, c))
                if below:
                    y0 -= 12
                pen.moveTo((x0, y0)); pen.lineTo((x0, y1))
                pen.lineTo((x1, y1)); pen.lineTo((x1, y0)); pen.closePath()
        return pen.glyph()

    names, glyphs, cmap, metrics = [".notdef"], {}, {}, {}
    empty = TTGlyphPen(None).glyph()
    glyphs[".notdef"] = empty
    metrics[".notdef"] = (ADV, 0)
    for ch, art in GLYPHS.items():
        name = "uni%04X" % ord(ch)
        rows = art.split()
        assert len(rows) == 7 and all(len(r) == 5 for r in rows), ch
        # Proportionale Breite: leere Spalten links/rechts abschneiden
        used = [i for i in range(5) if any(r[i] == "#" for r in rows)]
        if used:
            lo, hi = used[0], used[-1]
            rows = [(r[lo:hi + 1]).ljust(5, ".") for r in rows]
            adv = (hi - lo + 2) * PX
        else:
            adv = 4 * PX
        names.append(name)
        glyphs[name] = draw(rows)
        metrics[name] = (adv, 0)
        cmap[ord(ch)] = name
        if ch.lower() != ch:                 # Kleinbuchstaben zeigen auf Grossbuchstaben
            cmap[ord(ch.lower())] = name
    for src, dst in ALIASES.items():
        cmap[ord(src)] = "uni%04X" % ord(dst)

    fb = FontBuilder(1000, isTTF=True)
    fb.setupGlyphOrder(names)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyphs)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=800, descent=-200)
    fb.setupNameTable({"familyName": "Blockschrift", "styleName": "Regular"})
    fb.setupOS2(sTypoAscender=800, sTypoDescender=-200, usWinAscent=800, usWinDescent=200,
                sCapHeight=700, sxHeight=700)
    fb.setupPost()
    out = ROOT / "fonts"
    out.mkdir(parents=True, exist_ok=True)
    fb.font.flavor = "woff"
    fb.save(str(out / "blockschrift.woff"))


# --------------------------------------------------------------------------
# 2) Pixel-Art als SVG
# --------------------------------------------------------------------------
PALETTE = {
    "r": "#e23b3b", "R": "#b02323", "y": "#ffd23f", "o": "#f08a1c", "b": "#4f7df0",
    "B": "#2f55c0", "w": "#ffffff", "p": "#ff8fc7", "P": "#e0559f", "v": "#a66bff",
    "g": "#3f9b2f", "G": "#2c7a22", "l": "#7fd14a", "d": "#8a5a3a", "D": "#6e452b",
    "s": "#a9744f", "k": "#1d2b1a",
}

FLOWERS = {
    "poppy": ["..r.r..", ".rrRrr.", ".rryrr.", ".rrRrr.", "..r.r..", "...g...", ".G.g...", "..Gg...", "...g.G.", "...gG.."],
    "dandelion": ["..y..", ".yyy.", "yyoyy", ".yyy.", "..y..", "..g..", "..g..", ".Gg..", "..g.."],
    "cornflower": [".b.b.", "bbwbb", ".bBb.", "..g..", "..gG.", "..g.."],
    "tulip": ["p.p.p", "ppPpp", "ppppp", ".pPp.", "..g..", "G.g..", ".Gg..", "..g.."],
    "daisy": [".w.w.", "wwyww", ".w.w.", "..g..", ".Gg..", "..g.."],
    "allium": [".vv.", "vvvv", "vvvv", ".vv.", ".g..", ".g..", ".gG.", ".g.."],
    "tuft": ["l...l", ".l.l.", ".lll."],
}


def svg(width, height, cells, pixel=1):
    rects = "".join(
        f'<rect x="{x * pixel}" y="{y * pixel}" width="{pixel}" height="{pixel}" fill="{PALETTE[c]}"/>'
        for x, y, c in cells
    )
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width * pixel} {height * pixel}" '
            f'shape-rendering="crispEdges">{rects}</svg>')


def place(cells, art, x0, bottom):
    top = bottom - len(art)
    for y, row in enumerate(art):
        for x, c in enumerate(row):
            if c != ".":
                cells.append((x0 + x, top + y, c))


def build_art():
    out = ROOT / "img"
    out.mkdir(parents=True, exist_ok=True)

    # Blumenwiese (kachelbar)
    w, h, cells = 96, 12, []
    layout = [("poppy", 2), ("tuft", 12), ("dandelion", 20), ("cornflower", 29), ("tuft", 37),
              ("tulip", 45), ("daisy", 54), ("allium", 63), ("tuft", 69), ("dandelion", 77),
              ("cornflower", 85), ("tuft", 91)]
    for name, x in layout:
        place(cells, FLOWERS[name], x, h)
    (out / "flowers.svg").write_text(svg(w, h, cells))

    # Boden: Gras oben, Erde unten (kachelbar)
    w, h, cells = 16, 10, []
    edge = [3, 4, 3, 3, 5, 4, 3, 4, 4, 3, 5, 3, 4, 4, 3, 4]
    speck = {(2, 6), (7, 8), (11, 6), (14, 9), (5, 9), (9, 7), (0, 8)}
    for x in range(w):
        for y in range(h):
            if y < edge[x]:
                c = "l" if y == 0 else ("g" if (x + y) % 5 else "G")
            else:
                c = "D" if (x, y) in speck else ("s" if (x * 3 + y) % 7 == 0 else "d")
            cells.append((x, y, c))
    (out / "ground.svg").write_text(svg(w, h, cells))

    # Favicon: Blume auf hellgruenem Feld
    cells = [(x, y, "l") for x in range(9) for y in range(11)]
    place(cells, FLOWERS["poppy"], 1, 11)
    (out / "favicon.svg").write_text(svg(9, 11, cells))

    for name in ("poppy", "dandelion", "tulip", "cornflower"):
        art = FLOWERS[name]
        cells = []
        place(cells, art, 0, len(art))
        (out / f"{name}.svg").write_text(svg(max(map(len, art)), len(art), cells))


if __name__ == "__main__":
    build_font()
    build_art()
    print("Assets erzeugt in", ROOT)
