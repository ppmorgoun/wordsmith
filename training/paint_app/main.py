from random import random
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.graphics import Color, Ellipse, Line

class MyPaintWidget(Widget):
    def on_touch_down(self, touch):
        color = (random(), 1., 1.)
        with self.canvas:
            Color(*color, mode='hsv')
            d = 4.
            Ellipse(pos=(touch.x - d/2, touch.y - d/2), size=(d, d))
            touch.ud['line'] = Line(points=(touch.x, touch.y))

    def on_touch_move(self, touch):
        touch.ud['line'].points += [touch.x, touch.y]
            

class MyPaintApp(App):

    def build(self):
        parent = Widget() # a dummy widget to hold our two children
        self.painter = MyPaintWidget() # instead of returning this widget directly, we bind it to a variable
        clearbtn = Button(text='Clear')
        clearbtn.bind(on_release=self.clear_canvas) #binding the button's on-release event to the call-back function clear_canvas
        parent.add_widget(self.painter) #assinging out painter widget to the parent
        parent.add_widget(clearbtn) # assigning our button to the parent
        return parent

    def clear_canvas(self, obj):
        self.painter.canvas.clear()

if __name__ == '__main__':
    MyPaintApp().run() 