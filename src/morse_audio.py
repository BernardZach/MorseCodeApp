import os
import simpleaudio as sa
from pydub import AudioSegment
from pydub.generators import Sine

class MorseCodeTrainer:
    def __init__(self, dot_duration=100, frequency=800):
        """Initialize Morse Code settings."""
        self.dot_duration = dot_duration
        self.dash_duration = dot_duration * 3
        self.intra_letter_gap = dot_duration
        self.inter_letter_gap = dot_duration * 3
        self.inter_word_gap = dot_duration * 7
        self.frequency = frequency

        self.morse_code_dict = {
            'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
            'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
            'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
            'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
            'Y': '-.--', 'Z': '--..', ' ': ' '
        }

    def text_to_morse(self, text):
        """Convert text to Morse code representation."""
        text = text.upper()
        return " ".join([self.morse_code_dict[char] for char in text if char in self.morse_code_dict])

    def generate_morse_audio(self, text, output_filename="static/morse_output.wav"):
        """Generate and save a Morse code audio file."""
        morse_code = self.text_to_morse(text)

        dot_sound = Sine(self.frequency).to_audio_segment(duration=self.dot_duration)
        dash_sound = Sine(self.frequency).to_audio_segment(duration=self.dash_duration)
        silence = AudioSegment.silent(duration=self.intra_letter_gap)

        morse_audio = AudioSegment.silent(duration=0)
        for symbol in morse_code:
            if symbol == ".":
                morse_audio += dot_sound
            elif symbol == "-":
                morse_audio += dash_sound
            morse_audio += silence

        os.makedirs(os.path.dirname(output_filename), exist_ok=True)
        morse_audio.export(output_filename, format="wav")
        return output_filename

    def play_morse_audio(self, text):
        """Play the generated Morse code audio file."""
        output_file = self.generate_morse_audio(text)
        wave_obj = sa.WaveObject.from_wave_file(output_file)
        play_obj = wave_obj.play()
        play_obj.wait_done()
