# byBias Icons for Cinnamon

*A complete toolkit for managing a personal icon collection on Linux Mint / Cinnamon.*
*by Franz & Aldus 🦉 — July 2026*

---

## What's in the suite

| File | What it does |
|---|---|
| `create-icon-theme.sh` | Adds icons to a theme (or creates one): copies, cleans up the names (spaces and accents), generates `index.theme`, updates the cache, restarts Cinnamon and Nemo. Zenity graphical windows. |
| `pick-icon-bybias.py` | Custom chooser: shows the collection in **your** categories and applies the chosen icon to files and folders. |
| `change-icon-bybias.nemo_action` | Adds **"Change icon (byBias)..."** to Nemo's right-click menu. |
| `make-symbolic-icon.py` | Generates symbolic SVG icons (16×16, monochrome) from your PNGs. |
| `hunt-the-giants.py` | Finds and defuses "giant icons" (name collisions with system icons). Evicts nested complete themes. |
| `prefix-everything.sh` | Prefixes **all** icons in the theme with `bybias-`: zero automatic substitutions, zero triangles. The choice if you just want your collection to pick from by hand. |
| `FAQ-icon-theme-Cinnamon.md` | All the theory and every possible problem, personally battle-tested. |

---

## Installation

### The theme script and utilities

Put the scripts wherever you like — a handy path is `~/.local/bin/`:

```bash
mkdir -p ~/.local/bin
cp create-icon-theme.sh make-symbolic-icon.py hunt-the-giants.py prefix-everything.sh ~/.local/bin/
chmod +x ~/.local/bin/create-icon-theme.sh ~/.local/bin/*.py ~/.local/bin/prefix-everything.sh
```

### Chooser + Nemo right-click

```bash
cp pick-icon-bybias.py ~/.local/bin/
chmod +x ~/.local/bin/pick-icon-bybias.py
mkdir -p ~/.local/share/nemo/actions
cp change-icon-bybias.nemo_action ~/.local/share/nemo/actions/
nemo -q    # restart Nemo so it discovers the action
```

The theme path is defined at the top of `pick-icon-bybias.py` and
`hunt-the-giants.py` (`THEME = ...` / `THEME_DEFAULT = ...`): if the theme
changes name or home, update it there. In the `.nemo_action`, the `Exec=` line
must point to the real path of the script.

---

## Daily use

### Adding icons to the theme

```bash
bash create-icon-theme.sh
```

Asks, in order: **where** to take the new icons from → **which theme** to add
them to → permission to rename **spaces** and **accents** → which theme to
**inherit** from → whether to **activate** and **restart**. Then it does
everything on its own. Rerun it after every change. Tip: if you pick the theme
itself as the *source*, it skips the copy and only regenerates (handy after a
manual reorganisation).

### Changing a folder's or file's icon

Right-click → **Change icon (byBias)...** → the chooser opens with your
categories → double-click → done. From the terminal:

```bash
python3 ~/.local/bin/pick-icon-bybias.py ~/Documents/Invoices   # apply
python3 ~/.local/bin/pick-icon-bybias.py                        # copy the path
gio set -t unset ~/Documents/Invoices metadata::custom-icon     # restore
```

### Creating symbolic icons

```bash
python3 ~/.local/bin/make-symbolic-icon.py Trash-*.png --out ~/theme/symbolic/ --preview
```

See `README-symbolic-icon.md` for options and how to put them into service.

### Defeating giant icons

```bash
python3 ~/.local/bin/hunt-the-giants.py            # report (touches nothing)
python3 ~/.local/bin/hunt-the-giants.py --evict    # move nested complete themes out
python3 ~/.local/bin/hunt-the-giants.py --rename   # defuse the remaining collisions
python3 ~/.local/bin/hunt-the-giants.py --restore  # undo a --rename
```

**Recommended order:** report → `--evict` → report → `--rename`. Eviction must
come **first**, otherwise the rename hits tens of thousands of files from the
nested themes (the "avalanche"). To keep an intentional substitution (your own
`user-trash`), write the name — without extension, one per line — in
`giants-allowed.txt` in the theme folder.

### Zero substitutions: just my collection (no triangles)

If you **don't** want the theme to substitute any system icon — just your
collection to pick from by hand in the chooser — the cleanest route is to
prefix **everything**:

```bash
bash prefix-everything.sh    # adds 'bybias-' to every icon, asks for confirmation
nemo -q
```

No name can collide with a system one anymore, so both the giants and the
**triangles** (missing icons, see FAQ) disappear. It's repeatable: it skips
already-prefixed icons, so you can run it after each addition. Categories and
folders don't change: only file names are touched.

---

## The lean-theme philosophy 🦉

A theme in `~/.local/share/icons/` works best **lean**: only the collections
you actually use to assign icons. The full archive — downloaded themes,
experiments, thousands of "maybe someday" files — is better off elsewhere
(e.g. `~/Pictures/`).

Two concrete reasons:

- **complete themes** nested inside (with icons using standard names like
  `folder` or `edit-copy`) get picked by the system in place of the stock
  icons: alien colours and **giant icons** in menus;
- fewer files = a healthier cache, faster indexing, fewer surprises.

Your own experiments with complete themes deserve promotion to standalone
themes: moved into `~/.local/share/icons/`, they become selectable from
Settings.

---

## The liturgy (commit it to memory)

```
edit → regenerate index.theme → gtk-update-icon-cache -f <path> → Ctrl+Alt+Esc → nemo -q
```

The scripts run it for you, but knowing it by heart saves late nights.
For any problem: the **FAQ**, where every trap is documented with its scar.
