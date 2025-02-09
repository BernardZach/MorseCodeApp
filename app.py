from flask import Flask, jsonify, request, send_file, render_template, redirect, url_for, session
from src.morse_audio import MorseCodeTrainer
from src.morse_data import generate_and_load_morse_test_data
import os
from generate_morse_sounds import generate_morse_sounds
from pydub import AudioSegment

AudioSegment.converter = "/usr/bin/ffmpeg"  #ffmpeg path for aws ec2

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "your_secret_key"  # Needed for session handling


trainer = MorseCodeTrainer(dot_duration=100)
# test_data = generate_and_load_morse_test_data()

# Generate Morse sounds at startup
generate_morse_sounds(trainer)

# Game State
game_state = {
    "current_index": 0,  # Tracks the current test phrase
    "lives": 3,
}

# Placeholder for available test sets (Will come from MongoDB later)
TEST_SETS = {
    "default": ["HELLO", "WORLD", "GOOD MORNING"],
    "advanced": ["MORSE CODE TEST", "LEARNING MORSE CODE", "PYTHON DEVELOPMENT"],
    "fun": ["GAMING", "MOVIES", "MUSIC"]
}

@app.route("/")
def home():
    """Home page to select a test set."""
    return render_template("index.html", test_sets=TEST_SETS)

@app.route("/select-test-set", methods=["POST"])
def select_test_set():
    """Stores selected test set in session and regenerates test data."""
    selected_set = request.form.get("test_set")
    if selected_set in TEST_SETS:
        session["test_set_name"] = selected_set  # Save the name
        session["test_set"] = TEST_SETS[selected_set]  # Save test phrases
        generate_and_load_morse_test_data(TEST_SETS[selected_set])  # Regenerate with selected data
        return redirect(url_for("test"))
    return redirect(url_for("home"))

@app.route("/test")
def test():
    """Loads the testing page with the selected test set."""
    test_set = session.get("test_set", TEST_SETS["default"])  # Fallback to default
    return render_template("test.html", test_set=test_set)

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
    index = game_state.get("current_index", 0)

    # Get the selected test set from session
    test_set = session.get("test_set", [])
    
    print(f"play morse current index: {index}")

    # Ensure index is valid
    if index < 0 or index >= len(test_set):
        return jsonify({"error": "Invalid index"}), 404

    phrase = test_set[index]  # Get the phrase from the selected test set
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
    
@app.route("/api/update-speed", methods=["POST"])
def update_speed():
    """Updates Morse code dot duration and regenerates all necessary sound files."""
    data = request.json
    new_dot_duration = data.get("dot_duration", 100)  # Default to 100ms

    # Update trainer settings
    trainer.dot_duration = new_dot_duration

    # Regenerate dot and dash sounds
    trainer.generate_morse_sounds()  # Ensure this function regenerates `dot.wav` and `dash.wav`

    # Regenerate the current test phrase audio
    index = game_state.get("current_index", 0)
    test_set = session.get("test_set", [])  # Load the currently selected test set

    if 0 <= index < len(test_set):  # Ensure index is valid
        phrase = test_set[index]
        trainer.generate_morse_audio(phrase)  # Regenerate phrase audio

    return jsonify({"message": "Speed updated", "dot_duration": new_dot_duration})


if __name__ == "__main__":
    # Check if running on EC2 (by looking for an environment variable)
    is_ec2 = os.getenv("EC2_INSTANCE", "false").lower() == "true"

    # Use 0.0.0.0 for EC2, but 127.0.0.1 locally
    host = "0.0.0.0" if is_ec2 else "127.0.0.1"
    
    app.run(host=host, port=5000, debug=True)