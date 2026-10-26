# ⚡ Jarvis: Building My Personal AI Voice Assistant from Scratch

A 5-day build log documenting the development of an intelligent, offline/online voice assistant in Python. This project covers the full pipeline: capturing raw microphone audio, handling real-time speech recognition, integrating large language models for reasoning, automating local system workflows, and implementing low-latency wake-word detection.

---

## 🛠️ Tech Stack & Tools

- **Core Language:** Python 3.10+
- **Input (Ears):** `SpeechRecognition`, `PyAudio` (tuned for `en-IN` acoustic models)
- **Output (Voice):** `pyttsx3` (Offline SAPI5 synthesis engine)
- **Environment & Control:** Virtual environment (`venv`), Git, VS Code

---

## 📅 Daily Build Progress

### 📦 Day 1: Setup, Audio Calibration & Sensory Systems (Completed Today)
Focused on establishing the foundational audio I/O pipeline and troubleshooting real-world hardware/acoustic constraints:

- [x] **Isolated Environment Setup:** Configured an isolated virtual environment (`jarvis_env`) and added strict `.gitignore` rules to safeguard environment variables and system binaries from version control.
- [x] **Microphone Calibration & Audio Pipeline:** Resolved PyAudio device binding and sound card clipping issues. Reconfigured dynamic thresholding and set `pause_threshold = 1.2s` to eliminate premature audio cutoff.
- [x] **Acoustic Localization (`en-IN`):** Swapped default phoneme recognition to Indian English (`en-IN`), correcting transcription failures caused by accent and ambient room reflection.
- [x] **Offline Speech Synthesis:** Integrated `pyttsx3` with tuned speech rates (175 wpm) for low-latency, fully offline voice replies.
- [x] **Continuous Echo Loop:** Built an end-to-end interactive loop that listens, transcribes cleanly, logs to console, and repeats back user speech before gracefully terminating on exit commands.

---

### 🧠 Day 2: The Cognitive Brain (Up Next)
- [ ] Connect Gemini 2.5 Flash API via modern SDK client integration.
- [ ] Add conversation history memory so Jarvis retains multi-turn context.
- [ ] Craft a system prompt persona for concise, witty, and functional responses.

---

### ⚙️ Day 3: Local System Control & Automations (Upcoming)
- [ ] Implement an intent interceptor to catch commands locally before hitting the LLM API.
- [ ] Automate system diagnostics using `psutil` (CPU, RAM utilization, battery percentage).
- [ ] Add application launch routines (`subprocess`) and web shortcuts (`webbrowser`).

---

### 🎙️ Day 4: Wake-Word Detection (Upcoming)
- [ ] Eliminate manual keypress execution with continuous background listener loops.
- [ ] Implement keyword triggering for `"Jarvis"`.

---

### 🚀 Day 5: Latency Optimization & Packaging (Upcoming)
- [ ] Tune audio buffer chunk sizes to minimize round-trip speech latency.
- [ ] Handle network timeouts, API retries, and dropped internet connections gracefully.

---

## 📂 Repository Architecture

```text
Jarvis/
├── jarvis_env/          # Local virtual environment (ignored by Git)
├── .gitignore           # Git ignore patterns (protects secrets & venvs)
├── requirements.txt     # Locked project dependencies
├── README.md            # Active project log and setup guide
└── main.py              # Sensory loop and main execution script