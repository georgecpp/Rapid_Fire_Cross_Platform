from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.properties import ObjectProperty, NumericProperty, ListProperty, ReferenceListProperty, BooleanProperty
from kivy.clock import Clock
from kivy.vector import Vector
from random import randint
import random
from kivy.utils import get_color_from_hex
from kivy.core.audio import SoundLoader

Builder.load_file("RapidFireApp.kv")


# Declare both screens

class PlayScreen(Screen):
    rapid_fire_game = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(PlayScreen, self).__init__(**kwargs)

    def on_enter(self, *args):
        self.rapid_fire_game.eventTick = Clock.schedule_interval(self.rapid_fire_game.update_timer, 1)
        self.rapid_fire_game.event = Clock.schedule_interval(self.rapid_fire_game.appear_target,
                                                             1 / self.rapid_fire_game.spawn_time)


sound = SoundLoader.load('crazytrain.ogg')


class LeaderScreen(Screen):
    pass


class MenuScreen(Screen):
    player_name_input = ObjectProperty(None)
    btn_play = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)
        sound.play()
        self.player_name_input.bind(text=self.enable_play)

    def enable_play(self, instance, text):
        if text != '':
            self.btn_play.disabled = False
        else:
            self.btn_play.disabled = True


class SettingsScreen(Screen):
    toggle_music = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)

    def on_state(self, state):
        if state == 'down':
            sound.volume = 0.0
        else:
            sound.volume = 1.0


class Target(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    deltaPos_x = NumericProperty(0.0)
    deltaPos_y = NumericProperty(0.0)
    shoot = BooleanProperty(False)
    score_range = NumericProperty(0)

    def __init__(self, **kwargs):
        super(Target, self).__init__(**kwargs)

    def on_touch_down(self, touch):  # on_touch_down!
        if self.collide_point(*touch.pos):
            self.shoot = True
            self.pressed = touch.pos
            self.deltaPos_x = touch.pos[0] - self.pos[0]
            self.deltaPos_y = touch.pos[1] - self.pos[1]
            # CHECK FOR SCORE! CONCENTRIC CIRCLES
            # CASE 1 MAX CENTER - 20
            # if 48<self.deltaPos_x<51 and
            if (self.deltaPos_x > 0 and self.deltaPos_x < self.size[0]) and (
                    self.deltaPos_y > 0 and self.deltaPos_y < self.size[1]):
                self.score_range = 14
            if (self.deltaPos_x >= self.size[0] / 5 and self.deltaPos_x <= 0.8 * self.size[0]) and (
                    self.deltaPos_y >= self.size[1] / 5 and self.deltaPos_y <= 0.8 * self.size[1]):
                self.score_range = 16
            if (self.deltaPos_x >= 0.4 * self.size[0] and self.deltaPos_x <= 0.6 * self.size[0]) and (
                    self.deltaPos_y >= 0.4 * self.size[1] and self.deltaPos_y <= 0.6 * self.size[1]):
                self.score_range = 18
            if (self.deltaPos_x >= self.size[0] / 2 - self.size[0] / 50 and self.deltaPos_x <= self.size[0] / 2 +
                self.size[0] / 50) and (
                    self.deltaPos_y >= self.size[1] / 2 - self.size[1] / 50 and self.deltaPos_y <= self.size[1] / 2 +
                    self.size[1] / 50):
                self.score_range = 20
            # UPDATE ALL : SCORE, LEVEL, SCORE TO LEVEL, SPEED OF TARGETS, SPAWN TIME!!!!!
            self.parent.score += self.score_range
            if self.parent.score_to_lvl_up > 0:
                self.parent.score_to_lvl_up -= self.score_range
                if self.parent.score_to_lvl_up <= 0:
                    self.parent.update_new_level()
                    # UPDATE ALL - SCORE_LVL UP +=100, SPEED_TARGETS, SPAWN TIME!!!!! - CLOCK BACK TO 60.

            # pop up score next to target!
            label = Label()
            label.id = 'score2go'
            label.x = self.pos[0]
            label.y = self.pos[1]
            if self.score_range == 20:
                label.color = get_color_from_hex('#ff0000')
            label.text = str(self.score_range)
            self.parent.add_widget(label)

            self.parent.remove_widget(self)
            return True
        else:
            return super(Target, self).on_touch_down(touch)

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
    label = ObjectProperty(None)
    top_frame = ObjectProperty(None)
    main_frame = ObjectProperty(None)
    curr_level = NumericProperty(1)
    score = NumericProperty(0)
    score_to_lvl_up = NumericProperty(300)
    copy_score_lvl_up = NumericProperty(0)
    spawn_time = NumericProperty(1.5)
    speed_target = NumericProperty(1.5)
    timer_val = NumericProperty(30)
    event = 0
    eventTick = 0

    def __init__(self, **kwargs):
        super(RapidFireGame, self).__init__(**kwargs)
        self.copy_score_lvl_up = self.score_to_lvl_up

    def appear_target(self, *args):
        random_pos = Vector(random.randint(0, self.width), random.uniform(self.main_frame.height / 4,
                                                                          self.top_frame.height))
        target = Target()
        target.pos = random_pos
        if target.pos[1] < self.main_frame.height / 2:
            target.velocity = Vector(0, self.speed_target).rotate(
                randint(0, 360))  # different velocity for different level!!
        if target.pos[1] > self.main_frame.height / 2:
            target.velocity = Vector(0, -1.0 * self.speed_target).rotate(randint(0, 360))
        Clock.schedule_interval(target.update, 1.0 / 60.0)
        self.add_widget(target)

    def update_new_level(self):
        # self.level_up.opacity = 1

        # for timer
        self.eventTick.cancel()
        self.timer_val = 30
        self.eventTick = Clock.schedule_interval(self.update_timer, 1)

        self.curr_level += 1
        self.score_to_lvl_up = self.copy_score_lvl_up + 100
        self.copy_score_lvl_up += 100
        self.speed_target += 0.5

        # for spawn time modified of targets.
        self.event.cancel()
        self.spawn_time += 1.0
        self.event = Clock.schedule_interval(self.appear_target, 1 / self.spawn_time)

    def update_timer(self, *args):
        self.timer_val -= 1
        for label in list(self.children):
            if isinstance(label, Label) and label.id == 'score2go':
                self.remove_widget(label)
        if self.timer_val == 0:  # verify score to level up. if > 0, you lost.
            if self.score_to_lvl_up >= 0:
                self.event.cancel()
                self.eventTick.cancel()
                return


sm = ScreenManager()
sm.add_widget(MenuScreen(name='menu'))
sm.add_widget(PlayScreen(name='play'))
sm.add_widget(SettingsScreen(name='settings'))
sm.add_widget(LeaderScreen(name='leader'))


class RapidFireApp(App):

    def build(self):
        return sm


if __name__ == '__main__':
    RapidFireApp().run()
