import asyncio
import edge_tts
import os

VOICE = "en-US-AndrewNeural"
RATE = "-15%"

TEXTS = [
    # Scene 1 — Title
    ("hug_sc1_title.mp3", "Hug Day."),

    # Scene 1 — Theme intro
    ("hug_sc1_intro.mp3",
     "Growth brought them closer. But closeness asks for trust."),

    # Scene 1 — Theme continued
    ("hug_sc1_theme.mp3",
     "Not every distance is physical. Some distances live in hesitation."),

    # Scene 2 — Standing
    ("hug_sc2.mp3",
     "They had shared words. They had shared truth. But there was still something unspoken."),

    # Scene 3 — Sitting
    ("hug_sc3.mp3",
     "Closeness doesn't arrive suddenly. It arrives when fear begins to fade."),

    # Scene 4 — Standing transition
    ("hug_sc4.mp3",
     "Neither of them asked. Neither of them needed to."),

    # Scene 5 — Hug moment
    ("hug_sc5.mp3",
     "This was not about holding on. It was about letting each other in."),

    # Scene 6 — After hug
    ("hug_sc6.mp3",
     "Some closeness cannot be explained. It can only be felt."),

    # Scene 7 — Final meaning
    ("hug_sc7.mp3",
     "Hug Day isn't about touch. It's about knowing you are no longer alone."),

    # Scene 8 — Ending title
    ("hug_sc8_title.mp3", "Hug Day."),
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
