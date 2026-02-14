import asyncio, edge_tts, os

VOICE = "en-US-AndrewNeural"
RATE = "-15%"

TEXTS = [
    ("kiss_sc1_title.mp3", "Kiss Day."),
    ("kiss_sc1_intro.mp3",
     "Trust had brought them here. Now nothing needed to be hidden."),
    ("kiss_sc1_theme.mp3",
     "Some moments do not ask for words. They ask for acceptance."),
    ("kiss_sc2.mp3",
     "They had shared fear. They had shared truth. They had shared closeness."),
    ("kiss_sc3.mp3",
     "There was nothing left to prove. Nothing left to protect."),
    ("kiss_sc4.mp3",
     "This was not a promise. This was acceptance."),
    ("kiss_sc5.mp3",
     "When nothing is forced, everything becomes real."),
    ("kiss_sc6.mp3",
     "Kiss Day isn't about the kiss. It's about knowing you are home."),
    ("kiss_sc7_title.mp3", "Kiss Day."),
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
