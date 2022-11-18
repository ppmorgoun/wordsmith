import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.recycleview import RecycleView
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.properties import ObjectProperty, StringProperty, ListProperty
from kivy.clock import Clock
import pyperclip
from PyDictionary import PyDictionary
import sqlite3
import os
from speech import Free_Google_ASR
import speech_recognition as sr

__version__ = "0.1"
kivy.require('2.0.0')

class WordBox(Popup):
    word = StringProperty()
    definition = StringProperty()

class RemoveWordBox(Popup):
    word = StringProperty()

class DidntUnderstand(Popup):
    pass

class RecycleViewRow(BoxLayout):
    text = StringProperty()  

""" <RecycleViewRow>:
    orientation: 'horizontal'
    Label:
        text: root.text
        #text_size: root.width, root.height
        #font_size: self.texture
        #font_size: root.test_funct()
        #larger_font: min(10, self.font_size + 1)  # one point larger but not over maximum
        #on_texture_size:
            #if self.texture_size[0] > self.width: self.font_size -= 1  # reduce font size if too wide
            #elif self.texture_size[0] + self.font_size / 2 < self.width: self.font_size = self.larger_font 
    Button:
        text: 'Show definition'
        font_size: "10sp"
        on_release: app.root.homepagescreen.word_box(root.text, root.id)
    Button:
        text: "X"
        size_hint: 0.5, 1
        on_release: app.root.homepagescreen.remove_word_box(root.text) """
class SSLScreen(Screen):
    pass

class EnterWord(Screen):
    new_word = ObjectProperty(None)
    word_meaning = StringProperty('')

    # adjust for ambient noise
    recognizer = Free_Google_ASR()
    recognizer.adjust_for_ambient_noise()
    print("Adjusting for ambient noise...")

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

    def recognize_spoken_word(self):
        # uses the speech recognition module to recognize the spoken word
        
        guess = self.recognizer.get_command()

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
            conn = sqlite3.connect('data/wordbank.db')
            c = conn.cursor()
            try:
                sql_command = "INSERT INTO words (word, definition, bucket) VALUES (?, ?, ?)"
                values = (word_stripped, self.word_meaning, 1)
                c.execute(sql_command, values)
                conn.commit()
                print("Word added to database")
            except:
                print('Error: word already exists in database')
            
            conn.close()
            

        self.word_meaning = ''
        self.new_word.text = ''

class SettingsScreen(Screen):
    def copy_wordbank(self):
        # copies the wordbank database to the user's clipboard
        conn = sqlite3.connect('data/wordbank.db')
        c = conn.cursor()
        c.execute("SELECT word FROM words")
        words= c.fetchall() # this is a list of tuples
        conn.close()
        words = [i[0] for i in words]
        words = '\n'.join(words)
        print(words)


        pyperclip.copy(words)

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
        conn = sqlite3.connect('data/wordbank.db')
        c = conn.cursor()
        c.execute("SELECT word, definition FROM words")
        word_row = c.fetchall()
        conn.close()

        self.data= [{'text': str(word), 'id': str(definition)} for word, definition in word_row]  

    def update_word(self):
        # a popup called from the recycleviewrow that updates the database with a word, definition, and bucket
        conn = sqlite3.connect('data/wordbank.db')
        c = conn.cursor()
        c.execute("SELECT word, definition FROM words")
        word_row = c.fetchall() # this is a list of tuples
        conn.close()
        
        self.data= [{'text': str(word), 'id': str(definition)} for word, definition in word_row]   
        print("Updated home page with wordbank")

    def remove_word(self, word):
        # a popup called by the recycleviewrow that removes a word from the database
        conn = sqlite3.connect('data/wordbank.db')
        c = conn.cursor()
        sql_command = "DELETE FROM words WHERE word = ?"
        c.execute(sql_command, (word,))
        conn.commit()
        c.execute("SELECT word, definition FROM words")
        word_row = c.fetchall()
        conn.close()

        self.data= [{'text': str(word), 'id': str(definition)} for word, definition in word_row] 
    

class Manager(ScreenManager):
    homepagescreen = ObjectProperty(None)
    enterword = ObjectProperty(None)
    settingsscreen = ObjectProperty(None)
    sslscreen = ObjectProperty(None) # spaced repitition learning screen

class WordSmith(App):
    def build(self):
        path = './data/wordbank.db'
        if not os.path.exists(path): 
            # create our database if it doesn't exist
            # create a table for words
            conn = sqlite3.connect('data/wordbank.db')
            c = conn.cursor()
            c.execute("""CREATE TABLE if not exists words(
			word VARCHAR(50), definition VARCHAR(300), bucket INT, UNIQUE(word))
		 """)
            conn.commit()
            # insert "wordsmith" and it's definition into words table
            c.execute("""INSERT INTO words (word, definition, bucket) VALUES ('Wordsmith', 'A skilled user of words', 1)""")
            conn.commit()
            conn.close()

        sm = Manager(transition=NoTransition())
        return sm


WordApp = WordSmith()

if __name__ == '__main__':
    WordApp.run()
