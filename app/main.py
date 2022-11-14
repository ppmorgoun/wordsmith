import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.recycleview import RecycleView
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.properties import ObjectProperty, StringProperty, ListProperty
from kivy.clock import Clock
from PyDictionary import PyDictionary
import sqlite3
import os
__version__ = "0.1"
kivy.require('2.0.0')

class WordBox(Popup):
    word = StringProperty()
    definition = StringProperty()

class RemoveWordBox(Popup):
    word = StringProperty()

class RecycleViewRow(BoxLayout):
    text = StringProperty()  

class EnterWord(Screen):
    new_word = ObjectProperty(None)
    word_meaning = StringProperty('')

    dictionary=PyDictionary()

    def search_word_meaning(self):
        # searches for the meaning of the word entered in the text input
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

    def submit_new_word(self):
        # writes a word, it's meaning, and the default bucket number to the database
        word_stripped = self.new_word.text.strip().capitalize()
        if word_stripped != '':
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
        word_row = c.fetchall()
        conn.close()

        self.data= [{'text': str(word), 'id': str(definition)} for word, definition in word_row]   
        print('updated home page with words from db')

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
