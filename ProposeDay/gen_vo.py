import asyncio
import edge_tts
import os

# Using a mature, calm male voice
VOICE = "en-US-AndrewNeural" 

TEXTS = [
    ("h_sc1.mp3", "After the rose was given, nothing was said. But something had already been understood."),
    ("h_sc2.mp3", "He thought: I’ve never known how to show love loudly. Words were the only place I felt honest."),
    ("h_sc3.mp3", "She noticed the difference between silence and hesitation. This was not hesitation."),
    ("h_sc4.mp3", "He said, quietly: I don't know how to impress you. But I don't want to stand in your way; I want to stand with you, when you're ready."),
    ("h_sc5.mp3", "He continued: If one day you choose forever, I want to choose it with you."),
    ("h_sc6.mp3", "She didn’t answer him. She let him know he was heard."),
    ("h_sc7.mp3", "Propose Day is not about hearing yes. It is about being brave enough to mean it.")
]

async def generate():
    os.makedirs("assets/audio", exist_ok=True)
    for filename, text in TEXTS:
        path = os.path.join("assets/audio", filename)
        communicate = edge_tts.Communicate(text, VOICE)
        await communicate.save(path)
        print(f"Generated {path}")

if __name__ == "__main__":
    asyncio.run(generate())
