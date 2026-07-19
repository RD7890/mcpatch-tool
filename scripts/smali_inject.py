#!/usr/bin/env python3
"""
Smali Injector for Minecraft APK
- Loads libmaterialbinloader.so at app startup
- Adds "Powered By MaterialBin Tool" TextView at bottom-center of screen
"""

import os
import sys
import re
import glob

WATERMARK_TEXT = "Powered By MaterialBin Tool"
LIB_NAME       = "materialbinloader"

# Smali snippet that goes inside MainActivity.onCreate()
# Uses high register numbers (v10-v15) to avoid collisions with existing code.
# The .registers directive is bumped up if needed.
SMALI_INJECT = f"""
    # ── MaterialBinLoader: load native library ──────────────────────────────
    const-string v10, "{LIB_NAME}"
    invoke-static {{v10}}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V

    # ── MaterialBinLoader: add watermark TextView ────────────────────────────
    new-instance v10, Landroid/widget/TextView;
    invoke-direct {{v10, p0}}, Landroid/widget/TextView;-><init>(Landroid/content/Context;)V

    const-string v11, "{WATERMARK_TEXT}"
    invoke-virtual {{v10, v11}}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    # White text color
    const v11, -0x1
    invoke-virtual {{v10, v11}}, Landroid/widget/TextView;->setTextColor(I)V

    # Text size 12sp  (TypedValue.COMPLEX_UNIT_SP = 2)
    const/4 v11, 0x2
    const/16 v12, 0xC
    int-to-float v12, v12
    invoke-virtual {{v10, v11, v12}}, Landroid/widget/TextView;->setTextSize(IF)V

    # Black background 80% opacity = 0xCC000000 = -0x34000000
    const v11, -0x34000000
    invoke-virtual {{v10, v11}}, Landroid/widget/TextView;->setBackgroundColor(I)V

    # Padding: left=16, top=4, right=16, bottom=4
    const/16 v11, 0x10
    const/4 v12, 0x4
    invoke-virtual {{v10, v11, v12, v11, v12}}, Landroid/widget/TextView;->setPadding(IIII)V

    # Get Window DecorView
    invoke-virtual {{p0}}, Landroid/app/Activity;->getWindow()Landroid/view/Window;
    move-result-object v11
    invoke-virtual {{v11}}, Landroid/view/Window;->getDecorView()Landroid/view/View;
    move-result-object v11
    check-cast v11, Landroid/widget/FrameLayout;

    # LayoutParams: WRAP_CONTENT x WRAP_CONTENT
    const v12, -0x2
    new-instance v13, Landroid/widget/FrameLayout$LayoutParams;
    invoke-direct {{v13, v12, v12}}, Landroid/widget/FrameLayout$LayoutParams;-><init>(II)V

    # gravity = BOTTOM(0x50) | CENTER_HORIZONTAL(0x1) = 0x51
    const/16 v12, 0x51
    iput v12, v13, Landroid/widget/FrameLayout$LayoutParams;->gravity:I

    # bottomMargin = 48
    const/16 v12, 0x30
    iput v12, v13, Landroid/widget/FrameLayout$LayoutParams;->bottomMargin:I

    # addView
    invoke-virtual {{v11, v10, v13}}, Landroid/widget/FrameLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V
    # ────────────────────────────────────────────────────────────────────────
"""


def bump_registers(method_text: str, minimum: int = 16) -> str:
    """Ensure .registers is at least `minimum` so our v10-v15 are valid."""
    def replacer(m):
        current = int(m.group(1))
        new_val = max(current, minimum)
        return f".registers {new_val}"
    return re.sub(r"\.registers\s+(\d+)", replacer, method_text)


def inject_into_method(method_text: str) -> str:
    """Inject our smali block just before the last return-void in onCreate."""
    # Find last return-void
    idx = method_text.rfind("return-void")
    if idx == -1:
        return method_text  # nothing to do
    return method_text[:idx] + SMALI_INJECT + "\n    " + method_text[idx:]


def patch_main_activity(smali_path: str) -> bool:
    with open(smali_path, "r", encoding="utf-8") as f:
        src = f.read()

    if LIB_NAME in src:
        print(f"  Already patched: {smali_path}")
        return False

    # Split into methods, find onCreate
    # Match from ".method ... onCreate" to ".end method"
    pattern = re.compile(
        r"(\.method\s+[^\n]*\bonCreate\b.*?\.end\s+method)",
        re.DOTALL
    )
    match = pattern.search(src)
    if not match:
        print(f"  WARNING: onCreate not found in {smali_path}")
        return False

    original_method = match.group(1)
    patched_method  = bump_registers(original_method)
    patched_method  = inject_into_method(patched_method)

    new_src = src[:match.start()] + patched_method + src[match.end():]

    with open(smali_path, "w", encoding="utf-8") as f:
        f.write(new_src)

    print(f"  Patched: {smali_path}")
    return True


def find_main_activity(decompiled_dir: str) -> list:
    """Search for MainActivity.smali across all smali_classes* folders."""
    candidates = []
    for pattern in [
        os.path.join(decompiled_dir, "smali*", "com", "mojang", "minecraftpe", "MainActivity.smali"),
        os.path.join(decompiled_dir, "smali*", "com", "mojang", "minecraftpe", "*.smali"),
    ]:
        candidates.extend(glob.glob(pattern))

    # Prefer the exact MainActivity match
    exact = [p for p in candidates if os.path.basename(p) == "MainActivity.smali"]
    return exact if exact else candidates[:1]


def main():
    if len(sys.argv) < 2:
        print("Usage: smali_inject.py <decompiled_dir>")
        sys.exit(1)

    decompiled_dir = sys.argv[1]
    print(f"[*] Target directory: {decompiled_dir}")

    targets = find_main_activity(decompiled_dir)
    if not targets:
        print("[ERROR] Could not locate MainActivity.smali — check decompiled dir structure.")
        sys.exit(1)

    patched_any = False
    for path in targets:
        print(f"[*] Processing: {path}")
        if patch_main_activity(path):
            patched_any = True

    if patched_any:
        print("[+] Smali injection successful.")
    else:
        print("[!] No files were modified (already patched or no match).")


if __name__ == "__main__":
    main()
