import asyncio, edge_tts, os

VOICE = "en-US-AndrewNeural"
RATE = "-15%"

TEXTS = [
    ("val_sc1_title.mp3", "Valentine's Day."),
    ("val_sc1_intro.mp3",
     "What is written by God, finds its way to the heart."),
    ("val_sc1_narr.mp3",
     "They never planned this. They never expected this."),
    ("val_sc2.mp3",
     "They were different. They were uncertain. They were afraid."),
    ("val_sc2b.mp3",
     "But step by step... they stayed."),
    ("val_sc3a.mp3",
     "There were moments they could not see the path. Moments they did not understand why."),
    ("val_sc3b.mp3",
     "But what is held by God's grace, never loses its way."),
    ("val_sc3c.mp3",
     "By His will, they were led to each other."),
    ("val_sc4a.mp3",
     "Not by force. Not by chance. But by love that was protected."),
    ("val_sc4b.mp3",
     "They did not become perfect. They became true."),
    ("val_sc5.mp3",
     "This was never just a week. It was the beginning of a lifetime."),
    ("val_sc6a.mp3",
     "They walked forward together. Through every season. Through every test. Through every blessing."),
    ("val_sc6b.mp3",
     "And by the grace of God, they lived the rest of their lives together."),
    ("val_sc7_title.mp3", "Valentine's Day."),
    ("val_sc7_ending.mp3",
     "Their story was no longer uncertain. It was complete."),
]

async def generate():
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "audio")
    os.makedirs(out, exist_ok=True)
    for fn, txt in TEXTS:
        p = os.path.join(out, fn)
        await edge_tts.Communicate(txt, VOICE, rate=RATE).save(p)
        print(f"Generated {p}")

if __name__ == "__main__":
    asyncio.run(generate())
