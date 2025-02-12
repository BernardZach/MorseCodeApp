let userInput = "";
let correctMorse = "";
let currentIndex = 0;
let lives = 3;

document.addEventListener("keydown", function(event) {
    let userInputDisplay = document.getElementById("userInputDisplay");

    // Prevent Morse sound playback when typing in an input field
    if (document.activeElement.tagName === "INPUT" || document.activeElement.tagName === "TEXTAREA") {
        return;
    }

    if (event.key === "n" || event.key === "N") {
        userInput += ".";
        playDot();
    } else if (event.key === "m" || event.key === "M") {
        userInput += "-";
        playDash();
    } else if (event.key === " ") {
        userInput += " ";  // Allow spaces
    }

    if (userInput.length > 0) {
        userInputDisplay.classList.remove("hidden");  // Show input text
        userInputDisplay.innerText = userInput;  // Update text display
    }
});




function startGame() {
    fetch("/api/start-game", { method: "POST" })
        .then(response => response.json())
        .then(data => {
            currentIndex = data.current_index;
            lives = data.lives;
            document.getElementById("lives").innerText = lives;
            loadPhrase();
        });
}

function loadPhrase() {
    fetch("/api/get-morse")
        .then(response => response.json())
        .then(data => {
            document.getElementById("phraseText").innerText = data.phrase;  // Update displayed phrase
            correctMorse = data.morse_code;
            userInput = "";  // Reset user input

            let userInputDisplay = document.getElementById("userInputDisplay");
            if (userInputDisplay) {
                userInputDisplay.innerText = "";  // Clear previous input
                userInputDisplay.classList.add("hidden");  // Hide it until user types
            } else {
                console.error("Error: userInputDisplay element not found!");
            }

            console.log("DEBUG: Loaded New Phrase:", data.phrase);
            console.log("DEBUG: Correct Morse Code:", correctMorse);
        })
        .catch(error => console.error("Error loading phrase:", error));
}





let morseAudio = null;  // Track current audio instance

function playMorse() {
    // Ensure correct Morse file is generated before playing
    fetch("/api/play-morse")
        .then(response => response.blob())  // Ensure the new file is downloaded
        .then(blob => {
            let url = URL.createObjectURL(blob);  // Create an object URL for the new audio
            if (morseAudio) {
                morseAudio.pause();  // Stop previous audio
                morseAudio.currentTime = 0;
            }
            morseAudio = new Audio(url);
            morseAudio.play();
        })
        .catch(error => console.error("Error playing Morse code:", error));
}

function submitInput() {
    fetch("/api/check-input", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input: userInput })
    })
    .then(response => response.json())
    .then(data => {
        console.log("DEBUG: User submitted:", userInput);
        console.log("DEBUG: Correct Morse :", data.correct_morse);
        console.log("DEBUG: Next Index    :", data.next_index);

        alert(data.message);

        let userInputDisplay = document.getElementById("userInputDisplay");

        if (data.completed) {
            document.getElementById("phraseDisplay").innerText = "🎉 Test Complete! 🎉";
            document.getElementById("userInputDisplay").innerText = "";
            userInput = "";
            return; // Stop here since the test is complete
        }

        if (data.game_over) {
            document.getElementById("phraseDisplay").innerText = "Game Over! Restart to play again.";
        } else {
            lives = data.lives;
            document.getElementById("lives").innerText = lives;
            userInput = "";

            if (userInputDisplay) {
                userInputDisplay.innerText = "";
                userInputDisplay.classList.add("hidden");
            } else {
                console.error("Error: userInputDisplay element not found!");
            }

            if (data.message === "Correct!") {
                loadPhrase();  // Move to the next level
            }
        }
    })
    .catch(error => console.error("Error submitting input:", error));
}



// Function to update the speed value display
function updateSpeed(value) {
    document.getElementById("speedValue").innerText = value; // Update the UI display
    localStorage.setItem("morseSpeed", value); // Save the speed setting persistently

    // Send the new speed setting to the backend
    fetch("/api/update-speed", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ dot_duration: parseInt(value) })
    })
    .then(response => response.json())
    .then(data => console.log("Speed updated:", data))
    .catch(error => console.error("Error updating speed:", error));
}

function updateTestSetDropdown() {
    fetch("/api/get-test-sets", { cache: "no-store" }) // Ensure no old cache is used
        .then(response => response.json())
        .then(data => {
            const dropdown = document.getElementById("test_set");

            if (!dropdown) {
                console.error("Error: Dropdown element not found!");
                return;
            }

            dropdown.innerHTML = ""; // Clear the existing options

            Object.keys(data).forEach(key => {
                let option = document.createElement("option");
                option.value = key;
                option.textContent = `${data[key].name} (${data[key].words.length} phrases)`;
                dropdown.appendChild(option);
            });

            console.log("DEBUG: Updated test sets in dropdown:", data);
        })
        .catch(error => console.error("Error updating test dropdown:", error));
}


function submitTestSet() {
    let testSetName = document.getElementById("testSetName").value.trim();
    let words = document.getElementById("testWords").value.trim().split(",");

    if (!testSetName || words.length < 1) {
        alert("Please enter a valid test name and at least one word.");
        return;
    }

    fetch("/api/add-test-set", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: testSetName, words: words })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert("Error: " + data.error);
        } else {
            alert("Test set added successfully!");

            // Clear input fields
            document.getElementById("testSetName").value = "";
            document.getElementById("testWords").value = "";

            // Fetch updated test sets and update dropdown
            fetchTestSets();
        }
    })
    .catch(error => console.error("Error submitting test set:", error));
}

// Function to refresh test sets dropdown
function fetchTestSets() {
    fetch("/api/get-test-sets")
        .then(response => response.json())
        .then(data => {
            let dropdown = document.getElementById("test_set");
            dropdown.innerHTML = ""; // Clear existing options

            for (const [key, value] of Object.entries(data)) {
                let option = document.createElement("option");
                option.value = key;
                option.textContent = `${value.name} (${value.words.length} phrases)`;
                dropdown.appendChild(option);
            }
        })
        .catch(error => console.error("Error fetching test sets:", error));
}

// Call fetchTestSets on page load to get latest test sets
document.addEventListener("DOMContentLoaded", fetchTestSets);




// Ensure the slider loads the saved speed on page load
window.onload = function () {
    let savedSpeed = localStorage.getItem("morseSpeed") || "100"; // Default to 100ms if not set
    document.getElementById("speedSlider").value = savedSpeed;
    document.getElementById("speedValue").innerText = savedSpeed;
};



function playDot() {
    let dotSound = new Audio("/static/sounds/dot.wav");
    dotSound.play();
}

function playDash() {
    let dashSound = new Audio("/static/sounds/dash.wav");
    dashSound.play();
}
