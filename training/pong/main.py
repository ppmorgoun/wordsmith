from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock
from random import randint

class PongPaddle(Widget):
    score = NumericProperty(0)

    def bounce_ball(self, ball):
        if self.collide_widget(ball):
            vx, vy = ball.velocity
            offset = (ball.center_y - self.center_y) / (self.height / 2)
            bounced = Vector(-1 * vx, vy)
            vel = bounced * 1.1
            ball.velocity = vel.x, vel.y + offset

class PongBall(Widget):

    # velocity of the ball on x and y axis
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    # ``move`` function will move the ball one step. This
    #  will be called in equal intervals to animate the ball
    def move(self):
        self.pos = Vector(*self.velocity) + self.pos

class PongGame(Widget):

    ball = ObjectProperty(None) # need to set this object property so that the kv file references the same ball as below
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)

    pressed_keys = {
        'w': False,
        's': False,
        'o': False,
        'l': False
    }


    def __init__(self):
        super(PongGame, self).__init__()
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down = self._on_keyboard_down)
        self._keyboard.bind(on_key_up = self._on_keyboard_up)


    def _keyboard_closed (self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None


    def _on_keyboard_down (self, keyboard, keycode, text, modifiers):
        #pressed_key = self._keyboard.keycode_to_string(keycode) # this does not work somehow
        pressed_key = keycode[1]
        print('You pressed the key', pressed_key, '.', sep=' ', end='\n')

        self.pressed_keys[pressed_key] = True

        return True


    def _on_keyboard_up (self, keyboard, keycode):
        released_key = keycode[1]
        print('You released the key', released_key, '.', sep=' ', end='\n')
        self.pressed_keys[released_key] = False
        return True

    def serve_ball(self, vel=(4, 0)):
        self.ball.center = self.center
        self.ball.velocity = vel

    def update(self, dt):
        self.ball.move()

        self.player1.bounce_ball(self.ball)
        self.player2.bounce_ball(self.ball)

        if (self.ball.y < 0) or (self.ball.top > self.height):
            self.ball.velocity_y *= -1
        
        # went of to a side to score point?
        if self.ball.x < self.x:
            self.player2.score += 1
            self.serve_ball(vel=(4, 0))
        if self.ball.right > self.width:
            self.player1.score += 1
            self.serve_ball(vel=(-4, 0))

    # actions for keys pressed
        paddle_speed = 10
        if self.pressed_keys['w']:
            if self.player1.center_y + paddle_speed < self.height:
                self.player1.center_y += paddle_speed

        if self.pressed_keys['s']:
            if self.player1.center_y + paddle_speed > 0:
                self.player1.center_y -= paddle_speed

        if self.pressed_keys['o']:
            if self.player2.center_y + paddle_speed < self.height:
                self.player2.center_y += paddle_speed

        if self.pressed_keys['l']:
            if self.player2.center_y + paddle_speed > 0:
                self.player2.center_y -= paddle_speed
                
    def on_touch_move(self, touch):
        if touch.x < self.width / 3:
            self.player1.center_y = touch.y
        if touch.x > self.width - self.width / 3:
            self.player2.center_y = touch.y

class PongApp(App):
    def build(self):
        game = PongGame()
        Clock.schedule_interval(game.update, 1.0/60.0)
        game.serve_ball()
        return game

if __name__ == '__main__':
    PongApp().run()