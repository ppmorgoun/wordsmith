""" import kivy
from kivy.event import EventDispatcher

class MyEventDispatcher(EventDispatcher):
    def __init__(self, **kwargs):
        self.register_event_type('on_test')
        super(MyEventDispatcher, self).__init__(**kwargs)

    def do_something(self, value):
        # when do_something is called, the 'on_test' event will be
        # dispatched with the value
        self.dispatch('on_test', value)

    def on_test(self, *args):
        print("I am dispatched", args)

def my_callback(value, *args):
    print("Hello, I got an event!", args)


ev = MyEventDispatcher()
ev.bind(on_test=my_callback)
ev.do_something('test')
"""
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.popup import Popup
 
Builder.load_string('''
#:kivy 1.10.0
#: import Popup kivy.uix.popup

<MessageBox>:
    title: 'Popup Message Box'
    size_hint: None, None
    size: 400, 400

    BoxLayout:
        orientation: 'vertical'
        Label:
            text: root.message
        Button:
            size_hint: 1, 0.2
            text: 'OK'
            on_press: root.dismiss()

<RecycleViewRow>:
    orientation: 'horizontal'
    Label:
        text: root.text
    Button:
        text: 'Show'
        on_press: app.root.message_box(root.text)

<MainScreen>:
    viewclass: 'RecycleViewRow'
    RecycleBoxLayout:
        default_size: None, dp(56)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        orientation: 'vertical'                    
                    ''')

class MessageBox(Popup):
    message = StringProperty()

class RecycleViewRow(BoxLayout):
    text = StringProperty()   

class MainScreen(RecycleView):    
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.data = [{'text': "Button " + str(x), 'id': str(x)} for x in range(3)]

    def message_box(self, message):
        p = MessageBox()
        p.message = message
        p.open() 
        print('test press: ', message)

class TestApp(App):
    title = "RecycleView Direct Test"

    def build(self):
        return MainScreen()

if __name__ == "__main__":
    TestApp().run()