from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty
from kivy.lang import Builder
import os

Builder.load_file(os.path.join(os.path.dirname(__file__), 'audiofileview.kv'))
class AudioFileView(MDBoxLayout):
    source = StringProperty()