from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, NumericProperty, ListProperty, ReferenceListProperty, BooleanProperty
from kivy.core.window import Window
from kivy.config import Config
from kivy.clock import Clock
from kivy.vector import Vector
from kivy.uix.floatlayout import FloatLayout
from random import randint
import random, time

Builder.load_file("RapidFireApp.kv")


# Declare both screens

class PlayScreen(Screen):
    rapid_fire_game = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(PlayScreen, self).__init__(**kwargs)

    def on_enter(self, *args):
        Clock.schedule_interval(self.rapid_fire_game.appear_target, 1 / 1)


class MenuScreen(Screen):
    pass


class SettingsScreen(Screen):
    pass


class Target(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    shoot = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(Target, self).__init__(**kwargs)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.shoot = True

            # UPDATE ALL : SCORE, LEVEL, SCORE TO LEVEL, SPEED OF TARGETS, SPAWN TIME!!!!!
            self.parent.score += 10
            if self.parent.score_to_lvl_up > 0:
                self.parent.score_to_lvl_up -= 10
                if self.parent.score_to_lvl_up == 0:
                    self.parent.curr_level += 1
            self.parent.remove_widget(self)

    # Latest position = Current velocity + Current position
    def move(self):
        self.pos = Vector(*self.velocity) + self.pos

    def update(self, dt):
        if not self.shoot:
            self.move()
            # Bounce off top and bottom
            if (self.y < self.parent.main_frame.height / 4 - 50) or (self.y > self.parent.main_frame.height):
                self.parent.remove_widget(self)
                return False


class RapidFireGame(Widget):
    top_frame = ObjectProperty(None)
    main_frame = ObjectProperty(None)
    curr_level = NumericProperty(1)
    score = NumericProperty(0)
    score_to_lvl_up = NumericProperty(300)

    def __init__(self, **kwargs):
        super(RapidFireGame, self).__init__(**kwargs)

    def appear_target(self, *args):
        random_pos = Vector(random.randint(0, self.width), random.uniform(self.main_frame.height / 4,
                                                                          self.top_frame.height))
        target = Target()
        target.pos = random_pos
        if target.pos[1] < self.main_frame.height / 2:
            target.velocity = Vector(0, 1.5).rotate(randint(0, 360))  # different velocity for different level!!
        if target.pos[1] > self.main_frame.height / 2:
            target.velocity = Vector(0, -1.5).rotate(randint(0, 360))
        Clock.schedule_interval(target.update, 1.0 / 60.0)
        self.add_widget(target)


sm = ScreenManager()
sm.add_widget(MenuScreen(name='menu'))
sm.add_widget(PlayScreen(name='play'))
sm.add_widget(SettingsScreen(name='settings'))


class RapidFireApp(App):

    def build(self):
        return sm


if __name__ == '__main__':
    RapidFireApp().run()
