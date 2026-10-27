import io
import re
import pygame
import speech_recognition as sr
from gtts import gTTS

# -----------------------------
# 1. SETUP AUDIO & RECOGNIZER
# -----------------------------
pygame.mixer.init()

listener = sr.Recognizer()
listener.pause_threshold = 1.0
listener.dynamic_energy_adjustment_damping = 0.15
listener.dynamic_energy_ratio = 1.5

# Language configurations dictionary
LANGUAGES = {
    "1": {
        "code": "en",
        "sr_code": "en-IN",
        "name": "English",
        "tld": "co.in",
        "welcome": "Jarvis is online in English mode. How can I help you?",
        "repeat": "I didn't catch that, could you please repeat?",
        "offline": "Network error reaching speech servers.",
        "echo_prefix": "I heard you say: ",
        "bye": "Goodbye, shutting down.",
        "exit_words": ["exit", "stop", "quit", "shutdown"],
    },
    "2": {
        "code": "hi",
        "sr_code": "hi-IN",
        "name": "Hindi",
        "tld": "com",
        "welcome": "जार्विस हिंदी मोड में तैयार है। कहिए, मैं क्या मदद करूँ?",
        "repeat": "मुझे समझ नहीं आया, क्या आप दोबारा बोल सकते हैं?",
        "offline": "इंटरनेट में समस्या आ रही है।",
        "echo_prefix": "मैंने सुना: ",
        "bye": "अलविदा, फिर मिलेंगे!",
        "exit_words": ["exit", "stop", "quit", "अलविदा", "बंद करो", "रुक जाओ"],
    },
    "3": {
        "code": "mr",
        "sr_code": "mr-IN",
        "name": "Marathi",
        "tld": "com",
        "welcome": "जार्विस मराठी मोडमध्ये सुरू झाला आहे. बोला, काय मदत करू?",
        "repeat": "मला समजले नाही, कृपया पुन्हा एकदा सांगा?",
        "offline": "इंटरनेटमध्ये अडचण येत आहे.",
        "echo_prefix": "तुम्ही म्हणालात: ",
        "bye": "निरोप, काळजी घ्या!",
        "exit_words": ["exit", "stop", "quit", "थांब", "बंद कर", "निरोप"],
    },
}


# -----------------------------
# 2. CORE FUNCTIONS
# -----------------------------
def speak(text: str, lang_config: dict):
    """Speaks out text in the chosen language using gTTS and pygame."""
    print(f"🤖 Jarvis: {text}")

    try:
        tts = gTTS(
            text=text,
            lang=lang_config["code"],
            tld=lang_config.get("tld", "com"),
            slow=False,
        )
        audio_stream = io.BytesIO()
        tts.write_to_fp(audio_stream)
        audio_stream.seek(0)

        pygame.mixer.music.load(audio_stream)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    except Exception as e:
        print(f"Audio playback error: {e}")


def listen(lang_config: dict) -> tuple[str, str]:
    """Captures microphone input and transcribes based on chosen language.

    Returns: (status, user_text)
    """
    with sr.Microphone() as source:
        print(f"\n🎙️ Listening... (Speak in {lang_config['name']})")

        try:
            audio = listener.listen(source, timeout=6, phrase_time_limit=8)
            print("⏳ Processing speech...")

            text = listener.recognize_google(audio, language=lang_config["sr_code"])
            print(f"👤 You said: '{text}'")
            return "success", text.strip()

        except sr.WaitTimeoutError:
            return "timeout", ""
        except sr.UnknownValueError:
            return "unclear", ""
        except sr.RequestError:
            return "error", ""


def is_exit_command(text: str, exit_words: list) -> bool:
    """Checks for explicit exit commands while ignoring negations like 'don't

    stop'.
    """
    cleaned = text.lower().strip()

    # Negation words in English, Hindi, and Marathi
    negations = ["don't", "dont", "do not", "नको", "मत", "नाही"]
    if any(neg in cleaned for neg in negations):
        return False

    # Check for exact whole-word triggers
    words = cleaned.split()
    return any(term in words or term == cleaned for term in exit_words)


def choose_language() -> dict:
    """Terminal prompt to select the active language profile."""
    print("\n==============================")
    print("   CHOOSE JARVIS LANGUAGE     ")
    print("==============================")
    print("1. English (Indian Accent)")
    print("2. Hindi (हिंदी)")
    print("3. Marathi (मराठी)")
    print("==============================")

    while True:
        choice = input("Enter choice (1, 2, or 3): ").strip()
        if choice in LANGUAGES:
            selected = LANGUAGES[choice]
            print(f"\n✅ Mode selected: {selected['name']}\n")
            return selected
        print("Invalid choice. Please type 1, 2, or 3.")


# -----------------------------
# 3. MAIN RUN LOOP
# -----------------------------
def main():
    current_lang = choose_language()

    # Calibrate ambient microphone noise once at start
    with sr.Microphone() as source:
        print("Calibrating microphone for room noise... (1 second)")
        listener.adjust_for_ambient_noise(source, duration=1.0)
        print("Microphone ready.")

    speak(current_lang["welcome"], current_lang)

    while True:
        status, command = listen(current_lang)

        if status == "timeout":
            continue

        if status == "unclear":
            speak(current_lang["repeat"], current_lang)
            continue

        if status == "error":
            speak(current_lang["offline"], current_lang)
            continue

        # Check for shutdown trigger with negation protection
        if is_exit_command(command, current_lang["exit_words"]):
            speak(current_lang["bye"], current_lang)
            break

        # Echo captured command in the active language
        speak(f"{current_lang['echo_prefix']}{command}", current_lang)


if __name__ == "__main__":
    main()