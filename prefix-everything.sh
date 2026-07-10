#!/bin/bash
#############################################################
#  prefix-everything.sh  —  by Franz & Aldus 🦉
#
#  Adds the 'bybias-' prefix to ALL icons in the theme, so no
#  name can ever collide with a system icon: zero automatic
#  substitutions, zero triangles. The collection stays intact
#  and pickable by hand from the chooser.
#
#  Usage:  bash prefix-everything.sh
#############################################################

THEME="$HOME/.local/share/icons/byBias-Icons"
PREFIX="bybias-"

if [ ! -d "$THEME" ]; then
    echo "Theme not found: $THEME"
    exit 1
fi

echo "Blanket prefix on: $THEME"
echo "Counting the icons to rename..."

# all icon files that DON'T already have the prefix
mapfile -d '' FILES < <(find "$THEME" -type f \
    \( -iname "*.png" -o -iname "*.svg" -o -iname "*.xpm" \) \
    ! -iname "${PREFIX}*" -print0)

echo "  ${#FILES[@]} icons to rename."
if [ "${#FILES[@]}" -eq 0 ]; then
    echo "Nothing to do: they are all already prefixed."
    exit 0
fi

read -rp "Proceed? [y/N] " ok
[ "$ok" = "y" ] || [ "$ok" = "Y" ] || { echo "Cancelled."; exit 0; }

n=0
for f in "${FILES[@]}"; do
    dir=$(dirname "$f")
    base=$(basename "$f")
    # tidy up spaces in the same names, for free
    new="${PREFIX}${base// /_}"
    dest="$dir/$new"
    i=1
    while [ -e "$dest" ]; do
        root="${new%.*}"; ext="${new##*.}"
        dest="$dir/${root}_$i.$ext"; i=$((i+1))
    done
    mv "$f" "$dest"
    n=$((n+1))
done
echo "✔ $n icons prefixed."

# regenerate index.theme? No: only file names change, not folders.
# But the cache must be rebuilt because it indexes the names.
echo "Regenerating the cache..."
rm -f "$THEME/icon-theme.cache"
if gtk-update-icon-cache -f "$THEME"; then
    echo "✔ Cache regenerated."
else
    echo "⚠ Cache problem (but the icons are fine anyway)."
fi

echo ""
echo "Done. No icon in the theme can substitute a system one anymore:"
echo "the triangles will disappear. Restart Nemo:  nemo -q"
echo "Your collection stays pickable by hand from the byBias chooser."
