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


# -----------------------------
# 2. CORE FUNCTIONS
# -----------------------------
def is_devanagari(text: str) -> bool:
    """Checks if text contains Hindi/Marathi (Devanagari) characters."""
    return bool(re.search(r"[\u0900-\u097F]", text))


def speak(text: str, lang: str = "en"):
    """
    Speaks out text using gTTS and pygame.
    lang can be 'en', 'hi', or 'mr'.
    """
    print(f"🤖 Jarvis: {text}")

    # Set appropriate language parameters
    if lang == "mr":
        tts = gTTS(text=text, lang="mr", slow=False)
    elif lang == "hi":
        tts = gTTS(text=text, lang="hi", slow=False)
    else:
        # Indian English pronunciation
        tts = gTTS(text=text, lang="en", tld="co.in", slow=False)

    try:
        audio_stream = io.BytesIO()
        tts.write_to_fp(audio_stream)
        audio_stream.seek(0)

        pygame.mixer.music.load(audio_stream)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    except Exception as e:
        print(f"Audio playback error: {e}")


def listen():
    """
    Captures microphone input and attempts detection in:
    1. Indian English ('en-IN')
    2. Hindi ('hi-IN')
    3. Marathi ('mr-IN')
    Returns: (status, recognized_text, language_code)
    """
    with sr.Microphone() as source:
        print("\n🎙️ Listening... (Speak in English, Hindi, or Marathi)")

        try:
            audio = listener.listen(source, timeout=6, phrase_time_limit=8)
            print("⏳ Processing...")

            # Attempt 1: Indian English
            try:
                text = listener.recognize_google(audio, language="en-IN")
                print(f"👤 You said (EN): '{text}'")
                return "success", text.lower().strip(), "en"
            except sr.UnknownValueError:
                pass

            # Attempt 2: Hindi
            try:
                text = listener.recognize_google(audio, language="hi-IN")
                print(f"👤 You said (HI): '{text}'")
                return "success", text.strip(), "hi"
            except sr.UnknownValueError:
                pass

            # Attempt 3: Marathi
            try:
                text = listener.recognize_google(audio, language="mr-IN")
                print(f"👤 You said (MR): '{text}'")
                return "success", text.strip(), "mr"
            except sr.UnknownValueError:
                return "unclear", "", ""

        except sr.WaitTimeoutError:
            return "timeout", "", ""
        except sr.RequestError:
            return "error", "", ""


# -----------------------------
# 3. MAIN RUN LOOP
# -----------------------------
def main():
    speak("Jarvis is online and ready.", lang="en")

    # Calibrate ambient noise once at startup
    with sr.Microphone() as source:
        print("Calibrating room noise... (1 second)")
        listener.adjust_for_ambient_noise(source, duration=1.0)
        print("Calibration complete.")

    while True:
        status, command, lang = listen()

        if status == "unclear":
            speak("I didn't catch that, could you repeat?", lang="en")
            continue

        if status == "timeout":
            continue

        if status == "error":
            speak("Network error reaching speech servers.", lang="en")
            continue

        # Exit conditions
        exit_phrases = ["exit", "stop", "quit", "अलविदा", "बंद करो", "थांब", "बंद कर"]
        if any(term in command.lower() for term in exit_phrases):
            if lang == "mr":
                speak("निरोप, काळजी घ्या!", lang="mr")
            elif lang == "hi":
                speak("अलविदा, फिर मिलेंगे!", lang="hi")
            else:
                speak("Goodbye, shutting down.", lang="en")
            break

        # Response in matching language
        if lang == "mr":
            speak(f"तुम्ही म्हणालात: {command}", lang="mr")
        elif lang == "hi":
            speak(f"मैंने सुना: {command}", lang="hi")
        else:
            speak(f"I heard you say: {command}", lang="en")


if __name__ == "__main__":
    main()