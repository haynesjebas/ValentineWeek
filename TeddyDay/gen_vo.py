import asyncio
import edge_tts
import os

# Using the same voice as previous days
VOICE = "en-US-AndrewNeural" 

# Keeping the slow pace (-15%) for clarity and comfort
RATE = "-15%"

TEXTS = [
    # SCENE 0 - THEME TITLE
    ("teddy_sc0.mp3", "Comfort turns into care."),

    # SCENE 1 - INTRO
    ("teddy_sc1.mp3", "This day asks a quiet question. What happens when comfort becomes something you want to protect?"),
    
    # SCENE 2 - WHERE THEY ARE NOW
    ("teddy_sc2.mp3", "Somewhere between ease and familiarity, something deeper begins."),
    
    # SCENE 3 - HER PRESENCE
    ("teddy_sc3.mp3", "She felt it too. This wasn’t effort anymore."),
    
    # SCENE 4 - CARE FORMS
    ("teddy_sc4.mp3", "Care doesn’t arrive loudly. It shows up with responsibility."),
    
    # SCENE 5 - THE TEDDY MOMENT (PART 1 - BOY)
    ("teddy_sc5_boy.mp3", "He said. I saw this and thought of you."),
    
    # SCENE 5 - THE TEDDY MOMENT (PART 2 - GIRL)
    ("teddy_sc5_girl.mp3", "She Blushingly replied. I’ll take good care of it."),
    
    # SCENE 6 - WHAT IT MEANS
    ("teddy_sc6.mp3", "Some things aren’t given to be held. They’re given to be taken care of."),
    
    # FINAL FRAME
    ("teddy_sc_theme.mp3", "Teddy Day.")
]

async def generate():
    os.makedirs("TeddyDay/assets/audio", exist_ok=True)
    for filename, text in TEXTS:
        path = os.path.join("TeddyDay/assets/audio", filename)
        communicate = edge_tts.Communicate(text, VOICE, rate=RATE)
        await communicate.save(path)
        print(f"Generated {path}")

if __name__ == "__main__":
    asyncio.run(generate())
