# MCPE MaterialBin Patcher

A GitHub Actions workflow that patches Minecraft Bedrock APK with MaterialBinLoader for custom shader support.

## Usage

1. Go to **Actions** tab
2. Select **Patch Minecraft APK** workflow
3. Click **Run workflow**
4. Paste your Minecraft APK download URL
5. (Optional) Change the MBL version
6. Wait for it to finish — patched APK will be in **Releases**

## What it does

- Downloads the original Minecraft APK
- Injects `libmaterialbinloader.so` (arm64-v8a)
- Adds "Powered By MaterialBin Tool" text on the start screen
- Re-signs with a debug keystore
- Uploads patched APK as a GitHub Release

## Requirements

- Only supports **64-bit (arm64-v8a)** Android devices (Android 8.0+)
- You must provide a direct download link to the official Minecraft APK

## Credits

- [ddf8196/MaterialBinLoader](https://github.com/ddf8196/MaterialBinLoader) — the core MBL library
- [mcbegamerxx954/mtbinloader2](https://github.com/mcbegamerxx954/mtbinloader2) — improved MBL2 library
