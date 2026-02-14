#!/usr/bin/env python3
"""
Hug Day - Valentine's Week Day 6
Theme: When emotional walls fall, vulnerability becomes trust.
Full cinematic engine — standing-only scenes, skeletal joint hug animation,
particle system, idle animations, cloth/hair sway, subtitle fades, video export.
"""

import pygame
import math
import sys
import os
import random
import numpy as np
from moviepy import ImageSequenceClip, AudioFileClip, CompositeAudioClip

pygame.init()

WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hug Day")

BG_COLOR = (211, 211, 211)
TEXT_COLOR = (45, 45, 45)

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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
AUDIO_DIR = os.path.join(ASSETS_DIR, "audio")

FADE_DURATION = 1500

# ---------------------------------------------------------------------------
# SCENES — All standing, no furniture
# ---------------------------------------------------------------------------

SCENES = [
    {"id": 0, "type": "final",
     "vo": "hug_sc1_title.mp3", "text": "Hug Day", "layout": "standing"},

    {"id": 1, "type": "theme",
     "vo": "hug_sc1_intro.mp3",
     "text": "Growth brought them closer.\nBut closeness asks for trust.",
     "layout": "standing"},

    {"id": 2, "type": "theme",
     "vo": "hug_sc1_theme.mp3",
     "text": "Not every distance is physical.\nSome distances live in hesitation.",
     "layout": "standing"},

    {"id": 3, "type": "scene",
     "vo": "hug_sc2.mp3",
     "text": "They had shared words.\nThey had shared truth.\nBut there was still something unspoken.",
     "layout": "standing", "both": True},

    {"id": 4, "type": "scene",
     "vo": "hug_sc3.mp3",
     "text": "Closeness doesn't arrive suddenly.\nIt arrives when fear begins to fade.",
     "layout": "standing", "both": True},

    {"id": 5, "type": "scene",
     "vo": "hug_sc4.mp3",
     "text": "Neither of them asked.\nNeither of them needed to.",
     "layout": "standing_close", "both": True},

    {"id": 6, "type": "scene",
     "vo": "hug_sc5.mp3",
     "text": "This was not about holding on.\nIt was about letting each other in.",
     "layout": "hugging", "both": True,
     "start_delay": 2000, "hold_extra": 3500},

    {"id": 7, "type": "scene",
     "vo": "hug_sc6.mp3",
     "text": "Some closeness cannot be explained.\nIt can only be felt.",
     "layout": "standing_close", "both": True},

    {"id": 8, "type": "theme",
     "vo": "hug_sc7.mp3",
     "text": "Hug Day isn't about touch.\nIt's about knowing you are no longer alone.",
     "layout": "standing_close"},

    {"id": 9, "type": "final",
     "vo": "hug_sc8_title.mp3", "text": "Hug Day",
     "layout": "standing_close", "hold_extra": 3000},
]

# ---------------------------------------------------------------------------
# PARTICLE SYSTEM
# ---------------------------------------------------------------------------

class Petal:
    def __init__(self):
        self.reset(True)
    def reset(self, initial=False):
        self.x = random.uniform(-40, WIDTH + 40) if initial else WIDTH + random.uniform(10, 60)
        self.y = random.uniform(-20, HEIGHT + 20)
        self.size = random.uniform(3, 7)
        self.speed_x = -random.uniform(0.15, 0.55)
        self.speed_y = random.uniform(-0.08, 0.12)
        self.angle = random.uniform(0, 360)
        self.spin = random.uniform(-0.3, 0.3)
        self.alpha_max = random.randint(50, 110)
        self.alpha = 0 if not initial else random.randint(20, self.alpha_max)
        self.life = random.uniform(400, 1200)
        self.age = 0 if not initial else random.uniform(0, self.life * 0.6)
        self.color = random.choice([
            (255, 210, 220), (255, 200, 210), (245, 225, 230),
            (255, 230, 235), (240, 215, 225)])
    def update(self, wind_offset=0):
        self.x += self.speed_x + wind_offset * 0.02
        self.y += self.speed_y + math.sin(self.age * 0.008) * 0.15
        self.angle += self.spin
        self.age += 1
        fz = self.life * 0.2
        if self.age < fz:
            self.alpha = int(self.alpha_max * (self.age / fz))
        elif self.age > self.life - fz:
            self.alpha = int(self.alpha_max * ((self.life - self.age) / fz))
        else:
            self.alpha = self.alpha_max
        if self.x < -60 or self.age >= self.life:
            self.reset(False)
    def draw(self, surface):
        if self.alpha <= 0:
            return
        s = int(self.size)
        ps = pygame.Surface((s * 3, s * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(ps, (*self.color, self.alpha), (0, 0, s * 3, s * 2))
        rotated = pygame.transform.rotate(ps, self.angle)
        surface.blit(rotated, rotated.get_rect(center=(int(self.x), int(self.y))))

class ParticleSystem:
    def __init__(self, count=40):
        self.petals = [Petal() for _ in range(count)]
        self.wind_phase = 0
    def update(self):
        self.wind_phase += 0.005
        w = math.sin(self.wind_phase) * 0.5
        for p in self.petals:
            p.update(w)
    def draw(self, surface):
        for p in self.petals:
            p.draw(surface)
    def get_wind(self):
        return math.sin(self.wind_phase) * 0.5

# ---------------------------------------------------------------------------
# IDLE SYSTEM
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
    """Compute all joint positions for a character. Returns a dict of joints."""
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
        'torso_center': (base_x, shoulder_y + TORSO_H * 0.5),
    }


def draw_body(surface, skel, is_woman, talking, virtual_time, idle, lean_x=0, lean_y=0, smile=0.0):
    """Draw legs, torso, head, face, hair/bow — everything except arms."""
    scale = skel['scale']
    base_x, base_y = skel['base_x'], skel['base_y']
    hips_y, shoulder_y = skel['hips_y'], skel['shoulder_y']
    HEAD_R = skel['HEAD_R']
    SHOULDER_W = skel['SHOULDER_W']
    TORSO_H = skel['TORSO_H']
    HIP_W = skel['HIP_W']
    cloth_sway = skel['cloth_sway']
    head_cx = skel['head_cx'] + lean_x
    head_cy = skel['head_cy'] + lean_y

    # Outfit colors
    if is_woman:
        clothing_color = (128, 0, 128)
        clothing_accent = (100, 0, 105)
        leg_color = (240, 200, 180)
    else:
        shirt_color = (120, 80, 55)
        shirt_outline = (100, 65, 40)
        pants_color = (50, 48, 55)

    # Shadow
    shadow_w = 110 * scale
    pygame.draw.ellipse(surface, (190, 190, 190),
                        (base_x - shadow_w / 2, base_y - 10, shadow_w, 20))

    # Legs
    if not is_woman:
        for side in [-1, 1]:
            lx = base_x + side * (HIP_W / 4)
            draw_capsule(surface, pants_color, (lx, hips_y), (lx, base_y), int(8 * scale))
            pygame.draw.circle(surface, (255, 255, 255), (int(lx), int(base_y)), int(10 * scale))
    else:
        for side in [-1, 1]:
            lx = base_x + side * (HIP_W / 4)
            draw_capsule(surface, leg_color,
                         (base_x + side * (HIP_W / 4), hips_y + 30 * scale),
                         (lx, base_y), int(7 * scale))
            pygame.draw.circle(surface, (255, 255, 255), (int(lx), int(base_y)), int(9 * scale))

    # Torso
    sway_r = cloth_sway * 0.5
    if is_woman:
        pts = [
            (base_x - SHOULDER_W / 2 - sway_r * 0.3, shoulder_y),
            (base_x + SHOULDER_W / 2 + sway_r * 0.3, shoulder_y),
            (base_x + HIP_W / 2 + 20 * scale + sway_r, hips_y + 30 * scale),
            (base_x - HIP_W / 2 - 20 * scale - sway_r * 0.2, hips_y + 30 * scale)]
        pygame.draw.polygon(surface, clothing_color, pts)
        for i in range(1, 4):
            ly = shoulder_y + i * 25 * scale
            pygame.draw.line(surface, clothing_accent,
                             (base_x - SHOULDER_W / 2 + i * 2, ly),
                             (base_x + SHOULDER_W / 2 - i * 2, ly), 1)
        pygame.draw.polygon(surface, clothing_accent, pts, 2)
    else:
        pts = [
            (base_x - SHOULDER_W / 2 - sway_r * 0.2, shoulder_y),
            (base_x + SHOULDER_W / 2 + sway_r * 0.2, shoulder_y),
            (base_x + HIP_W / 2 + sway_r * 0.3, hips_y),
            (base_x - HIP_W / 2 - sway_r * 0.1, hips_y)]
        pygame.draw.polygon(surface, shirt_color, pts)
        pygame.draw.polygon(surface, shirt_outline, pts, 2)

    # Head
    pygame.draw.circle(surface, (255, 255, 255), (int(head_cx), int(head_cy)), int(HEAD_R))
    pygame.draw.circle(surface, (240, 240, 240), (int(head_cx), int(head_cy)), int(HEAD_R), 2)

    # Blush (soft pink, gradual with smile)
    if smile > 0.1:
        blush_alpha = min(70, int(70 * ((smile - 0.1) / 0.9)))
        blush_r = int(8 * scale)
        for sx in [-1, 1]:
            bx = int(head_cx + sx * 14 * scale)
            by = int(head_cy + HEAD_R * 0.15)
            bs = pygame.Surface((blush_r * 2, blush_r * 2), pygame.SRCALPHA)
            pygame.draw.ellipse(bs, (255, 160, 160, blush_alpha), (0, 0, blush_r * 2, blush_r * 2))
            surface.blit(bs, (bx - blush_r, by - blush_r))

    # Eyes — normal size, natural blinking continues
    eye_x_off = 10 * scale
    eye_y_off = -HEAD_R / 5
    is_blinking = idle.is_blinking if idle else False
    for sx in [-1, 1]:
        ex = int(head_cx + sx * eye_x_off)
        ey = int(head_cy + eye_y_off)
        if is_blinking:
            pygame.draw.line(surface, (40, 40, 40), (ex - 3, ey), (ex + 3, ey), 2)
        else:
            pygame.draw.circle(surface, (40, 40, 40), (ex, ey), 3)

    # Mouth — gentle smile curve when smile > 0
    m_y = head_cy + HEAD_R / 2
    if talking:
        talk_h = 4 + math.sin(virtual_time * 0.02) * 4
        pygame.draw.ellipse(surface, (40, 40, 40),
                            (head_cx - 4, m_y - talk_h / 2, 8, max(2, talk_h)))
    elif smile > 0.05:
        # Gentle upward curve — corners lift naturally
        mouth_w = 5 + smile * 2
        curve_h = smile * 3  # subtle lift at corners
        pts = []
        for i in range(9):
            t = i / 8.0
            mx = head_cx - mouth_w + t * mouth_w * 2
            # parabola: highest at edges, lowest at center
            my = m_y - curve_h * (2 * t - 1) ** 2 + curve_h
            pts.append((mx, my))
        pygame.draw.lines(surface, (40, 40, 40), False, pts, 2)
    else:
        pygame.draw.line(surface, (40, 40, 40), (head_cx - 4, m_y), (head_cx + 4, m_y), 2)

    # Hair/Bow (Girl)
    if is_woman:
        hair_sway = cloth_sway * 0.6
        bow_x = head_cx + 22 * scale + hair_sway * 0.4
        bow_y = head_cy - 25 * scale
        bow_color = (200, 170, 70)
        bow_accent = (170, 140, 50)
        pygame.draw.ellipse(surface, bow_color, (bow_x - 12, bow_y - 6, 10, 12))
        pygame.draw.ellipse(surface, bow_color, (bow_x + 2, bow_y - 6, 10, 12))
        pygame.draw.circle(surface, bow_accent, (int(bow_x), int(bow_y)), 4)


def draw_arm_segment(surface, shoulder, elbow, hand, radius):
    """Draw a two-segment arm: shoulder→elbow→hand."""
    skin = (255, 255, 255)
    draw_capsule(surface, skin, shoulder, elbow, radius)
    draw_capsule(surface, skin, elbow, hand, radius)


def draw_human_standing(surface, x, y, is_woman, breathing, talking,
                        virtual_time, idle, wind):
    """Draw a standing character with normal resting arms."""
    skel = _compute_skeleton(x, y, is_woman, breathing, idle, wind, virtual_time)
    scale = skel['scale']
    draw_body(surface, skel, is_woman, talking, virtual_time, idle)
    # Resting arms
    arm_r = int(7 * scale)
    cs = skel['cloth_sway']
    nl = (skel['base_x'] - skel['SHOULDER_W'] / 2 - 5 + cs * 0.3, skel['shoulder_y'] + 95 * scale)
    nr = (skel['base_x'] + skel['SHOULDER_W'] / 2 + 5 + cs * 0.2, skel['shoulder_y'] + 95 * scale)
    draw_capsule(surface, (255, 255, 255), skel['l_shoulder'], nl, arm_r)
    draw_capsule(surface, (255, 255, 255), skel['r_shoulder'], nr, arm_r)


def draw_embrace_pair(surface, boy_x, girl_x, floor_y, progress,
                      breathing, virtual_time, boy_idle, girl_idle, wind):
    """
    Draw both characters in a full-body embrace with proper layering.
    progress: 0.0 (standing apart) → 1.0 (full embrace).

    Layering order:
      1. Boy back-arm (wraps behind girl — hidden by her body)
      2. Girl back-arm (wraps behind boy — hidden by his body)
      3. Boy body (legs, torso, head)
      4. Girl body (legs, torso, head)
      5. Boy front-arm (visible on top of girl)
      6. Girl front-arm (visible on top of boy)
    """
    p = _ease_out(min(1.0, progress))
    wrap = min(1.0, progress / 0.7)  # arms fully wrapped by 70% of approach

    # Lean-in during last 30%
    lean_amt = max(0, (p - 0.7) / 0.3) if p > 0.7 else 0.0

    boy_skel = _compute_skeleton(boy_x, floor_y, False, breathing, boy_idle, wind, virtual_time)
    girl_skel = _compute_skeleton(girl_x, floor_y, True, breathing, girl_idle, wind, virtual_time)

    bs = boy_skel['scale']
    gs = girl_skel['scale']
    arm_r_boy = int(7 * bs)
    arm_r_girl = int(7 * gs)

    # --- Compute arm joint targets ---
    # Boy: arms reach rightward past girl's center to her far side
    boy_torso_mid_y = boy_skel['shoulder_y'] + boy_skel['TORSO_H'] * 0.45

    # Normal resting arms
    cs_b = boy_skel['cloth_sway']
    boy_nl = (boy_skel['base_x'] - boy_skel['SHOULDER_W'] / 2 - 5 + cs_b * 0.3,
              boy_skel['shoulder_y'] + 95 * bs)
    boy_nr = (boy_skel['base_x'] + boy_skel['SHOULDER_W'] / 2 + 5 + cs_b * 0.2,
              boy_skel['shoulder_y'] + 95 * bs)

    # Wrapping targets — hands reach PAST girl's center x
    # Left arm wraps around girl's upper back
    boy_wl_elbow = (boy_x + 25 * bs, boy_torso_mid_y - 5 * bs)
    boy_wl_hand = (girl_x + 18 * gs, boy_torso_mid_y + 5 * bs)  # past girl center

    # Right arm wraps around girl's mid-back
    boy_wr_elbow = (boy_x + 22 * bs, boy_torso_mid_y + 25 * bs)
    boy_wr_hand = (girl_x + 15 * gs, boy_torso_mid_y + 30 * bs)  # past girl center

    # Girl: arms reach leftward past boy's center
    girl_torso_mid_y = girl_skel['shoulder_y'] + girl_skel['TORSO_H'] * 0.45

    cs_g = girl_skel['cloth_sway']
    girl_nl = (girl_skel['base_x'] - girl_skel['SHOULDER_W'] / 2 + cs_g * 0.3,
               girl_skel['shoulder_y'] + 95 * gs)
    girl_nr = (girl_skel['base_x'] + girl_skel['SHOULDER_W'] / 2 + cs_g * 0.2,
               girl_skel['shoulder_y'] + 95 * gs)

    # Left arm wraps around boy's mid-back
    girl_wl_elbow = (girl_x - 22 * gs, girl_torso_mid_y + 20 * gs)
    girl_wl_hand = (boy_x - 15 * bs, girl_torso_mid_y + 28 * gs)  # past boy center

    # Right arm wraps around boy's upper back
    girl_wr_elbow = (girl_x - 20 * gs, girl_torso_mid_y - 5 * gs)
    girl_wr_hand = (boy_x - 12 * bs, girl_torso_mid_y + 8 * gs)  # past boy center

    # Interpolate from resting to wrapping
    boy_nl_mid = _lerp(boy_skel['l_shoulder'], boy_nl, 0.5)
    boy_nr_mid = _lerp(boy_skel['r_shoulder'], boy_nr, 0.5)

    boy_l_elbow = _lerp(boy_nl_mid, boy_wl_elbow, wrap)
    boy_l_hand = _lerp(boy_nl, boy_wl_hand, wrap)
    boy_r_elbow = _lerp(boy_nr_mid, boy_wr_elbow, wrap)
    boy_r_hand = _lerp(boy_nr, boy_wr_hand, wrap)

    girl_nl_mid = _lerp(girl_skel['l_shoulder'], girl_nl, 0.5)
    girl_nr_mid = _lerp(girl_skel['r_shoulder'], girl_nr, 0.5)

    girl_l_elbow = _lerp(girl_nl_mid, girl_wl_elbow, wrap)
    girl_l_hand = _lerp(girl_nl, girl_wl_hand, wrap)
    girl_r_elbow = _lerp(girl_nr_mid, girl_wr_elbow, wrap)
    girl_r_hand = _lerp(girl_nr, girl_wr_hand, wrap)

    # --- LAYERED DRAWING ---
    # Layer 1: Boy's RIGHT arm (wraps behind girl — will be covered by girl body)
    draw_arm_segment(surface, boy_skel['r_shoulder'], boy_r_elbow, boy_r_hand, arm_r_boy)

    # Layer 2: Girl's LEFT arm (wraps behind boy — will be covered by boy body)
    draw_arm_segment(surface, girl_skel['l_shoulder'], girl_l_elbow, girl_l_hand, arm_r_girl)

    # Layer 3: Boy body (with smile)
    draw_body(surface, boy_skel, False, False, virtual_time, boy_idle,
              lean_x=lean_amt * 4, lean_y=lean_amt * 2, smile=wrap)

    # Layer 4: Girl body (with smile)
    draw_body(surface, girl_skel, True, False, virtual_time, girl_idle,
              lean_x=-lean_amt * 3, lean_y=lean_amt * 2, smile=wrap)

    # Layer 5: Boy's LEFT arm (visible in front of girl)
    draw_arm_segment(surface, boy_skel['l_shoulder'], boy_l_elbow, boy_l_hand, arm_r_boy)

    # Layer 6: Girl's RIGHT arm (visible in front of boy)
    draw_arm_segment(surface, girl_skel['r_shoulder'], girl_r_elbow, girl_r_hand, arm_r_girl)


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
    def draw(self, surface):
        if not self.text or self.alpha <= 0:
            return
        lines = self.text.split("\n")
        start_y = HEIGHT - 40 - len(lines) * 40
        for i, line in enumerate(lines):
            rendered = subtitle_font.render(line, True, TEXT_COLOR)
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
            print(f"Error playing {path}: {e}")
            return 0
    def is_playing(self):
        return self.vo_channel.get_busy()
    def stop(self):
        self.vo_channel.stop()

# ---------------------------------------------------------------------------
# APPLICATION
# ---------------------------------------------------------------------------

class App:
    def __init__(self):
        self.audio = AudioController()
        self.particles = ParticleSystem(40)
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

        # Positions
        self.boy_x_standing = WIDTH * 0.42
        self.girl_x_standing = WIDTH * 0.58
        self.boy_x_close = WIDTH * 0.45
        self.girl_x_close = WIDTH * 0.55
        # Hug final: near-overlap for real embrace
        self.boy_x_hug = WIDTH * 0.485
        self.girl_x_hug = WIDTH * 0.515

    def _positions_for_layout(self, layout):
        if layout == "standing_close":
            return self.boy_x_close, self.girl_x_close
        elif layout == "hugging":
            return self.boy_x_hug, self.girl_x_hug
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
        self.particles.update()
        self.subtitle.update(now)
        self.boy_idle.update()
        self.girl_idle.update()

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
            is_finished = False
            post_delay = 1500
            if scene.get("hold_extra"):
                post_delay = scene["hold_extra"]
            elapsed_m = now - self.main_vo_start_time
            if not (elapsed_m < self.current_audio_duration) and elapsed_m > 1000:
                if self.audio_finished_time == 0:
                    self.audio_finished_time = now
                if now - self.audio_finished_time > post_delay:
                    is_finished = True
            if is_finished:
                self.state = "FADE_OUT"
                self.transition_start_time = now
                self.subtitle.begin_fade_out(now)
        elif self.state == "FADE_OUT":
            elapsed = now - self.transition_start_time
            self.fade_alpha = min(255, int(255 * (elapsed / FADE_DURATION)))
            if elapsed > FADE_DURATION:
                self.next_scene()

    def draw(self):
        if self.current_scene_idx < 0 or self.current_scene_idx >= len(SCENES):
            return
        screen.fill(BG_COLOR)
        scene = SCENES[self.current_scene_idx]
        now = self.virtual_time
        breath = math.sin(now * 0.002) * 3
        elapsed_main = now - self.main_vo_start_time
        is_vo = (not self.delay_phase) and elapsed_main < self.current_audio_duration
        boy_talks = is_vo and scene.get("talking") == "boy"
        girl_talks = is_vo and scene.get("talking") == "girl"

        layout = scene.get("layout", "standing")
        is_hugging = (layout == "hugging")
        wind = self.particles.get_wind()
        floor_y = int(HEIGHT * 0.72)
        show_chars = scene.get("both") or scene.get("boy") or scene.get("girl")

        if scene.get("type") in ["theme", "final"] and not show_chars:
            text = scene["text"]
            lines = text.split("\n")
            f = title_font if scene["type"] == "final" else theme_font
            ls = 55
            sy = (HEIGHT - len(lines) * ls) // 2
            for i, line in enumerate(lines):
                surf = f.render(line, True, TEXT_COLOR)
                screen.blit(surf, surf.get_rect(center=(WIDTH // 2, sy + i * ls)))
            self.particles.draw(screen)
        else:
            self.particles.draw(screen)
            if show_chars:
                if is_hugging:
                    elapsed = now - self.scene_start_time
                    approach_dur = scene.get("start_delay", 2000)
                    progress = min(1.0, elapsed / approach_dur) if approach_dur > 0 else 1.0
                    # Interpolate positions from standing to hug
                    boy_x = self.boy_x_close + (self.boy_x_hug - self.boy_x_close) * _ease_out(progress)
                    girl_x = self.girl_x_close + (self.girl_x_hug - self.girl_x_close) * _ease_out(progress)
                    draw_embrace_pair(screen, boy_x, girl_x, floor_y, progress,
                                     breath, now, self.boy_idle, self.girl_idle, wind)
                else:
                    boy_x, girl_x = self._positions_for_layout(layout)
                    draw_human_standing(screen, boy_x, floor_y,
                                       False, breath, boy_talks, now,
                                       self.boy_idle, wind)
                    draw_human_standing(screen, girl_x, floor_y,
                                       True, breath, girl_talks, now,
                                       self.girl_idle, wind)
            self.subtitle.draw(screen)

        if self.fade_alpha > 0:
            fs = pygame.Surface((WIDTH, HEIGHT))
            fs.fill(BG_COLOR)
            fs.set_alpha(self.fade_alpha)
            screen.blit(fs, (0, 0))

        pygame.display.flip()
        fd = pygame.surfarray.array3d(screen).transpose([1, 0, 2])
        self.frames.append(fd)

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
                ac = AudioFileClip(ap).with_start(ms / 1000.0)
                clips.append(ac)
        if clips:
            vc = vc.with_audio(CompositeAudioClip(clips))
        out = os.path.join(BASE_DIR, "output.mp4")
        vc.write_videofile(out, fps=self.fps, codec="libx264", audio_codec="aac")
        print(f"Export complete: {out}")


if __name__ == "__main__":
    print("\n--- Hug Day — Cinematic Story Export ---")
    print("NOTE: On-screen playback will lag during frame capture. This is normal.")
    print("The final 'output.mp4' will have perfect synchronization.\n")
    App().run_loop()
