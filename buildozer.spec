[app]
title = Image Converter
package.name = imageconverter
package.domain = org.example
source.dir = .
source.include_exts = py,json
entrypoint = main.py
version = 0.1

requirements = python3,pillow,tkinterdnd2
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1

[android]
android.permissions =
android.api = 34
android.minapi = 24
android.ndk = 25b
android.sdk = 34
android.archs = arm64-v8a,armeabi-v7a
