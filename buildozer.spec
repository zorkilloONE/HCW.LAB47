[app]
title = Hard Crazy Worm
package.name = hardcrazyworm
package.domain = io.github.zorkilloone

source.dir = .
source.include_exts = py
source.include_patterns = main.py

version = 1.0.0

requirements = python3,kivy

orientation = portrait
fullscreen = 0

author = Luis / zorkilloONE

android.api = 36
android.minapi = 28
android.ndk = 29
android.ndk_api = 28
android.archs = arm64-v8a
android.accept_sdk_license = True
android.private_storage = True
android.allow_backup = True
android.debug_artifact = apk

p4a.branch = develop
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1
