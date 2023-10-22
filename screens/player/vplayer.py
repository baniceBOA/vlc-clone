
from kivymd.uix.screen import  MDScreen
from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty
from mutagen.mp4 import MP4
from kivy.clock import Clock
from kivy.core.window import Window
from kivymd.app import MDApp
from datetime import timedelta
import os
import subprocess

Builder.load_file(os.path.join(os.path.dirname(__file__), 'vplayer.kv'))


class Player(MDScreen):
    title = StringProperty()
    source = StringProperty()
    duration = NumericProperty(0)
    thumb = StringProperty()
    time_duration = StringProperty('00:00')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.late_init,1)

    def late_init(self, interval):
        Window.bind(on_keyboard=self.key_input)
        self.ids.video.bind(position=self.change_slider_value)
    def on_source(self, instance, value):
        if value.endswith('.mp4'):
            self.duration = MP4(value).info.length
            delta = timedelta(seconds=self.duration)
            h, m, s = str(delta).split(':')
            self.time_duration = f'{h}:{m}:{round(float(s))}'
        elif value.endswith('.mkv') or value.endswith('.avi'):
            self.duration = self.get_length(value)
            delta = timedelta(seconds=self.duration)
            h, m, s = str(delta).split(':')
            self.time_duration = f'{h}:{m}:{round(float(s))}'
        else:
            #prevent division by zero error
            self.duration = 1
    def on_pre_enter(self, *args):
        self.ids.video.preview = self.thumb
        
    def on_leave(self, *args):
        self.ids.video.play = False
        self.ids.video.unload()

            
        

    
    def play_video(self, instance):
        if instance.icon == 'play':
            self.ids.video.play = True
            instance.icon = 'pause'
        elif instance.icon == 'pause':
            self.ids.video.play = False
            instance.icon = 'play'
    def seek_video(self, value):
        self.ids.video.seek(value/100, precise=True)

    def change_slider_value(self, instance, value):
       
        time = str(timedelta(seconds=self.duration) - timedelta(seconds=value)).zfill(3)
        h, m, s = time.split(':')
        self.time_duration = f'{h}:{m}:{round(float(s))}'
        position = (value/self.duration)*100
        self.ids.video_progressbar.value = position
    
    def get_length(self, filename):
        result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                "format=duration", "-of",
                                "default=noprint_wrappers=1:nokey=1", filename],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        return float(result.stdout)

    def key_input(self, window, key, scancode, codepoint, modifier):
        print(key)
        if key == 27 or key == 13 or key == 8:
            app = MDApp.get_running_app()
            app.root.add_widget(app.root.ids.bottom_bar)
            app.root.screen_manager.current = 'videofilescreen'
            return True # override the default behaviour
        else:
            # the key now does nothing
            return False
            

