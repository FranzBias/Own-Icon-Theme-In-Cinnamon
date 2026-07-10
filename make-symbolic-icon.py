#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#############################################################
#  make-symbolic-icon.py  —  by Franz & Aldus 🦉
#
#  Turns PNG icons into symbolic SVG icons: extracts the
#  silhouette, reduces it onto a 16×16 grid and generates a
#  monochrome SVG (#bebebe) ready for GTK themes.
#
#  Usage:
#    make-symbolic-icon.py icon.png [other.png ...]
#    make-symbolic-icon.py folder/          (all PNGs inside)
#
#  Options:
#    --out FOLDER      where to save the SVGs (default: next to the PNGs)
#    --grid N          grid resolution (default 16; 32 for more
#                      detail — the SVG stays 16×16 either way)
#    --coverage X      how much of a cell must be filled for it
#                      to switch on (0.0–1.0, default 0.42;
#                      lower = fatter icon)
#    --preview         also save an enlarged preview PNG
#
#  Requires: python3-pil  (sudo apt install python3-pil)
#############################################################

import argparse
import os
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit("The PIL library is required:  sudo apt install python3-pil")

GREY = "#bebebe"


def mask(img, alpha_threshold=64, white_threshold=242):
    """Returns a True/False matrix: True = pixel belonging to the icon.

    Uses the alpha channel if present; otherwise treats near-white as
    background.
    """
    img = img.convert("RGBA")
    px = img.load()
    w, h = img.size
    use_alpha = any(px[x, y][3] < 250 for y in range(0, h, max(1, h // 16))
                    for x in range(0, w, max(1, w // 16)))
    m = [[False] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if use_alpha:
                m[y][x] = a >= alpha_threshold
            else:
                m[y][x] = not (r >= white_threshold and g >= white_threshold
                               and b >= white_threshold)
    return m, w, h


def reduce(m, w, h, grid, coverage):
    """Reduces the mask to grid×grid: each cell switches on if the
    fraction of filled pixels exceeds the coverage threshold."""
    # crop to the useful bounding box to centre the silhouette
    xs = [x for y in range(h) for x in range(w) if m[y][x]]
    ys = [y for y in range(h) for x in range(w) if m[y][x]]
    if not xs:
        return None
    x0, x1, y0, y1 = min(xs), max(xs) + 1, min(ys), max(ys) + 1
    side = max(x1 - x0, y1 - y0)
    # centre the box in a square
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    x0, y0 = cx - side / 2, cy - side / 2

    cells = [[False] * grid for _ in range(grid)]
    step = side / grid
    for gy in range(grid):
        for gx in range(grid):
            filled = tot = 0
            ax0, ay0 = x0 + gx * step, y0 + gy * step
            for py in range(int(ay0), int(ay0 + step) + 1):
                for pxx in range(int(ax0), int(ax0 + step) + 1):
                    if 0 <= pxx < w and 0 <= py < h:
                        tot += 1
                        if m[py][pxx]:
                            filled += 1
            if tot and filled / tot >= coverage:
                cells[gy][gx] = True
    return cells


def cells_to_svg(cells, grid):
    """Converts the grid into a compact SVG: contiguous cells in a row
    become rectangles."""
    scale = 16 / grid
    rects = []
    for gy in range(grid):
        gx = 0
        while gx < grid:
            if cells[gy][gx]:
                start = gx
                while gx < grid and cells[gy][gx]:
                    gx += 1
                rects.append((start * scale, gy * scale,
                              (gx - start) * scale, scale))
            else:
                gx += 1
    bodies = "".join(
        f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}"/>'
        for x, y, w, h in rects)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" '
            f'viewBox="0 0 16 16">\n'
            f'<g fill="{GREY}">{bodies}</g>\n</svg>\n')


def process(path, out_dir, grid, coverage, preview):
    name = os.path.splitext(os.path.basename(path))[0]
    name = name.replace(" ", "_") + "-symbolic"
    img = Image.open(path)
    m, w, h = mask(img)
    cells = reduce(m, w, h, grid, coverage)
    if cells is None:
        print(f"  ✘ {path}: no silhouette found (fully transparent?)")
        return
    svg = cells_to_svg(cells, grid)
    dest = os.path.join(out_dir or os.path.dirname(path) or ".",
                        name + ".svg")
    with open(dest, "w") as f:
        f.write(svg)
    print(f"  ✔ {dest}")

    if preview:
        side = 16 * 8
        prev = Image.new("RGB", (side, side), "white")
        step = side / grid
        for gy in range(grid):
            for gx in range(grid):
                if cells[gy][gx]:
                    for py in range(int(gy * step), int((gy + 1) * step)):
                        for pxx in range(int(gx * step),
                                         int((gx + 1) * step)):
                            prev.putpixel((pxx, py), (190, 190, 190))
        prev.save(dest.replace(".svg", "_preview.png"))


def main():
    ap = argparse.ArgumentParser(
        description="Generate symbolic SVG icons from PNGs.")
    ap.add_argument("sources", nargs="+",
                    help="PNG files or folders to process")
    ap.add_argument("--out", default=None, help="destination folder")
    ap.add_argument("--grid", type=int, default=16)
    ap.add_argument("--coverage", type=float, default=0.42)
    ap.add_argument("--preview", action="store_true")
    args = ap.parse_args()

    if args.out:
        os.makedirs(args.out, exist_ok=True)

    files = []
    for s in args.sources:
        if os.path.isdir(s):
            files += [os.path.join(s, f) for f in sorted(os.listdir(s))
                      if f.lower().endswith(".png")]
        else:
            files.append(s)

    if not files:
        sys.exit("No PNGs to process.")

    print(f"Processing {len(files)} icons "
          f"(grid {args.grid}, coverage {args.coverage}):")
    for f in files:
        process(f, args.out, args.grid, args.coverage, args.preview)


if __name__ == "__main__":
    main()
