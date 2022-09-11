import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
import speechbrain as sb
from speech_recognition import recognise_word
import random

kivy.require('2.0.0')

class MyRoot(BoxLayout):
    def __init__(self):
        super(MyRoot, self).__init__()

    def listen(self):
        self.spoken_word.text = recognise_word()


class wordSmith(App):
    def build(self):
        return MyRoot()


wordApp = wordSmith()
wordApp.run()