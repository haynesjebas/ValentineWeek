#!/usr/bin/env python3
"""
Kiss Day - Valentine's Week Day 7
Theme: Acceptance — when nothing needs to be hidden.
Engine: particle system, kiss animation with lip contact, hug embrace,
heart particles, idle animations, cloth/hair sway, subtitle fades, video export.
"""

import pygame, math, sys, os, random, numpy as np
from moviepy import ImageSequenceClip, AudioFileClip, CompositeAudioClip

pygame.init()

WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Kiss Day")

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
AUDIO_DIR = os.path.join(BASE_DIR, "assets", "audio")
FADE_DURATION = 1500

# ---------------------------------------------------------------------------
# SCENES — Kiss then Hug then Meaning
# ---------------------------------------------------------------------------

SCENES = [
    # --- Theme introduction (no characters) ---
    {"id": 0, "type": "final",
     "vo": "kiss_sc1_title.mp3", "text": "Kiss Day", "layout": "standing"},

    {"id": 1, "type": "theme",
     "vo": "kiss_sc1_intro.mp3",
     "text": "Trust had brought them here.\nNow nothing needed to be hidden.",
     "layout": "standing"},

    {"id": 2, "type": "theme",
     "vo": "kiss_sc1_theme.mp3",
     "text": "Some moments do not ask for words.\nThey ask for acceptance.",
     "layout": "standing"},

    # --- Standing narration (characters appear) ---
    {"id": 3, "type": "scene",
     "vo": "kiss_sc2.mp3",
     "text": "They had shared fear.\nThey had shared truth.\nThey had shared closeness.",
     "layout": "standing", "both": True},

    # --- Emotional stillness ---
    {"id": 4, "type": "scene",
     "vo": "kiss_sc3.mp3",
     "text": "There was nothing left to prove.\nNothing left to protect.",
     "layout": "standing_close", "both": True},

    # --- KISS scene: 2s approach → kiss → narration → hold ---
    {"id": 5, "type": "scene",
     "vo": "kiss_sc4.mp3",
     "text": "This was not a promise.\nThis was acceptance.",
     "layout": "kissing", "both": True,
     "start_delay": 2000, "hold_extra": 3000},

    # --- HUG scene: starts in full embrace, hearts floating ---
    {"id": 6, "type": "scene",
     "vo": "kiss_sc5.mp3",
     "text": "When nothing is forced,\neverything becomes real.",
     "layout": "hugging_hold", "both": True},

    # --- Final meaning ---
    {"id": 7, "type": "scene",
     "vo": "kiss_sc6.mp3",
     "text": "Kiss Day isn't about the kiss.\nIt's about knowing you are home.",
     "layout": "standing_close", "both": True},

    # --- Ending (no characters) ---
    {"id": 8, "type": "final",
     "vo": "kiss_sc7_title.mp3", "text": "Kiss Day",
     "layout": "standing_close", "hold_extra": 3000},
]

# ---------------------------------------------------------------------------
# PETAL PARTICLE SYSTEM
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
# HEART PARTICLE SYSTEM
# ---------------------------------------------------------------------------

class Heart:
    def __init__(self, x, y):
        self.x = x + random.uniform(-6, 6)
        self.y = y + random.uniform(-4, 4)
        self.speed_x = random.uniform(-0.3, 0.3)
        self.speed_y = -random.uniform(0.3, 0.8)
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
    def draw(self, surface):
        if self.alpha <= 0:
            return
        s = int(self.size)
        hs = pygame.Surface((s * 3, s * 3), pygame.SRCALPHA)
        cx, cy = s * 1.5, s * 1.5
        r = s * 0.5
        pygame.draw.circle(hs, (*self.color, self.alpha),
                           (int(cx - r * 0.6), int(cy - r * 0.3)), int(r))
        pygame.draw.circle(hs, (*self.color, self.alpha),
                           (int(cx + r * 0.6), int(cy - r * 0.3)), int(r))
        pygame.draw.polygon(hs, (*self.color, self.alpha), [
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
    def update(self, spawning=False, cx=0, cy=0):
        if spawning:
            self.spawn_timer += 1
            if self.spawn_timer % 8 == 0:
                for _ in range(random.randint(1, 3)):
                    self.hearts.append(Heart(cx, cy))
        self.hearts = [h for h in self.hearts if h.alive]
        for h in self.hearts:
            h.update()
    def draw(self, surface):
        for h in self.hearts:
            h.draw(surface)

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
              lean_x=0, lean_y=0, smile=0.0, eyes_closed=False, head_tilt=0):
    """Draw body, head, face. Returns (lip_x, lip_y) for kiss contact."""
    scale = skel['scale']
    base_x, base_y = skel['base_x'], skel['base_y']
    hips_y, shoulder_y = skel['hips_y'], skel['shoulder_y']
    HEAD_R, SHOULDER_W = skel['HEAD_R'], skel['SHOULDER_W']
    TORSO_H, HIP_W = skel['TORSO_H'], skel['HIP_W']
    cloth_sway = skel['cloth_sway']
    head_cx = skel['head_cx'] + lean_x + head_tilt
    head_cy = skel['head_cy'] + lean_y + abs(head_tilt) * 0.15

    # --- Kiss Day Outfits ---
    if is_woman:
        clothing_color = (135, 200, 235)    # Soft sky blue
        clothing_accent = (110, 175, 210)
        leg_color = (240, 200, 180)
        bow_color = (120, 185, 220)
        bow_accent = (100, 160, 195)
    else:
        shirt_color = (185, 165, 130)       # Warm beige
        shirt_outline = (160, 140, 110)
        pants_color = (50, 48, 55)

    # Shadow
    sw = 110 * scale
    pygame.draw.ellipse(surface, (190, 190, 190),
                        (base_x - sw / 2, base_y - 10, sw, 20))

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

    # Eyes
    eye_x_off = 10 * scale
    eye_y_off = -HEAD_R / 5
    is_blinking = idle.is_blinking if idle else False
    for sx in [-1, 1]:
        ex = int(head_cx + sx * eye_x_off)
        ey = int(head_cy + eye_y_off)
        if eyes_closed or is_blinking:
            if eyes_closed and smile > 0.3:
                pygame.draw.arc(surface, (40, 40, 40),
                                (ex - 4, ey - 2, 8, 6), 0.2, math.pi - 0.2, 2)
            else:
                pygame.draw.line(surface, (40, 40, 40), (ex - 3, ey), (ex + 3, ey), 2)
        else:
            pygame.draw.circle(surface, (40, 40, 40), (ex, ey), 3)

    # Mouth
    m_y = head_cy + HEAD_R / 2
    lip_x, lip_y = head_cx, m_y
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

    # Bow (Girl)
    if is_woman:
        hs = cloth_sway * 0.6
        bx = head_cx + 22 * scale + hs * 0.4
        by = head_cy - 25 * scale
        pygame.draw.ellipse(surface, bow_color, (bx - 12, by - 6, 10, 12))
        pygame.draw.ellipse(surface, bow_color, (bx + 2, by - 6, 10, 12))
        pygame.draw.circle(surface, bow_accent, (int(bx), int(by)), 4)

    return lip_x, lip_y


def draw_arm_segment(surface, shoulder, elbow, hand, radius):
    skin = (255, 255, 255)
    draw_capsule(surface, skin, shoulder, elbow, radius)
    draw_capsule(surface, skin, elbow, hand, radius)


def draw_human_standing(surface, x, y, is_woman, breathing, talking,
                        virtual_time, idle, wind, smile=0.0):
    skel = _compute_skeleton(x, y, is_woman, breathing, idle, wind, virtual_time)
    scale = skel['scale']
    draw_body(surface, skel, is_woman, talking, virtual_time, idle, smile=smile)
    arm_r = int(7 * scale)
    cs = skel['cloth_sway']
    nl = (skel['base_x'] - skel['SHOULDER_W'] / 2 - 5 + cs * 0.3,
          skel['shoulder_y'] + 95 * scale)
    nr = (skel['base_x'] + skel['SHOULDER_W'] / 2 + 5 + cs * 0.2,
          skel['shoulder_y'] + 95 * scale)
    draw_capsule(surface, (255, 255, 255), skel['l_shoulder'], nl, arm_r)
    draw_capsule(surface, (255, 255, 255), skel['r_shoulder'], nr, arm_r)


# ---------------------------------------------------------------------------
# KISS PAIR — profile view, audience sees lips approach and touch
# ---------------------------------------------------------------------------

def _draw_profile_face(surface, head_cx, head_cy, HEAD_R, scale, profile_dir,
                       smile, eyes_closed, idle, virtual_time, talking):
    """
    Draw a profile/side-view face on an already-drawn head circle.
    profile_dir: +1 = facing right, -1 = facing left.
    Returns (lip_x, lip_y) at the edge of the head on the facing side.
    """
    d = profile_dir  # direction multiplier

    # — Blush (same as front, just shifted toward facing side)
    if smile > 0.1:
        ba = min(70, int(70 * ((smile - 0.1) / 0.9)))
        br = int(7 * scale)
        bx = int(head_cx + d * 6 * scale)
        by = int(head_cy + HEAD_R * 0.15)
        bs = pygame.Surface((br * 2, br * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(bs, (255, 160, 160, ba), (0, 0, br * 2, br * 2))
        surface.blit(bs, (bx - br, by - br))

    # — One visible eye (the far eye from partner, i.e. toward viewer)
    ex = int(head_cx - d * 4 * scale)
    ey = int(head_cy - HEAD_R * 0.2)
    is_blinking = idle.is_blinking if idle else False
    if eyes_closed or is_blinking:
        if eyes_closed and smile > 0.3:
            pygame.draw.arc(surface, (40, 40, 40),
                            (ex - 4, ey - 2, 8, 6), 0.2, math.pi - 0.2, 2)
        else:
            pygame.draw.line(surface, (40, 40, 40), (ex - 3, ey), (ex + 3, ey), 2)
    else:
        pygame.draw.circle(surface, (40, 40, 40), (ex, ey), 3)

    # — Nose bump on facing side
    nose_tip_x = head_cx + d * HEAD_R * 0.85
    nose_tip_y = head_cy - HEAD_R * 0.05
    nose_base_y_top = head_cy - HEAD_R * 0.25
    nose_base_y_bot = head_cy + HEAD_R * 0.12
    nose_base_x = head_cx + d * HEAD_R * 0.55
    pygame.draw.polygon(surface, (245, 235, 230), [
        (int(nose_base_x), int(nose_base_y_top)),
        (int(nose_tip_x), int(nose_tip_y)),
        (int(nose_base_x), int(nose_base_y_bot))])
    pygame.draw.lines(surface, (210, 200, 195), False, [
        (int(nose_base_x), int(nose_base_y_top)),
        (int(nose_tip_x), int(nose_tip_y)),
        (int(nose_base_x), int(nose_base_y_bot))], 2)

    # — Lips at edge of head, facing side
    lip_x = head_cx + d * HEAD_R * 0.88
    lip_y = head_cy + HEAD_R * 0.35
    lip_w = 5 * scale
    # Two small lips (upper and lower)
    lip_color = (220, 140, 140) if smile > 0.3 else (200, 130, 130)
    # Upper lip
    pygame.draw.ellipse(surface, lip_color,
                        (int(lip_x - lip_w * 0.3), int(lip_y - 3), int(lip_w), 4))
    # Lower lip
    pygame.draw.ellipse(surface, lip_color,
                        (int(lip_x - lip_w * 0.3), int(lip_y), int(lip_w * 0.9), 3))

    return lip_x, lip_y


def draw_kiss_pair(surface, boy_x, girl_x, floor_y, progress,
                   breathing, virtual_time, boy_idle, girl_idle, wind):
    """
    Kiss with profile faces — audience sees lips approach and touch.
    Returns (lip_mid_x, lip_mid_y, is_kissing).
    """
    p = _ease_out(min(1.0, progress))
    wrap = min(1.0, progress / 0.7)
    kiss_contact = p >= 0.95

    # Profile transition: faces turn from front to side during approach
    profile_amt = min(1.0, max(0, (p - 0.15) / 0.5))

    # Head lean — moderate, just enough to bring lip-edges together
    lean_prog = max(0, (p - 0.2) / 0.8) if p > 0.2 else 0.0
    boy_lean_x = lean_prog * 16       # toward girl
    boy_lean_y = lean_prog * 24       # DOWN significantly toward her
    girl_lean_x = lean_prog * -12     # toward boy
    girl_lean_y = lean_prog * -4      # slight upward tilt

    boy_skel = _compute_skeleton(boy_x, floor_y, False, breathing, boy_idle, wind, virtual_time)
    girl_skel = _compute_skeleton(girl_x, floor_y, True, breathing, girl_idle, wind, virtual_time)

    bs, gs = boy_skel['scale'], girl_skel['scale']
    arm_r_boy, arm_r_girl = int(7 * bs), int(7 * gs)

    # --- Arm positions (hand-holding + waist) ---
    boy_mid_y = boy_skel['shoulder_y'] + boy_skel['TORSO_H'] * 0.45
    cs_b = boy_skel['cloth_sway']
    boy_nl = (boy_skel['base_x'] - boy_skel['SHOULDER_W'] / 2 - 5 + cs_b * 0.3,
              boy_skel['shoulder_y'] + 95 * bs)
    boy_nr = (boy_skel['base_x'] + boy_skel['SHOULDER_W'] / 2 + 5 + cs_b * 0.2,
              boy_skel['shoulder_y'] + 95 * bs)
    mid_x_hands = (boy_x + girl_x) / 2
    hand_y = boy_skel['shoulder_y'] + 80 * bs
    boy_wl_elbow = (boy_x + 15 * bs, hand_y - 15 * bs)
    boy_wl_hand = (mid_x_hands, hand_y)
    boy_wr_elbow = (boy_x + 20 * bs, boy_mid_y + 10 * bs)
    boy_wr_hand = (girl_x - 5 * gs, boy_mid_y + 25 * bs)

    girl_mid_y = girl_skel['shoulder_y'] + girl_skel['TORSO_H'] * 0.45
    cs_g = girl_skel['cloth_sway']
    girl_nl = (girl_skel['base_x'] - girl_skel['SHOULDER_W'] / 2 + cs_g * 0.3,
               girl_skel['shoulder_y'] + 95 * gs)
    girl_nr = (girl_skel['base_x'] + girl_skel['SHOULDER_W'] / 2 + cs_g * 0.2,
               girl_skel['shoulder_y'] + 95 * gs)
    girl_wr_elbow = (girl_x - 15 * gs, hand_y - 15 * gs)
    girl_wr_hand = (mid_x_hands, hand_y)
    girl_wl_elbow = (girl_x - 12 * gs, girl_mid_y - 5 * gs)
    girl_wl_hand = (boy_x + 15 * bs, girl_mid_y + 5 * gs)

    # Interpolate arms
    boy_nl_m = _lerp(boy_skel['l_shoulder'], boy_nl, 0.5)
    boy_nr_m = _lerp(boy_skel['r_shoulder'], boy_nr, 0.5)
    boy_l_elbow = _lerp(boy_nl_m, boy_wl_elbow, wrap)
    boy_l_hand = _lerp(boy_nl, boy_wl_hand, wrap)
    boy_r_elbow = _lerp(boy_nr_m, boy_wr_elbow, wrap)
    boy_r_hand = _lerp(boy_nr, boy_wr_hand, wrap)

    girl_nl_m = _lerp(girl_skel['l_shoulder'], girl_nl, 0.5)
    girl_nr_m = _lerp(girl_skel['r_shoulder'], girl_nr, 0.5)
    girl_l_elbow = _lerp(girl_nl_m, girl_wl_elbow, wrap)
    girl_l_hand = _lerp(girl_nl, girl_wl_hand, wrap)
    girl_r_elbow = _lerp(girl_nr_m, girl_wr_elbow, wrap)
    girl_r_hand = _lerp(girl_nr, girl_wr_hand, wrap)

    smile = min(1.0, wrap * 1.2)

    # --- LAYERED DRAWING ---
    # Back arms
    draw_arm_segment(surface, boy_skel['r_shoulder'], boy_r_elbow, boy_r_hand, arm_r_boy)
    draw_arm_segment(surface, girl_skel['l_shoulder'], girl_l_elbow, girl_l_hand, arm_r_girl)

    # --- Boy body (torso, legs drawn normally via draw_body) ---
    # Draw body WITHOUT face (we'll draw profile face separately)
    boy_head_cx = boy_skel['head_cx'] + boy_lean_x
    boy_head_cy = boy_skel['head_cy'] + boy_lean_y
    girl_head_cx = girl_skel['head_cx'] + girl_lean_x
    girl_head_cy = girl_skel['head_cy'] + girl_lean_y

    if profile_amt < 0.1:
        # Still mostly front-facing — use normal draw_body
        boy_lip = draw_body(surface, boy_skel, False, False, virtual_time, boy_idle,
                            lean_x=boy_lean_x, lean_y=boy_lean_y,
                            smile=smile, eyes_closed=kiss_contact, head_tilt=0)
        girl_lip = draw_body(surface, girl_skel, True, False, virtual_time, girl_idle,
                             lean_x=girl_lean_x, lean_y=girl_lean_y,
                             smile=smile, eyes_closed=kiss_contact, head_tilt=0)
    else:
        # Profile view — draw body without head, then profile head
        # Boy body (no head — we'll draw it manually with profile)
        draw_body(surface, boy_skel, False, False, virtual_time, boy_idle,
                  lean_x=boy_lean_x, lean_y=boy_lean_y,
                  smile=0, eyes_closed=False, head_tilt=0)
        # Girl body
        draw_body(surface, girl_skel, True, False, virtual_time, girl_idle,
                  lean_x=girl_lean_x, lean_y=girl_lean_y,
                  smile=0, eyes_closed=False, head_tilt=0)

        # Redraw heads with profile faces on top
        HEAD_R_boy = boy_skel['HEAD_R']
        HEAD_R_girl = girl_skel['HEAD_R']

        # Boy head circle
        pygame.draw.circle(surface, (255, 255, 255),
                           (int(boy_head_cx), int(boy_head_cy)), int(HEAD_R_boy))
        pygame.draw.circle(surface, (240, 240, 240),
                           (int(boy_head_cx), int(boy_head_cy)), int(HEAD_R_boy), 2)
        # Boy profile face — facing RIGHT toward girl
        boy_lip = _draw_profile_face(surface, boy_head_cx, boy_head_cy,
                                      HEAD_R_boy, bs, +1,
                                      smile, kiss_contact, boy_idle, virtual_time, False)

        # Girl head circle
        pygame.draw.circle(surface, (255, 255, 255),
                           (int(girl_head_cx), int(girl_head_cy)), int(HEAD_R_girl))
        pygame.draw.circle(surface, (240, 240, 240),
                           (int(girl_head_cx), int(girl_head_cy)), int(HEAD_R_girl), 2)
        # Girl profile face — facing LEFT toward boy
        girl_lip = _draw_profile_face(surface, girl_head_cx, girl_head_cy,
                                       HEAD_R_girl, gs, -1,
                                       smile, kiss_contact, girl_idle, virtual_time, False)

        # Girl bow (on profile)
        cloth_sway = girl_skel['cloth_sway']
        hs = cloth_sway * 0.6
        bx = girl_head_cx + 22 * gs + hs * 0.4
        by = girl_head_cy - 25 * gs
        pygame.draw.ellipse(surface, (120, 185, 220), (bx - 12, by - 6, 10, 12))
        pygame.draw.ellipse(surface, (120, 185, 220), (bx + 2, by - 6, 10, 12))
        pygame.draw.circle(surface, (100, 160, 195), (int(bx), int(by)), 4)

    # Front arms
    draw_arm_segment(surface, boy_skel['l_shoulder'], boy_l_elbow, boy_l_hand, arm_r_boy)
    draw_arm_segment(surface, girl_skel['r_shoulder'], girl_r_elbow, girl_r_hand, arm_r_girl)

    mid_lx = (boy_lip[0] + girl_lip[0]) / 2
    mid_ly = (boy_lip[1] + girl_lip[1]) / 2
    return mid_lx, mid_ly, kiss_contact


# ---------------------------------------------------------------------------
# HUG PAIR — starts in full embrace (from HugDay engine)
# ---------------------------------------------------------------------------

def draw_embrace_hold(surface, boy_x, girl_x, floor_y,
                      breathing, virtual_time, boy_idle, girl_idle, wind):
    """Draw both characters already in full embrace — no approach animation."""
    wrap = 1.0  # fully wrapped
    lean_amt = 0.6  # gentle lean

    boy_skel = _compute_skeleton(boy_x, floor_y, False, breathing, boy_idle, wind, virtual_time)
    girl_skel = _compute_skeleton(girl_x, floor_y, True, breathing, girl_idle, wind, virtual_time)

    bs, gs = boy_skel['scale'], girl_skel['scale']
    arm_r_boy, arm_r_girl = int(7 * bs), int(7 * gs)

    # Boy arms wrap around girl's back
    boy_mid_y = boy_skel['shoulder_y'] + boy_skel['TORSO_H'] * 0.45
    # Left arm → girl upper back
    boy_l_elbow = (boy_x + 25 * bs, boy_mid_y - 5 * bs)
    boy_l_hand = (girl_x + 18 * gs, boy_mid_y + 5 * bs)
    # Right arm → girl mid-back
    boy_r_elbow = (boy_x + 22 * bs, boy_mid_y + 25 * bs)
    boy_r_hand = (girl_x + 15 * gs, boy_mid_y + 30 * bs)

    # Girl arms wrap around boy's back
    girl_mid_y = girl_skel['shoulder_y'] + girl_skel['TORSO_H'] * 0.45
    # Left arm → boy mid-back
    girl_l_elbow = (girl_x - 22 * gs, girl_mid_y + 20 * gs)
    girl_l_hand = (boy_x - 15 * bs, girl_mid_y + 28 * gs)
    # Right arm → boy upper back
    girl_r_elbow = (girl_x - 20 * gs, girl_mid_y - 5 * gs)
    girl_r_hand = (boy_x - 12 * bs, girl_mid_y + 8 * gs)

    # --- LAYERED DRAWING (same as HugDay) ---
    # 1: Boy right arm (behind girl)
    draw_arm_segment(surface, boy_skel['r_shoulder'], boy_r_elbow, boy_r_hand, arm_r_boy)
    # 2: Girl left arm (behind boy)
    draw_arm_segment(surface, girl_skel['l_shoulder'], girl_l_elbow, girl_l_hand, arm_r_girl)

    # 3: Boy body
    draw_body(surface, boy_skel, False, False, virtual_time, boy_idle,
              lean_x=lean_amt * 4, lean_y=lean_amt * 2, smile=0.9)
    # 4: Girl body
    draw_body(surface, girl_skel, True, False, virtual_time, girl_idle,
              lean_x=-lean_amt * 3, lean_y=lean_amt * 2, smile=0.9)

    # 5: Boy left arm (in front)
    draw_arm_segment(surface, boy_skel['l_shoulder'], boy_l_elbow, boy_l_hand, arm_r_boy)
    # 6: Girl right arm (in front)
    draw_arm_segment(surface, girl_skel['r_shoulder'], girl_r_elbow, girl_r_hand, arm_r_girl)

    # Heart spawn point (between their heads)
    mid_x = (boy_skel['head_cx'] + girl_skel['head_cx']) / 2
    mid_y = (boy_skel['head_cy'] + girl_skel['head_cy']) / 2 - 10
    return mid_x, mid_y


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
            print(f"Error: {e}")
            return 0

# ---------------------------------------------------------------------------
# APPLICATION
# ---------------------------------------------------------------------------

class App:
    def __init__(self):
        self.audio = AudioController()
        self.particles = ParticleSystem(40)
        self.hearts = HeartSystem()
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

        self.kiss_active = False
        self.kiss_start_time = 0
        self.heart_cx = WIDTH / 2
        self.heart_cy = HEIGHT * 0.3

        # Positions
        self.boy_x_standing = WIDTH * 0.42
        self.girl_x_standing = WIDTH * 0.58
        self.boy_x_close = WIDTH * 0.45
        self.girl_x_close = WIDTH * 0.55
        self.boy_x_kiss = WIDTH * 0.48
        self.girl_x_kiss = WIDTH * 0.52
        # Hug positions (near-overlap)
        self.boy_x_hug = WIDTH * 0.485
        self.girl_x_hug = WIDTH * 0.515

    def _positions_for_layout(self, layout):
        if layout == "standing_close":
            return self.boy_x_close, self.girl_x_close
        elif layout == "kissing":
            return self.boy_x_kiss, self.girl_x_kiss
        elif layout == "hugging_hold":
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
        self.kiss_active = False

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

        layout = scene.get("layout", "standing")

        # Heart updates — during kiss and hug scenes
        if layout == "kissing":
            elapsed = now - self.scene_start_time
            approach_dur = scene.get("start_delay", 2000)
            progress = min(1.0, elapsed / approach_dur) if approach_dur > 0 else 1.0
            if progress >= 0.95:
                if not self.kiss_active:
                    self.kiss_active = True
                    self.kiss_start_time = now
                he = now - self.kiss_start_time
                self.hearts.update(500 < he < 3500, self.heart_cx, self.heart_cy)
            else:
                self.hearts.update(False)
        elif layout == "hugging_hold":
            # Continue gentle heart spawning during hug
            self.hearts.update(True, self.heart_cx, self.heart_cy)
        else:
            self.hearts.update(False)

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
        layout = scene.get("layout", "standing")
        is_kissing = (layout == "kissing")
        is_hugging = (layout == "hugging_hold")
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
                if is_kissing:
                    elapsed = now - self.scene_start_time
                    approach_dur = scene.get("start_delay", 2000)
                    progress = min(1.0, elapsed / approach_dur) if approach_dur > 0 else 1.0
                    boy_x = self.boy_x_close + (self.boy_x_kiss - self.boy_x_close) * _ease_out(progress)
                    girl_x = self.girl_x_close + (self.girl_x_kiss - self.girl_x_close) * _ease_out(progress)
                    result = draw_kiss_pair(screen, boy_x, girl_x, floor_y, progress,
                                           breath, now, self.boy_idle, self.girl_idle, wind)
                    if result:
                        self.heart_cx, self.heart_cy, _ = result
                    self.hearts.draw(screen)
                elif is_hugging:
                    result = draw_embrace_hold(screen, self.boy_x_hug, self.girl_x_hug,
                                              floor_y, breath, now,
                                              self.boy_idle, self.girl_idle, wind)
                    if result:
                        self.heart_cx, self.heart_cy = result
                    self.hearts.draw(screen)
                else:
                    boy_x, girl_x = self._positions_for_layout(layout)
                    scene_smile = 0.3 if layout == "standing_close" else 0.0
                    draw_human_standing(screen, boy_x, floor_y,
                                       False, breath, False, now,
                                       self.boy_idle, wind, smile=scene_smile)
                    draw_human_standing(screen, girl_x, floor_y,
                                       True, breath, False, now,
                                       self.girl_idle, wind, smile=scene_smile)
            self.subtitle.draw(screen)

        if self.fade_alpha > 0:
            fs = pygame.Surface((WIDTH, HEIGHT))
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
    print("\n--- Kiss Day — Cinematic Story Export ---")
    print("NOTE: On-screen playback will lag during frame capture. This is normal.")
    print("The final 'output.mp4' will have perfect synchronization.\n")
    App().run_loop()
