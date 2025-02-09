import os
from pydub import AudioSegment
from pydub.generators import Sine
from src.morse_audio import MorseCodeTrainer

def generate_morse_sounds(self):
    """Generates the dot and dash sound files based on the current speed."""
    dot_sound = Sine(self.frequency).to_audio_segment(duration=self.dot_duration)
    dash_sound = Sine(self.frequency).to_audio_segment(duration=self.dot_duration * 3)

    dot_sound.export("static/sounds/dot.wav", format="wav")
    dash_sound.export("static/sounds/dash.wav", format="wav")

    print(f"Generated dot.wav ({self.dot_duration} ms) and dash.wav ({self.dot_duration * 3} ms)")

# Only run this script when executed directly
if __name__ == "__main__":
    trainer = MorseCodeTrainer(dot_duration=100)  # Default speed, can be updated dynamically
    generate_morse_sounds(trainer)
