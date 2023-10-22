from kivymd.uix.toolbar import MDTopAppBar
from kivy.lang import Builder
import os

Builder.load_file(os.path.join(os.path.dirname(__file__), 'silvertopappbar.kv'))

class SilverTopAppBar(MDTopAppBar):
    pass