import os
from pydub import AudioSegment
from pydub.generators import Sine
from src.morse_audio import MorseCodeTrainer
# Manually specify FFmpeg path for pydub

AudioSegment.converter = r"C:\Users\Zachb\Downloads\ffmpeg-2025-02-17-git-b92577405b-full_build\bin\ffmpeg.exe"


def generate_morse_sounds(self):
    """Generates the dot and dash sound files based on the current speed."""
    
    # Ensure the sounds directory exists
    output_dir = "static/sounds"
    os.makedirs(output_dir, exist_ok=True)

    dot_sound = Sine(self.frequency).to_audio_segment(duration=self.dot_duration)
    dash_sound = Sine(self.frequency).to_audio_segment(duration=self.dot_duration * 3)

    dot_sound.export(f"{output_dir}/dot.wav", format="wav")
    dash_sound.export(f"{output_dir}/dash.wav", format="wav")

    print(f"Generated dot.wav ({self.dot_duration} ms) and dash.wav ({self.dot_duration * 3} ms)")

# Only run this script when executed directly
if __name__ == "__main__":
    trainer = MorseCodeTrainer(dot_duration=100)  # Default speed, can be updated dynamically
    generate_morse_sounds(trainer)
