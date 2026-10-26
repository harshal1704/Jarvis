import pyttsx3
import speech_recognition as sr

# -----------------------------
# 1. SETUP ENGINES
# -----------------------------
# Initialize text-to-speech
speaker = pyttsx3.init()
speaker.setProperty("rate", 175)

# Initialize speech recognizer
listener = sr.Recognizer()

# Crucial Tuning:
# - pause_threshold: how many seconds of silence before it stops listening (default 0.8s)
#   If you pause while thinking, increase this to 1.2s so it doesn't cut you off early!
listener.pause_threshold = 1.2


# -----------------------------
# 2. CORE FUNCTIONS
# -----------------------------
def speak(text):
    """Speaks out any text string passed to it."""
    print(f"🤖 Jarvis: {text}")
    speaker.say(text)
    speaker.runAndWait()


def listen():
    """Captures microphone input and returns a clean text string."""
    with sr.Microphone() as source:
        print("\n🎙️ Listening... (Speak now)")
        
        # Continuously adapt to changing ambient noise
        listener.adjust_for_ambient_noise(source, duration=0.8)

        try:
            # Capture speech from mic
            audio = listener.listen(source, timeout=6, phrase_time_limit=6)
            print("⏳ Processing your words...")

            # Transcribe using Indian English grammar dictionary
            text = listener.recognize_google(audio, language="en-IN")
            print(f"👤 You said: '{text}'")
            return text.lower()

        except sr.WaitTimeoutError:
            # You waited too long before speaking
            return ""

        except sr.UnknownValueError:
            # Voice was detected, but the sound wave was too muffled to identify words
            print("❌ Could not understand audio. Try speaking closer to the mic.")
            return ""

        except sr.RequestError:
            # Internet drop
            print("❌ Internet connection error reaching speech servers.")
            return ""


# -----------------------------
# 3. MAIN RUN LOOP
# -----------------------------
def main():
    speak("Jarvis is online and ready.")

    while True:
        command = listen()

        # If nothing was heard or it was silent, continue waiting
        if not command:
            continue

        # Check if you asked to quit
        if "exit" in command or "stop" in command or "quit" in command:
            speak("Goodbye, shutting down.")
            break

        # Day 1 Goal: Echo back what was spoken
        speak(f"I heard you say: {command}")


if __name__ == "__main__":
    main()