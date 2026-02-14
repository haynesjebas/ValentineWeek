import asyncio
import edge_tts
import os

VOICE = "en-GB-ThomasNeural"

TEXTS = [
    ("sc0.mp3", "Wilson College, Mumbai. A place where paths often cross… quietly."),
    # Updated Boy Intro: Restored original atmosphere + specific line change
    ("sc1.mp3", "He belonged to the IT department. Quiet. Thoughtful. He expressed his feelings more through words than actions."),
    # Original Girl Intro
    ("sc2.mp3", "She studied Bio. Loud. Dramatic. Yet steady where it mattered."),
    # Original Shared
    ("sc3.mp3", "They shared friends. But feelings… stayed unshared."),
    # Original Decision
    ("sc4_1.mp3", "He didn’t come to impress her."),
    ("sc4_2.mp3", "He didn’t come asking for an answer."),
    ("sc4_3.mp3", "He came with something simpler."),
    ("sc4_4.mp3", "The truth of what he wanted; someday."),
    # Final Narration (Corrected wording)
    ("sc6_1.mp3", "She didn’t hear a question."),
    ("sc6_2.mp3", "She felt an intention."),
    ("sc6_3.mp3", "And that… was enough for now.")
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
