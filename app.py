from flask import Flask, jsonify, request, send_file, render_template, redirect, url_for, session
from src.morse_audio import MorseCodeTrainer
from src.morse_data import generate_and_load_morse_test_data
from src.mongo_utils import fetch_test_sets, insert_test_set, test_sets_collection
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
    """Homepage to select test sets from MongoDB."""
    test_sets = fetch_test_sets()
    return render_template("index.html", test_sets=test_sets)

from bson import ObjectId  # Import to work with MongoDB ObjectIds

@app.route("/select-test-set", methods=["POST"])
def select_test_set():
    """Select a test set by its MongoDB ObjectId and store it in session."""
    selected_test_id = request.form.get("test_set")  # Get selected test ID

    # Ensure we fetch the test set properly by querying MongoDB again
    test_set = test_sets_collection.find_one({"_id": ObjectId(selected_test_id)})

    if not test_set:
        return jsonify({"error": "Invalid test set selection"}), 400

    # Store the words of the selected test set in session
    session["test_set"] = test_set["words"]
    session["test_set_name"] = test_set["name"]  # Store the test set name for display

    return redirect(url_for("test_page"))



@app.route("/test")
def test_page():
    """Load the test page with the selected test set."""
    test_set = session.get("test_set", "No Test Set Selected")
    return render_template("test.html", test_set=test_set)

import re

@app.route("/api/add-test-set", methods=["POST"])
def add_test_set():
    """Handles submission of new test sets with input cleaning and validation."""
    data = request.json
    test_set_name = data.get("name", "").strip()  # Remove extra spaces
    words = data.get("words", [])

    # Ensure test set name is provided
    if not test_set_name:
        return jsonify({"error": "Test set name is required."}), 400

    cleaned_words = []
    for word in words:
        word = word.strip()  # Remove leading/trailing spaces
        word = re.sub(r"\s+", " ", word)  # Replace multiple spaces with a single space
        if word and word not in cleaned_words:  # Avoid duplicates
            cleaned_words.append(word)

    # Ensure at least one valid word remains
    if len(cleaned_words) < 1:
        return jsonify({"error": "Test set must contain at least one valid word."}), 400

    # Check if the test set already exists (avoid duplicates)
    existing_set = test_sets_collection.find_one({"name": test_set_name})
    if existing_set:
        return jsonify({"error": "A test set with this name already exists!"}), 400

    # Insert the cleaned data into MongoDB
    test_sets_collection.insert_one({"name": test_set_name, "words": cleaned_words})
    return jsonify({"message": "Test set added successfully!", "name": test_set_name, "words": cleaned_words}), 201




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

    # Get the selected test set from session (should be a list of words)
    test_set = session.get("test_set")

    if not test_set or not isinstance(test_set, list):
        return jsonify({"error": "No valid test set selected!"}), 400

    print(f"play morse current index: {index}")

    # Ensure index is valid
    if index < 0 or index >= len(test_set):
        return jsonify({"error": "Invalid index"}), 404

    phrase = test_set[index]  # Get the phrase from the selected test set
    print("Test phrase: ", phrase)
    trainer.generate_morse_audio(phrase)
    return send_file("static/morse_output.wav", mimetype="audio/wav")

@app.route("/api/get-test-sets", methods=["GET"])
def get_test_sets():
    """Returns all available test sets from MongoDB."""
    test_sets = list(test_sets_collection.find({}, {"_id": 1, "name": 1, "words": 1}))  # Fetch latest

    # Convert ObjectId to string for frontend compatibility
    formatted_test_sets = {str(test["_id"]): {"name": test["name"], "words": test["words"]} for test in test_sets}
    
    return jsonify(formatted_test_sets)


@app.route("/api/get-morse", methods=["GET"])
def get_morse():
    """Returns the Morse code for the current phrase (for checking user input)."""
    
    # Retrieve the actual test set (words list) from session
    selected_test_set = session.get("test_set")

    if not selected_test_set or not isinstance(selected_test_set, list):
        return jsonify({"error": "No valid test set selected!"}), 400

    # Ensure current index is within range
    index = game_state.get("current_index", 0)
    if index >= len(selected_test_set):
        return jsonify({"error": "Test set completed!"}), 400

    phrase = selected_test_set[index]
    morse_code = trainer.text_to_morse(phrase)

    return jsonify({"index": index, "phrase": phrase, "morse_code": morse_code})


@app.route("/api/check-input", methods=["POST"])
def check_input():
    """Checks the user's input against the correct Morse code."""
    global game_state
    data = request.json
    user_input = data.get("input", "").strip()

    # Retrieve the selected test set from session
    test_set = session.get("test_set", [])

    if not test_set:
        return jsonify({"error": "No test set selected!"}), 400

    index = game_state["current_index"]

    # If all words are completed, stop the game
    if index >= len(test_set):
        return jsonify({
            "message": "Test Complete! You finished all words.",
            "lives": game_state["lives"],
            "game_over": True,
            "completed": True
        })

    phrase = test_set[index]  # Get the phrase
    correct_morse = trainer.text_to_morse(phrase)  # Convert to Morse

    print(f"DEBUG: User Submitted: '{user_input}'")
    print(f"DEBUG: Correct Morse : '{correct_morse}'")

    if user_input == correct_morse:
        game_state["current_index"] += 1

        # Check if this was the last word
        if game_state["current_index"] >= len(test_set):
            return jsonify({
                "message": "Test Complete! You finished all words.",
                "lives": game_state["lives"],
                "game_over": True,
                "completed": True
            })

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