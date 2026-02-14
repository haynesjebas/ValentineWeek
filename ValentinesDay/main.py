#!/usr/bin/env python3
"""
Valentine's Day — Valentine's Week Final Chapter
Theme: Completion — What is written by God finds its way to the heart.
Engine: glowing particle system, heart particles, idle animations,
cloth/hair sway, centered text, character fade-out, subtitle fades, video export.
"""

import pygame, math, sys, os, random, numpy as np
from moviepy import ImageSequenceClip, AudioFileClip, CompositeAudioClip

pygame.init()

WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Valentine's Day")

BG_COLOR = (211, 211, 211)
TEXT_COLOR = (45, 45, 45)
WHITE = (255, 255, 255)

pygame.font.init()
title_font = pygame.font.Font(None, 72)
try:
    theme_font = pygame.font.SysFont("georgia", 40, italic=True)
except Exception:
    theme_font = pygame.font.Font(None, 44)
try:
    subtitle_font = pygame.font.SysFont("georgia", 36, italic=True)
except Exception:
    subtitle_font = pygame.font.Font(None, 36)
try:
    centered_font = pygame.font.SysFont("georgia", 38, italic=True)
except Exception:
    centered_font = pygame.font.Font(None, 40)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "assets", "audio")
FADE_DURATION = 1500

# ---------------------------------------------------------------------------
# SCENES — Valentine's Day — 7 story scenes → 15 scene entries
# ---------------------------------------------------------------------------

SCENES = [
    # --- Scene 1: Theme Introduction (NO characters) ---
    {"id": 0, "type": "final",
     "vo": "val_sc1_title.mp3", "text": "Valentine's Day", "layout": "standing"},

    {"id": 1, "type": "theme",
     "vo": "val_sc1_intro.mp3",
     "text": "What is written by God\nfinds its way to the heart.",
     "layout": "standing"},

    {"id": 2, "type": "theme",
     "vo": "val_sc1_narr.mp3",
     "text": "They never planned this.\nThey never expected this.",
     "layout": "standing"},

    # --- Scene 2: Characters Appear Together ---
    {"id": 3, "type": "scene",
     "vo": "val_sc2.mp3",
     "text": "They were different.\nThey were uncertain.\nThey were afraid.",
     "layout": "standing", "both": True},

    {"id": 4, "type": "scene",
     "vo": "val_sc2b.mp3",
     "text": "But step by step…\nthey stayed.",
     "layout": "standing", "both": True, "smile": 0.2},

    # --- Scene 3: Acknowledging God's Grace ---
    {"id": 5, "type": "scene",
     "vo": "val_sc3a.mp3",
     "text": "There were moments they could not see the path.\nMoments they did not understand why.",
     "layout": "standing", "both": True, "glow_boost": True},

    {"id": 6, "type": "scene",
     "vo": "val_sc3b.mp3",
     "text": "But what is held by God's grace\nnever loses its way.",
     "layout": "standing", "both": True, "glow_boost": True},

    {"id": 7, "type": "scene",
     "vo": "val_sc3c.mp3",
     "text": "By His will,\nthey were led to each other.",
     "layout": "standing", "both": True, "look_at_each_other": True,
     "smile": 0.4, "glow_boost": True},

    # --- Scene 4: Peaceful Fulfillment ---
    {"id": 8, "type": "scene",
     "vo": "val_sc4a.mp3",
     "text": "Not by force.\nNot by chance.\nBut by love that was protected.",
     "layout": "standing_close", "both": True, "smile": 0.5},

    {"id": 9, "type": "scene",
     "vo": "val_sc4b.mp3",
     "text": "They did not become perfect.\nThey became true.",
     "layout": "standing_close", "both": True, "smile": 0.7},

    # --- Scene 5: Emotional Completion ---
    {"id": 10, "type": "scene",
     "vo": "val_sc5.mp3",
     "text": "This was never just a week.\nIt was the beginning of a lifetime.",
     "layout": "standing_close", "both": True, "smile": 0.9,
     "hearts": True, "hearts_fullscreen": True},

    # --- Scene 6: Future Life Epilogue (NO characters) ---
    {"id": 11, "type": "centered_text",
     "vo": "val_sc6a.mp3",
     "text": "They walked forward together.\nThrough every season.\nThrough every test.\nThrough every blessing.",
     "layout": "standing_close"},

    {"id": 12, "type": "centered_text",
     "vo": "val_sc6b.mp3",
     "text": "And by the grace of God,\nthey lived the rest of their lives together.",
     "layout": "standing_close"},

    # --- Scene 7: Final Ending — Characters reappear holding hands ---
    {"id": 13, "type": "scene",
     "vo": "val_sc7_ending.mp3",
     "text": "Their story was no longer uncertain.\nIt was complete.",
     "layout": "standing_close", "both": True, "smile": 1.0,
     "hold_extra": 4000, "fade_to_black": True,
     "hearts": True, "hearts_fullscreen": True,
     "holding_hands": True, "look_at_each_other": True,
     "cinematic": True},
]

# ---------------------------------------------------------------------------
# CINEMATIC EFFECTS — warm gradient, vignette, bokeh
# ---------------------------------------------------------------------------

def draw_warm_gradient_bg(surface, w, h, t=0):
    """Draw a warm vertical gradient background with subtle color shift over time."""
    # Top: deep warm amber-brown, Bottom: dark rich brown
    pulse = math.sin(t * 0.0005) * 0.05  # very subtle color pulse
    for y in range(0, h, 3):  # step by 3 for performance
        ratio = y / h
        r = int(45 + 30 * (1 - ratio) + pulse * 20)
        g = int(25 + 15 * (1 - ratio) + pulse * 10)
        b = int(20 + 10 * (1 - ratio))
        pygame.draw.rect(surface, (min(255, r), min(255, g), min(255, b)),
                         (0, y, w, 3))

def draw_vignette(surface, w, h, intensity=120):
    """Draw a cinematic vignette — darkened edges, bright center."""
    vig = pygame.Surface((w, h), pygame.SRCALPHA)
    cx, cy = w // 2, h // 2
    max_dist = math.sqrt(cx * cx + cy * cy)
    # Draw concentric semi-transparent dark rectangles from edge inward
    steps = 20
    for i in range(steps):
        ratio = i / steps  # 0=center, 1=edge
        alpha = int(intensity * ratio * ratio)  # quadratic falloff
        margin_x = int(cx * (1 - ratio))
        margin_y = int(cy * (1 - ratio))
        rect_w = w - 2 * margin_x
        rect_h = h - 2 * margin_y
        if rect_w > 0 and rect_h > 0:
            s = pygame.Surface((rect_w, rect_h), pygame.SRCALPHA)
            s.fill((0, 0, 0, alpha))
            vig.blit(s, (margin_x, margin_y))
    # Apply outer border darkening
    border = pygame.Surface((w, h), pygame.SRCALPHA)
    # Top and bottom bands
    for y in range(80):
        a = int(intensity * 0.7 * (1 - y / 80))
        pygame.draw.line(border, (0, 0, 0, a), (0, y), (w, y))
        pygame.draw.line(border, (0, 0, 0, a), (0, h - 1 - y), (w, h - 1 - y))
    # Left and right bands
    for x in range(100):
        a = int(intensity * 0.5 * (1 - x / 100))
        pygame.draw.line(border, (0, 0, 0, a), (x, 0), (x, h))
        pygame.draw.line(border, (0, 0, 0, a), (w - 1 - x, 0), (w - 1 - x, h))
    surface.blit(border, (0, 0))

class BokehOrb:
    """A soft, glowing bokeh light orb."""
    def __init__(self, w, h):
        self.x = random.uniform(0, w)
        self.y = random.uniform(0, h)
        self.r = random.uniform(15, 50)
        self.alpha = random.uniform(15, 45)
        self.drift_x = random.uniform(-0.15, 0.15)
        self.drift_y = random.uniform(-0.1, 0.1)
        self.pulse_speed = random.uniform(0.001, 0.004)
        self.pulse_phase = random.uniform(0, math.pi * 2)
        self.color = random.choice([
            (255, 220, 150),  # warm gold
            (255, 200, 130),  # amber
            (255, 180, 160),  # soft pink-gold
            (255, 240, 200),  # cream
            (255, 160, 140),  # rose
        ])
        self.w, self.h = w, h
    def update(self, t):
        self.x += self.drift_x
        self.y += self.drift_y
        # Wrap around
        if self.x < -self.r: self.x = self.w + self.r
        if self.x > self.w + self.r: self.x = -self.r
        if self.y < -self.r: self.y = self.h + self.r
        if self.y > self.h + self.r: self.y = -self.r
    def draw(self, surface, t):
        pulse = 0.6 + 0.4 * math.sin(t * self.pulse_speed + self.pulse_phase)
        a = int(self.alpha * pulse)
        if a < 2: return
        s = int(self.r * 2.5)
        orb = pygame.Surface((s * 2, s * 2), pygame.SRCALPHA)
        # Draw concentric circles for soft glow
        for i in range(8, 0, -1):
            ratio = i / 8
            cr = int(self.r * ratio * (0.8 + 0.2 * pulse))
            ca = int(a * (1 - ratio) * 0.7)
            if cr > 0 and ca > 0:
                pygame.draw.circle(orb, (*self.color, min(255, ca)),
                                   (s, s), cr)
        surface.blit(orb, (int(self.x - s), int(self.y - s)))

class BokehSystem:
    def __init__(self, count=25):
        self.orbs = [BokehOrb(WIDTH, HEIGHT) for _ in range(count)]
    def update(self, t):
        for o in self.orbs:
            o.update(t)
    def draw(self, surface, t):
        for o in self.orbs:
            o.draw(surface, t)

# ---------------------------------------------------------------------------
# GLOWING PARTICLE SYSTEM — soft warm golden / white glow
# ---------------------------------------------------------------------------

class GlowParticle:
    def __init__(self):
        self.reset(True)
    def reset(self, initial=False):
        self.x = random.uniform(-40, WIDTH + 40) if initial else random.choice([
            random.uniform(-60, -10), random.uniform(WIDTH + 10, WIDTH + 60),
            random.uniform(-40, WIDTH + 40)])
        self.y = random.uniform(-20, HEIGHT + 20) if initial else random.uniform(-30, HEIGHT * 0.3)
        self.size = random.uniform(2, 6)
        self.speed_x = random.uniform(-0.12, 0.12)
        self.speed_y = random.uniform(0.02, 0.18)
        self.angle = random.uniform(0, 360)
        self.spin = random.uniform(-0.2, 0.2)
        self.alpha_max = random.randint(40, 100)
        self.alpha = 0 if not initial else random.randint(15, self.alpha_max)
        self.life = random.uniform(500, 1400)
        self.age = 0 if not initial else random.uniform(0, self.life * 0.6)
        self.pulse_phase = random.uniform(0, math.pi * 2)
        self.color = random.choice([
            (255, 245, 220), (255, 235, 200), (255, 250, 240),
            (240, 230, 210), (255, 255, 245), (255, 240, 215)])
    def update(self, wind_offset=0):
        self.x += self.speed_x + wind_offset * 0.015
        self.y += self.speed_y + math.sin(self.age * 0.006) * 0.1
        self.angle += self.spin
        self.age += 1
        fz = self.life * 0.25
        base_alpha = self.alpha_max
        if self.age < fz:
            base_alpha = int(self.alpha_max * (self.age / fz))
        elif self.age > self.life - fz:
            base_alpha = int(self.alpha_max * ((self.life - self.age) / fz))
        pulse = math.sin(self.age * 0.015 + self.pulse_phase) * 0.2 + 0.8
        self.alpha = max(0, min(self.alpha_max, int(base_alpha * pulse)))
        if self.y > HEIGHT + 40 or self.age >= self.life:
            self.reset(False)
    def draw(self, surface):
        if self.alpha <= 0:
            return
        s = int(self.size)
        # Soft circle glow
        glow_r = s * 3
        ps = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        # Outer glow
        for ring in range(3, 0, -1):
            r = int(glow_r * ring / 3)
            a = int(self.alpha * (0.15 / ring))
            pygame.draw.circle(ps, (*self.color, a), (glow_r, glow_r), r)
        # Core
        pygame.draw.circle(ps, (*self.color, self.alpha), (glow_r, glow_r), s)
        surface.blit(ps, (int(self.x - glow_r), int(self.y - glow_r)))

class ParticleSystem:
    def __init__(self, count=35):
        self.particles = [GlowParticle() for _ in range(count)]
        self.wind_phase = 0
        self.base_count = count
    def update(self, boost=False):
        self.wind_phase += 0.004
        w = math.sin(self.wind_phase) * 0.4
        target = self.base_count * 2 if boost else self.base_count
        while len(self.particles) < target:
            self.particles.append(GlowParticle())
        for p in self.particles:
            p.update(w)
    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)
    def get_wind(self):
        return math.sin(self.wind_phase) * 0.4

# ---------------------------------------------------------------------------
# HEART PARTICLE SYSTEM
# ---------------------------------------------------------------------------

class Heart:
    def __init__(self, x, y):
        self.x = x + random.uniform(-6, 6)
        self.y = y + random.uniform(-4, 4)
        self.speed_x = random.uniform(-0.15, 0.15)
        self.speed_y = random.uniform(-0.2, 0.2)  # float gently in any dir
        self.size = random.uniform(4, 8)
        self.alpha = 255
        self.life = random.uniform(120, 240)
        self.age = 0
        self.color = random.choice([
            (255, 100, 120), (255, 130, 150), (240, 80, 110),
            (255, 110, 140), (230, 90, 120)])
    def update(self):
        self.x += self.speed_x + math.sin(self.age * 0.03) * 0.2
        self.y += self.speed_y
        self.age += 1
        fz = self.life * 0.3
        if self.age > self.life - fz:
            self.alpha = int(255 * ((self.life - self.age) / fz))
        if self.age < 20:
            self.alpha = min(self.alpha, int(255 * self.age / 20))
        self.alpha = max(0, self.alpha)
    def draw(self, surface, global_alpha=255):
        if self.alpha <= 0:
            return
        a = int(self.alpha * global_alpha / 255)
        if a <= 0:
            return
        s = int(self.size)
        hs = pygame.Surface((s * 3, s * 3), pygame.SRCALPHA)
        cx, cy = s * 1.5, s * 1.5
        r = s * 0.5
        pygame.draw.circle(hs, (*self.color, a),
                           (int(cx - r * 0.6), int(cy - r * 0.3)), int(r))
        pygame.draw.circle(hs, (*self.color, a),
                           (int(cx + r * 0.6), int(cy - r * 0.3)), int(r))
        pygame.draw.polygon(hs, (*self.color, a), [
            (int(cx - r * 1.4), int(cy)),
            (int(cx + r * 1.4), int(cy)),
            (int(cx), int(cy + r * 1.8))])
        surface.blit(hs, (int(self.x - s * 1.5), int(self.y - s * 1.5)))
    @property
    def alive(self):
        return self.age < self.life

class HeartSystem:
    def __init__(self):
        self.hearts = []
        self.spawn_timer = 0
        self.spread_level = 0.0  # 0=near chars, 1=full screen
    def update(self, spawning=False, cx=0, cy=0, spread=0.0):
        self.spread_level = spread
        if spawning:
            self.spawn_timer += 1
            freq = 1  # spawn every single frame
            if self.spawn_timer % freq == 0:
                count = random.randint(6, 14 + int(spread * 12))
                for _ in range(count):
                    # Spawn using absolute screen coordinates for full coverage
                    if spread > 0.5:
                        sx = random.uniform(0, WIDTH)
                        sy = random.uniform(0, HEIGHT)
                    else:
                        sx = cx + random.uniform(-120, 120) + random.uniform(-WIDTH * 0.3, WIDTH * 0.3) * spread
                        sy = cy + random.uniform(-60, 60) + random.uniform(-HEIGHT * 0.3, HEIGHT * 0.3) * spread
                    self.hearts.append(Heart(sx, sy))
        self.hearts = [h for h in self.hearts if h.alive]
        for h in self.hearts:
            h.update()
    def draw(self, surface, global_alpha=255):
        for h in self.hearts:
            h.draw(surface, global_alpha)

# ---------------------------------------------------------------------------
# IDLE SYSTEM — blink, breathe, head micro-motion
# ---------------------------------------------------------------------------

class IdleState:
    def __init__(self):
        self.blink_timer = random.uniform(180, 360)
        self.blink_frame = 0
        self.blink_duration = 8
        self.head_offset_x = 0.0
        self.head_offset_y = 0.0
        self.head_target_x = 0.0
        self.head_target_y = 0.0
        self.head_timer = random.uniform(120, 300)
    def update(self):
        if self.blink_frame > 0:
            self.blink_frame -= 1
        else:
            self.blink_timer -= 1
            if self.blink_timer <= 0:
                self.blink_frame = self.blink_duration
                self.blink_timer = random.uniform(180, 360)
        self.head_timer -= 1
        if self.head_timer <= 0:
            self.head_target_x = random.uniform(-1.5, 1.5)
            self.head_target_y = random.uniform(-0.8, 0.8)
            self.head_timer = random.uniform(120, 300)
        self.head_offset_x += (self.head_target_x - self.head_offset_x) * 0.03
        self.head_offset_y += (self.head_target_y - self.head_offset_y) * 0.03
    @property
    def is_blinking(self):
        return self.blink_frame > 0

# ---------------------------------------------------------------------------
# DRAWING UTILITIES
# ---------------------------------------------------------------------------

def draw_capsule(surface, color, p1, p2, radius):
    pygame.draw.line(surface, color, p1, p2, radius * 2)
    pygame.draw.circle(surface, color, (int(p1[0]), int(p1[1])), radius)
    pygame.draw.circle(surface, color, (int(p2[0]), int(p2[1])), radius)

def _lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)

def _ease_out(t):
    return 1.0 - (1.0 - t) ** 2


def _compute_skeleton(x, y, is_woman, breathing, idle, wind, virtual_time):
    scale = 0.78 if is_woman else 0.95
    HEAD_R = 30 * scale
    SHOULDER_W = (52 if is_woman else 68) * scale
    TORSO_H = (110 + breathing) * scale
    HIP_W = (56 if is_woman else 48) * scale
    LEG_L = 120 * scale
    base_x = x
    base_y = y - breathing * (0.3 if is_woman else 0.4)
    head_ox = idle.head_offset_x if idle else 0
    head_oy = idle.head_offset_y if idle else 0
    cloth_sway = wind * 2.5 + math.sin(virtual_time * 0.0015) * 1.2
    hips_y = base_y - LEG_L
    shoulder_y = hips_y - TORSO_H
    head_cy = shoulder_y - 10 * scale - HEAD_R
    head_cx = base_x + head_ox
    return {
        'scale': scale, 'base_x': base_x, 'base_y': base_y,
        'hips_y': hips_y, 'shoulder_y': shoulder_y,
        'head_cx': head_cx + head_ox, 'head_cy': head_cy + head_oy,
        'HEAD_R': HEAD_R, 'SHOULDER_W': SHOULDER_W, 'TORSO_H': TORSO_H,
        'HIP_W': HIP_W, 'LEG_L': LEG_L, 'cloth_sway': cloth_sway,
        'l_shoulder': (base_x - SHOULDER_W / 2 - (5 if not is_woman else 0), shoulder_y + 10),
        'r_shoulder': (base_x + SHOULDER_W / 2, shoulder_y + 10),
    }


def draw_body(surface, skel, is_woman, talking, virtual_time, idle,
              lean_x=0, lean_y=0, smile=0.0, eyes_closed=False, head_tilt=0,
              look_direction=0):
    """Draw body, head, face. look_direction: -1=left, 0=forward, +1=right."""
    scale = skel['scale']
    base_x, base_y = skel['base_x'], skel['base_y']
    hips_y, shoulder_y = skel['hips_y'], skel['shoulder_y']
    HEAD_R, SHOULDER_W = skel['HEAD_R'], skel['SHOULDER_W']
    TORSO_H, HIP_W = skel['TORSO_H'], skel['HIP_W']
    cloth_sway = skel['cloth_sway']
    head_cx = skel['head_cx'] + lean_x + head_tilt
    head_cy = skel['head_cy'] + lean_y + abs(head_tilt) * 0.15

    # --- Valentine's Day Outfits ---
    SKIN_COLOR = (255, 255, 255)  # White skin tone
    if is_woman:
        # Slightly dark green one-piece dress
        clothing_color = (75, 130, 85)
        clothing_accent = (60, 110, 70)
        leg_color = (255, 255, 255)  # White legs
        shoe_color = (255, 255, 255)
    else:
        # Light green shirt
        shirt_color = (130, 195, 140)
        shirt_outline = (110, 170, 120)
        # Black pants
        pants_color = (35, 35, 40)
        # Black shoes
        shoe_color = (25, 25, 30)

    # Shadow
    sw = 110 * scale
    pygame.draw.ellipse(surface, (190, 190, 190),
                        (base_x - sw / 2, base_y - 10, sw, 20))

    # Legs
    if not is_woman:
        for side in [-1, 1]:
            lx = base_x + side * (HIP_W / 4)
            draw_capsule(surface, pants_color, (lx, hips_y), (lx, base_y), int(8 * scale))
            pygame.draw.circle(surface, shoe_color, (int(lx), int(base_y)), int(10 * scale))
    else:
        for side in [-1, 1]:
            lx = base_x + side * (HIP_W / 4)
            draw_capsule(surface, leg_color,
                         (base_x + side * (HIP_W / 4), hips_y + 30 * scale),
                         (lx, base_y), int(7 * scale))
            pygame.draw.circle(surface, shoe_color, (int(lx), int(base_y)), int(9 * scale))

    # Torso
    sway_r = cloth_sway * 0.5
    if is_woman:
        # One-piece dress extends down to near knee
        pts = [
            (base_x - SHOULDER_W / 2 - sway_r * 0.3, shoulder_y),
            (base_x + SHOULDER_W / 2 + sway_r * 0.3, shoulder_y),
            (base_x + HIP_W / 2 + 20 * scale + sway_r, hips_y + 30 * scale),
            (base_x - HIP_W / 2 - 20 * scale - sway_r * 0.2, hips_y + 30 * scale)]
        pygame.draw.polygon(surface, clothing_color, pts)
        # Dress detail lines
        for i in range(1, 4):
            ly = shoulder_y + i * 25 * scale
            pygame.draw.line(surface, clothing_accent,
                             (base_x - SHOULDER_W / 2 + i * 2, ly),
                             (base_x + SHOULDER_W / 2 - i * 2, ly), 1)
        pygame.draw.polygon(surface, clothing_accent, pts, 2)
    else:
        # Green full-sleeve shirt (extends to hips)
        shirt_bottom_y = hips_y  # full shirt extends to waist
        pts = [
            (base_x - SHOULDER_W / 2 - sway_r * 0.2, shoulder_y),
            (base_x + SHOULDER_W / 2 + sway_r * 0.2, shoulder_y),
            (base_x + HIP_W / 2 + sway_r * 0.3, shirt_bottom_y),
            (base_x - HIP_W / 2 - sway_r * 0.1, shirt_bottom_y)]
        pygame.draw.polygon(surface, shirt_color, pts)
        pygame.draw.polygon(surface, shirt_outline, pts, 2)
        # Belt line at shirt bottom
        pygame.draw.line(surface, (30, 30, 35),
                         (base_x - HIP_W / 2 - 2, shirt_bottom_y),
                         (base_x + HIP_W / 2 + 2, shirt_bottom_y), 2)

    # Head
    pygame.draw.circle(surface, (255, 255, 255), (int(head_cx), int(head_cy)), int(HEAD_R))
    pygame.draw.circle(surface, (240, 240, 240), (int(head_cx), int(head_cy)), int(HEAD_R), 2)

    # Blush
    if smile > 0.1:
        ba = min(70, int(70 * ((smile - 0.1) / 0.9)))
        br = int(8 * scale)
        for sx in [-1, 1]:
            bx = int(head_cx + sx * 14 * scale)
            by = int(head_cy + HEAD_R * 0.15)
            bs = pygame.Surface((br * 2, br * 2), pygame.SRCALPHA)
            pygame.draw.ellipse(bs, (255, 160, 160, ba), (0, 0, br * 2, br * 2))
            surface.blit(bs, (bx - br, by - br))

    # Eyes — with look_direction support
    eye_x_off = 10 * scale
    eye_y_off = -HEAD_R / 5
    is_blinking = idle.is_blinking if idle else False
    for sx in [-1, 1]:
        ex = int(head_cx + sx * eye_x_off + look_direction * 3 * scale)
        ey = int(head_cy + eye_y_off)
        if eyes_closed or is_blinking:
            if eyes_closed and smile > 0.3:
                pygame.draw.arc(surface, (40, 40, 40),
                                (ex - 4, ey - 2, 8, 6), 0.2, math.pi - 0.2, 2)
            else:
                pygame.draw.line(surface, (40, 40, 40), (ex - 3, ey), (ex + 3, ey), 2)
        else:
            pygame.draw.circle(surface, (40, 40, 40), (ex, ey), 3)

    # Mouth — calm peaceful smile
    m_y = head_cy + HEAD_R / 2
    if talking:
        talk_h = 4 + math.sin(virtual_time * 0.02) * 4
        pygame.draw.ellipse(surface, (40, 40, 40),
                            (head_cx - 4, m_y - talk_h / 2, 8, max(2, talk_h)))
    elif smile > 0.05:
        mouth_w = 5 + smile * 2
        curve_h = smile * 3
        mpts = []
        for i in range(9):
            t = i / 8.0
            mx = head_cx - mouth_w + t * mouth_w * 2
            my = m_y - curve_h * (2 * t - 1) ** 2 + curve_h
            mpts.append((mx, my))
        pygame.draw.lines(surface, (40, 40, 40), False, mpts, 2)
    else:
        pygame.draw.line(surface, (40, 40, 40), (head_cx - 4, m_y), (head_cx + 4, m_y), 2)

    # Hair ribbon for girl
    if is_woman:
        hs = cloth_sway * 0.6
        bx = head_cx + 22 * scale + hs * 0.4
        by = head_cy - 25 * scale
        # Small ribbon in dark green accent
        pygame.draw.ellipse(surface, (55, 100, 65), (bx - 12, by - 6, 10, 12))
        pygame.draw.ellipse(surface, (55, 100, 65), (bx + 2, by - 6, 10, 12))
        pygame.draw.circle(surface, (45, 85, 55), (int(bx), int(by)), 4)

    return head_cx, head_cy


def draw_arm_segment_half_sleeve(surface, shoulder, elbow, hand, radius, sleeve_color):
    """Draw arm with half-sleeve (shoulder to elbow), forearm exposed."""
    skin = (255, 255, 255)
    # Sleeve from shoulder to elbow only
    draw_capsule(surface, sleeve_color, shoulder, elbow, radius)
    # Exposed forearm from elbow to hand
    draw_capsule(surface, skin, elbow, hand, radius)


def draw_arm_segment_mid_sleeve(surface, shoulder, elbow, hand, radius, sleeve_color):
    """Draw arm with sleeve past elbow (about 70% down), forearm and hand exposed."""
    skin = (255, 255, 255)
    # Sleeve covers shoulder to past elbow (70% of arm length)
    mid_forearm = ((elbow[0] + hand[0]) / 2, (elbow[1] + hand[1]) / 2)
    sleeve_end = ((elbow[0] * 0.4 + mid_forearm[0] * 0.6),
                  (elbow[1] * 0.4 + mid_forearm[1] * 0.6))
    draw_capsule(surface, sleeve_color, shoulder, elbow, radius)
    draw_capsule(surface, sleeve_color, elbow, sleeve_end, radius)
    # Exposed forearm from sleeve end to hand
    draw_capsule(surface, skin, sleeve_end, hand, radius)



def draw_human_standing(surface, x, y, is_woman, breathing, talking,
                        virtual_time, idle, wind, smile=0.0,
                        look_direction=0, holding_hands=False):
    skel = _compute_skeleton(x, y, is_woman, breathing, idle, wind, virtual_time)
    scale = skel['scale']
    draw_body(surface, skel, is_woman, talking, virtual_time, idle,
              smile=smile, look_direction=look_direction)
    arm_r = int(7 * scale)
    cs = skel['cloth_sway']
    # Hand positions (end of arm)
    lh = (skel['base_x'] - skel['SHOULDER_W'] / 2 - 5 + cs * 0.3,
          skel['shoulder_y'] + 95 * scale)
    rh = (skel['base_x'] + skel['SHOULDER_W'] / 2 + 5 + cs * 0.2,
          skel['shoulder_y'] + 95 * scale)
    # If holding hands, move the inner hand toward partner
    if holding_hands:
        if is_woman:
            # Girl's left hand reaches far toward boy
            lh = (lh[0] - 40 * scale, lh[1] - 3 * scale)
        else:
            # Boy's right hand reaches far toward girl
            rh = (rh[0] + 40 * scale, rh[1] - 3 * scale)
    # Elbow midpoints (halfway between shoulder and hand with slight outward bend)
    l_elbow = ((skel['l_shoulder'][0] + lh[0]) / 2 - 4 * scale,
               (skel['l_shoulder'][1] + lh[1]) / 2)
    r_elbow = ((skel['r_shoulder'][0] + rh[0]) / 2 + 4 * scale,
               (skel['r_shoulder'][1] + rh[1]) / 2)
    if is_woman:
        # Girl: dark green dress sleeves past elbow, forearm/hand exposed
        sleeve_col = (75, 130, 85)
        draw_arm_segment_mid_sleeve(surface, skel['l_shoulder'], l_elbow, lh, arm_r, sleeve_col)
        draw_arm_segment_mid_sleeve(surface, skel['r_shoulder'], r_elbow, rh, arm_r, sleeve_col)
    else:
        # Boy: light green half-sleeve shirt (to elbow), forearm/hand exposed
        sleeve_col = (130, 195, 140)
        draw_arm_segment_half_sleeve(surface, skel['l_shoulder'], l_elbow, lh, arm_r, sleeve_col)
        draw_arm_segment_half_sleeve(surface, skel['r_shoulder'], r_elbow, rh, arm_r, sleeve_col)
    return skel, lh, rh


# ---------------------------------------------------------------------------
# SUBTITLE RENDERER
# ---------------------------------------------------------------------------

class SubtitleRenderer:
    FADE_IN_MS = 400
    FADE_OUT_MS = 400
    def __init__(self):
        self.text = ""
        self.start_time = 0
        self.end_time = 0
        self.alpha = 0
    def show(self, text, now):
        self.text = text
        self.start_time = now
        self.end_time = 0
        self.alpha = 0
    def begin_fade_out(self, now):
        if self.end_time == 0:
            self.end_time = now
    def update(self, now):
        if not self.text:
            self.alpha = 0
            return
        elapsed = now - self.start_time
        if elapsed < self.FADE_IN_MS:
            self.alpha = int(255 * (elapsed / self.FADE_IN_MS))
        else:
            self.alpha = 255
        if self.end_time > 0:
            fe = now - self.end_time
            if fe < self.FADE_OUT_MS:
                self.alpha = int(255 * (1 - fe / self.FADE_OUT_MS))
            else:
                self.alpha = 0
                self.text = ""
    def draw(self, surface, color=None):
        if not self.text or self.alpha <= 0:
            return
        c = color or TEXT_COLOR
        lines = self.text.split("\n")
        start_y = HEIGHT - 40 - len(lines) * 40
        for i, line in enumerate(lines):
            rendered = subtitle_font.render(line, True, c)
            alpha_surf = rendered.copy()
            alpha_surf.set_alpha(self.alpha)
            r = alpha_surf.get_rect(center=(WIDTH // 2, start_y + i * 40))
            surface.blit(alpha_surf, r)

# ---------------------------------------------------------------------------
# AUDIO CONTROLLER
# ---------------------------------------------------------------------------

class AudioController:
    def __init__(self):
        pygame.mixer.init()
        self.vo_channel = pygame.mixer.Channel(0)
    def play(self, filename):
        path = os.path.join(AUDIO_DIR, filename)
        if not os.path.exists(path):
            print(f"ERROR: Audio not found: {path}")
            return 0
        try:
            sound = pygame.mixer.Sound(path)
            self.vo_channel.play(sound)
            return int(sound.get_length() * 1000)
        except Exception as e:
            print(f"Error: {e}")
            return 0

# ---------------------------------------------------------------------------
# APPLICATION
# ---------------------------------------------------------------------------

class App:
    def __init__(self):
        self.audio = AudioController()
        self.particles = ParticleSystem(35)
        self.hearts = HeartSystem()
        self.bokeh = BokehSystem(30)
        self.subtitle = SubtitleRenderer()
        self.boy_idle = IdleState()
        self.girl_idle = IdleState()

        self.state = "INIT"
        self.current_scene_idx = -1
        self.scene_start_time = 0
        self.transition_start_time = 0
        self.fade_alpha = 0
        self.running = True
        self.clock = pygame.time.Clock()
        self.audio_finished_time = 0

        self.delay_phase = False
        self.start_delay = 0
        self.main_vo_start_time = 0

        self.frames = []
        self.frame_count = 0
        self.virtual_time = 0.0
        self.fps = 60
        self.scene_audio_events = []
        self.current_audio_duration = 0

        self.heart_cx = WIDTH / 2
        self.heart_cy = HEIGHT * 0.3
        self.heart_spread = 0.0  # 0=near chars, 1=full screen
        self.hearts_global_alpha = 255

        # Character fade-out alpha (255=fully visible, 0=invisible)
        self.char_alpha = 255
        self.char_fading = False

        # Positions
        self.boy_x_standing = WIDTH * 0.42
        self.girl_x_standing = WIDTH * 0.58
        self.boy_x_close = WIDTH * 0.45
        self.girl_x_close = WIDTH * 0.55

    def _positions_for_layout(self, layout):
        if layout == "standing_close":
            return self.boy_x_close, self.girl_x_close
        return self.boy_x_standing, self.girl_x_standing

    def next_scene(self):
        self.subtitle.begin_fade_out(self.virtual_time)
        self.current_scene_idx += 1
        if self.current_scene_idx >= len(SCENES):
            self.running = False
            return
        self.state = "FADE_IN"
        self.scene_start_time = self.virtual_time
        self.transition_start_time = self.virtual_time
        self.audio_finished_time = 0
        self.main_vo_start_time = self.virtual_time
        self.start_delay = 0
        self.delay_phase = False

        scene = SCENES[self.current_scene_idx]

        # Reset character fade for non-fade-out scenes
        if not scene.get("char_fade_out"):
            if not self.char_fading:
                self.char_alpha = 255
        else:
            self.char_fading = True

        if scene.get("start_delay", 0) > 0:
            self.start_delay = scene["start_delay"]
            self.delay_phase = True
            self.current_audio_duration = 0
        elif "vo" in scene:
            self.current_audio_duration = self.audio.play(scene["vo"])
            self.scene_audio_events.append((self.virtual_time, scene["vo"]))
            self.main_vo_start_time = self.virtual_time
        else:
            self.current_audio_duration = 0
        if not self.delay_phase and scene.get("text"):
            self.subtitle.show(scene["text"], self.virtual_time)

    def update(self):
        now = self.virtual_time
        if self.current_scene_idx == -1:
            self.next_scene()
            return
        scene = SCENES[self.current_scene_idx]

        glow_boost = scene.get("glow_boost", False)
        self.particles.update(boost=glow_boost)
        self.subtitle.update(now)
        self.boy_idle.update()
        self.girl_idle.update()

        # Heart updates during heart scenes ONLY
        if scene.get("hearts") or scene.get("hearts_bg"):
            boy_x, girl_x = self._positions_for_layout(scene.get("layout", "standing"))
            mid_x = (boy_x + girl_x) / 2
            mid_y = HEIGHT * 0.35
            self.heart_cx = mid_x
            self.heart_cy = mid_y
            # Full screen hearts — start at max spread immediately
            if scene.get("hearts_fullscreen"):
                self.heart_spread = 1.0
            elif scene.get("hearts_bg"):
                self.heart_spread = min(1.0, self.heart_spread + 0.002)
            elif scene.get("hearts"):
                self.heart_spread = min(0.5, self.heart_spread + 0.003)
            self.hearts.update(True, mid_x, mid_y, spread=self.heart_spread)
            # Hearts stay at full alpha — fade-to-black overlay handles fading
            self.hearts_global_alpha = 255
        else:
            # Non-heart scene: clear hearts immediately so they don't bleed
            self.hearts.hearts.clear()
            self.hearts.update(False)
            self.heart_spread = 0.0
            self.hearts_global_alpha = 255

        # Character fade-out
        if scene.get("char_fade_out") and self.char_alpha > 0:
            elapsed = now - self.scene_start_time
            # Fade chars over the duration of the audio + hold
            fade_dur = max(self.current_audio_duration, 3000)
            self.char_alpha = max(0, int(255 * (1.0 - elapsed / fade_dur)))

        if self.state == "FADE_IN":
            elapsed = now - self.transition_start_time
            self.fade_alpha = max(0, 255 - int(255 * (elapsed / FADE_DURATION)))
            if elapsed > FADE_DURATION:
                self.state = "PLAYING"
                self.fade_alpha = 0
        elif self.state == "PLAYING":
            if self.delay_phase:
                if now - self.scene_start_time > self.start_delay:
                    self.delay_phase = False
                    self.main_vo_start_time = now
                    if "vo" in scene:
                        self.current_audio_duration = self.audio.play(scene["vo"])
                        self.scene_audio_events.append((now, scene["vo"]))
                    if scene.get("text"):
                        self.subtitle.show(scene["text"], now)
                    self.audio_finished_time = 0
                return
            post_delay = scene.get("hold_extra", 1500)
            elapsed_m = now - self.main_vo_start_time
            if not (elapsed_m < self.current_audio_duration) and elapsed_m > 1000:
                if self.audio_finished_time == 0:
                    self.audio_finished_time = now
                if now - self.audio_finished_time > post_delay:
                    self.state = "FADE_OUT"
                    self.transition_start_time = now
                    self.subtitle.begin_fade_out(now)
        elif self.state == "FADE_OUT":
            elapsed = now - self.transition_start_time
            # For fade_to_black scenes, fade to black instead of bg
            self.fade_alpha = min(255, int(255 * (elapsed / FADE_DURATION)))
            if elapsed > FADE_DURATION:
                self.next_scene()

    def _draw_centered_text(self, text, font_to_use=None, color=None):
        """Draw centered text with subtitle alpha for fading."""
        f = font_to_use or centered_font
        c = color or TEXT_COLOR
        lines = text.split("\n")
        ls = 55
        sy = (HEIGHT - len(lines) * ls) // 2
        for i, line in enumerate(lines):
            surf = f.render(line, True, c)
            alpha_surf = surf.copy()
            alpha_surf.set_alpha(self.subtitle.alpha if self.subtitle.alpha > 0 else 255)
            r = alpha_surf.get_rect(center=(WIDTH // 2, sy + i * ls))
            screen.blit(alpha_surf, r)

    def draw(self):
        if self.current_scene_idx < 0 or self.current_scene_idx >= len(SCENES):
            return
        screen.fill(BG_COLOR)
        scene = SCENES[self.current_scene_idx]
        now = self.virtual_time
        breath = math.sin(now * 0.002) * 3
        layout = scene.get("layout", "standing")
        wind = self.particles.get_wind()
        floor_y = int(HEIGHT * 0.72)
        show_chars = scene.get("both") or scene.get("boy") or scene.get("girl")
        scene_type = scene.get("type", "scene")
        scene_smile = scene.get("smile", 0.0)
        look_at = scene.get("look_at_each_other", False)

        is_cinematic = scene.get("cinematic", False)
        scene_text_color = WHITE if is_cinematic else TEXT_COLOR

        if scene_type in ["theme", "final"] and not show_chars:
            # Centered text (no characters)
            self.particles.draw(screen)
            self.hearts.draw(screen, self.hearts_global_alpha)
            text = scene["text"]
            lines = text.split("\n")
            f = title_font if scene_type == "final" else theme_font
            ls = 55
            sy = (HEIGHT - len(lines) * ls) // 2
            for i, line in enumerate(lines):
                surf = f.render(line, True, scene_text_color)
                screen.blit(surf, surf.get_rect(center=(WIDTH // 2, sy + i * ls)))

        elif scene_type == "centered_text":
            # Centered text with optional fading characters behind
            self.particles.draw(screen)
            if show_chars and self.char_alpha > 0:
                boy_x, girl_x = self._positions_for_layout(layout)
                # Draw chars to an offscreen surface for alpha control
                char_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                draw_human_standing(char_surf, boy_x, floor_y,
                                   False, breath, False, now,
                                   self.boy_idle, wind, smile=scene_smile)
                draw_human_standing(char_surf, girl_x, floor_y,
                                   True, breath, False, now,
                                   self.girl_idle, wind, smile=scene_smile)
                char_surf.set_alpha(self.char_alpha)
                screen.blit(char_surf, (0, 0))
            # Draw centered text on top
            text = scene["text"]
            lines = text.split("\n")
            ls = 50
            sy = (HEIGHT - len(lines) * ls) // 2
            for i, line in enumerate(lines):
                surf = centered_font.render(line, True, scene_text_color)
                screen.blit(surf, surf.get_rect(center=(WIDTH // 2, sy + i * ls)))
            self.hearts.draw(screen, self.hearts_global_alpha)

        else:
            # Normal scene with characters
            if is_cinematic:
                # Cinematic warm gradient background
                draw_warm_gradient_bg(screen, WIDTH, HEIGHT, now)
                self.bokeh.update(now)
                self.bokeh.draw(screen, now)
            self.particles.draw(screen)
            # Draw hearts BEHIND characters
            self.hearts.draw(screen, self.hearts_global_alpha)
            if show_chars:
                boy_x, girl_x = self._positions_for_layout(layout)
                # Look direction: boy looks right (+1), girl looks left (-1)
                boy_look = 1.0 if look_at else 0.0
                girl_look = -1.0 if look_at else 0.0
                hand_hold = scene.get("holding_hands", False)
                boy_skel, boy_lh, boy_rh = draw_human_standing(
                    screen, boy_x, floor_y,
                    False, breath, False, now,
                    self.boy_idle, wind, smile=scene_smile,
                    look_direction=boy_look,
                    holding_hands=hand_hold)
                girl_skel, girl_lh, girl_rh = draw_human_standing(
                    screen, girl_x, floor_y,
                    True, breath, False, now,
                    self.girl_idle, wind, smile=scene_smile,
                    look_direction=girl_look,
                    holding_hands=hand_hold)
                # Arms already overlap at the meeting point for hand holding
            if is_cinematic:
                draw_vignette(screen, WIDTH, HEIGHT, intensity=100)
            self.subtitle.draw(screen, color=scene_text_color)

        # Fade overlay
        if self.fade_alpha > 0:
            fs = pygame.Surface((WIDTH, HEIGHT))
            if scene.get("fade_to_black") and self.state == "FADE_OUT":
                fs.fill((0, 0, 0))
            else:
                fs.fill(BG_COLOR)
            fs.set_alpha(self.fade_alpha)
            screen.blit(fs, (0, 0))

        pygame.display.flip()
        self.frames.append(pygame.surfarray.array3d(screen).transpose([1, 0, 2]))

    def run_loop(self):
        while self.running:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    self.running = False
            self.update()
            self.draw()
            self.clock.tick(self.fps)
            self.frame_count += 1
            self.virtual_time = self.frame_count * (1000.0 / self.fps)
        self.export_video()
        pygame.quit()
        sys.exit()

    def export_video(self):
        print("Exporting video... please wait.")
        vc = ImageSequenceClip(self.frames, fps=self.fps)
        clips = []
        for ms, fn in self.scene_audio_events:
            ap = os.path.join(AUDIO_DIR, fn)
            if os.path.exists(ap):
                clips.append(AudioFileClip(ap).with_start(ms / 1000.0))
        if clips:
            vc = vc.with_audio(CompositeAudioClip(clips))
        out = os.path.join(BASE_DIR, "output.mp4")
        vc.write_videofile(out, fps=self.fps, codec="libx264", audio_codec="aac")
        print(f"Export complete: {out}")


if __name__ == "__main__":
    print("\n--- Valentine's Day — Cinematic Story Export ---")
    print("NOTE: On-screen playback will lag during frame capture. This is normal.")
    print("The final 'output.mp4' will have perfect synchronization.\n")
    App().run_loop()
