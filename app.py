from flask import Flask, jsonify, request, send_file, render_template
from src.morse_audio import MorseCodeTrainer
from src.morse_data import load_morse_test_data
import os
from generate_morse_sounds import generate_morse_sounds

app = Flask(__name__, template_folder="templates", static_folder="static")

trainer = MorseCodeTrainer(dot_duration=100)
test_data = load_morse_test_data()

# Generate Morse sounds at startup
generate_morse_sounds(trainer)

# Game State
game_state = {
    "current_index": 0,  # Tracks the current test phrase
    "lives": 3,
}

@app.route("/")
def index():
    """Serve the main HTML page."""
    return render_template("index.html")

@app.route("/api/set-speed", methods=["POST"])
def set_speed():
    """Update the Morse code speed dynamically."""
    global trainer
    data = request.json
    new_speed = data.get("dot_duration", 100)

    trainer.dot_duration = new_speed
    trainer.dash_duration = new_speed * 3

    # Regenerate the sounds
    generate_morse_sounds(trainer)

    return jsonify({"message": "Speed updated", "dot_duration": trainer.dot_duration})


@app.route("/api/start-game", methods=["POST"])
def start_game():
    """Resets the game state and starts at test 1 (index 0)."""
    global game_state
    game_state["current_index"] = 0
    game_state["lives"] = 3
    return jsonify({"message": "Game started", "current_index": game_state["current_index"], "lives": game_state["lives"]})

@app.route("/api/play-morse", methods=["GET"])
def play_morse():
    """Plays Morse code for the current test phrase."""
    index = game_state["current_index"]
    
    if index not in test_data:
        return jsonify({"error": "Invalid index"}), 404
    
    phrase = test_data[index]
    trainer.generate_morse_audio(phrase)
    return send_file("static/morse_output.wav", mimetype="audio/wav")

@app.route("/api/get-morse", methods=["GET"])
def get_morse():
    """Returns the Morse code for the current phrase (for checking user input)."""
    index = game_state["current_index"]
    if index not in test_data:
        return jsonify({"error": "Invalid index"}), 404
    
    phrase = test_data[index]
    morse_code = trainer.text_to_morse(phrase)
    return jsonify({"index": index, "phrase": phrase, "morse_code": morse_code})

@app.route("/api/check-input", methods=["POST"])
def check_input():
    """Checks the user's input against the correct Morse code."""
    global game_state
    data = request.json
    user_input = data.get("input", "").strip()  # Remove leading/trailing spaces

    index = game_state["current_index"]
    correct_morse = trainer.text_to_morse(test_data[index])

    # Debugging: Log user input vs correct Morse code
    print(f"DEBUG: User Submitted: '{user_input}'")
    print(f"DEBUG: Correct Morse : '{correct_morse}'")

    if user_input == correct_morse:
        game_state["current_index"] += 1
        return jsonify({
            "message": "Correct!",
            "next_index": game_state["current_index"],
            "lives": game_state["lives"],
            "user_input": user_input, 
            "correct_morse": correct_morse
        })
    else:
        game_state["lives"] -= 1
        if game_state["lives"] <= 0:
            return jsonify({
                "message": "Game Over!",
                "lives": 0,
                "game_over": True,
                "user_input": user_input,
                "correct_morse": correct_morse
            })
        return jsonify({
            "message": "Incorrect, try again!",
            "lives": game_state["lives"],
            "game_over": False,
            "user_input": user_input,
            "correct_morse": correct_morse
        })


if __name__ == "__main__":
    app.run(debug=True)
