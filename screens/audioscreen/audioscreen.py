
from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.properties import ListProperty
from kivy.clock import Clock
import os
Builder.load_file(os.path.join(os.path.dirname(__file__), 'audioscreen.kv'))



class AudioScreen(MDScreen):
    music = ListProperty()
    def find_music(self, interval):
        self.music = []
        app = MDApp.get_running_app()
        paths = app.root.system_storage
        for path in paths:  
            for dirpath, dirname, filenames in os.walk(path):
                for filename in filenames:
                    if filename.endswith('.mp3') or filename.endswith('.m4a'):
                        self.music.append(os.path.join(dirpath, filename))
    def on_pre_enter(self, *args):
        pass
    def on_enter(self, *args):
        Clock.schedule_once(self.find_music, 1)
        Clock.schedule_once(self.update, 1)
    def update(self, interval):
        for music in self.music: 
            self.ids.tracks.ids.audio_rv.data.append({'source':music})