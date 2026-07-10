# FAQ — Adding a personal icon set to Cinnamon

*Complete, scarred edition — Franz & Aldus 🦉, Linux Mint / Cinnamon, July 2026*

---

## 1. How an icon theme works

An icon theme is a folder living in one of these paths:

| Path | Who uses it |
|---|---|
| `~/.local/share/icons/` | **recommended** — your user only, no sudo |
| `~/.icons/` | same (historical path) |
| `/usr/share/icons/` | all users, but needs sudo and system updates touch it |

Inside there must be:

- **`index.theme`** — the ID card: name, theme to inherit from (`Inherits=`),
  the list of subfolders with icons (`Directories=`), each with its own
  section. Without this file the theme is invisible.
- **`icon-theme.cache`** (optional) — a binary index that speeds up loading.
  The theme works without it; a *stale* cache, though, is worse than none.
- The subfolders with the icons: **only `.png`, `.svg`, `.xpm`** (no `.ico`,
  `.jpg`, `.gif`).

**Key concept:** the system substitutes icons **by file name**.
`user-trash.png` replaces the trash bin; `Red_bin.png` replaces nothing but
stays available for manual assignment. The theme's **internal name** (for
`gsettings`) is the **folder name**; the `Name=` in the index is only the
displayed label.

---

## 2. The suite's tools

See the **README** for installation and use. In short: `create-icon-theme.sh`
(adds icons and regenerates everything), `pick-icon-bybias.py` + Nemo action
(chooser with your categories), `make-symbolic-icon.py` (generates symbolic
icons), `hunt-the-giants.py` (defuses collisions and evicts nested themes),
`prefix-everything.sh` (prefixes **all** icons: zero substitutions, zero
triangles — the choice for those who just want their own collection).

---

## 3. Common problems (all tested on our own skin)

### ⚠ "The command can't find the folder" — spaces in names
The shell splits arguments at spaces: `.../0-aaa NEW ICONS` becomes three
arguments and the commands fail. **Cure:** quotes around the path — or no
spaces (the scripts remove them).

### ⚠ The cache never gets created: `-v` does NOT mean "verbose"!
```
-q, --quiet     Turn off verbose output
-v, --validate  Validate existing icon cache
```
`gtk-update-icon-cache -f -v` **builds nothing**: it only checks whether a
cache exists, and not finding one it answers `File not found:
icon-theme.cache`. **Cure:** just `-f`. On success it says
`Cache file created successfully.`

### ⚠ "The generated cache was invalid" — the treacherous accents
`gtk-update-icon-cache` **rejects non-ASCII characters** in file names (à è ì ò
ù, ä ö ü ß), even in valid UTF-8. A single `icòna.png` and the whole cache is
discarded.
**Diagnosis:** `LC_ALL=C find <theme> -name '*[! -~]*'`
**Cure:** transliterate (icòna → icona) — the script does it for you.

### ⚠ `gtk-update-icon-cache -f` alone → "No theme index file in '(null)'"
The path is missing. Always:
`gtk-update-icon-cache -f ~/.local/share/icons/ThemeName/`.
Don't use `--ignore-theme-index` in the wrong folder.

### ⚠ `sudo` where it isn't needed
In your own home, sudo is harmful: files created by root can't be modified
anymore. **Cure:** `sudo chown -R user:user ~/.local/share/icons/ThemeName`

### ⚠ GIANT icons in menus, toolbars, Nemo's sidebar
An app asks for `edit-copy` at 16px; if one of your files is named that way —
even a 256px PNG — GTK finds it and many apps show it at natural size. These
are the **name collisions**, almost always brought in by **nested complete
themes**.
**Diagnosis and cure:** `hunt-the-giants.py` (report → `--evict` →
`--rename`). Then `nemo -q`.
**Beware the avalanche:** if you run `--rename` *before* `--evict`, the hunter
also hits the tens of thousands of files from the nested themes (real case:
95,225 files!). Correct, but it effectively breaks those themes. Reversible
with `--restore`, but the right order is **evict first, rename after**.

### ⚠ GIANT icons but it's Nemo's ZOOM (not the theme)
If the big ones are the **files and folders** in the main view, it's the zoom
(an accidental Ctrl+scroll). **Cure:** `Ctrl+0`, or
`gsettings reset org.nemo.icon-view default-zoom-level`. Test to tell them
apart: temporarily switch the icon theme and `nemo -q` — if the giants stay,
it's the zoom; if they vanish, it was the collisions.

### ⚠⚠ TRIANGLES with an exclamation mark (MISSING icons, look giant)
The trickiest case, and the most common with a personal theme. Those grey
triangles in a white sheet are the `image-missing` placeholder: **they aren't
big icons, they're missing icons**, drawn at full size (so they look giant).
They appear in **several apps** (Nemo, Shutter...), a sign the problem is
system-wide, not app-specific. Three causes, in order:

1. **Lean inheritance.** `Inherits=` points to a theme that *isn't complete*.
   Beware: `Mint-X-Red` and the other **coloured** variants exist but contain
   almost only the coloured folders — for interface icons they inherit in
   turn, and if the chain doesn't rise to a complete theme, the missing icons
   become triangles. **Cure:** inherit from a **complete** theme:
   ```bash
   sed -i 's/^Inherits=.*/Inherits=Mint-Y/' ~/.local/share/icons/byBias-Icons/index.theme
   rm -f ~/.local/share/icons/byBias-Icons/icon-theme.cache
   gtk-update-icon-cache -f ~/.local/share/icons/byBias-Icons/
   nemo -q
   ```
   Golden rule: **always inherit from a complete theme** (`Mint-Y`), never
   from a coloured variant that itself inherits.

2. **Collisions.** One of your files with standard names (`folder`,
   `edit-copy`...) covers only *some* sizes: where the requested size is
   missing → triangle. **Definitive cure if you don't want to substitute
   anything:** `prefix-everything.sh` (prefix `bybias-` on all icons → no
   collision possible).

3. **Corrupted system cache.** If the triangles remain **even with a healthy
   theme like Mint-Y** and **after a full logout**, the global icon cache is
   corrupted. **Cure:**
   ```bash
   sudo update-icon-caches /usr/share/icons/*
   nemo -q
   ```

**Quick diagnosis:** switch the icon theme to `Mint-Y` + `nemo -q`. Triangles
gone → it was your theme (cause 1 or 2). Triangles remain → it's the system
cache (cause 3) or the session (try a full logout first).

### ⚠ Alien icons out of nowhere (the Mint-Aqua case 😂)
Same cause as the giants: the nested themes with standard names *win* on the
inheritance chain, and folders turn aqua-coloured. Same cure: lean theme
(`--evict`).

### ⚠ The theme appears but looks identical to before
Normal if the icons have non-standard names: they substitute nothing
automatically. They show up in manual assignment, or by renaming them to the
standard names (table in §5).

### ⚠ The preview in Settings never changes
It uses icons with standard names: if the theme doesn't have them, it shows
the inherited ones. Not a fault.

### ⚠ `Inherits=` points to an uninstalled theme
If the inherited theme doesn't exist (e.g. `Mint-X-Red` on recent Mint), the
chain breaks and falls back to `hicolor`, nearly empty → generic icons.
**Cure:** `ls /usr/share/icons`, then install (`sudo apt install
mint-x-icons`) or change `Inherits`.

### ⚠ MY categories don't appear in the icon chooser
They never will: the Mint chooser (XAppIconChooserDialog) has a category table
**hardcoded in its source**, recognising only ten standard Contexts (Actions,
Applications, Categories, Devices, Emblems, Emotes, MimeTypes, Places, Status,
Panel). A custom Context is **ignored**.
**Cures:** (1) map your folders onto the standard Contexts — the script does
this, and the icons become searchable by name; (2) for *real* personal
categories, `pick-icon-bybias.py`, which uses the `add_custom_category` API.

### ⚠ Changes don't show / stale cache
GTK and Nemo keep the theme in memory. After every change:
`edit → index → gtk-update-icon-cache -f <path> → Ctrl+Alt+Esc → nemo -q`.
When in doubt, delete the old cache (`rm icon-theme.cache`) before regenerating
it: better no cache than a lying one.

### ⚠ The collection isn't found in the file picker
`~/.local` is **hidden**: in file pickers press **Ctrl+H**.

### ⚠ Cjs-CRITICAL messages in the terminal (St.BoxLayout disposed...)
Cinnamon's **internal** grumbling on restart or theme change. Harmless. For
silent restarts: `nohup cinnamon --replace >/dev/null 2>&1 &` or Ctrl+Alt+Esc.

### ⚠ "No png/svg file found"
The folder contains unsupported formats (`.ico`, `.jpg`, `.gif`) or the picker
pointed at the wrong level. Inventory:
`find "folder" -type f | sed 's/.*\.//' | sort | uniq -c | sort -rn`.
Convert to PNG (e.g. `mogrify -format png *.ico`).

---

## 4. Symbolic icons (bonus)

The monochrome little icons of panels and menus: `-symbolic` suffix, SVG
16×16, `#bebebe` fill (GTK **recolours** them to match the theme, light or
dark). Fills only, no strokes; pixel-aligned shapes; plain SVG. Generate them
automatically with `make-symbolic-icon.py`. Preview with `gtk3-icon-browser`
(package `gtk-3-examples`).

---

## 5. Useful standard names for automatic substitutions

| File name | What it replaces |
|---|---|
| `folder` | generic folder |
| `user-home` | Home folder |
| `user-trash` / `user-trash-full` | empty / full trash |
| `folder-download` | Downloads folder |
| `folder-documents` | Documents folder |
| `folder-pictures` | Pictures folder |
| `folder-music` | Music folder |
| `folder-videos` | Videos folder |
| `folder-desktop` / `user-desktop` | Desktop |
| `computer` | the computer |
| `drive-harddisk` | hard disk |
| `drive-removable-media` | USB stick |
| `network-workgroup` | network |
| `text-x-generic` | generic text file |
| `image-x-generic` | generic image |
| `application-x-executable` | executable |

Full list: the freedesktop "Icon Naming Specification", or by peeking inside
`/usr/share/icons/Mint-Y/places/48/`.

---

## 6. Quick triage: "I see strange/big/missing icons"

1. **Look closely / take a screenshot.** Are they *big* icons or *missing*
   icons (triangles) drawn big? It changes everything.
2. **Only files and folders in the view, enlarged** → Nemo zoom (`Ctrl+0`).
3. **Exclamation-mark triangles, in several apps** → missing icons:
   - switch the theme to `Mint-Y` + `nemo -q`;
   - gone → it's your theme: fix `Inherits=Mint-Y`, or
     `prefix-everything.sh` if you don't want to substitute anything;
   - still there → full logout; if still there →
     `sudo update-icon-caches /usr/share/icons/*`.
4. **Big menu/toolbar icons** → check the **GTK theme** (Settings → Themes →
   Applications): a theme activated by mistake can force them. Go back to
   `Mint-Y`.
5. **The rule that prevents almost everything:** inherit from a **complete**
   theme, keep the theme **lean**, and if you only want your collection,
   **prefix everything**.

---

*Last revision: July 2026 — written at the owl's hour, battle won after
meeting every mask of the dragon: missing index, spaces, the `-v` flag,
accents, hardcoded categories, nested themes, the 95k avalanche, the GTK
theme, lean inheritance and the corrupted system cache.* 🦉
