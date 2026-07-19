#!/usr/bin/env python3
"""Replace every mipmap launcher icon in the decompiled APK with our custom icon."""

import os
import sys
import glob
from PIL import Image

SIZES = {
    'mipmap-mdpi':    48,
    'mipmap-hdpi':    72,
    'mipmap-xhdpi':   96,
    'mipmap-xxhdpi':  144,
    'mipmap-xxxhdpi': 192,
}

def main():
    if len(sys.argv) < 3:
        print("Usage: inject_icons.py <decompiled_dir> <icon_src>")
        sys.exit(1)

    decompiled_dir = sys.argv[1]
    icon_src       = sys.argv[2]

    src = Image.open(icon_src).convert('RGBA')
    replaced = 0

    for dname, size in SIZES.items():
        pattern = os.path.join(decompiled_dir, 'res', dname, '*.png')
        for f in glob.glob(pattern):
            img = src.resize((size, size), Image.LANCZOS)
            img.save(f, 'PNG')
            print(f'  Replaced: {f}  ({size}x{size})')
            replaced += 1

    if replaced == 0:
        print('WARNING: No mipmap PNGs found. Listing all PNGs in res/:')
        for root, dirs, files in os.walk(os.path.join(decompiled_dir, 'res')):
            for fn in files:
                if fn.endswith('.png'):
                    print(' ', os.path.join(root, fn))
    else:
        print(f'[+] Replaced {replaced} icon file(s).')

if __name__ == '__main__':
    main()
