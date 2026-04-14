
from kivymd.uix.list import OneLineRightIconListItem
from kivymd.uix.button import MDIconButton
from kivymd.app import MDApp
from kivy.properties import StringProperty, ObjectProperty, NumericProperty
from kivy.core.audio import SoundLoader
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.utils import platform
import os
from datetime import timedelta
from ..MinimalAudioplayer import MinimalAudioPlayer
from utils.audio_notification import show_audio_notification, cancel_audio_notification
Builder.load_file(os.path.join(os.path.dirname(__file__), 'audiofile.kv'))

class RightIconButton(MDIconButton):
    pass

class AudioFile(OneLineRightIconListItem):
    source = StringProperty() # for playing the music and setting the music name
    name = StringProperty()
    player = ObjectProperty()
    min_player = ObjectProperty()
    screen_player = ObjectProperty()
    length = StringProperty()
    duration = NumericProperty()

    def on_source(self, instance, value):
        name = os.path.split(value)[1]
        self.name = name

    def show_option(self):
        print(self.source)

    def play_audio(self, filename):
        app = MDApp.get_running_app()
        app.current_audio = self
        self.source = filename
        if self.min_player and self.player:
            # we already have a player loaded just change the song
            # but first remove the current playing song
            self.player.stop()
            self.player.unload()
            self.player = SoundLoader.load(filename)
            self.min_player.filename = filename
        else:
            self.min_player = MinimalAudioPlayer(filename=filename, pos_hint={'bottom':0.9})
            self.min_player.min_player_btn.bind(on_release=self.pause_play)
            app = MDApp.get_running_app()
            self.screen_player = app.root.screen_manager.get_screen('audioscreen')
            play_file = SoundLoader.load(filename)
            if play_file:
                self.screen_player.add_widget(self.min_player)
                self.player = play_file
        self.update_notification(True)
            
    def pause_play(self, instance):
        print(self.player.state, instance.icon )
        if self.player.state == 'play' and instance.icon == 'pause-circle-outline':
            self.toggle_playback()
        elif self.player.state == 'stop' and instance.icon == 'play-circle-outline':
            self.toggle_playback()

    def update_notification(self, is_playing):
        title = os.path.split(self.source)[1] if self.source else 'Audio'
        text = 'Playing' if is_playing else 'Paused'
        show_audio_notification(title, text, is_playing=is_playing)

    def toggle_playback(self):
        if not self.player:
            return
        if self.player.state == 'play':
            self.player.stop()
            if self.min_player:
                self.min_player.min_player_btn.icon = 'play-circle-outline'
            Clock.unschedule(self.update_progress)
            self.update_notification(False)
        else:
            self.player.play()
            if self.min_player:
                self.min_player.min_player_btn.icon = 'pause-circle-outline'
            Clock.schedule_interval(self.update_progress, 1)
            self.update_notification(True)

    def play_from_notification(self):
        if not self.player:
            return
        if self.player.state != 'play':
            self.player.play()
            if self.min_player:
                self.min_player.min_player_btn.icon = 'pause-circle-outline'
            Clock.schedule_interval(self.update_progress, 1)
            self.update_notification(True)

    def stop_from_notification(self):
        self.terminate()

    def on_player(self, instance, value):
        '''' value here is the player'''
        if value:
            self.duration = value.length
            delta = timedelta(seconds=self.duration)
            h, m, s = str(delta).split(':')
            self.length = f'{h}:{m}:{round(float(s))}'
            if self.min_player:
                self.min_player.length = self.length
            value.play()
            self.update_notification(True)
            if value.state == 'play':
                Clock.schedule_interval(self.update_progress, 1)

    def update_progress(self, interval):
        position = self.player.get_pos()
        current = (position/self.duration)*100
        self.min_player.ids.min_player_progressbar.value = current
        time = str(timedelta(seconds=position))
        h, m, s = time.split(':')
        self.min_player.length = f'{h}:{m}:{round(float(s))}'
        

        if round(current)  == 100 and not self.player.loop:
            self.termininate()
        elif self.player.loop:
            pass
    def termininate(self):
        Clock.unschedule(self.update_progress)
        cancel_audio_notification()
        if self.min_player and self.screen_player:
            self.screen_player.remove_widget(self.min_player)
        if self.player:
            self.player.stop()
            self.player.unload()
        

        

        



    

