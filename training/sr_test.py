import speech_recognition as sr
from time import sleep
import keyboard # pip install keyboard

go = 1

def quit():
    global go
    print("q pressed, exiting...")
    go = 0

keyboard.on_press_key("q", lambda _:quit()) # press q to quit

r = sr.Recognizer()

mic = sr.Microphone()


while go:
    try:
        sleep(0.01)
        with mic as source:
            audio = r.listen(source)
            print(r.recognize_google(audio))
    except:
        print("error")