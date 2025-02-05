let userInput = "";
let correctMorse = "";
let currentIndex = 0;
let lives = 3;

document.addEventListener("keydown", function(event) {
    if (event.key === "n" || event.key === "N") {
        userInput += ".";
        playDot();
    } else if (event.key === "m" || event.key === "M") {
        userInput += "-";
        playDash();
    } else if (event.key === " ") {  // Capture space for letter separation
        userInput += " ";
    }
    
    document.getElementById("userInput").innerText = userInput;

    // print current user input 
    console.log("DEBUG: User Input    :", userInput);  // Debug log user input
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
            document.getElementById("phraseDisplay").innerText = `Phrase: ${data.phrase}`;
            correctMorse = data.morse_code;
            userInput = "";
            document.getElementById("userInput").innerText = "";

            console.log("DEBUG: Correct Morse Code:", correctMorse);  // Logs the correct answer for debugging
        })
        .catch(error => console.error("Error loading phrase:", error));
}


function playMorse() {
    let audio = new Audio("/api/play-morse");
    audio.play();
}

function submitInput() {
    fetch("/api/check-input", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input: userInput })
    })
    .then(response => response.json())
    .then(data => {

        // print Comparison of user input with correct input
        console.log("DEBUG: User submitted:", userInput);
        console.log("DEBUG: Correct Morse :", data.correct_morse);

        alert(data.message);
        
        if (data.game_over) {
            document.getElementById("phraseDisplay").innerText = "Game Over! Restart to play again.";
        } else {
            lives = data.lives;
            document.getElementById("lives").innerText = lives;
            userInput = "";
            document.getElementById("userInput").innerText = "";
            
            if (data.message === "Correct!") {
                loadPhrase();
            }
        }
    })
    .catch(error => console.error("Error submitting input:", error));
}


function updateSpeed() {
    let speed = document.getElementById("speedInput").value;
    
    fetch("/api/set-speed", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ dot_duration: parseInt(speed) })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
    });
}

function playDot() {
    let dotSound = new Audio("/static/dot.wav");
    dotSound.play();
}

function playDash() {
    let dashSound = new Audio("/static/dash.wav");
    dashSound.play();
}
