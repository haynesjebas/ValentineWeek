#!/usr/bin/env python3
"""
Promise Day - Valentine's Week Day 5
Theme: Growing together — not staying the same, not promising forever.
Full cinematic engine with particle system, idle animations, sitting scenes,
cloth/hair sway, subtitle fades, pre_vo narrator chaining, and video export.
"""

import pygame
import math
import sys
import os
import random
import numpy as np
from moviepy import ImageSequenceClip, AudioFileClip, CompositeAudioClip

pygame.init()

# Display
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Promise Day")

# Colors
BG_COLOR = (211, 211, 211)
TEXT_COLOR = (45, 45, 45)

# Typography
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

# --- PATHS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
AUDIO_DIR = os.path.join(ASSETS_DIR, "audio")

FADE_DURATION = 1500

# ---------------------------------------------------------------------------
# SCENE CONFIGURATION
# ---------------------------------------------------------------------------
# layout: "standing" | "sitting" | "standing_close"
# talking: "boy" | "girl" | None (narrator)
# pre_vo: narrator framing audio that plays BEFORE main vo (no subtitle shown)
# type "theme": centered text, no characters
# type "final": centered title text, no characters
# type "scene": characters + subtitle at bottom

SCENES = [
    # --- Scene 0: Title ---
    {
        "id": 0, "type": "final",
        "vo": "promise_sc1_title.mp3",
        "text": "Promise Day",
        "layout": "standing",
    },
    # --- Scene 1: Theme intro (centered, no chars) ---
    {
        "id": 1, "type": "theme",
        "vo": "promise_sc1_intro.mp3",
        "text": "Care brought them close.\nNow they had to decide who they would become to each other.",
        "layout": "standing",
    },
    # --- Scene 2a: Theme extended part 1 (centered, no chars) ---
    {
        "id": 2, "type": "theme",
        "vo": "promise_sc1_theme_a.mp3",
        "text": "Care had brought them this far.\nBut care alone cannot shape what comes next.",
        "layout": "standing",
    },
    # --- Scene 2b: Theme extended part 2 (centered, no chars) ---
    {
        "id": 3, "type": "theme",
        "vo": "promise_sc1_theme_b.mp3",
        "text": "Growth asks a quieter question.\nWhat kind of people will they become to each other?",
        "layout": "standing",
    },
    # --- Scene 3a: Sitting - beat 1 ---
    {
        "id": 3, "type": "scene",
        "vo": "promise_sc2a.mp3",
        "text": "They were afraid of losing each other.",
        "layout": "sitting", "both": True,
    },
    # --- Scene 3b: Sitting - beat 2 ---
    {
        "id": 4, "type": "scene",
        "vo": "promise_sc2b.mp3",
        "text": "They were afraid of becoming strangers\nas they changed.",
        "layout": "sitting", "both": True,
    },
    # --- Scene 4: Girl dialogue (narrator framing chained) ---
    {
        "id": 5, "type": "scene",
        "pre_vo": "promise_sc3_nar.mp3",
        "vo": "promise_sc3_girl.mp3",
        "text": "Promise me something.\nPromise me we won't stop being honest,\neven when we grow.",
        "layout": "sitting", "both": True,
        "talking": "girl",
    },
    # --- Scene 5: Boy dialogue (narrator framing chained) ---
    {
        "id": 6, "type": "scene",
        "pre_vo": "promise_sc4_nar.mp3",
        "vo": "promise_sc4_boy.mp3",
        "text": "Then promise me something too.\nPromise me we'll learn each version of each other.\nEven the ones we haven't met yet.",
        "layout": "sitting", "both": True,
        "talking": "boy",
    },
    # --- Scene 6: Standing transition - both visible ---
    {
        "id": 7, "type": "scene",
        "vo": "promise_sc5.mp3",
        "text": "This was not a promise to remain the same.\nIt was a promise to grow without growing apart.",
        "layout": "standing_close", "both": True,
    },
    # --- Scene 7: Final meaning - no characters ---
    {
        "id": 8, "type": "theme",
        "vo": "promise_sc6.mp3",
        "text": "Promise Day isn't about staying unchanged.\nIt's about choosing to grow side by side.",
        "layout": "standing_close",
    },
    # --- Scene 8: Ending ---
    {
        "id": 9, "type": "final",
        "vo": "promise_sc7_title.mp3",
        "text": "Promise Day",
        "layout": "standing_close",
        "hold_extra": 3000,
    },
]

# ---------------------------------------------------------------------------
# PARTICLE SYSTEM — Soft blossom petals
# ---------------------------------------------------------------------------

class Petal:
    """A single drifting blossom petal."""
    def __init__(self):
        self.reset(initial=True)

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
        self.fade_in = True
        self.life = random.uniform(400, 1200)
        self.age = 0 if not initial else random.uniform(0, self.life * 0.6)
        c = random.choice([
            (255, 210, 220),
            (255, 200, 210),
            (245, 225, 230),
            (255, 230, 235),
            (240, 215, 225),
        ])
        self.color = c

    def update(self, wind_offset=0):
        self.x += self.speed_x + wind_offset * 0.02
        self.y += self.speed_y + math.sin(self.age * 0.008) * 0.15
        self.angle += self.spin
        self.age += 1
        fade_zone = self.life * 0.2
        if self.age < fade_zone:
            self.alpha = int(self.alpha_max * (self.age / fade_zone))
        elif self.age > self.life - fade_zone:
            self.alpha = int(self.alpha_max * ((self.life - self.age) / fade_zone))
        else:
            self.alpha = self.alpha_max
        if self.x < -60 or self.age >= self.life:
            self.reset(initial=False)

    def draw(self, surface):
        if self.alpha <= 0:
            return
        s = int(self.size)
        petal_surf = pygame.Surface((s * 3, s * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(petal_surf, (*self.color, self.alpha), (0, 0, s * 3, s * 2))
        rotated = pygame.transform.rotate(petal_surf, self.angle)
        rect = rotated.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(rotated, rect)


class ParticleSystem:
    """Manages collection of drifting petals."""
    def __init__(self, count=35):
        self.petals = [Petal() for _ in range(count)]
        self.wind_phase = 0

    def update(self):
        self.wind_phase += 0.005
        wind = math.sin(self.wind_phase) * 0.5
        for p in self.petals:
            p.update(wind)

    def draw(self, surface):
        for p in self.petals:
            p.draw(surface)

    def get_wind(self):
        return math.sin(self.wind_phase) * 0.5


# ---------------------------------------------------------------------------
# CHARACTER IDLE SYSTEM
# ---------------------------------------------------------------------------

class IdleState:
    """Tracks blinking, head micro-adjustments for one character."""
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


def draw_table_and_chairs(surface, cx, floor_y):
    """Draw a simple cafe-style table with two chairs."""
    table_w, table_h = 180, 12
    table_top_y = floor_y - 120
    leg_h = 90

    leg_color = (120, 90, 65)
    for lx in [cx - table_w // 2 + 15, cx + table_w // 2 - 15]:
        pygame.draw.line(surface, leg_color, (lx, table_top_y + table_h),
                         (lx, table_top_y + table_h + leg_h), 4)

    table_color = (160, 120, 85)
    pygame.draw.rect(surface, table_color,
                     (cx - table_w // 2, table_top_y, table_w, table_h),
                     border_radius=4)
    pygame.draw.rect(surface, (180, 145, 110),
                     (cx - table_w // 2 + 5, table_top_y + 2, table_w - 10, 4),
                     border_radius=2)

    chair_color = (130, 100, 75)
    for side in [-1, 1]:
        chair_cx = cx + side * 130
        seat_y = floor_y - 85
        seat_w, seat_h = 50, 8
        pygame.draw.rect(surface, chair_color,
                         (chair_cx - seat_w // 2, seat_y, seat_w, seat_h),
                         border_radius=3)
        back_h = 55
        pygame.draw.rect(surface, chair_color,
                         (chair_cx - seat_w // 2, seat_y - back_h, 6, back_h),
                         border_radius=2)
        pygame.draw.rect(surface, chair_color,
                         (chair_cx + seat_w // 2 - 6, seat_y - back_h, 6, back_h),
                         border_radius=2)
        pygame.draw.rect(surface, chair_color,
                         (chair_cx - seat_w // 2, seat_y - back_h, seat_w, 6),
                         border_radius=2)
        for ll in [-1, 1]:
            lx = chair_cx + ll * (seat_w // 2 - 6)
            pygame.draw.line(surface, chair_color,
                             (lx, seat_y + seat_h), (lx, floor_y), 3)


def draw_human(surface, x, y, is_woman=False, breathing=0,
               talking=False, virtual_time=0, idle=None, wind=0.0,
               sitting=False):
    """
    Draw a human character with idle animations, cloth/hair sway.
    Same proportions and facial style as TeddyDay.
    """
    scale = 0.78 if is_woman else 0.95

    # Promise Day Outfits — rani pink for girl, navy for boy
    if is_woman:
        clothing_color = (222, 49, 99)     # Rani pink dress
        clothing_accent = (190, 40, 85)    # Darker rani pink accent
        bow_color = (230, 100, 80)         # Warm coral bow
        bow_accent = (200, 75, 60)         # Deeper coral accent
        leg_color = (240, 200, 180)        # Skin-tone for girl legs
    else:
        shirt_color = (70, 85, 130)        # Deep navy blue
        shirt_outline = (55, 70, 110)
        pants_color = (55, 55, 65)         # Dark charcoal

    HEAD_R = 30 * scale
    SHOULDER_W = (52 if is_woman else 68) * scale
    TORSO_H = (110 + breathing) * scale
    HIP_W = (56 if is_woman else 48) * scale
    LEG_L = 120 * scale

    if sitting:
        LEG_L = 50 * scale
        y = y + 18

    base_x = x
    base_y = y - breathing * (0.3 if is_woman else 0.4)

    head_ox = idle.head_offset_x if idle else 0
    head_oy = idle.head_offset_y if idle else 0

    cloth_sway = wind * 2.5 + math.sin(virtual_time * 0.0015) * 1.2

    shadow_w = 110 * scale
    if not sitting:
        pygame.draw.ellipse(surface, (190, 190, 190),
                            (base_x - shadow_w / 2, y - 10, shadow_w, 20))

    hips_y = base_y - LEG_L
    shoulder_y = hips_y - TORSO_H
    head_center_y = shoulder_y - 10 * scale - HEAD_R
    head_cx = base_x + head_ox
    head_cy = head_center_y + head_oy

    # --- Legs ---
    if not is_woman:
        if sitting:
            for side in [-1, 1]:
                lx = base_x + side * (HIP_W / 4)
                knee_x = lx + side * 5
                knee_y = hips_y + 30 * scale
                foot_x = lx + side * 10
                foot_y = base_y
                draw_capsule(surface, pants_color, (lx, hips_y), (knee_x, knee_y), int(8 * scale))
                draw_capsule(surface, pants_color, (knee_x, knee_y), (foot_x, foot_y), int(8 * scale))
                pygame.draw.circle(surface, (255, 255, 255), (int(foot_x), int(foot_y)), int(10 * scale))
        else:
            for side in [-1, 1]:
                lx = base_x + side * (HIP_W / 4)
                draw_capsule(surface, pants_color, (lx, hips_y), (lx, base_y), int(8 * scale))
                pygame.draw.circle(surface, (255, 255, 255), (int(lx), int(base_y)), int(10 * scale))
    else:
        # Girl legs — visible in ALL scenes (sitting and standing)
        if sitting:
            for side in [-1, 1]:
                lx = base_x + side * (HIP_W / 4)
                knee_x = lx + side * 5
                knee_y = hips_y + 30 * scale
                foot_x = lx + side * 10
                foot_y = base_y
                draw_capsule(surface, leg_color, (lx, hips_y + 30 * scale), (knee_x, knee_y + 15 * scale), int(7 * scale))
                draw_capsule(surface, leg_color, (knee_x, knee_y + 15 * scale), (foot_x, foot_y), int(7 * scale))
                pygame.draw.circle(surface, (255, 255, 255), (int(foot_x), int(foot_y)), int(9 * scale))
        else:
            for side in [-1, 1]:
                lx = base_x + side * (HIP_W / 4)
                draw_capsule(surface, leg_color,
                             (base_x + side * (HIP_W / 4), hips_y + 30 * scale),
                             (lx, base_y), int(7 * scale))
                pygame.draw.circle(surface, (255, 255, 255), (int(lx), int(base_y)), int(9 * scale))

    # --- Torso ---
    sway_r = cloth_sway * 0.5
    if is_woman:
        dress_pts = [
            (base_x - SHOULDER_W / 2 - sway_r * 0.3, shoulder_y),
            (base_x + SHOULDER_W / 2 + sway_r * 0.3, shoulder_y),
            (base_x + HIP_W / 2 + 20 * scale + sway_r, hips_y + 30 * scale),
            (base_x - HIP_W / 2 - 20 * scale - sway_r * 0.2, hips_y + 30 * scale),
        ]
        pygame.draw.polygon(surface, clothing_color, dress_pts)
        for i in range(1, 4):
            ly = shoulder_y + i * 25 * scale
            pygame.draw.line(surface, clothing_accent,
                             (base_x - SHOULDER_W / 2 + i * 2, ly),
                             (base_x + SHOULDER_W / 2 - i * 2, ly), 1)
        pygame.draw.polygon(surface, clothing_accent, dress_pts, 2)
    else:
        shirt_pts = [
            (base_x - SHOULDER_W / 2 - sway_r * 0.2, shoulder_y),
            (base_x + SHOULDER_W / 2 + sway_r * 0.2, shoulder_y),
            (base_x + HIP_W / 2 + sway_r * 0.3, hips_y),
            (base_x - HIP_W / 2 - sway_r * 0.1, hips_y),
        ]
        pygame.draw.polygon(surface, shirt_color, shirt_pts)
        pygame.draw.polygon(surface, shirt_outline, shirt_pts, 2)

    # --- Arms ---
    arm_radius = int(7 * scale)
    skin = (255, 255, 255)
    l_shoulder = (base_x - SHOULDER_W / 2 - (5 if not is_woman else 0), shoulder_y + 10)
    if sitting:
        l_hand = (base_x - SHOULDER_W / 2 + 10, shoulder_y + 70 * scale)
    else:
        l_hand = (base_x - SHOULDER_W / 2 - 5 + cloth_sway * 0.3, shoulder_y + 95 * scale)
    draw_capsule(surface, skin, l_shoulder, l_hand, arm_radius)

    r_shoulder = (base_x + SHOULDER_W / 2, shoulder_y + 10)
    if sitting:
        r_hand = (base_x + SHOULDER_W / 2 - 10, shoulder_y + 70 * scale)
    else:
        r_hand = (base_x + SHOULDER_W / 2 + 5 + cloth_sway * 0.2, shoulder_y + 95 * scale)
    draw_capsule(surface, skin, r_shoulder, r_hand, arm_radius)

    # --- Head ---
    pygame.draw.circle(surface, (255, 255, 255),
                       (int(head_cx), int(head_cy)), int(HEAD_R))
    pygame.draw.circle(surface, (240, 240, 240),
                       (int(head_cx), int(head_cy)), int(HEAD_R), 2)

    # --- Face ---
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

    # Mouth
    m_y = head_cy + HEAD_R / 2
    if talking:
        talk_h = 4 + math.sin(virtual_time * 0.02) * 4
        pygame.draw.ellipse(surface, (40, 40, 40),
                            (head_cx - 4, m_y - talk_h / 2, 8, max(2, talk_h)))
    else:
        pygame.draw.line(surface, (40, 40, 40),
                         (head_cx - 4, m_y), (head_cx + 4, m_y), 2)

    # --- Hair / Bow (Girl) ---
    if is_woman:
        hair_sway = cloth_sway * 0.6
        bow_x = head_cx + 22 * scale + hair_sway * 0.4
        bow_y = head_cy - 25 * scale
        pygame.draw.ellipse(surface, bow_color,
                            (bow_x - 12, bow_y - 6, 10, 12))
        pygame.draw.ellipse(surface, bow_color,
                            (bow_x + 2, bow_y - 6, 10, 12))
        pygame.draw.circle(surface, bow_accent,
                           (int(bow_x), int(bow_y)), 4)


# ---------------------------------------------------------------------------
# SUBTITLE RENDERER WITH FADE
# ---------------------------------------------------------------------------

class SubtitleRenderer:
    """Renders subtitles with fade-in/fade-out at bottom center."""
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
            fade_elapsed = now - self.end_time
            if fade_elapsed < self.FADE_OUT_MS:
                self.alpha = int(255 * (1 - fade_elapsed / self.FADE_OUT_MS))
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
            print(f"ERROR: Audio file not found: {path}")
            return 0
        try:
            sound = pygame.mixer.Sound(path)
            self.vo_channel.play(sound)
            return int(sound.get_length() * 1000)
        except Exception as e:
            print(f"Error playing sound {path}: {e}")
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

        # Pre-vo chaining state
        self.in_pre_vo = False
        self.pre_vo_duration = 0
        self.main_vo_start_time = 0

        # Video capture
        self.frames = []
        self.frame_count = 0
        self.virtual_time = 0.0
        self.fps = 60

        # Audio sync for export
        self.scene_audio_events = []
        self.current_audio_duration = 0

        # Character positions
        self.boy_x_standing = WIDTH * 0.42
        self.girl_x_standing = WIDTH * 0.58
        self.boy_x_close = WIDTH * 0.45
        self.girl_x_close = WIDTH * 0.55
        self.boy_x_sitting = WIDTH * 0.35
        self.girl_x_sitting = WIDTH * 0.65

    def _positions_for_layout(self, layout):
        if layout == "sitting":
            return self.boy_x_sitting, self.girl_x_sitting
        elif layout == "standing_close":
            return self.boy_x_close, self.girl_x_close
        else:
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
        self.in_pre_vo = False
        self.pre_vo_duration = 0
        self.main_vo_start_time = self.virtual_time

        scene = SCENES[self.current_scene_idx]

        if scene.get("pre_vo"):
            # Play narrator framing audio first — no subtitle, no talking
            self.in_pre_vo = True
            self.pre_vo_duration = self.audio.play(scene["pre_vo"])
            self.scene_audio_events.append((self.virtual_time, scene["pre_vo"]))
            self.current_audio_duration = 0  # main vo not started yet
        elif "vo" in scene:
            self.current_audio_duration = self.audio.play(scene["vo"])
            self.scene_audio_events.append((self.virtual_time, scene["vo"]))
            self.main_vo_start_time = self.virtual_time
        else:
            self.current_audio_duration = 0

        # Show subtitle immediately only if no pre_vo
        if not scene.get("pre_vo") and scene.get("text"):
            self.subtitle.show(scene["text"], self.virtual_time)

    def update(self):
        now = self.virtual_time
        if self.current_scene_idx == -1:
            self.next_scene()
            return

        scene = SCENES[self.current_scene_idx]

        # Update systems
        self.particles.update()
        self.subtitle.update(now)
        self.boy_idle.update()
        self.girl_idle.update()

        # State machine
        if self.state == "FADE_IN":
            elapsed = now - self.transition_start_time
            self.fade_alpha = max(0, 255 - int(255 * (elapsed / FADE_DURATION)))
            if elapsed > FADE_DURATION:
                self.state = "PLAYING"
                self.fade_alpha = 0

        elif self.state == "PLAYING":
            # Handle pre_vo → main vo transition
            if self.in_pre_vo:
                elapsed_since_scene = now - self.scene_start_time
                if elapsed_since_scene > self.pre_vo_duration + 500:
                    # Pre-vo finished + 500ms pause → start main vo
                    self.in_pre_vo = False
                    self.main_vo_start_time = now
                    if "vo" in scene:
                        self.current_audio_duration = self.audio.play(scene["vo"])
                        self.scene_audio_events.append((now, scene["vo"]))
                    if scene.get("text"):
                        self.subtitle.show(scene["text"], now)
                    self.audio_finished_time = 0
                return  # Don't check for scene end during pre_vo

            # Normal audio finish logic
            is_finished = False

            post_audio_delay = 1500
            if scene.get("talking") in ["boy", "girl"]:
                post_audio_delay = 2000
            if scene.get("hold_extra"):
                post_audio_delay = scene["hold_extra"]

            elapsed_since_main = now - self.main_vo_start_time
            audio_playing_virtual = elapsed_since_main < self.current_audio_duration
            min_time_safety = elapsed_since_main > 1000

            if not audio_playing_virtual and min_time_safety:
                if self.audio_finished_time == 0:
                    self.audio_finished_time = now
                if now - self.audio_finished_time > post_audio_delay:
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

        # Talking states — only during main vo (not pre_vo)
        elapsed_since_main = now - self.main_vo_start_time
        is_main_playing = (not self.in_pre_vo) and elapsed_since_main < self.current_audio_duration
        boy_talks = is_main_playing and scene.get("talking") == "boy"
        girl_talks = is_main_playing and scene.get("talking") == "girl"

        layout = scene.get("layout", "standing")
        is_sitting = (layout == "sitting")
        wind = self.particles.get_wind()
        floor_y = int(HEIGHT * 0.72)  # Raised to prevent subtitle overlap
        show_characters = scene.get("both") or scene.get("boy") or scene.get("girl")

        if scene.get("type") in ["theme", "final"] and not show_characters:
            # Centered text mode (theme introduction or ending title)
            text = scene["text"]
            lines = text.split("\n")
            f = title_font if scene["type"] == "final" else theme_font
            line_spacing = 55
            total_height = len(lines) * line_spacing
            start_y = (HEIGHT - total_height) // 2
            for i, line in enumerate(lines):
                surf = f.render(line, True, TEXT_COLOR)
                r = surf.get_rect(center=(WIDTH // 2, start_y + i * line_spacing))
                screen.blit(surf, r)
            # Particles still drift on text-only screens
            self.particles.draw(screen)
        else:
            # --- Character scene ---
            if is_sitting and show_characters:
                draw_table_and_chairs(screen, WIDTH // 2, floor_y)

            # Particles behind characters
            self.particles.draw(screen)

            if show_characters:
                boy_x, girl_x = self._positions_for_layout(layout)

                # Draw Boy
                draw_human(screen, boy_x, floor_y,
                           is_woman=False, breathing=breath,
                           talking=boy_talks, virtual_time=now,
                           idle=self.boy_idle, wind=wind,
                           sitting=is_sitting)

                # Draw Girl
                draw_human(screen, girl_x, floor_y,
                           is_woman=True, breathing=breath,
                           talking=girl_talks, virtual_time=now,
                           idle=self.girl_idle, wind=wind,
                           sitting=is_sitting)

            # Draw subtitles
            self.subtitle.draw(screen)

        # Fade overlay
        if self.fade_alpha > 0:
            fade_s = pygame.Surface((WIDTH, HEIGHT))
            fade_s.fill(BG_COLOR)
            fade_s.set_alpha(self.fade_alpha)
            screen.blit(fade_s, (0, 0))

        pygame.display.flip()

        # Capture frame
        frame_data = pygame.surfarray.array3d(screen)
        frame_data = frame_data.transpose([1, 0, 2])
        self.frames.append(frame_data)

    def run_loop(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
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
        video_clip = ImageSequenceClip(self.frames, fps=self.fps)

        clips = []
        for start_ms, filename in self.scene_audio_events:
            audio_path = os.path.join(AUDIO_DIR, filename)
            if os.path.exists(audio_path):
                a_clip = AudioFileClip(audio_path)
                a_clip = a_clip.with_start(start_ms / 1000.0)
                clips.append(a_clip)

        if clips:
            composite_audio = CompositeAudioClip(clips)
            video_clip = video_clip.with_audio(composite_audio)

        output_path = os.path.join(BASE_DIR, "output.mp4")
        video_clip.write_videofile(output_path, fps=self.fps,
                                   codec="libx264", audio_codec="aac")
        print(f"Export complete: {output_path}")


if __name__ == "__main__":
    print("\n--- Promise Day — Cinematic Story Export ---")
    print("NOTE: On-screen playback will lag during frame capture. This is normal.")
    print("The final 'output.mp4' will have perfect synchronization.\n")
    app = App()
    app.run_loop()
