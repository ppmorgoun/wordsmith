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
import mysql.connector
import sqlite3

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
        word_stripped = self.new_word.text.strip()
        meaning = str(self.dictionary.meaning(word_stripped))
        self.word_meaning = meaning

    def submit_new_word(self):
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
        p = WordBox()
        p.word = word
        p.definition = definition
        p.open()
        print("{} was pressed".format(word))

    def remove_word_box(self, word):
        p = RemoveWordBox()
        p.word = word
        p.open()
        print("{} was removed".format(word))



class HomePage(RecycleView):

    
    word_bank = ListProperty('')
    word = StringProperty()
    #app = App.get_running_app()
    def __init__(self, **kwargs):
        super(HomePage, self).__init__(**kwargs)
        conn = sqlite3.connect('data/wordbank.db')
        c = conn.cursor()
        c.execute("SELECT word, definition FROM words")
        word_row = c.fetchall()
        conn.close()

        self.data= [{'text': str(word), 'id': str(definition)} for word, definition in word_row]  

    """ 
    def __init__(self, **kwargs):
        super(HomePage, self).__init__(**kwargs)
        Clock.schedule_once(self.after_init)

    def after_init(self, dt):
        self.data = [{'text': "Wordsmith", 'id': "A skilled user of words"}] """

    def update_word(self):
        conn = sqlite3.connect('data/wordbank.db')
        c = conn.cursor()
        c.execute("SELECT word, definition FROM words")
        word_row = c.fetchall()
        conn.close()

        self.data= [{'text': str(word), 'id': str(definition)} for word, definition in word_row]   
        print('updated home page with words from db')

        

    def remove_word(self, word):
        """ del word_bank[word]
        self.update_word() """

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
    """ global word_bank
    word_bank = {}
    word_bank["Wordsmith"] = "A skilled user of words"
 """
    homepagescreen = ObjectProperty(None)
    enterword = ObjectProperty(None)

class WordSmith(App):
    def build(self):
        sm = Manager(transition=NoTransition())
        conn = sqlite3.connect('data/wordbank.db')
        c = conn.cursor()
        c.execute("""CREATE TABLE if not exists words(
			word VARCHAR(50), definition VARCHAR(300), bucket INT, UNIQUE(word))
		 """)
        c.execute("SELECT * FROM words")
        conn.commit()

        conn.close()


        return sm


WordApp = WordSmith()


if __name__ == '__main__':
    WordApp.run()
