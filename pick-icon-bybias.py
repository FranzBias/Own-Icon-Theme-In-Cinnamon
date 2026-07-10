#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#############################################################
#  pick-icon-bybias.py  —  by Franz & Aldus 🦉
#
#  Icon chooser with YOUR categories (the folders of the
#  byBias-Icons theme), built on Linux Mint's XApp API
#  (add_custom_category — the one the stock chooser doesn't
#  use, but we do).
#
#  Usage:
#    pick-icon-bybias.py                → pick an icon,
#                                         path goes to the clipboard
#    pick-icon-bybias.py /path/to/folder
#                                       → pick an icon and APPLY it
#                                         to that folder or file
#
#  To remove a custom icon:
#    gio set -t unset /path metadata::custom-icon
#############################################################

import gi
import os
import re
import subprocess
import sys

gi.require_version("Gtk", "3.0")
gi.require_version("XApp", "1.0")
from gi.repository import Gtk, Gdk, XApp  # noqa: E402

# ---------- Configuration ------------------------------------
THEME = os.path.expanduser("~/.local/share/icons/byBias-Icons")
EXTENSIONS = (".png", ".svg", ".xpm")


def category_name(folder):
    """'5-EMAIL_and_MAIL' → 'Email And Mail' (nicer in the sidebar)"""
    name = re.sub(r"^\d+[-_]*", "", folder)   # drop the numeric prefix
    name = name.replace("_", " ").strip()
    return name.title() if name else folder


def collect_icons(path):
    """All icons inside a folder, subfolders included."""
    icons = []
    for root, _dirs, files in os.walk(path):
        for f in sorted(files):
            if f.lower().endswith(EXTENSIONS):
                icons.append(os.path.join(root, f))
    return icons


def main():
    if not os.path.isdir(THEME):
        d = Gtk.MessageDialog(message_type=Gtk.MessageType.ERROR,
                              buttons=Gtk.ButtonsType.OK,
                              text="Theme not found:\n" + THEME)
        d.run(); d.destroy()
        return 1

    dialog = XApp.IconChooserDialog()
    dialog.set_property("allow-paths", True)
    dialog.set_title("byBias Icons — pick from the collection")

    # one category per top-level folder of the theme
    found = 0
    for folder in sorted(os.listdir(THEME)):
        path = os.path.join(THEME, folder)
        if not os.path.isdir(path):
            continue
        icons = collect_icons(path)
        if icons:
            dialog.add_custom_category(category_name(folder), icons)
            found += len(icons)

    if found == 0:
        d = Gtk.MessageDialog(message_type=Gtk.MessageType.ERROR,
                              buttons=Gtk.ButtonsType.OK,
                              text="No icons found in the theme.")
        d.run(); d.destroy()
        return 1

    response = dialog.run()
    icon = dialog.get_icon_string() if response == Gtk.ResponseType.OK else None
    dialog.destroy()

    if not icon:
        return 0

    # ---------- Apply or clipboard -------------------------------
    if len(sys.argv) > 1:
        # apply the icon to the file/folder passed as argument
        target = sys.argv[1]
        uri = icon if icon.startswith("file://") else "file://" + icon
        result = subprocess.run(
            ["gio", "set", target, "metadata::custom-icon", uri],
            capture_output=True, text=True)
        if result.returncode != 0:
            d = Gtk.MessageDialog(message_type=Gtk.MessageType.ERROR,
                                  buttons=Gtk.ButtonsType.OK,
                                  text="Could not apply the icon:\n"
                                       + result.stderr.strip())
            d.run(); d.destroy()
            return 1
    else:
        # no target: copy the path to the clipboard
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(icon, -1)
        clipboard.store()
        d = Gtk.MessageDialog(message_type=Gtk.MessageType.INFO,
                              buttons=Gtk.ButtonsType.OK,
                              text="Path copied to clipboard:\n" + icon)
        d.run(); d.destroy()

    return 0


if __name__ == "__main__":
    sys.exit(main())
