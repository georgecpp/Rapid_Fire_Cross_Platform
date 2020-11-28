from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.properties import ObjectProperty, NumericProperty, ListProperty, ReferenceListProperty, BooleanProperty, \
    StringProperty
from kivy.clock import Clock
from kivy.vector import Vector
from random import randint
import random
from kivy.utils import get_color_from_hex
from kivy.core.audio import SoundLoader
from kivy.config import Config
from kivy.core.window import Window
import math

Builder.load_file("RapidFireApp.kv")

Window.size = (1024, 768)


class PlayScreen(Screen):
    rapid_fire_game = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(PlayScreen, self).__init__(**kwargs)

    def on_enter(self, *args):
        if not sm.screens[0].ids.player_name_input.readonly:
            self.rapid_fire_game.update_leaderboard(str(sm.screens[0].ids.player_name_input.text))

        # self.rapid_fire_game.listPlayers.append({str(sm.screens[0].ids.player_name_input.text): 0})
        self.rapid_fire_game.eventTick = Clock.schedule_interval(self.rapid_fire_game.update_timer, 1)
        self.rapid_fire_game.event = Clock.schedule_interval(self.rapid_fire_game.appear_target,
                                                             1 / self.rapid_fire_game.spawn_time)


sound = SoundLoader.load('crazytrain.ogg')


class LeaderScreen(Screen):
    # rapid_fire_game = ObjectProperty(None)
    leaderText = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(LeaderScreen, self).__init__(**kwargs)

    def on_enter(self, *args):
        self.leaderText.text = ''
        ctr = 1
        with open('leaderboard.txt') as file_in:
            for line in file_in:
                words = line.split(", ")
                self.leaderText.text += (str(ctr) + '. ' + words[0] + ' ' + words[1])
                ctr += 1
        # with open('leaderboard.txt') as f:
        # contents = f.read()
        # print(contents[1])
        # self.leaderText.text = contents


class MenuScreen(Screen):
    player_name_input = ObjectProperty(None)
    btn_play = ObjectProperty(None)
    left_from_play = BooleanProperty(False)
    btn_quit = ObjectProperty(None)

    # list_prop = ListProperty([{'boss': 100}])

    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)
        sound.play()
        self.player_name_input.bind(text=self.enable_play)
        self.btn_play.bind(on_press=self.on_press)
        self.btn_quit.bind(on_press=self.on_quit)
        # self.list_prop.append(15)
        # print(self.list_prop[0]['boss'])

    def on_quit(self, instance):
        App.get_running_app().stop()

    def on_press(self, instance):
        self.parent.current = 'play'
        self.player_name_input.background_color = get_color_from_hex('#999999')
        # print(self.player_name_input.text)
        self.left_from_play = True

    def on_enter(self, *args):
        if self.left_from_play is True:
            self.player_name_input.readonly = True
            self.left_from_play = False

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
    N_target = NumericProperty(1)

    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    deltaPos_x = NumericProperty(0.0)
    deltaPos_y = NumericProperty(0.0)
    shoot = BooleanProperty(False)
    score_range = NumericProperty(0)

    def __init__(self, nt, **kwargs):
        super().__init__(**kwargs)
        self.N_target = nt
        print(self.N_target)

    def on_touch_down(self, touch):  # on_touch_down!
        if self.collide_point(*touch.pos):
            self.shoot = True
            self.pressed = touch.pos
            self.deltaPos_x = touch.pos[0] - self.pos[0]
            self.deltaPos_y = touch.pos[1] - self.pos[1]
            # CHECK FOR SCORE! CONCENTRIC CIRCLES
            # CASE 1 MAX CENTER - 20
            # if 48<self.deltaPos_x<51 and
            if (0 < self.deltaPos_x < self.size[0]) and (
                    0 < self.deltaPos_y < self.size[1]):
                self.score_range = 14 * self.N_target

            if (self.size[0] / 5 <= self.deltaPos_x <= 0.8 * self.size[0]) and (
                    self.size[1] / 5 <= self.deltaPos_y <= 0.8 * self.size[1]):
                self.score_range = 16 * self.N_target

            if (0.4 * self.size[0] <= self.deltaPos_x <= 0.6 * self.size[0]) and (
                    0.4 * self.size[1] <= self.deltaPos_y <= 0.6 * self.size[1]):
                self.score_range = 18 * self.N_target

            if (self.size[0] / 2 - self.size[0] / 50 <= self.deltaPos_x <= self.size[0] / 2 +
                self.size[0] / 50) and (
                    self.size[1] / 2 - self.size[1] / 50 <= self.deltaPos_y <= self.size[1] / 2 +
                    self.size[1] / 50):
                self.score_range = 20 * self.N_target

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
    listPlayers = ListProperty([])
    currPlayer = StringProperty(None)
    label = ObjectProperty(None)
    top_frame = ObjectProperty(None)
    main_frame = ObjectProperty(None)
    curr_level = NumericProperty(1)
    score = NumericProperty(0)
    score_to_lvl_up = NumericProperty(300)
    copy_score_lvl_up = NumericProperty(0)
    spawn_time = NumericProperty(2.5)
    speed_target = NumericProperty(2.0)
    timer_val = NumericProperty(30)
    event = 0
    eventTick = 0
    eventPlayer = 0

    def __init__(self, **kwargs):
        super(RapidFireGame, self).__init__(**kwargs)
        self.copy_score_lvl_up = self.score_to_lvl_up
        with open('leaderboard.txt') as file_in:
            for line in file_in:
                words = line.split(", ")
                self.listPlayers.append({words[0]: int(words[1])})
        self.listPlayers = sorted(self.listPlayers, key=lambda d: list(d.values()), reverse=True)

    def appear_target(self, *args):
        random_pos = Vector(random.randint(0, self.width), random.uniform(self.main_frame.height / 4,
                                                                          self.top_frame.height))

        va = [1, self.curr_level]
        distribution = [0.7, 0.3]

        N_tg = random.choices(va, distribution)[0]
        if self.curr_level > 5:
            N_tg = 1

        target = Target(N_tg)
        target.pos = random_pos
        if N_tg > 2:
            N_tg = math.log2(N_tg)
        if target.pos[1] < self.main_frame.height / 2:
            target.velocity = Vector(0, self.speed_target * N_tg).rotate(
                randint(0, 360))  # different velocity for different level!!
        if target.pos[1] > self.main_frame.height / 2:
            target.velocity = Vector(0, -1.0 * self.speed_target * N_tg).rotate(randint(0, 360))
        Clock.schedule_interval(target.update, 1.0 / 120.0)
        self.add_widget(target)

    def update_leaderboard(self, *args):
        self.currPlayer = args[0]
        # check if already there! if so, update score, second member of dict!!! {key,value}
        for el in self.listPlayers:
            if args[0] in el:
                el[args[0]] = 0
                return
        self.listPlayers.append({args[0]: 0})
        self.listPlayers = sorted(self.listPlayers, key=lambda d: list(d.values()), reverse=True)

    def update_new_level(self):
        # self.level_up.opacity = 1

        # for timer
        self.eventTick.cancel()
        self.timer_val = 30
        self.eventTick = Clock.schedule_interval(self.update_timer, 1)

        self.curr_level += 1
        self.score_to_lvl_up = self.copy_score_lvl_up + 100
        self.copy_score_lvl_up += (100 * self.curr_level - 100)
        self.speed_target += (0.1 * self.curr_level)

        # for spawn time modified of targets.
        self.event.cancel()
        self.spawn_time += (0.2 * self.curr_level)
        self.event = Clock.schedule_interval(self.appear_target, 1 / self.spawn_time)

    def update_timer(self, *args):
        self.timer_val -= 1
        for label in list(self.children):
            if isinstance(label, Label) and label.id == 'score2go':
                self.remove_widget(label)
        if self.timer_val == 0:  # verify score to level up. if > 0, you lost, update your score to leaderboard
            if self.score_to_lvl_up >= 0:
                self.event.cancel()
                self.eventTick.cancel()
                for el in self.listPlayers:
                    if self.currPlayer in el:
                        el[self.currPlayer] = self.score
                self.listPlayers = sorted(self.listPlayers, key=lambda d: list(d.values()), reverse=True)
                with open('leaderboard.txt', 'w') as f:
                    for el in self.listPlayers:
                        for key, value in el.items():
                            f.write('%s, %s\n' % (key, value))
                self.timer_val = 30
                self.score = 0
                self.curr_level = 1
                self.score_to_lvl_up = 300
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
