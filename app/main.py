import os
import random
from datetime import datetime
import sqlite3

import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.recycleview import RecycleView
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition, SlideTransition
from kivy.properties import ObjectProperty, StringProperty, ListProperty, NumericProperty
from kivy.clock import Clock

from PyDictionary import PyDictionary
import speech_recognition as sr

from speech import Free_Google_ASR
from db_functions import create_table, add_word, fetch_word, fetch_next_word, fetch_all_words, fetch_all_words_with_defs, update_word, delete_word

kivy.require('2.0.0')

class WordBox(Popup):
    """ The popup for a word in the wordbank that displays it's definition"""
    word = StringProperty()
    definition = StringProperty()

class CopyWordbankBox(Popup):
    """ The popup for copying the wordbank to the clipboard"""
    words = StringProperty()

class RemoveWordBox(Popup):
    """ The popup for removing a word from the wordbank"""
    word = StringProperty()

class DidntUnderstand(Popup):
    """ The popup for when the user says something that the app doesn't understand"""
    pass

class RecycleViewRow(BoxLayout):
    """ The row for the recycle view in the homepage screen"""
    text = StringProperty()  

class WordMeaningScreen(Screen):
    """ The screen for the word meaning screen"""
    word = StringProperty()
    definition = StringProperty()
    ef = NumericProperty()
    ci = NumericProperty()
    isGraduate = NumericProperty()
    time = NumericProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def change_word(self, word):
        self.word = word
        word_row = fetch_word(word)
        print(repr(word_row))
        self.definition = word_row[1] 
        self.ef = word_row[2]
        self.ci = word_row[3]
        self.isGraduate = word_row[4]
        self.time = word_row[5]

    def update_word(self, **kwargs):
            # was updateCurrentWord
            # update the current word in the database

            word_params = {'word', 'definition', 'EF', 'CI', 'isGraduate', 'time'}
            changed_CI = False

            for key, value in kwargs.items():
                if key == 'EF':
                    # implementing EF change logic
                    self.ef += value
                    if key == -0.2:
                        self.ci = 1
                        changed_CI = True
                    else:
                        self.ci = self.ci * self.ef
                    if self.ef < 1.3:
                        """less than 1.3 creates a frusttrating experience for the user where it takes
                        forever to get the word to a higher EF"""
                        self.ef = 1.3
                elif key == 'CI':
                    # logic to prevent CI from being updated in the case it has been reset to 1 due to 
                    # a user selecting "Again"
                    if changed_CI == True:
                        continue
                    else:
                        self.ci = value
                elif key in word_params:
                    setattr(self, key, value)
                else:
                    raise TypeError(f"Invalid argument: {key}")

            self.time = int(datetime.now().strftime("%Y%m%d%H%M%S"))    

            try:
                update_word(word=self.word, definition=self.definition, EF=self.ef, CI=self.ci, isGraduate=self.isGraduate, time=self.time)
                print("Updated word: ", self.word, "EF: ", self.ef, "CI: ", self.ci, "time: ", self.time)
            except Exception as e:
                print("Error updating word: ", repr(e))

class EditWordMeaningScreen(Screen):
    word = StringProperty()
    word_def = StringProperty()

    def current_word(self, word, word_def):
        self.word = word
        self.word_def = word_def

class SSLScreen(Screen):
    """ The first screen for the spaced repetition learning system,
    which displays the word to be defined.
    
    Attributes:
        current_word (str): The current word to be defined
        current_word_row (tuple): The row of the current word in the database"""
    def __init__(self, **kwargs):
        super().__init__()

    current_word = StringProperty()
    current_word_row = ObjectProperty()
 
    def fetchNextWord(self):
        # Get the next word from the database
        # will prioritse words with the lowest CI (current interval) and the oldest datetime
        # #word VARCHAR(50), definition VARCHAR(400), EF INT, CI INT, isGraduate BOOLEAN, time TEXT
        try:
            word_row= fetch_next_word()
            print(word_row)
            self.current_word = word_row[0][0]
            self.current_word_row = word_row[0]
            print(f"Fetched word: {self.current_word_row}")
        except Exception as e:
            self.current_word = "No words"
            self.current_word_row = None
            print("No words in database: exception: ", repr(e))

        self.ids.nextword.text = self.current_word


class SSLScreenMeaning(Screen):
    """ The second screen for the spaced repetition learning system, which shows 
    the definition of the word and allows the user to select the difficulty of the word."""
    word_def = StringProperty("")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_pre_enter(self, *args):
        app = App.get_running_app()
        try:
            current_word_row = app.root.sslscreen.current_word_row
        except:
            current_word_row = None

        if current_word_row:
            #word VARCHAR(50), definition VARCHAR(400), EF INT, CI INT, isGraduate BOOLEAN, time TEXT
            self.word = current_word_row[0]
            self.word_def = current_word_row[1] 
            self.ef = current_word_row[2]
            self.ci = current_word_row[3]
            self.isGraduate = current_word_row[4]
            self.time = current_word_row[5]
        else:
            self.word = "No words"
            self.word_def = "No words"
            self.ef = 0
            self.ci = 0
            self.isGraduate = 0
            self.time = 0

    
class EnterWord(Screen):
    """ The screen for entering a new word into the database
        Includes voice recognition and a dictionary search

    Attributes:
        new_word (str): The word entered by the user
        word_meaning (str): The definition of the word entered by the user
        recognizer (Free_Google_ASR): The voice recognition object
        dictionary (PyDictionary): The dictionary object
    """
    def __init__(self, **kwargs):
        super().__init__()

    new_word = ObjectProperty(None)
    word_meaning = StringProperty('')

    recognizer = Free_Google_ASR()

    dictionary=PyDictionary()

    def search_word_meaning(self):
        # searches for the meaning of the word entered in the text input
        if self.new_word.text == '':
            return
        word_stripped = self.new_word.text.strip()
        meaning = self.dictionary.meaning(word_stripped)
        if meaning is not None:
            meaning_cleaned = self.unwrap_definition(meaning)
            self.word_meaning = meaning_cleaned
        else:
            self.word_meaning = 'Word not found'

    def unwrap_definition(self, meaning):
        meaning_clean = ''
        for i, j in meaning.items():
            sub_meaning = '{type}: \n'.format(type = i)
            for m in j:
                sub_meaning += m.capitalize() + ';\n'
            meaning_clean += sub_meaning + '\n\n'
        return meaning_clean

    def check_state(self, dt):
        pass
     # checks if the speech recognition module is listening for a word
        if not self.recognizer.response["success"]:
            print("Listening...")
        else:
            print('Recognized')
            Clock.unschedule(self.check_state)

        
    def recognize_spoken_word(self):
         # uses the speech recognition module to recognize the spoken word
        
        guess = self.recognizer.get_command()

        Clock.schedule_interval(self.check_state, 1 / 5)

        if guess["transcription"]:
            self.new_word.text = guess["transcription"]
            print("You said: {}".format(guess["transcription"]))

        elif guess["error"] == "Unable to recognize speech":
            # adding an error popup for when the speech recognition module can't recognize the word
            
            layout = BoxLayout(orientation='vertical')
            btn1 = Button(text='Ok', size_hint= (1, 0.2))
            label = Label(text='Unable to recognize speech, please try again. Alternatively please type the word instead', size_hint= (1, 0.8), text_size= (350, None))
            layout.add_widget(label)
            layout.add_widget(btn1)
            #layout.children[1].config(text_size=(layout.children[1].width, None), halign='center', valign='middle')
            popup = Popup(title='Error', content=layout, auto_dismiss=False, size_hint=(None, None), size=(400, 400))
            btn1.bind(on_press=popup.dismiss)
            popup.open()


    def submit_new_word(self):
        # writes a word, it's meaning, and the default bucket number to the database     
        if self.new_word.text != '':
            word_stripped = self.new_word.text.strip().capitalize()
            conn = sqlite3.connect('wordbank.db')
            c = conn.cursor()
            try:
                add_word(word=word_stripped, definition=self.word_meaning)
                print(f"Word \"{word_stripped}\" added to database")
            except Exception as e:
                print('Error: ', repr(e))

        self.word_meaning = ''
        self.new_word.text = ''


class SettingsScreen(Screen):
    """ The screen for changing the settings of the app
    Currently only allows the user to copy the wordbank to your clipboard"""
    def __init__(self, **kwargs):
        super().__init__()

    def copy_wordbank(self):
        # copies the wordbank database to the user's clipboard
        word = fetch_all_words()
        words = [i[0] for i in words]
        words = '\n'.join(words)
        print(words)
        return words
    
    def copy_wordbank_box(self):
        # opens a popup with the wordbank database
        words = self.copy_wordbank()
        p = CopyWordbankBox()
        p.words = words
        p.open()
        print("Copy wordbank popup was shown")


class HomePageScreen(Screen):
    """ The screen for the homepage of the app """
    def __init__(self, **kwargs):
        super().__init__()

    def word_box(self, word, definition):
        # this is a popup that shows the word and definition
        p = WordBox()
        p.word = word
        p.definition = definition
        p.open()
        print("{}'s definition was shown".format(word))

    def remove_word_box(self, word):
        # this is a popup that asks if you want to remove the word
        p = RemoveWordBox()
        p.word = word
        p.open()
        print("{} was removed".format(word))
    

class HomePage(RecycleView):
    """ The recycleview portion of the homepage that shows all the words in the database"""

    def __init__(self, **kwargs):
        super(HomePage, self).__init__(**kwargs)

        words_with_defs = fetch_all_words_with_defs()
        self.data= [{'text': str(word), 'id': str(definition)} for word, definition in words_with_defs]  

    def update_wordbank(self):
        # a popup called from the recycleviewrow that updates the database with a word, definition, and bucket

        words_with_defs = fetch_all_words_with_defs()
        self.data= [{'text': str(word), 'id': str(definition)} for word, definition in words_with_defs] 

        print("Updated home page with wordbank")

    def remove_word(self, word):
        # a popup called by the recycleviewrow that removes a word from the database
        delete_word(word)
        print(f"Removed word: \"{word}\" from database")

        words_with_defs = fetch_all_words_with_defs()
        self.data= [{'text': str(word), 'id': str(definition)} for word, definition in words_with_defs] 
    

class Manager(ScreenManager):
    """ The screen manager for the app
    This is where all the screens are defined """
    def __init__(self, **kwargs):
        super().__init__()

    homepagescreen = ObjectProperty(None)
    enterword = ObjectProperty(None)
    settingsscreen = ObjectProperty(None)
    sslscreen = ObjectProperty(None) # spaced repitition learning screen
    sslscreenmeaning = ObjectProperty(None) # word definition spaced repitition learning screen
    wordmeaningscreen = ObjectProperty(None) # word definition screen


class WordSmith(App):
    """ The main app class """
    def on_start(self) -> None:
        print(type(App.get_running_app()))
        print(type(App.get_running_app().root))
        print(type(App.get_running_app().root.get_screen('SSL Screen')))

    def build(self):
        create_table()
    
        sm = Manager(transition=NoTransition())
        return sm

WordApp = WordSmith()

if __name__ == '__main__':
    WordApp.run()
