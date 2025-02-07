import os
from pydub import AudioSegment
from pydub.generators import Sine
from src.morse_audio import MorseCodeTrainer

def generate_morse_sounds(trainer):
    """Generate dot.wav and dash.wav based on the dot duration in MorseCodeTrainer."""
    sounds_dir = "static/sounds"
    os.makedirs(sounds_dir, exist_ok=True)  # Ensure the static directory exists

    # Generate dot and dash sounds
    dot_sound = Sine(trainer.frequency).to_audio_segment(duration=trainer.dot_duration)
    dash_sound = Sine(trainer.frequency).to_audio_segment(duration=trainer.dash_duration)

    # Save them as WAV files
    dot_sound.export(os.path.join(sounds_dir, "dot.wav"), format="wav")
    dash_sound.export(os.path.join(sounds_dir, "dash.wav"), format="wav")

    print(f"Generated dot.wav ({trainer.dot_duration} ms) and dash.wav ({trainer.dash_duration} ms) in {sounds_dir}/")

# Only run this script when executed directly
if __name__ == "__main__":
    trainer = MorseCodeTrainer(dot_duration=100)  # Default speed, can be updated dynamically
    generate_morse_sounds(trainer)
