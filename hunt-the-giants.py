#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#############################################################
#  hunt-the-giants.py  —  by Franz & Aldus 🦉
#
#  Finds and defuses "giant icons": files in your collection
#  whose name collides with a system icon.
#
#  When an app asks for an icon (e.g. "edit-copy" at 16px),
#  GTK searches by NAME in the active theme: if one of your
#  files is named that way — even a 256px PNG — it wins, and
#  many apps show it at its natural size. Hence the giants.
#
#  Usage:
#    hunt-the-giants.py                    → report only (touches nothing)
#    hunt-the-giants.py --rename           → adds the 'bybias-' prefix
#                                            to colliding files
#    hunt-the-giants.py --restore          → REMOVES the 'bybias-' prefix
#                                            (undoes a --rename)
#    hunt-the-giants.py --prefix mine-     → custom prefix
#    hunt-the-giants.py --theme /path      → theme other than the default
#
#  Intentional exceptions (deliberate substitutions, e.g. YOUR
#  user-trash): list them in a file 'giants-allowed.txt' in the
#  theme folder, one name per line.
#
#  BEWARE THE AVALANCHE: if the theme contains NESTED COMPLETE
#  THEMES (whole downloaded sets, with thousands of icons using
#  standard names), --rename will hit tens of thousands of them —
#  correct, but it effectively "breaks" those themes. Better to
#  evict them first:  --evict  moves them to ~/Pictures/.
#############################################################

import argparse
import os
import sys

THEME_DEFAULT = os.path.expanduser("~/.local/share/icons/byBias-Icons")
SYSTEM_THEMES = ["/usr/share/icons"]
EXTENSIONS = (".png", ".svg", ".xpm")


def stem(filename):
    base = os.path.basename(filename)
    for ext in EXTENSIONS:
        if base.lower().endswith(ext):
            return base[: -len(ext)]
    return None


def system_names(excluded_theme):
    """All icon names of installed themes (the system's vocabulary)."""
    names = set()
    for root_dir in SYSTEM_THEMES:
        if not os.path.isdir(root_dir):
            continue
        for root, _dirs, files in os.walk(root_dir):
            if os.path.abspath(root).startswith(os.path.abspath(excluded_theme)):
                continue  # don't compare against yourself
            for f in files:
                s = stem(f)
                if s:
                    names.add(s)
                    # also the variant without -symbolic
                    if s.endswith("-symbolic"):
                        names.add(s[: -len("-symbolic")])
    return names


def restore(theme, prefix):
    """Undoes a --rename: removes the prefix where it creates no conflict."""
    n = 0
    for root, _d, files in os.walk(theme):
        for f in files:
            if f.startswith(prefix):
                orig = f[len(prefix):]
                dest = os.path.join(root, orig)
                if not os.path.exists(dest):
                    os.rename(os.path.join(root, f), dest)
                    n += 1
    print(f"✔ Restored {n} files (prefix '{prefix}' removed).")
    print("  Now regenerate the theme and restart Nemo (nemo -q).")


def evict(theme):
    """Moves NESTED COMPLETE THEMES out of the theme.

    A subtree is a 'complete theme' if it contains its own index.theme
    or the typical structure (folders like 16x16/apps, scalable/...).
    Everything goes to ~/Pictures/ICONS/ARCHIVE-from-theme.
    """
    archive = os.path.expanduser("~/Pictures/ICONS/ARCHIVE-from-theme")
    os.makedirs(archive, exist_ok=True)
    suspects = []
    for entry in sorted(os.listdir(theme)):
        path = os.path.join(theme, entry)
        if not os.path.isdir(path):
            continue
        # look for complete themes inside this top-level group
        for root, dirs, files in os.walk(path):
            if "index.theme" in files or \
               any(d in ("scalable", "16x16", "22x22", "48x48") for d in dirs):
                suspects.append(path)
                break
    if not suspects:
        print("✔ No nested complete themes: the collection is already lean.")
        return
    print(f"Found {len(suspects)} groups containing complete themes:")
    import shutil
    for s in suspects:
        name = os.path.basename(s)
        dest = os.path.join(archive, name)
        i = 1
        while os.path.exists(dest):
            dest = os.path.join(archive, f"{name}_{i}"); i += 1
        shutil.move(s, dest)
        print(f"  → {name}  moved to {archive}")
    print("\n✔ Eviction complete. Now run a normal report,")
    print("  then regenerate the theme and restart Nemo (nemo -q).")


def main():
    ap = argparse.ArgumentParser(
        description="Find the name collisions that cause giant icons.")
    ap.add_argument("--theme", default=THEME_DEFAULT)
    ap.add_argument("--rename", action="store_true",
                    help="apply the prefix to colliding files")
    ap.add_argument("--restore", action="store_true",
                    help="remove the prefix (undo a --rename)")
    ap.add_argument("--evict", action="store_true",
                    help="move nested complete themes out of the theme")
    ap.add_argument("--prefix", default="bybias-")
    args = ap.parse_args()

    theme = os.path.abspath(os.path.expanduser(args.theme))
    if not os.path.isdir(theme):
        sys.exit(f"Theme not found: {theme}")

    if args.restore:
        restore(theme, args.prefix)
        return
    if args.evict:
        evict(theme)
        return

    # intentional exceptions
    allowed = set()
    allowed_file = os.path.join(theme, "giants-allowed.txt")
    if os.path.isfile(allowed_file):
        with open(allowed_file) as f:
            allowed = {r.strip() for r in f if r.strip()
                       and not r.startswith("#")}

    print("Building the vocabulary of system icons...")
    vocabulary = system_names(theme)
    print(f"  {len(vocabulary)} names known to the system.\n")

    collisions = []
    for root, _dirs, files in os.walk(theme):
        for f in sorted(files):
            s = stem(f)
            if not s or s.startswith(args.prefix):
                continue
            if s in vocabulary:
                if s in allowed:
                    continue
                collisions.append(os.path.join(root, f))

    if not collisions:
        print("✔ No collisions: no giants lurking.")
        if allowed:
            print(f"  ({len(allowed)} intentional substitutions respected)")
        return

    print(f"⚠ {len(collisions)} files hijack system icons:\n")
    for c in collisions:
        print("  " + os.path.relpath(c, theme))

    if not args.rename:
        print(f"\nRead-only report: no files touched.")
        print(f"To defuse them:  {sys.argv[0]} --rename")
        print(f"To keep some on purpose (e.g. your own user-trash):")
        print(f"  add the name (without extension) to {allowed_file}")
        return

    print(f"\nApplying the prefix '{args.prefix}'...")
    n = 0
    for c in collisions:
        folder, name = os.path.split(c)
        new = os.path.join(folder, args.prefix + name)
        i = 1
        while os.path.exists(new):
            root, ext = os.path.splitext(args.prefix + name)
            new = os.path.join(folder, f"{root}_{i}{ext}")
            i += 1
        os.rename(c, new)
        n += 1
    print(f"✔ {n} files defused.")
    print("\nNow regenerate the theme (index + cache):")
    print("  rerun create-icon-theme.sh with source = the theme itself,")
    print("  then Ctrl+Alt+Esc. The giants are history.")


if __name__ == "__main__":
    main()
