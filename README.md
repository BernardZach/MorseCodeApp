## **Morse Code Trainer Game**
A simple **Flask web app** that helps users **learn Morse code** by listening to Morse code and typing the correct sequence. The game progresses through different levels, tracking the player's input and adjusting Morse speed dynamically.

---

## **🔹 Features**
✅ **Listen to Morse Code**: Hear a phrase in Morse code and type the correct translation.  
✅ **Interactive Game**: Progress through levels with 3 lives.  
✅ **Customizable Speed**: Adjust Morse playback speed with a slider.  
✅ **Real-Time Audio Generation**: New sounds are generated when changing speed.  

---

## **🔹 Installation Instructions**
### **1️⃣ Install FFMPEG (Required for `pydub`)**
To generate and play Morse code audio, you must install **FFmpeg**.

- **Windows**:
  1. Download FFmpeg from [FFmpeg Official Site](https://ffmpeg.org/download.html).
  2. Extract it and **add the `bin/` folder to your system PATH**.
  3. Verify installation:
     ```bash
     ffmpeg -version
     ```

- **Mac (via Homebrew)**:
  ```bash
  brew install ffmpeg
  ```

- **Linux (Debian/Ubuntu)**:
  ```bash
  sudo apt update && sudo apt install ffmpeg -y
  ```

---

### **2️⃣ Clone the Repository**
```bash
git clone https://github.com/BernardZach/MorseCodeApp
cd morse-code-trainer
```

---

### **3️⃣ Install Dependencies**
Run the following command to install the required Python packages:
```bash
pip install -r requirements.txt
```

---

### **4️⃣ Run the App**
Start the Flask server:
```bash
python app.py
```

The app will be accessible at:
```
http://127.0.0.1:5000/
```

---

## **🔹 Project Structure**
```
morse-code-trainer/
┣ data/                    # Stores generated Morse test phrases
┣ src/                     # Python backend logic (Morse generation, game logic)
┣ static/                  # Frontend assets (JS, CSS, sound files)
┃ ┣ sounds/                # Generated Morse audio (dot.wav, dash.wav)
┃ ┣ script.js              # Handles UI and game interactions
┃ ┗ styles.css             # Custom styling
┣ templates/               # HTML templates for the web app
┃ ┗ index.html             # Main UI page
┣ .gitignore               # Ignored files (sound files, data, cache)
┣ app.py                   # Main Flask application
┣ generate_morse_sounds.py # Generates Morse audio dynamically
┣ requirements.txt         # Python dependencies
┗ README.md                # Documentation
```

---

## **🔹 How to Play**
1️⃣ **Press "Start Game"** to begin.  
2️⃣ **Listen to the Morse Code** by clicking "Play Morse Code".  
3️⃣ **Type using:**
   - `N` for **dot (.)**
   - `M` for **dash (-)**
   - `Space` to **separate letters**  

4️⃣ **Progress through levels** when you get the correct answer.  
5️⃣ **Adjust Speed** anytime using the slider.  

---

## **🔹 Future Enhancements**
- 🔥 **Leaderboard**: Track top scores.  
- 🎨 **Better UI/UX**: Animated feedback.  
- 📡 **Multiplayer Mode**: Add game elements (relearn mistakes)
- 🤖 **incorperate AI**: Add AI to work on  hard letters or phrases

---

## **🔹 Contributing**
Feel free to fork the repository and submit pull requests. If you find a bug or have suggestions, open an issue on GitHub.

---
