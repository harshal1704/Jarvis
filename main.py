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

LANGUAGES = {
    "en": {
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
        "triggers": ["english", "one", "1", "first"],
    },
    "hi": {
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
        "triggers": ["hindi", "हिंदी", "two", "2", "second"],
    },
    "mr": {
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
        "triggers": ["marathi", "मराठी", "three", "3", "third"],
    },
}


# -----------------------------
# 2. CORE FUNCTIONS
# -----------------------------
def speak(text: str, lang_code: str = "en", tld: str = "co.in"):
    """Speaks out text using gTTS and pygame."""
    print(f"🤖 Jarvis: {text}")

    try:
        tts = gTTS(text=text, lang=lang_code, tld=tld, slow=False)
        audio_stream = io.BytesIO()
        tts.write_to_fp(audio_stream)
        audio_stream.seek(0)

        pygame.mixer.music.load(audio_stream)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    except Exception as e:
        print(f"Audio playback error: {e}")


def listen_raw(sr_language: str = "en-IN") -> tuple[str, str]:
    """Captures microphone input and transcribes using specified speech-to-text language.

    Returns: (status, user_text)
    """
    with sr.Microphone() as source:
        print("\n🎙️ Listening...")

        try:
            audio = listener.listen(source, timeout=6, phrase_time_limit=6)
            print("⏳ Processing speech...")

            text = listener.recognize_google(audio, language=sr_language)
            print(f"👤 You said: '{text}'")
            return "success", text.strip().lower()

        except sr.WaitTimeoutError:
            return "timeout", ""
        except sr.UnknownValueError:
            return "unclear", ""
        except sr.RequestError:
            return "error", ""


def is_exit_command(text: str, exit_words: list) -> bool:
    """Checks for explicit exit commands while ignoring negations."""
    cleaned = text.lower().strip()

    negations = ["don't", "dont", "do not", "नको", "मत", "नाही"]
    if any(neg in cleaned for neg in negations):
        return False

    words = cleaned.split()
    return any(term in words or term == cleaned for term in exit_words)


def select_language_by_voice() -> dict:
    """Asks the user verbally to choose a language and detects the spoken answer."""
    prompt = "Please choose your language. Say English, Hindi, or Marathi."
    speak(prompt, lang_code="en", tld="co.in")

    while True:
        status, response = listen_raw(sr_language="en-IN")

        if status == "timeout":
            speak("I didn't hear your choice. Please say English, Hindi, or Marathi.", lang_code="en")
            continue

        if status == "unclear":
            speak("I couldn't understand. Please say English, Hindi, or Marathi clearly.", lang_code="en")
            continue

        if status == "error":
            speak("Internet connection error. Trying again...", lang_code="en")
            continue

        # Match spoken voice input to the corresponding language profile
        for lang_key, config in LANGUAGES.items():
            if any(trigger in response for trigger in config["triggers"]):
                speak(f"Selected {config['name']}.", lang_code="en")
                return config

        speak("I didn't recognize that language. Please say English, Hindi, or Marathi.", lang_code="en")


# -----------------------------
# 3. MAIN RUN LOOP
# -----------------------------
def main():
    # 1. Calibrate ambient noise on launch
    with sr.Microphone() as source:
        print("Calibrating microphone for room noise... (1 second)")
        listener.adjust_for_ambient_noise(source, duration=1.0)
        print("Microphone ready.")

    # 2. Select language purely by voice
    current_lang = select_language_by_voice()

    # 3. Greet in the chosen language
    speak(current_lang["welcome"], lang_code=current_lang["code"], tld=current_lang.get("tld", "com"))

    # 4. Continuous listening loop
    while True:
        status, command = listen_raw(sr_language=current_lang["sr_code"])

        if status == "timeout":
            continue

        if status == "unclear":
            speak(current_lang["repeat"], lang_code=current_lang["code"], tld=current_lang.get("tld", "com"))
            continue

        if status == "error":
            speak(current_lang["offline"], lang_code=current_lang["code"], tld=current_lang.get("tld", "com"))
            continue

        # Check for shutdown trigger with negation protection
        if is_exit_command(command, current_lang["exit_words"]):
            speak(current_lang["bye"], lang_code=current_lang["code"], tld=current_lang.get("tld", "com"))
            break

        # Echo captured command in the active language
        response_text = f"{current_lang['echo_prefix']}{command}"
        speak(response_text, lang_code=current_lang["code"], tld=current_lang.get("tld", "com"))


if __name__ == "__main__":
    main()