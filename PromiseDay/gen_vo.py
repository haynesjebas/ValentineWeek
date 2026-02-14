import asyncio
import edge_tts
import os

# Same voice and pacing as TeddyDay
VOICE = "en-US-AndrewNeural"
RATE = "-15%"

TEXTS = [
    # SCENE 1 — Theme Introduction
    ("promise_sc1_title.mp3",
     "Promise Day."),

    ("promise_sc1_intro.mp3",
     "Care brought them close. Now they had to decide who they would become to each other."),

    ("promise_sc1_theme.mp3",
     "Care had brought them this far. But care alone cannot shape what comes next. Growth asks a quieter question. What kind of people will they become to each other?"),

    # SCENE 2 — Sitting Scene (SPLIT into two beats)
    ("promise_sc2a.mp3",
     "They were afraid of losing each other."),

    ("promise_sc2b.mp3",
     "But more, they were afraid of becoming strangers as they changed."),

    # SCENE 3 — Girl Dialogue
    ("promise_sc3_nar.mp3",
     "She said,"),

    ("promise_sc3_girl.mp3",
     "Promise me something. Promise me we won't stop being honest, even when we grow."),

    # SCENE 4 — Boy Dialogue
    ("promise_sc4_nar.mp3",
     "He said,"),

    ("promise_sc4_boy.mp3",
     "Then promise me something too. Promise me we'll learn each version of each other. Even the ones we haven't met yet."),

    # SCENE 5 — Standing Transition
    ("promise_sc5.mp3",
     "This was not a promise to remain the same. It was a promise to grow without growing apart."),

    # SCENE 6 — Final Meaning
    ("promise_sc6.mp3",
     "Promise Day isn't about staying unchanged. It's about choosing to grow side by side."),

    # SCENE 7 — Ending Title
    ("promise_sc7_title.mp3",
     "Promise Day."),
]

async def generate():
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "audio")
    os.makedirs(out_dir, exist_ok=True)
    for filename, text in TEXTS:
        path = os.path.join(out_dir, filename)
        communicate = edge_tts.Communicate(text, VOICE, rate=RATE)
        await communicate.save(path)
        print(f"Generated {path}")

if __name__ == "__main__":
    asyncio.run(generate())
