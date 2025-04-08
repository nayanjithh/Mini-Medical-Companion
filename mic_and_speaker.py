import speech_recognition as sr
import requests
import base64
import io
import pygame

recognizer = sr.Recognizer()
GOOGLE_CLOUD_API = "AIzaSyDncunQw_iIj5afY5S1WYhzRkp3p3Tchzo"
speaking = False

# 🎤 Initialize mic and source ONCE when the module is loaded
mic = sr.Microphone()
with mic as source:
    print("Adjusting for ambient noise...")
    recognizer.adjust_for_ambient_noise(source, duration=5)
    print("Microphone ready.")
    
source = mic

def listen():
    global speaking
    try:
        if not speaking:
            with source as s:
                audio = recognizer.listen(s, timeout=5)
            user_input = recognizer.recognize_google(audio)
            return user_input
    except sr.WaitTimeoutError:
        print(".")
    except sr.UnknownValueError:
        print("Chatbot: Sorry, I couldn't understand you.")
    except sr.RequestError as e:
        print(f"Error with speech recognition: {e}")
    return None

def speak(user_input):
    global speaking
    url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={GOOGLE_CLOUD_API}"
    request_body = {
        "input": {"text": user_input},
        "voice": {"languageCode": "en-US", "ssmlGender": "NEUTRAL"},
        "audioConfig": {"audioEncoding": "MP3"}
    }

    response = requests.post(url, json=request_body)
    if response.status_code == 200:
        audio_content = response.json()["audioContent"]
        audio_data = base64.b64decode(audio_content)
        pygame.mixer.init()
        sound = pygame.mixer.Sound(io.BytesIO(audio_data))
        sound.play()
        speaking = True
        while pygame.mixer.get_busy():
            pygame.time.Clock().tick(10)
        speaking = False
    else:
        print("TTS Error:", response.status_code, response.text)

if __name__ == "__main__":
    while True:
        text = listen()
        if text:
            print("You said:", text)
            speak("You said: " + text)