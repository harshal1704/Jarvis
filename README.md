# ⚡ Jarvis: Building My Personal AI Voice Assistant from Scratch

A 5-day build log documenting the development of an intelligent, multilingual voice assistant in Python. This project covers the full pipeline: capturing raw microphone audio, handling real-time speech recognition, integrating large language models for reasoning, automating local system workflows, and implementing low-latency wake-word detection.

---

## 🛠️ Tech Stack & Tools

- **Core Language:** Python 3.10+
- **Input (Ears):** `SpeechRecognition`, `PyAudio` (tuned for `en-IN`, `hi-IN`, `mr-IN`)
- **Reasoning Engine (Brain):** Google Gemini API (`google-genai` SDK)
- **Output (Voice):** `gTTS` with in-memory `pygame.mixer` streaming
- **Environment & Control:** Virtual environment (`venv`), Git, `python-dotenv`

---

## 📅 Daily Build Progress

### 📦 Day 1: Setup, Audio Calibration & Sensory Systems (Completed)
Focused on establishing the foundational audio I/O pipeline and troubleshooting hardware/acoustic constraints:

- [x] **Isolated Environment Setup:** Configured an isolated virtual environment (`jarvis_env`) and added strict `.gitignore` rules to safeguard environment variables and system binaries from version control.
- [x] **Microphone Calibration & Audio Pipeline:** Resolved PyAudio device binding and sound card clipping issues. Reconfigured dynamic thresholding and set `pause_threshold = 1.2s` to eliminate premature audio cutoff.
- [x] **Acoustic Localization (`en-IN`):** Swapped default phoneme recognition to Indian English (`en-IN`), correcting transcription failures caused by accent and ambient room reflection.
- [x] **Offline Speech Synthesis:** Integrated `pyttsx3` with tuned speech rates (175 wpm) for low-latency, fully offline voice replies.
- [x] **Continuous Echo Loop:** Built an end-to-end interactive loop that listens, transcribes cleanly, logs to console, and repeats back user speech before gracefully terminating on exit commands.

---

### 🧠 Day 2: Cognitive Integration, Multilingual Voice & The Latency Bottleneck (In Progress / Investigating)
Focused on integrating LLM reasoning, conversational multilingual support, and confronting a major round-trip latency hurdle:

- [x] **SDK & Secure Credential Architecture:** Configured `google-genai` and `python-dotenv` to isolate `GEMINI_API_KEY` inside `.env`, maintaining strict security hygiene.
- [x] **Voice-Driven Multilingual Interface:** Implemented a hands-free, zero-keystroke startup routine. Jarvis verbally prompts for language choice and activates models for Indian English (`en-IN`), Hindi (`hi-IN`), or Marathi (`mr-IN`).
- [x] **In-Memory Audio Streaming:** Connected `gTTS` with `io.BytesIO` and `pygame.mixer` to eliminate temporary disk I/O overhead.
- [x] **Negation-Aware Intent Filtering:** Engineered custom exit-matching logic (`is_exit_command`) to prevent premature shutdowns on negated commands (e.g., distinguishing *"don't stop"* from explicit shutdown triggers).
- [!] **🚨 Critical Bug Encountered: Severe LLM Response Latency (2–3 Minute Delays)**
  - During live testing, the system stalls at `🧠 Jarvis is thinking...`, taking anywhere from 90 seconds to 3 minutes to return and vocalize an answer.

---

### ⚙️ Day 3: Local System Control & Automations (Upcoming)
- [ ] Implement an intent interceptor to catch commands locally before hitting the LLM API.
- [ ] Automate system diagnostics using `psutil` (CPU, RAM utilization, battery percentage).
- [ ] Add application launch routines (`subprocess`) and web shortcuts (`webbrowser`).

---

### 🎙️ Day 4: Wake-Word Detection (Upcoming)
- [ ] Eliminate manual script triggers with continuous background listener loops.
- [ ] Implement keyword triggering for `"Jarvis"`.

---

### 🚀 Day 5: Latency Optimization & Packaging (Upcoming)
- [ ] Tune audio buffer chunk sizes to minimize speech-to-text latency.
- [ ] Handle network timeouts, API retries, and dropped internet connections gracefully.

---

## 📂 Repository Architecture

```text
Jarvis/
├── jarvis_env/          # Local virtual environment (ignored by Git)
├── .gitignore           # Git ignore patterns (protects secrets & venvs)
├── requirements.txt     # Locked project dependencies
├── README.md            # Active project log, issue tracking, and roadmap
└── main.py              # Sensory loop, streaming brain engine, and main execution script
```