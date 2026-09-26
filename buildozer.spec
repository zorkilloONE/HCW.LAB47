[app]
title = Hard Crazy Worm
package.name = hardcrazyworm
package.domain = io.github.zorkilloone

source.dir = .
source.include_exts = py,png
source.include_patterns = main.py,assets/*.png

version = 1.0.2

requirements = python3,kivy

presplash.filename = %(source.dir)s/assets/hcw_intro.png
icon.filename = %(source.dir)s/assets/hcw_app_icon.png

orientation = portrait
fullscreen = 0

author = Luis / zorkilloONE

android.presplash_color = #000000
android.api = 36
android.minapi = 28
android.ndk = 29
android.ndk_api = 28
android.archs = arm64-v8a
android.accept_sdk_license = True
android.private_storage = True
android.allow_backup = True
android.debug_artifact = apk
android.release_artifact = apk

p4a.branch = develop
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1
