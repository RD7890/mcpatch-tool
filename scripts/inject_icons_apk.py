#!/usr/bin/env python3
"""
Inject custom icon directly into an already-built (unsigned) APK zip.
Works on the APK as a zip file — no resource decompile/recompile needed.
"""

import os
import sys
import io
import glob
import zipfile
from PIL import Image

SIZES = {
    'mipmap-mdpi':    48,
    'mipmap-hdpi':    72,
    'mipmap-xhdpi':   96,
    'mipmap-xxhdpi':  144,
    'mipmap-xxxhdpi': 192,
}

def resize_to_bytes(src_image, size):
    img = src_image.resize((size, size), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, 'PNG')
    return buf.getvalue()

def main():
    if len(sys.argv) < 3:
        print("Usage: inject_icons_apk.py <input.apk> <icon.png>")
        sys.exit(1)

    apk_path  = sys.argv[1]
    icon_path = sys.argv[2]
    out_path  = apk_path + '.iconpatched'

    src = Image.open(icon_path).convert('RGBA')

    # Build a map of dname → resized bytes
    sized = {}
    for dname, size in SIZES.items():
        sized[dname] = resize_to_bytes(src, size)

    replaced = 0
    with zipfile.ZipFile(apk_path, 'r') as zin, \
         zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as zout:

        for item in zin.infolist():
            data = zin.read(item.filename)
            # Check if this entry is a mipmap PNG
            matched = False
            for dname, img_bytes in sized.items():
                if f'res/{dname}/' in item.filename and item.filename.endswith('.png'):
                    zout.writestr(item, img_bytes)
                    print(f'  Replaced: {item.filename}')
                    replaced += 1
                    matched = True
                    break
            if not matched:
                zout.writestr(item, data)

    if replaced == 0:
        print('WARNING: No mipmap PNGs found in APK. Icons not replaced.')
        # List what IS in res/ for debugging
        with zipfile.ZipFile(apk_path, 'r') as z:
            for n in z.namelist():
                if n.startswith('res/') and n.endswith('.png'):
                    print(' ', n)
    else:
        print(f'[+] Replaced {replaced} icon(s). Saving to {out_path}')

    # Replace original with patched
    os.replace(out_path, apk_path)
    print('[+] Done.')

if __name__ == '__main__':
    main()
