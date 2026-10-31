import io
import os
import re
import pygame
import speech_recognition as sr
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError
from gtts import gTTS

# -----------------------------
# 1. ENVIRONMENT & LLM CLIENT SETUP
# -----------------------------
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY is not set. Please create a .env file and add your key."
    )

client = genai.Client(api_key=api_key)

# -----------------------------
# 2. AUDIO & SPEECH SETUP
# -----------------------------
pygame.mixer.init()

listener = sr.Recognizer()
# Reduced pause threshold for snappier cutoffs when you finish speaking
listener.pause_threshold = 0.6
listener.non_speaking_duration = 0.4
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
        "api_error": "I encountered an error connecting to my cognitive servers.",
        "bye": "Goodbye, shutting down.",
        "exit_words": ["exit", "stop", "quit", "shutdown"],
        "triggers": ["english", "one", "1", "first"],
        "system_instruction": (
            "You are Jarvis, a fast, witty, and highly intelligent personal AI assistant. "
            "You are communicating entirely via voice, so keep your answers clear, natural, and concise—"
            "ideally 1 to 2 sentences maximum. "
            "Never output markdown, asterisks, bullet points, or code blocks. Speak conversationally in English."
        ),
    },
    "hi": {
        "code": "hi",
        "sr_code": "hi-IN",
        "name": "Hindi",
        "tld": "com",
        "welcome": "जार्विस हिंदी मोड में तैयार है। कहिए, मैं क्या मदद करूँ?",
        "repeat": "मुझे समझ नहीं आया, क्या आप दोबारा बोल सकते हैं?",
        "offline": "इंटरनेट में समस्या आ रही है।",
        "api_error": "सर्वर से संपर्क करने में समस्या आ रही है।",
        "bye": "अलविदा, फिर मिलेंगे!",
        "exit_words": ["exit", "stop", "quit", "अलविदा", "बंद करो", "रुक जाओ"],
        "triggers": ["hindi", "हिंदी", "two", "2", "second"],
        "system_instruction": (
            "आप जार्विस हैं, एक बुद्धिमान और तेज़ आवाज़ सहायक। "
            "चूँकि आपका उत्तर आवाज़ (TTS) द्वारा बोला जाएगा, इसलिए उत्तर हमेशा छोटा, सरल और संवादात्मक रखें (अधिकतम 1-2 वाक्य)। "
            "बुलेट पॉइंट्स, मार्कडाउन या कोड का प्रयोग न करें। शुद्ध और सहज हिंदी में जवाब दें।"
        ),
    },
    "mr": {
        "code": "mr",
        "sr_code": "mr-IN",
        "name": "Marathi",
        "tld": "com",
        "welcome": "जार्विस मराठी मोडमध्ये सुरू झाला आहे. बोला, काय मदत करू?",
        "repeat": "मला समजले नाही, कृपया पुन्हा एकदा सांगा?",
        "offline": "इंटरनेटमध्ये अडचण येत आहे.",
        "api_error": "सर्व्हरशी संपर्क साधण्यात त्रुटी येत आहे.",
        "bye": "निरोप, काळजी घ्या!",
        "exit_words": ["exit", "stop", "quit", "थांब", "बंद कर", "निरोप"],
        "triggers": ["marathi", "मराठी", "three", "3", "third"],
        "system_instruction": (
            "तुम्ही जार्विस आहात, एक हुशार आणि कार्यक्षम व्हॉइस असिस्टंट. "
            "तुमचे उत्तर ऑडिओमध्ये बोलले जाणार असल्याने, उत्तर अगदी लहान, स्पष्ट आणि बोलण्यासारखे ठेवा (जास्तीत जास्त १ ते २ वाक्ये). "
            "मार्कडाउन, बुलेट पॉइंट्स किंवा तारे वापरू नका. सरळ आणि शुद्ध मराठीत संवाद साधा."
        ),
    },
}

# Fast multimodal model
MODEL_NAME = "gemini-2.5-flash"


# -----------------------------
# 3. CORE AUDIO & VOICE FUNCTIONS
# -----------------------------
def speak(text: str, lang_code: str = "en", tld: str = "co.in"):
    """Speaks out text using gTTS and pygame."""
    clean_text = text.strip()
    if not clean_text:
        return

    print(f"🤖 Jarvis: {clean_text}")

    try:
        tts = gTTS(text=clean_text, lang=lang_code, tld=tld, slow=False)
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
    """Captures microphone input and transcribes using specified speech-to-text language."""
    with sr.Microphone() as source:
        print("\n🎙️ Listening...")

        try:
            audio = listener.listen(source, timeout=6, phrase_time_limit=8)
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

        for lang_key, config in LANGUAGES.items():
            if any(trigger in response for trigger in config["triggers"]):
                speak(f"Selected {config['name']}.", lang_code="en")
                return config

        speak("I didn't recognize that language. Please say English, Hindi, or Marathi.", lang_code="en")


# -----------------------------
# 4. FAST GEMINI STREAMING ENGINE
# -----------------------------
class JarvisBrain:
    def __init__(self, system_instruction: str):
        self.system_instruction = system_instruction
        self.chat_session = client.chats.create(
            model=MODEL_NAME,
            config=types.GenerateContentConfig(
                system_instruction=self.system_instruction,
                temperature=0.6,
                # thinking_budget=0 eliminates reasoning delays for instant replies
                thinking_config=types.ThinkingConfig(thinking_budget=0),
            ),
        )

    def stream_sentences(self, user_prompt: str):
        """Streams tokens from Gemini and yields full sentences as soon as punctuation is reached."""
        buffer = ""
        response_stream = self.chat_session.send_message_stream(user_prompt)

        for chunk in response_stream:
            if not chunk.text:
                continue
            buffer += chunk.text

            # Splits on sentence punctuation across English, Hindi, and Marathi (. ? ! । newline)
            parts = re.split(r"([.?!।\n]+)", buffer)
            if len(parts) > 1:
                complete_sentence = "".join(parts[:-1]).strip()
                buffer = parts[-1]
                if complete_sentence:
                    yield complete_sentence

        if buffer.strip():
            yield buffer.strip()


# -----------------------------
# 5. MAIN RUN LOOP
# -----------------------------
def main():
    # 1. Calibrate background noise
    with sr.Microphone() as source:
        print("Calibrating microphone for room noise... (1 second)")
        listener.adjust_for_ambient_noise(source, duration=1.0)
        print("Microphone ready.")

    # 2. Voice-driven language selection
    current_lang = select_language_by_voice()

    # 3. Create persistent chat session
    brain = JarvisBrain(current_lang["system_instruction"])

    # 4. Greet user
    speak(
        current_lang["welcome"],
        lang_code=current_lang["code"],
        tld=current_lang.get("tld", "com"),
    )

    # 5. Main AI conversation loop
    while True:
        status, command = listen_raw(sr_language=current_lang["sr_code"])

        if status == "timeout":
            continue

        if status == "unclear":
            speak(
                current_lang["repeat"],
                lang_code=current_lang["code"],
                tld=current_lang.get("tld", "com"),
            )
            continue

        if status == "error":
            speak(
                current_lang["offline"],
                lang_code=current_lang["code"],
                tld=current_lang.get("tld", "com"),
            )
            continue

        # Exit check
        if is_exit_command(command, current_lang["exit_words"]):
            speak(
                current_lang["bye"],
                lang_code=current_lang["code"],
                tld=current_lang.get("tld", "com"),
            )
            break

        # Stream sentences from Gemini and speak each sentence immediately
        try:
            print("🧠 Jarvis is thinking...")
            for sentence in brain.stream_sentences(command):
                speak(
                    sentence,
                    lang_code=current_lang["code"],
                    tld=current_lang.get("tld", "com"),
                )
        except APIError as e:
            print(f"API Error: {e}")
            speak(
                current_lang["api_error"],
                lang_code=current_lang["code"],
                tld=current_lang.get("tld", "com"),
            )
        except Exception as e:
            print(f"Brain Error: {e}")
            speak(
                current_lang["api_error"],
                lang_code=current_lang["code"],
                tld=current_lang.get("tld", "com"),
            )


if __name__ == "__main__":
    main()