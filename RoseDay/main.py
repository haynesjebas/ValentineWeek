import pygame
import sys
import os
import math
import imageio
try:
    from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip
except ImportError:
    from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
import numpy as np

# Constants
WIDTH, HEIGHT = 1280, 720
FPS = 30
FADE_DURATION = 1500
MAX_TEXT_WIDTH = int(WIDTH * 0.8)
BOTTOM_MARGIN = 40

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
TEXT_COLOR = (30, 30, 30)

def ease_in_out(t):
    return 2*t*t if t < 0.5 else 1 - math.pow(-2*t + 2, 2) / 2

class AudioService:
    def __init__(self, base_dir):
        pygame.init()
        pygame.mixer.init()
        self.base_dir = base_dir
        self.vo_channel = pygame.mixer.Channel(1)
        self.vo_queue = []
        self.current_vo = None
        self.current_subtitle = ""
        self.audio_log = [] # (filepath, raw_ticks)

    def queue_vo_set(self, vo_sub_pairs):
        self.vo_queue = list(vo_sub_pairs)
        self.current_vo = None
        self.current_subtitle = ""

    def update(self):
        if not self.vo_channel.get_busy():
            if self.vo_queue:
                vo_file, text = self.vo_queue.pop(0)
                if vo_file:
                    path = os.path.join(self.base_dir, "assets", "audio", vo_file)
                    if os.path.exists(path):
                        sound = pygame.mixer.Sound(path)
                        self.vo_channel.play(sound)
                        self.audio_log.append((path, pygame.time.get_ticks()))
                self.current_vo = vo_file
                self.current_subtitle = text
            else:
                pass

    def is_finished(self):
        return len(self.vo_queue) == 0 and not self.vo_channel.get_busy()

class Scene:
    def __init__(self, vo_content=[]):
        self.vo_content = vo_content
    def start(self, audio):
        audio.queue_vo_set(self.vo_content)
    def update(self, audio):
        audio.update()
    def is_done(self, audio):
        return audio.is_finished()
    def draw(self, app, progress, elapsed):
        app.screen.fill(WHITE)

class Scene0(Scene): # Intro
    def draw(self, app, progress, elapsed):
        app.draw_background("background.png")

class Scene1(Scene): # Boy Intro
    def draw(self, app, progress, elapsed):
        app.draw_background("quiet_corridor.png")
        x = int(-200 + (400 + 200) * min(progress * 1.5, 1.0))
        app.draw_character("boy.png", x, HEIGHT - 100, scale=0.6, flip=False)

class Scene2(Scene): # Woman Intro
    def draw(self, app, progress, elapsed):
        app.draw_background("canteen.png")
        x = int(WIDTH + 200 - (WIDTH + 200 - 900) * min(progress * 1.5, 1.0))
        app.draw_character("girl.png", x, HEIGHT - 100, scale=0.6, flip=True)

class Scene3(Scene): # Together
    def draw(self, app, progress, elapsed):
        app.draw_background("quiet_corridor.png")
        app.draw_character("boy.png", 400, HEIGHT - 100, scale=0.6)
        app.draw_character("girl.png", 900, HEIGHT - 100, scale=0.6, flip=True)

class Scene4(Scene): # Decision
    def draw(self, app, progress, elapsed):
        app.draw_background("quiet_corridor.png")
        app.draw_character("boy.png", 450, HEIGHT - 100, scale=0.6)
        app.draw_character("girl.png", 850, HEIGHT - 100, scale=0.6, flip=True)

class Scene5(Scene): # Silent Transfer
    def __init__(self, duration=12000):
        super().__init__([])
        self.duration = duration
    def is_done(self, audio): return False
    def draw(self, app, progress, elapsed):
        app.draw_background("quiet_corridor.png")
        mx, wx = 450, 850
        move_start, move_end = 0.2, 0.8
        p_move = min(1.0, (progress - move_start) / (move_end - move_start)) if progress > move_start else 0
        
        app.draw_character("boy.png", mx, HEIGHT - 100, scale=0.6)
        app.draw_character("girl.png", wx, HEIGHT - 100, scale=0.6, flip=True)
        
        # Rose movement
        rx = (mx + 80) + (wx - mx - 160) * p_move
        ry = HEIGHT - 350
        rose_scale = 0.2 + (0.1 * p_move)
        app.draw_sprite("rose.png", int(rx), int(ry), scale=rose_scale)

class Scene6(Scene): # Post-Exchange Narration
    def draw(self, app, progress, elapsed):
        app.draw_background("quiet_corridor.png")
        app.draw_character("boy.png", 450, HEIGHT - 100, scale=0.6)
        app.draw_character("girl.png", 850, HEIGHT - 100, scale=0.6, flip=True)
        app.draw_sprite("rose.png", 850 - 60, HEIGHT - 350, scale=0.3)

class Scene7(Scene): # Ending Card
    def __init__(self, duration=15000):
        super().__init__([
            (None, "Some love stories don’t begin with answers."),
            (None, "They begin with intention."),
            (None, "Rose Day.")
        ])
        self.duration = duration
    def draw(self, app, progress, elapsed): app.screen.fill(BLACK)

class StoryApp:
    def __init__(self):
        pygame.init()
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Happy Rose Day - Complete Version")
        self.clock = pygame.time.Clock()
        self.audio = AudioService(self.base_dir)
        self.assets = {}
        self.load_assets()
        
        try:
            self.font = pygame.font.SysFont("georgia", 30, italic=True)
            self.intro_font = pygame.font.SysFont("georgia", 40, italic=True)
            self.title_font = pygame.font.SysFont("georgia", 64, bold=True)
        except:
            self.font = pygame.font.SysFont("serif", 30, italic=True)
            self.intro_font = pygame.font.SysFont("serif", 40, italic=True)
            self.title_font = pygame.font.SysFont("serif", 64, bold=True)
        
        self.scenes = [
            Scene0([("sc0.mp3", "Wilson College, Mumbai.\nA place where paths often cross… quietly.")]),
            Scene1([("sc1.mp3", "He belonged to the IT department. Quiet. Thoughtful.\nHe expressed his feelings more through words than actions.")]),
            Scene2([("sc2.mp3", "She studied Bio. Loud. Dramatic. Yet steady where it mattered.")]),
            Scene3([("sc3.mp3", "They shared friends.\nBut feelings… stayed unshared.")]),
            Scene4([
                ("sc4_1.mp3", "He didn’t come to impress her."),
                ("sc4_2.mp3", "He didn’t come asking for an answer."),
                ("sc4_3.mp3", "He came with something simpler."),
                ("sc4_4.mp3", "The truth of what he wanted; someday.")
            ]),
            Scene5(12000), # Silent Rose Transfer
            Scene6([
                ("sc6_1.mp3", "She didn’t hear a question."),
                ("sc6_2.mp3", "She felt an intention."),
                ("sc6_3.mp3", "And that… was enough for now.")
            ]),
            Scene7(15000) # Ending Card
        ]
        self.idx = 0
        self.app_init_ticks = pygame.time.get_ticks()
        self.start_ticks = self.app_init_ticks
        self.fade_surface = pygame.Surface((WIDTH, HEIGHT)); self.fade_surface.fill(BLACK)
        
        output_temp = os.path.join(self.base_dir, 'output_temp.mp4')
        self.video_writer = imageio.get_writer(output_temp, fps=30)
        print("Recording video stream...")
        self.scenes[0].start(self.audio)

    def load_assets(self):
        asset_paths = {
            "background.png": "assets/backgrounds/background.png",
            "quiet_corridor.png": "assets/backgrounds/quiet_corridor.png",
            "canteen.png": "assets/backgrounds/canteen.png",
            "boy.png": "assets/boy.png",
            "girl.png": "assets/girl.png",
            "rose.png": "assets/rose.png"
        }
        for name, rel_path in asset_paths.items():
            path = os.path.join(self.base_dir, rel_path)
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                if "background" in name or "corridor" in name or "canteen" in name:
                    img = pygame.transform.smoothscale(img, (WIDTH, HEIGHT))
                self.assets[name] = img
            else:
                print(f"Warning: Asset not found: {path}")

    def draw_background(self, name):
        if name in self.assets:
            self.screen.blit(self.assets[name], (0, 0))

    def draw_character(self, name, x, y, scale=0.6, flip=False):
        if name in self.assets:
            img = self.assets[name]
            w, h = img.get_size()
            img = pygame.transform.smoothscale(img, (int(w * scale), int(h * scale)))
            if flip: img = pygame.transform.flip(img, True, False)
            rect = img.get_rect(midbottom=(x, y))
            self.screen.blit(img, rect)

    def draw_sprite(self, name, x, y, scale=1.0):
        if name in self.assets:
            img = self.assets[name]
            w, h = img.get_size()
            img = pygame.transform.smoothscale(img, (int(w * scale), int(h * scale)))
            rect = img.get_rect(center=(x, y))
            self.screen.blit(img, rect)

    def wrap_text(self, text, font, max_width):
        lines = []
        for raw_line in text.split('\n'):
            words = raw_line.split(' ')
            line = []
            for word in words:
                if font.size(' '.join(line + [word]))[0] <= max_width: line.append(word)
                else: lines.append(' '.join(line)); line = [word]
            if line: lines.append(' '.join(line))
        return lines

    def draw_subtitles(self, text, is_intro, is_ending):
        if not text: return
        font = self.intro_font if is_intro else (self.title_font if is_ending else self.font)
        wrapped = self.wrap_text(text, font, MAX_TEXT_WIDTH)
        spacing = font.get_linesize() * 1.3
        total_h = len(wrapped) * spacing
        
        y_base = HEIGHT // 2 - total_h // 2 if (is_intro or is_ending) else HEIGHT - BOTTOM_MARGIN - total_h
        
        if not (is_intro or is_ending):
            box_rect = pygame.Rect(0, 0, MAX_TEXT_WIDTH + 40, total_h + 20)
            box_rect.center = (WIDTH // 2, y_base + total_h // 2)
            box_surf = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
            box_surf.fill((255, 255, 255, 180))
            self.screen.blit(box_surf, box_rect.topleft)
        
        for i, line in enumerate(wrapped):
            color = WHITE if is_ending else BLACK
            surf = font.render(line, True, color)
            rect = surf.get_rect(center=(WIDTH // 2, int(y_base + i * spacing + spacing // 2)))
            self.screen.blit(surf, rect)

    def run(self):
        self.running = True
        while self.idx < len(self.scenes) and self.running:
            for e in pygame.event.get():
                if e.type == pygame.QUIT: self.running = False
            ticks = pygame.time.get_ticks(); elapsed = ticks - self.start_ticks; scene = self.scenes[self.idx]
            done = False
            if self.idx not in [5, 7]:
                scene.update(self.audio)
                done = scene.is_done(self.audio)
                progress = 0.5
                if self.idx in [1, 2]: progress = min(1.0, elapsed / 3000)
            else:
                progress = min(1.0, elapsed / scene.duration)
                done = (progress >= 1.0)
                if self.idx == 7:
                    self.audio.current_subtitle = scene.vo_content[min(int(progress * 3), 2)][1]
            
            if done:
                self.idx += 1; self.start_ticks = ticks
                if self.idx < len(self.scenes): self.scenes[self.idx].start(self.audio)
                continue
            
            scene.draw(self, progress, elapsed)
            self.draw_subtitles(self.audio.current_subtitle, self.idx == 0, self.idx == 7)
            
            fade_alpha = 0
            if elapsed < FADE_DURATION: fade_alpha = int(255 * (1 - ease_in_out(elapsed / FADE_DURATION)))
            if fade_alpha > 0: self.fade_surface.set_alpha(fade_alpha); self.screen.blit(self.fade_surface, (0, 0))
            pygame.display.flip(); self.clock.tick(FPS)
            
            try:
                frame = pygame.surfarray.array3d(self.screen)
                frame = frame.transpose([1, 0, 2])
                self.video_writer.append_data(frame)
            except: pass

        self.video_writer.close()
        try:
            self.export_final()
        except Exception as e:
            print(f"Export failed: {e}")
        pygame.quit()

    def export_final(self):
        print("Mixing audio...")
        output_temp = os.path.join(self.base_dir, "output_temp.mp4")
        video_clip = VideoFileClip(output_temp)
        audio_clips = []
        
        for path, ticks in self.audio.audio_log:
            try:
                clip = AudioFileClip(path)
                offset = (ticks - self.app_init_ticks) / 1000.0
                clip = clip.set_start(max(0, offset))
                audio_clips.append(clip)
            except: pass
            
        output_final = os.path.join(self.base_dir, "output.mp4")
        if audio_clips:
            final_audio = CompositeAudioClip(audio_clips)
            final_clip = video_clip.set_audio(final_audio)
            final_clip.write_videofile(output_final, codec="libx264", audio_codec="aac")
        else:
            video_clip.write_videofile(output_final, codec="libx264")
        
        video_clip.close()
        if os.path.exists(output_temp):
            os.remove(output_temp)
        print(f"Done! Saved as {output_final}")

if __name__ == "__main__":
    StoryApp().run()
