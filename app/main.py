import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.recycleview import RecycleView
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition, SlideTransition
from kivy.properties import ObjectProperty, StringProperty, ListProperty
from kivy.clock import Clock
from PyDictionary import PyDictionary
import sqlite3
import os
import random
from datetime import datetime
from speech import Free_Google_ASR
import speech_recognition as sr

kivy.require('2.0.0')

class WordBox(Popup):
    word = StringProperty()
    definition = StringProperty()

class CopyWordbankBox(Popup):
    words = StringProperty()

class RemoveWordBox(Popup):
    word = StringProperty()

class DidntUnderstand(Popup):
    pass

class RecycleViewRow(BoxLayout):
    text = StringProperty()  

class SSLScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__()

    current_word = StringProperty()
    current_word_row = ObjectProperty()

    def fetchNextWord(self):
        # Get the next word from the database
        # will prioritse words with the lowest CI (current interval) and the oldest datetime
        # #word VARCHAR(50), definition VARCHAR(400), EF INT, CI INT, isGraduate BOOLEAN, time TEXT
        conn = sqlite3.connect('wordbank.db')
        c = conn.cursor()
        try:
            c.execute("SELECT * FROM words WHERE CI = (SELECT MIN(CI) FROM words)  AND time = (SELECT MIN(time) FROM (SELECT * FROM words WHERE CI = (SELECT MIN(CI) FROM words)))")
            word_row= c.fetchall() # this is a list of tuples
            self.current_word = word_row[0][0]
            self.current_word_row = word_row[0]
            print("Fetched word: {}".format(self.current_word_row))
        except:
            self.current_word = "No words"
            self.current_word_row = None
            print("No words in database")
        conn.close()
        self.ids.nextword.text = self.current_word


class SSLScreenMeaning(Screen):
    word_def = StringProperty("")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_pre_enter(self, *args):
        # get the definition of the current word
        app = App.get_running_app()
        try:
            current_word_row = app.root.sslscreen.current_word_row
        except:
            current_word_row = None

        if current_word_row:
            self.word = current_word_row[0]
            self.word_def = current_word_row[1] #word VARCHAR(50), definition VARCHAR(400), EF INT, CI INT, isGraduate BOOLEAN, time TEXT
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

    def updateCurrentWord(self, EFchange):
        # update the current word in the database
        #if self.isGraduate:
        if self.word != "No words":
            self.ef += EFchange
            if EFchange == -0.2:
                self.ci = 1
            else:
                self.ci = self.ci * self.ef
                
            if self.ef < 1.3:
                self.ef = 1.3

            self.time = int(datetime.now().strftime("%Y%m%d%H%M%S"))
            conn = sqlite3.connect('wordbank.db')
            c = conn.cursor()
            c.execute("UPDATE words SET EF = ?, CI = ?, time = ? WHERE word = ?", (self.ef, self.ci, self.time, self.word))
            conn.commit()
            conn.close()
            print("Updated word: ", self.word, "EF: ", self.ef, "CI: ", self.ci, "time: ", self.time)
        else:
            print("No words to update")

class EnterWord(Screen):
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
                sql_command = "INSERT INTO words (word, definition, EF, CI, isGraduate, time) VALUES (?, ?, ?, ?, ?, ?)"
                values = (word_stripped, self.word_meaning, 2.5, 1, False, int(datetime.now().strftime("%Y%m%d%H%M%S")))
                c.execute(sql_command, values)
                conn.commit()
                print("Word added to database")
            except:
                print('Error: word already exists in database')
            conn.close()

        self.word_meaning = ''
        self.new_word.text = ''


class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__()

    def copy_wordbank(self):
        # copies the wordbank database to the user's clipboard
        conn = sqlite3.connect('wordbank.db')
        c = conn.cursor()
        c.execute("SELECT word FROM words")
        words= c.fetchall() # this is a list of tuples
        conn.close()
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

    def __init__(self, **kwargs):
        super(HomePage, self).__init__(**kwargs)
        conn = sqlite3.connect('wordbank.db')
        c = conn.cursor()
        c.execute("SELECT word, definition FROM words")
        word_row = c.fetchall()
        conn.close()

        self.data= [{'text': str(word), 'id': str(definition)} for word, definition in word_row]  

    def update_word(self):
        # a popup called from the recycleviewrow that updates the database with a word, definition, and bucket
        conn = sqlite3.connect('wordbank.db')
        c = conn.cursor()
        c.execute("SELECT word, definition FROM words")
        word_row = c.fetchall() # this is a list of tuples
        conn.close()
        
        self.data= [{'text': str(word), 'id': str(definition)} for word, definition in word_row]   
        print("Updated home page with wordbank")

    def remove_word(self, word):
        # a popup called by the recycleviewrow that removes a word from the database
        conn = sqlite3.connect('wordbank.db')
        c = conn.cursor()
        sql_command = "DELETE FROM words WHERE word = ?"
        c.execute(sql_command, (word,))
        conn.commit()
        c.execute("SELECT word, definition FROM words")
        word_row = c.fetchall()
        conn.close()

        self.data= [{'text': str(word), 'id': str(definition)} for word, definition in word_row] 
    

class Manager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__()

    homepagescreen = ObjectProperty(None)
    enterword = ObjectProperty(None)
    settingsscreen = ObjectProperty(None)
    sslscreen = ObjectProperty(None) # spaced repitition learning screen
    sslscreenmeaning = ObjectProperty(None) # word definition spaced repitition learning screen


class WordSmith(App):
    def on_start(self) -> None:
        print(type(App.get_running_app()))
        print(type(App.get_running_app().root))
        print(type(App.get_running_app().root.get_screen('SSL Screen')))

    def build(self):
        path = './wordbank.db'
        if not os.path.exists(path): 
            # create our database if it doesn't exist
            # create a table for words
            conn = sqlite3.connect('wordbank.db')
            c = conn.cursor()
            c.execute("""CREATE TABLE if not exists words(
			word VARCHAR(50), definition VARCHAR(400), EF INT, CI INT, isGraduate BOOLEAN, time TEXT, UNIQUE(word))
		 """)
            conn.commit()

            # insert "wordsmith" and it's definition into words table
            c.execute("""INSERT INTO words (word, definition, EF, CI, isGraduate, time) VALUES ('Wordsmith', 'A skilled user of words', 2.5, 1, True, '{}')""".format(int(datetime.now().strftime("%Y%m%d%H%M%S"))))
            conn.commit()
            conn.close()
        
        sm = Manager(transition=NoTransition())
        return sm

WordApp = WordSmith()

if __name__ == '__main__':
    WordApp.run()
