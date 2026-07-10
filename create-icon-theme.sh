#!/bin/bash
#############################################################
#  create-icon-theme.sh  (v2)  —  by Franz & Aldus 🦉
#
#  1. Asks WHERE to take the new icons from (source)
#  2. Asks WHICH THEME to add them to (or creates a new one)
#  3. Copies the icons into the theme
#  4. Regenerates index.theme, updates the cache
#  5. Activates the theme and restarts Cinnamon (on request)
#
#  Graphical interface via Zenity (GTK, native Cinnamon style).
#  Usage:  bash create-icon-theme.sh
#############################################################

TITLE="Cinnamon icon theme"
ICONS_DIR="$HOME/.local/share/icons"

# ---------- 0. Preliminary checks ---------------------------
if ! command -v zenity >/dev/null 2>&1; then
    echo "Zenity is not installed. Install with: sudo apt install zenity"
    exit 1
fi
mkdir -p "$ICONS_DIR"

# ---------- 1. SOURCE: where to take the new icons from -----
SRC=$(zenity --file-selection --directory \
      --title="$TITLE — WHERE to take the NEW icons from?" \
      --filename="$HOME/")
[ -z "$SRC" ] && exit 0

N_ICONS=$(find "$SRC" -type f \( -iname "*.png" -o -iname "*.svg" -o -iname "*.xpm" \) | wc -l)
if [ "$N_ICONS" -eq 0 ]; then
    zenity --error --title="$TITLE" \
           --text="No icons (png/svg/xpm) found in:\n$SRC"
    exit 1
fi

# ---------- 2. DESTINATION: which theme to add them to ------
THEMES=$(ls -1 "$ICONS_DIR" 2>/dev/null | grep -v "^default$")
DEST_NAME=$(zenity --list --title="$TITLE" --width=380 --height=440 \
            --text="Found $N_ICONS icons in:\n$(basename "$SRC")\n\nWhich THEME do you want to add them to?" \
            --column="Theme" "➕ Create NEW theme..." $THEMES)
[ -z "$DEST_NAME" ] && exit 0

if [ "$DEST_NAME" = "➕ Create NEW theme..." ]; then
    DEST_NAME=$(zenity --entry --title="$TITLE" \
                --text="Name of the new theme (no spaces!):" \
                --entry-text="byBias-Icons")
    [ -z "$DEST_NAME" ] && exit 0
    DEST_NAME="${DEST_NAME// /_}"
fi
DEST="$ICONS_DIR/$DEST_NAME"
mkdir -p "$DEST"

# ---------- 3. Copy (with accident protection) --------------
case "$SRC" in
    "$DEST"|"$DEST"/*)
        zenity --info --title="$TITLE" \
               --text="The source is already inside the theme:\nskipping the copy and only regenerating the index."
        ;;
    *)
        GROUP=$(basename "$SRC")
        GROUP="${GROUP// /_}"
        if [ -d "$DEST/$GROUP" ]; then
            zenity --question --title="$TITLE" --width=400 --text=\
"A folder '$GROUP' already exists in the theme.\nMerge the new icons into it?\n(files with the same name will be overwritten)" \
            || exit 0
        fi
        mkdir -p "$DEST/$GROUP"
        cp -r "$SRC/." "$DEST/$GROUP/"
        ;;
esac

# ---------- 4. Spaces in names: the old trap ----------------
N_SPACES=$(find "$DEST" -depth -name "* *" | wc -l)
if [ "$N_SPACES" -gt 0 ]; then
    if zenity --question --title="$TITLE" --width=420 --text=\
"Found $N_SPACES files or folders with SPACES in the name inside the theme.\n\nSpaces cause problems for the shell and GTK parsers.\nRename them automatically? (space → _ )"; then
        find "$DEST" -depth -name "* *" \
             -execdir bash -c 'mv "$1" "${1// /_}"' _ {} \;
    fi
fi

# ---------- 4-bis. Accents in names: the cache trap ---------
# gtk-update-icon-cache rejects ANY non-ASCII character in
# file names (à è ì ò ù ü ß ...) → "generated cache was invalid"
N_ACCENTS=$(LC_ALL=C find "$DEST" -name '*[! -~]*' | wc -l)
if [ "$N_ACCENTS" -gt 0 ]; then
    if zenity --question --title="$TITLE" --width=440 --text=\
"Found $N_ACCENTS files or folders with ACCENTS or special\ncharacters in the name (à è ò ü ...).\n\nThese characters make the icon cache INVALID.\nRename them automatically? (icòna → icona)"; then
        python3 - "$DEST" <<'PYEOF'
import os, sys, unicodedata
base = sys.argv[1]
for root, dds, ffs in os.walk(base, topdown=False):
    for name in ffs + dds:
        new = unicodedata.normalize("NFKD", name)
        new = "".join(c for c in new if ord(c) < 128 and not unicodedata.combining(c))
        new = new or "noname"
        if new != name:
            src, dst = os.path.join(root, name), os.path.join(root, new)
            i = 1
            while os.path.exists(dst):
                r, e = os.path.splitext(new)
                dst = os.path.join(root, f"{r}_{i}{e}"); i += 1
            os.rename(src, dst)
PYEOF
    fi
fi

# ---------- 5. Theme to inherit from ------------------------
INHERITS=""
if [ -f "$DEST/index.theme" ]; then
    INHERITS=$(grep -m1 "^Inherits=" "$DEST/index.theme" | cut -d= -f2)
fi
if [ -z "$INHERITS" ]; then
    # IMPORTANT: inherit from a COMPLETE theme (e.g. Mint-Y), never from a
    # coloured variant (Mint-X-Red...) that itself inherits — otherwise
    # missing icons show up as "missing" triangles.
    THEME_LIST=$(ls /usr/share/icons "$ICONS_DIR" 2>/dev/null \
                 | grep -v "^$DEST_NAME$" | grep -v ":" | grep -v "^$" | sort -u)
    INHERITS=$(zenity --list --title="$TITLE" --width=350 --height=420 \
               --text="Theme to INHERIT missing icons from\n(must be really installed AND complete — Mint-Y is a safe choice):" \
               --column="Theme" $THEME_LIST)
    [ -z "$INHERITS" ] && INHERITS="Mint-Y"
fi

# ---------- 6. Generating index.theme -----------------------
DIRS=()
while IFS= read -r d; do
    rel="${d#$DEST/}"
    if find "$d" -maxdepth 1 -type f \
         \( -iname "*.png" -o -iname "*.svg" -o -iname "*.xpm" \) \
         | grep -q .; then
        DIRS+=("$rel")
    fi
done < <(find "$DEST" -mindepth 1 -type d | sort)

if [ ${#DIRS[@]} -eq 0 ]; then
    zenity --error --title="$TITLE" \
           --text="No icons found in the theme's subfolders."
    exit 1
fi

# map a folder name onto one of the 10 STANDARD Contexts:
# the Mint chooser only recognises these (fixed table in the code of
# xapp-icon-chooser-dialog.c) — custom Contexts = invisible icons
map_context () {
    local NAME=$(echo "$1" | tr '[:lower:]' '[:upper:]')
    case "$NAME" in
        *FOLDER*|*TRASH*|*DESKTOP*|*HOME*|*DOWNLOAD*|*PLACES*)
            echo "Places" ;;
        *ARROW*|*SYMBOL*|*EMOJI*|*EMOTE*)
            echo "Emotes" ;;
        *DOC*|*OFFICE*|*BOOK*|*MIME*)
            echo "MimeTypes" ;;
        *DEVICE*|*HARDWARE*)
            echo "Devices" ;;
        *STATUS*|*NOTIF*)
            echo "Status" ;;
        *ACTION*)
            echo "Actions" ;;
        *)
            echo "Applications" ;;
    esac
}

{
    echo "[Icon Theme]"
    echo "Name=$DEST_NAME"
    echo "Comment=Theme generated by create-icon-theme.sh"
    echo "Inherits=$INHERITS"
    echo -n "Directories="
    ( IFS=,; echo "${DIRS[*]}" )
    echo ""
    for d in "${DIRS[@]}"; do
        ctx=$(map_context "${d%%/*}")
        echo "[$d]"
        echo "Size=48"
        echo "MinSize=16"
        echo "MaxSize=512"
        echo "Context=$ctx"
        echo "Type=Scalable"
        echo ""
    done
} > "$DEST/index.theme"

# ---------- 7. Cache update ---------------------------------
# NB: no -v ! (-v = --validate, NOT "verbose"... lesson learned)
rm -f "$DEST/icon-theme.cache"
if OUT=$(gtk-update-icon-cache -f "$DEST" 2>&1); then
    RESULT="✔ Cache created successfully."
else
    RESULT="✘ Cache problem:\n$OUT"
fi

zenity --info --title="$TITLE" --width=440 --text=\
"Icons added to theme: $DEST_NAME\nindex.theme regenerated with ${#DIRS[@]} folders.\n\n$RESULT"

# ---------- 8. Activation and Cinnamon restart --------------
ACTIVE=$(gsettings get org.cinnamon.desktop.interface icon-theme | tr -d "'")
if [ "$ACTIVE" != "$DEST_NAME" ]; then
    if zenity --question --title="$TITLE" \
       --text="ACTIVATE the theme '$DEST_NAME' now?\n(current theme: $ACTIVE)"; then
        gsettings set org.cinnamon.desktop.interface icon-theme "$DEST_NAME"
    fi
fi

if zenity --question --title="$TITLE" \
   --text="Restart Cinnamon now?\n(open windows stay alive)"; then
    nohup cinnamon --replace >/dev/null 2>&1 &
    # also restart Nemo, which caches the theme
    nemo -q 2>/dev/null
fi

exit 0
