#!/usr/bin/env python3
"""
Teddy Day - Valentine's Week Day 4
Theme: Comfort turns into care
Strict State Machine Implementation & Audio Sync
"""

import pygame
import math
import sys
import os
import numpy as np
from moviepy import VideoClip, ImageSequenceClip, AudioFileClip, CompositeAudioClip

pygame.init()

# Display
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Teddy Day")

# Colors
BG_COLOR = (211, 211, 211)  # Light grey
TEXT_COLOR = (45, 45, 45)

# Typography
pygame.font.init()
title_font = pygame.font.Font(None, 72)
try:
    subtitle_font = pygame.font.SysFont("georgia", 36, italic=True)
except:
    subtitle_font = pygame.font.Font(None, 36)

# --- CONFIGURATION ---

# Path helper
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
AUDIO_DIR = os.path.join(ASSETS_DIR, "audio")

SCENES = [
    {
        "id": 0,
        "type": "theme", 
        "vo": "teddy_sc0.mp3", 
        "text": "Comfort turns into care."
    },
    {
        "id": 1,
        "type": "theme", # Using "theme" type for centered text mode
        "vo": "teddy_sc1.mp3", 
        "text": "This day asks:\nWhat happens when comfort becomes something you want to protect?"
    },
    {
        "id": 2,
        "type": "intro", 
        "vo": "teddy_sc2.mp3", 
        "text": "Somewhere between ease and familiarity,\nsomething deeper begins.",
        "boy": True
    },
    {
        "id": 3,
        "type": "scene",
        "vo": "teddy_sc3.mp3", 
        "text": "She felt it too.\nThis wasn’t effort anymore.", 
        "girl": True
    },
    {
        "id": 4,
        "type": "scene",
        "vo": "teddy_sc4.mp3", 
        "text": "Care doesn’t arrive loudly.\nIt shows up with responsibility.", 
        "both": True
    },
    {
        "id": 5,
        "type": "scene",
        "vo": "teddy_sc5_boy.mp3", 
        "text": "He said: I saw this and thought of you.", 
        "both": True, 
        "teddy": "transferring",
        "talking": "boy", # Direct speech
        "duration": 2500 # Transfer duration
    },
    {
        "id": 6,
        "type": "scene",
        "vo": "teddy_sc5_girl.mp3", 
        "text": "She Blushingly replied: I’ll take good care of it.", 
        "both": True, 
        "teddy": "received",
        "talking": "girl" # Direct speech
    },
    {
        "id": 7,
        "type": "scene",
        "vo": "teddy_sc6.mp3", 
        "text": "Some things aren’t given to be held.\nThey’re given to be taken care of.", 
        "both": True, # Girl leaves?
        "teddy": "received",
        "action": "leave" # Girl leaves
    },
    {
        "id": 8,
        "type": "final", 
        "vo": "teddy_sc_theme.mp3", 
        "text": "Teddy Day"
    }
]

FADE_DURATION = 1500

# --- UTILS ---

def draw_capsule(screen, color, p1, p2, radius):
    pygame.draw.line(screen, color, p1, p2, radius * 2)
    pygame.draw.circle(screen, color, (int(p1[0]), int(p1[1])), radius)
    pygame.draw.circle(screen, color, (int(p2[0]), int(p2[1])), radius)

def draw_teddy(screen, x, y, angle=0):
    scale = 1.0
    
    # Simple Teddy Bear drawing
    # Body
    body_color = (139, 100, 60) # Brown
    light_color = (205, 170, 125) # Light Tan
    
    # Create surface strictly for teddy to allow rotation easily
    w, h = 60, 70
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    
    # Position logic inside surf (centered x w/2)
    cx = w // 2
    
    # Ears
    pygame.draw.circle(surf, body_color, (cx - 15, 15), 10)
    pygame.draw.circle(surf, body_color, (cx + 15, 15), 10)
    
    # Head
    pygame.draw.circle(surf, body_color, (cx, 25), 18)
    # Snout
    pygame.draw.circle(surf, light_color, (cx, 28), 7)
    # Nose
    pygame.draw.circle(surf, (20, 10, 5), (cx, 26), 3)
    # Eyes
    pygame.draw.circle(surf, (10, 10, 10), (cx - 6, 22), 2)
    pygame.draw.circle(surf, (10, 10, 10), (cx + 6, 22), 2)
    
    # Body
    pygame.draw.ellipse(surf, body_color, (cx - 18, 38, 36, 30))
    # Belly patch
    pygame.draw.ellipse(surf, light_color, (cx - 10, 42, 20, 20))
    
    # Arms
    pygame.draw.ellipse(surf, body_color, (cx - 24, 40, 12, 10))
    pygame.draw.ellipse(surf, body_color, (cx + 12, 40, 12, 10))
    
    # Legs
    pygame.draw.ellipse(surf, body_color, (cx - 18, 60, 14, 10))
    pygame.draw.ellipse(surf, body_color, (cx + 4, 60, 14, 10))

    if angle != 0:
        surf = pygame.transform.rotate(surf, angle)
    
    rect = surf.get_rect(center=(x, y))
    screen.blit(surf, rect)

def draw_human(screen, x, y, is_woman=False, expression="neutral", breathing=0, 
               has_teddy=False, talking=False, force_hold_pose=False, virtual_time=0):
    scale = 0.78 if is_woman else 0.95
    
    # Colors - Teddy Day Outfits
    if is_woman:
        clothing_color = (245, 240, 230) # Soft Cozy Cream/Off-white sweater
        clothing_accent = (176, 196, 222) # Soft Blue skirt accent
    else:
        shirt_color = (100, 149, 237) # Cornflower Blue
        pants_color = (60, 60, 70) # Dark Grey
    
    HEAD_R = 30 * scale
    SHOULDER_W = (52 if is_woman else 68) * scale
    TORSO_H = (110 + breathing) * scale
    HIP_W = (56 if is_woman else 48) * scale
    LEG_L = 120 * scale
    
    base_x = x
    base_y = y - breathing * (0.3 if is_woman else 0.4)
    
    # Shadow
    pygame.draw.ellipse(screen, (190, 190, 190), (base_x - 55*scale, y - 10, 110*scale, 20))
    
    hips_y = base_y - LEG_L
    shoulder_y = hips_y - TORSO_H
    head_center_y = shoulder_y - 10*scale - HEAD_R
    
    # Legs / Pants
    if not is_woman:
        for side in [-1, 1]:
            lx = base_x + side * (HIP_W / 4)
            draw_capsule(screen, pants_color, (lx, hips_y), (lx, base_y), int(8*scale))
    
    # Torso
    if is_woman:
        dress_pts = [
            (base_x - SHOULDER_W/2, shoulder_y), (base_x + SHOULDER_W/2, shoulder_y),
            (base_x + HIP_W/2 + 20*scale, hips_y + 30*scale), (base_x - HIP_W/2 - 20*scale, hips_y + 30*scale)
        ]
        pygame.draw.polygon(screen, clothing_color, dress_pts)
        # Texture lines for knit effect
        for i in range(1, 4):
            ly = shoulder_y + i * 25 * scale
            pygame.draw.line(screen, (220, 215, 205), (base_x - SHOULDER_W/2 + i*2, ly), (base_x + SHOULDER_W/2 - i*2, ly), 1)
        pygame.draw.polygon(screen, (200, 195, 185), dress_pts, 2)
    else:
        shirt_pts = [
            (base_x - SHOULDER_W/2, shoulder_y), (base_x + SHOULDER_W/2, shoulder_y),
            (base_x + HIP_W/2, hips_y), (base_x - HIP_W/2, hips_y)
        ]
        pygame.draw.polygon(screen, shirt_color, shirt_pts)
        pygame.draw.polygon(screen, (100, 110, 90), shirt_pts, 2)
    
    # Legs (Skin)
    if not is_woman:
        for side in [-1, 1]:
            lx = base_x + side * (HIP_W / 4)
            pygame.draw.circle(screen, (255, 255, 255), (int(lx), int(base_y)), int(10*scale))
    else:
        # Skirt leg
        for side in [-1, 1]:
            lx = base_x + side * (HIP_W / 4)
            # Tights color maybe? No, skin.
            draw_capsule(screen, (255, 255, 255), (base_x + side*(HIP_W/4), hips_y + 30*scale), 
                        (lx, base_y), int(8*scale))

    # Arms
    arm_radius = 7 * scale
    l_hand_pos = (0,0) # Placeholder
    
    # Left Arm
    l_shoulder = (base_x - SHOULDER_W/2 - (5 if not is_woman else 0), shoulder_y + 10)
    
    # Check if arm should be in "holding" pose
    is_holding_pose = has_teddy or force_hold_pose
    
    if is_holding_pose:
        l_elbow = (base_x - SHOULDER_W/2 - 10, shoulder_y + 40*scale)
        l_hand = (base_x - 20, shoulder_y + 60*scale)
        draw_capsule(screen, (255, 255, 255), l_shoulder, l_elbow, int(arm_radius))
        draw_capsule(screen, (255, 255, 255), l_elbow, l_hand, int(arm_radius))
        l_hand_pos = l_hand
    else:
        l_hand = (base_x - SHOULDER_W/2 - 5, shoulder_y + 95*scale)
        draw_capsule(screen, (255, 255, 255), l_shoulder, l_hand, int(arm_radius))
    
    # Right Arm
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
    if talking:
        talk_h = 4 + math.sin(virtual_time * 0.02) * 4
        pygame.draw.ellipse(screen, (40, 40, 40), (base_x - 4, m_y - talk_h/2, 8, max(2, talk_h)))
    elif expression == "smile":
        pygame.draw.arc(screen, (40, 40, 40), (int(base_x-10), int(m_y-5), 20, 10), math.pi, 0, 2)
    elif expression == "blush":
        # Smile + Blush cheeks
        pygame.draw.arc(screen, (40, 40, 40), (int(base_x-10), int(m_y-5), 20, 10), math.pi, 0, 2)
        pygame.draw.circle(screen, (255, 180, 180), (int(base_x - 12*scale), int(m_y + 5)), 5*scale)
        pygame.draw.circle(screen, (255, 180, 180), (int(base_x + 12*scale), int(m_y + 5)), 5*scale)
    else:
        pygame.draw.line(screen, (40, 40, 40), (base_x-4, m_y), (base_x+4, m_y), 2)

    # Hair / Bow (Girl)
    if is_woman:
        bow_x, bow_y = base_x + 22*scale, head_center_y - 25*scale
        pygame.draw.ellipse(screen, (100, 149, 237), (bow_x-12, bow_y-6, 10, 12)) # Cornflower blue bow
        pygame.draw.ellipse(screen, (100, 149, 237), (bow_x+2, bow_y-6, 10, 12))
        pygame.draw.circle(screen, (70, 130, 180), (int(bow_x), int(bow_y)), 4)
    
    if has_teddy:
        draw_teddy(screen, int(l_hand_pos[0]), int(l_hand_pos[1]))

    return l_hand_pos

# --- APP CONTROLLER ---

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

class App:
    def __init__(self):
        self.audio = AudioController()
        self.state = "INIT"
        self.current_scene_idx = -1
        self.scene_start_time = 0
        self.transition_start_time = 0
        self.fade_alpha = 0
        self.running = True
        self.clock = pygame.time.Clock()
        self.paused = False
        self.audio_finished_time = 0 # Track completion
        
        # Video Capture State
        self.frames = []
        self.frame_count = 0
        self.virtual_time = 0.0 # ms (float for precision)
        self.fps = 60
        
        # To rebuild audio track
        self.scene_audio_events = [] # list of (start_ms, audio_filename)
        self.current_audio_duration = 0
        
        # Positions
        self.boy_x = WIDTH * 0.42
        self.girl_x = WIDTH * 0.58
        
    def next_scene(self):
        self.current_scene_idx += 1
        if self.current_scene_idx >= len(SCENES):
            self.running = False
            return
        
        self.state = "FADE_IN"
        self.scene_start_time = self.virtual_time
        self.transition_start_time = self.virtual_time
        self.audio_finished_time = 0
        
        scene = SCENES[self.current_scene_idx]
        if "vo" in scene:
            self.current_audio_duration = self.audio.play(scene["vo"])
            self.scene_audio_events.append((self.virtual_time, scene["vo"]))
        else:
            self.current_audio_duration = 0
            
    def update(self):
        now = self.virtual_time
        if self.current_scene_idx == -1:
            self.next_scene()
            return

        scene = SCENES[self.current_scene_idx]
        
        # FADE LOGIC
        if self.state == "FADE_IN":
            elapsed = now - self.transition_start_time
            self.fade_alpha = max(0, 255 - int(255 * (elapsed / FADE_DURATION)))
            if elapsed > FADE_DURATION:
                self.state = "PLAYING"
                self.fade_alpha = 0
        
        elif self.state == "PLAYING":
            is_finished = False
            
            # Post Audio Delay Logic
            post_audio_delay = 1500
            if scene.get("talking") in ["boy", "girl"]:
                 post_audio_delay = 2000

            # Determine audio status - Use virtual time for sync
            elapsed_in_scene = now - self.scene_start_time
            audio_playing_virtual = elapsed_in_scene < self.current_audio_duration
            
            # Minimal safety time
            min_time_safety = (elapsed_in_scene > 1000)
            
            if not audio_playing_virtual and min_time_safety:
                if self.audio_finished_time == 0:
                    self.audio_finished_time = now
                
                if now - self.audio_finished_time > post_audio_delay:
                    is_finished = True
            
            # Special case for transfer scene (animation duration)
            if scene.get("teddy") == "transferring":
                anim_dur = scene.get("duration", 2500)
                if now - self.scene_start_time < anim_dur:
                    is_finished = False # wait for anim even if audio ends fast
            
            if is_finished:
                self.state = "FADE_OUT"
                self.transition_start_time = now
        
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
        
        # Calculate Boy/Girl Talking state (mouth animation) - Use virtual time
        elapsed_in_scene = now - self.scene_start_time
        is_playing_virtual = elapsed_in_scene < self.current_audio_duration
        boy_talks = is_playing_virtual and scene.get("talking") == "boy"
        girl_talks = is_playing_virtual and scene.get("talking") == "girl"
        
        if scene.get("type") in ["theme", "intro", "final"] and "boy" not in scene: # Simple text screens
             # Text Only Mode (or final)
             # But prompt says Scene 1 is theme, Scene 2 is 'Where they are now' with Boy.
             # Scene 0 is theme.
            text = scene["text"]
            lines = text.split("\n")
            total_height = len(lines) * 60
            start_y = (HEIGHT - total_height) // 2
            f = title_font if scene["type"] == "final" else subtitle_font
            
            for i, line in enumerate(lines):
                surf = f.render(line, True, TEXT_COLOR)
                r = surf.get_rect(center=(WIDTH//2, start_y + i*60))
                screen.blit(surf, r)
        else:
            # Character Mode
            teddy_state = scene.get("teddy")
            
            # Action: Leave
            girl_x_draw = self.girl_x
            if scene.get("action") == "leave":
                elapsed = now - self.scene_start_time
                # Girl moves right
                girl_x_draw += elapsed * 0.1
            
            start_pos = (0, 0)
            end_pos = (0, 0)

            # Draw Boy
            if scene.get("boy") or scene.get("both"):
                # Boy holds teddy only if transferring
                has_teddy_boy = (teddy_state == "transferring")
                force_hold_boy = (teddy_state == "transferring")
                
                # If transferring, we manually draw teddy, so pass false for has_teddy, but true for pose
                pos = draw_human(screen, self.boy_x, HEIGHT*0.8, is_woman=False, breathing=breath, 
                           has_teddy=False, talking=boy_talks, force_hold_pose=force_hold_boy, virtual_time=now)
                if force_hold_boy: start_pos = pos
            
            # Draw Girl
            if scene.get("girl") or scene.get("both"):
                # Girl expressions
                girl_expr = "neutral"
                if teddy_state == "received": girl_expr = "blush" # "Glow with smile"
                
                has_teddy_girl = (teddy_state == "received")
                force_hold_girl = (teddy_state == "transferring") or has_teddy_girl
                
                # If transferring, we manually draw teddy
                pos = draw_human(screen, girl_x_draw, HEIGHT*0.8, is_woman=True, breathing=breath,
                           expression=girl_expr, has_teddy=has_teddy_girl, talking=girl_talks, force_hold_pose=force_hold_girl, virtual_time=now)
                if force_hold_girl: end_pos = pos
            
            # Draw Transfer Animation
            if teddy_state == "transferring":
                elapsed = now - self.scene_start_time
                duration = scene.get("duration", 2500)
                progress = min(1.0, elapsed / duration)
                
                if start_pos == (0,0): start_pos = (self.boy_x - 20, HEIGHT*0.8 - 140)
                if end_pos == (0,0): end_pos = (self.girl_x - 20, HEIGHT*0.8 - 140)
                
                cur_x = start_pos[0] + (end_pos[0] - start_pos[0]) * progress
                cur_y = start_pos[1] + (end_pos[1] - start_pos[1]) * progress
                
                draw_teddy(screen, cur_x, cur_y)

            # Intro text for scene 1 (Boy alone text?)
            # No, text is handled by subtitle logic below.
            
            # Draw Subtitles
            if scene.get("text"):
                lines = scene["text"].split("\n")
                start_y = HEIGHT - 80
                for i, line in enumerate(lines):
                    surf = subtitle_font.render(line, True, TEXT_COLOR)
                    r = surf.get_rect(center=(WIDTH//2, start_y + i*40))
                    screen.blit(surf, r)

        # 2. Draw Fade Overlay
        if self.fade_alpha > 0:
            fade_s = pygame.Surface((WIDTH, HEIGHT))
            fade_s.fill(BG_COLOR)
            fade_s.set_alpha(self.fade_alpha)
            screen.blit(fade_s, (0,0))

        pygame.display.flip()
        
        # Capture Frame
        frame_data = pygame.surfarray.array3d(screen)
        # Transpose from (W, H, 3) to (H, W, 3) for moviepy
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

        # Final Export
        self.export_video()
        
        pygame.quit()
        sys.exit()

    def export_video(self):
        print("Exporting video... please wait.")
        # Create video clip from frames
        video_clip = ImageSequenceClip(self.frames, fps=self.fps)
        
        # Load and sync audio
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
        
        # Write file
        output_path = os.path.join(BASE_DIR, "output.mp4")
        video_clip.write_videofile(output_path, fps=self.fps, codec="libx264", audio_codec="aac")
        print(f"Export complete: {output_path}")

if __name__ == "__main__":
    print("\n--- Teddy Day Story Export ---")
    print("NOTE: On-screen playback will lag during frame capture. This is normal.")
    print("The final 'output.mp4' will have perfect synchronization.\n")
    app = App()
    app.run_loop()
