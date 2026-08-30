#!/bin/bash
#
# Double-click this to make print files. Nothing to install by hand and
# nothing to type first - it checks what it needs, installs anything missing,
# and opens the window.
#
# It must stay in the same folder as print_tool.py, order.py, wl_lookup.py
# and buckets.txt. Move the whole folder, not one file out of it.

cd "$(dirname "$0")" || exit 1
clear
echo "  Wonderleaf print files"
echo "  ----------------------"
echo

if ! command -v python3 >/dev/null 2>&1; then
    echo "  Python 3 is not installed on this Mac."
    echo
    echo "  Install it from https://www.python.org/downloads/macos/"
    echo "  then double-click this again."
    echo
    read -r -p "  Press Enter to close."
    exit 1
fi

# Pillow and numpy do the image work. Checked every run rather than assumed:
# a new Mac has neither, and the error they produce otherwise is a stack
# trace that means nothing to whoever is trying to print an order.
if ! python3 -c "import PIL, numpy" >/dev/null 2>&1; then
    echo "  First run on this Mac - installing what it needs."
    echo "  This takes a minute and only happens once."
    echo
    python3 -m pip install --quiet --user Pillow numpy 2>/dev/null \
        || python3 -m pip install --quiet --user --break-system-packages Pillow numpy
    if ! python3 -c "import PIL, numpy" >/dev/null 2>&1; then
        echo
        echo "  That did not work. Open Terminal and run:"
        echo "      python3 -m pip install --user Pillow numpy"
        echo
        read -r -p "  Press Enter to close."
        exit 1
    fi
    echo "  Done."
    echo
fi

# The window needs tkinter, which some Python builds ship without. Fall back
# to the typed version rather than failing - the person still gets their files.
if python3 -c "import tkinter" >/dev/null 2>&1; then
    python3 print_tool.py
else
    echo "  (This Python has no window support - using the typed version.)"
    echo
    python3 order.py
fi
