# ============================================================================
# HARD CRAZY WORM (HCW)
# Juego Arcade Survival
#
# Creador y desarrollador original: Luis
# GitHub: zorkilloONE
# Asistencia de desarrollo y balance: Emely
# Apoyo creativo: Toñita
# Control de calidad: Pungy
#
# 3 IA + 1 Humano = Juego Arcade Survival
# ============================================================================

__author__ = "Luis"
__github__ = "zorkilloONE"

import json
import math
import os
import random
import struct
import wave

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.core.text import Label as CoreLabel
from kivy.graphics import Color, Ellipse, Line, Rectangle, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.utils import platform

if platform not in ("android", "ios"):
    Window.size = (400, 700)

ARENA_BG = (0.04, 0.07, 0.08, 1)
HUD_BG = (0.05, 0.09, 0.08, 1)
TEXT_DARK = (0.86, 0.93, 0.88, 1)
WHITE = (1, 1, 1, 1)
SPACE_BG = (0.02, 0.02, 0.06, 1)
GREEN_ON = (0.14, 0.78, 0.32, 0.75)
GREEN_OFF = (0.07, 0.28, 0.14, 0.75)


def style_night_popup(popup):
    popup.background = ""
    popup.background_color = (0.02, 0.05, 0.04, 0.32)
    popup.title_color = (0.45, 1.00, 0.58, 1)
    popup.separator_color = (0.18, 0.78, 0.36, 0.55)
    popup.title_size = "18sp"


def ghost_text_btn(text, font_size="16sp", height=None, color=None, **kwargs):
    btn = Button(
        text=text,
        font_size=font_size,
        bold=True,
        italic=True,
        color=color or (0.45, 1.00, 0.55, 1),
        background_normal="",
        background_down="",
        background_color=(0, 0, 0, 0),
        **kwargs
    )
    if height is not None:
        btn.size_hint_y = None
        btn.height = height
    return btn

STAR_SPECS = [
    (0.08, 0.92, 4), (0.22, 0.84, 3), (0.78, 0.88, 5),
    (0.90, 0.80, 3), (0.12, 0.68, 2), (0.35, 0.74, 4),
    (0.64, 0.72, 3), (0.86, 0.62, 4), (0.10, 0.50, 4),
    (0.72, 0.52, 3), (0.28, 0.42, 2), (0.88, 0.38, 4),
    (0.16, 0.26, 3), (0.48, 0.20, 5), (0.76, 0.18, 3),
]


class RoundedButton(Button):
    def __init__(self, bg_color=(0.18, 0.42, 0.18, 1), radius=28, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        self.radius_value = radius
        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)
        with self.canvas.before:
            self._btn_color = Color(*self.bg_color)
            self._btn_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius_value])
        self.bind(pos=self._update_canvas, size=self._update_canvas)

    def _update_canvas(self, *_args):
        self._btn_rect.pos = self.pos
        self._btn_rect.size = self.size

    def on_press(self):
        r, g, b, a = self.bg_color
        self._btn_color.rgba = (max(0, r - 0.08), max(0, g - 0.08), max(0, b - 0.08), a)
        return super().on_press()

    def on_release(self):
        self._btn_color.rgba = self.bg_color
        try:
            SoundManager.play("click")
        except Exception:
            pass
        return super().on_release()


class ArrowButton(ButtonBehavior, Widget):
    def __init__(self, direction="up", **kwargs):
        super().__init__(**kwargs)
        self.direction = direction
        with self.canvas.before:
            self.pad_color = Color(0.07, 0.16, 0.10, 0.92)
            self.pad = Ellipse(pos=self.pos, size=self.size)
        with self.canvas:
            self.arrow_color = Color(0.55, 1.0, 0.62, 1)
            self.arrow = Line(points=[], width=3.6, joint="round", cap="round")
        self.bind(pos=self._redraw, size=self._redraw)
        self._redraw()

    def _redraw(self, *_args):
        pad = min(self.width, self.height) * 0.78
        self.pad.pos = (self.center_x - pad / 2, self.center_y - pad / 2)
        self.pad.size = (pad, pad)
        cx = self.x + self.width / 2
        cy = self.y + self.height / 2
        s = min(self.width, self.height) * 0.24
        if self.direction == "up":
            pts = [cx, cy+s, cx-s, cy, cx-s*0.38, cy, cx-s*0.38, cy-s,
                   cx+s*0.38, cy-s, cx+s*0.38, cy, cx+s, cy, cx, cy+s]
        elif self.direction == "down":
            pts = [cx, cy-s, cx-s, cy, cx-s*0.38, cy, cx-s*0.38, cy+s,
                   cx+s*0.38, cy+s, cx+s*0.38, cy, cx+s, cy, cx, cy-s]
        elif self.direction == "left":
            pts = [cx-s, cy, cx, cy+s, cx, cy+s*0.38, cx+s, cy+s*0.38,
                   cx+s, cy-s*0.38, cx, cy-s*0.38, cx, cy-s, cx-s, cy]
        else:
            pts = [cx+s, cy, cx, cy+s, cx, cy+s*0.38, cx-s, cy+s*0.38,
                   cx-s, cy-s*0.38, cx, cy-s*0.38, cx, cy-s, cx+s, cy]
        self.arrow.points = pts

    def on_press(self):
        self.arrow_color.rgba = (0.85, 1.0, 0.55, 1)

    def on_release(self):
        self.arrow_color.rgba = (0.55, 1.0, 0.62, 1)


class MenuButton(ButtonBehavior, Widget):
    """Phone-friendly circular pause button with a large touch target."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            self.bg_color = Color(0.08, 0.18, 0.12, 0.94)
            self.bg_circle = Ellipse(pos=self.pos, size=self.size)
            self.glow_color = Color(0.20, 1.0, 0.42, 0.18)
            self.glow_ring = Line(circle=(0, 0, 1), width=2.0)
        with self.canvas:
            self.icon_color = Color(1, 1, 1, 1)
            # Pungy: pause glyph (two vertical bars), not a hamburger — the icon
            # must read as "pause" to match the tutorial text.
            self.pause_bars = [
                Line(points=[], width=5.0, cap="round"),
                Line(points=[], width=5.0, cap="round"),
            ]
        self.bind(pos=self._redraw, size=self._redraw)
        self._redraw()

    def _redraw(self, *_args):
        self.bg_circle.pos = self.pos
        self.bg_circle.size = self.size
        cx = self.x + self.width / 2
        cy = self.y + self.height / 2
        self.glow_ring.circle = (cx, cy, min(self.width, self.height) / 2 + 4)
        bar_gap = min(self.width, self.height) * 0.11
        bar_len = min(self.width, self.height) * 0.17
        for bar, x in zip(self.pause_bars, (cx - bar_gap, cx + bar_gap)):
            bar.points = [x, cy - bar_len, x, cy + bar_len]

    def collide_point(self, x, y):
        pad = max(14.0, min(self.width, self.height) * 0.22)
        return (self.x - pad <= x <= self.right + pad and
                self.y - pad <= y <= self.top + pad)

    def on_press(self):
        self.bg_color.rgba = (0.19, 0.24, 0.19, 0.96)
        self.glow_color.rgba = (0.45, 0.75, 1.0, 0.30)
        self.icon_color.rgba = (0.92, 0.96, 1.0, 1)

    def on_release(self):
        self.bg_color.rgba = (0.26, 0.31, 0.25, 0.92)
        self.glow_color.rgba = (0.45, 0.75, 1.0, 0.16)
        self.icon_color.rgba = (1, 1, 1, 1)
        try:
            SoundManager.play("click")
        except Exception:
            pass


class HungerBar(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.value = 100.0
        with self.canvas:
            Color(0.04, 0.08, 0.06, 0.92)
            self.background = RoundedRectangle(pos=self.pos, size=self.size, radius=[9])
            self.track_glow = Color(0.12, 0.85, 0.38, 0.18)
            self.track_line = Line(rounded_rectangle=(0, 0, 1, 1, 9), width=1.15)
            self.fill_color = Color(0.04, 0.42, 0.16, 1)
            self.fill = RoundedRectangle(pos=self.pos, size=self.size, radius=[9])
            self.fill_hi_color = Color(0.35, 1.00, 0.55, 0.55)
            self.fill_hi = RoundedRectangle(pos=self.pos, size=self.size, radius=[8])
            # Pungy ricura: a tiny worm face rides the fill's leading edge.
            self._eye_color = Color(1, 1, 1, 0.95)
            self._eye1 = Ellipse(size=(0, 0))
            self._eye2 = Ellipse(size=(0, 0))
            self._pupil_color = Color(0.05, 0.08, 0.05, 1)
            self._pupil1 = Ellipse(size=(0, 0))
            self._pupil2 = Ellipse(size=(0, 0))
        self.bind(pos=self._update, size=self._update)
        self._update()

    def set_value(self, value):
        self.value = max(0.0, min(100.0, float(value)))
        if self.value <= 10:
            self.fill_color.rgba = (0.55, 0.04, 0.06, 1)
            self.fill_hi_color.rgba = (1.00, 0.28, 0.28, 0.70)
            self.track_glow.rgba = (1.00, 0.18, 0.18, 0.35)
        elif self.value <= 25:
            self.fill_color.rgba = (0.55, 0.22, 0.02, 1)
            self.fill_hi_color.rgba = (1.00, 0.62, 0.18, 0.65)
            self.track_glow.rgba = (1.00, 0.50, 0.10, 0.28)
        elif self.value <= 50:
            self.fill_color.rgba = (0.48, 0.38, 0.02, 1)
            self.fill_hi_color.rgba = (1.00, 0.92, 0.25, 0.60)
            self.track_glow.rgba = (0.95, 0.85, 0.15, 0.22)
        else:
            self.fill_color.rgba = (0.04, 0.42, 0.16, 1)
            self.fill_hi_color.rgba = (0.40, 1.00, 0.58, 0.58)
            self.track_glow.rgba = (0.18, 1.00, 0.42, 0.22)
        self._update()

    def _update(self, *_args):
        self.background.pos = self.pos
        self.background.size = self.size
        pad = 2
        available_w = max(0, self.width - pad * 2)
        fill_w = available_w * (self.value / 100.0)
        fill_h = max(0, self.height - pad * 2)
        self.fill.pos = (self.x + pad, self.y + pad)
        self.fill.size = (fill_w, fill_h)
        hi_h = max(0, fill_h * 0.42)
        self.fill_hi.pos = (self.x + pad, self.y + pad + fill_h - hi_h)
        self.fill_hi.size = (fill_w, hi_h)
        self.track_line.rounded_rectangle = (self.x + 0.5, self.y + 0.5, max(1, self.width - 1), max(1, self.height - 1), 9)
        # The face only shows when the fill is wide enough to hold it.
        if fill_w >= 34 and fill_h >= 18:
            r = min(5.0, fill_h * 0.17)
            ex = self.x + pad + fill_w - r * 2.8
            cy = self.y + self.height / 2
            pr = r * 0.45
            for eye, pupil, dy in ((self._eye1, self._pupil1, r * 1.2),
                                   (self._eye2, self._pupil2, -r * 1.2)):
                eye.pos = (ex - r, cy + dy - r)
                eye.size = (r * 2, r * 2)
                pupil.pos = (ex + r * 0.4 - pr, cy + dy - pr)
                pupil.size = (pr * 2, pr * 2)
        else:
            for part in (self._eye1, self._eye2, self._pupil1, self._pupil2):
                part.size = (0, 0)


class WormLogoMark(Widget):
    """Tiny in-app vector mascot/logo mark; no external art asset required."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._redraw, size=self._redraw)
        self._redraw()

    def _redraw(self, *_args):
        self.canvas.clear()
        if self.width <= 0 or self.height <= 0:
            return
        s = min(self.width, self.height)
        cx = self.center_x
        cy = self.center_y
        with self.canvas:
            # Blue orbit echoes the night/neon menu language.
            Color(0.12, 0.58, 1.00, 0.42)
            Line(circle=(cx, cy, s * 0.42), width=1.4)
            # Three body beads + solid head, matching the actual character.
            body = [(-0.18, -0.03), (-0.03, 0.05), (0.12, 0.01)]
            for ox, oy in body:
                Color(0.08, 0.50, 0.08, 1)
                Ellipse(pos=(cx + ox*s - s*0.12, cy + oy*s - s*0.12), size=(s*0.24, s*0.24))
                Color(0.45, 0.90, 0.45, 0.45)
                Ellipse(pos=(cx + ox*s - s*0.05, cy + oy*s + s*0.01), size=(s*0.09, s*0.06))
            hx, hy = cx + 0.28*s, cy + 0.05*s
            Color(0.00, 0.30, 0.00, 1)
            Ellipse(pos=(hx-s*0.14, hy-s*0.14), size=(s*0.28, s*0.28))
            Color(0.02, 0.02, 0.02, 1)
            Ellipse(pos=(hx+s*0.02, hy+s*0.035), size=(s*0.035, s*0.035))
            Ellipse(pos=(hx+s*0.02, hy-s*0.065), size=(s*0.035, s*0.035))


class GearButton(ButtonBehavior, Widget):
    """Circular settings control drawn in canvas — no extra asset."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            self.bg_color = Color(0.14, 0.16, 0.22, 0.94)
            self.bg_circle = Ellipse(pos=self.pos, size=self.size)
            self.icon_color = Color(1, 1, 1, 0.96)
            self.ring = Line(circle=(0, 0, 1), width=1.8)
            self.hub = Line(circle=(0, 0, 1), width=1.6)
            self.teeth = [Line(points=[], width=2.4, cap="round") for _ in range(6)]
        self.bind(pos=self._redraw, size=self._redraw)
        self._redraw()

    def _redraw(self, *_args):
        self.bg_circle.pos = self.pos
        self.bg_circle.size = self.size
        cx = self.x + self.width / 2
        cy = self.y + self.height / 2
        r = min(self.width, self.height) / 2
        self.ring.circle = (cx, cy, r * 0.28)
        self.hub.circle = (cx, cy, r * 0.12)
        tooth = r * 0.38
        inner = r * 0.22
        for i, line in enumerate(self.teeth):
            ang = (math.pi / 3.0) * i
            line.points = [
                cx + math.cos(ang) * inner, cy + math.sin(ang) * inner,
                cx + math.cos(ang) * tooth, cy + math.sin(ang) * tooth,
            ]

    def collide_point(self, x, y):
        pad = max(12.0, min(self.width, self.height) * 0.22)
        return (self.x - pad <= x <= self.right + pad and
                self.y - pad <= y <= self.top + pad)

    def on_press(self):
        self.bg_color.rgba = (0.20, 0.24, 0.32, 0.98)
        self.icon_color.rgba = (0.75, 0.90, 1.0, 1)

    def on_release(self):
        self.bg_color.rgba = (0.14, 0.16, 0.22, 0.94)
        self.icon_color.rgba = (1, 1, 1, 0.96)
        try:
            SoundManager.play("click")
        except Exception:
            pass


class NeonTitle(FloatLayout):
    """
    R7 deterministic arcade title.

    R6 used nested Kivy Labels for the neon face. On the phone the tested build could
    still present the title as the old plain white header. R7 rasterizes the title
    through CoreLabel into explicit canvas textures, so the green face, dark edge and
    cyan halo are owned by this widget itself instead of relying on inherited Label UI.
    """
    def __init__(self, text="HARD CRAZY WORM", face_color=(0.20, 0.96, 0.38, 1),
                 edge_color=(0.015, 0.04, 0.06, 1), halo_color=(0.12, 1.00, 0.42, 1),
                 glow_color=(0.08, 0.90, 1.00, 1), blink=False, blink_speed=5.0,
                 font_size=29, **kwargs):
        super().__init__(**kwargs)
        self._text = text
        self._face_color = face_color
        self._edge_color = edge_color
        self._halo_color = halo_color
        self._glow_rgb = glow_color
        self._blink = blink
        self._blink_speed = blink_speed
        self._font_size = font_size
        self._phase = 0.0
        self._main_texture = None
        self._glow_texture = None

        with self.canvas:
            # Halo is rendered slightly larger than the face and breathes slowly.
            self._glow_color = Color(1, 1, 1, 0.34)
            self._glow_rect = Rectangle(pos=self.pos, size=(1, 1))
            self._main_color = Color(1, 1, 1, 1)
            self._main_rect = Rectangle(pos=self.pos, size=(1, 1))

        self.bind(pos=self._layout_title, size=self._layout_title)
        self._build_textures()
        self._layout_title()
        self._pulse_event = Clock.schedule_interval(self._pulse, 0.05)

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        value = str(value)
        if value == self._text:
            return
        self._text = value
        self._build_textures()
        self._layout_title()

    def _build_textures(self):
        # Solid front face with a dark outline.
        face = max(12, int(self._font_size))
        main = CoreLabel(
            text=self._text,
            font_size=sp(face),
            bold=True,
            italic=True,
            color=self._face_color,
            outline_width=2,
            outline_color=self._edge_color,
        )
        main.refresh()
        self._main_texture = main.texture

        # Halo texture. Alpha is controlled separately by _glow_color.
        glow = CoreLabel(
            text=self._text,
            font_size=sp(face + 1),
            bold=True,
            italic=True,
            color=self._glow_rgb,
            outline_width=4,
            outline_color=self._halo_color,
        )
        glow.refresh()
        self._glow_texture = glow.texture
        self._main_rect.texture = self._main_texture
        self._glow_rect.texture = self._glow_texture

    @staticmethod
    def _fit_texture(texture, max_w, max_h):
        if texture is None:
            return (1.0, 1.0)
        tw, th = texture.size
        if tw <= 0 or th <= 0:
            return (1.0, 1.0)
        scale = min(1.0, max_w / float(tw), max_h / float(th))
        return (max(1.0, tw * scale), max(1.0, th * scale))

    def _layout_title(self, *_args):
        main_w, main_h = self._fit_texture(
            self._main_texture,
            max(1.0, self.width * 0.88),
            max(1.0, self.height * 0.64),
        )
        glow_w, glow_h = self._fit_texture(
            self._glow_texture,
            max(1.0, self.width * 0.91),
            max(1.0, self.height * 0.69),
        )
        self._main_rect.size = (main_w, main_h)
        self._main_rect.pos = (self.center_x - main_w / 2, self.center_y - main_h / 2)
        self._glow_rect.size = (glow_w, glow_h)
        self._glow_rect.pos = (self.center_x - glow_w / 2, self.center_y - glow_h / 2)

    def _pulse(self, dt):
        self._phase = (self._phase + dt) % 10.0
        if self._blink:
            # Pungy: neon-sign blink — the halo breathes deep and fast, the face
            # dips slightly with it so the whole title reads as blinking neon.
            wave = (math.sin(self._phase * self._blink_speed * math.tau) + 1.0) * 0.5
            self._glow_color.a = 0.15 + 0.75 * wave
            self._main_color.a = 0.72 + 0.28 * wave
        else:
            pulse = (math.sin((self._phase / 1.9) * math.tau) + 1.0) * 0.5
            # Slow glow only. The green title face remains solid and fully opaque.
            self._glow_color.a = 0.20 + 0.36 * pulse

    def stop_pulse(self):
        if self._pulse_event is not None:
            self._pulse_event.cancel()
            self._pulse_event = None


class TappableNeon(ButtonBehavior, NeonTitle):
    """Neon title that can start the game when touched."""
    def on_release(self):
        try:
            SoundManager.play("click")
        except Exception:
            pass
        return super().on_release()


class TutorialIcon(Widget):
    """Tiny canvas icon used by the tutorial so instructions are not a wall of text."""
    def __init__(self, icon_color=(1, 1, 1, 1), style="orb", **kwargs):
        super().__init__(**kwargs)
        self.icon_color = icon_color
        self.style = style
        self.bind(pos=self._redraw, size=self._redraw)
        self._redraw()

    def _redraw(self, *_args):
        self.canvas.clear()
        cx = self.x + self.width / 2
        cy = self.y + self.height / 2
        s = min(self.width, self.height)
        with self.canvas:
            if self.style == "food":
                Color(0.92, 1.00, 0.72, 0.20)
                Ellipse(pos=(cx-s*0.42, cy-s*0.42), size=(s*0.84, s*0.84))
                Color(0.95, 1.00, 0.72, 1)
                Ellipse(pos=(cx-s*0.27, cy-s*0.27), size=(s*0.54, s*0.54))
                Color(1, 1, 1, 0.90)
                Ellipse(pos=(cx-s*0.11, cy+s*0.05), size=(s*0.12, s*0.12))
            else:
                Color(*self.icon_color)
                Ellipse(pos=(cx-s*0.30, cy-s*0.30), size=(s*0.60, s*0.60))
                if self.style == "strange":
                    Color(0.84, 0.38, 0.92, 0.55)
                    Line(circle=(cx, cy, s*0.39), width=1.2)
                    Color(1, 1, 1, 0.65)
                    Line(points=[cx-s*0.48, cy+s*0.18, cx-s*0.32, cy+s*0.18], width=1.0)
                    Line(points=[cx-s*0.50, cy, cx-s*0.28, cy], width=1.0)



class SpaceScreen(Screen):
    def build_space_background(self, root):
        with root.canvas.before:
            Color(*SPACE_BG)
            self.bg_rect = Rectangle(pos=root.pos, size=root.size)
            self.star_shapes = []
            for _sx, _sy, size in STAR_SPECS:
                Color(1, 1, 1, 0.85)
                self.star_shapes.append(Ellipse(pos=(0, 0), size=(size, size)))
        root.bind(pos=self._update_space_background, size=self._update_space_background)

    def _update_space_background(self, instance, _value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size
        for i, (sx, sy, size) in enumerate(STAR_SPECS):
            self.star_shapes[i].pos = (instance.x + instance.width*sx, instance.y + instance.height*sy)
            self.star_shapes[i].size = (size, size)


class RecordManager:
    # Fresh scoreboard namespace for the polished build; old test AAA entries stay archived.
    FILE_NAME = "records_r4.json"

    @classmethod
    def file_path(cls):
        folder = App.get_running_app().user_data_dir
        os.makedirs(folder, exist_ok=True)
        return os.path.join(folder, cls.FILE_NAME)

    @classmethod
    def load_records(cls):
        try:
            with open(cls.file_path(), "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return []

    @classmethod
    def save_record(cls, initials, score):
        records = cls.load_records()
        records.append({"initials": (initials or "AAA").upper()[:3], "score": int(score)})
        records = sorted(records, key=lambda item: item.get("score", 0), reverse=True)[:5]
        try:
            with open(cls.file_path(), "w", encoding="utf-8") as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
        except OSError:
            pass


class SettingsManager:
    FILE_NAME = "settings.json"
    DEFAULTS = {
        "music_enabled": True,
        "sfx_enabled": True,
        "volume": 0.70,
    }
    _data = None

    @classmethod
    def file_path(cls):
        app = App.get_running_app()
        if app is None:
            return None
        folder = app.user_data_dir
        os.makedirs(folder, exist_ok=True)
        return os.path.join(folder, cls.FILE_NAME)

    @classmethod
    def load(cls):
        if cls._data is not None:
            return cls._data

        path = cls.file_path()
        if path is None:
            return dict(cls.DEFAULTS)

        data = dict(cls.DEFAULTS)
        try:
            with open(path, "r", encoding="utf-8") as f:
                stored = json.load(f)
            if isinstance(stored, dict):
                data.update(stored)
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            pass

        data["music_enabled"] = bool(data.get("music_enabled", True))
        data["sfx_enabled"] = bool(data.get("sfx_enabled", True))
        try:
            data["volume"] = max(0.0, min(1.0, float(data.get("volume", 0.70))))
        except (TypeError, ValueError):
            data["volume"] = 0.70

        cls._data = data
        return cls._data

    @classmethod
    def get(cls, key):
        return cls.load().get(key, cls.DEFAULTS.get(key))

    @classmethod
    def set(cls, key, value):
        data = cls.load()
        data[key] = value
        cls._data = data

        path = cls.file_path()
        if path is None:
            return

        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except OSError:
            pass


class SaveGameManager:
    FILE_NAME = "savegame.json"
    TEMP_FILE_NAME = "savegame.tmp"
    SAVE_VERSION = 2

    @classmethod
    def file_path(cls):
        app = App.get_running_app()
        if app is None:
            return None
        folder = app.user_data_dir
        os.makedirs(folder, exist_ok=True)
        return os.path.join(folder, cls.FILE_NAME)

    @classmethod
    def temp_path(cls):
        app = App.get_running_app()
        if app is None:
            return None
        folder = app.user_data_dir
        os.makedirs(folder, exist_ok=True)
        return os.path.join(folder, cls.TEMP_FILE_NAME)

    @classmethod
    def load(cls):
        path = cls.file_path()
        if path is None:
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                return None
            if data.get("save_version") != cls.SAVE_VERSION:
                return None
            state = data.get("state")
            return data if isinstance(state, dict) else None
        except (FileNotFoundError, json.JSONDecodeError, OSError, TypeError, ValueError):
            return None

    @classmethod
    def has_valid_save(cls):
        return cls.load() is not None

    @classmethod
    def save(cls, state):
        path = cls.file_path()
        temp = cls.temp_path()
        if path is None or temp is None:
            return False

        payload = {
            "save_version": cls.SAVE_VERSION,
            "state": state,
        }
        try:
            with open(temp, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
                f.flush()
                try:
                    os.fsync(f.fileno())
                except OSError:
                    pass
            os.replace(temp, path)
            return True
        except (OSError, TypeError, ValueError):
            try:
                if os.path.exists(temp):
                    os.remove(temp)
            except OSError:
                pass
            return False

    @classmethod
    def delete(cls):
        for path in (cls.file_path(), cls.temp_path()):
            if path is None:
                continue
            try:
                if os.path.exists(path):
                    os.remove(path)
            except OSError:
                pass


class SoundManager:
    """Small self-contained retro SFX system; no external audio files are required."""
    _cache = {}
    _prepared = False
    SPECS = {
        "click": (520, 0.045, 0.12),
        "eat": (760, 0.060, 0.18),
        "bonus": (1080, 0.095, 0.18),
        "death": (165, 0.260, 0.22),
    }
    _music = None
    _music_position = 0.0
    _music_suspended = False
    MUSIC_GAIN = 0.63

    @classmethod
    def _folder(cls):
        app = App.get_running_app()
        if app is None:
            return None
        folder = os.path.join(app.user_data_dir, "sfx")
        os.makedirs(folder, exist_ok=True)
        return folder

    @classmethod
    def _write_tone(cls, path, frequency, duration, amplitude):
        sample_rate = 22050
        count = max(1, int(sample_rate * duration))
        fade_in = max(1, int(sample_rate * 0.008))
        fade_out = max(1, int(sample_rate * 0.025))
        frames = bytearray()
        for i in range(count):
            attack = min(1.0, i / fade_in)
            release = min(1.0, (count - i) / fade_out)
            envelope = max(0.0, min(attack, release))
            value = int(32767 * amplitude * envelope * math.sin(2.0 * math.pi * frequency * i / sample_rate))
            frames.extend(struct.pack("<h", value))
        with wave.open(path, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(bytes(frames))

    @classmethod
    def _write_music_loop(cls, path):
        """Arcade-survival loop with a clear 120 BPM pulse. Still one-file portable."""
        sample_rate = 11025
        duration = 8.0
        count = int(sample_rate * duration)
        beat = 0.5
        eighth = beat / 2.0
        bass_notes = (
            110.00, 110.00, 130.81, 110.00,
            98.00, 98.00, 130.81, 146.83,
            110.00, 110.00, 164.81, 130.81,
            98.00, 87.31, 110.00, 130.81,
        )
        lead_notes = (
            440.00, 0.0, 523.25, 0.0, 440.00, 392.00, 0.0, 523.25,
            440.00, 0.0, 659.25, 523.25, 392.00, 0.0, 440.00, 349.23,
        )
        frames = bytearray()
        edge = 0.07
        tau = 2.0 * math.pi
        for i in range(count):
            t = i / sample_rate
            step = int(t / eighth) % 16
            local = (t % eighth) / eighth
            qlocal = (t % beat) / beat
            q = int(t / beat) % 4

            kick = 0.0
            if qlocal < 0.14:
                kick = math.sin(tau * 60.0 * t) * (1.0 - qlocal / 0.14) * 0.62

            snare = 0.0
            if q in (1, 3) and qlocal < 0.09:
                snare = math.sin(tau * 175.0 * t) * (1.0 - qlocal / 0.09) * 0.28

            bass_env = (1.0 - local) ** 1.35
            bass = math.sin(tau * bass_notes[step] * t) * bass_env * 0.40

            lead = 0.0
            lead_n = lead_notes[step]
            if lead_n > 0 and local < 0.50:
                lead_env = math.sin(math.pi * (local / 0.50))
                lead = math.sin(tau * lead_n * t) * lead_env * 0.24
                lead += math.sin(tau * lead_n * 2.0 * t) * lead_env * 0.06

            drone = math.sin(tau * 55.0 * t) * 0.10
            edge_env = min(1.0, t / edge, (duration - t) / edge)
            sample = (kick + snare + bass + lead + drone) * 0.30 * max(0.0, edge_env)
            value = int(max(-1.0, min(1.0, sample)) * 32767)
            frames.extend(struct.pack("<h", value))
        with wave.open(path, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(bytes(frames))

    @classmethod
    def ensure_assets(cls):
        if cls._prepared:
            return
        cls._prepared = True
        folder = cls._folder()
        if folder is None:
            return
        for name, (freq, duration, amp) in cls.SPECS.items():
            path = os.path.join(folder, f"{name}.wav")
            try:
                if not os.path.exists(path):
                    cls._write_tone(path, freq, duration, amp)
            except OSError:
                continue
        music_path = os.path.join(folder, "arcade_survival_loop_p2.wav")
        try:
            if not os.path.exists(music_path):
                cls._write_music_loop(music_path)
        except OSError:
            pass

    @classmethod
    def play(cls, name):
        if not SettingsManager.get("sfx_enabled"):
            return
        volume = max(0.0, min(1.0, float(SettingsManager.get("volume"))))
        if volume <= 0:
            return
        cls.ensure_assets()
        folder = cls._folder()
        if folder is None:
            return
        sound = cls._cache.get(name)
        if sound is None:
            try:
                sound = SoundLoader.load(os.path.join(folder, f"{name}.wav"))
            except Exception:
                sound = None
            cls._cache[name] = sound
        if sound is not None:
            try:
                sound.stop()
                sound.volume = volume
                sound.play()
            except Exception:
                pass

    @classmethod
    def _music_path(cls):
        folder = cls._folder()
        return os.path.join(folder, "arcade_survival_loop_p2.wav") if folder else None

    @classmethod
    def update_music_volume(cls):
        if cls._music is None:
            return
        try:
            master = max(0.0, min(1.0, float(SettingsManager.get("volume"))))
            cls._music.volume = master * cls.MUSIC_GAIN
        except Exception:
            pass

    @classmethod
    def start_music(cls, resume_position=None):
        if not SettingsManager.get("music_enabled"):
            return
        cls.ensure_assets()
        path = cls._music_path()
        if path is None:
            return
        if cls._music is None:
            try:
                cls._music = SoundLoader.load(path)
                if cls._music is not None:
                    cls._music.loop = True
            except Exception:
                cls._music = None
        if cls._music is None:
            return
        cls.update_music_volume()
        try:
            if getattr(cls._music, "state", "stop") != "play":
                cls._music.play()
                pos = cls._music_position if resume_position is None else resume_position
                if pos and pos > 0:
                    Clock.schedule_once(lambda _dt: cls._safe_music_seek(pos), 0.08)
            cls._music_suspended = False
        except Exception:
            pass

    @classmethod
    def _safe_music_seek(cls, position):
        if cls._music is None:
            return
        try:
            cls._music.seek(max(0.0, float(position)))
        except Exception:
            pass

    @classmethod
    def stop_music(cls, reset_position=True):
        if cls._music is not None:
            try:
                if not reset_position:
                    pos = cls._music.get_pos()
                    if pos is not None and pos >= 0:
                        cls._music_position = float(pos)
                cls._music.stop()
            except Exception:
                pass
        if reset_position:
            cls._music_position = 0.0
        cls._music_suspended = False

    @classmethod
    def suspend_music(cls):
        if cls._music is None:
            cls._music_suspended = True
            return
        try:
            pos = cls._music.get_pos()
            if pos is not None and pos >= 0:
                cls._music_position = float(pos)
            cls._music.stop()
        except Exception:
            pass
        cls._music_suspended = True

    @classmethod
    def resume_music(cls):
        if cls._music_suspended and SettingsManager.get("music_enabled"):
            cls.start_music(cls._music_position)


TEXTS = {
    "es": {
        "tagline": "Sobrevive al hambre.",
        "start": "INICIAR JUEGO",
        "how": "CÓMO JUGAR",
        "credits": "CRÉDITOS",
        "settings": "CONFIGURACIÓN",
        "records": "VER RÉCORDS",
        "records_title": "RÉCORDS",
        "close": "CERRAR",
        "continue_game": "CONTINUAR PARTIDA",
        "pause": "PAUSA",
        "resume": "CONTINUAR",
        "save_exit": "GUARDAR Y SALIR",
        "saved_game": "PARTIDA GUARDADA",
        "save_status": "Progreso guardado automáticamente.",
        "new_game_warning": "Ya existe una partida guardada. Iniciar una nueva reemplazará ese progreso.",
        "new_game_confirm": "NUEVA PARTIDA",
        "cancel": "CANCELAR",
        "top_scores": "=== MEJORES PUNTAJES ===",
        "no_scores": "Aún no hay récords",
        "back": "VOLVER",
        "tutorial_title": "CÓMO JUGAR",
        "tutorial_survival_title": "SUPERVIVENCIA",
        "tutorial_survival": "COMIDA baja sin parar. Cada comida la deja en 100% y te hace crecer.\nCOMIDA 0% = fin de partida. Las paredes conectan lados opuestos.",
        "tutorial_body_warning": "Tu propio cuerpo también es peligroso.",
        "tutorial_bonus_title": "BONUS",
        "tutorial_blue": "AZUL  • reduce un poco la velocidad",
        "tutorial_orange": "NARANJA  • locura: puede ayudarte o destruirte",
        "tutorial_green": "VERDE OCULTO  • 5 segundos de tregua",
        "tutorial_pause_title": "PAUSA Y CONTINUAR",
        "tutorial_pause": "Usa el botón de pausa para pausar, continuar o guardar y salir.\nInicio, Recientes o cambiar de app pausa y guarda automáticamente.",
        "tutorial_strange_title": "BOLITA EXTRAÑA",
        "tutorial_strange": "Desde niveles avanzados puede aparecer algo que se mueve. Descubre por tu cuenta qué hace.",
        "credits_text": (
            "[size=94][b]HARD CRAZY WORM[/b][/size]\n\n\n"
            "[size=40][b]Creador y desarrollador original[/b][/size]\n"
            "[size=30][b]Luis[/b][/size]\n"
            "[size=26][b]GitHub: zorkilloONE[/b][/size]\n\n"
            "[size=40][b]Diseño de mecánicas y concepto[/b][/size]\n"
            "[size=30][b]Luis[/b][/size]\n\n"
            "[size=40][b]Asistencia de desarrollo y balance[/b][/size]\n"
            "[size=30][b]Emely[/b][/size]\n\n"
            "[size=40][b]Apoyo creativo[/b][/size]\n"
            "[size=30][b]Toñita[/b][/size]\n\n"
            "[size=40][b]Control de calidad[/b][/size]\n"
            "[size=30][b]Pungy[/b][/size]\n\n"
            "[size=40][b]3 IA + 1 Humano = Juego Arcade Survival[/b][/size]\n\n"
            "[size=30][b]Gracias por jugar.[/b][/size]"
        ),
        "settings_title": "CONFIGURACIÓN",
        "music": "MÚSICA",
        "sfx": "EFECTOS",
        "sound_on": "ACTIVADO",
        "sound_off": "DESACTIVADO",
        "volume": "VOLUMEN GENERAL",
        "settings_saved": "Los ajustes se guardan en el dispositivo.",
        "food": "COMIDA",
        "level": "NIVEL",
        "score": "PUNTOS",
        "game_over": "FIN DE PARTIDA",
        "initials": "TUS INICIALES",
        "save_return": "GUARDAR Y VOLVER",
        "death_hunger": "El gusano murió de hambre",
        "death_orange": "El bonus naranja perdió la cabeza",
        "death_enemy": "Entraste directo en una amenaza",
        "death_self": "El gusano chocó con su cuerpo",
    },
}


def tr(key):
    return TEXTS["es"].get(key, key)


class MenuScreen(SpaceScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = FloatLayout()
        self.build_space_background(root)
        self._menu_root = root

        self.title_worm_mark = WormLogoMark(
            size_hint=(None, None),
            size=(dp(72), dp(72)),
        )
        root.add_widget(self.title_worm_mark)

        self.settings_button = GearButton(
            size_hint=(None, None),
            size=(dp(72), dp(72)),
        )
        self.settings_button.bind(on_release=lambda _x: setattr(self.manager, "current", "settings"))
        root.add_widget(self.settings_button)
        root.bind(size=self._place_menu_marks, pos=self._place_menu_marks)
        Clock.schedule_once(self._place_menu_marks, 0)

        self.tagline_label = Label(
            text="",
            font_size="15sp",
            bold=True,
            color=(0.82, 0.88, 1, 1),
            size_hint=(0.88, 0.05),
            pos_hint={"center_x": 0.5, "center_y": 0.58},
            halign="center",
            valign="middle",
        )
        self.tagline_label.bind(size=lambda inst, _v: setattr(inst, "text_size", inst.size))
        root.add_widget(self.tagline_label)

        self.start_button = Button(
            text="INICIAR JUEGO",
            font_size="32sp",
            bold=True,
            italic=True,
            color=(0.35, 1.0, 0.48, 1),
            background_normal="",
            background_down="",
            background_color=(0, 0, 0, 0),
            size_hint=(0.92, 0.12),
            pos_hint={"center_x": 0.5, "center_y": 0.50},
        )
        self.start_button.bind(on_release=self.on_start_pressed)
        root.add_widget(self.start_button)

        self.continue_button = Button(
            text="",
            font_size="22sp",
            bold=True,
            italic=True,
            color=(0.35, 1.0, 0.48, 1),
            background_normal="",
            background_down="",
            background_color=(0, 0, 0, 0),
            size_hint=(0.88, 0.08),
            pos_hint={"center_x": 0.5, "center_y": 0.41},
            opacity=0,
            disabled=True,
        )
        self.continue_button.bind(on_press=self.on_continue_pressed)
        root.add_widget(self.continue_button)

        self.title_widget = Label(
            text="HARD CRAZY WORM",
            font_size="26sp",
            bold=True,
            italic=True,
            color=(0.22, 0.98, 0.40, 1),
            size_hint=(0.92, 0.08),
            pos_hint={"center_x": 0.5, "center_y": 0.20},
            halign="center",
            valign="middle",
        )
        self.title_widget.bind(size=lambda inst, _v: setattr(inst, "text_size", inst.size))
        root.add_widget(self.title_widget)

        self._start_phase = 0.0
        Clock.schedule_interval(self._pulse_start, 0.05)

        self.add_widget(root)

    def _place_menu_marks(self, *_args):
        root = getattr(self, "_menu_root", None)
        if root is None or root.width <= 1 or root.height <= 1:
            return
        mark = self.title_worm_mark
        mark.size = (dp(72), dp(72))
        mark.pos = (root.x + dp(12), root.top - mark.height - dp(12))
        gear = self.settings_button
        gear.size = (dp(72), dp(72))
        gear.pos = (root.right - gear.width - dp(12), root.top - gear.height - dp(12))

    def _pulse_start(self, dt):
        self._start_phase = (self._start_phase + dt) % 6.28
        wave = 0.5 + 0.5 * math.sin(self._start_phase * 2.2)
        face = 0.62 + 0.38 * wave
        self.start_button.color = (0.28, 1.0, 0.42, face)

    def _apply_mascot_position(self, *_args):
        if not hasattr(self, "menu_mascot") or not hasattr(self, "_menu_root"):
            return
        nx, ny = self._mascot_anchor
        root = self._menu_root
        x = root.x + root.width * nx
        y = root.y + root.height * ny
        # Keep the whole mascot inside the app viewport.
        x = max(root.x + 8, min(x, root.right - self.menu_mascot.width - 8))
        y = max(root.y + 8, min(y, root.top - self.menu_mascot.height - 8))
        self.menu_mascot.pos = (x, y)

    def _move_menu_mascot(self, *_args):
        # Corners/edge pockets with enough breathing room to avoid interactive controls.
        safe_anchors = [
            (0.055, 0.87),
            (0.885, 0.87),
            (0.055, 0.055),
            (0.885, 0.055),
            (0.055, 0.23),
            (0.885, 0.23),
        ]
        previous = getattr(self, "_mascot_anchor", None)
        choices = [p for p in safe_anchors if p != previous] or safe_anchors
        self._mascot_anchor = random.choice(choices)
        self._apply_mascot_position()

    def _begin_new_game(self):
        game = self.manager.get_screen("game")
        game.entry_mode = "new"
        self.manager.current = "game"

    def on_start_pressed(self, _instance):
        if not SaveGameManager.has_valid_save():
            self._begin_new_game()
            return

        content = BoxLayout(orientation="vertical", padding=[20, 10, 20, 12], spacing=10)
        message = Label(
            text=tr("new_game_warning"),
            color=(0.70, 1.00, 0.78, 0.90),
            font_size="14sp",
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=dp(72),
        )
        message.bind(size=lambda inst, _v: setattr(inst, "text_size", inst.size))
        content.add_widget(message)

        cancel = Button(
            text=tr("cancel"),
            font_size="18sp",
            bold=True,
            italic=True,
            size_hint_y=None,
            height=dp(44),
            color=(0.45, 1.00, 0.55, 1),
            background_normal="",
            background_down="",
            background_color=(0, 0, 0, 0),
        )
        confirm = Button(
            text=tr("new_game_confirm"),
            font_size="18sp",
            bold=True,
            italic=True,
            size_hint_y=None,
            height=dp(44),
            color=(1.00, 0.38, 0.38, 1),
            background_normal="",
            background_down="",
            background_color=(0, 0, 0, 0),
        )
        content.add_widget(cancel)
        content.add_widget(confirm)

        popup = Popup(
            title=tr("saved_game"),
            content=content,
            size_hint=(0.84, 0.32),
            auto_dismiss=False,
            separator_height=1
        )
        style_night_popup(popup)
        popup.background_color = (0.02, 0.05, 0.04, 0.32)
        popup.title_color = (0.45, 1.00, 0.58, 1)
        cancel.bind(on_press=lambda _x: popup.dismiss())

        def confirm_new(_x):
            popup.dismiss()
            SaveGameManager.delete()
            self._begin_new_game()

        confirm.bind(on_press=confirm_new)
        popup.open()

    def on_continue_pressed(self, _instance):
        if not SaveGameManager.has_valid_save():
            self.on_pre_enter()
            return
        game = self.manager.get_screen("game")
        game.entry_mode = "continue"
        self.manager.current = "game"

    def show_records_popup(self, _instance):
        records = RecordManager.load_records()[:5]

        content = BoxLayout(orientation="vertical", padding=[18, 14, 18, 18], spacing=10)

        # Fixed-height stack inside a FloatLayout prevents 1-2 records from being stretched
        # across the entire popup. Whether there are 1 or 5, rows stay evenly aligned.
        records_area = FloatLayout(size_hint_y=0.76)
        if not records:
            empty = Label(
                text=tr("no_scores"),
                font_size="15sp",
                color=(0.90, 0.93, 1, 1),
                size_hint=(0.92, None),
                height=46,
                pos_hint={"center_x": 0.5, "center_y": 0.56},
                halign="center",
                valign="middle",
            )
            empty.bind(size=lambda inst, _v: setattr(inst, "text_size", inst.size))
            records_area.add_widget(empty)
        else:
            # Pungy: always 5 fixed rows — missing entries render dimmed so the
            # dialog never looks half-empty with 1-4 records.
            row_h = 50
            gap = 4
            stack_h = 5 * row_h + 4 * gap
            records_stack = BoxLayout(
                orientation="vertical",
                spacing=gap,
                size_hint=(0.92, None),
                height=stack_h,
                pos_hint={"center_x": 0.5, "center_y": 0.56},
            )
            for index in range(1, 6):
                if index <= len(records):
                    record = records[index - 1]
                    row_text = f"{index}. {record['initials']} - {record['score']}"
                    row_color = (0.95, 0.95, 1, 1)
                else:
                    row_text = f"{index}. ···"
                    row_color = (0.45, 0.50, 0.62, 1)
                row = Label(
                    text=row_text,
                    font_size="18sp",
                    color=row_color,
                    size_hint_y=None,
                    height=row_h,
                    halign="center",
                    valign="middle",
                )
                row.bind(size=lambda inst, _v: setattr(inst, "text_size", inst.size))
                records_stack.add_widget(row)
            records_area.add_widget(records_stack)

        content.add_widget(records_area)
        close_button = ghost_text_btn(tr("close"), font_size="18sp", height=dp(44))
        content.add_widget(close_button)

        popup = Popup(
            title=tr("records_title"),
            content=content,
            size_hint=(0.84, 0.52),
            auto_dismiss=True,
            separator_height=1
        )
        style_night_popup(popup)
        close_button.bind(on_press=lambda _x: popup.dismiss())
        popup.open()

    def on_pre_enter(self):
        self.tagline_label.text = tr("tagline")
        self.start_button.text = tr("start")
        self.continue_button.text = tr("continue_game")
        self._place_menu_marks()
        has_save = SaveGameManager.has_valid_save()
        self.continue_button.disabled = not has_save
        self.continue_button.opacity = 1 if has_save else 0


class TutorialScreen(SpaceScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _section_title(self, text):
        return Label(text=text, font_size="13sp", bold=True, color=(0.75, 0.85, 1, 1),
                     size_hint_y=0.055, halign="left", valign="middle")

    def _info_label(self, text, size_hint_y):
        lbl = Label(text=text, font_size="11.5sp", color=(0.90, 0.93, 1, 1),
                    halign="left", valign="middle", size_hint_y=size_hint_y)
        lbl.bind(size=lambda inst, _v: setattr(inst, "text_size", inst.size))
        return lbl

    def _legend_row(self, color, text, style="orb"):
        row = BoxLayout(orientation="horizontal", spacing=8, size_hint_y=0.055)
        icon = TutorialIcon(icon_color=color, style=style, size_hint_x=0.10)
        label = Label(text=text, font_size="11.3sp", color=(0.92, 0.94, 1, 1),
                      halign="left", valign="middle", size_hint_x=0.90)
        label.bind(size=lambda inst, _v: setattr(inst, "text_size", inst.size))
        row.add_widget(icon)
        row.add_widget(label)
        return row

    def on_pre_enter(self):
        self.clear_widgets()
        root = FloatLayout()
        self.build_space_background(root)

        panel = BoxLayout(
            orientation="vertical",
            padding=24,
            spacing=4,
            size_hint=(0.92, 0.92),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )

        panel.add_widget(Label(
            text=tr("tutorial_title"), font_size="28sp", bold=True, color=WHITE, size_hint_y=0.10
        ))

        panel.add_widget(self._section_title(tr("tutorial_survival_title")))
        survival = BoxLayout(orientation="horizontal", spacing=8, size_hint_y=0.12)
        survival.add_widget(TutorialIcon(style="food", size_hint_x=0.10))
        survival.add_widget(self._info_label(tr("tutorial_survival"), 1.0))
        panel.add_widget(survival)
        panel.add_widget(self._info_label(tr("tutorial_body_warning"), 0.05))

        panel.add_widget(self._section_title(tr("tutorial_bonus_title")))
        panel.add_widget(self._legend_row((0.20, 0.60, 1.00, 1), tr("tutorial_blue")))
        panel.add_widget(self._legend_row((1.00, 0.42, 0.02, 1), tr("tutorial_orange")))
        panel.add_widget(self._legend_row((0.10, 1.00, 0.28, 1), tr("tutorial_green")))

        panel.add_widget(self._section_title(tr("tutorial_pause_title")))
        panel.add_widget(self._info_label(tr("tutorial_pause"), 0.10))

        panel.add_widget(self._section_title(tr("tutorial_strange_title")))
        strange = BoxLayout(orientation="horizontal", spacing=8, size_hint_y=0.08)
        strange.add_widget(TutorialIcon(icon_color=(0.48, 0.04, 0.58, 0.90), style="strange", size_hint_x=0.10))
        strange.add_widget(self._info_label(tr("tutorial_strange"), 1.0))
        panel.add_widget(strange)

        back = ghost_text_btn(tr("back"), font_size="18sp", height=dp(46))
        back.bind(on_press=lambda _x: setattr(self.manager, "current", "settings"))
        panel.add_widget(back)

        root.add_widget(panel)
        self.add_widget(root)

class CreditsScreen(SpaceScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_pre_enter(self):
        ev = getattr(self, "_credits_event", None)
        if ev is not None:
            ev.cancel()
            self._credits_event = None
        self.clear_widgets()
        root = FloatLayout()
        self.build_space_background(root)
        self._credits_root = root

        roll_text = tr("credits_text")

        self.credits_roll = Label(
            text=roll_text,
            markup=True,
            font_size="16sp",
            color=(0.90, 0.93, 1, 1),
            halign="center",
            valign="top",
            size_hint=(0.88, None),
            pos_hint={"center_x": 0.5},
        )
        root.add_widget(self.credits_roll)
        hint = Label(
            text="TOCA PARA VOLVER",
            font_size="11sp",
            bold=True,
            color=(0.45, 1.00, 0.55, 0.45),
            size_hint=(0.90, 0.06),
            pos_hint={"center_x": 0.5, "top": 0.98},
        )
        root.add_widget(hint)
        self.add_widget(root)
        Clock.schedule_once(self._start_credits_roll, 0.05)

    def on_touch_down(self, touch):
        if self.manager and self.manager.current == "credits":
            self.manager.current = "settings"
            return True
        return super().on_touch_down(touch)

    def _start_credits_roll(self, *_args):
        roll = getattr(self, "credits_roll", None)
        root = getattr(self, "_credits_root", None)
        if roll is None or root is None:
            return
        roll.text_size = (root.width * 0.88, None)
        roll.texture_update()
        roll.height = max(root.height, roll.texture_size[1] + dp(40))
        roll.y = -roll.height + dp(80)
        ev = getattr(self, "_credits_event", None)
        if ev is not None:
            ev.cancel()
        self._credits_event = Clock.schedule_interval(self._tick_credits_roll, 1 / 30.0)

    def _tick_credits_roll(self, dt):
        roll = getattr(self, "credits_roll", None)
        root = getattr(self, "_credits_root", None)
        if roll is None or root is None or root.height <= 1:
            return
        roll.y += dp(60) * dt
        if roll.y > root.height + dp(24):
            roll.y = -roll.height

    def on_leave(self):
        ev = getattr(self, "_credits_event", None)
        if ev is not None:
            ev.cancel()
            self._credits_event = None


class SettingsScreen(SpaceScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_pre_enter(self):
        self.refresh()

    def refresh(self, *_args):
        self.clear_widgets()
        root = FloatLayout()
        self.build_space_background(root)

        panel = BoxLayout(
            orientation="vertical",
            padding=[22, 16, 22, 16],
            spacing=7,
            size_hint=(0.90, 0.92),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )

        panel.add_widget(Label(
            text=tr("settings_title"),
            font_size="26sp",
            bold=True,
            color=WHITE,
            size_hint_y=0.10
        ))

        panel.add_widget(self._setting_toggle_row(
            "music", "music_enabled", self.on_music_toggle, size_hint_y=0.08
        ))
        panel.add_widget(self._setting_toggle_row(
            "sfx", "sfx_enabled", self.on_sfx_toggle, size_hint_y=0.08
        ))

        self.volume_value_label = Label(
            text="",
            font_size="14sp",
            color=(0.75, 0.85, 1, 1),
            size_hint_y=0.06
        )
        self.update_volume_label()
        panel.add_widget(Label(
            text=tr("volume"),
            font_size="17sp",
            color=(0.92, 0.94, 1, 1),
            size_hint_y=0.07
        ))
        panel.add_widget(self.volume_value_label)

        self.volume_slider = Slider(
            min=0,
            max=100,
            value=SettingsManager.get("volume") * 100,
            step=1,
            size_hint_y=0.10,
            background_width=5,
            cursor_size=(26, 26),
            value_track=True,
            value_track_color=(0.14, 0.78, 0.32, 1),
            value_track_width=5
        )
        self.volume_slider.bind(value=self.on_volume_change)
        panel.add_widget(self.volume_slider)


        how_btn = ghost_text_btn(tr("how"), font_size="16sp", height=dp(40))
        how_btn.bind(on_press=lambda _x: setattr(self.manager, "current", "tutorial"))
        panel.add_widget(how_btn)

        credits_btn = ghost_text_btn(tr("credits"), font_size="16sp", height=dp(40))
        credits_btn.bind(on_press=lambda _x: setattr(self.manager, "current", "credits"))
        panel.add_widget(credits_btn)

        records_btn = ghost_text_btn(tr("records"), font_size="16sp", height=dp(40))
        records_btn.bind(on_press=self._open_records)
        panel.add_widget(records_btn)

        panel.add_widget(Label(
            text=tr("settings_saved"),
            font_size="12sp",
            color=(0.65, 0.72, 0.86, 1),
            size_hint_y=0.05
        ))

        back = ghost_text_btn(tr("back"), font_size="18sp", height=dp(46))
        back.bind(on_press=lambda _x: setattr(self.manager, "current", "menu"))
        panel.add_widget(back)

        root.add_widget(panel)
        self.add_widget(root)

    def _setting_toggle_row(self, label_key, setting_key, handler, size_hint_y=0.10):
        row = BoxLayout(
            orientation="horizontal",
            size_hint_y=size_hint_y,
            spacing=12
        )
        row.add_widget(Label(
            text=tr(label_key),
            font_size="17sp",
            color=(0.92, 0.94, 1, 1),
            halign="left"
        ))
        enabled = SettingsManager.get(setting_key)
        row.size_hint_y = None
        row.height = dp(40)
        toggle = ghost_text_btn(
            tr("sound_on") if enabled else tr("sound_off"),
            font_size="14sp",
            height=dp(40),
            color=(0.45, 1.00, 0.55, 1) if enabled else (0.30, 0.50, 0.34, 1),
        )
        toggle.size_hint_x = 0.38
        toggle.bind(on_press=handler)
        row.add_widget(toggle)
        return row

    def update_volume_label(self):
        if hasattr(self, "volume_value_label"):
            self.volume_value_label.text = f"{int(SettingsManager.get('volume') * 100)}%"

    def on_music_toggle(self, _instance):
        enabled = not SettingsManager.get("music_enabled")
        SettingsManager.set("music_enabled", enabled)
        if enabled:
            SoundManager.start_music()
        else:
            SoundManager.stop_music(reset_position=False)
        Clock.schedule_once(self.refresh, 0)

    def on_sfx_toggle(self, _instance):
        SettingsManager.set("sfx_enabled", not SettingsManager.get("sfx_enabled"))
        Clock.schedule_once(self.refresh, 0)

    def on_volume_change(self, _instance, value):
        SettingsManager.set("volume", max(0.0, min(1.0, float(value) / 100.0)))
        self.volume_value_label.text = f"{int(round(value))}%"
        SoundManager.update_music_volume()


    def _open_records(self, _instance):
        menu = self.manager.get_screen("menu")
        menu.show_records_popup(None)


class GameScreen(Screen):
    GRID_SIZE = 20

    LEVEL_FOOD_THRESHOLDS = [0, 10, 25, 45, 70]
    FOOD_COUNT_BY_LEVEL = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5}
    HUNGER_DRAIN_BY_LEVEL = {1: 6.2, 2: 6.8, 3: 7.4, 4: 8.0, 5: 8.6}
    HUNGER_RESTORE = 100.0

    START_SPEED = 0.20
    MIN_SPEED = 0.09
    ACCELERATION_CHANCE = 0.06
    ACCELERATION_FACTOR = 0.92
    SLOW_POWERUP_FACTOR = 1.05
    SLOW_POWERUP_CHANCE = 0.10

    TIME_START = 30.0
    TIME_CRITICAL = 13.0
    TIME_MAX = 30.0

    YELLOW_CHANCE_ON_FOOD = 0.035
    YELLOW_TTL = 6.0
    ORANGE_CHANCE_ON_FOOD = 0.025
    ORANGE_TTL = 6.0
    ORANGE_EFFECT_DURATION = 3.0
    ORANGE_DEATH_CHANCE = 0.05
    GREEN_CHANCE_ON_FOOD = 0.012
    GREEN_TTL = 5.5
    GREEN_EFFECT_DURATION = 5.0

    ENEMY_MIN_TTL = 8.0
    ENEMY_MAX_TTL = 12.0
    ENEMY_WARNING = 0.7
    SWIPE_THRESHOLD = 25.0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game_event = None
        self.tick_event = None
        self.autosave_event = None
        self.running = False
        self.paused = False
        self.touch_start = None
        self.swipe_locked = False
        self.queued_direction = None
        self.entry_mode = "new"
        self.pause_popup = None
        self.pause_popup_requested = False

        root = BoxLayout(orientation="vertical")
        with root.canvas.before:
            Color(*HUD_BG)
            self.root_bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=self._update_root_bg, size=self._update_root_bg)

        hud = BoxLayout(orientation="horizontal", size_hint_y=0.15,
                        padding=[10, 8, 10, 4], spacing=6)

        # Pungy HUD pass: pause button true-centered in a slot wide enough that the
        # 74px circle never overflows, even on narrow test windows.
        pause_slot = FloatLayout(size_hint_x=0.20)
        self.pause_button = MenuButton(
            size_hint=(None, None),
            size=(74, 74),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        self.pause_button.bind(on_release=self.pause_game)
        pause_slot.add_widget(self.pause_button)
        hud.add_widget(pause_slot)

        # Pungy HUD fix: compact food block, vertically centered in the HUD band.
        # The label row now sits directly above the bar instead of floating at the
        # top of the band while the bar drifted far below on tall screens.
        hunger_wrapper = AnchorLayout(anchor_x="center", anchor_y="center", size_hint_x=0.46)
        hunger_block = BoxLayout(orientation="vertical", size_hint=(1, None), height=64, spacing=2)
        hunger_top = BoxLayout(orientation="horizontal", size_hint_y=None, height=26, spacing=4)
        self.hunger_title_label = Label(text=tr('food'), font_size="14sp", bold=True,
                                        color=TEXT_DARK, size_hint_x=0.62,
                                        halign="left", valign="middle")
        self.hunger_title_label.bind(size=lambda inst, _v: setattr(inst, "text_size", inst.size))
        self.hunger_percent_label = Label(text="100%", font_size="14sp", bold=True,
                                          color=TEXT_DARK, size_hint_x=0.38,
                                          halign="right", valign="middle")
        self.hunger_percent_label.bind(size=lambda inst, _v: setattr(inst, "text_size", inst.size))
        hunger_top.add_widget(self.hunger_title_label)
        hunger_top.add_widget(self.hunger_percent_label)
        hunger_bar_slot = FloatLayout(size_hint_y=None, height=36)
        self.hunger_bar = HungerBar(size_hint=(0.96, None), height=30,
                                    pos_hint={"center_x": 0.5, "center_y": 0.5})
        hunger_bar_slot.add_widget(self.hunger_bar)
        hunger_block.add_widget(hunger_top)
        hunger_block.add_widget(hunger_bar_slot)
        hunger_wrapper.add_widget(hunger_block)

        info_col = BoxLayout(orientation="vertical", size_hint_x=0.34, spacing=2)
        self.level_label = self._right_label(f"{tr('level')} 1")
        self.score_label = self._right_label(f"{tr('score')} 0")
        info_col.add_widget(self.level_label)
        info_col.add_widget(self.score_label)
        hud.add_widget(hunger_wrapper)
        hud.add_widget(info_col)

        self.play_area = BoxLayout(size_hint_y=0.72)

        controls = BoxLayout(orientation="vertical", size_hint_y=0.13,
                             padding=[16, 0, 16, 4], spacing=2)
        up_row = BoxLayout()
        up_row.add_widget(Widget())
        self.btn_up = ArrowButton(direction="up")
        self.btn_up.bind(on_press=lambda _x: self.set_direction((0, 1)))
        up_row.add_widget(self.btn_up)
        up_row.add_widget(Widget())

        mid_row = BoxLayout(spacing=10)
        self.btn_left = ArrowButton(direction="left")
        self.btn_down = ArrowButton(direction="down")
        self.btn_right = ArrowButton(direction="right")
        self.btn_left.bind(on_press=lambda _x: self.set_direction((-1, 0)))
        self.btn_down.bind(on_press=lambda _x: self.set_direction((0, -1)))
        self.btn_right.bind(on_press=lambda _x: self.set_direction((1, 0)))
        mid_row.add_widget(self.btn_left)
        mid_row.add_widget(self.btn_down)
        mid_row.add_widget(self.btn_right)
        controls.add_widget(up_row)
        controls.add_widget(mid_row)

        root.add_widget(hud)
        root.add_widget(self.play_area)
        root.add_widget(controls)
        self.add_widget(root)
        self.reset_game()

    def _right_label(self, text):
        lbl = Label(text=text, font_size="15sp", bold=True, color=TEXT_DARK,
                    halign="right", valign="middle")
        lbl.bind(size=lambda inst, _v: setattr(inst, "text_size", inst.size))
        return lbl

    def _update_root_bg(self, instance, _value):
        self.root_bg.pos = instance.pos
        self.root_bg.size = instance.size

    def get_level(self):
        level = 1
        for index, threshold in enumerate(self.LEVEL_FOOD_THRESHOLDS, start=1):
            if self.foods_eaten >= threshold:
                level = index
        return min(level, 5)

    def desired_food_count(self):
        return self.FOOD_COUNT_BY_LEVEL[self.get_level()]

    def reset_game(self):
        self.snake = [(10, 10), (9, 10), (8, 10)]
        self.direction = (1, 0)
        self.queued_direction = None
        self.swipe_locked = False
        self.touch_start = None
        self.score = 0
        self.foods_eaten = 0
        self.time_left = self.TIME_START
        self.hunger = 100.0
        self.current_speed = self.START_SPEED
        self.saved_speed_before_green = None
        self.foods = []
        self.powerup = None
        self.powerup_pos = None
        self.powerup_ttl = 0.0
        self.orange_effect = None
        self.orange_effect_left = 0.0
        self.orange_saved_speed = None
        self.green_active = False
        self.green_left = 0.0
        self.time_powerup_armed = True
        self.enemies = []
        self.enemy_spawn_cooldown = 5.0
        self.sync_food_count()
        self.update_hud()

    def on_enter(self):
        self.stop_events()
        Window.unbind(on_key_down=self.on_key_down)
        Window.bind(on_key_down=self.on_key_down)
        self.touch_start = None
        self.swipe_locked = False
        self.queued_direction = None
        self.pause_popup_requested = False
        self._dismiss_pause_popup()

        mode = self.entry_mode
        self.entry_mode = "new"

        if mode == "continue":
            payload = SaveGameManager.load()
            if payload is None or not self.restore_game_state(payload.get("state", {})):
                SaveGameManager.delete()
                self.running = False
                self.paused = False
                Clock.schedule_once(lambda _dt: setattr(self.manager, "current", "menu"), 0)
                return
            self.running = False
            self.paused = True
            self.pause_popup_requested = True
            self.update_hud()
            Clock.schedule_once(lambda _dt: self.draw_elements(), 0)
            Clock.schedule_once(lambda _dt: self.show_pause_popup(), 0.05)
            return

        SaveGameManager.delete()
        self.reset_game()
        self.paused = False
        self.running = True
        self.start_events()
        Clock.schedule_once(lambda _dt: self.draw_elements(), 0)
        self.save_game_state()

    def on_leave(self):
        self.running = False
        self.touch_start = None
        self.swipe_locked = False
        self.queued_direction = None
        Window.unbind(on_key_down=self.on_key_down)
        self.stop_events()
        self._dismiss_pause_popup()

    def start_events(self):
        self.stop_events()
        if not self.running or self.paused:
            return
        self.game_event = Clock.schedule_interval(self.update_game, self.current_speed)
        self.tick_event = Clock.schedule_interval(self.update_survival, 0.1)
        self.autosave_event = Clock.schedule_interval(self._autosave, 5.0)

    def stop_events(self):
        if self.game_event is not None:
            self.game_event.cancel()
            self.game_event = None
        if self.tick_event is not None:
            self.tick_event.cancel()
            self.tick_event = None
        if self.autosave_event is not None:
            self.autosave_event.cancel()
            self.autosave_event = None

    def restart_move_event(self):
        if self.game_event is not None:
            self.game_event.cancel()
            self.game_event = None
        if self.running and not self.paused:
            self.game_event = Clock.schedule_interval(self.update_game, self.current_speed)

    def _autosave(self, _dt):
        if self.running and not self.paused:
            self.save_game_state()

    def serialize_game_state(self):
        return {
            "snake": [list(cell) for cell in self.snake],
            "direction": list(self.direction),
            "score": int(self.score),
            "foods_eaten": int(self.foods_eaten),
            "time_left": float(self.time_left),
            "hunger": float(self.hunger),
            "current_speed": float(self.current_speed),
            "saved_speed_before_green": self.saved_speed_before_green,
            "foods": [list(cell) for cell in self.foods],
            "powerup": self.powerup,
            "powerup_pos": list(self.powerup_pos) if self.powerup_pos is not None else None,
            "powerup_ttl": float(self.powerup_ttl),
            "orange_effect": self.orange_effect,
            "orange_effect_left": float(self.orange_effect_left),
            "orange_saved_speed": self.orange_saved_speed,
            "green_active": bool(self.green_active),
            "green_left": float(self.green_left),
            "time_powerup_armed": bool(self.time_powerup_armed),
            "enemies": [
                {
                    "pos": list(enemy["pos"]),
                    "ttl": float(enemy["ttl"]),
                    "warning": float(enemy["warning"]),
                    "move_timer": float(enemy["move_timer"]),
                    "move_interval": float(enemy["move_interval"]),
                    "speed_factor": float(enemy.get("speed_factor", 1.20)),
                }
                for enemy in self.enemies
            ],
            "enemy_spawn_cooldown": float(self.enemy_spawn_cooldown),
        }

    def save_game_state(self):
        try:
            state = self.serialize_game_state()
        except (AttributeError, KeyError, TypeError, ValueError):
            return False
        return SaveGameManager.save(state)

    def _valid_cell(self, cell):
        if not isinstance(cell, (list, tuple)) or len(cell) != 2:
            return False
        try:
            x, y = int(cell[0]), int(cell[1])
        except (TypeError, ValueError):
            return False
        return 0 <= x < self.GRID_SIZE and 0 <= y < self.GRID_SIZE

    def restore_game_state(self, state):
        try:
            if not isinstance(state, dict):
                return False

            snake_raw = state["snake"]
            foods_raw = state["foods"]
            direction_raw = state["direction"]
            enemies_raw = state.get("enemies", [])

            if not isinstance(snake_raw, list) or not snake_raw or not all(self._valid_cell(c) for c in snake_raw):
                return False
            if not isinstance(foods_raw, list) or not all(self._valid_cell(c) for c in foods_raw):
                return False
            if not isinstance(direction_raw, (list, tuple)) or len(direction_raw) != 2:
                return False

            direction = (int(direction_raw[0]), int(direction_raw[1]))
            if direction not in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                return False

            powerup_pos_raw = state.get("powerup_pos")
            if powerup_pos_raw is not None and not self._valid_cell(powerup_pos_raw):
                return False

            enemies = []
            if not isinstance(enemies_raw, list):
                return False
            for enemy in enemies_raw:
                if not isinstance(enemy, dict) or not self._valid_cell(enemy.get("pos")):
                    return False
                enemies.append({
                    "pos": tuple(int(v) for v in enemy["pos"]),
                    "ttl": max(0.0, float(enemy.get("ttl", 0.0))),
                    "warning": max(0.0, float(enemy.get("warning", 0.0))),
                    "move_timer": max(0.0, float(enemy.get("move_timer", 0.0))),
                    "move_interval": max(0.01, float(enemy.get("move_interval", self.START_SPEED * 1.20))),
                    "speed_factor": max(1.05, min(1.60, float(enemy.get("speed_factor", 1.20)))),
                })

            powerup = state.get("powerup")
            if powerup not in (None, "slow", "time", "yellow", "orange", "green"):
                return False
            orange_effect = state.get("orange_effect")
            if orange_effect not in (None, "turbo", "slow", "hunger_fast", "time_fast"):
                return False

            self.snake = [tuple(int(v) for v in cell) for cell in snake_raw]
            self.direction = direction
            self.queued_direction = None
            self.score = max(0, int(state.get("score", 0)))
            self.foods_eaten = max(0, int(state.get("foods_eaten", 0)))
            self.time_left = max(0.001, min(self.TIME_MAX, float(state.get("time_left", self.TIME_START))))
            self.hunger = max(0.001, min(100.0, float(state.get("hunger", 100.0))))
            self.current_speed = max(0.01, min(1.0, float(state.get("current_speed", self.START_SPEED))))

            saved_green = state.get("saved_speed_before_green")
            self.saved_speed_before_green = None if saved_green is None else max(0.01, min(1.0, float(saved_green)))
            self.foods = [tuple(int(v) for v in cell) for cell in foods_raw]
            self.powerup = powerup
            self.powerup_pos = None if powerup_pos_raw is None else tuple(int(v) for v in powerup_pos_raw)
            self.powerup_ttl = max(0.0, float(state.get("powerup_ttl", 0.0)))
            self.orange_effect = orange_effect
            self.orange_effect_left = max(0.0, float(state.get("orange_effect_left", 0.0)))

            orange_saved = state.get("orange_saved_speed")
            self.orange_saved_speed = None if orange_saved is None else max(0.01, min(1.0, float(orange_saved)))
            self.green_active = bool(state.get("green_active", False))
            self.green_left = max(0.0, float(state.get("green_left", 0.0)))
            self.time_powerup_armed = bool(state.get("time_powerup_armed", True))
            self.enemies = enemies
            self.enemy_spawn_cooldown = max(0.0, float(state.get("enemy_spawn_cooldown", 5.0)))

            self.update_hud()
            return True
        except (KeyError, TypeError, ValueError, OverflowError):
            return False

    def pause_game(self, _instance=None, automatic=False):
        if self.manager is None or self.manager.current != "game":
            return
        if self.paused:
            self.save_game_state()
            if automatic:
                self.pause_popup_requested = True
            return
        if not self.running:
            return

        self.running = False
        self.paused = True
        self.touch_start = None
        self.swipe_locked = False
        self.queued_direction = None
        self.stop_events()
        self.save_game_state()
        self.pause_popup_requested = True
        if not automatic:
            self.show_pause_popup()

    def resume_game(self, _instance=None):
        if not self.paused:
            return
        self._dismiss_pause_popup()
        self.pause_popup_requested = False
        self.paused = False
        self.running = True
        self.start_events()
        self.draw_elements()

    def save_and_exit_to_menu(self, _instance=None):
        if self.manager is None:
            return
        self.running = False
        self.paused = True
        self.stop_events()
        self.save_game_state()
        self.pause_popup_requested = False
        self._dismiss_pause_popup()
        self.manager.current = "menu"

    def show_pause_popup(self):
        if self.manager is None or self.manager.current != "game" or not self.paused:
            return
        if self.pause_popup is not None:
            return

        content = BoxLayout(orientation="vertical", padding=[20, 10, 20, 12], spacing=10)
        status = Label(
            text=tr("save_status"),
            color=(0.70, 1.00, 0.78, 0.90),
            font_size="13sp",
            size_hint_y=None,
            height=dp(32),
            halign="center",
            valign="middle",
        )
        status.bind(size=lambda inst, _v: setattr(inst, "text_size", inst.size))
        content.add_widget(status)

        resume = Button(
            text=tr("resume"),
            font_size="18sp",
            bold=True,
            italic=True,
            size_hint_y=None,
            height=dp(44),
            color=(0.45, 1.00, 0.55, 1),
            background_normal="",
            background_down="",
            background_color=(0, 0, 0, 0),
        )
        save_exit = Button(
            text=tr("save_exit"),
            font_size="18sp",
            bold=True,
            italic=True,
            size_hint_y=None,
            height=dp(44),
            color=(0.45, 1.00, 0.55, 1),
            background_normal="",
            background_down="",
            background_color=(0, 0, 0, 0),
        )
        content.add_widget(resume)
        content.add_widget(save_exit)

        popup = Popup(
            title=tr("pause"),
            content=content,
            size_hint=(0.84, 0.28),
            auto_dismiss=False,
            separator_height=1
        )
        style_night_popup(popup)
        popup.background_color = (0.02, 0.05, 0.04, 0.32)
        popup.title_color = (0.45, 1.00, 0.58, 1)
        self.pause_popup = popup
        resume.bind(on_press=self.resume_game)
        save_exit.bind(on_press=self.save_and_exit_to_menu)
        popup.bind(on_dismiss=self._on_pause_popup_dismissed)
        popup.open()

    def _on_pause_popup_dismissed(self, *_args):
        self.pause_popup = None

    def _dismiss_pause_popup(self):
        popup = self.pause_popup
        self.pause_popup = None
        if popup is not None:
            try:
                popup.dismiss()
            except Exception:
                pass

    def handle_app_pause(self):
        if self.manager is not None and self.manager.current == "game":
            self.pause_game(automatic=True)

    def handle_app_resume(self):
        if self.manager is not None and self.manager.current == "game" and self.paused:
            self.pause_popup_requested = True
            Clock.schedule_once(lambda _dt: self.show_pause_popup(), 0.05)

    def handle_app_stop(self):
        if self.manager is not None and self.manager.current == "game":
            if self.running:
                self.running = False
                self.paused = True
                self.stop_events()
            self.save_game_state()

    def set_direction(self, new_direction):
        if not self.running or self.paused:
            return
        if new_direction == self.direction:
            return
        if new_direction == (-self.direction[0], -self.direction[1]):
            return
        self.queued_direction = new_direction

    def _direction_from_swipe(self, dx, dy):
        if abs(dx) < self.SWIPE_THRESHOLD and abs(dy) < self.SWIPE_THRESHOLD:
            return None
        if abs(dx) > abs(dy):
            return (1, 0) if dx > 0 else (-1, 0)
        return (0, 1) if dy > 0 else (0, -1)

    def on_key_down(self, _window, key, _scancode, _codepoint, _modifiers):
        if key == 273:
            self.set_direction((0, 1))
        elif key == 274:
            self.set_direction((0, -1))
        elif key == 276:
            self.set_direction((-1, 0))
        elif key == 275:
            self.set_direction((1, 0))

    def on_touch_down(self, touch):
        if self.manager is None or self.manager.current != "game":
            return super().on_touch_down(touch)
        if self.play_area.collide_point(touch.x, touch.y):
            self.touch_start = (touch.x, touch.y)
            self.swipe_locked = False
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.touch_start is not None and not self.swipe_locked:
            start_x, start_y = self.touch_start
            direction = self._direction_from_swipe(touch.x - start_x, touch.y - start_y)
            if direction is not None:
                self.set_direction(direction)
                self.swipe_locked = True
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.touch_start is not None:
            start_x, start_y = self.touch_start
            if not self.swipe_locked:
                direction = self._direction_from_swipe(touch.x - start_x, touch.y - start_y)
                if direction is not None:
                    self.set_direction(direction)
            self.touch_start = None
            self.swipe_locked = False
            return True
        return super().on_touch_up(touch)

    def update_hud(self):
        safe_hunger = max(0.0, min(100.0, self.hunger))
        self.hunger_bar.set_value(safe_hunger)
        # Pungy HUD pass: don't rebuild the label texture 10x/sec when nothing changed,
        # and tint the % with the hunger state so low food reads as an alarm.
        food_text = tr('food')
        if self.hunger_title_label.text != food_text:
            self.hunger_title_label.text = food_text
        self.hunger_percent_label.text = f"{int(safe_hunger)}%"
        # Pungy tint: the % readout mirrors the bar's hunger state (dark -> orange -> red).
        if safe_hunger <= 10:
            self.hunger_percent_label.color = (1.0, 0.28, 0.28, 1)
        elif safe_hunger <= 25:
            self.hunger_percent_label.color = (1.0, 0.72, 0.22, 1)
        else:
            self.hunger_percent_label.color = TEXT_DARK
        self.level_label.text = f"{tr('level')} {self.get_level()}"
        self.score_label.text = f"{tr('score')} {self.score}"

    def update_survival(self, dt):
        if not self.running:
            return

        if self.green_active:
            self.green_left -= dt
            if self.green_left <= 0:
                self.end_green_effect()
        else:
            hunger_factor = 2.0 if self.orange_effect == "hunger_fast" else 1.0
            self.hunger -= self.HUNGER_DRAIN_BY_LEVEL[self.get_level()] * hunger_factor * dt

        if self.orange_effect is not None:
            self.orange_effect_left -= dt
            if self.orange_effect_left <= 0:
                self.end_orange_effect()

        if self.powerup is not None:
            if self.powerup == "time":
                self.clear_powerup()
            else:
                self.powerup_ttl -= dt
                if self.powerup_ttl <= 0:
                    self.clear_powerup()

        self.update_enemies(dt)
        self.update_hud()

        if self.hunger <= 0:
            self.game_over(tr("death_hunger"))
            return
        self.draw_elements()

    def occupied_cells(self):
        occupied = set(self.snake)
        occupied.update(self.foods)
        if self.powerup_pos is not None:
            occupied.add(self.powerup_pos)
        for enemy in self.enemies:
            occupied.add(enemy["pos"])
        return occupied

    def random_free_cell(self):
        occupied = self.occupied_cells()
        free_cells = [(x, y) for x in range(self.GRID_SIZE) for y in range(self.GRID_SIZE)
                      if (x, y) not in occupied]
        return random.choice(free_cells) if free_cells else None

    def toroidal_distance(self, a, b):
        ax, ay = a
        bx, by = b
        dx = min(abs(ax-bx), self.GRID_SIZE-abs(ax-bx))
        dy = min(abs(ay-by), self.GRID_SIZE-abs(ay-by))
        return dx + dy

    def random_near_head_cell(self, min_distance=2, max_distance=5):
        head = self.snake[0]
        occupied = self.occupied_cells()
        cells = [(x, y) for x in range(self.GRID_SIZE) for y in range(self.GRID_SIZE)
                 if (x, y) not in occupied and min_distance <= self.toroidal_distance(head, (x, y)) <= max_distance]
        return random.choice(cells) if cells else self.random_free_cell()

    def random_far_from_head_cell(self, min_distance=12):
        head = self.snake[0]
        occupied = self.occupied_cells()
        cells = [(x, y) for x in range(self.GRID_SIZE) for y in range(self.GRID_SIZE)
                 if (x, y) not in occupied and self.toroidal_distance(head, (x, y)) >= min_distance]
        return random.choice(cells) if cells else self.random_free_cell()

    def random_ahead_cell(self, min_steps=2, max_steps=5):
        hx, hy = self.snake[0]
        dx, dy = self.direction
        occupied = self.occupied_cells()
        cells = []
        for steps in range(min_steps, max_steps+1):
            cell = ((hx + dx*steps) % self.GRID_SIZE, (hy + dy*steps) % self.GRID_SIZE)
            if cell not in occupied:
                cells.append(cell)
        return random.choice(cells) if cells else self.random_near_head_cell(2, 5)

    def sync_food_count(self):
        desired = self.desired_food_count()
        while len(self.foods) < desired:
            cell = self.random_free_cell()
            if cell is None:
                break
            self.foods.append(cell)
        while len(self.foods) > desired:
            self.foods.pop()

    def spawn_powerup(self, kind, near_head=False, far=False, ahead=False, ttl=8.0):
        if self.powerup is not None:
            return False
        if far:
            cell = self.random_far_from_head_cell()
        elif ahead:
            cell = self.random_ahead_cell()
        elif near_head:
            cell = self.random_near_head_cell()
        else:
            cell = self.random_free_cell()
        if cell is None:
            return False
        self.powerup = kind
        self.powerup_pos = cell
        self.powerup_ttl = ttl
        return True

    def clear_powerup(self):
        self.powerup = None
        self.powerup_pos = None
        self.powerup_ttl = 0.0

    def maybe_spawn_special_after_food(self):
        if self.powerup is not None:
            return
        roll = random.random()
        if roll < self.GREEN_CHANCE_ON_FOOD:
            self.spawn_powerup("green", far=True, ttl=self.GREEN_TTL)
            return
        if roll < self.GREEN_CHANCE_ON_FOOD + self.ORANGE_CHANCE_ON_FOOD:
            self.spawn_powerup("orange", ahead=True, ttl=self.ORANGE_TTL)
            return
        if random.random() < self.SLOW_POWERUP_CHANCE:
            self.spawn_powerup("slow", ttl=8.0)

    def max_enemies(self):
        level = self.get_level()
        if level < 3:
            return 0
        if level < 5:
            return 1
        return 2

    def update_enemies(self, dt):
        max_count = self.max_enemies()
        for enemy in self.enemies[:]:
            enemy["ttl"] -= dt
            enemy["move_timer"] -= dt
            if enemy["warning"] > 0:
                enemy["warning"] -= dt
            elif enemy["move_timer"] <= 0:
                self.move_enemy(enemy)
            if enemy["ttl"] <= 0:
                self.enemies.remove(enemy)
                self.enemy_spawn_cooldown = random.uniform(5.0, 9.0)

        if max_count == 0:
            return
        if len(self.enemies) >= max_count:
            return

        self.enemy_spawn_cooldown -= dt
        if self.enemy_spawn_cooldown <= 0:
            self.spawn_enemy()
            if len(self.enemies) < max_count:
                self.enemy_spawn_cooldown = random.uniform(5.0, 9.0)

    def spawn_enemy(self):
        cell = self.random_far_from_head_cell(min_distance=7)
        if cell is None:
            return

        # The strange orb is intentionally a little slower than the player.
        # It should look catchable so curiosity can tempt the player to chase it.
        speed_factor = random.uniform(1.18, 1.25)
        enemy_interval = max(0.055, self.current_speed * speed_factor)
        self.enemies.append({
            "pos": cell,
            "ttl": random.uniform(self.ENEMY_MIN_TTL, self.ENEMY_MAX_TTL),
            "warning": self.ENEMY_WARNING,
            "move_timer": enemy_interval,
            "move_interval": enemy_interval,
            "speed_factor": speed_factor,
        })

    def move_enemy(self, enemy):
        factor = max(1.05, min(1.60, float(enemy.get("speed_factor", 1.20))))
        enemy["move_interval"] = max(0.055, self.current_speed * factor)
        enemy["move_timer"] = enemy["move_interval"]
        ex, ey = enemy["pos"]
        head = self.snake[0]
        options = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        random.shuffle(options)
        for dx, dy in options:
            nxt = ((ex + dx) % self.GRID_SIZE, (ey + dy) % self.GRID_SIZE)
            if nxt != head:
                enemy["pos"] = nxt
                return

    def activate_yellow(self):
        self.hunger = 100.0

    def activate_orange(self):
        if random.random() < self.ORANGE_DEATH_CHANCE:
            self.game_over(tr("death_orange"))
            return
        effect = random.choice(["turbo", "slow", "hunger_fast"])
        self.orange_effect = effect
        self.orange_effect_left = self.ORANGE_EFFECT_DURATION
        if effect in ("turbo", "slow"):
            self.orange_saved_speed = self.current_speed
            if effect == "turbo":
                self.current_speed = max(0.055, self.current_speed * 0.50)
            else:
                self.current_speed = min(0.50, self.current_speed * 2.20)
            self.restart_move_event()

    def end_orange_effect(self):
        effect = self.orange_effect
        self.orange_effect = None
        self.orange_effect_left = 0.0
        if effect in ("turbo", "slow") and not self.green_active:
            if self.orange_saved_speed is not None:
                self.current_speed = max(self.MIN_SPEED, self.orange_saved_speed)
                self.orange_saved_speed = None
                self.restart_move_event()

    def activate_green(self):
        if self.green_active:
            self.green_left = self.GREEN_EFFECT_DURATION
            return
        self.green_active = True
        self.green_left = self.GREEN_EFFECT_DURATION
        self.saved_speed_before_green = self.current_speed
        self.current_speed = self.START_SPEED
        self.restart_move_event()

    def end_green_effect(self):
        self.green_active = False
        self.green_left = 0.0
        if self.saved_speed_before_green is not None:
            self.current_speed = max(self.MIN_SPEED, self.saved_speed_before_green)
            self.saved_speed_before_green = None
            self.restart_move_event()

    def update_game(self, _dt):
        if not self.running:
            return
        if self.queued_direction is not None:
            self.direction = self.queued_direction
            self.queued_direction = None
        hx, hy = self.snake[0]
        dx, dy = self.direction
        new_head = ((hx + dx) % self.GRID_SIZE, (hy + dy) % self.GRID_SIZE)

        enemy_positions = {enemy["pos"] for enemy in self.enemies if enemy["warning"] <= 0}
        if new_head in enemy_positions:
            self.game_over(tr("death_enemy"))
            return

        will_eat_food = new_head in self.foods
        body_to_check = self.snake if will_eat_food else self.snake[:-1]
        if new_head in body_to_check:
            self.game_over(tr("death_self"))
            return

        self.snake.insert(0, new_head)

        if will_eat_food:
            self.foods.remove(new_head)
            SoundManager.play("eat")
            self.score += 10
            self.foods_eaten += 1
            self.hunger = min(100.0, self.hunger + self.HUNGER_RESTORE)

            if not self.green_active and self.orange_effect not in ("turbo", "slow"):
                if random.random() < self.ACCELERATION_CHANCE:
                    old_speed = self.current_speed
                    self.current_speed = max(self.MIN_SPEED, self.current_speed * self.ACCELERATION_FACTOR)
                    if self.current_speed != old_speed:
                        self.restart_move_event()

            self.sync_food_count()
            self.maybe_spawn_special_after_food()
            self.save_game_state()

        elif self.powerup_pos is not None and new_head == self.powerup_pos:
            kind = self.powerup
            self.clear_powerup()
            SoundManager.play("bonus")
            self.snake.pop()

            if kind == "slow":
                if not self.green_active and self.orange_effect not in ("turbo", "slow"):
                    self.current_speed = min(self.START_SPEED * 1.50, self.current_speed * self.SLOW_POWERUP_FACTOR)
                    self.restart_move_event()
                self.score += 25
            elif kind == "time":
                pass
            elif kind == "yellow":
                self.activate_yellow()
                self.score += 40
            elif kind == "orange":
                self.score += 50
                self.activate_orange()
                if not self.running:
                    return
            elif kind == "green":
                self.activate_green()
                self.score += 75

            self.sync_food_count()
            self.save_game_state()
        else:
            self.snake.pop()

        self.update_hud()
        self.draw_elements()

    def eye_offsets(self):
        dx, dy = self.direction
        if (dx, dy) == (1, 0):
            return [(0.63, 0.65), (0.63, 0.25)]
        if (dx, dy) == (-1, 0):
            return [(0.23, 0.65), (0.23, 0.25)]
        if (dx, dy) == (0, 1):
            return [(0.28, 0.63), (0.62, 0.63)]
        return [(0.28, 0.23), (0.62, 0.23)]

    def _draw_neon_orb(self, cx, cy, base, core, glow, pulse=0.5):
        spread = 1.08 + 0.22 * pulse
        Color(glow[0], glow[1], glow[2], 0.08 + 0.16 * pulse)
        Ellipse(pos=(cx - base * 0.62 * spread, cy - base * 0.62 * spread),
                size=(base * 1.24 * spread, base * 1.24 * spread))
        Color(glow[0], glow[1], glow[2], 0.18 + 0.22 * pulse)
        Ellipse(pos=(cx - base * 0.46, cy - base * 0.46), size=(base * 0.92, base * 0.92))
        Color(core[0], core[1], core[2], 0.82 + 0.18 * pulse)
        Ellipse(pos=(cx - base * 0.26, cy - base * 0.26), size=(base * 0.52, base * 0.52))
        Color(1, 1, 1, 0.45 + 0.50 * pulse)
        Ellipse(pos=(cx - base * 0.09, cy + base * 0.05), size=(base * 0.12, base * 0.12))

    def draw_elements(self):
        self.play_area.canvas.clear()
        if self.play_area.width <= 0 or self.play_area.height <= 0:
            return
        cell_w = self.play_area.width / self.GRID_SIZE
        cell_h = self.play_area.height / self.GRID_SIZE

        with self.play_area.canvas:
            Color(*ARENA_BG)
            Rectangle(pos=self.play_area.pos, size=self.play_area.size)
            Color(0.02, 0.12, 0.08, 0.55)
            Rectangle(
                pos=(self.play_area.x + cell_w * 0.20, self.play_area.y + cell_h * 0.20),
                size=(self.play_area.width - cell_w * 0.40, self.play_area.height - cell_h * 0.40),
            )

            Color(0.18, 0.85, 0.40, 0.16)
            for i in range(0, self.GRID_SIZE + 1):
                x = self.play_area.x + i * cell_w
                y = self.play_area.y + i * cell_h
                Line(points=[x, self.play_area.y, x, self.play_area.top], width=0.80)
                Line(points=[self.play_area.x, y, self.play_area.right, y], width=0.80)
            Color(0.22, 1.00, 0.45, 0.22)
            for i in range(0, self.GRID_SIZE + 1, 5):
                x = self.play_area.x + i * cell_w
                y = self.play_area.y + i * cell_h
                Line(points=[x, self.play_area.y, x, self.play_area.top], width=1.35)
                Line(points=[self.play_area.x, y, self.play_area.right, y], width=1.35)

            edge_w = max(6.0, cell_w * 0.70)
            edge_h = max(6.0, cell_h * 0.70)
            Color(0.00, 0.00, 0.00, 0.42)
            Rectangle(pos=(self.play_area.x, self.play_area.y), size=(edge_w, self.play_area.height))
            Rectangle(pos=(self.play_area.right-edge_w, self.play_area.y), size=(edge_w, self.play_area.height))
            Rectangle(pos=(self.play_area.x, self.play_area.y), size=(self.play_area.width, edge_h))
            Rectangle(pos=(self.play_area.x, self.play_area.top-edge_h), size=(self.play_area.width, edge_h))
            Color(0.20, 1.00, 0.42, 0.55)
            Line(rectangle=(self.play_area.x, self.play_area.y, self.play_area.width, self.play_area.height), width=1.70)
            Color(0.10, 0.55, 0.28, 0.28)
            Line(
                rectangle=(
                    self.play_area.x + 4,
                    self.play_area.y + 4,
                    self.play_area.width - 8,
                    self.play_area.height - 8,
                ),
                width=1.15,
            )

            star = 0.5 + 0.5 * math.sin(Clock.get_time() * 2.4)
            for fx, fy in self.foods:
                cx = self.play_area.x + fx*cell_w + cell_w/2
                cy = self.play_area.y + fy*cell_h + cell_h/2
                self._draw_neon_orb(cx, cy, min(cell_w, cell_h), (1.00, 0.98, 0.62), (1.00, 1.00, 0.75), pulse=star)

            if self.powerup is not None and self.powerup_pos is not None:
                px, py = self.powerup_pos
                cx = self.play_area.x + px*cell_w + cell_w/2
                cy = self.play_area.y + py*cell_h + cell_h/2
                if self.powerup == "slow":
                    core, glow = (0.25, 0.75, 1.00), (0.35, 0.85, 1.00)
                elif self.powerup == "orange":
                    core, glow = (1.00, 0.42, 0.08), (1.00, 0.55, 0.18)
                elif self.powerup == "green":
                    core, glow = (0.15, 1.00, 0.38), (0.45, 1.00, 0.62)
                else:
                    core, glow = (0.55, 0.70, 0.55), (0.70, 0.90, 0.70)
                self._draw_neon_orb(cx, cy, min(cell_w, cell_h), core, glow, pulse=star)

            for enemy in self.enemies:
                ex, ey = enemy["pos"]
                cx = self.play_area.x + ex*cell_w + cell_w/2
                cy = self.play_area.y + ey*cell_h + cell_h/2
                if enemy["warning"] > 0:
                    Color(0.85, 0.20, 1.00, 0.28)
                    Ellipse(pos=(cx - min(cell_w, cell_h)*0.55, cy - min(cell_w, cell_h)*0.55),
                            size=(min(cell_w, cell_h)*1.10, min(cell_w, cell_h)*1.10))
                    Color(0.90, 0.35, 1.00, 0.80)
                    Line(circle=(cx, cy, min(cell_w, cell_h)*0.40), width=1.6)
                else:
                    self._draw_neon_orb(cx, cy, min(cell_w, cell_h), (0.62, 0.12, 0.85), (0.90, 0.35, 1.00))

            for index, (sx, sy) in enumerate(self.snake):
                pos_x = self.play_area.x + sx*cell_w
                pos_y = self.play_area.y + sy*cell_h
                cx = pos_x + cell_w/2
                cy = pos_y + cell_h/2
                base = min(cell_w, cell_h)
                if self.green_active:
                    Color(0.20, 1.00, 0.45, 0.22)
                    Ellipse(pos=(cx-base*0.52, cy-base*0.52), size=(base*1.04, base*1.04))
                    Color(0.18, 0.85, 0.38, 1)
                elif index == 0:
                    Color(0.15, 1.00, 0.40, 0.20)
                    Ellipse(pos=(cx-base*0.54, cy-base*0.54), size=(base*1.08, base*1.08))
                    Color(0.00, 0.34, 0.08, 1)
                else:
                    Color(0.08, 0.50, 0.12, 1)
                Ellipse(pos=(pos_x+1, pos_y+1), size=(max(2, cell_w-2), max(2, cell_h-2)))
                if index != 0:
                    Color(0.55, 1.00, 0.55, 0.42)
                    Ellipse(pos=(pos_x + cell_w*0.18, pos_y + cell_h*0.50),
                            size=(cell_w*0.34, cell_h*0.22))
                if index == 0:
                    # Pungy: head eyes match the food-bar face — white with black pupils.
                    eye_size = max(2, min(cell_w, cell_h)*0.16)
                    pupil_size = max(1, eye_size*0.45)
                    dx, dy = self.direction
                    for ox, oy in self.eye_offsets():
                        ex = pos_x + cell_w*ox
                        ey = pos_y + cell_h*oy
                        Color(1, 1, 1, 0.95)
                        Ellipse(pos=(ex, ey), size=(eye_size, eye_size))
                        Color(0.05, 0.08, 0.05, 1)
                        px = ex + eye_size/2 - pupil_size/2 + dx*pupil_size*0.35
                        py = ey + eye_size/2 - pupil_size/2 + dy*pupil_size*0.35
                        Ellipse(pos=(px, py), size=(pupil_size, pupil_size))

    def game_over(self, reason):
        if not self.running:
            return
        self.running = False
        self.paused = False
        SoundManager.play("death")
        self.stop_events()
        self._dismiss_pause_popup()
        SaveGameManager.delete()
        GameOverScreen.current_score = self.score
        GameOverScreen.reason = reason
        self.manager.current = "gameover"


class GameOverScreen(SpaceScreen):
    current_score = 0
    reason = ""

    def on_pre_enter(self):
        # Stop the previous neon title's pulse before rebuilding (each visit creates
        # a fresh NeonTitle; without this the Clock events would pile up).
        old_title = getattr(self, "_neon_title", None)
        if old_title is not None:
            old_title.stop_pulse()
        self.clear_widgets()
        root = FloatLayout()
        self.build_space_background(root)

        score_label = Label(text=f"{tr('score').upper()}  {self.current_score}", font_size="16sp", bold=True,
                            color=(0.82, 0.90, 1, 1), size_hint=(0.38, 0.08),
                            pos_hint={"right": 0.96, "top": 0.97}, halign="right", valign="middle")
        score_label.bind(size=lambda inst, _v: setattr(inst, "text_size", inst.size))
        root.add_widget(score_label)

        self._neon_title = None
        title = Label(
            text=tr("game_over"),
            font_size="28sp",
            bold=True,
            italic=True,
            color=(1.0, 0.22, 0.22, 1),
            size_hint=(0.92, 0.10),
            pos_hint={"center_x": 0.5, "center_y": 0.80},
            halign="center",
            valign="middle",
        )
        title.bind(size=lambda inst, _v: setattr(inst, "text_size", inst.size))
        root.add_widget(title)

        reason = Label(text=self.reason, font_size="16sp", color=(0.88, 0.88, 0.95, 1),
                       size_hint=(0.90, 0.07), pos_hint={"center_x": 0.5, "center_y": 0.64},
                       halign="center", valign="middle")
        reason.bind(size=lambda inst, _v: setattr(inst, "text_size", inst.size))
        root.add_widget(reason)

        initials_panel = BoxLayout(orientation="vertical", spacing=4, size_hint=(0.50, 0.11),
                                   pos_hint={"center_x": 0.5, "center_y": 0.46})
        initials_panel.add_widget(Label(text=tr("initials"), font_size="13sp", bold=True,
                                        color=(0.45, 1.00, 0.55, 1), size_hint_y=0.38))
        # Pungy: preload the last used initials so the field never silently saves
        # the AAA default when the player doesn't touch it — but only when the
        # stored initials are REAL ones. If the top record is itself "AAA" (the
        # default the player never edited), keep the gray AAA hint instead of
        # filling AAA as white real text (which looked like the block broke).
        last_initials = ""
        try:
            top_records = RecordManager.load_records()
            if top_records:
                cand = str(top_records[0].get("initials", "")).strip().upper()[:3]
                if cand and cand != "AAA":
                    last_initials = cand
        except Exception:
            last_initials = ""
        self.initials_input = TextInput(text=last_initials, hint_text="AAA", font_size="28sp", multiline=False,
                                        halign="center", size_hint_y=0.62,
                                        background_normal="", background_active="",
                                        background_color=(0, 0, 0, 0),
                                        foreground_color=(0.55, 1.00, 0.62, 1),
                                        hint_text_color=(0.35, 0.70, 0.42, 0.55),
                                        cursor_color=(0.45, 1.00, 0.55, 1), padding=[4, 6, 4, 6])
        self.initials_input.bind(text=self._limit_initials)
        initials_panel.add_widget(self.initials_input)
        root.add_widget(initials_panel)

        save_button = Button(
            text=tr("save_return"),
            font_size="18sp",
            bold=True,
            italic=True,
            color=(0.35, 1.00, 0.48, 1),
            background_normal="",
            background_down="",
            background_color=(0, 0, 0, 0),
            size_hint=(0.70, 0.08),
            pos_hint={"center_x": 0.5, "center_y": 0.22},
        )
        save_button.bind(on_press=self.save_and_return)
        root.add_widget(save_button)
        self.add_widget(root)

    def _limit_initials(self, instance, value):
        # Arcade initials: letters only, uppercase, hard limit of 3.
        filtered = "".join(ch for ch in value if ch.isalpha())[:3].upper()
        if value != filtered:
            instance.text = filtered

    def save_and_return(self, _instance):
        initials = self.initials_input.text.strip()[:3] or "AAA"
        RecordManager.save_record(initials, self.current_score)
        self.manager.current = "menu"


class HardCrazyWormApp(App):
    def build(self):
        self.title = "Hard Crazy Worm"
        manager = ScreenManager()
        manager.add_widget(MenuScreen(name="menu"))
        manager.add_widget(TutorialScreen(name="tutorial"))
        manager.add_widget(CreditsScreen(name="credits"))
        manager.add_widget(SettingsScreen(name="settings"))
        manager.add_widget(GameScreen(name="game"))
        manager.add_widget(GameOverScreen(name="gameover"))
        return manager

    def on_start(self):
        SoundManager.start_music()

    def _game_screen(self):
        if self.root is None:
            return None
        try:
            return self.root.get_screen("game")
        except Exception:
            return None

    def on_pause(self):
        SoundManager.suspend_music()
        game = self._game_screen()
        if game is not None:
            game.handle_app_pause()
        return True

    def on_resume(self):
        SoundManager.resume_music()
        game = self._game_screen()
        if game is not None:
            game.handle_app_resume()

    def on_stop(self):
        SoundManager.stop_music(reset_position=False)
        game = self._game_screen()
        if game is not None:
            game.handle_app_stop()


if __name__ == "__main__":
    HardCrazyWormApp().run()