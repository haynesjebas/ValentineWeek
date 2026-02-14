#!/usr/bin/env python3
"""
Chocolate Day - Valentine's Week Day 3
Theme: Comfort after clarity
Strict State Machine Implementation & Audio Sync
"""

import pygame
import math
import sys
import os
import numpy as np
from moviepy import ImageSequenceClip, AudioFileClip, CompositeAudioClip

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
        "vo": "choc_sc0.mp3", 
        "text": "Rose Day showed intention.\nPropose Day brings clarity and courage."
    },
    {
        "id": 1,
        "type": "intro", 
        "vo": "choc_sc1.mp3", 
        "text": "Not every day needs courage.\nSome days need comfort."
    },
    {
        "id": 2,
        "type": "scene",
        "vo": "choc_sc2.mp3", 
        "text": "After saying what mattered,\nhe didn't feel the need to prove anything.", 
        "boy": True
        # "talking": "boy" Removed as requested - narrator speaks here
    },
    {
        "id": 3,
        "type": "scene",
        "vo": "choc_sc3.mp3", 
        "text": "This wasn't about a gesture.\nIt was about sharing something ordinary.", 
        "boy": True
    },
    {
        "id": 4,
        "type": "scene",
        "vo": "choc_sc4.mp3", 
        "text": "She noticed the shift.\nThis wasn't effort. This was ease.", 
        "girl": True
    },
    {
        "id": 5,
        "type": "scene",
        "vo": "choc_sc5.mp3", 
        "text": "He said: I thought you might like this.", 
        "both": True, 
        "chocolate": "transferring",
        "talking": "boy", # Direct speech
        "duration": 2500 # Duration for transfer interpolation
    },
    # Scene 6 merged into 5
    {
        "id": 6,
        "type": "scene",
        "vo": "choc_sc7.mp3", 
        "text": "Some connections grow louder.\nOthers grow easier.", 
        "both": True, 
        "chocolate": "received"
    },
    {
        "id": 7,
        "type": "scene",
        "vo": "choc_sc8.mp3", 
        "text": "Chocolate Day isn't about sweetness.\nIt's about choosing comfort after honesty."
        # Characters removed as requested
    },
    {
        "id": 8,
        "type": "final", 
        "vo": "choc_sc9.mp3", 
        "text": "Chocolate Day"
    }
]

FADE_DURATION = 1500

# --- UTILS ---

def ease_in_out(t):
    return t * t * (3 - 2 * t)

def draw_capsule(screen, color, p1, p2, radius):
    pygame.draw.line(screen, color, p1, p2, radius * 2)
    pygame.draw.circle(screen, color, (int(p1[0]), int(p1[1])), radius)
    pygame.draw.circle(screen, color, (int(p2[0]), int(p2[1])), radius)

def draw_chocolate(screen, x, y, angle=0):
    w, h = 30, 20
    choc_rect = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(choc_rect, (139, 69, 19), (0, 0, w, h), border_radius=3)
    pygame.draw.rect(choc_rect, (101, 51, 15), (0, 0, w, h), 2, border_radius=3)
    pygame.draw.line(choc_rect, (160, 90, 40), (5, 3), (w-5, 3), 1)
    pygame.draw.line(choc_rect, (160, 90, 40), (5, h-3), (w-5, h-3), 1)
    
    if angle != 0:
        choc_rect = pygame.transform.rotate(choc_rect, angle)
    
    rect = choc_rect.get_rect(center=(x, y))
    screen.blit(choc_rect, rect)

def draw_human(screen, x, y, is_woman=False, expression="neutral", breathing=0, 
               has_chocolate=False, step_offset=0, talking=False, force_hold_pose=False):
    scale = 0.78 if is_woman else 0.95
    
    # Colors
    if is_woman:
        clothing_color = (230, 190, 220)
        clothing_accent = (210, 170, 200)
    else:
        shirt_color = (200, 210, 220)
        pants_color = (60, 70, 90)
    
    HEAD_R = 30 * scale
    SHOULDER_W = (52 if is_woman else 68) * scale
    TORSO_H = (110 + breathing) * scale
    HIP_W = (56 if is_woman else 48) * scale
    LEG_L = 120 * scale
    
    base_x = x + (step_offset if is_woman else 0)
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
        pygame.draw.polygon(screen, clothing_accent, dress_pts, 2)
    else:
        shirt_pts = [
            (base_x - SHOULDER_W/2, shoulder_y), (base_x + SHOULDER_W/2, shoulder_y),
            (base_x + HIP_W/2, hips_y), (base_x - HIP_W/2, hips_y)
        ]
        pygame.draw.polygon(screen, shirt_color, shirt_pts)
        pygame.draw.polygon(screen, (180, 190, 200), shirt_pts, 2)
    
    # Legs (Skin)
    if not is_woman:
        for side in [-1, 1]:
            lx = base_x + side * (HIP_W / 4)
            pygame.draw.circle(screen, (255, 255, 255), (int(lx), int(base_y)), int(10*scale))
    else:
        for side in [-1, 1]:
            lx = base_x + side * (HIP_W / 4)
            draw_capsule(screen, (255, 255, 255), (base_x + side*(HIP_W/4), hips_y + 30*scale), 
                        (lx, base_y), int(8*scale))

    # Arms
    arm_radius = 7 * scale
    l_hand_pos = (0,0) # Placeholder
    
    # Left Arm
    l_shoulder = (base_x - SHOULDER_W/2 - (5 if not is_woman else 0), shoulder_y + 10)
    
    # Check if arm should be in "holding" pose
    is_holding_pose = has_chocolate or force_hold_pose
    
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
    # Simpler mouth movement synchronized with generally "on" state
        talk_h = 4 + math.sin(pygame.time.get_ticks() * 0.02) * 4
        pygame.draw.ellipse(screen, (40, 40, 40), (base_x - 4, m_y - talk_h/2, 8, max(2, talk_h)))
    elif expression == "smile":
        pygame.draw.arc(screen, (40, 40, 40), (int(base_x-10), int(m_y-5), 20, 10), math.pi, 0, 2)
    else:
        pygame.draw.line(screen, (40, 40, 40), (base_x-4, m_y), (base_x+4, m_y), 2)

    if is_woman:
        bow_x, bow_y = base_x + 22*scale, head_center_y - 25*scale
        pygame.draw.ellipse(screen, (255, 120, 170), (bow_x-12, bow_y-6, 10, 12))
        pygame.draw.ellipse(screen, (255, 120, 170), (bow_x+2, bow_y-6, 10, 12))
        pygame.draw.circle(screen, (200, 50, 100), (int(bow_x), int(bow_y)), 4)
    
    if has_chocolate:
        draw_chocolate(screen, int(l_hand_pos[0]), int(l_hand_pos[1]))

    return l_hand_pos # Return hand pos if needed for animation start

# --- APP CONTROLLER ---

class AudioController:
    def __init__(self):
        pygame.mixer.init()
        self.vo_channel = pygame.mixer.Channel(0)
    
    def play(self, filename):
        path = os.path.join(AUDIO_DIR, filename)
        if not os.path.exists(path):
            print(f"ERROR: Audio file not found: {path}")
            return
        try:
            sound = pygame.mixer.Sound(path)
            self.vo_channel.play(sound)
        except Exception as e:
            print(f"Error playing sound {path}: {e}")

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
        self.audio_finished_time = 0
        self.frames = []
        self.audio_events = []
        self.fps = 60
        
    def next_scene(self):
        self.current_scene_idx += 1
        if self.current_scene_idx >= len(SCENES):
            self.running = False
            return
        
        self.state = "FADE_IN"
        self.scene_start_time = pygame.time.get_ticks()
        self.transition_start_time = pygame.time.get_ticks()
        self.audio_finished_time = 0
        
        scene = SCENES[self.current_scene_idx]
        if "vo" in scene:
            self.audio.play(scene["vo"])
            # Record audio event with the current frame index for syncing
            self.audio_events.append({
                "filename": scene["vo"],
                "frame_index": len(self.frames)
            })
            
    def update(self):
        now = pygame.time.get_ticks()
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
            # Check completion condition
            is_finished = False
            
            if scene.get("silent"):
                # Time-based for silent scene
                if now - self.scene_start_time > scene.get("duration", 3000):
                    is_finished = True
            else:
                # Audio-based
                # Slow down the pace: wait for narration to finish AND some minimum time
                # Delay after audio finishes
                post_audio_delay = 1500 # Default delay after speech
                
                # Extra delay for boy speaking scene to let it sink in
                if scene.get("talking") == "boy":
                     post_audio_delay = 2000

                if not self.audio.is_playing() and (now - self.scene_start_time > 1000):
                     # Check if we've waited enough since audio started (min duration)
                     # But better: check if we've waited enough since audio FINISHED.
                     # However, current logic only tracks scene_start_time.
                     # Let's use a simpler heuristic: Minimum scene length = Audio + Delay
                     # The (now - start > 1000) was just a safety pad.
                     
                     # We can't know exactly when audio stopped without a flag, 
                     # but we can just ensure the TOTAL scene time is long enough.
                     # Given we don't know audio length easily here, let's just 
                     # add a generous check.
                     
                     # Better approach: If audio is done, start a timer?
                     # Since we don't have a "audio_finished_time" variable in this scope easily without adding state,
                     # we will rely on the fact that if audio is NOT playing, we are in the "tail" of the scene.
                     # But this loop runs every frame.
                     # To properly implement "wait X seconds AFTER audio", we need to track when audio stopped.
                     pass 
                
                # REVISED LOGIC:
                # We need to know when audio stopped to add a precise delay. 
                # OR we just rely on "Audio IS NOT playing" being true + ensuring we don't skip instantly.
                # If we just use `if not self.audio.is_playing():`, it happens instantly on finish.
                # We need a hold timer.
                
                if self.audio.is_playing():
                    self.audio_finished_time = 0 # Reset
                else: 
                    if self.audio_finished_time == 0:
                        self.audio_finished_time = now # Mark finish time
                    
                    if now - self.audio_finished_time > post_audio_delay:
                        is_finished = True
            
            if is_finished:
                self.state = "FADE_OUT"
                self.transition_start_time = now
        
        elif self.state == "FADE_OUT":
            elapsed = now - self.transition_start_time
            self.fade_alpha = min(255, int(255 * (elapsed / FADE_DURATION)))
            
            # If fade out is done, move to next scene
            if elapsed > FADE_DURATION:
                self.next_scene()

    def draw(self):
        screen.fill(BG_COLOR)
        scene = SCENES[self.current_scene_idx]
        
        # 1. Draw Characters
        bx, gx = WIDTH * 0.42, WIDTH * 0.58
        now = pygame.time.get_ticks()
        breath = math.sin(now * 0.002) * 3
        
        # Calculate Boy/Girl Talking state
        is_playing = self.audio.is_playing()
        boy_talks = is_playing and scene.get("talking") == "boy"
        
        if scene.get("type") in ["theme", "intro", "final"]:
            # Text Only Mode
            text = scene["text"]
            lines = text.split("\n")
            # Center text
            total_height = len(lines) * 60
            start_y = (HEIGHT - total_height) // 2
            f = title_font if scene["type"] == "final" else subtitle_font
            
            for i, line in enumerate(lines):
                surf = f.render(line, True, TEXT_COLOR)
                r = surf.get_rect(center=(WIDTH//2, start_y + i*60))
                screen.blit(surf, r)
        else:
            # Character Mode
            choc_state = scene.get("chocolate")
            
            start_pos = (0, 0)
            end_pos = (0, 0)

            # Draw Boy
            if scene.get("boy") or scene.get("both"):
                has_choc_boy = (choc_state in ["in_hand", "looking", "offering"])
                # Boy keeps arm up during transfer
                force_hold_boy = (choc_state == "transferring")
                
                pos = draw_human(screen, bx, HEIGHT*0.8, is_woman=False, breathing=breath, 
                           has_chocolate=has_choc_boy, talking=boy_talks, force_hold_pose=force_hold_boy)
                if force_hold_boy: start_pos = pos
            
            # Draw Girl
            if scene.get("girl") or scene.get("both"):
                girl_expr = "smile" if choc_state == "received" else "neutral"
                has_choc_girl = (choc_state == "received")
                # Girl raises arm to receive
                force_hold_girl = (choc_state == "transferring")
                
                pos = draw_human(screen, gx, HEIGHT*0.8, is_woman=True, breathing=breath,
                           expression=girl_expr, has_chocolate=has_choc_girl, force_hold_pose=force_hold_girl)
                if force_hold_girl: end_pos = pos
            
            # Draw Transfer Animation
            if choc_state == "transferring":
                # We need smooth interpolation
                elapsed = now - self.scene_start_time
                duration = scene.get("duration", 3000)
                progress = min(1.0, elapsed / duration)
                
                # Use captured positions from real draw calls
                # fallback if 0,0
                if start_pos == (0,0): start_pos = (bx - 20, HEIGHT*0.8 - 140)
                if end_pos == (0,0): end_pos = (gx - 20, HEIGHT*0.8 - 140)
                
                cur_x = start_pos[0] + (end_pos[0] - start_pos[0]) * progress
                cur_y = start_pos[1] + (end_pos[1] - start_pos[1]) * progress
                
                draw_chocolate(screen, cur_x, cur_y)

            # Draw Subtitles (always if text present)
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

    def run_loop(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                    if self.paused: self.audio.vo_channel.pause()
                    else: self.audio.vo_channel.unpause()
            
            if not self.paused:
                self.update()
                self.draw()
                
                # Capture frame
                frame_data = pygame.surfarray.array3d(screen)
                # Pygame uses (width, height, rgb), MoviePy expects (height, width, rgb)
                # and Pygame's array3d returns transposed (x, y, rgb)
                frame_data = np.transpose(frame_data, (1, 0, 2))
                self.frames.append(frame_data)
            
            self.clock.tick(self.fps)
            
        self.export_video()
        pygame.quit()
        sys.exit()

    def export_video(self):
        if not self.frames:
            print("No frames captured. Skipping video export.")
            return

        print(f"Exporting video ({len(self.frames)} frames) to output.mp4...")
        
        try:
            # Create video clip from frames
            clip = ImageSequenceClip(self.frames, fps=self.fps)
            
            # Create audio clips for each event
            audio_clips = []
            for event in self.audio_events:
                audio_path = os.path.join(AUDIO_DIR, event["filename"])
                if os.path.exists(audio_path):
                    audio_clip = AudioFileClip(audio_path)
                    # Calculate start time based on frame index
                    start_time = event["frame_index"] / self.fps
                    audio_clip = audio_clip.with_start(start_time)
                    audio_clips.append(audio_clip)
            
            if audio_clips:
                composite_audio = CompositeAudioClip(audio_clips)
                clip = clip.with_audio(composite_audio)
            
            # Write file - libx264 is standard and compatible with web browsers
            # We use a preset like 'ultrafast' or 'medium' for speed/quality balance
            clip.write_videofile("output.mp4", codec="libx264", audio_codec="aac", fps=self.fps)
            print("Video export complete: output.mp4")
            
        except Exception as e:
            print(f"Error during video export: {e}")

if __name__ == "__main__":
    app = App()
    app.run_loop()
