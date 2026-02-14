import pygame
import sys
import os
import math
import numpy as np
from moviepy import ImageSequenceClip, AudioFileClip, CompositeAudioClip


# Constants
WIDTH, HEIGHT = 1280, 720
FPS = 60
FADE_DURATION = 1500
TEXT_COLOR = (45, 45, 45)
BG_COLOR = (211, 211, 211) # #D3D3D3 Light Grey

def ease_in_out(t):
    return 2*t*t if t < 0.5 else 1 - math.pow(-2*t + 2, 2) / 2

def draw_capsule(screen, color, p1, p2, radius):
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    dist = math.hypot(dx, dy)
    if dist == 0:
        pygame.draw.circle(screen, color, (int(p1[0]), int(p1[1])), radius)
        return
    pygame.draw.circle(screen, color, (int(p1[0]), int(p1[1])), radius)
    pygame.draw.circle(screen, color, (int(p2[0]), int(p2[1])), radius)
    angle = math.atan2(dy, dx)
    perp_angle = angle + math.pi / 2
    pts = [
        (p1[0] + radius * math.cos(perp_angle), p1[1] + radius * math.sin(perp_angle)),
        (p2[0] + radius * math.cos(perp_angle), p2[1] + radius * math.sin(perp_angle)),
        (p2[0] - radius * math.cos(perp_angle), p2[1] - radius * math.sin(perp_angle)),
        (p1[0] - radius * math.cos(perp_angle), p1[1] - radius * math.sin(perp_angle))
    ]
    pygame.draw.polygon(screen, color, pts)

def draw_thought_cloud(screen, x, y, scale=1.0):
    """Draw a thought cloud above character's head"""
    # Main cloud circles
    pygame.draw.circle(screen, (255, 255, 255), (int(x), int(y)), int(18 * scale))
    pygame.draw.circle(screen, (255, 255, 255), (int(x - 15 * scale), int(y - 5)), int(14 * scale))
    pygame.draw.circle(screen, (255, 255, 255), (int(x + 15 * scale), int(y - 5)), int(14 * scale))
    pygame.draw.circle(screen, (255, 255, 255), (int(x), int(y - 15)), int(12 * scale))
    
    # Small bubbles connecting to head
    pygame.draw.circle(screen, (255, 255, 255), (int(x - 10), int(y + 25)), int(5 * scale))
    pygame.draw.circle(screen, (255, 255, 255), (int(x - 15), int(y + 35)), int(3 * scale))
    
    # Outlines
    pygame.draw.circle(screen, (200, 200, 200), (int(x), int(y)), int(18 * scale), 1)
    pygame.draw.circle(screen, (200, 200, 200), (int(x - 15 * scale), int(y - 5)), int(14 * scale), 1)
    pygame.draw.circle(screen, (200, 200, 200), (int(x + 15 * scale), int(y - 5)), int(14 * scale), 1)
    pygame.draw.circle(screen, (200, 200, 200), (int(x), int(y - 15)), int(12 * scale), 1)
    pygame.draw.circle(screen, (200, 200, 200), (int(x - 10), int(y + 25)), int(5 * scale), 1)
    pygame.draw.circle(screen, (200, 200, 200), (int(x - 15), int(y + 35)), int(3 * scale), 1)

def draw_human(screen, x, y, is_woman=False, expression="neutral", 
               breathing=0, note_state="hidden", note_open=False, step_offset=0, talking=False, facing="side"):
    # Proportions: Refined Human Aesthetic
    # Refinement: Woman is significantly shorter than the boy
    scale = 0.95 if not is_woman else 0.78 
    base_x = x + step_offset
    
    HEAD_R = 30 * scale
    NECK_H = 10 * scale
    SHOULDER_W = 65 * scale if not is_woman else 50 * scale
    TORSO_H = 110 * scale + (breathing if not is_woman else breathing * 0.8)
    HIP_W = 45 * scale if not is_woman else 55 * scale
    LEG_L = 120 * scale
    
    pygame.draw.ellipse(screen, (190, 190, 190), (base_x - 60*scale, y - 10, 120*scale, 20))
    
    hips_y = y - LEG_L
    shoulder_y = hips_y - TORSO_H
    head_center_y = shoulder_y - NECK_H - HEAD_R
    
    # Torso
    torso_pts = [(base_x-SHOULDER_W/2, shoulder_y), (base_x+SHOULDER_W/2, shoulder_y), 
                 (base_x+HIP_W/2, hips_y), (base_x-HIP_W/2, hips_y)]
    pygame.draw.polygon(screen, (255, 255, 255), torso_pts)
    pygame.draw.polygon(screen, (240, 240, 240), torso_pts, 2)
    
    # Head
    pygame.draw.circle(screen, (255, 255, 255), (int(base_x), int(head_center_y)), int(HEAD_R))
    pygame.draw.circle(screen, (240, 240, 240), (int(base_x), int(head_center_y)), int(HEAD_R), 2)
    
    # Arms
    arm_radius = 7 * scale
    l_shoulder = (base_x - SHOULDER_W/2 + 5, shoulder_y + 10)
    if note_state != "hidden" and not is_woman:
        l_hand = (base_x - 25*scale, hips_y - 20)
        l_elbow = (base_x - 45*scale, (l_shoulder[1] + l_hand[1])/2 + 15)
        draw_capsule(screen, (255, 255, 255), l_shoulder, l_elbow, int(arm_radius))
        draw_capsule(screen, (255, 255, 255), l_elbow, l_hand, int(arm_radius))
        nw, nh = (40*scale, 30*scale) if note_open else (25*scale, 18*scale)
        pygame.draw.rect(screen, (255, 255, 255), (l_hand[0]-nw/2, l_hand[1]-nh/2, nw, nh))
        pygame.draw.rect(screen, (180, 180, 180), (l_hand[0]-nw/2, l_hand[1]-nh/2, nw, nh), 1)
    else:
        l_hand = (base_x - SHOULDER_W/2 - 8, shoulder_y + 90*scale)
        draw_capsule(screen, (255, 255, 255), l_shoulder, l_hand, int(arm_radius))
    
    r_shoulder = (base_x + SHOULDER_W/2 - 5, shoulder_y + 10)
    r_hand = (base_x + SHOULDER_W/2 + 8, shoulder_y + 90*scale)
    draw_capsule(screen, (255, 255, 255), r_shoulder, r_hand, int(arm_radius))
    
    # Legs
    leg_radius = 8 * scale
    draw_capsule(screen, (255, 255, 255), (base_x-HIP_W/4-2, hips_y), (base_x-HIP_W/4-4, y), int(leg_radius))
    draw_capsule(screen, (255, 255, 255), (base_x+HIP_W/4+2, hips_y), (base_x+HIP_W/4+4, y), int(leg_radius))
    
    # Face
    eye_x, eye_y = 10 * scale, -HEAD_R/5
    for sx in [-1, 1]:
        pygame.draw.circle(screen, (40, 40, 40), (int(base_x + sx * eye_x), int(head_center_y + eye_y)), 3)
    
    m_y = head_center_y + HEAD_R/2
    if talking:
        # Mouth movement: small oval that opens/closes
        talk_h = 4 + math.sin(pygame.time.get_ticks() * 0.02) * 4
        pygame.draw.ellipse(screen, (40, 40, 40), (base_x - 4, m_y - talk_h/2, 8, max(2, talk_h)))
    elif expression == "smile":
        pygame.draw.arc(screen, (40, 40, 40), (int(base_x-10), int(m_y-5), 20, 10), math.pi, 0, 2)
    else:
        pygame.draw.line(screen, (40, 40, 40), (base_x-4, m_y), (base_x+4, m_y), 2)

    if is_woman:
        # Ribbon bow on the side of her head
        bow_x, bow_y = base_x + 22*scale, head_center_y - 25*scale
        # Left loop
        pygame.draw.ellipse(screen, (255, 120, 170), (bow_x-12, bow_y-6, 10, 12))
        # Right loop
        pygame.draw.ellipse(screen, (255, 120, 170), (bow_x+2, bow_y-6, 10, 12))
        # Center knot
        pygame.draw.circle(screen, (200, 50, 100), (int(bow_x), int(bow_y)), 4)

def draw_human_front(screen, x, y, is_woman=False, expression="neutral", 
                     breathing=0, walk_phase=0):
    """Draw human facing forward (toward camera) with walking animation"""
    scale = 0.78 if is_woman else 0.95
    
    HEAD_R = 30 * scale
    TORSO_H = 110 * scale + breathing
    SHOULDER_W = 65 * scale if not is_woman else 50 * scale
    HIP_W = 45 * scale if not is_woman else 55 * scale
    LEG_L = 120 * scale
    
    # Shadow
    pygame.draw.ellipse(screen, (190, 190, 190), (x - 60*scale, y - 10, 120*scale, 20))
    
    hips_y = y - LEG_L
    shoulder_y = hips_y - TORSO_H
    head_center_y = shoulder_y - 10*scale - HEAD_R
    
    # Walking leg animation
    leg_offset = math.sin(walk_phase) * 15
    left_knee_x = x - HIP_W/4 + leg_offset
    right_knee_x = x + HIP_W/4 - leg_offset
    left_foot_x = x - HIP_W/4 + leg_offset * 1.5
    right_foot_x = x + HIP_W/4 - leg_offset * 1.5
    knee_y = (hips_y + y) / 2
    
    # Legs (with walking motion)
    leg_radius = 8 * scale
    draw_capsule(screen, (255, 255, 255), (x - HIP_W/4, hips_y), (left_knee_x, knee_y), int(leg_radius))
    draw_capsule(screen, (255, 255, 255), (left_knee_x, knee_y), (left_foot_x, y), int(leg_radius))
    draw_capsule(screen, (255, 255, 255), (x + HIP_W/4, hips_y), (right_knee_x, knee_y), int(leg_radius))
    draw_capsule(screen, (255, 255, 255), (right_knee_x, knee_y), (right_foot_x, y), int(leg_radius))
    
    # Torso (front view - rectangular)
    torso_pts = [(x-SHOULDER_W/2, shoulder_y), (x+SHOULDER_W/2, shoulder_y), 
                 (x+HIP_W/2, hips_y), (x-HIP_W/2, hips_y)]
    pygame.draw.polygon(screen, (255, 255, 255), torso_pts)
    pygame.draw.polygon(screen, (240, 240, 240), torso_pts, 2)
    
    # Arms (hanging down in front view)
    arm_radius = 7 * scale
    l_shoulder = (x - SHOULDER_W/2, shoulder_y + 10)
    l_hand = (x - SHOULDER_W/2 - 5, shoulder_y + 90*scale)
    draw_capsule(screen, (255, 255, 255), l_shoulder, l_hand, int(arm_radius))
    
    r_shoulder = (x + SHOULDER_W/2, shoulder_y + 10)
    r_hand = (x + SHOULDER_W/2 + 5, shoulder_y + 90*scale)
    draw_capsule(screen, (255, 255, 255), r_shoulder, r_hand, int(arm_radius))
    
    # Head (front view)
    pygame.draw.circle(screen, (255, 255, 255), (int(x), int(head_center_y)), int(HEAD_R))
    pygame.draw.circle(screen, (240, 240, 240), (int(x), int(head_center_y)), int(HEAD_R), 2)
    
    # Face (front view - symmetrical)
    eye_x = 12 * scale
    eye_y = head_center_y - 8 * scale
    pygame.draw.circle(screen, (40, 40, 40), (int(x - eye_x), int(eye_y)), 3)
    pygame.draw.circle(screen, (40, 40, 40), (int(x + eye_x), int(eye_y)), 3)
    
    m_y = head_center_y + HEAD_R/2 - 5
    if expression == "smile":
        pygame.draw.arc(screen, (40, 40, 40), (int(x-12), int(m_y-5), 24, 12), math.pi, 0, 2)
    else:
        pygame.draw.line(screen, (40, 40, 40), (x-6, m_y), (x+6, m_y), 2)
    
    # Bow (centered on top of head for front view)
    if is_woman:
        bow_x, bow_y = x, head_center_y - HEAD_R - 5
        # Left loop
        pygame.draw.ellipse(screen, (255, 120, 170), (bow_x-12, bow_y-6, 10, 12))
        # Right loop
        pygame.draw.ellipse(screen, (255, 120, 170), (bow_x+2, bow_y-6, 10, 12))
        # Center knot
        pygame.draw.circle(screen, (200, 50, 100), (int(bow_x), int(bow_y)), 4)

class AudioService:
    def __init__(self):
        pygame.mixer.init()
        self.vo_channel = pygame.mixer.Channel(1)
        self.current_subtitle = ""
        self.vo_ended = False
        self.played_segments = [] # List of (timestamp, file_path)

    def play_vo(self, file, text, start_time_ms):
        path = os.path.join("assets", "audio", file)
        if os.path.exists(path):
            self.vo_channel.play(pygame.mixer.Sound(path))
            self.played_segments.append((start_time_ms / 1000.0, path))
        self.current_subtitle = text
        self.vo_ended = False

    def update(self):
        if not self.vo_channel.get_busy(): self.vo_ended = True
    def is_finished(self): return self.vo_ended
    def pause(self): self.vo_channel.pause()
    def unpause(self): self.vo_channel.unpause()

class StoryApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Propose Day - Press [SPACE] to Pause")
        self.clock = pygame.time.Clock()
        self.audio = AudioService()
        try:
            self.font = pygame.font.SysFont("georgia", 30, italic=True)
            self.title_font = pygame.font.SysFont("georgia", 55)
        except:
            self.font = pygame.font.SysFont("serif", 30, italic=True)
            self.title_font = pygame.font.SysFont("serif", 55)
        self.scenes = [
            {"type": "theme", "text": "Rose Day showed intention.\nPropose Day brings clarity and courage."},
            {"vo": "h_sc1.mp3", "text": "After the rose was given, nothing was said.\nBut something had already been understood."},
            {"vo": "h_sc2.mp3", "text": "I’ve never known how to show love loudly.\nWords were the only place I felt honest.", "boy": True},
            {"vo": "h_sc3.mp3", "text": "She noticed the difference between silence and hesitation.\nThis was not hesitation.", "girl": True},
            {"vo": "h_sc4.mp3", "text": "I don't know how to impress you.\nBut I don't want to stand in your way; I want to stand with you, when you're ready.", "both": True},
            {"vo": "h_sc5.mp3", "text": "If one day you choose forever,\nI want to choose it with you.", "both": True},
            {"vo": "h_sc6.mp3", "text": "She didn’t answer him.\nShe let him know he was heard.", "both": True, "smile": True, "step": True},
            {"vo": "h_sc7.mp3", "text": "Propose Day is not about hearing yes.\nIt is about being brave enough to mean it.", "type": "final_resolution"}
        ]
        self.idx = 0
        self.start_ticks = pygame.time.get_ticks()
        self.init_ticks = self.start_ticks
        self.frames = []
        self.scene_hold_ticks = 0
        self.paused = False
        self.pause_start_ticks = 0
        self.fade_surface = pygame.Surface((WIDTH, HEIGHT))
        self.fade_surface.fill(BG_COLOR)
        if self.scenes[0].get("vo"): 
            self.audio.play_vo(self.scenes[0]["vo"], self.scenes[0]["text"], 0)

    def draw_subtitles(self, text=None, large=False):
        t = text if text else self.audio.current_subtitle
        if not t: return
        lines = t.split('\n')
        for i, line in enumerate(lines):
            f = self.title_font if large else self.font
            surf = f.render(line, True, TEXT_COLOR)
            y = HEIGHT//2 + i*65 if large else HEIGHT - 100 + i*40
            self.screen.blit(surf, surf.get_rect(center=(WIDTH//2, y)))

    def run(self):
        while self.idx <= len(self.scenes):
            for e in pygame.event.get():
                if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                    self.paused = not self.paused
                    if self.paused:
                        self.audio.pause()
                        self.pause_start_ticks = pygame.time.get_ticks()
                    else:
                        self.audio.unpause()
                        pause_duration = pygame.time.get_ticks() - self.pause_start_ticks
                        self.start_ticks += pause_duration
                        if self.scene_hold_ticks > 0: self.scene_hold_ticks += pause_duration

            if self.paused:
                self.clock.tick(FPS)
                continue

            ticks = pygame.time.get_ticks()
            elapsed = ticks - self.start_ticks
            if self.idx < len(self.scenes):
                scene = self.scenes[self.idx]
                self.audio.update()
                done = self.audio.is_finished() if scene.get("vo") else (elapsed > 5000)
                if done and self.scene_hold_ticks == 0: self.scene_hold_ticks = ticks
                if self.scene_hold_ticks > 0:
                    if ticks - self.scene_hold_ticks < 2000: done = False
                    else: done = True
                if done:
                    self.idx += 1; self.start_ticks = ticks; self.scene_hold_ticks = 0
                    if self.idx < len(self.scenes) and self.scenes[self.idx].get("vo"):
                        self.audio.play_vo(self.scenes[self.idx]["vo"], self.scenes[self.idx]["text"], ticks - self.init_ticks)
                    continue
                self.screen.fill(BG_COLOR)
                breath = math.sin(ticks * 0.002) * 3
                if scene.get("type") == "theme":
                    self.draw_subtitles(scene["text"], True)
                elif scene.get("type") == "final_resolution":
                    self.draw_subtitles()
                else:
                    bx, gx = WIDTH*0.42, WIDTH*0.58
                    breath = math.sin(ticks * 0.002) * 3
                    
                    if scene.get("boy"):
                        boy_talking = False  # Scene 2 is thoughts, not speech
                        draw_human(self.screen, bx+50, HEIGHT*0.8, note_state="folded", breathing=breath, talking=boy_talking)
                    elif scene.get("girl"):
                        draw_human(self.screen, gx-50, HEIGHT*0.8, is_woman=True, breathing=breath)
                    elif scene.get("both"):
                        # Scene 6: Girl turns and walks away (but smiling)
                        if self.idx == 6:
                            step = -min(80, (elapsed/5000)*80)  # Negative step = moving away, increased distance
                        elif self.idx > 6:
                            step = -80  # Keep the distance
                        else:
                            step = 0
                        
                        # Note Exchange Logic in Scene 4
                        note_to_girl = self.idx >= 4
                        note_progress = 0
                        if self.idx == 4:
                            # Move note from boy to girl during the confession
                            note_progress = min(1.0, elapsed / 4000) # Move over 4 seconds
                        elif self.idx > 4:
                            note_progress = 1.0 # Girl has it
                            
                        # Positions for note
                        boy_note_x, boy_note_y = bx + 20, HEIGHT*0.8 - 140
                        girl_note_x, girl_note_y = gx - 30, HEIGHT*0.8 - 130
                        
                        note_x = boy_note_x + (girl_note_x - boy_note_x) * note_progress
                        note_y = boy_note_y + (girl_note_y - boy_note_y) * note_progress
                        
                        # Mouth movement for Boy (when speaking in Scenes 4 & 5)
                        boy_talking = (self.idx in [4, 5]) and self.audio.vo_channel.get_busy() and not self.paused
                        
                        female_expression = "neutral"
                        if self.idx == 6:  # Only smile when leaving in Scene 6
                            female_expression = "smile"
                        
                        # Scene 6: Girl faces camera and walks away with smile
                        if self.idx == 6:
                            # Girl walks toward camera (away from boy) - she actually moves
                            walk_distance = min(80, (elapsed/5000)*80)  # Distance she moves away
                            walk_phase = (elapsed / 500) * math.pi  # Walking animation speed
                            draw_human(self.screen, bx, HEIGHT*0.8, note_state=("folded" if note_progress < 0.2 else "hidden"), 
                                       breathing=breath, talking=boy_talking)
                            # Girl moves toward right side of screen as she walks toward camera
                            draw_human_front(self.screen, gx + walk_distance, HEIGHT*0.8, is_woman=True, 
                                           expression=female_expression, breathing=breath, walk_phase=walk_phase)
                        else:
                            # Normal side view for other scenes
                            draw_human(self.screen, bx, HEIGHT*0.8, note_state=("folded" if note_progress < 0.2 else "hidden"), 
                                       breathing=breath, talking=boy_talking)
                            draw_human(self.screen, gx, HEIGHT*0.8, is_woman=True, breathing=breath, 
                                       step_offset=-step, expression=female_expression)
                        
                        # Draw the moving note
                        if 0.2 <= note_progress <= 1.0:
                            scale = 0.78 # Girl's scale
                            nw, nh = 25 * scale, 18 * scale
                            
                            # In Scene 6, note moves with the girl
                            if self.idx == 6:
                                walk_distance = min(80, (elapsed/5000)*80)
                                final_note_x = gx + walk_distance - 30
                                final_note_y = HEIGHT*0.8 - 130
                            else:
                                final_note_x = note_x
                                final_note_y = note_y
                            
                            pygame.draw.rect(self.screen, (255, 255, 255), 
                                           (final_note_x - nw/2, final_note_y - nh/2, nw, nh), border_radius=2)
                            pygame.draw.rect(self.screen, (200, 200, 200), 
                                           (final_note_x - nw/2, final_note_y - nh/2, nw, nh), 1, border_radius=2)

                    self.draw_subtitles()
            else:
                self.screen.fill(BG_COLOR)
                surf = self.title_font.render("Propose Day", True, TEXT_COLOR)
                self.screen.blit(surf, surf.get_rect(center=(WIDTH//2, HEIGHT//2)))
                if elapsed > 4000: break
            fade_a = 0
            if elapsed < FADE_DURATION: fade_a = int(255 * (1 - ease_in_out(elapsed / FADE_DURATION)))
            if self.scene_hold_ticks > 0:
                dt = ticks - self.scene_hold_ticks
                if dt > 1000: fade_a = int(255 * ease_in_out((dt-1000)/1000))
            if fade_a > 0:
                self.fade_surface.set_alpha(max(0, fade_a))
                self.screen.blit(self.fade_surface, (0, 0))
            
            # Capture frame for video export
            frame_data = pygame.surfarray.array3d(self.screen)
            frame_data = np.transpose(frame_data, (1, 0, 2)) # Transpose from (W, H, C) to (H, W, C)
            self.frames.append(frame_data)

            pygame.display.flip(); self.clock.tick(FPS)
        
        # Video Export Logic
        if self.frames:
            print("Exporting video... please wait.")
            video_clip = ImageSequenceClip(self.frames, fps=FPS)
            
            audio_clips = []
            for start_time, path in self.audio.played_segments:
                ac = AudioFileClip(path).with_start(start_time)
                audio_clips.append(ac)
            
            if audio_clips:
                final_audio = CompositeAudioClip(audio_clips)
                video_clip = video_clip.with_audio(final_audio)
            
            video_clip.write_videofile("output.mp4", codec="libx264", audio_codec="aac", fps=FPS)
            print("Export complete: output.mp4")

        pygame.quit()

if __name__ == "__main__": StoryApp().run()
