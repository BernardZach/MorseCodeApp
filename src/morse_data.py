import json
import os

# Define the data file path
DATA_FILE = os.path.join(os.path.dirname(__file__), "../data/morse_test_words.json")

def generate_and_load_morse_test_data(test_words):
    """Regenerates and loads the Morse test data dynamically based on the selected set."""
    generate_morse_test_json(test_words)  # Always regenerates the file
    return load_morse_test_data()  # Loads the freshly generated data

def generate_morse_test_json(test_words):
    """Creates (or overwrites) a JSON file with the selected test words."""
    morse_test_data = {"morse_test_words": [{"index": i, "words": word} for i, word in enumerate(test_words)]}

    # Ensure data directory exists
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

    # Overwrite JSON file with new data
    with open(DATA_FILE, "w") as json_file:
        json.dump(morse_test_data, json_file, indent=4)

    print(f"Regenerated test words saved to {DATA_FILE}")

def load_morse_test_data():
    """Reads the JSON file and returns a dictionary of test phrases."""
    try:
        with open(DATA_FILE, "r") as json_file:
            data = json.load(json_file)
            return {item["index"]: item["words"] for item in data["morse_test_words"]}
    except FileNotFoundError:
        print(f"Error: Could not find {DATA_FILE}")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {DATA_FILE}")
        return {}

# Run this script directly to regenerate and load default data
if __name__ == "__main__":
    test_data = generate_and_load_morse_test_data(["HELLO", "WORLD", "GOOD MORNING"])
    print("Loaded Morse Test Data:", test_data)
