from kivymd.uix.screen import MDScreen
from kivy.properties import ListProperty
from kivy.lang import Builder
from kivy.clock import Clock
import os

from components import VideoCard
Builder.load_file(os.path.join(os.path.dirname(__file__), 'videofilescreen.kv'))


class VideoFileScreen(MDScreen):
    ''' Display the Video file according to the files '''
    files = ListProperty()

    def on_pre_enter(self, *args):
        ''' perform cleaning of the data before changing the data'''
        self.ids.rv.data = []

    def on_enter(self,*args):
        Clock.schedule_once(self.get_files, 1)
    def get_files(self, invterval):
        self.ids.rv.data = []
        if self.files:
            for file in self.files:
                data = {}
                data['thumb'] = f'assests/thumbs/{os.path.splitext(os.path.split(file)[1])[0]}.png'
                data['drive'] = os.path.splitdrive(file)[0]
                data['filename'] = os.path.split(file)[1]
                data['source'] = file
                self.ids.rv.data.append(data)

    