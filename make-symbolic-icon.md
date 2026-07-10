# make-symbolic-icon.py — README

*Generates symbolic SVG icons from your PNGs.*
*by Franz & Aldus 🦉 — July 2026*

---

## What it does

**Symbolic icons** are the monochrome, minimal little icons of panels and
menus, which the system recolours automatically to match the theme (light or
dark). They have SVG 16×16, a `#bebebe` fill (the "symbolic grey" that GTK
swaps for the theme colour), and a name with the `-symbolic` suffix.

This script takes your PNGs and derives the symbolic version automatically: it
extracts the **silhouette** (from the alpha channel, or from near-white if the
background isn't transparent), centres it, reduces it onto a **16×16 grid** and
generates a clean, pixel-aligned SVG — with the name already correct
(`Trash-01.png` → `Trash-01-symbolic.svg`).

## What it does NOT do (workshop honesty)

The script produces **silhouettes**: the outer shape, faithful and legible. It
can't *redraw* — the mesh of a wire basket, the ribs of a bin, the inner
details need a craftsman's eye. The ideal workflow:

1. the script generates the silhouette in a second;
2. if you like the result, it's ready;
3. if it needs character, open the SVG in **Inkscape** and carve the details
   (holes via boolean subtraction, always fills, never strokes).

## Requirements

```bash
sudo apt install python3-pil
```

## Usage

```bash
# one file (the SVG is created next to the PNG)
python3 make-symbolic-icon.py Trash-01.png

# several files, into a destination folder
python3 make-symbolic-icon.py Trash-*.png --out ~/theme/symbolic/

# a whole folder of PNGs
python3 make-symbolic-icon.py ~/Pictures/trash/ --out ~/theme/symbolic/

# with an enlarged preview PNG for visual checking
python3 make-symbolic-icon.py icon.png --preview
```

## Options

| Option | Default | Effect |
|---|---|---|
| `--out FOLDER` | next to the PNG | where to save the SVGs |
| `--grid N` | 16 | grid resolution. 16 = pixel-perfect style; 32 = more detail (the SVG stays 16×16) |
| `--coverage X` | 0.42 | how much of a cell must be filled for it to "switch on". Lower = fatter, fuller icon; higher = leaner, more jagged |
| `--preview` | off | also saves an enlarged PNG next to each SVG |

Practical tip: if a silhouette comes out "eaten", try `--coverage 0.3`; if it
comes out as a shapeless blob, raise it to `--coverage 0.55` or try `--grid 32`.

## Putting the icons into service

1. Copy the SVGs into a folder of the theme, e.g.
   `~/.local/share/icons/byBias-Icons/symbolic/`
2. Rerun `create-icon-theme.sh` (source = the theme itself) to regenerate
   `index.theme` and the cache.
3. With personal names (`Trash-01-symbolic`) they stay a collection to assign
   by hand. For the **system** to use them in place of its own, you need the
   **standard names**: rename the chosen pair to `user-trash-symbolic.svg` and
   `user-trash-full-symbolic.svg`, regenerate, and your trash bin will appear
   everywhere Cinnamon draws a small trash icon.

To see the theme's symbolic icons (and the light/dark recolouring):
`gtk3-icon-browser` (package `gtk-3-examples`).

**Note:** if after adding icons to the theme you see exclamation-mark
triangles (missing icons), it's not the symbolic icons' fault: it's the
theme's inheritance pointing to a non-complete theme. Make sure the
`index.theme` has `Inherits=Mint-Y` (a complete theme), not a coloured
variant. See the FAQ, section on triangles.

## How it works, for the curious

1. **Mask** — each pixel is classified icon/background: if the image has
   transparency the alpha channel is used, otherwise near-white counts as
   background.
2. **Crop and centre** — the silhouette is inscribed in a square, so the icon
   fills the canvas well whatever its original aspect ratio.
3. **Grid reduction** — for each 16×16 cell the fraction of filled pixels is
   measured: above the coverage threshold, the cell switches on. Same
   principle as typographic half-toning, but with a hard threshold.
4. **Compact SVG** — contiguous switched-on cells in each row are merged into a
   single rectangle: small SVGs (typically 15–20 rectangles) and perfectly
   pixel-aligned.

---

*Tested on the byBias trash bins: wire, weave and Flameia's autumn bin —
silhouettes recognisable at first glance. Written at the owl's hour.* 🦉
