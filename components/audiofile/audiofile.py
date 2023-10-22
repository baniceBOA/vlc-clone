
from kivymd.uix.list import OneLineAvatarIconListItem, IRightBodyTouch
from kivymd.uix.button import MDIconButton
from kivy.properties import StringProperty
from kivy.lang import Builder
import os

Builder.load_file(os.path.join(os.path.dirname(__file__), 'audiofile.kv'))

class RightIconButton(IRightBodyTouch, MDIconButton):
    pass

class AudioFile(OneLineAvatarIconListItem):
    source = StringProperty() # for playing the music and setting the music name
    name = StringProperty()

    def on_source(self, instance, value):
        name = os.path.split(value)[1]
        self.name = name
    def play_file(self):
        print(self.source)

