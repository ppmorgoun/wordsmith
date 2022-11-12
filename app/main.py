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
        print("{} word means: {}".format(word_stripped, meaning))
        self.word_meaning = meaning

    def submit_new_word(self):
        word_stripped = self.new_word.text.strip()
        if word_stripped != '':
            word_bank[word_stripped] = self.word_meaning
        self.word_meaning = ''
        self.new_word.text = ''
        print([i for i in word_bank])

    


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
        self.data = [{'text': word, 'id': definition} for word, definition in word_bank.items()]
        #self.data = [{'text': "Button " + str(x), 'id': str(x)} for x in self.app.root.ids.enter_word.WORD_BANK]
    """ 
    def __init__(self, **kwargs):
        super(HomePage, self).__init__(**kwargs)
        Clock.schedule_once(self.after_init)

    def after_init(self, dt):
        self.data = [{'text': "Wordsmith", 'id': "A skilled user of words"}] """

    def update_word(self):
        self.data= [{'text': word, 'id': definition} for word, definition in word_bank.items()]   
        print('update word')

    def remove_word(self, word):
        del word_bank[word]
        self.update_word()
    

class Manager(ScreenManager):
    global word_bank
    word_bank = {}
    word_bank["Wordsmith"] = "A skilled user of words"
    homepagescreen = ObjectProperty(None)
    enterword = ObjectProperty(None)

class WordSmith(App):
    def build(self):
        sm = Manager(transition=NoTransition())
        return sm


WordApp = WordSmith()


if __name__ == '__main__':
    WordApp.run()
