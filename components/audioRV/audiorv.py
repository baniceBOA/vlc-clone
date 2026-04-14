from kivy.lang import Builder
from kivy.properties import ObjectProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
import os

from components import AudioFileView

Builder.load_file(os.path.join(os.path.dirname(__file__),'audiorv.kv'))


class AudioRV(BoxLayout):
    music_file = ListProperty()

    def on_music_file(self, *args):
        self.ids.rv.data = []
        for music in self.music_file:
            self.ids.rv.data.append({'source':music})
        
    