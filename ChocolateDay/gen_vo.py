import asyncio
import edge_tts
import os

# Using the same voice as Propose Day
VOICE = "en-US-AndrewNeural" 

TEXTS = [
    ("choc_sc0.mp3", "Rose Day showed intention. Propose Day brings clarity and courage."),
    ("choc_sc1.mp3", "Not every day needs courage. Some days need comfort."),
    ("choc_sc2.mp3", "After saying what mattered, he didn't feel the need to prove anything."),
    ("choc_sc3.mp3", "This wasn't about a gesture. It was about sharing something ordinary."),
    ("choc_sc4.mp3", "She noticed the shift. This wasn't effort. This was ease."),
    ("choc_sc5.mp3", "He said. I thought you might like this."),
    ("choc_sc7.mp3", "Some connections grow louder. Others grow easier."),
    ("choc_sc8.mp3", "Chocolate Day isn't about sweetness. It's about choosing comfort after honesty."),
    ("choc_sc9.mp3", "Chocolate Day.")
]

async def generate():
    os.makedirs("ChocolateDay/assets/audio", exist_ok=True)
    for filename, text in TEXTS:
        path = os.path.join("ChocolateDay/assets/audio", filename)
        communicate = edge_tts.Communicate(text, VOICE, rate="-15%")
        await communicate.save(path)
        print(f"Generated {path}")

if __name__ == "__main__":
    asyncio.run(generate())
