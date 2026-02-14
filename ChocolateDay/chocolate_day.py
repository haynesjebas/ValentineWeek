#!/usr/bin/env python3
"""
Chocolate Day - Valentine's Week Day 3
Theme: Comfort after clarity

Following Rose Day (intention) and Propose Day (clarity),
this day shows the relationship settling into comfort.
"""

import pygame
import math
import sys

pygame.init()

# Display
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chocolate Day")

# Colors
BG_COLOR = (211, 211, 211)  # Light grey
TEXT_COLOR = (45, 45, 45)

# Typography
pygame.font.init()
title_font = pygame.font.Font(None, 72)
subtitle_font = pygame.font.Font(None, 42)

# Scene configuration
scenes = [
    {"type": "theme", "text": "Rose Day showed intention.\nPropose Day brings clarity and courage."},
    {"vo": "assets/audio/choc_sc1.mp3", "text": "Not every day needs courage.\nSome days need comfort.", "type": "intro"},
    {"vo": "assets/audio/choc_sc2.mp3", "text": "After saying what mattered,\nhe didn't feel the need to prove anything.", "boy": True, "chocolate": "in_hand"},
    {"vo": "assets/audio/choc_sc3.mp3", "text": "This wasn't about a gesture.\nIt was about sharing something ordinary.", "boy": True, "chocolate": "looking"},
    {"vo": "assets/audio/choc_sc4.mp3", "text": "She noticed the shift.\nThis wasn't effort.\nThis was ease.", "girl": True},
    {"vo": "assets/audio/choc_sc5.mp3", "text": "I thought you might like this.", "both": True, "chocolate": "offering"},
    {"text": "", "both": True, "chocolate": "transferring", "silent": True},  # Scene 6: Silent transfer
    {"vo": "assets/audio/choc_sc7.mp3", "text": "Some connections grow louder.\nOthers grow easier.", "both": True, "chocolate": "received"},
    {"vo": "assets/audio/choc_sc8.mp3", "text": "Chocolate Day isn't about sweetness.\nIt's about choosing comfort after honesty.", "both": True, "chocolate": "received"},
    {"type": "final", "text": "Chocolate Day"}
]

FADE_DURATION = 2000

def ease_in_out(t):
    return t * t * (3 - 2 * t)

def draw_capsule(screen, color, p1, p2, radius):
    """Draw a capsule (line with rounded ends)"""
    pygame.draw.line(screen, color, p1, p2, radius * 2)
    pygame.draw.circle(screen, color, (int(p1[0]), int(p1[1])), radius)
    pygame.draw.circle(screen, color, (int(p2[0]), int(p2[1])), radius)

def draw_chocolate(screen, x, y, angle=0):
    """Draw a small chocolate bar"""
    w, h = 30, 20
    
    # Main chocolate rectangle
    choc_rect = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(choc_rect, (139, 69, 19), (0, 0, w, h), border_radius=3)  # Brown
    pygame.draw.rect(choc_rect, (101, 51, 15), (0, 0, w, h), 2, border_radius=3)  # Darker outline
    
    # Wrapper highlights
    pygame.draw.line(choc_rect, (160, 90, 40), (5, 3), (w-5, 3), 1)
    pygame.draw.line(choc_rect, (160, 90, 40), (5, h-3), (w-5, h-3), 1)
    
    # Rotate if needed
    if angle != 0:
        choc_rect = pygame.transform.rotate(choc_rect, angle)
    
    rect = choc_rect.get_rect(center=(x, y))
    screen.blit(choc_rect, rect)

def draw_human(screen, x, y, is_woman=False, expression="neutral", breathing=0, 
               has_chocolate=False, step_offset=0):
    """Draw human character with clothing"""
    scale = 0.78 if is_woman else 0.95
    
    # Clothing colors
    if is_woman:
        clothing_color = (230, 190, 220)  # Soft lavender/pink dress
        clothing_accent = (210, 170, 200)
    else:
        shirt_color = (200, 210, 220)  # Light blue-grey shirt
        pants_color = (60, 70, 90)  # Dark grey pants
    
    HEAD_R = 30 * scale
    SHOULDER_W = (52 if is_woman else 68) * scale
    TORSO_H = (110 + breathing) * scale
    HIP_W = (56 if is_woman else 48) * scale
    LEG_L = 120 * scale
    
    base_x = x + (step_offset if is_woman else 0)
    base_y = y - breathing * (0.3 if is_woman else 0.4)
    
    # Shadow
    pygame.draw.ellipse(screen, (190, 190, 190), (base_x - 55*scale, y - 10, 110*scale, 20))
    
    # Positions
    hips_y = base_y - LEG_L
    shoulder_y = hips_y - TORSO_H
    head_center_y = shoulder_y - 10*scale - HEAD_R
    
    # === CLOTHING LAYER (drawn first, behind body) ===
    
    if not is_woman:
        # Boy: Pants (legs with color)
        for side in [-1, 1]:
            lx = base_x + side * (HIP_W / 4)
            # Pants as colored capsules
            draw_capsule(screen, pants_color, (lx, hips_y), (lx, base_y), int(8*scale))
    
    # Torso clothing
    if is_woman:
        # Girl: Simple dress
        dress_pts = [
            (base_x - SHOULDER_W/2, shoulder_y),
            (base_x + SHOULDER_W/2, shoulder_y),
            (base_x + HIP_W/2 + 20*scale, hips_y + 30*scale),
            (base_x - HIP_W/2 - 20*scale, hips_y + 30*scale)
        ]
        pygame.draw.polygon(screen, clothing_color, dress_pts)
        pygame.draw.polygon(screen, clothing_accent, dress_pts, 2)
    else:
        # Boy: Shirt
        shirt_pts = [
            (base_x - SHOULDER_W/2, shoulder_y),
            (base_x + SHOULDER_W/2, shoulder_y),
            (base_x + HIP_W/2, hips_y),
            (base_x - HIP_W/2, hips_y)
        ]
        pygame.draw.polygon(screen, shirt_color, shirt_pts)
        pygame.draw.polygon(screen, (180, 190, 200), shirt_pts, 2)
    
    # === WHITE BODY PARTS (over clothing) ===
    
    if not is_woman:
        # Boy legs (white, visible below pants)
        for side in [-1, 1]:
            lx = base_x + side * (HIP_W / 4)
            pygame.draw.circle(screen, (255, 255, 255), (int(lx), int(base_y)), int(10*scale))
    else:
        # Girl legs (white, visible below dress)
        for side in [-1, 1]:
            lx = base_x + side * (HIP_W / 4)
            draw_capsule(screen, (255, 255, 255), (base_x + side*(HIP_W/4), hips_y + 30*scale), 
                        (lx, base_y), int(8*scale))
    
    # Arms
    arm_radius = 7 * scale
    
    # Left arm
    if has_chocolate:
        # Arm bent, holding chocolate
        l_elbow = (base_x - SHOULDER_W/2 - 10, shoulder_y + 40*scale)
        l_hand = (base_x - 20, shoulder_y + 60*scale)
    else:
        l_shoulder = (base_x - SHOULDER_W/2, shoulder_y + 10)
        l_hand = (base_x - SHOULDER_W/2 - 5, shoulder_y + 95*scale)
        draw_capsule(screen, (255, 255, 255), l_shoulder, l_hand, int(arm_radius))
    
    if has_chocolate:
        l_shoulder = (base_x - SHOULDER_W/2, shoulder_y + 10)
        draw_capsule(screen, (255, 255, 255), l_shoulder, l_elbow, int(arm_radius))
        draw_capsule(screen, (255, 255, 255), l_elbow, l_hand, int(arm_radius))
    
    # Right arm
    r_shoulder = (base_x + SHOULDER_W/2, shoulder_y + 10)
    r_hand = (base_x + SHOULDER_W/2 + 5, shoulder_y + 95*scale)
    draw_capsule(screen, (255, 255, 255), r_shoulder, r_hand, int(arm_radius))
    
    # Head
    pygame.draw.circle(screen, (255, 255, 255), (int(base_x), int(head_center_y)), int(HEAD_R))
    pygame.draw.circle(screen, (240, 240, 240), (int(base_x), int(head_center_y)), int(HEAD_R), 2)
    
    # Face
    eye_x, eye_y = 10 * scale, -HEAD_R/5
    for sx in [-1, 1]:
        pygame.draw.circle(screen, (40, 40, 40), (int(base_x + sx * eye_x), int(head_center_y + eye_y)), 3)
    
    m_y = head_center_y + HEAD_R/2
    if expression == "smile":
        pygame.draw.arc(screen, (40, 40, 40), (int(base_x-10), int(m_y-5), 20, 10), math.pi, 0, 2)
    else:
        pygame.draw.line(screen, (40, 40, 40), (base_x-4, m_y), (base_x+4, m_y), 2)

    if is_woman:
        # Ribbon bow
        bow_x, bow_y = base_x + 22*scale, head_center_y - 25*scale
        pygame.draw.ellipse(screen, (255, 120, 170), (bow_x-12, bow_y-6, 10, 12))
        pygame.draw.ellipse(screen, (255, 120, 170), (bow_x+2, bow_y-6, 10, 12))
        pygame.draw.circle(screen, (200, 50, 100), (int(bow_x), int(bow_y)), 4)
    
    # Draw chocolate if in hand
    if has_chocolate:
        draw_chocolate(screen, int(l_hand[0]), int(l_hand[1]))

class AudioService:
    def __init__(self):
        pygame.mixer.init()
        self.vo_channel = pygame.mixer.Channel(0)
        
    def play_vo(self, path, text):
        try:
            sound = pygame.mixer.Sound(path)
            self.vo_channel.play(sound)
        except:
            print(f"Could not load {path}")

class StoryApp:
    def __init__(self):
        self.audio = AudioService()
        self.scenes = scenes
        self.idx = 0
        self.start_ticks = 0
        self.scene_hold_ticks = 0
        self.paused = False
        self.subtitle_font = subtitle_font
        self.title_font = title_font
        self.screen = screen
        
    def draw_subtitles(self):
        scene = self.scenes[self.idx]
        text = scene.get("text", "")
        if not text:
            return
        
        lines = text.split("\n")
        line_height = 50
        total_height = len(lines) * line_height
        start_y = HEIGHT - 140 - total_height
        
        for i, line in enumerate(lines):
            surf = self.subtitle_font.render(line, True, TEXT_COLOR)
            rect = surf.get_rect(center=(WIDTH//2, start_y + i * line_height))
            self.screen.blit(surf, rect)
    
    def run(self):
        clock = pygame.time.Clock()
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                        if self.paused:
                            if self.audio.vo_channel.get_busy():
                                self.audio.vo_channel.pause()
                        else:
                            if self.audio.vo_channel.get_busy():
                                self.audio.vo_channel.unpause()
            
            if not self.paused:
                ticks = pygame.time.get_ticks()
                elapsed = ticks - self.start_ticks
                scene = self.scenes[self.idx]
                
                # Scene progression
                done = False
                if scene.get("type") in ["theme", "intro", "final"]:
                    if elapsed > 5000:
                        done = True
                elif scene.get("silent"):
                    if elapsed > 4000:  # Silent scene duration
                        done = True
                elif scene.get("vo"):
                    if not self.audio.vo_channel.get_busy() and elapsed > 1000:
                        if self.scene_hold_ticks == 0:
                            self.scene_hold_ticks = ticks
                        elif ticks - self.scene_hold_ticks > 2500:
                            done = True
                
                if done:
                    self.idx += 1
                    self.start_ticks = ticks
                    self.scene_hold_ticks = 0
                    if self.idx < len(self.scenes):
                        next_scene = self.scenes[self.idx]
                        if next_scene.get("vo"):
                            self.audio.play_vo(next_scene["vo"], next_scene["text"])
                    continue
                
                # Rendering
                self.screen.fill(BG_COLOR)
                
                if self.idx < len(self.scenes):
                    scene = self.scenes[self.idx]
                    
                    if scene.get("type") in ["theme", "intro", "final"]:
                        # Text only scenes
                        text = scene["text"]
                        lines = text.split("\n")
                        line_height = 60
                        total_height = len(lines) * line_height
                        start_y = (HEIGHT - total_height) // 2
                        
                        font = self.title_font if scene.get("type") == "final" else self.subtitle_font
                        
                        for i, line in enumerate(lines):
                            surf = font.render(line, True, TEXT_COLOR)
                            rect = surf.get_rect(center=(WIDTH//2, start_y + i * line_height))
                            self.screen.blit(surf, rect)
                    else:
                        # Character scenes
                        bx, gx = WIDTH * 0.42, WIDTH * 0.58
                        breath = math.sin(ticks * 0.002) * 3
                        
                        choc_state = scene.get("chocolate", "none")
                        
                        if scene.get("boy"):
                            has_choc = choc_state in ["in_hand", "looking"]
                            draw_human(self.screen, bx+50, HEIGHT*0.8, has_chocolate=has_choc, breathing=breath)
                        elif scene.get("girl"):
                            draw_human(self.screen, gx-50, HEIGHT*0.8, is_woman=True, breathing=breath)
                        elif scene.get("both"):
                            # Both characters
                            draw_human(self.screen, bx, HEIGHT*0.8, has_chocolate=(choc_state=="offering"), breathing=breath)
                            
                            girl_has_choc = choc_state == "received"
                            girl_expr = "smile" if choc_state == "received" else "neutral"
                            draw_human(self.screen, gx, HEIGHT*0.8, is_woman=True, 
                                     expression=girl_expr, breathing=breath, has_chocolate=girl_has_choc)
                            
                            # Chocolate transfer animation
                            if choc_state == "transferring":
                                progress = min(1.0, elapsed / 3000)
                                boy_choc_x, boy_choc_y = bx - 20, HEIGHT*0.8 - 140
                                girl_choc_x, girl_choc_y = gx - 20, HEIGHT*0.8 - 140
                                
                                choc_x = boy_choc_x + (girl_choc_x - boy_choc_x) * progress
                                choc_y = boy_choc_y + (girl_choc_y - boy_choc_y) * progress
                                
                                draw_chocolate(self.screen, int(choc_x), int(choc_y))
                        
                        self.draw_subtitles()
                else:
                    break
                
                # Fade effects
                fade_a = 0
                if elapsed < FADE_DURATION:
                    fade_a = int(255 * (1 - ease_in_out(elapsed / FADE_DURATION)))
                elif self.scene_hold_ticks > 0:
                    hold_elapsed = ticks - self.scene_hold_ticks
                    if hold_elapsed < FADE_DURATION:
                        fade_a = int(255 * ease_in_out(hold_elapsed / FADE_DURATION))
                
                if fade_a > 0:
                    fade_surf = pygame.Surface((WIDTH, HEIGHT))
                    fade_surf.fill(BG_COLOR)
                    fade_surf.set_alpha(fade_a)
                    self.screen.blit(fade_surf, (0, 0))
            
            pygame.display.flip()
            clock.tick(60)

if __name__ == "__main__":
    app = StoryApp()
    app.run()
